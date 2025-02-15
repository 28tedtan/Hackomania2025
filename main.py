import streamlit as skibidi

skibidi.button("Reset", type="primary")
if skibidi.button("Say hello"):
    skibidi.write("Why hello there")
else:
    skibidi.write("Goodbye")

if skibidi.button("Aloha", type="tertiary"):
    skibidi.write("Ciao")