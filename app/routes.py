from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, make_response
from app import db, bcrypt
from app.models import Member, MembershipPlan, Trainer, WorkoutPlan, Payment, Attendance, User, Inquiry
from app.forms import MemberForm, MembershipPlanForm, PaymentForm, AttendanceForm, TrainerForm, WorkoutPlanForm, LoginForm, AdminRegistrationForm, MemberAndUserForm, InquiryForm
from datetime import datetime, timedelta
from flask_login import login_user, current_user, logout_user, login_required

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/home')
def home():
    # This will be the public marketing page
    return render_template('home.html', title='Welcome to Gym House')

@bp.route('/inquiry', methods=['GET', 'POST'])
def inquiry():
    form = InquiryForm()
    if form.validate_on_submit():
        inquiry = Inquiry(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            message=form.message.data
        )
        db.session.add(inquiry)
        db.session.commit()
        flash('Your inquiry has been submitted successfully!', 'success')
        return redirect(url_for('main.home'))
    return render_template('inquiry.html', title='Submit Inquiry', form=form)

# --- Authentication Routes ---



@bp.route('/admin/create_admin', methods=['GET', 'POST'])
@login_required
def create_admin():
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        abort(403)
    form = AdminRegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role='admin')
        password = form.password.data
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()

        flash('Admin account created successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('auth/create_admin.html', title='Create Admin User', form=form)



@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('main.dashboard'))
        else:
            return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if user.role == 'admin':
                return redirect(next_page or url_for('main.dashboard'))
            else:
                return redirect(next_page or url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('auth/login.html', title='Login', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

# --- Admin Dashboard (Protected) ---
@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        abort(403)

    total_members = Member.query.count()
    active_members = Member.query.filter(Member.membership_end_date >= datetime.utcnow().date()).count()
    
    today = datetime.utcnow().date()
    today_checkins = Attendance.query.filter(
        db.func.date(Attendance.check_in_time) == today
    ).count()

    total_revenue = db.session.query(db.func.sum(Payment.amount)).scalar() or 0
    inquiries_count = Inquiry.query.count()

    expiring_members = Member.query.filter(
        Member.membership_end_date >= today,
        Member.membership_end_date <= today + timedelta(days=7)
    ).all()

    members_needing_renewal = Member.query.filter(
        Member.membership_end_date < today,
        Member.membership_end_date != None
    ).all()

    return render_template('admin_dashboard.html', title='Admin Dashboard', 
                           total_members=total_members,
                           active_members=active_members,
                           today_checkins=today_checkins,
                           total_revenue=total_revenue,
                           inquiries_count=inquiries_count,
                           expiring_members=expiring_members,
                           members_needing_renewal=members_needing_renewal)

@bp.route('/admin/inquiries')
@login_required
def list_inquiries():
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        abort(403)
    inquiries = Inquiry.query.order_by(Inquiry.submitted_at.desc()).all()
    return render_template('admin/inquiries.html', title='Inquiries', inquiries=inquiries)

@bp.route('/admin/create_member_and_user', methods=['GET', 'POST'])
@login_required
def create_member_and_user():
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        abort(403)
    form = MemberAndUserForm()
    if form.validate_on_submit():
        member = Member(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            join_date=form.membership_start_date.data,
            membership_start_date=form.membership_start_date.data,
            membership_end_date=form.membership_end_date.data,
            membership_plan_id=form.membership_plan.data if form.membership_plan.data != 0 else None,
            trainer_id=form.trainer.data if form.trainer.data != 0 else None,
            workout_plan_id=form.workout_plan.data if form.workout_plan.data != 0 else None
        )
        db.session.add(member)
        db.session.commit()

        user = User(
            username=form.username.data,
            email=form.email.data,
            role='subscription'
        )
        user.set_password(form.password.data)
        user.member_id = member.id
        db.session.add(user)
        db.session.commit()

        flash('Member and user account created successfully!', 'success')
        return redirect(url_for('main.list_members'))
    return render_template('admin/create_member_and_user.html', title='Create Member and User', form=form)

# --- Member Management Routes ---

@bp.route('/members')
@login_required
def list_members():
    if current_user.role not in ['admin', 'subscription']:
        flash('Access denied. Admins and Subscription users only.', 'danger')
        abort(403)
    
    members = Member.query.all()
    return render_template('members/list.html', title='Members', members=members)

@bp.route('/members/add', methods=['GET', 'POST'])
@login_required
def add_member():
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        abort(403)
    form = MemberForm()
    if form.validate_on_submit():
        member = Member(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            join_date=form.membership_start_date.data,
            membership_start_date=form.membership_start_date.data,
            membership_end_date=form.membership_end_date.data,
            membership_plan_id=form.membership_plan.data if form.membership_plan.data != 0 else None,
            trainer_id=form.trainer.data if form.trainer.data != 0 else None,
            workout_plan_id=form.workout_plan.data if form.workout_plan.data != 0 else None
        )
        db.session.add(member)
        db.session.commit()
        flash('Member added successfully!', 'success')
        return redirect(url_for('main.list_members'))
    return render_template('members/form.html', title='Add Member', form=form)

@bp.route('/members/<int:member_id>')
@login_required
def view_member(member_id):
    if current_user.role not in ['admin', 'subscription']:
        flash('Access denied. Admins and Subscription users only.', 'danger')
        abort(403)
    
    member = Member.query.get_or_404(member_id)
    # Subscription users can only view their own profile
    if current_user.role == 'subscription' and member.email != current_user.email:
        flash('Access denied. You can only view your own profile.', 'danger')
        abort(403)

    return render_template('members/profile.html', title=f'Member: {member.name}', member=member)

@bp.route('/members/edit/<int:member_id>', methods=['GET', 'POST'])
@login_required
def edit_member(member_id):
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        abort(403)
    member = Member.query.get_or_404(member_id)
    form = MemberForm(obj=member)
    if form.validate_on_submit():
        member.name = form.name.data
        member.email = form.email.data
        member.phone = form.phone.data
        member.membership_start_date = form.membership_start_date.data
        member.membership_end_date = form.membership_end_date.data
        member.membership_plan_id = form.membership_plan.data if form.membership_plan.data != 0 else None
        member.trainer_id = form.trainer.data if form.trainer.data != 0 else None
        member.workout_plan_id = form.workout_plan.data if form.workout_plan.data != 0 else None
        
        db.session.commit()
        flash('Member updated successfully!', 'success')
        return redirect(url_for('main.view_member', member_id=member.id))
    return render_template('members/form.html', title=f'Edit Member: {member.name}', form=form, member=member)

@bp.route('/members/export/<int:member_id>')
@login_required
def export_member(member_id):
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        abort(403)
    member = Member.query.get_or_404(member_id)
    
    # Create a string with member details
    details = f"Member ID: {member.id}\n"
    details += f"Name: {member.name}\n"
    details += f"Email: {member.email}\n"
    details += f"Phone: {member.phone}\n"
    details += f"Join Date: {member.join_date.strftime('%Y-%m-%d') if member.join_date else 'N/A'}\n"
    
    if member.membership_plan:
        details += f"Membership Plan: {member.membership_plan.name}\n"
        details += f"Membership Start Date: {member.membership_start_date.strftime('%Y-%m-%d') if member.membership_start_date else 'N/A'}\n"
        details += f"Membership End Date: {member.membership_end_date.strftime('%Y-%m-%d') if member.membership_end_date else 'N/A'}\n"
    else:
        details += "Membership Plan: N/A\n"
        
    if member.trainer:
        details += f"Trainer: {member.trainer.name}\n"
    else:
        details += "Trainer: N/A\n"
        
    if member.workout_plan:
        details += f"Workout Plan: {member.workout_plan.name}\n"
    else:
        details += "Workout Plan: N/A\n"
        
    # Create a response with the text file
    response = make_response(details)
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Disposition'] = f'attachment; filename=member_{member.id}_details.txt'
    
    return response

@bp.route('/members/delete/<int:member_id>', methods=['POST'])
@login_required
def delete_member(member_id):
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        abort(403)
    member = Member.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    flash('Member deleted successfully!', 'success')
    return redirect(url_for('main.list_members'))

# --- Membership Plan Management Routes ---

@bp.route('/plans')
@login_required
def list_plans():
    if current_user.role not in ['admin', 'subscription']:
        flash('Access denied. Admins and Subscription users only.', 'danger')
        abort(403)
    plans = MembershipPlan.query.all()
    return render_template('plans/list.html', title='Membership Plans', plans=plans)

@bp.route('/plans/add', methods=['GET', 'POST'])
@login_required
def add_plan():
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        abort(403)
    form = MembershipPlanForm()
    if form.validate_on_submit():
        plan = MembershipPlan(
            name=form.name.data,
            duration_days=form.duration_days.data,
            price=form.price.data
        )
        db.session.add(plan)
        db.session.commit()
        flash('Membership plan added successfully!', 'success')
        return redirect(url_for('main.list_plans'))
    return render_template('plans/form.html', title='Add Membership Plan', form=form)

@bp.route('/plans/edit/<int:plan_id>', methods=['GET', 'POST'])
@login_required
def edit_plan(plan_id):
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        abort(403)
    plan = MembershipPlan.query.get_or_404(plan_id)
    form = MembershipPlanForm(obj=plan)
    if form.validate_on_submit():
        plan.name = form.name.data
        plan.duration_days = form.duration_days.data
        plan.price = form.price.data
        db.session.commit()
        flash('Membership plan updated successfully!', 'success')
        return redirect(url_for('main.list_plans'))
    return render_template('plans/form.html', title=f'Edit Membership Plan: {plan.name}', form=form)

@bp.route('/plans/delete/<int:plan_id>', methods=['POST'])
@login_required
def delete_plan(plan_id):
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        abort(403)
    plan = MembershipPlan.query.get_or_404(plan_id)
    if plan.members.count() > 0:
        flash('Cannot delete plan: Members are currently assigned to it.', 'danger')
    else:
        db.session.delete(plan)
        db.session.commit()
        flash('Membership plan deleted successfully!', 'success')
    return redirect(url_for('main.list_plans'))

# --- Payment Management Routes ---

@bp.route('/payments')
@login_required
def list_payments():
    if current_user.role not in ['admin', 'subscription']:
        flash('Access denied. Admins and Subscription users only.', 'danger')
        abort(403)
    
    if current_user.role == 'subscription':
        member = Member.query.filter_by(email=current_user.email).first()
        if member:
            payments = Payment.query.filter_by(member_id=member.id).order_by(Payment.payment_date.desc()).all()
        else:
            payments = []
    else: # Admin
        payments = Payment.query.order_by(Payment.payment_date.desc()).all()
    
    return render_template('payments/list.html', title='Payments', payments=payments)

@bp.route('/payments/add', methods=['GET', 'POST'])
@login_required
def add_payment():
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        abort(403)
    form = PaymentForm()
    if form.validate_on_submit():
        member = Member.query.get(form.member.data)
        if not member:
            flash('Selected member does not exist.', 'danger')
            return render_template('payments/form.html', title='Record Payment', form=form)

        payment = Payment(
            member_id=form.member.data,
            amount=form.amount.data,
            payment_date=form.payment_date.data,
            plan_id=form.membership_plan.data if form.membership_plan.data != 0 else None
        )
        db.session.add(payment)
        
        if payment.plan_id:
            membership_plan = MembershipPlan.query.get(payment.plan_id)
            if membership_plan:
                if not member.membership_start_date:
                    member.membership_start_date = payment.payment_date
                    member.membership_end_date = payment.payment_date + timedelta(days=membership_plan.duration_days)
                elif member.membership_end_date and member.membership_end_date >= payment.payment_date:
                    member.membership_end_date += timedelta(days=membership_plan.duration_days)
                else:
                    member.membership_start_date = payment.payment_date
                    member.membership_end_date = payment.payment_date + timedelta(days=membership_plan.duration_days)
        
        db.session.commit()
        flash('Payment recorded successfully!', 'success')
        return redirect(url_for('main.list_payments'))
    return render_template('payments/form.html', title='Record Payment', form=form)

# --- Attendance Tracking Routes ---

@bp.route('/attendance')
@login_required
def list_attendance():
    if current_user.role not in ['admin', 'subscription']:
        flash('Access denied. Admins and Subscription users only.', 'danger')
        abort(403)
    
    if current_user.role == 'subscription':
        member = Member.query.filter_by(email=current_user.email).first()
        if member:
            attendance_records = Attendance.query.filter_by(member_id=member.id).order_by(Attendance.check_in_time.desc()).all()
        else:
            attendance_records = []
    else: # Admin
        attendance_records = Attendance.query.order_by(Attendance.check_in_time.desc()).all()
    
    return render_template('attendance/list.html', title='Attendance Records', attendance_records=attendance_records)

@bp.route('/attendance/checkin', methods=['GET', 'POST'])
@login_required
def check_in():
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        abort(403)
    form = AttendanceForm()
    if form.validate_on_submit():
        member = Member.query.get(form.member.data)
        if not member:
            flash('Selected member does not exist.', 'danger')
            return render_template('attendance/checkin_form.html', title='Member Check-in', form=form)
        
        if not member.is_membership_active():
            flash(f'Member {member.name} does not have an active membership.', 'warning')
            
        attendance = Attendance(
            member_id=form.member.data,
            check_in_time=form.check_in_time.data
        )
        db.session.add(attendance)
        db.session.commit()
        flash(f'Member {member.name} checked in successfully!', 'success')
        return redirect(url_for('main.list_attendance'))
    return render_template('attendance/checkin_form.html', title='Member Check-in', form=form)

@bp.route('/attendance/checkout/<int:attendance_id>', methods=['POST'])
@login_required
def check_out(attendance_id):
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        abort(403)
    attendance = Attendance.query.get_or_404(attendance_id)
    if not attendance.check_out_time:
        attendance.check_out_time = datetime.utcnow()
        db.session.commit()
        flash(f'Member {attendance.member.name} checked out successfully!', 'success')
    else:
        flash('Member already checked out.', 'info')
    return redirect(url_for('main.list_attendance'))

# --- Trainer Management Routes ---

@bp.route('/trainers')
@login_required
def list_trainers():
    if current_user.role not in ['admin', 'subscription']:
        flash('Access denied. Admins and Subscription users only.', 'danger')
        abort(403)
    
    trainers = Trainer.query.all()
    
    return render_template('trainers/list.html', title='Trainers', trainers=trainers)

@bp.route('/trainers/add', methods=['GET', 'POST'])
@login_required
def add_trainer():
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        abort(403)
    form = TrainerForm()
    if form.validate_on_submit():
        trainer = Trainer(
            name=form.name.data,
            specialization=form.specialization.data,
            schedule=form.schedule.data
        )
        db.session.add(trainer)
        db.session.commit()
        flash('Trainer added successfully!', 'success')
        return redirect(url_for('main.list_trainers'))
    return render_template('trainers/form.html', title='Add Trainer', form=form)

@bp.route('/trainers/edit/<int:trainer_id>', methods=['GET', 'POST'])
@login_required
def edit_trainer(trainer_id):
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        abort(403)
    trainer = Trainer.query.get_or_404(trainer_id)
    form = TrainerForm(obj=trainer)
    if form.validate_on_submit():
        trainer.name = form.name.data
        trainer.specialization = form.specialization.data
        trainer.schedule = form.schedule.data
        db.session.commit()
        flash('Trainer updated successfully!', 'success')
        return redirect(url_for('main.list_trainers'))
    return render_template('trainers/form.html', title=f'Edit Trainer: {trainer.name}', form=form)

@bp.route('/trainers/delete/<int:trainer_id>', methods=['POST'])
@login_required
def delete_trainer(trainer_id):
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        abort(403)
    trainer = Trainer.query.get_or_404(trainer_id)
    if trainer.members.count() > 0:
        flash('Cannot delete trainer: Members are currently assigned to them.', 'danger')
    else:
        db.session.delete(trainer)
        db.session.commit()
        flash('Trainer deleted successfully!', 'success')
    return redirect(url_for('main.list_trainers'))

# --- Workout Plan Management Routes ---

@bp.route('/workout_plans')
@login_required
def list_workout_plans():
    if current_user.role not in ['admin', 'subscription']:
        flash('Access denied. Admins and Subscription users only.', 'danger')
        abort(403)
    
    workout_plans = WorkoutPlan.query.all()
    
    return render_template('workout_plans/list.html', title='Workout Plans', workout_plans=workout_plans)

@bp.route('/workout_plans/add', methods=['GET', 'POST'])
@login_required
def add_workout_plan():
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        abort(403)
    form = WorkoutPlanForm()
    if form.validate_on_submit():
        workout_plan = WorkoutPlan(
            name=form.name.data,
            description=form.description.data,
            routines=form.routines.data
        )
        db.session.add(workout_plan)
        db.session.commit()
        flash('Workout plan added successfully!', 'success')
        return redirect(url_for('main.list_workout_plans'))
    return render_template('workout_plans/form.html', title='Add Workout Plan', form=form)

@bp.route('/workout_plans/edit/<int:plan_id>', methods=['GET', 'POST'])
@login_required
def edit_workout_plan(plan_id):
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        abort(403)
    workout_plan = WorkoutPlan.query.get_or_404(plan_id)
    form = WorkoutPlanForm(obj=workout_plan)
    if form.validate_on_submit():
        workout_plan.name = form.name.data
        workout_plan.description = form.description.data
        workout_plan.routines = form.routines.data
        db.session.commit()
        flash('Workout plan updated successfully!', 'success')
        return redirect(url_for('main.list_workout_plans'))
    return render_template('workout_plans/form.html', title=f'Edit Workout Plan: {workout_plan.name}', form=form)

@bp.route('/workout_plans/delete/<int:plan_id>', methods=['POST'])
@login_required
def delete_workout_plan(plan_id):
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        abort(403)
    workout_plan = WorkoutPlan.query.get_or_404(plan_id)
    if workout_plan.members.count() > 0:
        flash('Cannot delete workout plan: Members are currently assigned to it.', 'danger')
    else:
        db.session.delete(workout_plan)
        db.session.commit()
        flash('Workout plan deleted successfully!', 'success')
    return redirect(url_for('main.list_workout_plans'))
