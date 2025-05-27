import os
import threading
from flask import Flask
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import db

# Create Flask app
flask_app = Flask(__name__)
flask_app.secret_key = os.environ.get("FLASK_SECRET_KEY", "resume-shortlist-secret-key-2024")
flask_app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://localhost/resume_db")
flask_app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
flask_app.config["UPLOAD_FOLDER"] = "resumes"
flask_app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# Initialize the app with the extension
db.init_app(flask_app)

with flask_app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()

# Create FastAPI app
fastapi_app = FastAPI(title="Resume Shortlisting API")

# Add CORS middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register routes
from web_routes import register_web_routes
from api_routes import register_api_routes

register_web_routes(flask_app)
register_api_routes(fastapi_app, flask_app)

def run_flask():
    """Run Flask app on port 5000"""
    flask_app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)

def run_fastapi():
    """Run FastAPI app on port 8000"""
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    # Create resumes directory if it doesn't exist
    os.makedirs("resumes", exist_ok=True)
    
    # Run both servers
    flask_thread = threading.Thread(target=run_flask)
    fastapi_thread = threading.Thread(target=run_fastapi)
    
    flask_thread.start()
    fastapi_thread.start()
    
    flask_thread.join()
    fastapi_thread.join()
