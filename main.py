import streamlit as st
import pandas as pd
import datetime
import altair as alt

from git_stat_page import get_leaderboard_data, upsert_leaderboard_data, get_yearly_contributions
from socials_page_test import hard_coded_socials_page
from recommendations_page import find_matches


# ----- PAGE CONFIG & STYLES -----
st.set_page_config(
    page_title="Connect.ai App", page_icon="🌆", layout="wide"
)

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
        st.metric(label="Connections Made", value="10.5K", delta="↑125")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_m2:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.metric(label="Active Users (Last 30 Days)", value="510", delta="↓2")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_m3:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.metric(label="Engagement Rate", value="87.9%", delta="↑0.1%")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_m4:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.metric(label="Posts Created", value="150", delta="↑10")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_m5:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.metric(label="Average Session Time", value="30 minutes", delta="↓0.1s")
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
    # st.subheader("GeekSocial")
    # st.markdown("---")
    # st.markdown("### Share your thoughts, ideas, and creations with the community!")
    hard_coded_socials_page()


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
    current_year = datetime.datetime.now().year
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