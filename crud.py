from app import db
from models import JobDescription, Application

# Job Description CRUD operations
def get_all_jds():
    """Get all job descriptions"""
    return JobDescription.query.order_by(JobDescription.created_at.desc()).all()

def get_jd_by_id(jd_id):
    """Get a job description by ID"""
    return JobDescription.query.get(jd_id)

def create_jd(jd_id, description):
    """Create a new job description"""
    jd = JobDescription(jd_id=jd_id, description=description)
    db.session.add(jd)
    db.session.commit()
    return jd

def update_jd(jd_id, description):
    """Update an existing job description"""
    jd = get_jd_by_id(jd_id)
    if jd:
        jd.description = description
        db.session.commit()
    return jd

def delete_jd(jd_id):
    """Delete a job description"""
    jd = get_jd_by_id(jd_id)
    if jd:
        db.session.delete(jd)
        db.session.commit()
    return True

# Application CRUD operations
def get_all_applications():
    """Get all applications"""
    return Application.query.order_by(Application.applied_at.desc()).all()

def get_applications_by_jd(jd_id):
    """Get applications for a specific job description"""
    return Application.query.filter_by(jd_id=jd_id).order_by(Application.applied_at.desc()).all()

def get_application_by_id(application_id):
    """Get an application by ID"""
    return Application.query.get(application_id)
