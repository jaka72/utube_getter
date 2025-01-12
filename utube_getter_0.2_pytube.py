import ssl
import re
import certifi
import urllib.request
import sys
from pytube import YouTube
import subprocess
import os
import glob
import webvtt

### This is a PYTUBE VERSION ##########################################

class Colors:
    PUR = '\033[95m'
    BLU = '\033[94m'
    GRN = '\033[92m'
    YEL = '\033[93m'
    RED = '\033[91m'
    RES = '\033[0m'

PUR = Colors.PUR
BLU = Colors.BLU
GRN = Colors.GRN
YEL = Colors.YEL
RED = Colors.RED
RES = Colors.RES

download_folder = "/Users/jmb/Desktop/projects/utube_getter/results/"

ssl_context = ssl.create_default_context(cafile=certifi.where())
urllib.request.urlopen("https://example.com", context=ssl_context)

if len(sys.argv) < 2:
    print('Usage: python script_name.py "URL"')
    sys.exit(1)

video_url = sys.argv[1]
print("URL passed to Pytube:", video_url)

yt = YouTube(video_url)

def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "", title)

original_title = yt.title
new_title = sanitize_filename(original_title).replace(" ", "_")

print(PUR + "\n*** WELCOME TO JAKA'S UTUBE GETTER! ***\n")
print(BLU + "Chosen video: " + RES, new_title)
print(BLU + "Choose download option:" + RES)
print("   a) Audio only")
print("   b) Lowest resolution")
print("   c) Highest resolution")
print("   d) Default resolution (720p)")
print("   e) Subtitles only")
print(BLU + "Enter your choice: " + RES)
choice = input("").strip().lower()

choice_subs = 'n'
if choice != 'e' and choice != 'a':
    print(BLU + "Do you also want subtitles? (y/n)" + RES)
    choice_subs = input("").strip().lower()

stream = None
print(BLU + '... Checking ...')

try:
    if choice == 'a':
        stream = yt.streams.filter(only_audio=True).order_by('bitrate').desc().first()
        new_title += "_audio.mp4"
    elif choice == 'b':
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').asc().first()
        new_title += "_" + stream.resolution + '.mp4'
    elif choice == 'c':
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        new_title += "_" + stream.resolution + '.mp4'
    elif choice == 'd':
        stream = yt.streams.filter(res="720p", progressive=True).first()
        new_title += "_720p.mp4"
        if not stream:
            print(f"No stream available at '720p' resolution. Falling back to highest resolution.")
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    elif choice == 'e':
        pass
    else:
        print("Invalid choice.")
        sys.exit(1)

    if choice != 'e':
        if stream:
            print(BLU + '... Downloading: '  + RES, new_title)
            stream.download(filename=new_title, output_path=download_folder)
            print(GRN + 'Download complete' + RES)
        else:
            print(RED + "No stream available" + RES)
            sys.exit(1)

except Exception as e:
    print(RED + f"An error occurred during stream selection or download: {e}" + RES)
    sys.exit(1)



def download_utube_captions(video_url, title, output_directory):
    print("Start download_utube_captions()")
    try:
        output_path = os.path.join(output_directory, f"{title}.%(ext)s")
        command = [
            'yt-dlp',
            '--write-auto-sub',
            '--sub-lang', 'en',
            '--skip-download',
            '--output', output_path,
            video_url
        ]
        print("   Video Details:\n", command.stdout)
        subprocess.run(command, text=True, capture_output=True, check=True)
        vtt_files = glob.glob(os.path.join(output_directory, '*.vtt'))
        if vtt_files:
            return vtt_files[0]
        return None
    except subprocess.CalledProcessError as e:
        print("   Error fetching video details:", e.stderr)



def convert_vtt_to_srt(vtt_file_path):
    vtt = webvtt.read(vtt_file_path)
    srt_content = ""
    for i, caption in enumerate(vtt):
        srt_content += f"{i+1}\n{caption.start} --> {caption.end}\n{caption.text}\n\n"
    return srt_content


def write_srt_content_to_file(srt_content, output_filename):
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(srt_content)
    print(f"SRT file has been saved to {output_filename}")


def extract_text_from_srt(srt_file_path, output_filename):
    with open(srt_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    text_content = []
    last_line = None
    collect_text = False

    for line in lines:
        stripped_line = line.strip()
        
        if stripped_line.isdigit():
            collect_text = False
        elif "-->" in stripped_line:
            collect_text = True
        elif stripped_line == '':
            collect_text = False
        elif collect_text:
            if stripped_line != last_line:
                text_content.append(stripped_line)
                last_line = stripped_line

    pure_text = ' '.join(text_content)
    
    with open(output_filename, 'w', encoding='utf-8') as output_file:
        output_file.write(pure_text)

    print(f"Pure text has been saved to {output_filename}")


if choice == 'e' or choice_subs == 'y':
    print(BLU + 'Downloading subtitles ...' + RES)
    vtt_file_path = download_utube_captions(video_url, new_title, download_folder)
    if vtt_file_path:
        srt_content = convert_vtt_to_srt(vtt_file_path)
        try:
            write_srt_content_to_file(srt_content, new_title + ".srt")
            print(GRN + "Conversion successful." + RES)
            os.remove(vtt_file_path)
            print(GRN + f"Deleted the original VTT file: {vtt_file_path}" + RES)
        except IOError as e:
            print(f"An error occurred while writing to the file: {e}")
    else:
        print("Failed to download subtitles.")




if choice == 'a' or choice == 'e':
    srt_file_path = new_title + '.srt'
    output_filename = new_title + '.txt'
    if os.path.exists(srt_file_path):
        extract_text_from_srt(srt_file_path, output_filename)
        os.remove(srt_file_path)
    else:
        print("No SRT file found to extract text.")
