import re
import os
import PyPDF2
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file
    """
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {str(e)}")
        raise

def preprocess_text(text):
    """
    Preprocesses text by removing special characters, extra spaces, and converting to lowercase
    """
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)  # Remove special characters
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    return text.lower().strip()

def compute_matching_score(resume_text, jd_text):
    """
    Computes the matching score between a resume and a job description using cosine similarity
    """
    try:
        # Preprocess texts
        resume_text = preprocess_text(resume_text)
        jd_text = preprocess_text(jd_text)
        
        # Use TF-IDF vectorizer
        vectorizer = TfidfVectorizer(stop_words='english')
        
        # Create document-term matrix
        tfidf_matrix = vectorizer.fit_transform([jd_text, resume_text])
        
        # Compute cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # Convert to percentage
        score = similarity * 100
        
        return round(score, 2)
    except Exception as e:
        logging.error(f"Error computing matching score: {str(e)}")
        return 0.0  # Return 0 if there's an error
