from login import app, db1  # Replace with the actual name of your application file

with app.app_context():
    db1.create_all()  # This will create all tables defined in your models
    print("Database and tables created.")
