"""
Slots and Enrollment Models Module.

This module defines the data models for managing enrollment slots, students,
and enrollment records in the system. It includes:

1. EnrollmentActivity - Tracks user enrollment activity for summary emails
2. Slot - Represents available enrollment time slots with constraints and rules
3. Student - Contains encrypted student personal information
4. StudentEnrollment - Links students to specific slots with waiting list status

The module also includes several enumeration classes for standardizing options
such as time periods, departments, and gender categories.
"""
import os
from datetime import datetime, timedelta, timezone  # For date and time operations
from enum import Enum  # For defining enumeration types
from app.extensions import db  # Database ORM instance
from app.security.models import School, User  # Related models
from app.utils.crypto_utils import encrypt_value, decrypt_value  # For encrypting sensitive data
from sqlalchemy.ext.hybrid import hybrid_property  # For property encryption/decryption
from app.utils.email_utils import send_email  # For sending notification emails
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class EnrollmentActivity(db.Model):
    """
    User enrollment activity tracking model.
    
    This model tracks when users perform enrollment activities and manages the
    sending of summary emails. It ensures users receive a single summary email
    for all enrollments made within a specific time window rather than
    individual emails for each enrollment action.
    
    Attributes:
        id (int): Primary key identifier for the activity record
        user_id (int): Foreign key to the user performing enrollment actions
        last_activity (datetime): Timestamp of the most recent enrollment activity
        email_sent (bool): Whether a summary email has been sent for this activity period
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    email_sent = db.Column(db.Boolean, default=False)
    
    @classmethod
    def update_activity(cls, user_id):
        """Update or create activity tracking for a user"""
        now = datetime.utcnow()
        
        # First look for an existing unsent activity for this user
        existing_unsent = cls.query.filter_by(user_id=user_id, email_sent=False).first()
        
        if existing_unsent:
            # If an unsent activity exists, just update its timestamp
            logger.debug(f"Updating existing unsent activity for user {user_id}")
            existing_unsent.last_activity = now
            activity = existing_unsent
        else:
            # If no unsent activity exists, create a new one
            logger.debug(f"Creating new activity record for user {user_id}")
            activity = cls(
                user_id=user_id,
                last_activity=now,
                email_sent=False
            )
            db.session.add(activity)
        
        db.session.commit()
        return activity
        
    @classmethod
    def check_and_send_summaries(cls):
        """Check and send enrollment summaries for users who have been inactive for 30 minutes"""
        logger.info("Starting periodic enrollment summary check...")
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=30)
            logger.debug(f"Looking for activities before {cutoff_time}")
            
            pending_activities = cls.query.filter(
                cls.last_activity < cutoff_time,
                cls.email_sent == False
            ).all()

            logger.info(f"Found {len(pending_activities)} pending activities to process")

            for activity in pending_activities:
                logger.debug(f"Processing activity {activity.id} for user {activity.user_id}")
                try:
                    # Get all enrollments created by this user in the last 30 minutes
                    enrollments = StudentEnrollment.query.filter(
                        StudentEnrollment.user_id == activity.user_id,
                        StudentEnrollment.created_at >= activity.last_activity - timedelta(minutes=30),
                        StudentEnrollment.created_at <= activity.last_activity
                    ).all()

                    logger.debug(f"Found {len(enrollments)} enrollments to summarize for user {activity.user_id}")

                    if enrollments:
                        user = User.query.get(activity.user_id)
                        if user and not user.is_admin:
                            logger.info(f"Sending enrollment summary for non-admin user {user.email}")
                            from app.utils.email_utils import send_enrollment_summary_email
                            
                            # Use full name for greeting
                            user_full_name = f"{user.first_name} {user.last_name}"
                            
                            """ email_sent = send_enrollment_summary_email(
                                user_email=user.email,
                                user_name=user_full_name,
                                enrollments=enrollments
                            ) """
                            email_sent = True
                            if email_sent:
                                logger.info(f"Successfully sent summary email to {user.email}")
                            else:
                                logger.error(f"Failed to send summary email to {user.email}")
                                continue  # Don't mark as sent if email failed

                    activity.email_sent = True
                    db.session.commit()
                    logger.info(f"Marked activity {activity.id} as completed")
                    
                except Exception as e:
                    logger.error(f"Error processing activity {activity.id}: {str(e)}")
                    db.session.rollback()
                    
        except Exception as e:
            logger.error(f"Error in enrollment summary check: {str(e)}")
            db.session.rollback()
        finally:
            logger.info("Completed enrollment summary check")
            
class OrganizationInfo(str, Enum):
    FIRST_NAME = "Cesare"
    LAST_NAME = "Casaletel"
    TELEPHONE = "091 815 10 11"
    EMAIL = "decs-cpt.trevano.promtec@edu.ti.ch"


class DetailedTimePeriod(str, Enum):
    MORNING = "8:20-12:20"
    AFTERNOON = "13:15-16:30"


class TimePeriod(str, Enum):
    MORNING = "Mattina"
    AFTERNOON = "Pomeriggio"


class GenderCategory(str, Enum):
    MIXED = "Misto"
    BOYS = "Solo ragazzi"
    GIRLS = "Solo ragazze"

    def allows_gender(self, gender: 'Gender') -> bool:
        if self == self.MIXED:
            return True
        if self == self.BOYS:
            return gender == Gender.BOY
        if self == self.GIRLS:
            return gender == Gender.GIRL
        return False


class Gender(str, Enum):
    BOY = "Maschio"
    GIRL = "Femmina"


class Department(str, Enum):
    TECH = "Settore Tecnologie Innovative"
    CONSTRUCTION = "Settore Costruzioni"
    CHEMISTRY = "Settore Chimica"


class Slot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time_period = db.Column(db.Enum(TimePeriod), nullable=False)
    department = db.Column(db.Enum(Department), nullable=False)
    gender_category = db.Column(db.Enum(GenderCategory), nullable=False)
    notes = db.Column(db.Text)
    total_spots = db.Column(db.Integer, nullable=False)
    max_students_per_school = db.Column(db.Integer, nullable=False)
    is_locked = db.Column(db.Boolean, default=False)

    is_confirmed = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Initialize slot and set locked status based on date
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_locked = self.should_be_locked
        self.is_confirmed = False

    @hybrid_property 
    def should_be_locked(self):
        """Check if slot should be locked (2 weeks before date)"""
        today = datetime.now(timezone.utc).date()
        lock_date = self.date - timedelta(weeks=2) 
        return today >= lock_date

    @should_be_locked.expression
    def should_be_locked(cls):
        today = datetime.now(timezone.utc).date()
        return cls.date - timedelta(weeks=2) <= today

    def can_enroll_student(self, student: 'Student') -> bool:
        """Check if a student can be enrolled in this slot based on gender rules"""
        return self.gender_category.allows_gender(student.gender)

    def get_occupied_spots(self) -> int:
        """Get number of occupied spots in this slot"""
        return len([e for e in self.enrollments if not e.is_in_waiting_list])
        
    def get_school_enrollment_count(self, school_name: str) -> int:
        """Get number of enrolled students from a specific school"""
        return len([e for e in self.enrollments 
                   if e.student.school_name == school_name and not e.is_in_waiting_list])

    def get_available_spots(self) -> int:
        """Get number of available spots in total"""
        return self.total_spots - self.get_occupied_spots()
        
    def get_available_school_spots(self, school_name: str) -> int:
        """Get number of available spots for a specific school"""
        # A school can't have more students than the total available spots
        max_allowed = min(self.max_students_per_school, self.get_available_spots())
        current = self.get_school_enrollment_count(school_name)
        return max_allowed - current
        
    def should_be_in_waiting_list(self, school_name: str) -> bool:
        """Determine if a new student from this school should go to waiting list"""
        return self.get_available_school_spots(school_name) <= 0

    @classmethod
    def validate_time_period_constraint(cls, date, department, time_period, slot_id=None):
        """
        Validate that there isn't already a slot with the same time period for this department on this date
        Returns (is_valid, error_message)
        """
        query = cls.query.filter(
            cls.date == date,
            cls.department == department,
            cls.time_period == time_period
        )
        
        if slot_id:
            query = query.filter(cls.id != slot_id)
            
        existing_slot = query.first()
        if existing_slot:
            return False, f"A slot for {department.value} already exists on {date} during {time_period.value}"
        
        return True, None

    @classmethod
    def validate_slots_per_day(cls, date, department, slot_id=None):
        """
        Validate that there are no more than 2 slots per department per day
        Returns (is_valid, error_message)
        """
        query = cls.query.filter(
            cls.date == date,
            cls.department == department
        )
        
        if slot_id:
            query = query.filter(cls.id != slot_id)
        
        existing_slots_count = query.count()
        
        # Changed condition to check for strictly greater than 2
        if existing_slots_count >= 2:
            return False, f"Cannot create more than 2 slots per department per day. Found {existing_slots_count} slots for {department.value} on {date}"
        
        return True, None

    @staticmethod
    def _set_slot_unconfirmed(target, value, oldvalue, initiator):
        """Event listener to set is_confirmed to False when slot is updated"""
        if oldvalue != value:  # Only if the value actually changed
            target.is_confirmed = False

    @classmethod
    def __declare_last__(cls):
        # Set up the event listeners for all relevant fields
        db.event.listen(cls.date, 'set', cls._set_slot_unconfirmed)
        db.event.listen(cls.time_period, 'set', cls._set_slot_unconfirmed)
        db.event.listen(cls.department, 'set', cls._set_slot_unconfirmed)
        db.event.listen(cls.gender_category, 'set', cls._set_slot_unconfirmed)
        db.event.listen(cls.notes, 'set', cls._set_slot_unconfirmed)
        db.event.listen(cls.total_spots, 'set', cls._set_slot_unconfirmed)
        db.event.listen(cls.max_students_per_school, 'set', cls._set_slot_unconfirmed)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    _first_name = db.Column("first_name", db.String(255), nullable=False)
    _last_name = db.Column("last_name", db.String(255), nullable=False)
    _school_class = db.Column("school_class", db.String(255), nullable=False)
    _gender = db.Column("gender", db.String(255), nullable=False)
    _address = db.Column("address", db.String(255), nullable=False)
    _postal_code = db.Column("postal_code", db.String(255), nullable=False)
    _city = db.Column("city", db.String(255), nullable=False)
    _landline = db.Column("landline", db.String(255), nullable=True)
    _mobile = db.Column("mobile", db.String(255), nullable=False)

    school_name = db.Column(db.String(50), db.ForeignKey('school.name', name='fk_student_school', ondelete='SET NULL'), nullable=True)
    school = db.relationship('School', backref=db.backref('students', lazy=True))

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    @hybrid_property
    def first_name(self):
        return decrypt_value(self._first_name)

    @first_name.setter
    def first_name(self, value):
        self._first_name = encrypt_value(value)

    @first_name.expression
    def first_name(cls):
        return cls._first_name

    @hybrid_property
    def last_name(self):
        return decrypt_value(self._last_name)

    @last_name.setter
    def last_name(self, value):
        self._last_name = encrypt_value(value)

    @last_name.expression
    def last_name(cls):
        return cls._last_name

    @hybrid_property
    def school_class(self):
        return decrypt_value(self._school_class)

    @school_class.setter
    def school_class(self, value):
        self._school_class = encrypt_value(value)

    @school_class.expression
    def school_class(cls):
        return cls._school_class

    @hybrid_property
    def gender(self):
        return decrypt_value(self._gender)

    @gender.setter
    def gender(self, value):
        self._gender = encrypt_value(value)

    @gender.expression
    def gender(cls):
        return cls._gender

    @hybrid_property
    def address(self):
        return decrypt_value(self._address)

    @address.setter
    def address(self, value):
        if value and not value.strip().lower().startswith(('via ', 'viale ')):
            value = f'Via {value.strip()}'
        self._address = encrypt_value(value)

    @address.expression
    def address(cls):
        return cls._address

    @hybrid_property
    def postal_code(self):
        return decrypt_value(self._postal_code)

    @postal_code.setter
    def postal_code(self, value):
        self._postal_code = encrypt_value(value)

    @postal_code.expression
    def postal_code(cls):
        return cls._postal_code

    @hybrid_property
    def city(self):
        return decrypt_value(self._city)

    @city.setter
    def city(self, value):
        self._city = encrypt_value(value)

    @city.expression
    def city(cls):
        return cls._city

    @hybrid_property
    def landline(self):
        return decrypt_value(self._landline)

    @landline.setter
    def landline(self, value):
        self._landline = encrypt_value(value)

    @landline.expression
    def landline(cls):
        return cls._landline

    @hybrid_property
    def mobile(self):
        return decrypt_value(self._mobile)

    @mobile.setter
    def mobile(self, value):
        self._mobile = encrypt_value(value)

    @mobile.expression
    def mobile(cls):
        return cls._mobile

    @classmethod
    def __declare_last__(cls):
        # Listen for student changes
        db.event.listen(cls, 'after_update', cls._student_changed)

    @staticmethod
    def _student_changed(mapper, connection, target):
        """Set is_confirmed to False for all slots where this student is enrolled"""
        for enrollment in target.enrollments:
            if enrollment.slot:
                enrollment.slot.is_confirmed = False


class StudentEnrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('enrollments', lazy=True))

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    student = db.relationship('Student', backref=db.backref('enrollments', lazy=True))

    slot_id = db.Column(db.Integer, db.ForeignKey('slot.id'), nullable=False)
    slot = db.relationship('Slot', backref=db.backref('enrollments', lazy=True))

    is_in_waiting_list = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    @staticmethod
    def create(slot: Slot, student: Student, user: 'User') -> 'StudentEnrollment':
        """Factory method to create a valid enrollment"""
        if not slot.can_enroll_student(student):
            raise ValueError("Student gender not allowed in this slot")
            
        enrollment = StudentEnrollment(
            slot=slot,
            student=student,
            user=user,
            is_in_waiting_list=(slot.get_available_spots() <= 0)
        )
        return enrollment

    @staticmethod
    def _enrollment_changed(mapper, connection, target):
        """Set is_confirmed to False for the slot when enrollment changes"""
        if target.slot:
            target.slot.is_confirmed = False

    @classmethod
    def __declare_last__(cls):
        # Listen for changes to enrollments
        db.event.listen(cls, 'after_insert', cls._enrollment_changed)
        db.event.listen(cls, 'after_update', cls._enrollment_changed)
        db.event.listen(cls, 'after_delete', cls._enrollment_changed)