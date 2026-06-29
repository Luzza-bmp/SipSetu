import uuid
from datetime import datetime
from app import db

# Junction tables
job_skills = db.Table('job_skills',
    db.Column('job_id', db.UUID(as_uuid=True), db.ForeignKey('public.jobs.job_id', ondelete='CASCADE'), primary_key=True),
    db.Column('skill_id', db.UUID(as_uuid=True), db.ForeignKey('public.skills.skill_id', ondelete='CASCADE'), primary_key=True),
    schema='public'
)

resume_skills = db.Table('resume_skills',
    db.Column('resume_id', db.UUID(as_uuid=True), db.ForeignKey('public.resumes.resume_id', ondelete='CASCADE'), primary_key=True),
    db.Column('skill_id', db.UUID(as_uuid=True), db.ForeignKey('public.skills.skill_id', ondelete='CASCADE'), primary_key=True),
    schema='public'
)

class User(db.Model):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    user_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(255), nullable=True)

    __mapper_args__ = {
        'polymorphic_on': role,
        'polymorphic_identity': 'user'
    }

class Applicant(User):
    __tablename__ = 'applicants'
    __table_args__ = {"schema": "public"}
    
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('public.users.user_id', ondelete='CASCADE'), primary_key=True)
    resumes = db.relationship('Resume', backref='applicant', lazy=True, cascade='all, delete-orphan')

    __mapper_args__ = {
        'polymorphic_identity': 'applicant',
    }

class Recruiter(User):
    __tablename__ = 'recruiters'
    __table_args__ = {"schema": "public"}
    
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('public.users.user_id', ondelete='CASCADE'), primary_key=True)
    company = db.Column(db.String(255), nullable=True)
    job_title = db.Column(db.String(255), nullable=True)
    jobs = db.relationship('Job', backref='recruiter', lazy=True, cascade='all, delete-orphan')

    __mapper_args__ = {
        'polymorphic_identity': 'recruiter',
    }

class Skill(db.Model):
    __tablename__ = 'skills'
    __table_args__ = {"schema": "public"}
    
    skill_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_name = db.Column(db.String(100), unique=True, nullable=False)

class Job(db.Model):
    __tablename__ = 'jobs'
    __table_args__ = {"schema": "public"}
    
    job_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recruiter_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('public.recruiters.user_id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    skills = db.relationship('Skill', secondary=job_skills, backref=db.backref('jobs', lazy='dynamic'))
    rankings = db.relationship('Ranking', backref='job', lazy=True, cascade='all, delete-orphan')

class Resume(db.Model):
    __tablename__ = 'resumes'
    __table_args__ = {"schema": "public"}
    
    resume_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    applicant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('public.applicants.user_id', ondelete='CASCADE'), nullable=False)
    raw_text = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    skills = db.relationship('Skill', secondary=resume_skills, backref=db.backref('resumes', lazy='dynamic'))
    rankings = db.relationship('Ranking', backref='resume', lazy=True, cascade='all, delete-orphan')

class Ranking(db.Model):
    __tablename__ = 'rankings'
    __table_args__ = {"schema": "public"}
    
    ranking_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('public.jobs.job_id', ondelete='CASCADE'), nullable=False)
    resume_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('public.resumes.resume_id', ondelete='CASCADE'), nullable=False)
    matching_score = db.Column(db.Float)
    candidate_rank = db.Column(db.Integer)
    status = db.Column(db.String(20), nullable=False, default='Pending')