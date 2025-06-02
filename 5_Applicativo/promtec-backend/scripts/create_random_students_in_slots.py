import sys
import os
import random
from faker import Faker
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.slots.models import Slot, Student, StudentEnrollment, Gender
from app.security.models import School, User

fake = Faker('it_IT')

def generate_random_student(school_name):
    gender = random.choice([Gender.BOY, Gender.GIRL])
    first_name = fake.first_name_male() if gender == Gender.BOY else fake.first_name_female()
    
    student = Student(
        first_name=first_name,
        last_name=fake.last_name(),
        school_class=f"{random.randint(1, 4)}{random.choice(['A', 'B', 'C', 'D'])}",
        gender=gender,
        address=fake.street_address(),
        postal_code=fake.postcode(),
        city=fake.city(),
        mobile=fake.phone_number(),
        landline=fake.phone_number(),
        school_name=school_name
    )
    return student

def main():
    app = create_app()
    with app.app_context():
        try:
            school = School.query.first()

            slot = Slot.query.filter(Slot.is_locked == False).first()
            if not slot:
                print("No available slots found!")
                return

            user = User.query.offset(2).first()
            if not user:
                print("No users found in database!")
                return

            for i in range(30):
                student = generate_random_student(school.name)
                db.session.add(student)
                
                # Create enrollment
                enrollment = StudentEnrollment.create(slot, student, user)
                db.session.add(enrollment)
                
                if (i + 1) % 100 == 0:
                    db.session.commit()  # Commit in batches to avoid memory issues
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"Error occurred: {str(e)}")
            raise

if __name__ == "__main__":
    main()
