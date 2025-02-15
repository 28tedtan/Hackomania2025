import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Supabase credentials dones
SUPABASE_URL = "https://mzeqafsqczyjzrbuukdc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16ZXFhZnNxY3p5anpyYnV1a2RjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2MTAwODIsImV4cCI6MjA1NTE4NjA4Mn0.bPa-NoVD_0FeR61NMcxLcpP-BiDVToH71tOhxfxmOy8"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Fetch data from Supabase
def get_data():
    response = supabase.table("opport").select("*").execute()
    return pd.DataFrame(response.data)

# Streamlit UI
st.title("Supabase + Streamlit Demo")

if st.button("Load Data"):
    df = get_data()
    st.write(df)
