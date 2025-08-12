# import streamlit as st
# import requests
# import os
# from dotenv import load_dotenv

# # --- Setup ---
# load_dotenv()
# OMDB_API_KEY = os.getenv("OMDB_API_KEY")
# BASE_URL = "http://www.omdbapi.com/"

# st.set_page_config(page_title="🎬 OMDb Movie Explorer", layout="wide")

# # --- Netflix-Inspired CSS ---
# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

# /* Global dark theme */
# html, body, .main, .stApp {
#     background-color: #141414 !important;
#     color: #ffffff !important;
#     font-family: 'Inter', sans-serif;
#     transition: all 0.3s ease;
# }

# /* Movie card container */
# .netflix-card {
#     display: flex;
#     flex-direction: row;
#     background: linear-gradient(145deg, #1a1a1a 0%, #2d2d2d 100%);
#     border-radius: 12px;
#     overflow: hidden;
#     transition: all 0.3s ease;
#     border: 1px solid #333;
#     height: auto;
#     width: 100%;
#     max-width: 900px;
#     margin: 1rem auto 1.5rem auto;
#     position: relative;
#     cursor: pointer;
# }
# .netflix-card:hover {
#     transform: translateY(-5px);
#     box-shadow: 0 12px 30px rgba(229, 9, 20, 0.3);
#     border-color: #E50914;
#     z-index: 10;
# }
# .netflix-card::before {
#     content: '';
#     position: absolute;
#     inset: 0;
#     background: linear-gradient(135deg, transparent 0%, rgba(229, 9, 20, 0.1) 100%);
#     opacity: 0;
#     transition: opacity 0.3s ease;
#     pointer-events: none;
# }
# .netflix-card:hover::before {
#     opacity: 1;
# }

# /* Poster */
# .card-poster {
#     width: 200px;
#     height: 300px;
#     object-fit: cover;
#     flex-shrink: 0;
#     background-color: #222;
#     border-right: 2px solid #E50914;
# }

# /* Card content */
# .card-content {
#     padding: 1rem 1.5rem;
#     flex-grow: 1;
#     display: flex;
#     flex-direction: column;
#     justify-content: space-between;
# }

# /* Title */
# .card-title {
#     font-size: 1.2rem;
#     font-weight: 600;
#     color: #ffffff;
#     margin-bottom: 0.8rem;
#     line-height: 1.3;
#     overflow: hidden;
#     display: -webkit-box;
#     -webkit-line-clamp: 2;
#     -webkit-box-orient: vertical;
# }

# /* Meta section */
# .card-meta {
#     display: flex;
#     gap: 0.6rem;
#     margin-bottom: 0.8rem;
#     flex-wrap: wrap;
# }

# /* Meta badges */
# .meta-badge {
#     background: linear-gradient(135deg, #E50914 0%, #B20710 100%);
#     color: white;
#     padding: 0.3rem 0.7rem;
#     border-radius: 20px;
#     font-size: 0.75rem;
#     font-weight: 500;
#     text-transform: uppercase;
#     letter-spacing: 0.5px;
# }

# .rating-badge {
#     background: linear-gradient(135deg, #ffd700 0%, #ffb300 100%);
#     color: #000;
# }

# /* Enhanced Description */
# .enhanced-description {
#     font-size: 0.85rem;
#     margin-top: 10px;
#     color: #e0e0e0;
#     background-color: #1c1c1c;
#     padding: 10px;
#     border-radius: 10px;
#     line-height: 1.5;
# }

# /* Mobile styles */
# @media (max-width: 768px) {
#     .netflix-card {
#         flex-direction: column;
#         align-items: center;
#     }
#     .card-poster {
#         width: 100%;
#         height: auto;
#         aspect-ratio: 2 / 3;
#         border-right: none;
#         border-bottom: 2px solid #E50914;
#     }
#     .card-content {
#         padding: 1rem;
#     }
# }
# </style>
# """, unsafe_allow_html=True)


# # --- API Helper with Retry ---
# def get_omdb(params, max_retries=5):
#     params["apikey"] = OMDB_API_KEY
#     for attempt in range(max_retries):
#         try:
#             response = requests.get(BASE_URL, params=params, timeout=10)
#             if response.status_code == 200:
#                 return response.json()
#         except requests.exceptions.RequestException:
#             continue
#     return {}

# # --- Get Full Details of a Movie ---
# def get_movie_details(imdb_id):
#     return get_omdb({"i": imdb_id, "plot": "full"})

# # --- Search Movies ---
# def search_movie(query, country_filter=None, language_filter=None):
#     raw_results = get_omdb({"s": query})
#     if not raw_results or raw_results.get("Response") == "False":
#         return []

#     search_list = raw_results.get("Search", [])
#     filtered = []

#     for item in search_list:
#         details = get_movie_details(item["imdbID"])
#         if not details:
#             continue
#         if country_filter and country_filter.lower() not in details.get("Country", "").lower():
#             continue
#         if language_filter and language_filter.lower() not in details.get("Language", "").lower():
#             continue
#         filtered.append(details)

#     return filtered

# # --- Recommendation Search ---
# def recommend_movies(base_movie, max_results=5):
#     """Recommend movies based on Genre + Language + Year range."""
#     if not base_movie.get("Genre"):
#         return []
    
#     # Extract base movie details
#     genre_keyword = base_movie["Genre"].split(",")[0].strip()
#     base_language = base_movie.get("Language", "").split(",")[0].strip().lower()  

#     # Search by genre
#     search_results = get_omdb({"s": genre_keyword})
#     if not search_results or search_results.get("Response") == "False":
#         return []
    
#     recs = []
#     for item in search_results.get("Search", []):
#         if item["imdbID"] == base_movie.get("imdbID"):
#             continue
        
#         details = get_movie_details(item["imdbID"])
#         if not details:
#             continue
        
#         # Language match
#         movie_language = details.get("Language", "").split(",")[0].strip().lower()
#         if base_language and movie_language != base_language:
#             continue
        
#         # Add to recommendations
#         if details.get("Title") != base_movie.get("Title"):
#             recs.append(details)
        
#         if len(recs) >= max_results:
#             break
    
#     return recs


# # --- Display a Movie Card ---
# def display_movie_card(movie):
#     col1, col2 = st.columns([1, 3])

#     with col1:
#         if movie.get("Poster") and movie["Poster"] != "N/A":
#             st.image(movie["Poster"], use_container_width=True)
#         else:
#             st.warning("No poster available")

#     with col2:
#         st.markdown(f"### {movie.get('Title', 'Unknown Title')} ({movie.get('Year', 'N/A')})")
#         st.markdown(f"**📅 Released:** {movie.get('Released', 'N/A')}")
#         st.markdown(f"**🎬 Genre:** {movie.get('Genre', 'N/A')}")
#         st.markdown(f"**🎞️ Director:** {movie.get('Director', 'N/A')}")
#         st.markdown(f"**🌟 IMDb Rating:** {movie.get('imdbRating', 'N/A')}")
#         st.markdown(f"**🧾 Plot:** {movie.get('Plot', 'No plot info available.')}")
#         st.markdown("---")

# # # --- Main UI ---
# # # --- Main UI ---
# # def app_1():
# #     st.markdown('<div class="app-header">🎥 <strong>OMDb Movie Explorer</strong> + Recommendations</div>', unsafe_allow_html=True)

# #     with st.form("movie_search_form"):
# #         query = st.text_input("🔍 Search for a movie", placeholder="Try 'Inception'")
# #         country = st.text_input("🌍 Country filter (optional)", placeholder="e.g. India")
# #         language = st.text_input("🗣️ Language filter (optional)", placeholder="e.g. Hindi")
# #         submitted = st.form_submit_button("🔎 Search")

# #     if submitted and query:
# #         with st.spinner("Searching OMDb..."):
# #             results = search_movie(query, country_filter=country, language_filter=language)
# #         if not results:
# #             st.warning("No movies found with specified filters.")
# #         else:
# #             for movie in results:
# #                 display_movie_card(movie)
# #                 with st.expander(f"🎯 Recommended based on {movie['Title']}"):
# #                     recs = recommend_movies(movie)
# #                     if not recs:
# #                         st.info("No recommendations found.")
# #                     else:
# #                         for rec in recs:
# #                             display_movie_card(rec)
                            
                            
                            
# def show_search_mode():
#     """OMDb-based direct movie search without AI enhancements"""
#     st.markdown('<div class="section-header">🔍 Direct Movie Search - Powered by OMDb</div>', unsafe_allow_html=True)
    
#     with st.form("movie_search_form", clear_on_submit=False):
#         st.markdown("### 🎬 Search Parameters")
        
#         col1, col2 = st.columns([2, 1])
        
#         with col1:
#             query = st.text_input(
#                 "🔍 Movie Title", 
#                 placeholder="e.g., Inception, The Dark Knight, Titanic",
#                 help="Enter the movie title you're looking for"
#             )
        
#         with col2:
#             search_year = st.text_input(
#                 "📅 Year (Optional)", 
#                 placeholder="e.g., 2010",
#                 help="Filter by release year"
#             )
        
#         col3, col4, col5 = st.columns([1, 1, 1])
        
#         with col3:
#             country_filter = st.text_input(
#                 "🌍 Country Filter", 
#                 placeholder="e.g., USA, India, UK",
#                 help="Filter movies by country of origin"
#             )
        
#         with col4:
#             language_filter = st.text_input(
#                 "🗣️ Language Filter", 
#                 placeholder="e.g., English, Hindi, Spanish",
#                 help="Filter movies by language"
#             )
        
#         with col5:
#             movie_type = st.selectbox(
#                 "🎭 Type",
#                 ["All", "Movie", "Series", "Episode"],
#                 help="Filter by content type"
#             )
        
#         with st.expander("🔧 Advanced Search Options"):
#             col6, col7 = st.columns([1, 1])
            
#             with col6:
#                 min_rating = st.slider(
#                     "Minimum IMDb Rating",
#                     min_value=1.0,
#                     max_value=10.0,
#                     value=6.0,
#                     step=0.1,
#                     help="Filter movies with rating above this threshold"
#                 )
            
#             with col7:
#                 plot_length = st.selectbox(
#                     "Plot Detail Level",
#                     ["short", "full"],
#                     index=1,
#                     help="Choose plot summary length"
#                 )
        
#         submitted = st.form_submit_button("🚀 Search Movies", type="primary")
    
#     st.markdown('</div>', unsafe_allow_html=True)

#     if submitted and query:
#         with st.spinner(f"🔍 Searching OMDb for '{query}'..."):
#             log_message(f"User searched for: {query}")
            
#             movies = enhanced_search_movie(
#                 query=query,
#                 year=search_year if search_year else None,
#                 country_filter=country_filter if country_filter else None,
#                 language_filter=language_filter if language_filter else None,
#                 movie_type=movie_type if movie_type != "All" else None,
#                 min_rating=min_rating,
#                 plot_length=plot_length
#             )
            
#             st.session_state.search_results = movies
#             st.session_state.current_search_query = query

#     if st.session_state.get("search_results"):
#         results_count = len(st.session_state.search_results)
#         search_query = st.session_state.get("current_search_query", "your search")
        
#         st.markdown(
#             f'<div class="section-header">🎬 Found {results_count} Movie{"s" if results_count != 1 else ""} for "{search_query}"</div>', 
#             unsafe_allow_html=True
#         )
        
#         col1, col2, col3 = st.columns([1, 1, 1])
#         with col1:
#             st.metric("Total Results", results_count)
#         with col2:
#             valid_ratings = [float(movie.get('imdbRating', 0)) for movie in st.session_state.search_results 
#                              if movie.get('imdbRating') and movie.get('imdbRating') != 'N/A']
#             avg_rating = sum(valid_ratings) / len(valid_ratings) if valid_ratings else 0
#             st.metric("Average Rating", f"{avg_rating:.1f}/10" if avg_rating > 0 else "N/A")
#         with col3:
#             years = [movie.get('Year') for movie in st.session_state.search_results if movie.get('Year') != 'N/A']
#             year_range = f"{min(years)}-{max(years)}" if len(set(years)) > 1 else years[0] if years else "N/A"
#             st.metric("Year Range", year_range)
        
#         st.markdown("---")
        
#         for i, movie in enumerate(st.session_state.search_results):
#             movie_key = f"omdb_{movie.get('imdbID', i)}"
#             card_html = display_movie_card_universal(movie, movie_key)
#             st.markdown(card_html, unsafe_allow_html=True)
            
#             with st.expander(f"📋 Detailed Info: {movie.get('Title', 'Unknown')}", expanded=False):
#                 col_detail1, col_detail2 = st.columns([1, 1])
                
#                 with col_detail1:
#                     st.markdown("#### 🎬 Production Details")
#                     details = {
#                         "Director": movie.get('Director', 'N/A'),
#                         "Writer": movie.get('Writer', 'N/A'),
#                         "Actors": movie.get('Actors', 'N/A'),
#                         "Production": movie.get('Production', 'N/A'),
#                         "Box Office": movie.get('BoxOffice', 'N/A')
#                     }
                    
#                     for key, value in details.items():
#                         if value != 'N/A':
#                             st.markdown(f"**{key}:** {value}")
                
#                 with col_detail2:
#                     st.markdown("#### 📊 Ratings & Awards")
#                     ratings_info = {
#                         "IMDb Rating": movie.get('imdbRating', 'N/A'),
#                         "IMDb Votes": movie.get('imdbVotes', 'N/A'),
#                         "Metascore": movie.get('Metascore', 'N/A'),
#                         "Awards": movie.get('Awards', 'N/A'),
#                         "Runtime": movie.get('Runtime', 'N/A')
#                     }
                    
#                     for key, value in ratings_info.items():
#                         if value != 'N/A':
#                             st.markdown(f"**{key}:** {value}")
            
#             st.markdown("---")
        
#         if st.button("📥 Export Search Results", key="export_results"):
#             export_data = []
#             for movie in st.session_state.search_results:
#                 export_data.append({
#                     'Title': movie.get('Title', 'N/A'),
#                     'Year': movie.get('Year', 'N/A'),
#                     'IMDb Rating': movie.get('imdbRating', 'N/A'),
#                     'Genre': movie.get('Genre', 'N/A'),
#                     'Director': movie.get('Director', 'N/A'),
#                     'Plot': movie.get('Plot', 'N/A')[:200] + '...' if len(movie.get('Plot', '')) > 200 else movie.get('Plot', 'N/A')
#                 })
            
#             import json
#             json_data = json.dumps(export_data, indent=2)
#             st.download_button(
#                 label="📄 Download as JSON",
#                 data=json_data,
#                 file_name=f"cinematch_search_{search_query.replace(' ', '_')}.json",
#                 mime="application/json"
#             )
    
#     elif submitted and query and not st.session_state.get("search_results"):
#         st.warning(f"🤷‍♂️ No movies found for '{query}'. Try:")
#         st.markdown("""
#         - **Check spelling** - Make sure the movie title is spelled correctly
#         - **Try partial titles** - Search for part of the movie name
#         - **Remove filters** - Clear country/language filters to broaden search
#         - **Use alternative titles** - Some movies have different titles in different regions
#         """)


# Standard Library Imports
import os
import re
import json
import time
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
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


# def inject_global_css():
#     """Inject all CSS styles for the application"""
#     css = """
#     <style>
#     /* Main layout styles */
#     .main {
#         background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
#         color: #ffffff;
#     }
    
#     /* Header styles */
#     .header {
#         font-size: 2.5rem;
#         font-weight: 800;
#         background: linear-gradient(90deg, #ff8a00, #e52e71);
#         -webkit-background-clip: text;
#         background-clip: text;
#         color: transparent;
#         margin-bottom: 1rem;
#         text-align: center;
#     }
    
#     /* Card styles */
#     .netflix-card {
#         display: flex;
#         gap: 15px;
#         background: rgba(30, 30, 30, 0.8);
#         border-radius: 12px;
#         padding: 15px;
#         margin-bottom: 15px;
#         transition: all 0.3s ease;
#         border-left: 4px solid #ff8a00;
#     }
    
#     .netflix-card:hover {
#         transform: translateY(-3px);
#         box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
#         background: rgba(40, 40, 40, 0.9);
#     }
    
#     .card-poster {
#         width: 120px;
#         height: 180px;
#         object-fit: cover;
#         border-radius: 8px;
#         box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
#     }
    
#     .card-content {
#         flex: 1;
#         color: #eee;
#     }
    
#     .card-title {
#         font-size: 1.4rem;
#         font-weight: bold;
#         margin-bottom: 0.5rem;
#         color: #fff;
#     }
    
#     .card-meta {
#         font-size: 0.85rem;
#         margin-bottom: 0.8rem;
#         display: flex;
#         flex-wrap: wrap;
#         gap: 8px;
#     }
    
#     .rating-badge {
#         background: linear-gradient(135deg, #2ecc71, #27ae60);
#         padding: 3px 8px;
#         border-radius: 20px;
#         color: #fff;
#         font-weight: bold;
#         font-size: 0.8rem;
#     }
    
#     .meta-badge {
#         background: rgba(85, 85, 85, 0.7);
#         padding: 3px 8px;
#         border-radius: 20px;
#         color: #ddd;
#         font-size: 0.8rem;
#     }
    
#     .imdb-badge {
#         background: linear-gradient(135deg, #f5c518, #d4af37);
#         padding: 3px 8px;
#         border-radius: 20px;
#         color: #000;
#         font-weight: bold;
#         font-size: 0.8rem;
#     }
    
#     .enhanced-description {
#         font-size: 0.95rem;
#         line-height: 1.4;
#         margin-top: 0.5rem;
#     }
    
#     .enhanced-description p {
#         margin: 0;
#         color: #ccc;
#     }
    
#     /* Section headers */
#     .section-header {
#         font-size: 1.8rem;
#         font-weight: 700;
#         margin: 25px 0 15px 0;
#         color: #ffa500;
#         position: relative;
#         padding-bottom: 8px;
#     }
    
#     .section-header:after {
#         content: '';
#         position: absolute;
#         bottom: 0;
#         left: 0;
#         width: 60px;
#         height: 3px;
#         background: linear-gradient(90deg, #ff8a00, #e52e71);
#         border-radius: 3px;
#     }
    
#     /* Form styles */
#     .stForm {
#         background: rgba(30, 30, 30, 0.7);
#         border-radius: 12px;
#         padding: 20px;
#         margin-bottom: 25px;
#         border: 1px solid rgba(255, 255, 255, 0.1);
#     }
    
#     /* Button styles */
#     .stButton>button {
#         background: linear-gradient(135deg, #ff8a00, #e52e71);
#         color: white;
#         border: none;
#         border-radius: 8px;
#         padding: 10px 20px;
#         font-weight: bold;
#         transition: all 0.3s;
#     }
    
#     .stButton>button:hover {
#         transform: translateY(-2px);
#         box-shadow: 0 5px 15px rgba(255, 138, 0, 0.4);
#     }
    
#     /* Input field styles */
#     .stTextInput>div>div>input,
#     .stTextArea>div>div>textarea,
#     .stSelectbox>div>select {
#         background: rgba(40, 40, 40, 0.8) !important;
#         color: white !important;
#         border: 1px solid rgba(255, 255, 255, 0.1) !important;
#         border-radius: 8px !important;
#     }
    
#     /* Profile summary card */
#     .profile-card {
#         background: rgba(30, 30, 30, 0.8);
#         border-radius: 12px;
#         padding: 15px;
#         margin-bottom: 20px;
#         border-left: 4px solid #e52e71;
#     }
    
#     /* Tooltip styles */
#     .tooltip {
#         position: relative;
#         display: inline-block;
#     }
    
#     .tooltip .tooltiptext {
#         visibility: hidden;
#         width: 200px;
#         background-color: #333;
#         color: #fff;
#         text-align: center;
#         border-radius: 6px;
#         padding: 5px;
#         position: absolute;
#         z-index: 1;
#         bottom: 125%;
#         left: 50%;
#         margin-left: -100px;
#         opacity: 0;
#         transition: opacity 0.3s;
#     }
    
#     .tooltip:hover .tooltiptext {
#         visibility: visible;
#         opacity: 1;
#     }
    
#     /* Responsive adjustments */
#     @media (max-width: 768px) {
#         .netflix-card {
#             flex-direction: column;
#         }
        
#         .card-poster {
#             width: 100%;
#             height: auto;
#             max-height: 300px;
#         }
#     }
#     </style>
#     """
#     st.markdown(css, unsafe_allow_html=True)

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
# def inject_global_css():
#     """Inject all CSS styles for the application pages"""
#     css = """
#     <style>
#     @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
#     /* Main layout styles */
#     .stApp {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         font-family: 'Inter', sans-serif;
#     }
    
#     .main .block-container {
#         background: rgba(255, 255, 255, 0.05);
#         backdrop-filter: blur(20px);
#         border-radius: 20px;
#         border: 1px solid rgba(255, 255, 255, 0.1);
#         box-shadow: 0 25px 45px rgba(0, 0, 0, 0.2);
#         margin-top: 1rem;
#         padding: 2rem;
#     }
    
#     /* Header styles */
#     .header {
#         font-size: 2.8rem;
#         font-weight: 800;
#         background: linear-gradient(135deg, #ff6b6b, #4ecdc4, #45b7d1);
#         background-size: 200% 200%;
#         animation: gradientShift 3s ease infinite;
#         -webkit-background-clip: text;
#         background-clip: text;
#         color: transparent;
#         margin-bottom: 2rem;
#         text-align: center;
#         letter-spacing: -1px;
#     }
    
#     @keyframes gradientShift {
#         0% { background-position: 0% 50%; }
#         50% { background-position: 100% 50%; }
#         100% { background-position: 0% 50%; }
#     }
    
#     /* Movie Card styles */
#     .netflix-card {
#         display: flex;
#         gap: 20px;
#         background: rgba(255, 255, 255, 0.1);
#         backdrop-filter: blur(15px);
#         border-radius: 20px;
#         padding: 20px;
#         margin-bottom: 20px;
#         transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
#         border: 2px solid rgba(255, 255, 255, 0.1);
#         position: relative;
#         overflow: hidden;
#     }
    
#     .netflix-card::before {
#         content: '';
#         position: absolute;
#         top: 0;
#         left: -100%;
#         width: 100%;
#         height: 100%;
#         background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
#         transition: left 0.5s;
#     }
    
#     .netflix-card:hover::before {
#         left: 100%;
#     }
    
#     .netflix-card:hover {
#         transform: translateY(-8px) scale(1.02);
#         box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
#         background: rgba(255, 255, 255, 0.15);
#         border-color: rgba(78, 205, 196, 0.5);
#     }
    
#     .card-poster {
#         width: 140px;
#         height: 210px;
#         object-fit: cover;
#         border-radius: 12px;
#         box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
#         transition: all 0.3s ease;
#         flex-shrink: 0;
#     }
    
#     .netflix-card:hover .card-poster {
#         box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
#         transform: scale(1.05);
#     }
    
#     .card-content {
#         flex: 1;
#         color: #ffffff;
#         display: flex;
#         flex-direction: column;
#         justify-content: space-between;
#     }
    
#     .card-title {
#         font-size: 1.5rem;
#         font-weight: 700;
#         margin-bottom: 0.8rem;
#         color: #ffffff;
#         line-height: 1.3;
#     }
    
#     .card-meta {
#         font-size: 0.9rem;
#         margin-bottom: 1rem;
#         display: flex;
#         flex-wrap: wrap;
#         gap: 10px;
#         align-items: center;
#     }
    
#     .rating-badge {
#         background: linear-gradient(135deg, #2ecc71, #27ae60);
#         padding: 6px 12px;
#         border-radius: 20px;
#         color: #fff;
#         font-weight: 700;
#         font-size: 0.85rem;
#         box-shadow: 0 3px 10px rgba(46, 204, 113, 0.3);
#     }
    
#     .meta-badge {
#         background: rgba(255, 255, 255, 0.2);
#         backdrop-filter: blur(10px);
#         padding: 6px 12px;
#         border-radius: 20px;
#         color: #ffffff;
#         font-size: 0.85rem;
#         font-weight: 500;
#         border: 1px solid rgba(255, 255, 255, 0.1);
#     }
    
#     .imdb-badge {
#         background: linear-gradient(135deg, #f5c518, #d4af37);
#         padding: 6px 12px;
#         border-radius: 20px;
#         color: #000000;
#         font-weight: 700;
#         font-size: 0.85rem;
#         box-shadow: 0 3px 10px rgba(245, 197, 24, 0.3);
#     }
    
#     .enhanced-description {
#         font-size: 1rem;
#         line-height: 1.6;
#         margin-top: 0.8rem;
#         flex-grow: 1;
#     }
    
#     .enhanced-description p {
#         margin: 0;
#         color: rgba(255, 255, 255, 0.85);
#     }
    
#     /* Section headers */
#     .section-header {
#         font-size: 2rem;
#         font-weight: 700;
#         margin: 30px 0 20px 0;
#         color: #ffffff;
#         position: relative;
#         padding-bottom: 12px;
#         text-align: center;
#     }
    
#     .section-header:after {
#         content: '';
#         position: absolute;
#         bottom: 0;
#         left: 50%;
#         transform: translateX(-50%);
#         width: 80px;
#         height: 4px;
#         background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
#         border-radius: 4px;
#     }
    
#     /* Form styles */
#     .stForm {
#         background: rgba(255, 255, 255, 0.08);
#         backdrop-filter: blur(15px);
#         border-radius: 16px;
#         padding: 25px;
#         margin-bottom: 30px;
#         border: 2px solid rgba(255, 255, 255, 0.1);
#         box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
#     }
    
#     /* Button styles */
#     .stButton>button {
#         background: linear-gradient(135deg, #667eea, #764ba2) !important;
#         color: white !important;
#         border: none !important;
#         border-radius: 12px !important;
#         padding: 12px 24px !important;
#         font-weight: 600 !important;
#         font-size: 1rem !important;
#         transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
#         box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
#         width: 100% !important;
#         margin: 0.5rem 0 !important;
#     }
    
#     .stButton>button:hover {
#         transform: translateY(-2px) !important;
#         box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5) !important;
#         background: linear-gradient(135deg, #5a6fd8, #6b5b95) !important;
#     }
    
#     .stButton>button:active {
#         transform: translateY(0) !important;
#     }
    
#     /* Input field styles */
#     .stTextInput>div>div>input,
#     .stTextArea>div>div>textarea,
#     .stSelectbox>div>div>select,
#     .stMultiSelect>div>div>div {
#         background: rgba(255, 255, 255, 0.1) !important;
#         color: white !important;
#         border: 2px solid rgba(255, 255, 255, 0.1) !important;
#         border-radius: 12px !important;
#         font-size: 1rem !important;
#         padding: 12px !important;
#         transition: all 0.3s ease !important;
#     }
    
#     .stTextInput>div>div>input:focus,
#     .stTextArea>div>div>textarea:focus,
#     .stSelectbox>div>div>select:focus {
#         border-color: #4ecdc4 !important;
#         box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.1) !important;
#         background: rgba(255, 255, 255, 0.15) !important;
#     }
    
#     /* Profile summary card */
#     .profile-card {
#         background: rgba(255, 255, 255, 0.1);
#         backdrop-filter: blur(15px);
#         border-radius: 16px;
#         padding: 20px;
#         margin-bottom: 25px;
#         border: 2px solid rgba(78, 205, 196, 0.3);
#         box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
#     }
    
#     .profile-card h3 {
#         color: #ffffff;
#         margin-bottom: 1rem;
#         font-weight: 600;
#     }
    
#     .profile-card p {
#         color: rgba(255, 255, 255, 0.8);
#         line-height: 1.5;
#     }
    
#     /* Loading and status indicators */
#     .stSpinner {
#         text-align: center;
#         padding: 2rem;
#     }
    
#     .stSuccess {
#         background: rgba(46, 204, 113, 0.1) !important;
#         border: 1px solid rgba(46, 204, 113, 0.3) !important;
#         color: #2ecc71 !important;
#         border-radius: 12px !important;
#         backdrop-filter: blur(10px) !important;
#     }
    
#     .stError {
#         background: rgba(231, 76, 60, 0.1) !important;
#         border: 1px solid rgba(231, 76, 60, 0.3) !important;
#         color: #e74c3c !important;
#         border-radius: 12px !important;
#         backdrop-filter: blur(10px) !important;
#     }
    
#     .stWarning {
#         background: rgba(241, 196, 15, 0.1) !important;
#         border: 1px solid rgba(241, 196, 15, 0.3) !important;
#         color: #f1c40f !important;
#         border-radius: 12px !important;
#         backdrop-filter: blur(10px) !important;
#     }
    
#     .stInfo {
#         background: rgba(52, 152, 219, 0.1) !important;
#         border: 1px solid rgba(52, 152, 219, 0.3) !important;
#         color: #3498db !important;
#         border-radius: 12px !important;
#         backdrop-filter: blur(10px) !important;
#     }
    
#     /* Sidebar styling */
#     .css-1d391kg {
#         background: rgba(255, 255, 255, 0.05) !important;
#         backdrop-filter: blur(20px) !important;
#     }
    
#     /* Tooltip styles */
#     .tooltip {
#         position: relative;
#         display: inline-block;
#         cursor: help;
#     }
    
#     .tooltip .tooltiptext {
#         visibility: hidden;
#         width: 220px;
#         background: rgba(0, 0, 0, 0.9);
#         backdrop-filter: blur(10px);
#         color: #fff;
#         text-align: center;
#         border-radius: 8px;
#         padding: 8px;
#         position: absolute;
#         z-index: 1000;
#         bottom: 125%;
#         left: 50%;
#         margin-left: -110px;
#         opacity: 0;
#         transition: opacity 0.3s ease;
#         font-size: 0.85rem;
#         border: 1px solid rgba(255, 255, 255, 0.1);
#     }
    
#     .tooltip:hover .tooltiptext {
#         visibility: visible;
#         opacity: 1;
#     }
    
#     /* Search and filter components */
#     .stExpander {
#         background: rgba(255, 255, 255, 0.05) !important;
#         border: 1px solid rgba(255, 255, 255, 0.1) !important;
#         border-radius: 16px !important;
#         margin: 1rem 0 !important;
#         backdrop-filter: blur(10px) !important;
#     }
    
#     .stExpander > div:first-child {
#         background: transparent !important;
#         color: white !important;
#         font-weight: 600 !important;
#         font-size: 1.1rem !important;
#     }
    
#     /* Responsive adjustments */
#     @media (max-width: 768px) {
#         .netflix-card {
#             flex-direction: column;
#             text-align: center;
#         }
        
#         .card-poster {
#             width: 100%;
#             height: auto;
#             max-height: 350px;
#             margin: 0 auto 1rem;
#         }
        
#         .card-meta {
#             justify-content: center;
#         }
        
#         .main .block-container {
#             padding: 1rem;
#             margin-top: 0.5rem;
#         }
        
#         .header {
#             font-size: 2rem;
#         }
        
#         .section-header {
#             font-size: 1.5rem;
#         }
#     }
    
#     /* Custom scrollbar */
#     ::-webkit-scrollbar {
#         width: 8px;
#     }
    
#     ::-webkit-scrollbar-track {
#         background: rgba(255, 255, 255, 0.1);
#         border-radius: 4px;
#     }
    
#     ::-webkit-scrollbar-thumb {
#         background: linear-gradient(135deg, #667eea, #764ba2);
#         border-radius: 4px;
#     }
    
#     ::-webkit-scrollbar-thumb:hover {
#         background: linear-gradient(135deg, #5a6fd8, #6b5b95);
#     }
    
#     /* Animation for cards */
#     @keyframes fadeInUp {
#         from {
#             opacity: 0;
#             transform: translateY(30px);
#         }
#         to {
#             opacity: 1;
#             transform: translateY(0);
#         }
#     }
    
#     .netflix-card {
#         animation: fadeInUp 0.6s ease-out forwards;
#     }
    
#     /* Improved text readability */
#     h1, h2, h3, h4, h5, h6 {
#         color: #ffffff !important;
#     }
    
#     p, span, div {
#         color: rgba(255, 255, 255, 0.9) !important;
#     }
    
#     /* Genre tags and labels */
#     .genre-tag {
#         background: linear-gradient(135deg, #667eea, #764ba2);
#         color: white;
#         padding: 4px 12px;
#         border-radius: 15px;
#         font-size: 0.8rem;
#         font-weight: 500;
#         margin: 2px;
#         display: inline-block;
#         box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
#     }
    
#     /* Progress bars and sliders */
#     .stProgress > div > div {
#         background: linear-gradient(90deg, #667eea, #764ba2) !important;
#     }
    
#     .stSlider > div > div > div {
#         background: #667eea !important;
#     }
#     </style>
#     """
#     st.markdown(css, unsafe_allow_html=True)
    

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
