import uuid
from app import db

class User(db.Model):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    user_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)