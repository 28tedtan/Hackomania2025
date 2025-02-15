import streamlit as st
import altair as alt
import pandas as pd
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://mzeqafsqczyjzrbuukdc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16ZXFhZnNxY3p5anpyYnV1a2RjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2MTAwODIsImV4cCI6MjA1NTE4NjA4Mn0.bPa-NoVD_0FeR61NMcxLcpP-BiDVToH71tOhxfxmOy8"

# Create a Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_leaderboard_data():
    """
    Fetches the leaderboard data with columns 'name' and 'contributes' from the Supabase table.
    """
    response = supabase.table("leaderboards").select("name", "contributes").execute()
    return pd.DataFrame(response.data)

def main():
    st.title("Geeks for Geeks Leaderboard")
    st.write("Fetching data from the GeekerBase...")

    # Fetch data from Supabase
    data = get_leaderboard_data()
    
    # Show the raw data (optional)
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

if __name__ == "__main__":
    main()
