import streamlit as st
import pandas as pd
import datetime

from git_stat_page import get_leaderboard_data, upsert_leaderboard_data, get_yearly_contributions


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
            "Projects",
            "Leaderboards",
            "Recommendations"
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.write("**User:** John Doe")
    st.sidebar.write("**Version:** 0.0.1")
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

    elif selected_page == "Projects":
        projects_page()

    elif selected_page == "Leaderboards":
        leaderboards_page()

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


def projects_page():
    st.subheader("Ask the Smart Agent")
    st.write(
        """
        Input your query related to **demographic, transportation, economic, environment, or social** issues, 
        and let the agent automatically collect and consolidate old and new information from your prorietary data lakehouse.
        """
    )
    user_query = st.text_input(
        "What would you like to find out?",
        value="What is the distribution of green spaces in Singapore across different planning areas?",
    )

    if st.button("Get Insight Report"):
        #st.markdown("### Insight Report")
        # Placeholder text
        insight_report = generate_insight_report(user_query)
        st.write(insight_report)
        # Optionally display some “calls” or “steps” if you want to mimic an agent’s chain-of-thought (in a user-friendly format).

        report_bytes = BytesIO(insight_report.encode('utf-8'))
        st.download_button(
            label="Download Insight Report",
            data=report_bytes,
            file_name="insight_report.txt",
            mime="text/plain"
        )


def leaderboards_page():
    
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
    st.subheader("Comparative Analysis")
    st.write(
        """
        Wondering how other cities or countries tackle similar problems? 
        Ask the agent to pull **external data or case studies** from the web.
        """
    )

    compare_query = st.text_input(
        "For example: 'How do cities like Tokyo address demographic aging?'",
        value="How do cities like Tokyo address demographic aging?",
    )

    if st.button("Compare with Other Countries"):
        summary = generate_comparative_analysis(compare_query)
        st.markdown("### Comparative Analysis Results")
        st.write(summary)


def synthetic_generation_page():
    st.subheader("Synthetic Generation")
    st.write(
        """
        Want to create new data points that don't exist in the database? 
        Ask the agent to generate **synthetic data** based on the existing data.
        """
    )

    synthetic_query = st.text_input(
        "For example: 'Generate synthetic data for a new city with demographic data'",
        value="Generate synthetic data for Singapore with demographic data to simulate population growth after a year",
    )

    if st.button("Generate Synthetic Data"):
        csv_data = generate_synthetic_data_code(synthetic_query)
        st.markdown("### Synthetic Data")
        st.download_button(
            label="Download synthetic_data.csv",
            data=csv_data,
            file_name="synthetic_data.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    main()