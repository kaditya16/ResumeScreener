from flask import render_template, request, redirect, url_for, flash, session, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import uuid
from models import db, User, JobDescription, Application
from auth import login_required, admin_required, login_user, logout_user, create_user, authenticate_user, get_current_user
from resume_parser import analyze_resume

def register_web_routes(app):
    
    @app.route('/')
    def index():
        """Homepage showing all job descriptions"""
        job_descriptions = JobDescription.query.filter_by(is_active=True).all()
        current_user = get_current_user()
        return render_template('index.html', job_descriptions=job_descriptions, current_user=current_user)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login page"""
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            
            user = authenticate_user(email, password)
            if user:
                login_user(user)
                flash('Login successful!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Invalid email or password.', 'error')
        
        return render_template('login.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """User registration page"""
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            if password != confirm_password:
                flash('Passwords do not match.', 'error')
                return render_template('register.html')
            
            user, error = create_user(email, password)
            if user:
                login_user(user)
                flash('Registration successful! Welcome!', 'success')
                return redirect(url_for('index'))
            else:
                flash(error, 'error')
        
        return render_template('register.html')
    
    @app.route('/logout')
    def logout():
        """User logout"""
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))
    
    @app.route('/apply/<jd_id>')
    @login_required
    def apply(jd_id):
        """Application form for specific job"""
        job_description = JobDescription.query.get_or_404(jd_id)
        current_user = get_current_user()
        
        # Check if user already applied
        existing_application = Application.query.filter_by(
            user_id=current_user.id,
            jd_id=jd_id
        ).first()
        
        return render_template('apply.html', 
                             job_description=job_description, 
                             current_user=current_user,
                             existing_application=existing_application)
    
    @app.route('/submit_application', methods=['POST'])
    @login_required
    def submit_application():
        """Handle application submission"""
        current_user = get_current_user()
        
        name = request.form['name']
        jd_id = request.form['jd_id']
        
        # Check if file was uploaded
        if 'resume' not in request.files:
            flash('No resume file uploaded.', 'error')
            return redirect(url_for('apply', jd_id=jd_id))
        
        file = request.files['resume']
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(url_for('apply', jd_id=jd_id))
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            flash('Only PDF files are allowed.', 'error')
            return redirect(url_for('apply', jd_id=jd_id))
        
        # Check if user already applied
        existing_application = Application.query.filter_by(
            user_id=current_user.id,
            jd_id=jd_id
        ).first()
        
        if existing_application:
            flash('You have already applied for this position.', 'warning')
            return redirect(url_for('apply', jd_id=jd_id))
        
        # Get job description
        job_description = JobDescription.query.get(jd_id)
        if not job_description:
            flash('Job description not found.', 'error')
            return redirect(url_for('index'))
        
        try:
            # Create unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save file
            file.save(file_path)
            
            # Analyze resume
            analysis = analyze_resume(file_path, job_description.description)
            
            # Create application record
            application = Application(
                user_id=current_user.id,
                name=name,
                resume_path=file_path,
                jd_id=jd_id,
                matching_score=analysis['similarity_score'],
                shortlisted=analysis['shortlisted'],
                resume_text=analysis['text']
            )
            
            db.session.add(application)
            db.session.commit()
            
            if analysis['shortlisted']:
                flash(f'Application submitted successfully! You have been shortlisted with a matching score of {analysis["similarity_score"]:.1f}%.', 'success')
            else:
                flash(f'Application submitted successfully! Your matching score is {analysis["similarity_score"]:.1f}%.', 'info')
            
            return redirect(url_for('index'))
            
        except Exception as e:
            # Clean up file if it was created
            if os.path.exists(file_path):
                os.remove(file_path)
            db.session.rollback()
            flash(f'Error processing application: {str(e)}', 'error')
            return redirect(url_for('apply', jd_id=jd_id))
    
    @app.route('/admin')
    @admin_required
    def admin_dashboard():
        """Admin dashboard homepage"""
        # Get statistics
        total_applications = Application.query.count()
        shortlisted_applications = Application.query.filter_by(shortlisted=True).count()
        total_jds = JobDescription.query.filter_by(is_active=True).count()
        
        stats = {
            'total_applications': total_applications,
            'shortlisted_applications': shortlisted_applications,
            'total_jds': total_jds,
            'shortlist_rate': round((shortlisted_applications / total_applications * 100) if total_applications > 0 else 0, 2)
        }
        
        current_user = get_current_user()
        return render_template('admin/reports.html', stats=stats, current_user=current_user)
    
    @app.route('/admin/create_jd', methods=['GET', 'POST'])
    @admin_required
    def create_jd():
        """Create new job description"""
        if request.method == 'POST':
            jd_id = request.form['jd_id']
            headline = request.form['headline']
            short_description = request.form['short_description']
            description = request.form['description']
            
            # Check if JD ID already exists
            existing_jd = JobDescription.query.get(jd_id)
            if existing_jd:
                flash('Job Description ID already exists.', 'error')
                return render_template('admin/create_jd.html', current_user=get_current_user())
            
            # Create new job description
            jd = JobDescription(
                jd_id=jd_id,
                headline=headline,
                short_description=short_description,
                description=description
            )
            
            try:
                db.session.add(jd)
                db.session.commit()
                flash('Job description created successfully!', 'success')
                return redirect(url_for('admin_dashboard'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating job description: {str(e)}', 'error')
        
        current_user = get_current_user()
        return render_template('admin/create_jd.html', current_user=current_user)
    
    @app.route('/admin/jd/<jd_id>/edit', methods=['GET', 'POST'])
    @admin_required
    def edit_jd(jd_id):
        """Edit existing job description"""
        jd = JobDescription.query.get_or_404(jd_id)
        
        if request.method == 'POST':
            jd.headline = request.form['headline']
            jd.short_description = request.form['short_description']
            jd.description = request.form['description']
            
            try:
                db.session.commit()
                flash('Job description updated successfully!', 'success')
                return redirect(url_for('admin_dashboard'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating job description: {str(e)}', 'error')
        
        current_user = get_current_user()
        return render_template('admin/create_jd.html', jd=jd, current_user=current_user)
    
    @app.route('/admin/jd/<jd_id>/delete', methods=['POST'])
    @admin_required
    def delete_jd(jd_id):
        """Delete job description"""
        jd = JobDescription.query.get_or_404(jd_id)
        jd.is_active = False
        
        try:
            db.session.commit()
            flash('Job description deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting job description: {str(e)}', 'error')
        
        return redirect(url_for('admin_dashboard'))
    
    @app.route('/admin/applications')
    @admin_required
    def view_applications():
        """View all applications"""
        jd_id = request.args.get('jd_id')
        shortlisted_only = request.args.get('shortlisted') == 'true'
        
        query = Application.query
        
        if jd_id:
            query = query.filter_by(jd_id=jd_id)
        
        if shortlisted_only:
            query = query.filter_by(shortlisted=True)
        
        applications = query.order_by(Application.applied_at.desc()).all()
        job_descriptions = JobDescription.query.filter_by(is_active=True).all()
        
        current_user = get_current_user()
        return render_template('admin/reports.html', 
                             applications=applications,
                             job_descriptions=job_descriptions,
                             current_user=current_user,
                             selected_jd=jd_id,
                             shortlisted_only=shortlisted_only)
    
    @app.route('/admin/application/<int:app_id>/toggle_shortlist', methods=['POST'])
    @admin_required
    def toggle_shortlist(app_id):
        """Toggle shortlist status"""
        application = Application.query.get_or_404(app_id)
        application.shortlisted = not application.shortlisted
        
        try:
            db.session.commit()
            status = "shortlisted" if application.shortlisted else "removed from shortlist"
            flash(f'Application {status} successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating application: {str(e)}', 'error')
        
        return redirect(url_for('view_applications'))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
