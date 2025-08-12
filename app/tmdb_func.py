# import streamlit as st
# import os
# import re
# import json
# import time
# import asyncio
# from datetime import datetime
# from concurrent.futures import ThreadPoolExecutor
# from dotenv import load_dotenv
# import requests

# # Make sure you import your LLM and PromptTemplate classes here:
# from your_llm_lib import ChatGroq, PromptTemplate, StrOutputParser

# # Load environment variables
# load_dotenv("/Users/ssris/Desktop/RIMSAB/LANG/.env")

# # Initialize session state defaults
# session_state_defaults = {
#     'recommendations': [],
#     'user_profile': {},
#     'show_all': False,
#     'enhanced_movies': {},
#     'log_messages': []
# }
# for key, default in session_state_defaults.items():
#     if key not in st.session_state:
#         st.session_state[key] = default

# def log_message(message):
#     """Add timestamped message to logs, keep last 20."""
#     timestamp = datetime.now().strftime("%H:%M:%S")
#     full_message = f"[{timestamp}] {message}"
#     st.session_state.log_messages.append(full_message)
#     if len(st.session_state.log_messages) > 20:
#         st.session_state.log_messages = st.session_state.log_messages[-20:]

# GENRE_MAP_LOCAL = {
#     "action": 28, "adventure": 12, "animation": 16, "comedy": 35, "crime": 80,
#     "documentary": 99, "drama": 18, "family": 10751, "fantasy": 14, "history": 36,
#     "horror": 27, "music": 10402, "mystery": 9648, "romance": 10749,
#     "science fiction": 878, "tv movie": 10770, "thriller": 53, "war": 10752, "western": 37
# }

# def map_genres_to_ids(genres_list):
#     ids = [str(GENRE_MAP_LOCAL.get(g.strip().lower())) for g in genres_list if GENRE_MAP_LOCAL.get(g.strip().lower())]
#     return "|".join(ids)

# def extract_json_from_text(text):
#     match = re.search(r"\{[\s\S]*\}", text)
#     if match:
#         try:
#             return json.loads(match.group())
#         except json.JSONDecodeError:
#             return None
#     return None

# @st.cache_resource
# def initialize_llm():
#     try:
#         log_message("Initializing LLM connection...")
#         llm = ChatGroq(
#             api_key=os.getenv("GROQ_API_KEY"),
#             model_name="llama3-8b-8192",
#             temperature=0.3
#         )
#         log_message("LLM connection established successfully")
#         return llm
#     except Exception as e:
#         log_message(f"⚠️ LLM initialization failed: {str(e)}")
#         return None

# def extract_english_title(text):
#     match = re.search(r"English title:\s*(.*)", text, re.IGNORECASE)
#     return match.group(1).strip() if match else None

# def enhance_movie_info(movie):
#     llm = initialize_llm()
#     if not llm:
#         log_message("⚠️ Cannot enhance movie info - LLM not available")
#         return None

#     title = movie.get("title", "")
#     overview = movie.get("overview", "")

#     prompt = PromptTemplate(
#         template="""
#         Translate and enhance the following movie details into natural English.

#         Title: {title}
#         Overview: {overview}

#         Respond in 2-3 lines: English title (if appropriate), a brief and appealing description.
#         """,
#         input_variables=["title", "overview"]
#     )

#     try:
#         log_message(f"Enhancing movie info for: {title}")
#         chain = prompt | llm | StrOutputParser()
#         enhanced_description = chain.invoke({"title": title, "overview": overview}).strip()
#         return {"enhanced": enhanced_description}
#     except Exception as e:
#         log_message(f"⚠️ Error enhancing movie {title}: {str(e)}")
#         return None

# def discover_movies(params, max_retries=3):
#     if not params or not params.get("api_key"):
#         log_message("⚠️ Invalid API parameters for TMDb request")
#         return []

#     for attempt in range(max_retries):
#         try:
#             log_message(f"Fetching movies from TMDb (Attempt {attempt+1})...")
#             response = requests.get("https://api.themoviedb.org/3/discover/movie", params=params, timeout=10)
#             if response.status_code == 200:
#                 data = response.json()
#                 results = data.get("results", [])
#                 movies = []
#                 for movie in results[:10]:
#                     movies.append({
#                         "title": movie.get("title"),
#                         "overview": movie.get("overview"),
#                         "release_date": movie.get("release_date"),
#                         "vote_average": movie.get("vote_average"),
#                         "original_language": movie.get("original_language"),
#                         "genre_ids": movie.get("genre_ids"),
#                         "poster_url": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get("poster_path") else None
#                     })
#                 log_message(f"Successfully fetched {len(movies)} movies")
#                 return movies
#             elif response.status_code == 429:
#                 retry_after = int(response.headers.get('Retry-After', 5))
#                 log_message(f"Rate limit hit. Retrying after {retry_after}s...")
#                 time.sleep(retry_after)
#                 continue
#             else:
#                 log_message(f"Unexpected status {response.status_code}")
#                 if attempt < max_retries - 1:
#                     time.sleep(2)
#                     continue
#                 return []
#         except requests.exceptions.RequestException as e:
#             log_message(f"Connection error (attempt {attempt+1}): {str(e)}")
#             if attempt < max_retries - 1:
#                 time.sleep(2)
#                 continue
#             return []
#     log_message("Failed to fetch movies after retries")
#     return []

# def generate_recommendations(user_profile):
#     llm = initialize_llm()
#     if not llm:
#         st.error("⚠️ LLM not available. Check API keys.")
#         log_message("⚠️ Cannot generate recommendations - LLM not available")
#         return None

#     profile_prompt = PromptTemplate(
#         template="""
#         Given the user preferences, generate a Python dict named 'params' for TMDb Discover API.

#         Rules:
#         - Include 'api_key' as 'DUMMY_KEY'.
#         - Format 'language' as '{language}-IN'.
#         - Sort by popularity.desc
#         - Include_adult and include_video false.
#         - Page 1.
#         - with_genres pipe-separated genre IDs.
#         - with_original_language based on language.
#         - region is 2-letter ISO country code.

#         Respond ONLY with the Python dict.

#         User Preferences:
#         Genres: {genres}
#         Language: {language}
#         Country: {country}
#         Genre IDs: {genre_ids}
#         """,
#         input_variables=["genres", "language", "country", "genre_ids"]
#     )

#     genre_ids = map_genres_to_ids(user_profile.get("genres", []))
#     language = user_profile.get("languages", ["en"])[0].lower()
#     country = user_profile.get("country", "IN").upper()

#     try:
#         log_message("Generating API parameters via LLM...")
#         raw_response = (profile_prompt | llm | StrOutputParser()).invoke({
#             "genres": user_profile.get("genres", []),
#             "language": language,
#             "country": country,
#             "genre_ids": genre_ids
#         })
#         minimal_profile = extract_json_from_text(raw_response)
#         if minimal_profile:
#             minimal_profile["api_key"] = os.getenv("TMDB_API_KEY")
#             log_message("API params generated")
#             return minimal_profile
#         else:
#             log_message("⚠️ Failed to parse LLM response")
#             return None
#     except Exception as e:
#         log_message(f"⚠️ Error generating recommendations: {str(e)}")
#         st.error(f"Error: {str(e)}")
#         return None

# async def batch_enhance(movies):
#     log_message(f"Batch enhancing {len(movies)} movies...")
#     loop = asyncio.get_event_loop()
#     with ThreadPoolExecutor() as executor:
#         futures = [loop.run_in_executor(executor, enhance_movie_info, movie) for movie in movies]
#         results = await asyncio.gather(*futures)
#     log_message("Batch enhancement done")
#     return results

# def display_movie_card(movie, index):
#     poster_html = (
#         f'<img src="{movie["poster_url"]}" alt="Poster" class="card-poster" />'
#         if movie.get("poster_url") else
#         '<div class="card-poster" style="background: #333; display:flex; align-items:center; justify-content:center; color:#666;">No Poster</div>'
#     )
#     enhanced_info = st.session_state.enhanced_movies.get(index, {})
#     enhanced_text = enhanced_info.get("enhanced", movie.get("overview", "No description available."))

#     rating_color = "rating-badge" if movie.get("vote_average", 0) >= 7.0 else "meta-badge"

#     card_html = f"""
#     <div class="netflix-card">
#         {poster_html}
#         <div class="card-content">
#             <div class="card-title">{movie.get('title', 'N/A')}</div>
#             <div class="card-meta">
#                 <span class="{rating_color}">⭐ {movie.get('vote_average', 'N/A')}/10</span>
#                 <span class="meta-badge">📅 {movie.get('release_date', 'N/A')[:4]}</span>
#                 <span class="meta-badge">🗣 {movie.get('original_language', 'N/A').upper()}</span>
#             </div>
#             <div class="enhanced-description">
#                 <p><strong>🤖 Enhanced:</strong> {enhanced_text}</p>
#             </div>
#         </div>
#     </div>
#     """
#     return card_html

# # --- STREAMLIT PAGE CODE BELOW ---
# # def app_2():
# #     st.title("🎬 Movie Recommendations & Enhancement")

# #     with st.form("user_profile_form"):
# #         genres = st.text_input("Enter genres (comma-separated)", placeholder="e.g. Action, Comedy, Drama")
# #         languages = st.text_input("Preferred languages (comma-separated)", placeholder="e.g. en, hi")
# #         country = st.text_input("Country code (ISO 2-letter)", placeholder="e.g. IN")
# #         submitted = st.form_submit_button("Get Recommendations")

# #     if submitted:
# #         user_profile = {
# #             "genres": [g.strip() for g in genres.split(",") if g.strip()],
# #             "languages": [l.strip() for l in languages.split(",") if l.strip()],
# #             "country": country.strip().upper() if country.strip() else "IN"
# #         }
# #         st.session_state.user_profile = user_profile

# #         params = generate_recommendations(user_profile)
# #         if params:
# #             movies = discover_movies(params)
# #             st.session_state.recommendations = movies
# #             st.session_state.enhanced_movies = {}
# #             st.experimental_rerun()

# #     if st.session_state.recommendations:
# #         st.subheader("Movie Recommendations")
# #         for idx, movie in enumerate(st.session_state.recommendations):
# #             card_html = display_movie_card(movie, idx)
# #             st.markdown(card_html, unsafe_allow_html=True)

# #         if st.button("Enhance All Movies"):
# #             # Async run batch enhance and update session state
# #             enhanced_results = asyncio.run(batch_enhance(st.session_state.recommendations))
# #             # Filter out None results
# #             enhanced_dict = {i: r for i, r in enumerate(enhanced_results) if r}
# #             st.session_state.enhanced_movies = enhanced_dict
# #             st.experimental_rerun()

# #     # Show log messages
# #     if st.session_state.log_messages:
# #         with st.expander("📝 Logs", expanded=False):
# #             for log in st.session_state.log_messages:
# #                 st.text(log)

# def show_recommendations_mode():
#     """TMDb-based AI recommendations with user profiling - no sidebar, main page layout"""

#     st.markdown('<div class="section-header">👤 Your Movie Profile & AI Recommendations</div>', unsafe_allow_html=True)

#     # User Profile Form Section
#     with st.form("user_profile_form", clear_on_submit=False):
#         st.markdown("### 🎭 Tell us about yourself")

#         col1, col2 = st.columns(2)

#         with col1:
#             name = st.text_input("What's your name?", placeholder="Enter your name", key="name_input")
#             mood = st.selectbox(
#                 "How are you feeling today?",
#                 ["Happy", "Sad", "Excited", "Relaxed", "Adventurous", "Romantic", "Thrilled", "Nostalgic"],
#                 key="mood_select"
#             )
#             genres = st.multiselect(
#                 "Select your favorite genres:",
#                 list(GENRE_MAP_LOCAL.keys()),
#                 key="genre_select"
#             )
#             languages = st.multiselect(
#                 "What languages do you prefer?",
#                 ["English", "Hindi", "Tamil", "Telugu", "Malayalam", "Kannada", "Bengali", "Marathi"],
#                 default=["English"],
#                 key="language_select"
#             )

#         with col2:
#             actors = st.text_area(
#                 "List your favorite actors (comma-separated):",
#                 placeholder="e.g., Shah Rukh Khan, Deepika Padukone, Tom Hanks",
#                 key="actors_input"
#             )
#             favorites = st.text_area(
#                 "List some of your favorite movies (comma-separated):",
#                 placeholder="e.g., Inception, 3 Idiots, The Shawshank Redemption",
#                 key="favorites_input"
#             )
#             country = st.selectbox(
#                 "Country:",
#                 ["India", "United States", "United Kingdom", "Canada", "Australia"],
#                 key="country_select"
#             )

#         submitted = st.form_submit_button("🚀 Get AI-Powered Recommendations", type="primary")

#     if submitted:
#         if not name:
#             st.warning("Please enter your name to get personalized recommendations!")
#         elif not genres:
#             st.warning("Please select at least one genre!")
#         else:
#             user_profile = {
#                 "name": name,
#                 "mood": mood,
#                 "genres": genres,
#                 "actors": [actor.strip() for actor in actors.split(",")] if actors else [],
#                 "languages": [lang.lower()[:2] for lang in languages],
#                 "favorites": [movie.strip() for movie in favorites.split(",")] if favorites else [],
#                 "country": country[:3].upper()
#             }

#             st.session_state.user_profile = user_profile
#             st.session_state.show_all = False
#             st.session_state.enhanced_movies = {}

#             with st.spinner("🎬 AI is finding your perfect movies..."):
#                 params = generate_recommendations(user_profile)
                
#                 if params:
#                     movies = discover_movies(params)
#                     st.session_state.recommendations = movies

#                     if movies:
#                         st.success(f"🎉 Found {len(movies)} amazing movies for you!")
                        
#                         # Enhance first 5 movies
#                         enhanced_batch = asyncio.run(batch_enhance(movies[:5], "tmdb"))
#                         for i, enhanced in enumerate(enhanced_batch):
#                             if enhanced:
#                                 st.session_state.enhanced_movies[i] = enhanced
#                     else:
#                         st.warning("No movies found. Try different genres!")
#                 else:
#                     st.error("Unable to generate recommendations. Check API keys.")

#     # Display recommendations below form
#     if st.session_state.get("recommendations"):
#         st.markdown('<div class="section-header">🍿 Your AI-Curated Movies</div>', unsafe_allow_html=True)
        
#         movies_to_show = st.session_state.recommendations[:5] if not st.session_state.show_all else st.session_state.recommendations

#         for i, movie in enumerate(movies_to_show):
#             card_html = display_movie_card_universal(movie, i)
#             st.markdown(card_html, unsafe_allow_html=True)

#         if not st.session_state.show_all and len(st.session_state.recommendations) > 5:
#             if st.button("🔥 Load More Recommendations", key="load_more"):
#                 st.session_state.show_all = True
#                 # Enhance remaining movies
#                 for i, movie in enumerate(st.session_state.recommendations[5:], 5):
#                     if i not in st.session_state.enhanced_movies:
#                         enhanced = enhance_movie_info_unified(movie, "tmdb")
#                         if enhanced:
#                             st.session_state.enhanced_movies[i] = enhanced
#                 st.experimental_rerun()

#     # Show user profile summary and AI tips on right side if desired
#     col_left, col_right = st.columns([3, 1])
#     with col_right:
#         if st.session_state.get("user_profile"):
#             profile = st.session_state.user_profile
#             st.markdown("### 📊 Your Profile Summary")
#             st.markdown(f"""
#             **Name:** {profile.get('name', 'Not set')}  
#             **Mood:** {profile.get('mood', 'Not set')}  
#             **Genres:** {', '.join(profile.get('genres', []))}  
#             **Languages:** {', '.join(profile.get('languages', []))}
#             """)

#         st.markdown("### 💡 AI Tips")
#         st.info("🎯 Be specific with your preferences\n🎭 Mood influences recommendations")

# def display_movie_card_universal(movie, index=None):
#     """Universal movie card display for both TMDb and OMDb"""
#     source = movie.get("source", "tmdb")
    
#     if source == "tmdb":
#         # TMDb movie structure
#         title = movie.get("title", "Unknown Title")
#         year = movie.get("release_date", "")[:4] if movie.get("release_date") else "N/A"
#         rating = movie.get("vote_average", "N/A")
#         language = movie.get("original_language", "N/A").upper()
#         poster_url = movie.get("poster_url")
#         overview = movie.get("overview", "No description available.")
        
#         # Enhanced description from session state
#         enhanced_info = st.session_state.enhanced_movies.get(index, {}) if index is not None else {}
#         enhanced_text = enhanced_info.get("enhanced", overview)
        
#         rating_badge_class = "rating-badge" if isinstance(rating, (int, float)) and rating >= 7.0 else "meta-badge"
#         rating_display = f"⭐ {rating}/10"
        
#     else:
#         # OMDb movie structure
#         title = movie.get("Title", "Unknown Title")
#         year = movie.get("Year", "N/A")
#         rating = movie.get("imdbRating", "N/A")
#         language = movie.get("Language", "N/A").split(",")[0].strip()
#         poster_url = movie.get("Poster") if movie.get("Poster") != "N/A" else None
#         overview = movie.get("Plot", "No description available.")
        
#         # Enhanced description
#         enhanced_info = st.session_state.enhanced_movies.get(f"omdb_{movie.get('imdbID', index)}", {})
#         enhanced_text = enhanced_info.get("enhanced", overview)
        
#         rating_badge_class = "imdb-badge"
#         rating_display = f"⭐ {rating}/10"

#     # Generate poster HTML
#     if poster_url:
#         poster_html = f'<img src="{poster_url}" alt="Poster" class="card-poster" />'
#     else:
#         poster_html = '<div class="card-poster" style="background: #333; display:flex; align-items:center; justify-content:center; color:#666;">No Poster</div>'

#     # Generate card HTML
#     card_html = f"""
#     <div class="netflix-card">
#         {poster_html}
#         <div class="card-content">
#             <div class="card-title">{title}</div>
#             <div class="card-meta">
#                 <span class="{rating_badge_class}">{rating_display}</span>
#                 <span class="meta-badge">📅 {year}</span>
#                 <span class="meta-badge">🗣 {language}</span>
#                 <span class="meta-badge">📡 {source.upper()}</span>
#             </div>
#             <div class="enhanced-description">
#                 <p><strong>🤖 Enhanced:</strong> {enhanced_text}</p>
#             </div>
#         </div>
#     </div>
#     """
#     return card_html



# import streamlit as st
# import os
# import re
# import json
# import time
# import asyncio
# from datetime import datetime
# from concurrent.futures import ThreadPoolExecutor
# from dotenv import load_dotenv
# import requests


# # Standard Library Impoimport os
# import re
# import json
# import time
# import os 
# import asyncio
# from datetime import datetime
# from concurrent.futures import ThreadPoolExecutor
# from io import BytesIO

# # Third-Party Imports
# import requests
# import streamlit as st
# from PIL import Image
# from dotenv import load_dotenv

# # LangChain Core Imports
# from langchain_core.prompts import PromptTemplate
# from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
# from langchain_core.tools import Tool

# # LangChain Community Imports
# from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
# from langchain_community.utilities import WikipediaAPIWrapper

# # LangChain Agents (if needed)
# from langchain.agents import initialize_agent, AgentType

# # Groq Imports
# from langchain_groq import ChatGroq
# async def batch_enhance(movies):
#     tasks = [enhance_movie_info(movie) for movie in movies]
#     return await asyncio.gather(*tasks)

# def inject_global_css():
#     css = """
#     <style>
#     .netflix-card {
#         display: flex;
#         gap: 15px;
#         background: #222;
#         border-radius: 8px;
#         padding: 10px;
#         margin-bottom: 10px;
#     }
#     .card-poster {
#         width: 100px;
#         height: 150px;
#         object-fit: cover;
#         border-radius: 5px;
#     }
#     .card-content {
#         flex: 1;
#         color: #eee;
#     }
#     .card-title {
#         font-size: 20px;
#         font-weight: bold;
#         margin-bottom: 6px;
#     }
#     .card-meta {
#         font-size: 12px;
#         margin-bottom: 8px;
#         display: flex;
#         gap: 10px;
#     }
#     .rating-badge {
#         background: #2ecc71;
#         padding: 2px 6px;
#         border-radius: 4px;
#         color: #fff;
#     }
#     .meta-badge {
#         background: #555;
#         padding: 2px 6px;
#         border-radius: 4px;
#         color: #ddd;
#     }
#     .imdb-badge {
#         background: #f5c518;
#         padding: 2px 6px;
#         border-radius: 4px;
#         color: #000;
#     }
#     .enhanced-description p {
#         margin: 0;
#         font-style: italic;
#         color: #ccc;
#     }
#     .section-header {
#         font-size: 26px;
#         font-weight: bold;
#         margin: 20px 0 10px 0;
#         color: #ffa500;
#     }
#     </style>
#     """
#     st.markdown(css, unsafe_allow_html=True)


# # Load environment variables
# load_dotenv("/Users/ssris/Desktop/RIMSAB/LANG/.env")

# # Initialize session state defaults
# session_state_defaults = {
#     'recommendations': [],
#     'user_profile': {},
#     'show_all': False,
#     'enhanced_movies': {},
#     'log_messages': []
# }
# for key, default in session_state_defaults.items():
#     if key not in st.session_state:
#         st.session_state[key] = default

# def log_message(message):
#     """Add timestamped message to logs, keep last 20."""
#     if "log_messages" not in st.session_state:
#         st.session_state.log_messages = []
#     timestamp = datetime.now().strftime("%H:%M:%S")
#     full_message = f"[{timestamp}] {message}"
#     st.session_state.log_messages.append(full_message)
#     if len(st.session_state.log_messages) > 20:
#         st.session_state.log_messages = st.session_state.log_messages[-20:]


# GENRE_MAP_LOCAL = {
#     "action": 28, "adventure": 12, "animation": 16, "comedy": 35, "crime": 80,
#     "documentary": 99, "drama": 18, "family": 10751, "fantasy": 14, "history": 36,
#     "horror": 27, "music": 10402, "mystery": 9648, "romance": 10749,
#     "science fiction": 878, "tv movie": 10770, "thriller": 53, "war": 10752, "western": 37
# }

# def map_genres_to_ids(genres_list):
#     ids = [str(GENRE_MAP_LOCAL.get(g.strip().lower())) for g in genres_list if GENRE_MAP_LOCAL.get(g.strip().lower())]
#     return "|".join(ids)

# def extract_json_from_text(text):
#     match = re.search(r"\{[\s\S]*\}", text)
#     if match:
#         json_text = match.group()
#         # Replace single quotes with double quotes (not perfect but helps)
#         json_text = json_text.replace("'", '"')
#         try:
#             return json.loads(json_text)
#         except json.JSONDecodeError:
#             return None
#     return None

# @st.cache_resource
# def initialize_llm():
#     try:
#         log_message("Initializing LLM connection...")
#         llm = ChatGroq(
#             api_key=os.getenv("GROQ_API_KEY"),
#             model_name="llama3-8b-8192",
#             temperature=0.3
#         )
#         log_message("LLM connection established successfully")
#         return llm
#     except Exception as e:
#         log_message(f"⚠️ LLM initialization failed: {str(e)}")
#         return None

# def enhance_movie_info(movie):
#     llm = initialize_llm()
#     if not llm:
#         log_message("⚠️ Cannot enhance movie info - LLM not available")
#         return None

#     title = movie.get("title", "")
#     overview = movie.get("overview", "")

#     prompt = PromptTemplate(
#         template="""
# Translate and enhance the following movie details into natural English.

# Title: {title}
# Overview: {overview}

# Respond in 2-3 lines: English title (if appropriate), a brief and appealing description.
# """,
#         input_variables=["title", "overview"]
#     )

#     try:
#         log_message(f"Enhancing movie info for: {title}")
#         chain = prompt | llm | StrOutputParser()
#         enhanced_description = chain.invoke({"title": title, "overview": overview}).strip()
#         return {"enhanced": enhanced_description}
#     except Exception as e:
#         log_message(f"⚠️ Error enhancing movie {title}: {str(e)}")
#         return None

# def enhance_movie_info_unified(movie, source="tmdb"):
#     # For TMDb or OMDb unified enhancement
#     llm = initialize_llm()
#     if not llm:
#         log_message("⚠️ Cannot enhance movie info - LLM not available")
#         return None

#     if source == "tmdb":
#         title = movie.get("title", "")
#         overview = movie.get("overview", "")
#     else:
#         title = movie.get("Title", "")
#         overview = movie.get("Plot", "")

#     prompt = PromptTemplate(
#         template="""
# Translate and enhance the following movie details into natural English.

# Title: {title}
# Overview: {overview}

# Respond in 2-3 lines: English title (if appropriate), a brief and appealing description.
# """,
#         input_variables=["title", "overview"]
#     )

#     try:
#         log_message(f"Enhancing movie info for: {title}")
#         chain = prompt | llm | StrOutputParser()
#         enhanced_description = chain.invoke({"title": title, "overview": overview}).strip()
#         return {"enhanced": enhanced_description}
#     except Exception as e:
#         log_message(f"⚠️ Error enhancing movie {title}: {str(e)}")
#         return None

# def discover_movies(params, max_retries=3):
#     if not params or not params.get("api_key"):
#         log_message("⚠️ Invalid API parameters for TMDb request")
#         return []

#     for attempt in range(max_retries):
#         try:
#             log_message(f"Fetching movies from TMDb (Attempt {attempt+1})...")
#             response = requests.get("https://api.themoviedb.org/3/discover/movie", params=params, timeout=10)
#             if response.status_code == 200:
#                 data = response.json()
#                 results = data.get("results", [])
#                 movies = []
#                 for movie in results[:10]:
#                     movie_data = {
#                         "title": movie.get("title"),
#                         "overview": movie.get("overview"),
#                         "release_date": movie.get("release_date"),
#                         "vote_average": movie.get("vote_average"),
#                         "original_language": movie.get("original_language"),
#                         "genre_ids": movie.get("genre_ids"),
#                         "poster_url": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get("poster_path") else None
#                     }
#                     movies.append(movie_data)
#                 log_message(f"Successfully fetched {len(movies)} movies")
#                 return movies
#             elif response.status_code == 429:
#                 retry_after = int(response.headers.get('Retry-After', 5))
#                 log_message(f"Rate limit hit. Retrying after {retry_after}s...")
#                 time.sleep(retry_after)
#                 continue
#             else:
#                 log_message(f"Unexpected status {response.status_code}")
#                 if attempt < max_retries - 1:
#                     time.sleep(2)
#                     continue
#                 return []
#         except requests.exceptions.RequestException as e:
#             log_message(f"Connection error (attempt {attempt+1}): {str(e)}")
#             if attempt < max_retries - 1:
#                 time.sleep(2)
#                 continue
#             return []
#     log_message("Failed to fetch movies after retries")
#     return []

# def generate_recommendations(user_profile):
#     llm = initialize_llm()
#     if not llm:
#         st.error("⚠️ LLM not available. Check API keys.")
#         log_message("⚠️ Cannot generate recommendations - LLM not available")
#         return None

#     profile_prompt = PromptTemplate(
#     template="""
# Given the user preferences, generate a JSON dictionary named 'params' for TMDb Discover API with the following rules:

# - Include 'api_key' as 'DUMMY_KEY'.
# - 'language' formatted as '{language}-IN'.
# - Sort by 'popularity.desc'
# - Include_adult and include_video false.
# - Page 1.
# - with_genres pipe-separated genre IDs.
# - with_original_language based on language.
# - region is 2-letter ISO country code.

# Respond ONLY with the JSON dictionary, no explanations, comments, or extra text.

# User Preferences:
# Genres: {genres}
# Language: {language}
# Country: {country}
# Genre IDs: {genre_ids}
# """,
#     input_variables=["genres", "language", "country", "genre_ids"]
# )


#     genre_ids = map_genres_to_ids(user_profile.get("genres", []))
#     language = user_profile.get("languages", ["en"])[0].lower()
#     country = user_profile.get("country", "IN").upper()[:2]

#     try:
#         log_message("Generating API parameters via LLM...")
#         raw_response = (profile_prompt | llm | StrOutputParser()).invoke({
#             "genres": user_profile.get("genres", []),
#             "language": language,
#             "country": country,
#             "genre_ids": genre_ids
#         })
#         minimal_profile = extract_json_from_text(raw_response)
#         if minimal_profile:
#             minimal_profile["api_key"] = os.getenv("TMDB_API_KEY")
#             log_message("API params generated")
#             return minimal_profile
#         else:
#             log_message("⚠️ Failed to parse LLM response")
#             return None
#     except Exception as e:
#         log_message(f"⚠️ Error generating recommendations: {str(e)}")
#         st.error(f"Error: {str(e)}")
#         return None

# async def batch_enhance(movies):
#     log_message(f"Batch enhancing {len(movies)} movies...")
#     loop = asyncio.get_event_loop()
#     with ThreadPoolExecutor() as executor:
#         futures = [loop.run_in_executor(executor, enhance_movie_info, movie) for movie in movies]
#         results = await asyncio.gather(*futures)
#     log_message("Batch enhancement done")
#     return results

# def display_movie_card_universal(movie, index=None):
#     """Universal movie card display for both TMDb and OMDb"""
#     source = movie.get("source", "tmdb")

#     if source == "tmdb":
#         # TMDb movie structure
#         title = movie.get("title", "Unknown Title")
#         year = movie.get("release_date", "")[:4] if movie.get("release_date") else "N/A"
#         rating = movie.get("vote_average", "N/A")
#         language = movie.get("original_language", "N/A").upper()
#         poster_url = movie.get("poster_url")
#         overview = movie.get("overview", "No description available.")

#         # Enhanced description from session state
#         enhanced_info = st.session_state.enhanced_movies.get(index, {}) if index is not None else {}
#         enhanced_text = enhanced_info.get("enhanced", overview)

#         rating_badge_class = "rating-badge" if isinstance(rating, (int, float)) and rating >= 7.0 else "meta-badge"
#         rating_display = f"⭐ {rating}/10"

#     else:
#         # OMDb movie structure
#         title = movie.get("Title", "Unknown Title")
#         year = movie.get("Year", "N/A")
#         rating = movie.get("imdbRating", "N/A")
#         language = movie.get("Language", "N/A").split(",")[0].strip()
#         poster_url = movie.get("Poster") if movie.get("Poster") != "N/A" else None
#         overview = movie.get("Plot", "No description available.")

#         # Enhanced description
#         enhanced_info = st.session_state.enhanced_movies.get(f"omdb_{movie.get('imdbID', index)}", {})
#         enhanced_text = enhanced_info.get("enhanced", overview)

#         rating_badge_class = "imdb-badge"
#         rating_display = f"⭐ {rating}/10"

#     # Generate poster HTML
#     if poster_url:
#         poster_html = f'<img src="{poster_url}" alt="Poster" class="card-poster" />'
#     else:
#         poster_html = '<div class="card-poster" style="background: #333; display:flex; align-items:center; justify-content:center; color:#666;">No Poster</div>'

#     # Generate card HTML
#     card_html = f"""
#     <div class="netflix-card">
#         {poster_html}
#         <div class="card-content">
#             <div class="card-title">{title}</div>
#             <div class="card-meta">
#                 <span class="{rating_badge_class}">{rating_display}</span>
#                 <span class="meta-badge">📅 {year}</span>
#                 <span class="meta-badge">🗣 {language}</span>
#                 <span class="meta-badge">📡 {source.upper()}</span>
#             </div>
#             <div class="enhanced-description">
#                 <p><strong>🤖 Enhanced:</strong> {enhanced_text}</p>
#             </div>
#         </div>
#     </div>
#     """
#     return card_html

# def show_recommendations_mode():
#     """TMDb-based AI recommendations with user profiling - no sidebar, main page layout"""

#     st.markdown('<style>'
#                 '.netflix-card {display:flex; gap:15px; background:#222; border-radius:8px; padding:10px; margin-bottom:10px;}'
#                 '.card-poster {width:100px; height:150px; object-fit:cover; border-radius:5px;}'
#                 '.card-content {flex:1; color:#eee;}'
#                 '.card-title {font-size:20px; font-weight:bold; margin-bottom:6px;}'
#                 '.card-meta {font-size:12px; margin-bottom:8px; display:flex; gap:10px;}'
#                 '.rating-badge {background:#2ecc71; padding:2px 6px; border-radius:4px; color:#fff;}'
#                 '.meta-badge {background:#555; padding:2px 6px; border-radius:4px; color:#ddd;}'
#                 '.imdb-badge {background:#f5c518; padding:2px 6px; border-radius:4px; color:#000;}'
#                 '.enhanced-description p {margin:0; font-style: italic; color:#ccc;}'
#                 '.section-header {font-size:26px; font-weight:bold; margin:20px 0 10px 0; color:#ffa500;}'
#                 '</style>', unsafe_allow_html=True)

#     st.markdown('<div class="section-header">👤 Your Movie Profile & AI Recommendations</div>', unsafe_allow_html=True)

#     # User Profile Form Section
#     with st.form("user_profile_form", clear_on_submit=False):
#         st.markdown("### 🎭 Tell us about yourself")

#         col1, col2 = st.columns(2)

#         with col1:
#             name = st.text_input("What's your name?", placeholder="Enter your name", key="name_input")
#             mood = st.selectbox(
#                 "How are you feeling today?",
#                 ["Happy", "Sad", "Excited", "Relaxed", "Adventurous", "Romantic", "Thrilled", "Nostalgic"],
#                 key="mood_select"
#             )
#             genres = st.multiselect(
#                 "Select your favorite genres:",
#                 list(GENRE_MAP_LOCAL.keys()),
#                 key="genre_select"
#             )
#             languages = st.multiselect(
#                 "What languages do you prefer?",
#                 ["English", "Hindi", "Tamil", "Telugu", "Malayalam", "Kannada", "Bengali", "Marathi"],
#                 default=["English"],
#                 key="language_select"
#             )

#         with col2:
#             actors = st.text_area(
#                 "List your favorite actors (comma-separated):",
#                 placeholder="e.g., Shah Rukh Khan, Deepika Padukone, Tom Hanks",
#                 key="actors_input"
#             )
#             favorites = st.text_area(
#                 "List some of your favorite movies (comma-separated):",
#                 placeholder="e.g., Inception, 3 Idiots, The Shawshank Redemption",
#                 key="favorites_input"
#             )
#             country = st.selectbox(
#                 "Country:",
#                 ["India", "United States", "United Kingdom", "Canada", "Australia"],
#                 key="country_select"
#             )

#         submitted = st.form_submit_button("🚀 Get AI-Powered Recommendations", type="primary")

#     if submitted:
#         if not name:
#             st.warning("Please enter your name to get personalized recommendations!")
#         elif not genres:
#             st.warning("Please select at least one genre!")
#         else:
#             user_profile = {
#                 "name": name,
#                 "mood": mood,
#                 "genres": genres,
#                 "actors": [actor.strip() for actor in actors.split(",")] if actors else [],
#                 "languages": [lang.lower()[:2] for lang in languages],
#                 "favorites": [movie.strip() for movie in favorites.split(",")] if favorites else [],
#                 "country": country[:2].upper()
#             }

#             st.session_state.user_profile = user_profile
#             st.session_state.show_all = False
#             st.session_state.enhanced_movies = {}

#             with st.spinner("🎬 AI is finding your perfect movies..."):
#                 params = generate_recommendations(user_profile)

#                 if params:
#                     movies = discover_movies(params)
#                     st.session_state.recommendations = movies

#                     if movies:
#                         st.success(f"🎉 Found {len(movies)} amazing movies for you!")

#                         # Enhance first 5 movies asynchronously
#                         enhanced_batch = asyncio.run(batch_enhance(movies[:5]))
#                         for i, enhanced in enumerate(enhanced_batch):
#                             if enhanced:
#                                 st.session_state.enhanced_movies[i] = enhanced
#                     else:
#                         st.warning("No movies found. Try different genres!")
#                 else:
#                     st.error("Unable to generate recommendations. Check API keys.")

#     # Display recommendations below form
#     if st.session_state.get("recommendations"):
#         st.markdown('<div class="section-header">🍿 Your AI-Curated Movies</div>', unsafe_allow_html=True)

#         movies_to_show = st.session_state.recommendations[:5] if not st.session_state.show_all else st.session_state.recommendations

#         for i, movie in enumerate(movies_to_show):
#             card_html = display_movie_card_universal(movie, i)
#             st.markdown(card_html, unsafe_allow_html=True)

#         if not st.session_state.show_all and len(st.session_state.recommendations) > 5:
#             if st.button("🔥 Load More Recommendations", key="load_more"):
#                 st.session_state.show_all = True
#                 # Enhance remaining movies
#                 for i, movie in enumerate(st.session_state.recommendations[5:], 5):
#                     if i not in st.session_state.enhanced_movies:
#                         enhanced = enhance_movie_info_unified(movie, "tmdb")
#                         if enhanced:
#                             st.session_state.enhanced_movies[i] = enhanced
#                 st.rerun()

#     # Show user profile summary and AI tips on right side if desired
#     col_left, col_right = st.columns([3, 1])
#     with col_right:
#         if st.session_state.get("user_profile"):
#             profile = st.session_state.user_profile
#             st.markdown("### 📊 Your Profile Summary")
#             st.markdown(f"""
# **Name:** {profile.get('name', 'Not set')}  
# **Mood:** {profile.get('mood', 'Not set')}  
# **Genres:** {', '.join(profile.get('genres', []))}  
# **Languages:** {', '.join(profile.get('languages', []))}
# """)

#         st.markdown("### 💡 AI Tips")
#         st.info("🎯 Be specific with your preferences\n🎭 Mood influences recommendations")

# def main_tmdb():
#     st.title("🎥 TMDB Movie Explorer")
#     show_recommendations_mode()
# if __name__ == "__main__":
#     st.set_page_config(page_title="AI Movie Recommendations", layout="wide")
#     inject_global_css()
#     main_tmdb()

#     # Logs expander at bottom
#     if st.session_state.log_messages:
#         with st.expander("📝 Logs", expanded=False):
#             for log in st.session_state.log_messages:
#                 st.text(log)



import streamlit as st
import os
import re
import json
import time
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import requests


# Standard Library Impoimport os
import re
import json
import time
import os 
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

# Third-Party Imports
import requests
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

# LangChain Core Imports
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.tools import Tool

# LangChain Community Imports
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper

# LangChain Agents (if needed)
from langchain.agents import initialize_agent, AgentType

# Groq Imports
from langchain_groq import ChatGroq

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
#     with open("/Users/ssris/Desktop/RIMSAB/LANG/IBM/app/style.css") as f:
#         css = f.read()
#     st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
#     netflix_css = """
#     <style>
#     .netflix-card {
#     #     display: flex;
#     #     gap: 15px;
#     #     background: rgba(30, 30, 30, 0.8);
#     #     border-radius: 12px;
#     #     padding: 15px;
#     #     margin-bottom: 15px;
#     #     transition: all 0.3s ease;
#     #     border-left: 4px solid #ff8a00;
#     # }
    
#     # .netflix-card:hover {
#     #     transform: translateY(-3px);
#     #     box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
#     #     background: rgba(40, 40, 40, 0.9);
#     # }
    
#     # .card-poster {
#     #     width: 120px;
#     #     height: 180px;
#     #     object-fit: cover;
#     #     border-radius: 8px;
#     #     box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
#     # }
    
#     # .card-content {
#     #     flex: 1;
#     #     color: #eee;
#     # }
    
#     # .card-title {
#     #     font-size: 1.4rem;
#     #     font-weight: bold;
#     #     margin-bottom: 0.5rem;
#     #     color: #fff;
#     # }
    
#     # .card-meta {
#     #     font-size: 0.85rem;
#     #     margin-bottom: 0.8rem;
#     #     display: flex;
#     #     flex-wrap: wrap;
#     #     gap: 8px;
#     # }
    
#     # .rating-badge {
#     #     background: linear-gradient(135deg, #2ecc71, #27ae60);
#     #     padding: 3px 8px;
#     #     border-radius: 20px;
#     #     color: #fff;
#     #     font-weight: bold;
#     #     font-size: 0.8rem;
#     # }
    
#     # .meta-badge {
#     #     background: rgba(85, 85, 85, 0.7);
#     #     padding: 3px 8px;
#     #     border-radius: 20px;
#     #     color: #ddd;
#     #     font-size: 0.8rem;
#     # }
    
#     # .imdb-badge {
#     #     background: linear-gradient(135deg, #f5c518, #d4af37);
#     #     padding: 3px 8px;
#     #     border-radius: 20px;
#     #     color: #000;
#     #     font-weight: bold;
#     #     font-size: 0.8rem;
#     # }
    
#     # .enhanced-description {
#     #     font-size: 0.95rem;
#     #     line-height: 1.4;
#     #     margin-top: 0.5rem;
#     # }
    
#     # .enhanced-description p {
#     #     margin: 0;
#     #     color: #ccc;
#     # }
#     </style>
#     """
#     st.markdown(netflix_css, unsafe_allow_html=True)


# Load environment variables
load_dotenv("/Users/ssris/Desktop/RIMSAB/LANG/.env")

# Initialize session state defaults
session_state_defaults = {
    'recommendations': [],
    'user_profile': {},
    'show_all': False,
    'enhanced_movies': {},
    'log_messages': []
}
for key, default in session_state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default

def log_message(message):
    """Add timestamped message to logs, keep last 20."""
    if "log_messages" not in st.session_state:
        st.session_state.log_messages = []
    timestamp = datetime.now().strftime("%H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    st.session_state.log_messages.append(full_message)
    if len(st.session_state.log_messages) > 20:
        st.session_state.log_messages = st.session_state.log_messages[-20:]


GENRE_MAP_LOCAL = {
    "action": 28, "adventure": 12, "animation": 16, "comedy": 35, "crime": 80,
    "documentary": 99, "drama": 18, "family": 10751, "fantasy": 14, "history": 36,
    "horror": 27, "music": 10402, "mystery": 9648, "romance": 10749,
    "science fiction": 878, "tv movie": 10770, "thriller": 53, "war": 10752, "western": 37
}

def map_genres_to_ids(genres_list):
    ids = [str(GENRE_MAP_LOCAL.get(g.strip().lower())) for g in genres_list if GENRE_MAP_LOCAL.get(g.strip().lower())]
    return "|".join(ids)

def extract_json_from_text(text):
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        json_text = match.group()
        # Replace single quotes with double quotes (not perfect but helps)
        json_text = json_text.replace("'", '"')
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            return None
    return None

@st.cache_resource
def initialize_llm():
    try:
        log_message("Initializing LLM connection...")
        llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama3-8b-8192",
            temperature=0.3
        )
        log_message("LLM connection established successfully")
        return llm
    except Exception as e:
        log_message(f"⚠️ LLM initialization failed: {str(e)}")
        return None

def enhance_movie_info(movie):
    llm = initialize_llm()
    if not llm:
        log_message("⚠️ Cannot enhance movie info - LLM not available")
        return None

    title = movie.get("title", "")
    overview = movie.get("overview", "")

    prompt = PromptTemplate(
        template="""
Translate and enhance the following movie details into natural English.

Title: {title}
Overview: {overview}

Respond in 2-3 lines: English title (if appropriate), a brief and appealing description.
""",
        input_variables=["title", "overview"]
    )

    try:
        log_message(f"Enhancing movie info for: {title}")
        chain = prompt | llm | StrOutputParser()
        enhanced_description = chain.invoke({"title": title, "overview": overview}).strip()
        return {"enhanced": enhanced_description}
    except Exception as e:
        log_message(f"⚠️ Error enhancing movie {title}: {str(e)}")
        return None

def enhance_movie_info_unified(movie, source="tmdb"):
    # For TMDb or OMDb unified enhancement
    llm = initialize_llm()
    if not llm:
        log_message("⚠️ Cannot enhance movie info - LLM not available")
        return None

    if source == "tmdb":
        title = movie.get("title", "")
        overview = movie.get("overview", "")
    else:
        title = movie.get("Title", "")
        overview = movie.get("Plot", "")

    prompt = PromptTemplate(
        template="""
Translate and enhance the following movie details into natural English.

Title: {title}
Overview: {overview}

Respond in 2-3 lines: English title (if appropriate), a brief and appealing description.
""",
        input_variables=["title", "overview"]
    )

    try:
        log_message(f"Enhancing movie info for: {title}")
        chain = prompt | llm | StrOutputParser()
        enhanced_description = chain.invoke({"title": title, "overview": overview}).strip()
        return {"enhanced": enhanced_description}
    except Exception as e:
        log_message(f"⚠️ Error enhancing movie {title}: {str(e)}")
        return None

def discover_movies(params, max_retries=3):
    if not params or not params.get("api_key"):
        log_message("⚠️ Invalid API parameters for TMDb request")
        return []

    for attempt in range(max_retries):
        try:
            log_message(f"Fetching movies from TMDb (Attempt {attempt+1})...")
            response = requests.get("https://api.themoviedb.org/3/discover/movie", params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                movies = []
                for movie in results[:10]:
                    movie_data = {
                        "title": movie.get("title"),
                        "overview": movie.get("overview"),
                        "release_date": movie.get("release_date"),
                        "vote_average": movie.get("vote_average"),
                        "original_language": movie.get("original_language"),
                        "genre_ids": movie.get("genre_ids"),
                        "poster_url": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get("poster_path") else None
                    }
                    movies.append(movie_data)
                log_message(f"Successfully fetched {len(movies)} movies")
                return movies
            elif response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 5))
                log_message(f"Rate limit hit. Retrying after {retry_after}s...")
                time.sleep(retry_after)
                continue
            else:
                log_message(f"Unexpected status {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return []
        except requests.exceptions.RequestException as e:
            log_message(f"Connection error (attempt {attempt+1}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return []
    log_message("Failed to fetch movies after retries")
    return []

def generate_recommendations(user_profile):
    llm = initialize_llm()
    if not llm:
        st.error("⚠️ LLM not available. Check API keys.")
        log_message("⚠️ Cannot generate recommendations - LLM not available")
        return None

    profile_prompt = PromptTemplate(
    template="""
Given the user preferences, generate a JSON dictionary named 'params' for TMDb Discover API with the following rules:

- Include 'api_key' as 'DUMMY_KEY'.
- 'language' formatted as '{language}-IN'.
- Sort by 'popularity.desc'
- Include_adult and include_video false.
- Page 1.
- with_genres pipe-separated genre IDs.
- with_original_language based on language.
- region is 2-letter ISO country code.

Respond ONLY with the JSON dictionary, no explanations, comments, or extra text.

User Preferences:
Genres: {genres}
Language: {language}
Country: {country}
Genre IDs: {genre_ids}
""",
    input_variables=["genres", "language", "country", "genre_ids"]
)


    genre_ids = map_genres_to_ids(user_profile.get("genres", []))
    language = user_profile.get("languages", ["en"])[0].lower()
    country = user_profile.get("country", "IN").upper()[:2]

    try:
        log_message("Generating API parameters via LLM...")
        raw_response = (profile_prompt | llm | StrOutputParser()).invoke({
            "genres": user_profile.get("genres", []),
            "language": language,
            "country": country,
            "genre_ids": genre_ids
        })
        minimal_profile = extract_json_from_text(raw_response)
        if minimal_profile:
            minimal_profile["api_key"] = os.getenv("TMDB_API_KEY")
            log_message("API params generated")
            return minimal_profile
        else:
            log_message("⚠️ Failed to parse LLM response")
            return None
    except Exception as e:
        log_message(f"⚠️ Error generating recommendations: {str(e)}")
        st.error(f"Error: {str(e)}")
        return None

async def batch_enhance(movies):
    log_message(f"Batch enhancing {len(movies)} movies...")
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        futures = [loop.run_in_executor(executor, enhance_movie_info, movie) for movie in movies]
        results = await asyncio.gather(*futures)
    log_message("Batch enhancement done")
    return results

def display_movie_card_universal(movie, index=None):
    """Universal movie card display for both TMDb and OMDb"""
    source = movie.get("source", "tmdb")

    if source == "tmdb":
        # TMDb movie structure
        title = movie.get("title", "Unknown Title")
        year = movie.get("release_date", "")[:4] if movie.get("release_date") else "N/A"
        rating = movie.get("vote_average", "N/A")
        language = movie.get("original_language", "N/A").upper()
        poster_url = movie.get("poster_url")
        overview = movie.get("overview", "No description available.")

        # Enhanced description from session state
        enhanced_info = st.session_state.enhanced_movies.get(index, {}) if index is not None else {}
        enhanced_text = enhanced_info.get("enhanced", overview)

        rating_badge_class = "rating-badge" if isinstance(rating, (int, float)) and rating >= 7.0 else "meta-badge"
        rating_display = f"⭐ {rating}/10"

    else:
        # OMDb movie structure
        title = movie.get("Title", "Unknown Title")
        year = movie.get("Year", "N/A")
        rating = movie.get("imdbRating", "N/A")
        language = movie.get("Language", "N/A").split(",")[0].strip()
        poster_url = movie.get("Poster") if movie.get("Poster") != "N/A" else None
        overview = movie.get("Plot", "No description available.")

        # Enhanced description
        enhanced_info = st.session_state.enhanced_movies.get(f"omdb_{movie.get('imdbID', index)}", {})
        enhanced_text = enhanced_info.get("enhanced", overview)

        rating_badge_class = "imdb-badge"
        rating_display = f"⭐ {rating}/10"

    # Generate poster HTML
    if poster_url:
        poster_html = f'<img src="{poster_url}" alt="Poster" class="card-poster" />'
    else:
        poster_html = '<div class="card-poster" style="background: #333; display:flex; align-items:center; justify-content:center; color:#666;">No Poster</div>'

    # Generate card HTML
    card_html = f"""
    <div class="netflix-card">
        {poster_html}
        <div class="card-content">
            <div class="card-title">{title}</div>
            <div class="card-meta">
                <span class="{rating_badge_class}">{rating_display}</span>
                <span class="meta-badge">📅 {year}</span>
                <span class="meta-badge">🗣 {language}</span>
                <span class="meta-badge">📡 {source.upper()}</span>
            </div>
            <div class="enhanced-description">
                <p><strong>🤖 Enhanced:</strong> {enhanced_text}</p>
            </div>
        </div>
    </div>
    """
    return card_html

def show_recommendations_mode():
    st.markdown('<div class="section-header">🎬 AI Movie Recommender - Powered by Tmdb</div>', unsafe_allow_html=True)
    # User Profile Form Section
    with st.form("user_profile_form", clear_on_submit=False):
        # st.markdown('<div class="section-header">👤 Your Movie Profile</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("What's your name?", placeholder="Enter your name", key="name_input")
            mood = st.selectbox(
                "How are you feeling today?",
                ["Happy", "Sad", "Excited", "Relaxed", "Adventurous", "Romantic", "Thrilled", "Nostalgic"],
                key="mood_select",
                help="Your mood helps tailor recommendations"
            )
            genres = st.multiselect(
                "Select your favorite genres:",
                list(GENRE_MAP_LOCAL.keys()),
                key="genre_select",
                help="Select at least one genre"
            )
            languages = st.multiselect(
                "What languages do you prefer?",
                ["English", "Hindi", "Tamil", "Telugu", "Kannada"],
                default=["English"],
                key="language_select",
                help="Preferred movie languages"
            )

        with col2:
            actors = st.text_area(
                "List your favorite actors (optional):",
                placeholder="e.g., Shah Rukh Khan, Deepika Padukone, Tom Hanks",
                key="actors_input",
                help="Optional - helps personalize recommendations"
            )
            favorites = st.text_area(
                "List some of your favorite movies (optional):",
                placeholder="e.g., Inception, 3 Idiots, The Shawshank Redemption",
                key="favorites_input",
                help="Optional - helps understand your taste"
            )
            country = st.selectbox(
                "Country:",
                ["United Kingdom","India", "Canada", "Australia"],
                key="country_select",
                help="Helps with regional recommendations"
            )

        submitted = st.form_submit_button("🚀 Get AI-Powered Recommendations", type="primary", 
                                        help="Click to generate personalized movie suggestions")

    if submitted:
        if not name:
            st.warning("Please enter your name to get personalized recommendations!")
        elif not genres:
            st.warning("Please select at least one genre!")
        else:
            user_profile = {
                "name": name,
                "mood": mood,
                "genres": genres,
                "actors": [actor.strip() for actor in actors.split(",")] if actors else [],
                "languages": [lang.lower()[:2] for lang in languages],
                "favorites": [movie.strip() for movie in favorites.split(",")] if favorites else [],
                "country": country[:2].upper()
            }

            st.session_state.user_profile = user_profile
            st.session_state.show_all = False
            st.session_state.enhanced_movies = {}

            with st.spinner("🎬 AI is finding your perfect movies..."):
                params = generate_recommendations(user_profile)

                if params:
                    movies = discover_movies(params)
                    st.session_state.recommendations = movies

                    if movies:
                        st.success(f"🎉 Found {len(movies)} amazing movies for you!")

                        # Enhance first 5 movies asynchronously
                        enhanced_batch = asyncio.run(batch_enhance(movies[:5]))
                        for i, enhanced in enumerate(enhanced_batch):
                            if enhanced:
                                st.session_state.enhanced_movies[i] = enhanced
                    else:
                        st.warning("No movies found. Try different genres!")
                else:
                    st.error("Unable to generate recommendations. Check API keys.")

    # Display recommendations below form
    if st.session_state.get("recommendations"):
        st.markdown('<div class="section-header">🍿 Your AI-Curated Movies</div>', unsafe_allow_html=True)

        movies_to_show = st.session_state.recommendations[:5] if not st.session_state.show_all else st.session_state.recommendations

        for i, movie in enumerate(movies_to_show):
            card_html = display_movie_card_universal(movie, i)
            st.markdown(card_html, unsafe_allow_html=True)

        if not st.session_state.show_all and len(st.session_state.recommendations) > 5:
            if st.button("🔥 Load More Recommendations", key="load_more"):
                st.session_state.show_all = True
                # Enhance remaining movies
                for i, movie in enumerate(st.session_state.recommendations[5:], 5):
                    if i not in st.session_state.enhanced_movies:
                        enhanced = enhance_movie_info_unified(movie, "tmdb")
                        if enhanced:
                            st.session_state.enhanced_movies[i] = enhanced
                st.rerun()

    # Show user profile summary and AI tips on right side if desired
    col_left, col_right = st.columns([3, 1])
    with col_right:
        if st.session_state.get("user_profile"):
            profile = st.session_state.user_profile
            st.markdown("""
            <div class="profile-card">
                <h3>📊 Your Profile Summary</h3>
                <p><strong>Name:</strong> {name}<br>
                <strong>Mood:</strong> {mood}<br>
                <strong>Genres:</strong> {genres}<br>
                <strong>Languages:</strong> {languages}</p>
            </div>
            """.format(
                name=profile.get('name', 'Not set'),
                mood=profile.get('mood', 'Not set'),
                genres=', '.join(profile.get('genres', [])),
                languages=', '.join(profile.get('languages', []))
            ), unsafe_allow_html=True)

        st.markdown("""
        <div class="profile-card">
            <h3>💡 AI Tips</h3>
            <p>🎯 Be specific with your preferences<br>
            🎭 Mood influences recommendations<br>
            🌍 Country affects availability<br>
            🎬 More favorites = better suggestions</p>
        </div>
        """, unsafe_allow_html=True)

def main_tmdb():
    inject_global_css()
    show_recommendations_mode()
    
if __name__ == "__main__":
    main_tmdb()

    # Logs expander at bottom
    if st.session_state.log_messages:
        with st.expander("📝 System Logs", expanded=False):
            for log in st.session_state.log_messages:
                st.code(log, language="log")