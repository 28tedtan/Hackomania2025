import streamlit as st
from supabase import create_client, Client
from collections import Counter
import math

# --- Supabase Connection Setup ---
SUPABASE_URL = "https://mzeqafsqczyjzrbuukdc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16ZXFhZnNxY3p5anpyYnV1a2RjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2MTAwODIsImV4cCI6MjA1NTE4NjA4Mn0.bPa-NoVD_0FeR61NMcxLcpP-BiDVToH71tOhxfxmOy8"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@st.cache_data
def calculate_similarity(user_interests, db_interests):
    """
    Fast and accurate similarity calculation using:
    1. Enhanced Jaccard similarity with synonyms
    2. Interest depth scoring
    3. Category alignment
    """
    # Comprehensive interest mapping with hierarchical relationships
    interest_hierarchy = {
        'tech': {
            'programming': {'coding', 'software development', 'development', 'programming'},
            'web': {'web development', 'frontend', 'backend', 'fullstack', 'web dev'},
            'mobile': {'app development', 'ios', 'android', 'mobile dev'},
            'devops': {'docker', 'kubernetes', 'ci/cd', 'cloud'},
        },
        'ai_ml': {
            'ai': {'artificial intelligence', 'ai', 'machine learning', 'ml', 'deep learning'},
            'data_science': {'data science', 'data analytics', 'big data', 'statistics'},
            'nlp': {'natural language processing', 'nlp', 'text analysis'},
        },
        'gaming': {
            'gaming': {'gaming', 'video games', 'playing games', 'games', 'gamer'},
            'game_dev': {'game development', 'unity', 'unreal', 'game design'},
            'esports': {'esports', 'competitive gaming', 'streaming'},
        },
        'security': {
            'cybersecurity': {'cybersecurity', 'cyber security', 'security', 'infosec'},
            'blockchain': {'blockchain', 'crypto', 'web3', 'cryptocurrency', 'smart contracts'},
            'ethical_hacking': {'penetration testing', 'ethical hacking', 'security testing'},
        }
    }

    # Flatten hierarchy for quick lookups while maintaining relationships
    interest_to_category = {}
    interest_to_subcategory = {}
    all_synonyms = {}
    
    for category, subcategories in interest_hierarchy.items():
        for subcategory, terms in subcategories.items():
            for term in terms:
                interest_to_category[term] = category
                interest_to_subcategory[term] = subcategory
                all_synonyms[term] = terms

    def normalize_interests(interests):
        """Normalize and expand interests with synonyms"""
        normalized = set()
        for interest in interests:
            interest = interest.lower().strip()
            normalized.add(interest)
            # Add synonyms if they exist
            if interest in all_synonyms:
                normalized.update(all_synonyms[interest])
        return normalized

    # Normalize both sets
    user_set = normalize_interests(user_interests)
    db_set = normalize_interests(db_interests)

    # 1. Enhanced Jaccard Similarity (30%)
    intersection = len(user_set.intersection(db_set))
    union = len(user_set.union(db_set))
    jaccard = intersection / union if union > 0 else 0

    # 2. Category Alignment Score (40%)
    user_categories = {interest_to_category[interest] 
                      for interest in user_set 
                      if interest in interest_to_category}
    db_categories = {interest_to_category[interest] 
                    for interest in db_set 
                    if interest in interest_to_category}
    
    category_overlap = len(user_categories.intersection(db_categories))
    category_score = category_overlap / max(len(user_categories), 1)

    # 3. Interest Depth Score (30%)
    depth_weights = {
        'tech': 0.8,
        'ai_ml': 1.0,
        'gaming': 0.7,
        'security': 0.9
    }

    depth_score = 0
    matched_interests = user_set.intersection(db_set)
    if matched_interests:
        for interest in matched_interests:
            if interest in interest_to_category:
                category = interest_to_category[interest]
                depth_score += depth_weights.get(category, 0.5)
        depth_score /= len(matched_interests)

    # Calculate final score with weights
    final_score = (
        0.45 * jaccard +
        0.55 * category_score
    )

    return min(final_score, 1)

def find_matches(current_user_interests):
    """Find and return top 5 matches"""
    try:
        response = supabase.table("users").select("*").execute()
        all_users = response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        return []
    
    user_similarities = []
    
    for user in all_users:
        db_interests = {i.strip().lower() 
                       for i in user.get("interests", []) 
                       if isinstance(i, str)}
        
        if not db_interests:
            continue
            
        similarity = calculate_similarity(current_user_interests, db_interests)
        
        if similarity > 0.2:  # Only include meaningful matches
            user_similarities.append({
                "user_id": user.get("id"),
                "name": user.get("name", "Unknown"),
                "similarity": similarity,
                "interests": db_interests
            })
    
    return sorted(user_similarities, 
                 key=lambda x: x["similarity"], 
                 reverse=True)[:5]
