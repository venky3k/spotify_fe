import streamlit as st
import requests
from urllib.parse import unquote
import subprocess
import os
import yt_dlp
import zipfile
import tempfile
from yt_dlp import YoutubeDL

st.set_page_config(page_title="Spotiview", layout="wide")

st.sidebar.title("Spotiview")
pages = {
        "🏠 Home": "home",
        # "📁 All Playlists": "playlists", 
        "🎵 Create Playlist": "create",
        "🔍 add track": "search",
        # "📊 Top Tracks": "top",
        "👤 Profile": "profile",
       
    }
sel = st.sidebar.radio("------- NAV -------", pages.keys())
st.sidebar.markdown("")
page = pages[sel]

BACKEND = "spotify-61mzfte9x-kols-projects-e3efcee5.vercel.app"   


# @st.cache_data(show_spinner=False)
def fetch_profile():
    try:
        return requests.get(f"{BACKEND}/profile").json()
    except:
        return None

# @st.cache_data(show_spinner=False)
def fetch_playlists():
    try:
        return requests.get(f"{BACKEND}/playlists").json()
    except:
        return []

# @st.cache_data(show_spinner=False)
def fetch_playlist_by_id(pid):
    try:
        return requests.get(f"{BACKEND}/playlist/{pid}").json()
    except:
        return None

# @st.cache_data(show_spinner=False)
def fetch_top_tracks():
    try:
        return requests.get(f"{BACKEND}/track").json()
    except:
        return []

# === Track Search ===
def search_tracks(query):
    try:
        response = requests.get(f"{BACKEND}/search", params={"query": query})
        return response.json()
    except:
        return []

query = st.query_params
selected_playlist_id = query.get("playlist_id", None)
profile = fetch_profile()
col=st.columns([1,5,1])
with col[1]:
    st.markdown("<h1 style='color:#1DB954;'>Spotipy - Your Music, Streamlined</h1>", unsafe_allow_html=True)
col=st.columns([4,3,4])
with col[1]:
    if profile and not profile.get("error"):
        st.markdown(f"Welcome, **{profile['name']}** ")
    else:
        st.error("🔒 Please log in via Spotify: ")
        st.link_button("🔐 Login with Spotify", f"{BACKEND}/login")
        st.stop()

if page == "home":
    # Fetch playlists and tracks
    playlists = fetch_playlists()
    tracks = fetch_top_tracks()
    selected_playlist_id = st.query_params.get("playlist_id", None)

    # === TOP TRACKS ===
    st.subheader("🔥 Your Top Tracks")
    st.markdown("---")
    if not tracks:
        st.warning("No top tracks available.")
    else:
        for i in range(0, len(tracks), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(tracks):
                    track = tracks[i + j]
                    with cols[j]:
                        img_col, text_col = st.columns([1, 3])
                        with img_col:
                            if track['album_image']:
                                st.image(track['album_image'], width=100)
                            else:
                                st.write("No Image")
                        with text_col:
                            st.markdown(f"**{track['track']}**")
                            st.caption(track['artist'])
                            if track.get("preview_url"):
                                st.audio(track["preview_url"])
                            else:
                                st.caption("🔇 No Preview")




    # === PLAYLIST GRID ===
    st.subheader("🎶 Your Spotify Playlists")
    st.markdown("---")

    if isinstance(playlists, dict) and playlists.get("error"):
        st.error(playlists['error'])

    elif not playlists:
        st.warning("No playlists found.")
    else:
        for row in range(0, len(playlists), 4):
            cols = st.columns(4)
            for i, playlist in enumerate(playlists[row:row+4]):
                with cols[i]:
                    st.image(playlist.get("image") or "./spotify-png-template-transparent-background-E-7uLolpozA6z_l5-thumbnail.jpg", width=150)
                    # This sets the query param to trigger selected playlist
                    if st.button(playlist["name"], key=playlist["id"]):
                        st.query_params["playlist_id"] = playlist["id"]
                        st.rerun()

    st.markdown("---")

    # === SELECTED PLAYLIST TRACKS ===
    selected_playlist_id = st.query_params.get("playlist_id")

    if selected_playlist_id:
        selected_playlist_id = unquote(selected_playlist_id)
        playlist_data = fetch_playlist_by_id(selected_playlist_id)

        if not playlist_data or "error" in playlist_data:
            st.error("⚠️ Unable to fetch playlist.")
        else:
            st.subheader(f"🎧 Tracks in: {playlist_data['playlist']['name']}")

            # Safe fallback image
            fallback_url = "https://via.placeholder.com/200?text=No+Image"
            playlist_image = playlist_data["playlist"].get("image") or fallback_url
            st.image(playlist_image, width=200)

            # Handle empty playlist early
            if not playlist_data.get("tracks"):
                st.warning("🎧 This playlist is empty.")
            else:
                for i in range(0, len(playlist_data["tracks"]), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(playlist_data["tracks"]):
                            track = playlist_data["tracks"][i + j]
                            with cols[j]:
                                img_col, text_col = st.columns([1, 3])

                                with img_col:
                                    st.image(track.get("album_image") or fallback_url, width=100)

                                with text_col:
                                    st.markdown(f"**{track['track']}**")
                                    st.caption(track['artist'])
                                    if track.get("preview_url"):
                                        st.write(track["preview_url"])
                                        st.audio(track["preview_url"])
                                    else:
                                        
                                        st.caption("🔇 No Preview")

            if st.button("⬅ Back to All Playlists"):
                st.query_params.clear()
                st.rerun()
            if st.button("⬇ Download Songs from Playlist (via YouTube)"):

                with st.spinner("Downloading songs from YouTube..."):
                    temp_dir = tempfile.mkdtemp()
                    zip_path = os.path.join(temp_dir, "playlist_songs.zip")
                    
                    ffmpeg_path = r"C:\Users\vy846\Downloads\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"
                    
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'quiet': True,
                        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                        'ffmpeg_location': ffmpeg_path,
                    }

                    downloaded_files = set()
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for track in playlist_data["tracks"]:
                            query = f"{track['track']} {track['artist']} audio"
                            try:
                                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                    info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
                                    filename = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")

                                    # Avoid duplicate names
                                    if filename not in downloaded_files:
                                        zipf.write(filename, arcname=os.path.basename(filename))
                                        downloaded_files.add(filename)
                                    else:
                                        st.info(f"Skipped duplicate: {track['track']}")

                            except Exception as e:
                                st.warning(f"❌ Failed to download: {track['track']} - {track['artist']} | {str(e)}")

    # Send file to user
                    with open(zip_path, "rb") as f:
                        zip_bytes = f.read()

                    st.download_button(
                        label="🎧 Download ZIP of Songs",
                        data=zip_bytes,
                        file_name="playlist_songs.zip",
                        mime="application/zip"
                    )




elif page == "search":
    st.subheader("🔍 Search Tracks")

    # Search box
    search_query = st.text_input("Enter a track, artist, or album:")

    # If user types and submits query
    if search_query:
        with st.spinner("Searching..."):
            results = search_tracks(search_query)

        if isinstance(results, dict) and results.get("detail"):
            st.error("Failed to search tracks. Please check your server.")
        elif not results:
            st.info("No results found.")
        else:
            st.success(f"Found {len(results)} tracks")

            # Select a playlist to add tracks to
            playlists = fetch_playlists()
            if not playlists:
                st.warning("No playlists found. Create one first.")
            else:
                playlist_options = {pl['name']: pl['id'] for pl in playlists}
                selected_name = st.selectbox("Select a playlist to add songs:", list(playlist_options.keys()))
                selected_playlist_id = playlist_options[selected_name]

                # Track selection and display
                selected_track_ids = []
                for i in range(0, len(results), 2):
                    cols = st.columns(2)
                    for j in range(len(cols)):
                        if i + j < len(results):
                            track = results[i + j]
                            with cols[j]:
                                if track["album_image"]:
                                    st.image(track["album_image"], width=100)
                                st.markdown(f"**{track['track']}**")
                                st.caption(track["artist"])
                                if st.checkbox(f"Add: {track['track']}", key=track["id"]):
                                    selected_track_ids.append(track["id"])

                # Submit button to add tracks
                if selected_track_ids:
                    if st.button("➕ Add Selected Tracks to Playlist"):
                        res = requests.post(f"{BACKEND}/playlist/add-tracks", json={
                            "playlist_id": selected_playlist_id,
                            "track_ids": selected_track_ids
                        })

                        if res.status_code == 200:
                            st.success("Tracks added successfully!")
                        else:
                            st.error("Failed to add tracks.")





elif page == 'create':
    st.subheader("➕ Create a New Playlist")
    with st.form("create_playlist"):
        name = st.text_input("Playlist Name")
        desc = st.text_input("Description")
        submitted = st.form_submit_button("Create Playlist")
        if submitted:
            res = requests.post(f"{BACKEND}/create-playlist", json={"pl_name": name, "pl_desc": desc})
            if res.status_code == 200:
                st.success("✅ Playlist created successfully!")
                fetch_playlists.clear()
                st.rerun()
            else:
                st.error("❌ Failed to create playlist.")

elif page == "profile":
    st.subheader("👤 Profile")
    if profile:
        st.write(profile)
    else:
        st.error("No profile data found.")
