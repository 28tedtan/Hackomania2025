import json
import os
from datetime import datetime
import streamlit as st
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://mzeqafsqczyjzrbuukdc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16ZXFhZnNxY3p5anpyYnV1a2RjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2MTAwODIsImV4cCI6MjA1NTE4NjA4Mn0.bPa-NoVD_0FeR61NMcxLcpP-BiDVToH71tOhxfxmOy8"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# File path for persistent storage
POSTS_FILE = "data/posts.json"

def sync_with_supabase():
    """Sync local posts with Supabase data"""
    try:
        response = supabase.table("posts").select("*").execute()
        posts_data = response.data
        
        converted_posts = []
        for post in posts_data:
            # Ensure comments is a list and properly formatted
            comments = post.get('comments', [])
            if not isinstance(comments, list):
                comments = []
            
            # Convert each comment to ensure proper format
            formatted_comments = []
            for comment in comments:
                if isinstance(comment, dict):
                    formatted_comment = {
                        'author': comment.get('author', 'Anonymous'),
                        'text': comment.get('text', ''),
                        'timestamp': comment.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    }
                    formatted_comments.append(formatted_comment)
            
            converted_post = {
                'file': None,
                'caption': post.get('caption', ''),
                'title': post.get('title', ''),
                'likes': post.get('likes', 0),
                'comments': formatted_comments,  # Use formatted comments
                'timestamp': post.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            }
            converted_posts.append(converted_post)
        
        return converted_posts
    except Exception as e:
        st.error(f"Error syncing with Supabase: {str(e)}")
        return []

def save_posts():
    """Save posts to both local storage and Supabase"""
    posts_data = []
    for post in st.session_state.posts:
        post_copy = post.copy()
        if post_copy['file'] is not None:
            post_copy['file'] = {
                'id': getattr(post_copy['file'], 'id', 'default_id'),
                'name': post_copy['file'].name,
                'type': post_copy['file'].type,
                'data': post_copy['file'].getvalue().decode('latin1')
            }
        
        posts_data.append(post_copy)
        
        # Update or insert into Supabase
        try:
            supabase_post = {
                'title': post_copy['title'],
                'caption': post_copy['caption'],
                'likes': post_copy['likes'],
                'comments': post_copy['comments'],
                'timestamp': post_copy['timestamp'],
            }
            
            existing = supabase.table("posts").select("*").eq('timestamp', post_copy['timestamp']).execute()
            
            if existing.data:
                supabase.table("posts").update(supabase_post).eq('timestamp', post_copy['timestamp']).execute()
            else:
                supabase.table("posts").insert(supabase_post).execute()
        except Exception as e:
            st.error(f"Error updating Supabase: {str(e)}")
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(POSTS_FILE), exist_ok=True)
    
    # Save to local file
    with open(POSTS_FILE, 'w') as f:
        json.dump(posts_data, f)

def init_session_state():
    """Initialize session state with posts from Supabase"""
    if 'posts' not in st.session_state:
        # Get posts from Supabase
        st.session_state.posts = sync_with_supabase()
        
        # Load any local file attachments
        if os.path.exists(POSTS_FILE):
            with open(POSTS_FILE, 'r') as f:
                posts_data = json.load(f)
                for post in posts_data:
                    if post['file'] is not None:
                        post['file'] = st.runtime.uploaded_file_manager.UploadedFileRec(
                            id=post['file'].get('id', 'default_id'),
                            name=post['file']['name'],
                            type=post['file']['type'],
                            data=post['file']['data']
                        )
    
    if 'title' not in st.session_state:
        st.session_state.title = ""
    if 'caption' not in st.session_state:
        st.session_state.caption = ""

def reset_posts():
    """Reset all posts in both local storage and Supabase"""
    try:
        # Delete all posts from Supabase
        supabase.table("posts").delete().neq('timestamp', '').execute()
    except Exception as e:
        st.error(f"Error deleting from Supabase: {str(e)}")
    
    st.session_state.posts = []
    if os.path.exists(POSTS_FILE):
        os.remove(POSTS_FILE)