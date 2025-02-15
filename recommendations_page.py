import streamlit as st
from supabase import create_client, Client

# --- Supabase Connection Setup ---
SUPABASE_URL = "https://mzeqafsqczyjzrbuukdc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16ZXFhZnNxY3p5anpyYnV1a2RjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2MTAwODIsImV4cCI6MjA1NTE4NjA4Mn0.bPa-NoVD_0FeR61NMcxLcpP-BiDVToH71tOhxfxmOy8"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def find_matches(current_user_interests):
    try:
        response = supabase.table("users").select("*").execute()
        if response.data:
            all_users = response.data
        else:
            all_users = []
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        return
    
    user_similarities = []

    for user in all_users:
        db_user_interests_raw = user.get("interests", "")
        db_user_interests = {
            i.strip().lower() for i in db_user_interests_raw if isinstance(i, str)
        }

        similarity_score = jaccard_similarity(current_user_interests, db_user_interests)

        user_similarities.append(
            {
                "user_id": user.get("id"),
                "name": user.get("name", "Unknown"),
                "similarity": similarity_score,
                "interests": db_user_interests
            }
        )

        top_matches = sorted(user_similarities, key=lambda x: x["similarity"], reverse=True)[:5]
    
    return top_matches
    

def jaccard_similarity(set_a, set_b):
    """
    Jaccard similarity = (size of intersection) / (size of union)
    """
    intersection = set_a.intersection(set_b)
    union = set_a.union(set_b)
    if len(union) == 0:
        return 0
    return len(intersection) / len(union)
