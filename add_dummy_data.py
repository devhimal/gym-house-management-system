from app import create_app, db
from app.models import MembershipPlan, Trainer, WorkoutPlan, Member, User
from datetime import date, timedelta

app = create_app()
with app.app_context():
    # Check if data already exists to prevent duplicates
    if not MembershipPlan.query.first():
        db.session.add_all([
            MembershipPlan(name='Monthly Basic', duration_days=30, price=30.00),
            MembershipPlan(name='Yearly Premium', duration_days=365, price=300.00)
        ])
        db.session.commit() # Commit after adding plans
        print("Added Membership Plans.")
    else:
        print("Membership Plans already exist.")

    if not Trainer.query.first():
        db.session.add_all([
            Trainer(name='John Doe', specialization='Strength Training'),
            Trainer(name='Jane Smith', specialization='Yoga')
        ])
        db.session.commit() # Commit after adding trainers
        print("Added Trainers.")
    else:
        print("Trainers already exist.")

    if not WorkoutPlan.query.first():
        db.session.add_all([
            WorkoutPlan(name='Beginner Full Body', routines='3 sets of 10 reps: Squats, Bench Press, Rows'),
            WorkoutPlan(name='Advanced Cardio', routines='30 min HIIT, 15 min steady state')
        ])
        db.session.commit() # Commit after adding workout plans
        print("Added Workout Plans.")
    else:
        print("Workout Plans already exist.")

    if not Member.query.first():
        plan1 = MembershipPlan.query.first()
        plan2 = MembershipPlan.query.offset(1).first()
        trainer1 = Trainer.query.first()
        trainer2 = Trainer.query.offset(1).first()
        workout_plan1 = WorkoutPlan.query.first()
        workout_plan2 = WorkoutPlan.query.offset(1).first()

        members = [
            Member(name='Alice Johnson', email='alice@example.com', phone='123-456-7890', join_date=date.today() - timedelta(days=60), membership_plan=plan1, membership_start_date=date.today() - timedelta(days=60), membership_end_date=date.today() + timedelta(days=30), trainer=trainer1, workout_plan=workout_plan1),
            Member(name='Bob Williams', email='bob@example.com', phone='234-567-8901', join_date=date.today() - timedelta(days=90), membership_plan=plan2, membership_start_date=date.today() - timedelta(days=90), membership_end_date=date.today() + timedelta(days=275), trainer=trainer2, workout_plan=workout_plan2),
            Member(name='Charlie Brown', email='charlie@example.com', phone='345-678-9012', join_date=date.today() - timedelta(days=120)),
        ]
        db.session.add_all(members)
        db.session.commit()
        print("Added Members.")

        for member in members:
            if not User.query.filter_by(email=member.email).first():
                user = User(username=member.name.lower().replace(" ", ""), email=member.email, role='subscription')
                user.set_password('password')
                db.session.add(user)
        db.session.commit()
        print("Added Users for Members.")
    else:
        print("Members and Users already exist.")

print("Dummy data addition process complete.")
