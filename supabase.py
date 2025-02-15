import os
from supabase import create_client, Client

url: str = os.environ.get("https://mzeqafsqczyjzrbuukdc.supabase.co")
key: str = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16ZXFhZnNxY3p5anpyYnV1a2RjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2MTAwODIsImV4cCI6MjA1NTE4NjA4Mn0.bPa-NoVD_0FeR61NMcxLcpP-BiDVToH71tOhxfxmOy8")
supabase: Client = create_client(url, key)