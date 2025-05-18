import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

import time
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Set page configuration with emoji
st.set_page_config(
    page_title="Personal Library Management System",
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
.sub-header {
    font-size: 1.8rem !important;
    color: #B82F6F;
    margin-bottom: 1rem;
    font-weight: 600;
    margin-top: 1rem;
}
.success-message {
    padding: 1rem;
    background-color: #ECFDF5;
    border-left: 5px solid #10B981;
    border-radius: 0.375rem;
    margin-bottom: 1rem;
}
.warning-message {
    padding: 1rem;
    background-color: #FEF3C7;
    border-left: 5px solid #F59E0B;
    border-radius: 0.375rem;
    margin-bottom: 1rem;
}
.book-card {
    padding: 1rem;
    background-color: #F3F4F6;
    border-left: 5px solid #3B82F6;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    transition: transform 0.3s ease;
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
.action-button {
    margin-right: 0.5rem;
}
.stButton > button {
    border-radius: 0.375rem;
}
</style>
""", unsafe_allow_html=True)

# Function to load Lottie animations
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Initialize session state variables
if "library" not in st.session_state:
    st.session_state.library = []

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "book_added" not in st.session_state:
    st.session_state.book_added = False

if "book_removed" not in st.session_state:
    st.session_state.book_removed = False

if "current_view" not in st.session_state:
    st.session_state.current_view = 'library'

# Load library from JSON file
def load_library():
    try:
        if os.path.exists("library.json"):
            with open('library.json', 'r') as file:
                st.session_state.library = json.load(file)
            return True
        return False
    except Exception as e:
        st.error(f"Error loading library: {e}")
        return False

# Save library to JSON file
def save_library():
    try:
        with open('library.json', 'w') as file:
            json.dump(st.session_state.library, file, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False

# Add a book to the library
def add_book(title, author, publication_year, genre, read_status):
    book = {
        'title': title,
        'author': author,
        'publication_year': publication_year,
        'genre': genre,
        'read_status': read_status,
        'added_date': datetime.now().strftime("%y-%m-%d-%H:%M;%S"),

    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True

# Remove a book by index
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        return True
    return False

# Search books by a field
def search_books(search_term, search_by):
    search_term = search_term.lower()
    results = []
    for book in st.session_state.library:
        if search_by == 'title' and search_term in book['title'].lower():
            results.append(book)
        elif search_by == 'author' and search_term in book['author'].lower():
            results.append(book)
        elif search_by == 'genre' and search_term in book['genre'].lower():
            results.append(book)
    st.session_state.search_results = results

# Get statistics about the library
def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book['read_status'])
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0

    genres = {}
    authors = {}
    decades = {}

    for book in st.session_state.library:
        # Genres count
        genres[book['genre']] = genres.get(book['genre'], 0) + 1
        # Authors count
        authors[book['author']] = authors.get(book['author'], 0) + 1
        # Decade count
        decade = (book['publication_year'] // 10) * 10
        decades[decade] = decades.get(decade, 0) + 1

    # Sort dictionaries
    genres = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))
    authors = dict(sorted(authors.items(), key=lambda x: x[1], reverse=True))
    decades = dict(sorted(decades.items(), key=lambda x: x[0]))

    return {
        'total_books': total_books,
        'read_books': read_books,
        'percent_read': percent_read,
        'genres': genres,
        'authors': authors,
        'decades': decades
    }

# Create visualizations using Plotly
def create_visualizations(stats):
    if stats['total_books'] == 0:
        st.info("No books in library to display statistics.")
        return

    # Pie chart for read/unread books
    fig_read_status = go.Figure(data=[go.Pie(
        labels=['Read', 'Unread'],
        values=[stats['read_books'], stats['total_books'] - stats['read_books']],
        hole=.4,
        marker_colors=['#10B981', '#F87171']
    )])
    fig_read_status.update_layout(
        title_text="Read vs Unread Books",
        showlegend=True,
        height=400
    )
    st.plotly_chart(fig_read_status, use_container_width=True)

    # Bar chart for genres
    if stats['genres']:
        genres_df = pd.DataFrame({
            'Genre': list(stats['genres'].keys()),
            'Count': list(stats['genres'].values())
        })
        fig_genres = px.bar(
            genres_df,
            x='Genre',
            y='Count',
            color='Count',
            color_continuous_scale=px.colors.sequential.Blues
        )
        fig_genres.update_layout(
            title_text='Books by Genre',
            xaxis_title='Genre',
            yaxis_title='Number of Books',
            height=400
        )
        st.plotly_chart(fig_genres, use_container_width=True)

    # Line chart for decades
    if stats['decades']:
        decades_df = pd.DataFrame({
            'Decade': [f"{decade}s" for decade in stats['decades'].keys()],
            'Count': list(stats['decades'].values())
        })
        fig_decades = px.line(
            decades_df,
            x='Decade',
            y='Count',
            markers=True,
            line_shape="spline"
        )
        fig_decades.update_layout(
            title_text='Books by Publication Decade',
            xaxis_title='Decade',
            yaxis_title='Number of Books',
            height=400
        )
        st.plotly_chart(fig_decades, use_container_width=True)

# ---- MAIN APP ----

# Load library on start
load_library()

# Sidebar with navigation and Lottie animation
st.sidebar.markdown("<h1 style='text-align:center;'>Navigation</h1>", unsafe_allow_html=True)
lottie_book = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_1f20_aKAfIn.json")
if lottie_book:
    st.sidebar_lottie = st_lottie(lottie_book, height=200, key='book_animation')

# Navigation radio buttons
nav_options = st.sidebar.radio(
    "Choose an option:",
    ["View Library", "Add Book", "Search Books", "Library Statistics"]
)

# Update current view in session state
st.session_state.current_view = nav_options.lower().replace(" ", "_")

# VIEW LIBRARY
if st.session_state.current_view == "view_library":
    st.markdown("<h1 class='main-header'>Your Library</h1>", unsafe_allow_html=True)

    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your library is empty. Add some books to get started!</div>", unsafe_allow_html=True)
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
                    <p><span class='{"read-badge" if book["read_status"] else "unread-badge"}'>
                    {"Read" if book["read_status"] else "Unread"}
                    </span></p>
                </div>
                """, unsafe_allow_html=True)

                # Buttons for remove and toggle read status
                col1, col2 = st.columns([1, 2])
                with col1:
                    if st.button("Remove", key=f"remove_{i}"):
                        if remove_book(i):
                            st.experimental_rerun()
                with col2:
                    new_status = not book['read_status']
                    status_label = "Mark as Read" if not book['read_status'] else "Mark as Unread"
                    if st.button(status_label, key=f"toggle_{i}"):
                        st.session_state.library[i]['read_status'] = new_status
                        save_library()
                        st.experimental_rerun()

    # Show removal success message
    if st.session_state.book_removed:
        st.success("Book removed successfully!")
        st.session_state.book_removed = False

# ADD BOOK VIEW
elif st.session_state.current_view == "add_book":
    st.markdown("<h1 class='main-header'>Add a New Book</h1>", unsafe_allow_html=True)

    with st.form(key='add_book_form'):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Book Title", max_chars=100)
            author = st.text_input("Author(s)", max_chars=100)
            publication_year  = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, step=1, value=datetime.now().year)


        with col2:
            genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science", "Technology", "Fantasy", "History", "Art", "Religion"])
            read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True)
            read_bool = (read_status == "Read")

        submitted = st.form_submit_button("Add Book")

        if submitted:
            if title.strip() == "" or author.strip() == "":
                st.warning("Please provide both Title and Author.")
            else:
                add_book(title.strip(), author.strip(), publication_year, genre, read_bool)
                if st.session_state.book_added:
                    st.success("Book added successfully!")
                    st.balloons()
                    st.session_state.book_added = False

# SEARCH BOOK VIEW
elif st.session_state.current_view == "search_books":
    st.markdown("<h1 class='main-header'>Search Books</h1>", unsafe_allow_html=True)

    search_by = st.selectbox("Search by:", ['title', 'author', 'genre'])
    search_term = st.text_input("Enter search term:")

    if st.button("Search"):
        if search_term.strip() == "":
            st.warning("Please enter a search term.")
        else:
            with st.spinner("Searching..."):
                time.sleep(0.5)
                search_books(search_term.strip(), search_by)

            if st.session_state.search_results:
                st.markdown(f"<h3>Found {len(st.session_state.search_results)} result(s):</h3>", unsafe_allow_html=True)
                for book in st.session_state.search_results:
                    st.markdown(f"""
                    <div class='book-card'>
                        <h3>{book['title']}</h3>
                        <p><strong>Author:</strong> {book['author']}</p>
                        <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                        <p><strong>Genre:</strong> {book['genre']}</p>
                        <p><span class='{"read-badge" if book["read_status"] else "unread-badge"}'>
                        {"Read" if book["read_status"] else "Unread"}
                        </span></p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No books found matching your search.")

# LIBRARY STATISTICS VIEW
elif st.session_state.current_view == "library_statistics":
    st.markdown("<h1 class='main-header'>Library Statistics</h1>", unsafe_allow_html=True)

    if not st.session_state.library:
        st.warning("Your library is empty. Add some books to see statistics.")
    else:
        stats = get_library_stats()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Books", stats['total_books'])
        col2.metric("Books Read", stats['read_books'])
        col3.metric("Percentage Read", f"{stats['percent_read']:.1f}%")

        create_visualizations(stats)

        if stats['authors']:
            st.markdown("<h2>Top Authors</h2>", unsafe_allow_html=True)
            top_authors = dict(list(stats['authors'].items())[:5])
            for author, count in top_authors.items():
                st.markdown(f"**{author}**: {count} book{'s' if count > 1 else ''}")
                st.markdown("---")

# Footer
st.markdown("<hr><p style='text-align:center;'>© 2025 Ayla Rehman - Personal Library Manager</p>", unsafe_allow_html=True)
