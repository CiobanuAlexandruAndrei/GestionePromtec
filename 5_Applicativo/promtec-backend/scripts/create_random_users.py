import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.security.models import User
from app.schools.defaults import INITIAL_SCHOOLS
from app.extensions import db
from werkzeug.security import generate_password_hash
from faker import Faker
import random

fake = Faker('it_IT') 

def create_random_users(num_users=20):
    app = create_app()
    
    with app.app_context():
        for _ in range(num_users):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@{fake.free_email_domain()}"
            password = generate_password_hash("Test123!", method='pbkdf2:sha256')
            school_name = random.choice(INITIAL_SCHOOLS)
            
            user = User(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                school_name=school_name,
                is_active=True,
                is_admin=False,
                deleted=False
            )
            
            try:
                db.session.add(user)
                db.session.commit()
                print(f"Created user: {email} - {first_name} {last_name} - {school_name}")
            except Exception as e:
                db.session.rollback()
                print(f"Error creating user {email}: {str(e)}")

if __name__ == "__main__":
    create_random_users()