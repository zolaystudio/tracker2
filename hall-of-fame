import streamlit as st
from googleapiclient.discovery import build
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Arthur Murray Hall of Fame", layout="wide")
st.title("🏆 Top 100 Arthur Murray Videos of All Time")

# 1. Connection setup
conn = st.connection("gsheets", type=GSheetsConnection)
my_key = st.sidebar.text_input("YouTube API Key:", type="password")
sheet_url = st.sidebar.text_input("Paste Google Sheet URL:")

if my_key and sheet_url:
    youtube = build('youtube', 'v3', developerKey=my_key)
    
    # 2. SEARCH: Get 50 results (Max for one search)
    # To get 100, we'd need a 'nextPageToken', but 50 is a great start!
    search_response = youtube.search().list(
        q="Arthur Murray dance",
        part="snippet",
        type="video",
        maxResults=50,
        order="viewCount" # Sorts by most views of all time
    ).execute()

    video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
    
    # 3. GET FULL STATS
    v_details = youtube.videos().list(id=','.join(video_ids), part="snippet,statistics").execute()

    data = []
    for v in v_details.get('items', []):
        channel_name = v['snippet']['channelTitle']
        
        # Check if the channel starts with Arthur Murray
        if channel_name.lower().startswith("arthur murray"):
            data.append({
                "Thumbnail": v['snippet']['thumbnails']['default']['url'],
                "Title": v['snippet']['title'],
                "Channel": channel_name,
                "Views": int(v['statistics'].get('viewCount', 0)),
                "URL": f"https://www.youtube.com/watch?v={v['id']}"
            })

    # 4. SHOW AND SYNC
    df = pd.DataFrame(data)
    if not df.empty:
        if st.button("🚀 Push Top Videos to Google Sheet"):
            conn.update(spreadsheet=sheet_url, data=df)
            st.success("Your Google Sheet is now a Hall of Fame!")
        
        # Display the data visually with thumbnails
        st.data_editor(df, column_config={
            "Thumbnail": st.column_config.ImageColumn("Preview"),
            "URL": st.column_config.LinkColumn("Watch Video")
        })
    else:
        st.warning("No official studio videos found in the top results.")
