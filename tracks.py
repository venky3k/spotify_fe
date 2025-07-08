import streamlit as st

import requests

response = requests.get('http://127.0.0.1:8000/track')
if response.status_code != 200:
    st.error('failed to fetch')

else:
    tracks = response.json()

for track in tracks:
    col = st.columns([2,0.5,3])
    st.write('your spotify tracks')
    with col[0]:
        if track['album_image']:
            st.image(track['album_image'])
        else:
            st.write('no album image')

    with col[2]:
        if track['track']:
            st.write(f"{track['track']}")
        else:
            st.subheader('-- unknown track --')

        if track['artist']:
            st.subheader(track['artist'])
        else:
            st.subheader('--unknow artist--')
            

