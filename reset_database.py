from app import app
from config.database import db

with app.app_context():
    db.drop_all()
    db.create_all()

    # Reinsert departments, designations, leave types and admin user.
    from app import insert_initial_data
    insert_initial_data()

print("Database tables recreated successfully.")
