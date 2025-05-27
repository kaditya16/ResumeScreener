import os
import PyPDF2
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def extract_text_from_pdf(pdf_path):
    """Extract text content from PDF file"""
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return ""

def preprocess_text(text):
    """Preprocess text for similarity calculation"""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
    
    return ' '.join(tokens)

def calculate_similarity(resume_text, job_description):
    """Calculate cosine similarity between resume and job description"""
    if not resume_text or not job_description:
        return 0.0
    
    # Preprocess both texts
    resume_processed = preprocess_text(resume_text)
    jd_processed = preprocess_text(job_description)
    
    if not resume_processed or not jd_processed:
        return 0.0
    
    try:
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform([resume_processed, jd_processed])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # Convert to percentage
        return round(similarity * 100, 2)
    except Exception as e:
        print(f"Error calculating similarity: {str(e)}")
        return 0.0

def extract_key_skills(text):
    """Extract potential skills from resume text"""
    if not text:
        return []
    
    # Common technical skills patterns
    skill_patterns = [
        r'\b(python|java|javascript|c\+\+|html|css|sql|react|angular|vue|node\.js|django|flask|spring|mysql|postgresql|mongodb|aws|azure|docker|kubernetes|git|jenkins|linux|windows|machine learning|data science|artificial intelligence|deep learning)\b',
        r'\b(project management|agile|scrum|leadership|communication|teamwork|problem solving|analytical|creative|detail oriented)\b'
    ]
    
    skills = set()
    text_lower = text.lower()
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        skills.update(matches)
    
    return list(skills)

def get_matching_keywords(resume_text, job_description):
    """Find matching keywords between resume and job description"""
    if not resume_text or not job_description:
        return []
    
    resume_words = set(preprocess_text(resume_text).split())
    jd_words = set(preprocess_text(job_description).split())
    
    # Find common words (excluding very common ones)
    common_words = resume_words.intersection(jd_words)
    
    # Filter out very short words
    meaningful_matches = [word for word in common_words if len(word) > 3]
    
    return meaningful_matches[:10]  # Return top 10 matches

def analyze_resume(resume_path, job_description):
    """Complete resume analysis including text extraction and matching"""
    # Extract text from PDF
    resume_text = extract_text_from_pdf(resume_path)
    
    if not resume_text:
        return {
            'text': '',
            'similarity_score': 0.0,
            'skills': [],
            'matching_keywords': [],
            'shortlisted': False
        }
    
    # Calculate similarity score
    similarity_score = calculate_similarity(resume_text, job_description)
    
    # Extract skills
    skills = extract_key_skills(resume_text)
    
    # Find matching keywords
    matching_keywords = get_matching_keywords(resume_text, job_description)
    
    # Determine if shortlisted (score > 60%)
    shortlisted = similarity_score > 60.0
    
    return {
        'text': resume_text,
        'similarity_score': similarity_score,
        'skills': skills,
        'matching_keywords': matching_keywords,
        'shortlisted': shortlisted
    }
