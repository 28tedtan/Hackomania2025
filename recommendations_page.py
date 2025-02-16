import streamlit as st
from supabase import create_client, Client
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except:
    st.warning("Downloading language model for the first time...")
    spacy.cli.download('en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

# --- Supabase Connection Setup ---
SUPABASE_URL = "https://mzeqafsqczyjzrbuukdc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16ZXFhZnNxY3p5anpyYnV1a2RjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2MTAwODIsImV4cCI6MjA1NTE4NjA4Mn0.bPa-NoVD_0FeR61NMcxLcpP-BiDVToH71tOhxfxmOy8"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def preprocess_text(text):
    """Process text using spaCy for better matching"""
    doc = nlp(text.lower())
    # Remove stop words and punctuation, lemmatize
    return ' '.join([token.lemma_ for token in doc 
                    if not token.is_stop and not token.is_punct])

def calculate_similarity(user_interests, db_interests):
    """
    Calculate similarity using spaCy and TF-IDF
    """
    # Interest synonyms and related terms (keep this for expanding interests)
    interest_mapping = {
        'gaming': {'gaming', 'video games', 'playing games', 'games', 'gamer'},
        'programming': {'programming', 'coding', 'software development', 'development'},
        'artificial intelligence': {'ai', 'artificial intelligence', 'machine learning', 'ml'},
        'web development': {'web dev', 'web development', 'webdev', 'frontend', 'backend'},
        'cybersecurity': {'cybersecurity', 'cyber security', 'security', 'infosec'},
        'blockchain': {'blockchain', 'crypto', 'web3', 'cryptocurrency'},
    }
    
    # Expand interests using synonyms
    def expand_interests(interests):
        expanded = set()
        for interest in interests:
            expanded.add(interest)
            # Add synonyms
            for category, synonyms in interest_mapping.items():
                if interest.lower().strip() in synonyms:
                    expanded.update(synonyms)
        return expanded
    
    # Expand and preprocess interests
    user_expanded = expand_interests(user_interests)
    db_expanded = expand_interests(db_interests)
    
    # Convert to processed text
    user_text = ' '.join(user_expanded)
    db_text = ' '.join(db_expanded)
    
    user_processed = preprocess_text(user_text)
    db_processed = preprocess_text(db_text)
    
    # TF-IDF Vectorization (40% weight)
    tfidf = TfidfVectorizer()
    try:
        tfidf_matrix = tfidf.fit_transform([user_processed, db_processed])
        tfidf_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except:
        tfidf_score = 0
    
    # Semantic Similarity using spaCy (35% weight)
    user_doc = nlp(user_processed)
    db_doc = nlp(db_processed)
    semantic_score = user_doc.similarity(db_doc)
    
    # Category matching (25% weight)
    categories = {
        'tech': {'coding', 'programming', 'technology', 'software', 'web development'},
        'ai_ml': {'ai', 'artificial intelligence', 'machine learning', 'deep learning', 'data science'},
        'gaming': {'gaming', 'video games', 'playing games', 'game development', 'esports'},
        'security': {'cybersecurity', 'cyber security', 'hacking', 'cryptography', 'blockchain'}
    }
    
    user_categories = set()
    db_categories = set()
    
    for category, terms in categories.items():
        if any(term in user_expanded for term in terms):
            user_categories.add(category)
        if any(term in db_expanded for term in terms):
            db_categories.add(category)
    
    category_overlap = len(user_categories.intersection(db_categories))
    category_score = category_overlap / (len(user_categories) + 1)  # Normalize
    
    # Final weighted score
    final_score = (
        0.4 * tfidf_score +
        0.35 * semantic_score +
        0.25 * category_score
    )
    
    return min(final_score, 1)

def find_matches(current_user_interests):
    try:
        response = supabase.table("users").select("*").execute()
        if response.data:
            all_users = response.data
        else:
            all_users = []
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        return []
    
    user_similarities = []
    
    for user in all_users:
        db_user_interests_raw = user.get("interests", "")
        db_user_interests = {
            i.strip().lower() for i in db_user_interests_raw if isinstance(i, str)
        }
        
        similarity_score = calculate_similarity(current_user_interests, db_user_interests)
        
        if similarity_score > 0:  # Only include users with some similarity
            user_similarities.append({
                "user_id": user.get("id"),
                "name": user.get("name", "Unknown"),
                "similarity": similarity_score,
                "interests": db_user_interests
            })
    
    # Sort by similarity score and return top matches
    top_matches = sorted(user_similarities, key=lambda x: x["similarity"], reverse=True)[:5]
    
    return top_matches
