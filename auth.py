from functools import wraps
from flask import session, redirect, url_for, request, flash
from models import db, User

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current logged in user"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def login_user(user):
    """Log in a user by setting session"""
    session['user_id'] = user.id
    session['user_email'] = user.email
    session['is_admin'] = user.is_admin

def logout_user():
    """Log out current user by clearing session"""
    session.clear()

def create_user(email, password, is_admin=False):
    """Create a new user"""
    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return None, "Email already registered"
    
    # Create new user
    user = User()
    user.email = email
    user.is_admin = is_admin
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        return user, None
    except Exception as e:
        db.session.rollback()
        return None, f"Error creating user: {str(e)}"

def authenticate_user(email, password):
    """Authenticate user with email and password"""
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return user
    return None
