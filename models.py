from datetime import datetime
from app import db
from flask_login import UserMixin

class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class JobDescription(db.Model):
    __tablename__ = 'job_descriptions'
    jd_id = db.Column(db.String(50), primary_key=True)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    applications = db.relationship('Application', backref='job_description', lazy=True)

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    resume_path = db.Column(db.String(255), nullable=False)
    jd_id = db.Column(db.String(50), db.ForeignKey('job_descriptions.jd_id'), nullable=False)
    matching_score = db.Column(db.Float)
    shortlisted = db.Column(db.Boolean, default=False)
    applied_at = db.Column(db.DateTime, default=datetime.now)
