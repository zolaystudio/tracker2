import streamlit as st
from googleapiclient.discovery import build
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Arthur Murray Hall of Fame", layout="wide")
st.title("🏆 Top 100 Arthur Murray Videos of All Time")

conn = st.connection("gsheets", type=GSheetsConnection)
my_key = st.sidebar.text_input("YouTube API Key:", type="password")
sheet_url = st.sidebar.text_input("Paste Google Sheet URL:")

if my_key and sheet_url:
    youtube = build('youtube', 'v3', developerKey=my_key)
    
    data = []
    next_page_token = None
    target_count = 100 # We want 100 results

    # 1. LOOP: Keep searching until we hit 100 or run out of pages
    while len(data) < target_count:
        search_response = youtube.search().list(
            q="Arthur Murray dance",
            part="snippet",
            type="video",
            maxResults=50,
            order="viewCount",
            pageToken=next_page_token # Tell YouTube which page we are on
        ).execute()

        video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
        v_details = youtube.videos().list(id=','.join(video_ids), part="snippet,statistics").execute()

        for v in v_details.get('items', []):
            channel_name = v['snippet']['channelTitle']
            thumb_url = v['snippet']['thumbnails']['default']['url']
            
            if channel_name.lower().startswith("arthur murray") and len(data) < target_count:
                data.append({
                    # This formula makes the thumbnail a real image in Google Sheets!
                    "Thumbnail": f'=IMAGE("{thumb_url}")', 
                    "Title": v['snippet']['title'],
                    "Channel": channel_name,
                    "Views": int(v['statistics'].get('viewCount', 0)),
                    "URL": f"https://www.youtube.com/watch?v={v['id']}"
                })

        next_page_token = search_response.get('nextPageToken')
        if not next_page_token: # Stop if there are no more pages
            break

    df = pd.DataFrame(data)
    if not df.empty:
        st.write(f"Found {len(df)} official studio videos!")
        if st.button("🚀 Push Top 100 to Google Sheet"):
            conn.update(spreadsheet=sheet_url, data=df)
            st.success("Successfully updated the Hall of Fame!")
        
        st.dataframe(df)
