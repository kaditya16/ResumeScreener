from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('Application', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class JobDescription(db.Model):
    __tablename__ = 'job_descriptions'
    
    jd_id = db.Column(db.String(100), primary_key=True)
    headline = db.Column(db.String(255), nullable=False)
    short_description = db.Column(db.Text)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    applications = db.relationship('Application', backref='job_description', lazy=True)
    
    def to_dict(self):
        # Count applications using a query instead of relationship length
        from sqlalchemy import func
        application_count = db.session.query(func.count(Application.id)).filter_by(jd_id=self.jd_id).scalar() or 0
        
        return {
            'jd_id': self.jd_id,
            'headline': self.headline,
            'short_description': self.short_description,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'application_count': application_count
        }

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    resume_path = db.Column(db.String(500), nullable=False)
    jd_id = db.Column(db.String(100), db.ForeignKey('job_descriptions.jd_id'), nullable=False)
    matching_score = db.Column(db.Float)
    shortlisted = db.Column(db.Boolean, default=False)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    resume_text = db.Column(db.Text)  # Store extracted text for faster searching
    
    def to_dict(self):
        # Get user and job info using queries to avoid backref issues
        user_email = None
        job_headline = None
        
        if self.user_id:
            user = db.session.query(User).filter_by(id=self.user_id).first()
            if user:
                user_email = user.email
                
        if self.jd_id:
            job = db.session.query(JobDescription).filter_by(jd_id=self.jd_id).first()
            if job:
                job_headline = job.headline
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'resume_path': self.resume_path,
            'jd_id': self.jd_id,
            'matching_score': self.matching_score,
            'shortlisted': self.shortlisted,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'user_email': user_email,
            'job_headline': job_headline
        }
