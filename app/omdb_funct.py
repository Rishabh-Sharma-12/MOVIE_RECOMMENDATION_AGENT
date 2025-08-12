import os
import json
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st
import requests
import json
# Load environment variables
load_dotenv()

# Constants - set your OMDb API key and base URL here
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
BASE_URL = "http://www.omdbapi.com/"
# --- API Helper with Retry ---

st.set_page_config(page_title="OMDb Movie Explorer", layout="wide")

def inject_global_css():
    """Inject all CSS styles for the application"""
    css = """
    <style>
    /* Main layout styles */
    .main {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #ffffff;
    }
    
    /* Header styles */
    .header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ff8a00, #e52e71);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Card styles */
    .netflix-card {
        display: flex;
        gap: 15px;
        background: rgba(30, 30, 30, 0.8);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        transition: all 0.3s ease;
        border-left: 4px solid #ff8a00;
    }
    
    .netflix-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
        background: rgba(40, 40, 40, 0.9);
    }
    
    .card-poster {
        width: 120px;
        height: 180px;
        object-fit: cover;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    .card-content {
        flex: 1;
        color: #eee;
    }
    
    .card-title {
        font-size: 1.4rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #fff;
    }
    
    .card-meta {
        font-size: 0.85rem;
        margin-bottom: 0.8rem;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }
    
    .rating-badge {
        background: linear-gradient(135deg, #2ecc71, #27ae60);
        padding: 3px 8px;
        border-radius: 20px;
        color: #fff;
        font-weight: bold;
        font-size: 0.8rem;
    }
    
    .meta-badge {
        background: rgba(85, 85, 85, 0.7);
        padding: 3px 8px;
        border-radius: 20px;
        color: #ddd;
        font-size: 0.8rem;
    }
    
    .imdb-badge {
        background: linear-gradient(135deg, #f5c518, #d4af37);
        padding: 3px 8px;
        border-radius: 20px;
        color: #000;
        font-weight: bold;
        font-size: 0.8rem;
    }
    
    .enhanced-description {
        font-size: 0.95rem;
        line-height: 1.4;
        margin-top: 0.5rem;
    }
    
    .enhanced-description p {
        margin: 0;
        color: #ccc;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 25px 0 15px 0;
        color: #ffa500;
        position: relative;
        padding-bottom: 8px;
    }
    
    .section-header:after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #ff8a00, #e52e71);
        border-radius: 3px;
    }
    
    /* Form styles */
    .stForm {
        background: rgba(30, 30, 30, 0.7);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Button styles */
    .stButton>button {
        background: linear-gradient(135deg, #ff8a00, #e52e71);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 138, 0, 0.4);
    }
    
    /* Input field styles */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>select {
        background: rgba(40, 40, 40, 0.8) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    
    /* Profile summary card */
    .profile-card {
        background: rgba(30, 30, 30, 0.8);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        border-left: 4px solid #e52e71;
    }
    
    /* Tooltip styles */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #333;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .netflix-card {
            flex-direction: column;
        }
        
        .card-poster {
            width: 100%;
            height: auto;
            max-height: 300px;
        }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def get_omdb(params, max_retries=5):
    params["apikey"] = OMDB_API_KEY
    for attempt in range(max_retries):
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            continue
    return {}

# --- Get Full Details of a Movie ---
def get_movie_details(imdb_id, plot="full"):
    return get_omdb({"i": imdb_id, "plot": plot})

# --- Search Movies with filters ---
def search_movie(query, year=None, country_filter=None, language_filter=None, movie_type=None, min_rating=0, plot_length="full"):
    # Step 1: Initial search only by title, no filters (to get max possible results)
    raw_results = get_omdb({"s": query})
    
    if not raw_results:
        return []
    
    if raw_results.get("Response") == "False":
        return []

    search_list = raw_results.get("Search", [])
    filtered_movies = []

    for item in search_list:
        details = get_movie_details(item["imdbID"], plot=plot_length)
        if not details or details.get("Response") == "False":
            continue

        # Apply year filter *after* fetching full details
        if year and details.get("Year") != year:
            continue

        # Apply country filter
        if country_filter and country_filter.lower() not in details.get("Country", "").lower():
            continue

        # Apply language filter
        if language_filter and language_filter.lower() not in details.get("Language", "").lower():
            continue

        # Apply movie_type filter (e.g. movie, series) from details['Type']
        if movie_type and movie_type.lower() != "all" and details.get("Type", "").lower() != movie_type.lower():
            continue

        # Apply IMDb rating filter
        try:
            imdb_rating = float(details.get("imdbRating", "0"))
            if imdb_rating < min_rating:
                continue
        except (ValueError, TypeError):
            pass  # skip rating filter if no rating

        details["source"] = "omdb"
        filtered_movies.append(details)

        if len(filtered_movies) >= 10:
            break

    return filtered_movies



# --- Recommendation Search ---
def recommend_movies(base_movie, max_results=5):
    if not base_movie.get("Genre"):
        return []
    genre_keyword = base_movie["Genre"].split(",")[0].strip()
    base_language = base_movie.get("Language", "").split(",")[0].strip().lower()

    search_results = get_omdb({"s": genre_keyword})
    if not search_results or search_results.get("Response") == "False":
        return []
    
    recs = []
    for item in search_results.get("Search", []):
        if item["imdbID"] == base_movie.get("imdbID"):
            continue
        
        details = get_movie_details(item["imdbID"])
        if not details:
            continue
        
        movie_language = details.get("Language", "").split(",")[0].strip().lower()
        if base_language and movie_language != base_language:
            continue
        
        if details.get("Title") != base_movie.get("Title"):
            recs.append(details)
        if len(recs) >= max_results:
            break
    return recs


# --- Display Movie Card ---
def display_movie_card(movie):
    poster_url = movie.get("Poster")
    title = movie.get("Title", "Unknown Title")
    year = movie.get("Year", "N/A")
    released = movie.get("Released", "N/A")
    genre = movie.get("Genre", "N/A")
    director = movie.get("Director", "N/A")
    rating = movie.get("imdbRating", "N/A")
    plot = movie.get("Plot", "No plot info available.")

    # Poster HTML with class
    if poster_url and poster_url != "N/A":
        poster_html = f'<img src="{poster_url}" alt="Poster" class="card-poster" />'
    else:
        poster_html = '<div class="card-poster" style="background:#333; display:flex; align-items:center; justify-content:center; color:#666;">No Poster</div>'

    # Rating badge style (green if >=7 else grey)
    try:
        rating_value = float(rating)
        rating_class = "rating-badge" if rating_value >= 7 else "meta-badge"
    except:
        rating_class = "meta-badge"

    card_html = f"""
    <div class="netflix-card">
        {poster_html}
        <div class="card-content">
            <div class="card-title">{title} ({year})</div>
            <div class="card-meta">
                <span class="meta-badge">📅 Released: {released}</span>
                <span class="meta-badge">🎬 Genre: {genre}</span>
                <span class="meta-badge">🎥 Director: {director}</span>
                <span class="{rating_class}">⭐ IMDb Rating: {rating}</span>
            </div>
            <div class="enhanced-description">
                <p><strong>🧾 Plot:</strong> {plot}</p>
            </div>
        </div>
    </div>
    <hr style="border-color: #444; margin: 20px 0;">
    """

    st.markdown(card_html, unsafe_allow_html=True)


# --- Main UI ---
def show_search_mode():
    inject_global_css()
    st.markdown('<div class="section-header">🔍 Direct Movie Search - Powered by OMDb</div>', unsafe_allow_html=True)
    
    with st.form("movie_search_form", clear_on_submit=False):
        # st.markdown('<div class="section-header">🎬 Search-Parameters</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            query = st.text_input("🔍 Movie Title", placeholder="e.g., Inception, The Dark Knight, Titanic")
        with col2:
            search_year = st.text_input("📅 Year (Optional)", placeholder="e.g., 2010")
        
        col3, col4, col5 = st.columns([1, 1, 1])
        with col3:
            country_filter = st.text_input("🌍 Country Filter", placeholder="e.g., USA, India, UK")
        with col4:
            language_filter = st.text_input("🗣️ Language Filter", placeholder="e.g., English, Hindi, Spanish")
        with col5:
            movie_type = st.selectbox("🎭 Type", ["All", "Movie", "Series", "Episode"])

        with st.expander("🔧 Advanced Search Options"):
            col6, col7 = st.columns([1, 1])
            with col6:
                min_rating = st.slider("Minimum IMDb Rating", 1.0, 10.0, 6.0, 0.1)
            with col7:
                plot_length = st.selectbox("Plot Detail Level", ["short", "full"], index=0)

        submitted = st.form_submit_button("🚀 Search Movies")
    
    if submitted and query:
        with st.spinner(f"🔍 Searching OMDb for '{query}'..."):
            movies = search_movie(
                query=query,
                year=search_year if search_year else None,
                country_filter=country_filter if country_filter else None,
                language_filter=language_filter if language_filter else None,
                movie_type=movie_type if movie_type != "All" else None,
                min_rating=min_rating,
                plot_length=plot_length
            )
            st.session_state.search_results = movies
            st.session_state.current_search_query = query

    
    if st.session_state.get("search_results"):
        results = st.session_state.search_results
        results_count = len(results)
        search_query = st.session_state.get("current_search_query", "your search")
        
        st.markdown(f'<div class="section-header">🎬 Found {results_count} Movie{"s" if results_count != 1 else ""} for "{search_query}"</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.metric("Total Results", results_count)
        with col2:
            valid_ratings = [float(m.get('imdbRating', 0)) for m in results if m.get('imdbRating') and m.get('imdbRating') != 'N/A']
            avg_rating = sum(valid_ratings) / len(valid_ratings) if valid_ratings else 0
            st.metric("Average Rating", f"{avg_rating:.1f}/10" if avg_rating else "N/A")
        with col3:
            years = [m.get('Year') for m in results if m.get('Year') and m.get('Year') != 'N/A']
            year_range = f"{min(years)}-{max(years)}" if len(set(years)) > 1 else (years[0] if years else "N/A")
            st.metric("Year Range", year_range)
        
        st.markdown("---")
        
        for movie in results:
            display_movie_card(movie)
            with st.expander(f"📋 Detailed Info: {movie.get('Title', 'Unknown')}"):
                col_detail1, col_detail2 = st.columns([1, 1])
                with col_detail1:
                    st.markdown("#### 🎬 Production Details")
                    for key in ["Director", "Writer", "Actors", "Production", "BoxOffice"]:
                        val = movie.get(key, "N/A")
                        if val != "N/A":
                            st.markdown(f"**{key}:** {val}")
                with col_detail2:
                    st.markdown("#### 📊 Ratings & Awards")
                    for key in ["imdbRating", "imdbVotes", "Metascore", "Awards", "Runtime"]:
                        val = movie.get(key, "N/A")
                        if val != "N/A":
                            st.markdown(f"**{key}:** {val}")
                
                # Recommendations based on this movie
                st.markdown("---")
                st.markdown(f"🎯 Recommended movies based on **{movie.get('Title')}**:")
                recs = recommend_movies(movie)
                if not recs:
                    st.info("No recommendations found.")
                else:
                    for rec in recs:
                        display_movie_card(rec)
            st.markdown("---")
        
        # Export button
        if st.button("📥 Export Search Results as JSON"):
            export_data = []
            for m in results:
                export_data.append({
                    'Title': m.get('Title', 'N/A'),
                    'Year': m.get('Year', 'N/A'),
                    'IMDb Rating': m.get('imdbRating', 'N/A'),
                    'Genre': m.get('Genre', 'N/A'),
                    'Director': m.get('Director', 'N/A'),
                    'Plot': (m.get('Plot', '')[:200] + '...') if len(m.get('Plot', '')) > 200 else m.get('Plot', 'N/A')
                })
            json_data = json.dumps(export_data, indent=2)
            st.download_button(
                label="📄 Download as JSON",
                data=json_data,
                file_name=f"omdb_search_{search_query.replace(' ', '_')}.json",
                mime="application/json"
            )
    elif submitted and query:
        st.warning(f"🤷‍♂️ No movies found for '{query}'. Try:")
        st.markdown("""
        - **Check spelling** - Make sure the movie title is spelled correctly  
        - **Try partial titles** - Search for part of the movie name  
        - **Remove filters** - Clear country/language filters to broaden search  
        - **Use alternative titles** - Some movies have different titles in different regions  
        """)

def main_omdb():
    show_search_mode()

if __name__ == "__main__":
    main_omdb()
