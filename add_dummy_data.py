from app import create_app, db
from app.models import MembershipPlan, Trainer, WorkoutPlan
from datetime import date

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

print("Dummy data addition process complete.")
