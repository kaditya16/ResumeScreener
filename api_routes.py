from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import os
from werkzeug.utils import secure_filename
from models import db, User, JobDescription, Application
from resume_parser import analyze_resume
import uuid
from datetime import datetime

# Pydantic models for API
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_admin: bool = False

class UserResponse(BaseModel):
    id: int
    email: str
    is_admin: bool
    created_at: Optional[str] = None

class JobDescriptionCreate(BaseModel):
    jd_id: str
    headline: str
    short_description: Optional[str] = None
    description: str

class JobDescriptionResponse(BaseModel):
    jd_id: str
    headline: str
    short_description: Optional[str] = None
    description: str
    created_at: Optional[str] = None
    is_active: bool
    application_count: int

class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    name: str
    resume_path: str
    jd_id: str
    matching_score: Optional[float] = None
    shortlisted: bool
    applied_at: Optional[str] = None
    user_email: Optional[str] = None
    job_headline: Optional[str] = None

def register_api_routes(app: FastAPI, flask_app):
    
    @app.get("/api/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "message": "Resume Shortlisting API is running"}
    
    @app.get("/api/job-descriptions", response_model=List[JobDescriptionResponse])
    async def get_job_descriptions():
        """Get all active job descriptions"""
        with flask_app.app_context():
            jds = JobDescription.query.filter_by(is_active=True).all()
            return [JobDescriptionResponse(**jd.to_dict()) for jd in jds]
    
    @app.get("/api/job-descriptions/{jd_id}", response_model=JobDescriptionResponse)
    async def get_job_description(jd_id: str):
        """Get specific job description"""
        with flask_app.app_context():
            jd = JobDescription.query.get(jd_id)
            if not jd:
                raise HTTPException(status_code=404, detail="Job description not found")
            return JobDescriptionResponse(**jd.to_dict())
    
    @app.post("/api/job-descriptions", response_model=JobDescriptionResponse)
    async def create_job_description(jd_data: JobDescriptionCreate):
        """Create new job description"""
        with flask_app.app_context():
            # Check if JD ID already exists
            existing_jd = JobDescription.query.get(jd_data.jd_id)
            if existing_jd:
                raise HTTPException(status_code=400, detail="Job description ID already exists")
            
            jd = JobDescription(
                jd_id=jd_data.jd_id,
                headline=jd_data.headline,
                short_description=jd_data.short_description,
                description=jd_data.description
            )
            
            try:
                db.session.add(jd)
                db.session.commit()
                return JobDescriptionResponse(**jd.to_dict())
            except Exception as e:
                db.session.rollback()
                raise HTTPException(status_code=500, detail=f"Error creating job description: {str(e)}")
    
    @app.put("/api/job-descriptions/{jd_id}", response_model=JobDescriptionResponse)
    async def update_job_description(jd_id: str, jd_data: JobDescriptionCreate):
        """Update existing job description"""
        with flask_app.app_context():
            jd = JobDescription.query.get(jd_id)
            if not jd:
                raise HTTPException(status_code=404, detail="Job description not found")
            
            jd.headline = jd_data.headline
            jd.short_description = jd_data.short_description
            jd.description = jd_data.description
            
            try:
                db.session.commit()
                return JobDescriptionResponse(**jd.to_dict())
            except Exception as e:
                db.session.rollback()
                raise HTTPException(status_code=500, detail=f"Error updating job description: {str(e)}")
    
    @app.delete("/api/job-descriptions/{jd_id}")
    async def delete_job_description(jd_id: str):
        """Delete job description (soft delete by setting is_active=False)"""
        with flask_app.app_context():
            jd = JobDescription.query.get(jd_id)
            if not jd:
                raise HTTPException(status_code=404, detail="Job description not found")
            
            jd.is_active = False
            
            try:
                db.session.commit()
                return {"message": "Job description deleted successfully"}
            except Exception as e:
                db.session.rollback()
                raise HTTPException(status_code=500, detail=f"Error deleting job description: {str(e)}")
    
    @app.post("/api/applications/upload")
    async def upload_application(
        name: str = Form(...),
        jd_id: str = Form(...),
        user_id: int = Form(...),
        resume: UploadFile = File(...)
    ):
        """Upload resume and create application"""
        
        # Validate file type
        if not resume.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        with flask_app.app_context():
            # Check if job description exists
            jd = JobDescription.query.get(jd_id)
            if not jd:
                raise HTTPException(status_code=404, detail="Job description not found")
            
            # Check if user exists
            user = User.query.get(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Create unique filename
            file_extension = os.path.splitext(resume.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join("resumes", unique_filename)
            
            try:
                # Save file
                content = await resume.read()
                with open(file_path, "wb") as f:
                    f.write(content)
                
                # Analyze resume
                analysis = analyze_resume(file_path, jd.description)
                
                # Create application record
                application = Application(
                    user_id=user_id,
                    name=name,
                    resume_path=file_path,
                    jd_id=jd_id,
                    matching_score=analysis['similarity_score'],
                    shortlisted=analysis['shortlisted'],
                    resume_text=analysis['text']
                )
                
                db.session.add(application)
                db.session.commit()
                
                return {
                    "message": "Application submitted successfully",
                    "application_id": application.id,
                    "matching_score": analysis['similarity_score'],
                    "shortlisted": analysis['shortlisted'],
                    "skills": analysis['skills'],
                    "matching_keywords": analysis['matching_keywords']
                }
                
            except Exception as e:
                # Clean up file if it was created
                if os.path.exists(file_path):
                    os.remove(file_path)
                db.session.rollback()
                raise HTTPException(status_code=500, detail=f"Error processing application: {str(e)}")
    
    @app.get("/api/applications", response_model=List[ApplicationResponse])
    async def get_applications(jd_id: Optional[str] = None, shortlisted_only: bool = False):
        """Get applications with optional filtering"""
        with flask_app.app_context():
            query = Application.query
            
            if jd_id:
                query = query.filter_by(jd_id=jd_id)
            
            if shortlisted_only:
                query = query.filter_by(shortlisted=True)
            
            applications = query.order_by(Application.applied_at.desc()).all()
            return [ApplicationResponse(**app.to_dict()) for app in applications]
    
    @app.get("/api/applications/{application_id}", response_model=ApplicationResponse)
    async def get_application(application_id: int):
        """Get specific application"""
        with flask_app.app_context():
            application = Application.query.get(application_id)
            if not application:
                raise HTTPException(status_code=404, detail="Application not found")
            return ApplicationResponse(**application.to_dict())
    
    @app.put("/api/applications/{application_id}/shortlist")
    async def toggle_shortlist(application_id: int):
        """Toggle shortlist status of application"""
        with flask_app.app_context():
            application = Application.query.get(application_id)
            if not application:
                raise HTTPException(status_code=404, detail="Application not found")
            
            application.shortlisted = not application.shortlisted
            
            try:
                db.session.commit()
                return {
                    "message": "Shortlist status updated",
                    "shortlisted": application.shortlisted
                }
            except Exception as e:
                db.session.rollback()
                raise HTTPException(status_code=500, detail=f"Error updating application: {str(e)}")
    
    @app.get("/api/stats")
    async def get_statistics():
        """Get application statistics"""
        with flask_app.app_context():
            total_applications = Application.query.count()
            shortlisted_applications = Application.query.filter_by(shortlisted=True).count()
            total_jds = JobDescription.query.filter_by(is_active=True).count()
            total_users = User.query.count()
            
            # Applications by JD
            jd_stats = db.session.query(
                JobDescription.jd_id,
                JobDescription.headline,
                db.func.count(Application.id).label('application_count')
            ).outerjoin(Application).group_by(JobDescription.jd_id, JobDescription.headline).all()
            
            return {
                "total_applications": total_applications,
                "shortlisted_applications": shortlisted_applications,
                "total_job_descriptions": total_jds,
                "total_users": total_users,
                "shortlist_rate": round((shortlisted_applications / total_applications * 100) if total_applications > 0 else 0, 2),
                "applications_by_jd": [
                    {
                        "jd_id": stat.jd_id,
                        "headline": stat.headline,
                        "application_count": stat.application_count
                    }
                    for stat in jd_stats
                ]
            }
