import streamlit as st
from supabase import create_client, Client
from collections import Counter
import math

# --- Supabase Connection Setup ---
SUPABASE_URL = "https://mzeqafsqczyjzrbuukdc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16ZXFhZnNxY3p5anpyYnV1a2RjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2MTAwODIsImV4cCI6MjA1NTE4NjA4Mn0.bPa-NoVD_0FeR61NMcxLcpP-BiDVToH71tOhxfxmOy8"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def calculate_similarity(user_interests, db_interests):
    """
    Calculate similarity score using multiple metrics with synonym matching
    """
    # Interest synonyms and related terms
    interest_mapping = {
        'gaming': {'gaming', 'video games', 'playing games', 'games', 'gamer'},
        'programming': {'programming', 'coding', 'software development', 'development'},
        'artificial intelligence': {'ai', 'artificial intelligence', 'machine learning', 'ml'},
        'web development': {'web dev', 'web development', 'webdev', 'frontend', 'backend'},
        'cybersecurity': {'cybersecurity', 'cyber security', 'security', 'infosec'},
        'blockchain': {'blockchain', 'crypto', 'web3', 'cryptocurrency'},
    }
    
    # Normalize and expand interests using synonyms
    def normalize_interests(interests):
        normalized = set()
        for interest in interests:
            interest = interest.lower().strip()
            # Add the original interest
            normalized.add(interest)
            # Add any synonyms
            for category, synonyms in interest_mapping.items():
                if interest in synonyms:
                    normalized.update(synonyms)
        return normalized
    
    # Normalize both sets of interests
    user_interests = normalize_interests(user_interests)
    db_interests = normalize_interests(db_interests)
    
    # Jaccard Similarity (20% weight)
    intersection = len(user_interests.intersection(db_interests))
    union = len(user_interests.union(db_interests))
    jaccard = intersection / union if union > 0 else 0
    
    # TF-IDF like weighting (55% weight)
    interest_weights = {
        'gaming': 0.5,
        'programming': 0.5,
        'coding': 0.5,
        'technology': 0.5,
        'ai': 0.8,
        'machine learning': 0.8,
        'blockchain': 0.9,
        'quantum computing': 1.0,
        'cybersecurity': 0.9
    }
    
    weighted_score = 0
    matched_interests = user_interests.intersection(db_interests)
    for interest in matched_interests:
        # Find the highest weight among synonyms
        weight = 0.7  # default weight
        for category, synonyms in interest_mapping.items():
            if interest in synonyms:
                weight = max(weight, interest_weights.get(category, 0.7))
        weighted_score += weight
    
    weighted_score = weighted_score / (len(user_interests) + 1)  # Normalize
    
    # Category matching (25% weight)
    categories = {
        'tech': {'coding', 'programming', 'technology', 'software', 'web development'},
        'ai_ml': {'ai', 'artificial intelligence', 'machine learning', 'deep learning', 'data science'},
        'gaming': {'gaming', 'video games', 'playing games', 'game development', 'esports'},
        'security': {'cybersecurity', 'cyber security', 'hacking', 'cryptography', 'blockchain'}
    }
    
    category_score = 0
    user_categories = set()
    db_categories = set()
    
    for category, terms in categories.items():
        if any(term in user_interests for term in terms):
            user_categories.add(category)
        if any(term in db_interests for term in terms):
            db_categories.add(category)
    
    category_overlap = len(user_categories.intersection(db_categories))
    category_score = category_overlap / (len(user_categories) + 1)  # Normalize
    
    # Final weighted score
    final_score = (
        0.2 * jaccard +
        0.55 * weighted_score +
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
