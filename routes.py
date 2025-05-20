import os
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from flask import render_template, request, redirect, url_for, flash, abort, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user

from app import app, db
from models import Admin, JobDescription, Application
from resume_parser import extract_text_from_pdf, compute_matching_score
from crud import get_all_jds, get_jd_by_id, create_jd, update_jd, delete_jd, get_all_applications, get_applications_by_jd

# Add template context processor to make 'now' available in all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Home route
@app.route('/')
def index():
    job_descriptions = get_all_jds()
    return render_template('index.html', job_descriptions=job_descriptions)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_reports'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_reports'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

# Application submission route
@app.route('/apply', methods=['GET', 'POST'])
def apply():
    job_descriptions = get_all_jds()
    
    if request.method == 'POST':
        name = request.form.get('name')
        jd_id = request.form.get('jd_id')
        
        # Validate form data
        if not name or not jd_id:
            flash('All fields are required', 'danger')
            return render_template('apply.html', job_descriptions=job_descriptions)
        
        # Check if JD exists
        if not get_jd_by_id(jd_id):
            flash('Invalid job description selected', 'danger')
            return render_template('apply.html', job_descriptions=job_descriptions)
        
        # Handle file upload
        if 'resume' not in request.files:
            flash('No resume file provided', 'danger')
            return render_template('apply.html', job_descriptions=job_descriptions)
        
        file = request.files['resume']
        
        if file.filename == '':
            flash('No file selected', 'danger')
            return render_template('apply.html', job_descriptions=job_descriptions)
        
        if not file.filename.lower().endswith('.pdf'):
            flash('Only PDF files are accepted', 'danger')
            return render_template('apply.html', job_descriptions=job_descriptions)
        
        # Save resume file
        filename = secure_filename(f"{jd_id}_{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extract text from PDF
        try:
            resume_text = extract_text_from_pdf(file_path)
            
            # Get JD text
            jd = get_jd_by_id(jd_id)
            jd_text = jd.description
            
            # Compute matching score
            score = compute_matching_score(resume_text, jd_text)
            shortlisted = score >= 60  # Threshold is 60%
            
            # Create application record
            application = Application(
                name=name,
                resume_path=filename,
                jd_id=jd_id,
                matching_score=score,
                shortlisted=shortlisted
            )
            
            db.session.add(application)
            db.session.commit()
            
            flash('Application submitted successfully', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            logging.error(f"Error processing application: {str(e)}")
            flash('An error occurred while processing your application', 'danger')
            return render_template('apply.html', job_descriptions=job_descriptions)
    
    return render_template('apply.html', job_descriptions=job_descriptions)

# Admin routes
@app.route('/admin/jds')
@login_required
def admin_view_jds():
    job_descriptions = get_all_jds()
    return render_template('admin/view_jds.html', job_descriptions=job_descriptions)

@app.route('/admin/jds/create', methods=['GET', 'POST'])
@login_required
def admin_create_jd():
    if request.method == 'POST':
        jd_id = request.form.get('jd_id')
        description = request.form.get('description')
        
        # Validate form data
        if not jd_id or not description:
            flash('All fields are required', 'danger')
            return render_template('admin/create_jd.html')
        
        # Check if JD ID already exists
        if get_jd_by_id(jd_id):
            flash('Job description ID already exists', 'danger')
            return render_template('admin/create_jd.html')
        
        # Create job description
        create_jd(jd_id, description)
        flash('Job description created successfully', 'success')
        return redirect(url_for('admin_view_jds'))
    
    return render_template('admin/create_jd.html')

@app.route('/admin/jds/<jd_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_jd(jd_id):
    job_description = get_jd_by_id(jd_id)
    
    if not job_description:
        flash('Job description not found', 'danger')
        return redirect(url_for('admin_view_jds'))
    
    if request.method == 'POST':
        description = request.form.get('description')
        
        # Validate form data
        if not description:
            flash('Description is required', 'danger')
            return render_template('admin/edit_jd.html', job_description=job_description)
        
        # Update job description
        update_jd(jd_id, description)
        flash('Job description updated successfully', 'success')
        return redirect(url_for('admin_view_jds'))
    
    return render_template('admin/edit_jd.html', job_description=job_description)

@app.route('/admin/jds/<jd_id>/delete', methods=['POST'])
@login_required
def admin_delete_jd(jd_id):
    job_description = get_jd_by_id(jd_id)
    
    if not job_description:
        flash('Job description not found', 'danger')
        return redirect(url_for('admin_view_jds'))
    
    # Check if there are applications for this JD
    if job_description.applications:
        flash('Cannot delete job description that has applications', 'danger')
        return redirect(url_for('admin_view_jds'))
    
    # Delete job description
    delete_jd(jd_id)
    flash('Job description deleted successfully', 'success')
    return redirect(url_for('admin_view_jds'))

@app.route('/admin/reports')
@login_required
def admin_reports():
    jd_id = request.args.get('jd_id')
    job_descriptions = get_all_jds()
    
    if jd_id:
        applications = get_applications_by_jd(jd_id)
    else:
        applications = get_all_applications()
    
    return render_template('admin/reports.html', 
                           applications=applications, 
                           job_descriptions=job_descriptions,
                           selected_jd=jd_id)

# Route to view resumes
@app.route('/resumes/<filename>')
@login_required
def view_resume(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403
