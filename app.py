import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


api_key = st.secrets['default']['API_KEY']  
youtube = build('youtube', 'v3', developerKey=api_key)

def get_channel_id(custom_url):
    try:
        request = youtube.search().list(
            part="id",
            type="channel",
            q=custom_url
        )
        response = request.execute()
        
        if 'items' in response and response['items']:
            return response['items'][0]['id']['channelId']
        else:
            st.error(f"No channel found for custom URL: {custom_url}")
            return None
    except HttpError as e:
        st.error(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

def get_channel_data(channel_id):
    try:
        request = youtube.channels().list(
            part='snippet,statistics',
            id=channel_id
        )
        response = request.execute()
        
        if 'items' not in response or not response['items']:
            st.error(f"No data found for channel ID: {channel_id}")
            return None
        
        channel_data = response['items'][0]['statistics']
        channel_snippet = response['items'][0]['snippet']
        
        data = {
            'Channel Name': channel_snippet['title'],
            'Subscribers': int(channel_data['subscriberCount']),
            'Total Views': int(channel_data['viewCount']),
            'Video Count': int(channel_data['videoCount']),
        }
        return data
    except HttpError as e:
        st.error(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return None
    except KeyError as e:
        st.error(f"KeyError: {e}. The API response doesn't contain the expected data.")
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

def get_video_data(channel_id):
    try:
        request = youtube.search().list(
            part='id',
            channelId=channel_id,
            maxResults=50,
            order='date'  # Fetch the latest videos
        )
        response = request.execute()
        
        video_ids = [item['id']['videoId'] for item in response.get('items', []) if item['id']['kind'] == 'youtube#video']
        
        video_data_list = []
        
        for video_id in video_ids:
            video_request = youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            )
            video_response = video_request.execute()
            
            if 'items' in video_response and video_response['items']:
                video_info = video_response['items'][0]
                video_data = {
                    'Video Title': video_info['snippet']['title'],
                    'Views': int(video_info['statistics'].get('viewCount', 0)),
                    'Likes': int(video_info['statistics'].get('likeCount', 0)),
                    'Comments': int(video_info['statistics'].get('commentCount', 0)),
                }
                video_data_list.append(video_data)
                
        return pd.DataFrame(video_data_list)
    
    except HttpError as e:
        st.error(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_lottie import st_lottie
import requests

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def main():
    st.set_page_config(page_title="YouTube Channel Analysis", page_icon="📊", layout="centered")
    st.title("Cristiano Ronaldo's YouTube Analysis ⚽⚽")
    # Custom CSS
    st.markdown("""
    <style>
    .main{
        background-color: #0c1320       
                }
    .stButton>button {
        color: #ffffff;
        background-color: #ff0000;
        border-radius: 5px;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    
    </style>
    """, unsafe_allow_html=True)

    # Sidebar
    
    lottie_analysis = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_qp1q7mct.json")
    st_lottie(lottie_analysis, speed=1, height=200, key="analysis")
    
    # Automatically analyze @cristiano
    custom_url = "@cristiano"
    channel_id = get_channel_id(custom_url)
    
    if channel_id:
        channel_data = get_channel_data(channel_id)
        video_data = get_video_data(channel_id)
        
        if channel_data and video_data is not None:
            df = pd.DataFrame([channel_data])
            
            tab1, tab2 = st.tabs(["📊 Overall Analysis", "🎥 Video Analysis"])
            
            with tab1:
                overall_analysis(df)
            
            with tab2:
                video_analysis(video_data)
        else:
            st.error("Unable to fetch channel data.")
    else:
        st.error("Unable to find the channel ID.")


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_lottie import st_lottie
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



def overall_analysis(df):
    st.title("📊 Overall Channel Analysis")
    
    # Channel Statistics
    st.header("Channel Statistics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Channel Name", df['Channel Name'][0])
    col2.metric("Subscribers", f"{df['Subscribers'][0]:,}")
    col3.metric("Total Views", f"{df['Total Views'][0]:,}")
    col4.metric("Video Count", f"{df['Video Count'][0]:,}")

    # Performance Metrics
    st.header("Performance Metrics")
    df['Subscribers-to-Views Ratio'] = df['Subscribers'] / df['Total Views']
    df['Videos-to-Subscribers Ratio'] = df['Video Count'] / df['Subscribers']
    df['Average Views per Video'] = df['Total Views'] / df['Video Count']
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Subscribers-to-Views Ratio", f"{df['Subscribers-to-Views Ratio'][0]:.4f}")
    col2.metric("Videos-to-Subscribers Ratio", f"{df['Videos-to-Subscribers Ratio'][0]:.4f}")
    col3.metric("Average Views per Video", f"{df['Average Views per Video'][0]:,.0f}")

    # Visual Analysis
    st.header("Visual Analysis")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    sns.barplot(x=['Subscribers', 'Total Views', 'Video Count'], 
                y=[df['Subscribers'][0], df['Total Views'][0], df['Video Count'][0]], 
                ax=ax1, palette="viridis")
    ax1.set_title("Channel Metrics Comparison")
    ax1.set_ylabel("Count")
    ax1.set_yscale('log')
    
    ax2.pie([df['Subscribers'][0], df['Total Views'][0], df['Video Count'][0]],
            labels=['Subscribers', 'Total Views', 'Video Count'],
            autopct='%1.1f%%',
            startangle=140,
            colors=sns.color_palette("viridis", 3))
    ax2.set_title('Distribution of Channel Metrics')
    
    st.pyplot(fig)

    


    # Growth Projections
    st.header("🚀 Growth Projections")
    
    # Initialize session state for additional_videos if it doesn't exist
    if 'additional_videos' not in st.session_state:
        st.session_state.additional_videos = 50

    # Callback function to update session state
    def update_additional_videos():
        st.session_state.additional_videos = st.session_state.temp_additional_videos

    # Create the slider and update session state
    additional_videos = st.slider(
        "Project growth with additional videos:", 
        0, 100, 
        value=st.session_state.additional_videos,
        key="temp_additional_videos",
        on_change=update_additional_videos
    )

    # Use the session state value for calculations
    additional_videos = st.session_state.additional_videos

    # Calculate projections based on slider value
    new_video_count = df['Video Count'][0] + additional_videos
    new_views = df['Total Views'][0] + (additional_videos * df['Average Views per Video'][0])
    new_subscribers = df['Subscribers'][0] * (1 + (additional_videos / df['Video Count'][0]) * 0.1)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Projected Video Count", f"{new_video_count:,.0f}", f"+{additional_videos}")
    col2.metric("Projected Total Views", f"{new_views:,.0f}", f"+{new_views - df['Total Views'][0]:,.0f}")
    col3.metric("Projected Subscribers", f"{new_subscribers:,.0f}", f"+{new_subscribers - df['Subscribers'][0]:,.0f}")

def video_analysis(video_data):
    st.title("🎥 Video Analysis")

    # Top Videos
    st.header("Top 10 Videos by Views")
    top_videos = video_data.sort_values(by='Views', ascending=False).head(10)
    st.dataframe(top_videos)

    fig, ax = plt.subplots(figsize=(8, 8))
    sns.barplot(x='Views', y='Video Title', data=top_videos, ax=ax, palette="viridis")
    ax.set_title("Top Videos by Views")
    st.pyplot(fig)

    # Univariate Analysis
    st.header("Univariate Analysis")
    
    metrics = ['Views', 'Likes', 'Comments']
    for metric in metrics:
        st.subheader(f"Distribution of {metric}")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 6))
        
        # Histogram
        sns.histplot(video_data[metric], bins=30, kde=True, ax=ax1)
        ax1.set_title(f"Histogram of {metric}")
        ax1.set_xlabel(metric)
        ax1.set_ylabel("Frequency")
        
        # Box plot
        sns.boxplot(x=video_data[metric], ax=ax2)
        ax2.set_title(f"Box Plot of {metric}")
        ax2.set_xlabel(metric)
        
        st.pyplot(fig)
        
        # Summary statistics
        st.write(f"Summary Statistics for {metric}:")
        st.write(video_data[metric].describe())

    # Bivariate Analysis
    st.header("Bivariate Analysis")
    
    # Scatter plot matrix
    st.subheader("Scatter Plot Matrix")
    fig = sns.pairplot(video_data[metrics], height=3, aspect=1.2, plot_kws={"alpha": 0.6})
    fig.fig.suptitle("Relationships Between Views, Likes, and Comments", y=1.02)
    st.pyplot(fig)

    # Correlation heatmap
    st.subheader("Correlation Heatmap")
    corr = video_data[metrics].corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    ax.set_title("Correlation between Views, Likes, and Comments")
    st.pyplot(fig)

    # Video Engagement Analysis
    st.header("Video Engagement Analysis")
    
    # Engagement rate calculation
    video_data['Engagement Rate'] = (video_data['Likes'] + video_data['Comments']) / video_data['Views'] * 100
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.scatterplot(x='Views', y='Engagement Rate', data=video_data, ax=ax, alpha=0.6)
    ax.set_title("Views vs Engagement Rate")
    ax.set_xlabel("Views")
    ax.set_ylabel("Engagement Rate (%)")
    st.pyplot(fig)
    
    # Top 10 videos by engagement rate
    st.subheader("Top 10 Videos by Engagement Rate")
    top_engagement = video_data.sort_values(by='Engagement Rate', ascending=False).head(10)
    st.dataframe(top_engagement[['Video Title', 'Views', 'Likes', 'Comments', 'Engagement Rate']])

if __name__ == "__main__":
    main()