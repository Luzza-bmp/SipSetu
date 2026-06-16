import uuid
from app import db
from pgvector.sqlalchemy import Vector

class User(db.Model):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    user_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) #attribute name should be user_id, not id, because in the database, the column is named user_id. If we use id, it will not match the column name in the database and will cause an error when trying to access or manipulate user records.
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)


class Recruiter(db.Model):
    __tablename__ = "recruiters"
    __table_args__ = {"schema": "public"}
 
    user_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("public.users.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    jobs = db.relationship("Job", back_populates="recruiter", cascade="all, delete-orphan")
 
 
class Applicant(db.Model):
    __tablename__ = "applicants"
    __table_args__ = {"schema": "public"}
 
    user_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("public.users.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    resumes      = db.relationship("Resume",      back_populates="applicant", cascade="all, delete-orphan")
    applications = db.relationship("Application", back_populates="applicant", cascade="all, delete-orphan")
 
 
# ─────────────────────────────────────────
# Skills  (unchanged)
# ─────────────────────────────────────────
 
class Skill(db.Model):
    __tablename__ = "skills"
    __table_args__ = {"schema": "public"}
 
    skill_id   = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_name = db.Column(db.String(100), unique=True, nullable=False)
 
 
# ─────────────────────────────────────────
# Job  (+ description & required_experience)
# ─────────────────────────────────────────
 
job_skills = db.Table(
    "job_skills",
    db.metadata,
    db.Column("job_id",   db.UUID(as_uuid=True), db.ForeignKey("public.jobs.job_id",   ondelete="CASCADE")),
    db.Column("skill_id", db.UUID(as_uuid=True), db.ForeignKey("public.skills.skill_id", ondelete="CASCADE")),
    schema="public",
)
 
 
class Job(db.Model):
    __tablename__ = "jobs"
    __table_args__ = {"schema": "public"}
 
    job_id                   = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recruiter_id             = db.Column(db.UUID(as_uuid=True), db.ForeignKey("public.recruiters.user_id", ondelete="CASCADE"), nullable=False)
    title                    = db.Column(db.String(255), nullable=False)
    description              = db.Column(db.Text)                      # NEW – used for semantic ranking
    required_experience_years = db.Column(db.Numeric(4, 1), default=0) # NEW
    created_at               = db.Column(db.DateTime, server_default=db.func.current_timestamp())
 
    recruiter    = db.relationship("Recruiter", back_populates="jobs")
    skills       = db.relationship("Skill", secondary=job_skills)
    applications = db.relationship("Application", back_populates="job", cascade="all, delete-orphan")
    rankings     = db.relationship("Ranking",     back_populates="job", cascade="all, delete-orphan")
 
 
# ─────────────────────────────────────────
# Resume  (+ embedding + parsed fields)
# ─────────────────────────────────────────
 
resume_skills = db.Table(
    "resume_skills",
    db.metadata,
    db.Column("resume_id", db.UUID(as_uuid=True), db.ForeignKey("public.resumes.resume_id", ondelete="CASCADE")),
    db.Column("skill_id",  db.UUID(as_uuid=True), db.ForeignKey("public.skills.skill_id",   ondelete="CASCADE")),
    schema="public",
)
 
 
class Resume(db.Model):
    __tablename__ = "resumes"
    __table_args__ = {"schema": "public"}
 
    resume_id                = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    applicant_id             = db.Column(db.UUID(as_uuid=True), db.ForeignKey("public.applicants.user_id", ondelete="CASCADE"), nullable=False)
    raw_text                 = db.Column(db.Text)
    file_path                = db.Column(db.String(500))
    uploaded_at              = db.Column(db.DateTime, server_default=db.func.current_timestamp())
 
    # ── NEW columns (added by migration 003) ──────────────────────────────
    embedding                = db.Column(Vector(384))          # 384-dim from all-MiniLM-L6-v2
    parsed_skills            = db.Column(db.Text)              # pipe-separated, e.g. "Python|Django|SQL"
    parsed_experience_years  = db.Column(db.Numeric(4, 1))     # float years total
 
    applicant = db.relationship("Applicant", back_populates="resumes")
    skills    = db.relationship("Skill", secondary=resume_skills)
 
 
# ─────────────────────────────────────────
# Application  (NEW — explicit apply step)
# ─────────────────────────────────────────
 
class Application(db.Model):
    __tablename__ = "applications"
    __table_args__ = (
        db.UniqueConstraint("job_id", "applicant_id", name="applications_unique"),
        {"schema": "public"},
    )
 
    application_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id         = db.Column(db.UUID(as_uuid=True), db.ForeignKey("public.jobs.job_id",          ondelete="CASCADE"), nullable=False)
    applicant_id   = db.Column(db.UUID(as_uuid=True), db.ForeignKey("public.applicants.user_id",   ondelete="CASCADE"), nullable=False)
    applied_at     = db.Column(db.DateTime, server_default=db.func.current_timestamp())
 
    job      = db.relationship("Job",       back_populates="applications")
    applicant = db.relationship("Applicant", back_populates="applications")
 
 
# ─────────────────────────────────────────
# Ranking  (+ semantic / experience scores)
# ─────────────────────────────────────────
 
class Ranking(db.Model):
    __tablename__ = "rankings"
    __table_args__ = {"schema": "public"}
 
    ranking_id        = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id            = db.Column(db.UUID(as_uuid=True), db.ForeignKey("public.jobs.job_id",     ondelete="CASCADE"), nullable=False)
    resume_id         = db.Column(db.UUID(as_uuid=True), db.ForeignKey("public.resumes.resume_id", ondelete="CASCADE"), nullable=False)
    matching_score    = db.Column(db.Float)   # final weighted score (kept for compat)
    semantic_score    = db.Column(db.Float)   # cosine similarity component
    experience_score  = db.Column(db.Float)   # experience proximity component
    candidate_rank    = db.Column(db.Integer)
    status            = db.Column(db.String(20), nullable=False, default="Pending")
 
    job = db.relationship("Job", back_populates="rankings")