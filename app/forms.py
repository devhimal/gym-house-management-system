from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField, FloatField, IntegerField, DateTimeField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Optional, NumberRange, EqualTo, ValidationError
from app.models import MembershipPlan, Trainer, WorkoutPlan, Member, User # Import User
from datetime import date, datetime

class InquiryForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional()])
    message = TextAreaField('Message', validators=[Optional()])
    submit = SubmitField('Submit Inquiry')

class MemberForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional()])
    
    # Dynamically loaded choices for SelectField
    membership_plan = SelectField('Membership Plan', coerce=int, validators=[Optional()])
    membership_start_date = DateField('Membership Start Date', format='%Y-%m-%d', default=date.today, validators=[Optional()])
    membership_end_date = DateField('Membership End Date', format='%Y-%m-%d', validators=[Optional()])

    trainer = SelectField('Assigned Trainer', coerce=int, validators=[Optional()])
    workout_plan = SelectField('Workout Plan', coerce=int, validators=[Optional()])

    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(MemberForm, self).__init__(*args, **kwargs)
        self.membership_plan.choices = [(plan.id, plan.name) for plan in MembershipPlan.query.order_by('name').all()]
        self.membership_plan.choices.insert(0, (0, 'Select a plan')) # Add a default "Select" option

        self.trainer.choices = [(trainer.id, trainer.name) for trainer in Trainer.query.order_by('name').all()]
        self.trainer.choices.insert(0, (0, 'Select a trainer'))

        self.workout_plan.choices = [(wp.id, wp.name) for wp in WorkoutPlan.query.order_by('name').all()]
        self.workout_plan.choices.insert(0, (0, 'Select a workout plan'))

class MemberAndUserForm(MemberForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Member and User')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class MembershipPlanForm(FlaskForm):
    name = StringField('Plan Name', validators=[DataRequired()])
    duration_days = IntegerField('Duration (Days)', validators=[DataRequired(), NumberRange(min=1)])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Submit')

class PaymentForm(FlaskForm):
    member = SelectField('Member', coerce=int, validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    payment_date = DateField('Payment Date', format='%Y-%m-%d', default=date.today, validators=[DataRequired()])
    membership_plan = SelectField('Membership Plan (Optional)', coerce=int, validators=[Optional()])
    submit = SubmitField('Record Payment')

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.member.choices = [(m.id, m.name) for m in Member.query.order_by('name').all()]
        self.member.choices.insert(0, (0, 'Select a member'))

        self.membership_plan.choices = [(plan.id, plan.name) for plan in MembershipPlan.query.order_by('name').all()]
        self.membership_plan.choices.insert(0, (0, 'No specific plan'))

class AttendanceForm(FlaskForm):
    member = SelectField('Member', coerce=int, validators=[DataRequired()])
    check_in_time = DateTimeField('Check-in Time', format='%Y-%m-%d %H:%M', default=datetime.now, validators=[DataRequired()])
    submit = SubmitField('Check In')

    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)
        self.member.choices = [(m.id, m.name) for m in Member.query.order_by('name').all()]
        self.member.choices.insert(0, (0, 'Select a member'))

class TrainerForm(FlaskForm):
    name = StringField('Trainer Name', validators=[DataRequired()])
    specialization = StringField('Specialization', validators=[Optional()])
    schedule = TextAreaField('Schedule', validators=[Optional()])
    submit = SubmitField('Submit')

class WorkoutPlanForm(FlaskForm):
    name = StringField('Plan Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    routines = TextAreaField('Routines', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AdminRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Admin')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
