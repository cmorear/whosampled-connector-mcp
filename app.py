import streamlit as st
import asyncio
import nest_asyncio
from scraper import WhoSampledScraper

# Apply patch for running asyncio within Streamlit
nest_asyncio.apply()

st.set_page_config(
    page_title="WhoSampled Explorer",
    page_icon="🎵",
    layout="wide"
)

st.title("🎵 WhoSampled Explorer")
st.markdown("Search for a track to see its samples, covers, and remixes.")

# Initialize Scraper in Session State
if 'scraper' not in st.session_state:
    try:
        # FIX: Removed 'headless=True' argument to resolve the TypeError.
        # The scraper defaults to headless=True anyway.
        st.session_state.scraper = WhoSampledScraper()
        
        # Optional: Add a brief welcome message to confirm successful basic rendering
        st.sidebar.caption("Scraper initialized.")
    except Exception as e:
        # If initialization fails (e.g., missing dependency, Playwright issue), display the error
        st.error("Application Initialization Failed. Please check the terminal for errors.")
        st.exception(e)
        st.stop()
        
if 'current_track' not in st.session_state:
    st.session_state.current_track = None
if 'track_details' not in st.session_state:
    st.session_state.track_details = None

# --- Sidebar Search ---
with st.sidebar:
    st.header("Search")
    query = st.text_input("Artist & Track Name", placeholder="e.g. Daft Punk One More Time")
    search_btn = st.button("Search", type="primary")

async def perform_search(search_query):
    with st.spinner(f"Searching for '{search_query}'..."):
        return await st.session_state.scraper.search_track(search_query)

async def perform_details_lookup(url):
    with st.spinner("Fetching samples and YouTube data..."):
        return await st.session_state.scraper.get_track_details(url)

# --- Main Logic ---

if search_btn and query:
    # 1. Search for the track
    result = asyncio.run(perform_search(query))
    
    if result.get("found"):
        st.session_state.current_track = result
        # Reset details when a new track is found
        st.session_state.track_details = None 
        st.success(f"Found match!")
    else:
        st.error(f"Not found. Error: {result.get('error')}")

# --- Display Results ---

if st.session_state.current_track:
    track = st.session_state.current_track
    
    st.divider()
    
    # Layout: Left column for info/player, Right column for connections
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if track.get('image_url'):
            st.image(track['image_url'], width=200)
            
        st.subheader(track['title'])
        st.markdown(f"**Artist:** {track['artist']}")
        st.markdown(f"[View on WhoSampled]({track['url']})")
        
        # Load Details Button (if not already loaded)
        if st.session_state.track_details is None:
            if st.button("Load Connections & Audio"):
                details = asyncio.run(perform_details_lookup(track['url']))
                st.session_state.track_details = details
                st.rerun() # Rerun to update the UI with new data
        
        # Display YouTube Player if we have the ID
        if st.session_state.track_details:
            yt_id = st.session_state.track_details.get('youtube_id')
            if yt_id:
                st.markdown("#### Listen")
                st.video(f"https://www.youtube.com/watch?v={yt_id}")
            else:
                st.warning("No YouTube link found on WhoSampled page.")

    with col2:
        if st.session_state.track_details:
            details = st.session_state.track_details
            
            # Helper to display a list of tracks
            def display_list(items, empty_msg):
                if not items:
                    st.caption(empty_msg)
                    return
                for item in items:
                    with st.expander(f"{item['track']} - {item['artist']}"):
                        st.write(f"Link: {item['url']}")
            
            tab1, tab2, tab3, tab4 = st.tabs(["➡️ Samples", "⬅️ Sampled By", "🎤 Covers", "🎛️ Remixes"])
            
            with tab1:
                st.markdown("### Contains samples of:")
                display_list(details['samples'], "No samples found.")
                
            with tab2:
                st.markdown("### Was sampled in:")
                display_list(details['sampled_by'], "Has not been sampled.")
                
            with tab3:
                st.markdown("### Covered by:")
                display_list(details['covers'], "No covers found.")
                
            with tab4:
                st.markdown("### Remixes:")
                display_list(details['remixes'], "No remixes found.")
                
        elif st.session_state.current_track and st.session_state.track_details is None:
             st.info("👈 Click 'Load Connections & Audio' to see samples.")