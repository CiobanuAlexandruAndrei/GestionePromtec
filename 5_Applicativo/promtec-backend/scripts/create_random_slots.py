import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.slots.models import Slot, TimePeriod, Department, GenderCategory
from datetime import datetime, timedelta
import random

def create_random_slots(num_slots=20, start_date=None):
    """Create random slots for testing purposes."""
    if start_date is None:
        start_date = datetime.now().date()

    app = create_app()
    with app.app_context():
        for _ in range(num_slots):
            # Random date within next 60 days
            random_days = random.randint(1, 60)
            slot_date = start_date + timedelta(days=random_days)

            # Random selections from enums
            time_period = random.choice(list(TimePeriod))
            department = random.choice(list(Department))
            gender_category = random.choice(list(GenderCategory))

            # Random spots (between 15 and 30)
            total_spots = random.randint(15, 30)
            # Max students per school is usually between 5 and 10
            max_students = random.randint(5, min(10, total_spots))

            # Random notes
            notes = random.choice([
                "Portare il necessario per prendere appunti",
                "È richiesto un abbigliamento consono al laboratorio",
                "Presentarsi 10 minuti prima dell'inizio",
                None
            ])

            # Create slot
            slot = Slot(
                date=slot_date,
                time_period=time_period,
                department=department,
                gender_category=gender_category,
                notes=notes,
                total_spots=total_spots,
                max_students_per_school=max_students,
                is_locked=False  # New slots start unlocked
            )

            db.session.add(slot)
            
        db.session.commit()
        print(f"Created {num_slots} random slots successfully!")

if __name__ == "__main__":
    num_slots = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    create_random_slots(num_slots)