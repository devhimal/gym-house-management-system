from app import create_app, db
from app.models import Member

app = create_app()
with app.app_context():
    member_count = Member.query.count()
    print(f"Number of members in the database: {member_count}")
