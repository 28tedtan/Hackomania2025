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
