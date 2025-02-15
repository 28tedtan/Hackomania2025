import streamlit as st
import json
import os
from datetime import datetime


# File path for persistent storage
POSTS_FILE = "posts.json"


# Load posts from file if exists
if 'posts' not in st.session_state:
   if os.path.exists(POSTS_FILE):
       with open(POSTS_FILE, 'r') as f:
           # Convert file objects back to UploadedFile objects
           posts_data = json.load(f)
           st.session_state.posts = []
           for post in posts_data:
               if post['file'] is not None:
                   post['file'] = st.runtime.uploaded_file_manager.UploadedFile(
                       post['file']['name'],
                       post['file']['type'],
                       post['file']['data']
                   )
               st.session_state.posts.append(post)
   else:
       st.session_state.posts = []


# Function to save posts to file
def save_posts():
   # Convert UploadedFile objects to serializable format
   posts_data = []
   for post in st.session_state.posts:
       post_copy = post.copy()
       if post_copy['file'] is not None:
           post_copy['file'] = {
               'name': post_copy['file'].name,
               'type': post_copy['file'].type,
               'data': post_copy['file'].getvalue().decode('latin1')
           }
       posts_data.append(post_copy)
  
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


# Reset button
if st.button("⚠️ Reset All Posts"):
   reset_posts()
   st.rerun()


# Post creation section
st.markdown("---")
st.header("Create a New Post")
st.markdown("Share something interesting with the community!")
uploaded_file = st.file_uploader("Upload a photo or video", type=["jpg", "jpeg", "png", "mp4"])
title = st.text_input("Add a title")
caption = st.text_input("Add a caption")
if st.button("Post"):
   if not (caption.strip() and title.strip()):
       st.error("Please enter a caption before posting")
   else:
       post = {
           'file': uploaded_file,
           'caption': caption,
           'likes': 0,
           'title': title.strip() if title else 'Untitled Post',
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
   st.subheader(f"📝 {post_title}")
   st.caption(f"Posted on: {post.get('timestamp', 'Unknown')}")
  
   if post['file'] is not None:
       if post['file'].type.startswith("image"):
           st.image(post['file'])
       elif post['file'].type.startswith("video"):
           st.video(post['file'])
  
   st.markdown(f"**Post:** {post['caption']}")
   st.markdown(f"**Likes:** {post['likes']}")
  
   # Like button
   col1, col2 = st.columns([1, 4])
   with col1:
       if st.button(f"❤️ Like", key=f"like_{i}"):
           post['likes'] += 1
           save_posts()  # Save posts to file
           st.rerun()
  
   # Comment section
   with st.expander("💬 Comments"):
       # Display existing comments
       for comment in post['comments']:
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