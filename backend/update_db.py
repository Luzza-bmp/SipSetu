from app import create_app
from models import db
from sqlalchemy import text
app = create_app()
with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20)"))
        db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS location VARCHAR(255)"))
        db.session.execute(text("ALTER TABLE recruiters ADD COLUMN IF NOT EXISTS company VARCHAR(255)"))
        db.session.execute(text("ALTER TABLE recruiters ADD COLUMN IF NOT EXISTS job_title VARCHAR(255)"))
        db.session.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS description TEXT"))
        db.session.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active'"))
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                bookmark_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                applicant_id UUID NOT NULL REFERENCES applicants(user_id) ON DELETE CASCADE,
                job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        db.session.commit()
        print("Database schema updated successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error updating database: {e}")
