from unittest import result
import streamlit as st
import pandas as pd
import json
import os
import datetime
import time
import random
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Set page configuration with emoji
st.set_page_config(
    page_title=" Personal Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
.main-header {
    font-size: 3rem !important;
    color: #1E3A8A;
    margin-bottom: 1rem;
    font-weight: 700;
    text-align: center;
    text-shadow: 2px 2px 4px rgba(0,0,0,1);
}
.sub_header {
    font-size: 1.8rem !important;
    color: #B82F6F;
    margin-bottom: 1rem;
    font-weight: 600;
    margin-top: 1rem;
}
.success_message {
    padding: 1rem;
    background-color: #ECFDF5;
    border-left: 5px solid #10B981;
    border-radius: 0.375rem;
}
.warning_message {
    padding: 1rem;
    background-color: #FEF3C7;
    border-left: 5px solid #F59E0B;
    border-radius: 0.375rem;
}
.book-card {
    padding: 1rem;
    background-color: #F3F4F6;
    border-left: 5px solid #3B82F6;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    transition: transform 0.3s ease;
}
.book-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
}
.read-badge {
    background-color: #10B981;
    color: white;
    padding: 0.25rem 0.75rem;
    font-size: 1rem;
    font-weight: 600;
    border-radius: 1rem;
}
.unread-badge {
    background-color: #F87171;
    color: white;
    padding: 0.25rem 0.75rem;
    font-size: 1rem;
    font-weight: 600;
    border-radius: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "library" not in st.session_state:
    st.session_state.library = []
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "book_added" not in st.session_state:
    st.session_state.book_added = False
if "book_removed" not in st.session_state:
    st.session_state.book_removed = False
if "current_view" not in st.session_state:
    st.session_state.current_view = "library"

# Sidebar navigation
nav_options = st.sidebar.radio(
    "Choose an option:",
    ["View Library", "Add Book", "Search Books", "Library Statistics"]
)

# Update current view based on selection
st.session_state.current_view = nav_options.lower().replace(" ", "_")

# Define view rendering functions
def render_view_library():
    st.markdown("<h2 class='sub_header'>Your Library</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.markdown("<div class='warning_message'>Your library is empty. Add some books to get started!</div>", unsafe_allow_html=True)
    else:
        cols = st.columns(2)
        for i, book in enumerate(st.session_state.library):
            with cols[i % 2]:
                st.markdown(f"""
                <div class='book-card'>
                    <h3>{book['title']}</h3>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                    <p><strong>Genre:</strong> {book['genre']}</p>
                    <p><span class='{'read-badge' if book['read_status'] else 'unread-badge'}'>{'Read' if book['read_status'] else 'Unread'}</span></p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Remove", key=f"remove_{i}"):
                    st.session_state.library.pop(i)
                    st.session_state.book_removed = True
                    st.experimental_rerun()


def render_add_book():
    st.markdown("<h2 class='sub_header'>Add a New Book</h2>", unsafe_allow_html=True)
    with st.form("add_book_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Book Title", max_chars=100)
            author = st.text_input("Author", max_chars=100)
            publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.datetime.now().year, step=1, value=2023)
        with col2:
            genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science", "Technology", "Fantasy", "History", "Art", "Religion"])
            read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True)
            submit_button = st.form_submit_button("Add Book")

        if submit_button and title and author:
            new_book = {
                'title': title,
                'author': author,
                'publication_year': publication_year,
                'genre': genre,
                'read_status': read_status == "Read",
                'added_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.library.append(new_book)
            st.session_state.book_added = True
            st.success("Book added successfully!")


def render_search_books():
    st.markdown("<h2 class='sub_header'>Search Books</h2>", unsafe_allow_html=True)
    search_by = st.selectbox("Search by:", ["title", "author", "genre"])
    search_term = st.text_input("Enter search term:")

    if st.button("Search"):
        results = [book for book in st.session_state.library if search_term.lower() in book[search_by].lower()]
        st.session_state.search_results = results

        if results:
            for book in results:
                st.markdown(f"""
                <div class='book-card'>
                    <h3>{book['title']}</h3>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                    <p><strong>Genre:</strong> {book['genre']}</p>
                    <p><span class='{'read-badge' if book['read_status'] else 'unread-badge'}'>{'Read' if book['read_status'] else 'Unread'}</span></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No books found matching your search.")


def render_statistics():
    st.markdown("<h2 class='sub_header'>Library Statistics</h2>", unsafe_allow_html=True)
    total_books = len(st.session_state.library)
    read_books = sum(book['read_status'] for book in st.session_state.library)
    unread_books = total_books - read_books

    st.metric("Total Books", total_books)
    st.metric("Read Books", read_books)
    st.metric("Unread Books", unread_books)

    if total_books > 0:
        fig = go.Figure(data=[
            go.Pie(labels=['Read', 'Unread'], values=[read_books, unread_books], hole=.4)
        ])
        st.plotly_chart(fig, use_container_width=True)

# Load library (if stored in JSON)
def load_library():
    if os.path.exists("library.json"):
        with open("library.json", "r") as f:
            st.session_state.library = json.load(f)

def save_library():
    with open("library.json", "w") as f:
        json.dump(st.session_state.library, f)

load_library()

# Render the selected view
if st.session_state.current_view == "view_library":
    render_view_library()
elif st.session_state.current_view == "add_book":
    render_add_book()
elif st.session_state.current_view == "search_books":
    render_search_books()
elif st.session_state.current_view == "library_statistics":
    render_statistics()

# Save changes
save_library()

# Copyright footer
st.markdown("<hr><p style='text-align:center;'>© 2025 Ayla Rehman - Personal Library Manager</p>", unsafe_allow_html=True)
