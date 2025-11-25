from app import create_app, db
from app.models import Member, MembershipPlan, Payment, Attendance, Trainer, WorkoutPlan
import os

# Ensure the instance folder exists
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Member': Member,
        'MembershipPlan': MembershipPlan,
        'Payment': Payment,
        'Attendance': Attendance,
        'Trainer': Trainer,
        'WorkoutPlan': WorkoutPlan
    }

if __name__ == '__main__':
    app.run(debug=True)
