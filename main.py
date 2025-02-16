import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt
import pyperclip

# ----- PAGE CONFIG & STYLES -----
st.set_page_config(
    page_title="Connect.ai App", page_icon="🌆", layout="wide"
)

from git_stat_page import get_leaderboard_data, upsert_leaderboard_data, get_yearly_contributions
from socials_page_test import hard_coded_socials_page
from recommendations_page import find_matches
from socials_page import save_posts, init_session_state

# Inject a bit of CSS to style metric cards, titles, etc.
st.markdown(
    """
    <style>
    .stContainer {
        background-color: #F9F9F9;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .metric-container {
        background-color: #fff;
        border-radius: 6px;
        padding: 10px 15px;
        text-align: center;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    /* Sidebar style tweaks */
    section[data-testid="stSidebar"] {
        background-color: #F0F4F8;
    }
    section[data-testid="stSidebar"] .css-1d391kg {
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def main():
    st.sidebar.title("Navigation")
    selected_page = st.sidebar.radio(
        "Go to",
        [
            "Dashboard",
            "Socials",
            "Leaderboards",
            "Github Projects",
            "Recommendations"
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.write("**User:** John Doe")
    st.sidebar.write("**Version:** 0.0.1")
    st.sidebar.write("Bio: Just a tech enthusiast sharing random moments.")

    if st.sidebar.button("Logout"):
        st.sidebar.write("You have logged out.")

    st.title("Connect with other Geeks!")
    st.markdown(
        """
        Welcome to the **Connect.ai** application, a platform that connects geeks with other geeks! Powered by AI.
        """
    )

    if selected_page == "Dashboard":
        dashboard_page()
    
    elif selected_page == "Socials":
        socials_page()

    elif selected_page == "Leaderboards":
        leaderboards_page()
    
    elif selected_page == "Github Projects":
        github_projects_page()

    elif selected_page == "Recommendations":
        recommendations_page()


def dashboard_page():
    st.markdown("### Key Stats")
    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
    with col_m1:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.metric(label="Connections Made", value="10.5K", delta="125")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_m2:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.metric(label="Active Users (Last 30 Days)", value="510", delta="-2")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_m3:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.metric(label="Engagement Rate", value="87.9%", delta="0.1%")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_m4:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.metric(label="Posts Created", value="150", delta="10")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_m5:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.metric(label="Average Session Time", value="30 minutes", delta="-0.1s")
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("---")

    st.subheader("Overview")
    st.write(
        """
        **Becoming a well-connected geek is vital** for maintaining a healthy lifestyle. 
        This application helps geeks connect with each other using AI-driven insights 
        based on **demographic, environment**, and **social** data.
        """
    )
    st.info("Navigate using the sidebar to explore other features.")


def socials_page():
    # Initialize session state
    init_session_state()

    st.title("GeekSocial")
    st.markdown("---")
    st.markdown("### Share your thoughts, ideas, and creations with the community!")

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
            st.session_state.posts.append(post)
            save_posts()
            st.success("Post created successfully!")
            st.session_state.caption = ""
            st.session_state.title = ""
            st.rerun()

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
    
        # Action buttons
        like, share, delete = st.columns([1, 1, 3])
        with like:
            if st.button(f"❤️ Like", key=f"like_{i}"):
                post['likes'] += 1
                save_posts()
                st.rerun()
        
        with share:
            if st.button(f"🔗 Share", key=f"share_{i}"):
                share_url = f"http://localhost:8501?post_id={i}"
                try:
                    pyperclip.copy(share_url)
                    st.success(f"Link copied to clipboard: {share_url}")
                except Exception as e:
                    st.code(share_url)

        with delete:
            if st.button("🗑️ Delete", key=f"delete_{i}", type="secondary"):
                st.session_state.posts.pop(i)
                save_posts()
                st.rerun()
    
        # Comment section
        with st.expander("💬 Comments"):
            comments = post.get('comments', [])
            if isinstance(comments, list):  # Make sure comments is a list
                for comment in comments:
                    if isinstance(comment, dict):  # Make sure each comment is a dictionary
                        author = comment.get('author', 'Anonymous')
                        timestamp = comment.get('timestamp', 'Unknown time')
                        text = comment.get('text', '')
                        st.markdown(f"**{author}** ({timestamp}):")
                        st.markdown(f"> {text}")
                        st.markdown("---")
        
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
                    if not isinstance(post['comments'], list):
                        post['comments'] = []
                    post['comments'].append(new_comment)
                    save_posts()
                    st.rerun()
                else:
                    st.error("Please enter both your name and a comment")


def leaderboards_page():
    st.subheader("Geeks for Geeks Leaderboard")
    st.write("Fetching data from the GeekerBase...")

    # Fetch data from Supabase
    data = get_leaderboard_data()
    
    # Show the raw data (optional)
    # TODO: There's some sort of error here to fix
    #st.write("Raw Data", data)
    
    # Check if data is available and has the expected columns
    if not data.empty and 'name' in data.columns and 'contributes' in data.columns:
        # Create a horizontal bar chart using Altair
        chart = alt.Chart(data).mark_bar().encode(
            x=alt.X("contributes:Q", title="Contributions"),
            y=alt.Y("name:N", sort='-x', title="Name")
        ).properties(
            width=600,
            height=500
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.error("There is no data in the leaderboard.")

    st.link_button(label="Upload your contributions!", url="test.py",help=None, type="secondary", icon="🛠️", disabled=False, use_container_width=True)
    

def github_projects_page():
    st.subheader("View Geek's GitHub Contributions!")
    st.write("Enter your GitHub username and your personal access token")

    username = st.text_input("GitHub Username")
    token = st.text_input("Personal Access Token", type="password")
    current_year = datetime.now().year
    # Here we use a fixed year; you can make this dynamic with st.number_input if needed.
    year = 2025

    if st.button("Upload Contributions"):
        if username and token:
            try:
                # Fetch contributions from GitHub
                contributions = get_yearly_contributions(username, token, int(year))
                st.success(f"{username}, you made {contributions} contributions in {year}.")

                # Upsert data into Supabase (update if exists, otherwise insert)
                upsert_response = upsert_leaderboard_data(username, contributions)
                st.write("Data upsert response:", upsert_response)
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter both your GitHub username and personal access token.")


def recommendations_page():
    st.subheader("Simple Recommendation Engine")

    # Input interests from the current user
    st.write("Enter your interests (separate by commas):")
    interests_input = st.text_input(label="Your Interests", value="music, sports, coding")

    # Convert user input into a set of interests
    current_user_interests = {i.strip().lower() for i in interests_input.split(",") if i.strip()}
    if st.button("Find Matches"):
        top_matches = find_matches(current_user_interests)
        st.subheader("Top 5 Matches")
        if top_matches:
            for match in top_matches:
                st.write(
                    f"User ID: {match['user_id']}, "
                    f"Name: {match['name']}, "
                    f"Rating: {match['similarity']:.2f},",
                    f"Interests: {', '.join(match['interests'])}"
                )
        else:
            st.info("No matches found.")

if __name__ == "__main__":
    main()