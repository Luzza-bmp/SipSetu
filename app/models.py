import uuid
from app import db

class User(db.Model):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    user_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) #attribute name should be user_id, not id, because in the database, the column is named user_id. If we use id, it will not match the column name in the database and will cause an error when trying to access or manipulate user records.
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)