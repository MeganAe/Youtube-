import streamlit as st
import pytube
from pytube import YouTube
import os
import time

st.set_page_config(
    page_title="YouTube Video Downloader",
    page_icon="🎥",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
    }
    .download-info {
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🎥 YouTube Video Downloader")
st.markdown("Enter a YouTube URL to download the video")

# URL input
url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

def format_size(bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} GB"

def download_video(yt, stream, progress_bar, status_text):
    """Download the video with progress tracking"""
    total_size = stream.filesize
    filename = stream.default_filename
    download_path = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_path, exist_ok=True)
    
    def progress_callback(chunk, file_handle, bytes_remaining):
        current = total_size - bytes_remaining
        progress = current / total_size
        progress_bar.progress(progress)
        status_text.text(f"Downloading... {format_size(current)}/{format_size(total_size)}")
    
    yt.register_on_progress_callback(progress_callback)
    stream.download(output_path=download_path)
    return os.path.join(download_path, filename)

if url:
    try:
        # Create YouTube object
        yt = YouTube(url)
        
        # Display video information
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(yt.thumbnail_url, use_column_width=True)
        
        with col2:
            st.subheader(yt.title)
            st.write(f"Length: {yt.length//60}:{yt.length%60:02d} minutes")
            st.write(f"Views: {yt.views:,}")
            st.write(f"Author: {yt.author}")
        
        # Get available streams
        streams = yt.streams.filter(progressive=True)
        quality_options = {f"{s.resolution} ({format_size(s.filesize)})": s for s in streams}
        
        # Quality selection
        selected_quality = st.selectbox(
            "Select video quality",
            options=list(quality_options.keys())
        )
        
        if st.button("Download Video"):
            selected_stream = quality_options[selected_quality]
            
            # Create progress bar and status text
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Download the video
                file_path = download_video(yt, selected_stream, progress_bar, status_text)
                
                # Show success message
                st.success("Download completed!")
                
                # Create download link
                with open(file_path, 'rb') as f:
                    st.download_button(
                        label="Save Video",
                        data=f,
                        file_name=os.path.basename(file_path),
                        mime="video/mp4"
                    )
                
            except Exception as e:
                st.error(f"An error occurred during download: {str(e)}")
            
            finally:
                # Clean up progress bar
                progress_bar.empty()
                status_text.empty()
                
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.warning("Please enter a valid YouTube URL")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        ⚠️ Note: This tool is for educational purposes only. 
        Please respect YouTube's terms of service and copyright laws.
    </div>
""", unsafe_allow_html=True)
