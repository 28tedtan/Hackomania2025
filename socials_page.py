import streamlit as st
import json
import os
from datetime import datetime
import pyperclip
import platform
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://mzeqafsqczyjzrbuukdc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16ZXFhZnNxY3p5anpyYnV1a2RjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2MTAwODIsImV4cCI6MjA1NTE4NjA4Mn0.bPa-NoVD_0FeR61NMcxLcpP-BiDVToH71tOhxfxmOy8"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# File path for persistent storage
POSTS_FILE = "data/posts.json"

# variables
liked = False

def sync_with_supabase():
    """Sync local posts with Supabase data"""
    try:
        # Fetch data from Supabase
        response = supabase.table("posts").select("*").execute()
        posts_data = response.data
        
        # Convert Supabase data to match local format
        converted_posts = []
        for post in posts_data:
            converted_post = {
                'file': None,  # Handle file separately if needed
                'caption': post.get('caption', ''),
                'title': post.get('title', ''),
                'likes': post.get('likes', 0),
                'comments': post.get('comments', []) or [],  # Ensure comments is always a list
                'timestamp': post.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            }
            converted_posts.append(converted_post)
        
        # Save to local file
        with open(POSTS_FILE, 'w') as f:
            json.dump(converted_posts, f)
        
        return converted_posts
    except Exception as e:
        st.error(f"Error syncing with Supabase: {str(e)}")
        return []

# Initialize session state for posts and input fields
if 'posts' not in st.session_state:
    if os.path.exists(POSTS_FILE):
        # Sync with Supabase first
        st.session_state.posts = sync_with_supabase()
        
        # Then load local file with any file attachments
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
    else:
        st.session_state.posts = []
if 'title' not in st.session_state:
    st.session_state.title = ""
if 'caption' not in st.session_state:
    st.session_state.caption = ""


# Function to save posts to file
def save_posts():
    # Convert UploadedFile objects to serializable format
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
            
            # Check if post exists in Supabase
            existing = supabase.table("posts").select("*").eq('timestamp', post_copy['timestamp']).execute()
            
            if existing.data:
                # Update existing post
                supabase.table("posts").update(supabase_post).eq('timestamp', post_copy['timestamp']).execute()
            else:
                # Insert new post
                supabase.table("posts").insert(supabase_post).execute()
                
        except Exception as e:
            st.error(f"Error updating Supabase: {str(e)}")
    
    # Save to local file
    with open(POSTS_FILE, 'w') as f:
        json.dump(posts_data, f)


# Function to reset all posts
def reset_posts():
   st.session_state.posts = []
   if os.path.exists(POSTS_FILE):
       os.remove(POSTS_FILE)
   st.success("All posts have been reset!")


# Page title and description
st.title("GeekSocial")
st.markdown("---")
st.markdown("### Share your thoughts, ideas, and creations with the community!")


# Reset button (for debugging)
if False:
   if st.button("⚠️ Reset All Posts"):
        reset_posts()
        st.rerun()


# Post creation section
st.markdown("---")
st.header("Create a New Post")
st.markdown("Share something interesting with the community!")
uploaded_file = st.file_uploader("Upload a photo or video", type=["jpg", "jpeg", "png", "mp4"])
st.session_state.title = st.text_input("Add a title", value=st.session_state.title)
st.session_state.caption = st.text_input("Add a caption", value=st.session_state.caption)
if st.button("Post"):
   if not (st.session_state.caption.strip() and st.session_state.title.strip()):
       st.error("Please enter a caption and title before posting")
   else:
       post = {
           'file': uploaded_file,
           'caption': st.session_state.caption,
           'title': st.session_state.title,
           'likes': 0,
           'comments': [],
           'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
       }
       st.session_state.posts.append(post)  # Add new post at the beginning
       save_posts()  # Save posts to file
       st.success("Post created successfully!")
       st.session_state.caption = ""  # Clear the caption input
       st.session_state.title = ""
       st.rerun()  # Force rerun to clear input fields


# Display posts feed
st.markdown("---")
st.header("Community Feed")
for i, post in enumerate(st.session_state.posts):
   st.markdown("---")
   post_title = post.get('title', 'Untitled Post')
   st.subheader(f"{post_title}")
   st.caption(f"Posted on: {post.get('timestamp', 'Unknown')}")
  
   if post['file'] is not None:
       if post['file'].type.startswith("image"):
           st.image(post['file'])
       elif post['file'].type.startswith("video"):
           st.video(post['file'])
  
   st.markdown(f"**Post:** {post['caption']}")
   st.markdown(f"**Likes:** {post['likes']}")
  
   # Like button
   like, share, delete = st.columns([1, 3, 5])
   with like:
       if st.button(f"❤️ Like", key=f"like_{i}"):
           post['likes'] += 1
           save_posts()  # Save posts to file
           st.rerun()
   
   # Share button and functionality
   with share:
       if st.button(f"🔗 Share", key=f"share_{i}"):
           # Generate a shareable link for the post
           # Use a more reliable way to get the base URL
           share_url = f"http://localhost:8501?post_id={i}"  # For local development
           
           try:
               pyperclip.copy(share_url)
               st.success(f"Link copied to clipboard: {share_url}")
           except Exception as e:
               st.error(f"Could not copy to clipboard. Here's your link: {share_url}")
               st.code(share_url)  # Display as copyable code block

    # delete button
   with delete:
       if st.button(f"Delete Post {post['id']}"):
            supabase.from_("posts").delete().eq("id", post['id']).execute()
            st.rerun()
  
   # Comment section
   with st.expander("💬 Comments"):
       # Display existing comments
       comments = post.get('comments') or []  # Ensure comments is always a list
       for comment in comments:
           st.markdown(f"**{comment['author']}** ({comment['timestamp']}):")
           st.markdown(f"> {comment['text']}")
           st.markdown("---")
      
       # Add new comment
       with st.form(key=f"comment_form_{i}"):
           comment_author = st.text_input("Your name", key=f"comment_author_{i}")
           comment_text = st.text_area("Your comment", key=f"comment_text_{i}")
           if st.form_submit_button("Add Comment"):
               if comment_author.strip() and comment_text.strip():
                   new_comment = {
                       'author': comment_author,
                       'text': comment_text,
                       'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                   }
                   post['comments'].append(new_comment)
                   save_posts()  # Save posts to file
                   st.rerun()
               else:
                   st.error("Please enter both your name and a comment")