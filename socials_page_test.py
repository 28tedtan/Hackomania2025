import streamlit as st

def hard_coded_socials_page():
    # Page Title
    st.subheader("Geeks Social")

    # ---- POST 1 ----
    st.subheader("Post #1")
    st.write("**Posted by:** @hackerrman")
    st.write("**Time:** 2:15pm, February 15, 2025")
    st.write("**Location:** Singapore")

    # Display the first image (e.g., "hackathon.jpg")
    st.image(
        "images/photo1.jpg",  # Replace with the actual path to your first image
        caption="Great hackathon vibes! Loved working on exciting projects with like-minded folks. #Coding #Hackathon",
        use_column_width=True
    )

    # Post interactions
    st.write("**Likes:** 120 \u2764\ufe0f")
    st.write("**Comments:**")
    st.write("- @dev_guru: Looks awesome!")
    st.write("- @designqueen: Wish I could join next time!")

    st.markdown("---")

    # ---- POST 2 ----
    st.subheader("Post #2")
    st.write("**Posted by:** @codemasterr")
    st.write("**Time:** 6:06am, February 16, 2025")
    st.write("**Location:** Home Office")

    # Display the second image (e.g., "phone_coding.jpg")
    st.image(
        "images/photo2.jpeg",  # Replace with the actual path to your second image
        caption="Early morning grind. Working on my new app feature! #CodeLife #WeekendHustle",
        use_column_width=True
    )

    # Post interactions
    st.write("**Likes:** 45 \u2764\ufe0f")
    st.write("**Comments:**")
    st.write("- @nightowl: Respect the hustle!")
    st.write("- @earlybird: Good morning coding session? Love it!")

    st.markdown("---")

    # Optionally, a placeholder for new comments
    st.write("Add a comment:")
    user_comment = st.text_input("Enter your comment here", "")
    if st.button("Post Comment"):
        st.success(f"Your comment was posted: {user_comment}")