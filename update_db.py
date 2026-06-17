import os
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.models import db
from sqlalchemy import text

def update_schema():
    app = create_app()
    with app.app_context():
        try:
            print("Updating database schema...")
            
            # Add columns to users table
            db.session.execute(text("ALTER TABLE public.users ADD COLUMN IF NOT EXISTS phone VARCHAR(20)"))
            db.session.execute(text("ALTER TABLE public.users ADD COLUMN IF NOT EXISTS location VARCHAR(255)"))
            db.session.execute(text("ALTER TABLE public.users ADD COLUMN IF NOT EXISTS name VARCHAR(255)"))
            print("Checked/added phone, location, name columns in users table.")
            
            # Add columns to recruiters table
            db.session.execute(text("ALTER TABLE public.recruiters ADD COLUMN IF NOT EXISTS company VARCHAR(255)"))
            db.session.execute(text("ALTER TABLE public.recruiters ADD COLUMN IF NOT EXISTS job_title VARCHAR(255)"))
            print("Checked/added company, job_title columns in recruiters table.")
            
            # Add status column to rankings table
            db.session.execute(text("ALTER TABLE public.rankings ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'Pending'"))
            print("Checked/added status column in rankings table.")
            
            # Add check constraint to status in rankings (try/except in case it exists)
            try:
                db.session.execute(text("ALTER TABLE public.rankings ADD CONSTRAINT rankings_status_check CHECK (status IN ('Pending', 'Shortlisted', 'Rejected'))"))
                print("Added status check constraint to rankings table.")
            except Exception as const_e:
                db.session.rollback()
                print("Status check constraint already exists or could not be added:", str(const_e).split('\n')[0])
            
            db.session.commit()
            print("Database schema updated successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating database schema: {e}")

if __name__ == "__main__":
    update_schema()
