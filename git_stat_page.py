import streamlit as st
import requests
import datetime
import altair as alt
from supabase import create_client, Client
import pandas as pd

# Supabase credentials
SUPABASE_URL = "https://mzeqafsqczyjzrbuukdc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16ZXFhZnNxY3p5anpyYnV1a2RjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2MTAwODIsImV4cCI6MjA1NTE4NjA4Mn0.bPa-NoVD_0FeR61NMcxLcpP-BiDVToH71tOhxfxmOy8"

# Create a Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_leaderboard_data():
    """
    Fetches the leaderboard data with columns 'name' and 'contributes' from the Supabase table.
    """
    response = supabase.table("leaderboards-v2").select("id","name", "contributes").execute()
    return pd.DataFrame(response.data)

def upsert_leaderboard_data(username, contributions):
    """
    Checks if the username exists in the 'leaderboards' table.
    If it does, update the 'contributes' column with the new contributions.
    Otherwise, insert a new record.
    """
    # Check if the username already exists
    check_response = supabase.table("leaderboards-v2").select("*").eq("name", username).execute()
    
    if check_response.data:
        # Update the contributions if the record exists
        update_response = supabase.table("leaderboards-v2") \
            .update({"contributes": contributions}) \
            .eq("name", username) \
            .execute()
        return update_response
    else:
        # Insert a new record if the username doesn't exist
        insert_response = supabase.table("leaderboards-v2") \
            .insert({"name": username, "contributes": contributions}) \
            .execute()
        return insert_response

def get_yearly_contributions(username, token, year):
    """
    Fetches total GitHub contributions for a given user in a specified year using GitHub's GraphQL API.
    """
    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {token}"}

    start_date = datetime.datetime(year, 1, 1).isoformat() + "Z"
    end_date = datetime.datetime(year, 12, 31, 23, 59, 59).isoformat() + "Z"

    query ="""
    query($username: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $username) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            totalContributions
          }
        }
      }
    }
    """
    
    variables = {
        "username": username,
        "from": start_date,
        "to": end_date
    }

    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        total = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
        return total
    else:
        raise Exception(f"Query failed with status code {response.status_code}: {response.text}")

