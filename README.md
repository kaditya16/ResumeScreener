# Resume Shortlisting Web Application

## Project Overview

This is a full-stack Resume Shortlisting Web Application built with:
- **FastAPI**: Backend APIs (for AJAX/admin dashboard, resume upload, etc.)
- **Flask**: Serves HTML templates, handles authentication, and user-facing routes
- **SQLAlchemy**: ORM for database models (using SQLite by default, can be switched to PostgreSQL)
- **Jinja2**: For HTML templating
- **scikit-learn, NLTK, PyPDF2**: For resume parsing and matching logic
- **Bootstrap, JS, CSS**: Frontend styling and interactivity

---

## File-by-File Explanation

### Python Backend

- **[main.py](main.py)**  
  Entry point. Starts both Flask (port 5000) and FastAPI (port 8000) servers in parallel threads.  
  - Initializes Flask app for web routes and templates.
  - Initializes FastAPI app for API endpoints.
  - Sets up database, session, and uploads folder.

- **[models.py](models.py)**  
  SQLAlchemy ORM models:
  - `User`: Stores user info, password hash, admin flag.
  - `JobDescription`: Stores job postings.
  - `Application`: Stores job applications, resume path, matching score, etc.

- **[auth.py](auth.py)**  
  Authentication helpers and decorators:
  - `login_required`, `admin_required` for route protection.
  - `login_user`, `logout_user`, `create_user`, `authenticate_user`, `get_current_user`.

- **[resume_parser.py](resume_parser.py)**  
  Resume parsing and matching logic:
  - Extracts text from PDF resumes.
  - Preprocesses and compares resume text to job description using TF-IDF and cosine similarity.
  - Extracts key skills and matching keywords.

- **[web_routes.py](web_routes.py)**  
  All Flask web routes:
  - Home, login, register, logout, apply, submit application.
  - Admin dashboard, create/edit/delete job descriptions, view applications.
  - Error handlers for 404/500.

- **[api_routes.py](api_routes.py)**  
  All FastAPI API endpoints:
  - CRUD for job descriptions.
  - Application upload and management.
  - Statistics for admin dashboard.
  - Used by AJAX/admin dashboard JS.

---

### Frontend

- **[templates/](templates/)**  
  Jinja2 HTML templates for all pages:
  - `base.html`: Main layout, navbar, sidebar, flash messages.
  - `index.html`: Homepage with job listings.
  - `login.html`, `register.html`: Auth pages.
  - `apply.html`: Application form and status.
  - `admin/`: Admin dashboard, create JD, reports.
  - `404.html`, `500.html`: Error pages.

- **[static/style.css](static/style.css)**  
  Custom CSS for layout, cards, sidebar, forms, etc.

- **[static/app.js](static/app.js)**  
  Frontend JavaScript:
  - Handles form validation, file upload, drag-and-drop, search, table interactivity, notifications, and admin dashboard AJAX.

---

### Data & Assets

- **[resumes/](resumes/)**  
  Stores uploaded PDF resumes.

- **[instance/resume.db](instance/resume.db)**  
  SQLite database file (created at runtime).

- **[attached_assets/](attached_assets/)**  
  Miscellaneous assets (not required for app logic).

---

### Config & Dependency Files

- **[requirements.txt](requirements.txt)**  
  Python dependencies for the project.

- **[pyproject.toml](pyproject.toml)**  
  Project metadata and dependencies (for modern Python packaging).

- **[.replit](.replit)**  
  Replit-specific config for running the app.

---

## How the Application Runs (Start to End)

1. **Startup**  
   Run `python main.py`.  
   - Flask server starts on port 5000 (serves web pages).
   - FastAPI server starts on port 8000 (serves API endpoints).

2. **User Flow**
   - **Home Page**: Lists all active job descriptions.
   - **Register/Login**: Users can register or log in (with session-based auth).
   - **Apply**: Logged-in users can apply for jobs by uploading a PDF resume.
   - **Resume Parsing**: Uploaded resume is parsed, compared to the job description, and a matching score is calculated.
   - **Application Status**: Users see their application status and score.

3. **Admin Flow**
   - **Admin Dashboard**: Admins can create/edit/delete job descriptions, view all applications, and see statistics.
   - **AJAX/JS**: Admin dashboard uses JavaScript to fetch data from FastAPI endpoints for live updates.

4. **Database**
   - All user, job, and application data is stored in the SQLite database (`instance/resume.db`).

5. **Resume Storage**
   - Uploaded resumes are saved in the `resumes/` folder.

6. **Frontend**
   - All pages are rendered using Jinja2 templates.
   - Custom JS (`static/app.js`) handles interactivity, validation, and admin AJAX.

---

## Summary

- **Flask** serves the web pages and handles user sessions.
- **FastAPI** provides REST APIs for admin dashboard and AJAX.
- **SQLAlchemy** manages all database operations.
- **Resume parsing and matching** is handled in [`resume_parser.py`](resume_parser.py).
- **Frontend** is styled with Bootstrap and custom CSS/JS.

---

For more details, see the code in each file as described above.
