from app import create_app

app = create_app() #app is an instance of the Flask application created by the create_app function defined in the app package. create_app() returns a configured Flask application instance that can be run to start the web server.
#call the function create_app() and store its result in app
#This function is responsible for setting up the Flask application, including configuring routes, initializing extensions, and any other necessary setup for the application to run properly.
#on postman  http://127.0.0.1:5000/auth/login
if __name__ == "__main__":#. When Python runs a file directly, that file’s special name becomes __main__
#If this file is being executed directly, then start the Flask server”
    app.run(debug=True)#debug=True is used to automatically reload the server when code changes are made, and it also provides detailed error messages in the browser if any issues arise during development.