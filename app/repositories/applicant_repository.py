from app import db
from app.models import Applicant


def save_applicant(user_id, data):

    applicant = Applicant.query.get(user_id)
    if not applicant:
        applicant = Applicant(user_id=user_id)
        db.session.add(applicant)

    applicant.name = data["name"]
    applicant.email = data["email"]
    applicant.phone = data["phone"]
    applicant.education = ",".join(data["education"])
    applicant.experience = data["experience"]
    applicant.skills = data["skills"]

    db.session.commit()

    return applicant.user_id
