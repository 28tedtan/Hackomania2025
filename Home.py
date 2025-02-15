import streamlit as st

logged_in = False

st.title("Home")
st.caption("This website is built to help geeks like us find other geeks.")
st.caption("We are a community of geeks who are looking for other geeks to connect with.")
st.caption("Head to the leaderboard tab to see who's the geekiest of all!")
st.caption("We also have a tab for opportunities where people can post about their geeky stuff, including projects and own interests!")
st.caption("Head to the opportunities tab to see what's new! You can like, share and comment on posts!")

if logged_in != True:
    st.button("Login", type="primary")
