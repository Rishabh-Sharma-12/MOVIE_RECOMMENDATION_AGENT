import streamlit as st
from dotenv import load_dotenv
from app.omdb_funct import main_omdb
from app.tmdb_func import main_tmdb

load_dotenv()

def inject_global_css():
    with open("/Users/ssris/Desktop/RIMSAB/LANG/IBM/app/style.css") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def main_home():
    st.set_page_config(
        page_title="CineMatch - AI Movie Recommender",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    inject_global_css()

    if 'selected_mode' not in st.session_state:
        st.session_state.selected_mode = "tmdb"

    # Sidebar Section
     # Sidebar Section
    with st.sidebar:
        st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #ffcc00; font-size: 2.5rem;">🍿 Discover Your Next Favorite Movie</h1>
        <p style="color: #ccc; font-size: 1.2rem; max-width: 600px; margin: auto;">
            Whether you want AI-curated picks or instant search, CineMatch brings global cinema right to your screen.
        </p>
    </div>
    """, unsafe_allow_html=True)

    
        st.markdown("<hr style='border: 0.5px solid #444;'>", unsafe_allow_html=True)
        
        st.markdown('<div class="section-title" style="font-weight: bold; color: #fff; margin-bottom: 0.5rem;">🎯 Choose Your Experience</div>', unsafe_allow_html=True)
        
        # Buttons with hover styling
        if st.button(
            "🎯 Smart Recommendations",
            key="sidebar_tmdb_btn",
            help="AI-powered suggestions based on your preferences",
            use_container_width=True,
            type="primary" if st.session_state.selected_mode == "tmdb" else "secondary"
        ):
            st.session_state.selected_mode = "tmdb"
            st.rerun()
        
        if st.button(
            "🔍 Direct Movie Search",
            key="sidebar_omdb_btn",
            help="Find any movie instantly with detailed information",
            use_container_width=True,
            type="primary" if st.session_state.selected_mode == "omdb" else "secondary"
        ):
            st.session_state.selected_mode = "omdb"
            st.rerun()
            
        st.markdown("<hr style='border: 0.5px solid #444;'>", unsafe_allow_html=True)
        
        # Features
        with st.expander("✨ Features", expanded=False):
            st.markdown("""
            - 🎯 **AI-Powered Recommendations**  
            - 🎬 **Comprehensive Movie Search**  
            - 📊 **Smart Analytics**  
            - 🌍 **Global Content Database**  
            """)


    # Main Content Area
    st.markdown("""
        <div class="welcome-header">
            <div class="app-header">🎬 CineMatch</div>
        </div>
    """, unsafe_allow_html=True)
        
    # Load the selected mode
    if st.session_state.selected_mode == "tmdb":
        main_tmdb()
    else:
        main_omdb()

if __name__ == "__main__":
    main_home()