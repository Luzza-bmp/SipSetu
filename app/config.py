import os
from dotenv import load_dotenv

load_dotenv() #reads the .env file and loads the environment variables defined in it into the system's environment variables. 
#This allows you to access these variables using os.getenv() in your code, which is useful for keeping sensitive information.

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")