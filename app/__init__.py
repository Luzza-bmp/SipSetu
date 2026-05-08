from flask import Flask #flask is a package where the Flask class is defined. We import it to create an instance of the Flask application.
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy() # () is used to create an instance of the SQLAlchemy class, which will be used to interact with the database. This instance will be initialized with the Flask application later in the create_app function.
jwt = JWTManager()

def create_app():
    app = Flask(__name__)#flask(__name__) creates an instance of the Flask class, which represents the web application.
    # The __name__ variable is passed to Flask to help it determine the root path of the application, which is important for locating resources and templates.
    #__name__ is a special Python variable that tells Flask where this code is located.

#If the file is run directly, __name__ is "__main__"
#only for __init__.py: If it is imported from another module, __name__ is the module name, like "app". app.py importing from app/__init__.py will have __name__ of __init__.py as "app"

    app.config.from_object("app.config.Config")#parameter:go to package app
#open file config.py
#get class Config and loads its attributes like sqlalchemy_database_uri, sqlalchemy_track_modifications, jwt_secret_key into the app.config object.
    #.config is an attribute of the Flask application instance that holds the configuration settings for the application.
    # # it is a dictionary-like object that allows you to store and access various configuration values that your application may need, such as database connection strings, secret keys, and other settings.
    #The from_object method is used to load configuration settings from a specified object, in this case, "app.config.Config". It reads all attributes from that object and copies them into app.config.

#init_app s designed to give each extension only the config it needs, not everything.

    db.init_app(app) #init_app reads app.config and prepares the SQLAlchemy extension to work with the Flask application. It sets up the necessary configurations and connections to the database based on the settings defined in app.config.
    jwt.init_app(app)#enables the JWTManager extension to work with the Flask application. It sets up the necessary configurations for handling JSON Web Tokens (JWTs) in the application, such as secret keys and token expiration settings.

    from app.routes.auth import auth_bp #auth_bp is a Blueprint instance defined in the auth.py file located in the app/routes directory. A Blueprint is a way to organize a group of related routes and views in a Flask application.
    # It allows you to modularize your application and keep related functionality together.
    
    app.register_blueprint(auth_bp, url_prefix="/auth") #register_blueprint is a method of the Flask application instance that is used to register a Blueprint with the application. 
    #It takes two parameters: the Blueprint instance (auth_bp) and an optional url_prefix ("/auth"). The url_prefix is a string that will be prefixed to all routes defined in the Blueprint, meaning that all routes in auth_bp will be accessible under the "/auth" URL path.

    return app