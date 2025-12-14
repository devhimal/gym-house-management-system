# Gym House Management System

## Project Overview

The Gym House Management System is a comprehensive web application built with Flask, designed to streamline the daily operations of a gym. It provides essential functionalities for member management, membership plans, payments, attendance tracking, staff/trainer management, workout plans, and an administrative dashboard. The system also incorporates user authentication with role-based access control (RBAC) to ensure secure and tailored experiences for different user types (Admin, Subscription User, Normal User).

## Features

The application includes the following key features:

*   **User Authentication & Authorization (RBAC):**
    *   Secure user registration, login, and logout.
    *   Three distinct user roles: `Admin`, `Subscription User`, and `Normal User`.
    *   Role-based access control applied to all routes, restricting access to unauthorized users.
    *   Subscription users are automatically linked to their corresponding member profiles based on email during registration.
*   **Public Home Page:**
    *   A marketing-focused landing page with a hero section, call-to-action (CTA), features showcase, advantages, and user testimonials.
    *   Custom styling for an appealing user interface.
*   **Admin Dashboard:**
    *   A dedicated, protected dashboard providing administrators with an overview of key metrics:
        *   Total Members
        *   Active vs. Expired Memberships
        *   Today's Check-ins
        *   Total Revenue
    *   Basic notification alerts for expiring memberships and members needing renewal.
*   **Member Management:**
    *   Full CRUD (Create, Read, Update, Delete) operations for member profiles.
    *   Tracking of membership start and end dates.
    *   Admin-only access for managing all members.
    *   Subscription users can view their own member profile.
*   **Membership Plans:**
    *   CRUD operations for creating and managing various membership packages (e.g., monthly, yearly).
    *   Admin-only access for managing plans.
    *   Subscription users can view all available plans.
*   **Payments & Billing:**
    *   Record and track member payments.
    *   Automatic update of member's `membership_end_date` upon payment for a plan.
    *   Admin-only access for recording payments.
    *   Subscription users can view their own payment history.
*   **Attendance Tracking:**
    *   Record daily member check-ins and check-outs.
    *   Admin-only access for managing attendance records.
    *   Subscription users can view their own attendance records.
*   **Staff/Trainer Management:**
    *   CRUD operations for managing gym trainers and staff.
    *   Ability to store trainer specializations and schedules.
    *   Admin-only access for managing trainers.
    *   Subscription users can view details of their assigned trainer.
*   **Workout Plan Management:**
    *   CRUD operations for creating and managing basic workout routines.
    *   Admin-only access for managing workout plans.
    *   Subscription users can view their assigned workout plan.
*   **Error Handling:**
    *   Dedicated "Permission Denied" (HTTP 403 Forbidden) page for unauthorized access attempts.

## Technology Stack

*   **Backend:** Python, Flask
*   **Database:** SQLite (via SQLAlchemy ORM)
*   **Database Migrations:** Flask-Migrate (Alembic)
*   **Forms:** Flask-WTF, WTForms
*   **Authentication:** Flask-Login, Flask-Bcrypt (for password hashing)
*   **Frontend:** HTML5, CSS3, Bootstrap 5
*   **Email Validation:** `email_validator`

## Setup Instructions

Follow these steps to get the project up and running on your local machine.

### Prerequisites

*   Python 3.8+
*   `pip` (Python package installer)

### 1. Clone the Repository

```bash
git clone <repository_url> # Replace <repository_url> with your actual repository URL
cd gym-house-management-system
```

### 2. Create and Activate a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
python3 -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

Install all required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

### 4. Initialize and Migrate the Database

Set up the database schema using Flask-Migrate. If this is your first time setting up the project, you'll need to initialize the migration repository:

```bash
export FLASK_APP=run.py # On Windows: set FLASK_APP=run.py
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

After any changes to `app/models.py`, you will need to create a new migration and upgrade the database:

```bash
export FLASK_APP=run.py # On Windows: set FLASK_APP=run.py
flask db migrate -m "A meaningful message about your changes"
flask db upgrade
```

### 5. Running the Application

Start the Flask development server:

```bash
export FLASK_APP=run.py # On Windows: set FLASK_APP=run.py
flask run
```

The application will typically run on `http://127.0.0.1:5000/`.

## Usage

### Accessing the Application

Open your web browser and navigate to `http://127.0.0.1:5000/`.

### User Roles and Access

*   **Normal User:** Can only view the public home page (`/` or `/home`). Any attempt to access protected routes will result in a "Permission Denied" page.
*   **Subscription User:**
    *   Can view the public home page.
    *   Can view all Membership Plans (`/plans`).
    *   Can view all Trainers (`/trainers`).
    *   Can view all Workout Plans (`/workout_plans`).
    *   Can view their own Payment History (`/payments`).
    *   Can view their own Attendance Records (`/attendance`).
    *   Can view their own Member Profile (`/members/<member_id>`).
    *   Cannot access admin-only features (e.g., adding/editing members, plans, payments, etc.).
*   **Admin User:**
    *   Has full access to all features and management functionalities.
    *   Can access the Admin Dashboard (`/dashboard`).
    *   Can perform all CRUD operations on Members, Plans, Payments, Attendance, Trainers, and Workout Plans.
    *   Can create new Admin users via `/admin/create_admin`.
    *   Can create new Members and their associated Subscription User accounts via `/admin/create_member_and_user`.
    *   Can view inquiries via `/admin/inquiries`.

### Important Notes for Testing

*   **Create an Admin User:** To gain full access to the management features, you must first create an admin user. If you don't have one, you can create one by running the `create_admin.py` script (if it exists and you haven't run it before) or by manually inserting a user into the database with `role='admin'`.
    *   **Default Admin (if created by script):**
        *   Username: `admin`
        *   Email: `admin@example.com`
        *   Password: `admin`
*   **Creating Members and Subscription Users:**
    *   Use the `/admin/create_member_and_user` route (accessible after logging in as an admin) to create new member profiles and their associated subscription user accounts.
    *   The system will automatically link the created user to the member profile.
*   **Submitting Inquiries:**
    *   Users can submit inquiries via the `/inquiry` route (linked from the "Join Now" button on the home page).
    *   Admins can view submitted inquiries on the dashboard or directly via `/admin/inquiries`.