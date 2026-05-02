from app import create_app

app = create_app()
#on postman  http://127.0.0.1:5000/auth/login
if __name__ == "__main__":
    app.run(debug=True)