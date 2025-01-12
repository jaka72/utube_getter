import ssl
import re
import certifi
import urllib.request
import sys
from pytube import YouTube
import subprocess
import os

def download_with_pytube(video_url, output_path):
    try:
        yt = YouTube(video_url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if stream:
            stream.download(output_path=output_path)
            print("Download completed with pytube.")
            return True
    except Exception as e:
        print(f"pytube failed: {e}")
        return False

def download_with_ytdlp(video_url, output_path):
    command = [
        'yt-dlp',
        '-f', 'best',
        '-o', os.path.join(output_path, '%(title)s.%(ext)s'),
        video_url
    ]
    try:
        subprocess.run(command, check=True)
        print("Download completed with yt-dlp.")
    except subprocess.CalledProcessError as e:
        print(f"yt-dlp failed: {e}")

def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "", title)

if len(sys.argv) < 2:
    print('Usage: python script_name.py "URL"')
    sys.exit(1)

video_url = sys.argv[1]
output_path = "/Users/jmb/Desktop/projects/utube_getter/results"

# Try downloading with pytube first
if not download_with_pytube(video_url, output_path):
    # If pytube fails, fall back to yt-dlp
    download_with_ytdlp(video_url, output_path)
