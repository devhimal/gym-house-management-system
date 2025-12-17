from datetime import datetime, timedelta
from app import db, bcrypt # Import bcrypt
from flask_login import UserMixin # Import UserMixin

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    join_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    
    membership_plan_id = db.Column(db.Integer, db.ForeignKey('membership_plan.id'))
    membership_start_date = db.Column(db.Date)
    membership_end_date = db.Column(db.Date)
    
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.id'))
    workout_plan_id = db.Column(db.Integer, db.ForeignKey('workout_plan.id'))

    payments = db.relationship('Payment', backref='member', lazy='dynamic')
    attendances = db.relationship('Attendance', backref='member', lazy='dynamic')

    def is_membership_active(self):
        if self.membership_end_date:
            return self.membership_end_date >= datetime.utcnow().date()
        return False

    def __repr__(self):
        return f'<Member {self.name}>'

class MembershipPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    duration_days = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    members = db.relationship('Member', backref='membership_plan', lazy='dynamic')

    def __repr__(self):
        return f'<MembershipPlan {self.name}>'

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    plan_id = db.Column(db.Integer, db.ForeignKey('membership_plan.id'))

    plan = db.relationship('MembershipPlan')

    def __repr__(self):
        return f'<Payment {self.id}>'

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    check_in_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    check_out_time = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Attendance for Member {self.member_id} at {self.check_in_time}>'

class Trainer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100))
    schedule = db.Column(db.Text) # Simple text field for schedule
    
    members = db.relationship('Member', backref='trainer', lazy='dynamic')

    def __repr__(self):
        return f'<Trainer {self.name}>'

class WorkoutPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    routines = db.Column(db.Text, nullable=False) # Simple text field for routines
    
    members = db.relationship('Member', backref='workout_plan', lazy='dynamic')

    def __repr__(self):
        return f'<WorkoutPlan {self.name}>'

class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Inquiry {self.name}>'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='subscription') # 'admin', 'subscription'
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=True) # New field
    member = db.relationship('Member', backref='user', uselist=False) # Relationship

    goals = db.relationship('Goal', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goal_type = db.Column(db.String(20), nullable=False)  # e.g., 'daily', 'weekly', 'monthly', 'yearly'
    description = db.Column(db.String(255), nullable=False)
    target_value = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(50), nullable=False) # e.g., 'workouts', 'calories', 'kg', 'minutes'
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    is_admin_set = db.Column(db.Boolean, default=False)
    is_beginner_goal = db.Column(db.Boolean, default=False) # If this goal is specifically for beginners
    status = db.Column(db.String(20), default='active') # e.g., 'active', 'completed', 'failed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('goals_set', lazy=True))

    def __repr__(self):
        return f'<Goal {self.description} for User {self.user_id}>'