from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Check if the admin user already exists
    if User.query.filter_by(username='admin').first():
        print("Admin user already exists.")
    else:
        # Create a new admin user
        admin_user = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        admin_user.set_password('admin')
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created successfully.")
