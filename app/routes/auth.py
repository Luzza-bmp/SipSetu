from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User #app/models.py=app.models
import bcrypt
#blueprint is a way to organize a group of related routes and views in a Flask application. 
# #It allows you to modularize your application and keep related functionality together.
# In this case, auth_bp is a Blueprint instance that will contain all the routes related to authentication (like register, login, and me).
auth_bp = Blueprint("auth", __name__)#auth_bp is an object to hold routes (/login, /register, etc.)
 #__name__ = "app.routes.auth"
 #auth in the parameter is the name of the blueprint, which can be used for URL generation and other purposes. It is a unique identifier for the blueprint within the application 
 #like login route becomes auth.login

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() #parses the incoming JSON data from the request body and returns it as a Python dictionary. This allows you to easily access the data sent by the client in a structured format.

    email = data.get("email", "").strip().lower()#if email is missing "" returns an empty string. email is a key of dictionary in data variable
    password = data.get("password", "")
    role = data.get("role", "").strip().lower()

    # Basic validation
    if not email or not password or not role:
        return jsonify({"error": "email, password, and role are required"}), 400

    if role not in ("applicant", "recruiter"):
        return jsonify({"error": "role must be 'applicant' or 'recruiter'"}), 400

    if User.query.filter_by(email=email).first(): #left email is a column in the users table, right email is the variable we just defined. This line checks if there is already a user in the database with the same email address. If such a user exists, it returns an error response indicating that the email is already registered.
        return jsonify({"error": "Email already registered"}), 409

    # Hash password
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8") #bcrypt.hashpw(password_bytes, salt)
    #utf8 converts the password string into bytes, which is required by bcrypt. 
#with salt, bcrypt.gensalt() generates a random unique salt value that is used to enhance the security of the hashed password. The resulting hash is then decoded back into a string format for storage in the database.
    new_user = User(email=email, password_hash=password_hash, role=role)
    db.session.add(new_user) #only stored in the session, not yet in the database. To save it to the database, we need to call db.session.commit() after adding all the new users or making all the changes we want to persist.
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):#encode converts the password string into bytes, which is required by bcrypt. bcrypt.checkpw() compares the provided password (after encoding) with the stored password hash (also after encoding). If the user does not exist or the password does not match, it returns an error response indicating that the email or password is invalid.
        return jsonify({"error": "Invalid email or password"}), 401

    # Create JWT — store user_id and role in token
    access_token = create_access_token(
        identity=str(user.user_id),
        additional_claims={"role": user.role}
    )

    return jsonify({
        "access_token": access_token,
        "role": user.role,
        "user_id": str(user.user_id)
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user_id": str(user.user_id),
        "email": user.email,
        "role": user.role
    }), 200