import ssl
import re
import certifi
import urllib.request
import sys # To be able to pass arguments to .py
from pytube import YouTube
import subprocess	# To use with youtube-dl for downloading auto-generated subtitles
from io import StringIO

class Colors:
	PUR = '\033[95m'  # Purple
	BLU = '\033[94m'  # Blue
	GRN = '\033[92m'  # Green
	YEL = '\033[93m'  # Yellow
	RED = '\033[91m'  # Red
	RES = '\033[0m'  # Reset to default color

PUR = Colors.PUR
BLU = Colors.BLU
GRN = Colors.GRN
YEL = Colors.YEL
RED = Colors.RED
RES = Colors.RES

# EXPLANATIONS ###################################################################
#
#   It works with: python3 exec_name.py "utube_url"
#
#
#	Filtering Streams:
#	The streams.filter() method is used to select streams that match specific criteria. The res 
#	parameter is used to specify the resolution (e.g., '720p', '1080p'). The progressive=True 
#	parameter is used to filter for streams that contain both video and audio. If you only want #	video or audio, you can adjust this parameter accordingly.
#
#	Selecting the Stream:
#	The .first() method is used to select the first stream that matches the filters. If no such 
#	stream exists, it will return None.
#
#	Must have installed in terminal:
#		pip3 install certifi
#			or run:   /Applications/Python\ 3.12/Install\ Certificates.command 
#	Python must verify the SSL certificate of the server it's trying to connect to: YouTube.
#	The system does not automatically trust the root certificates.
#	Python installations from python.org include a script to install the necessary root 
#	certificates into the Python environment. This command installs a set of root certificates 
#	for your Python environment, which should resolve the SSL certificate verification issues.
#
#	pip install youtube-dl    --> for auto-generated subtitles
#   or    pip install -U yt-dlp   ---> this one works
#
#	pip install webvtt-py     --> Could be that it is also needed to convert .vtt to .srt
#
#   To update the pytube:
#       pip install --upgrade pytube yt-dlp
#
#
####################################################################################

# Test if certificate works
# try:
#     response = urllib.request.urlopen('https://www.google.com')
#     print('Success:', response.status)
# except Exception as e:
#     print('Error:', e)

download_folder = "/Users/jmb/Desktop/projects/utube_getter" 

ssl_context = ssl.create_default_context(cafile=certifi.where())

# When creating an HTTPS connection, you can pass this context
urllib.request.urlopen("https://example.com", context=ssl_context)


if len(sys.argv) < 2:
	print('Usage: python script_name.py <URL>')
	sys.exit(1)

video_url = sys.argv[1]
print("URL passed to Pytube:", video_url)
# video_url = 'https://www.youtube.com/watch?v=mMHlJlo89I0'
yt = YouTube(video_url)


# Remove spec. chars from the filename
def sanitize_filename(title):
	return re.sub(r'[\\/*?:"<>|]', "", title)  # Remove disallowed characters in filenames

original_title = yt.title
new_title = original_title.replace(" ", "_")
new_title = sanitize_filename(new_title)



# Prompt choices:
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
if choice != 'e' and choice != 'a':
	print(BLU + "Do you also want subtitles? (y/n)" + RES)
	choice_subs = input("").strip().lower()

stream = None
print(BLU + '... Checking ...')

if choice == 'a':
	stream = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('bitrate').desc().first()
	new_title = new_title + "_" + "_audio.mp4"
	# audio_streams = yt.streams.filter(only_audio=True).order_by('bitrate').desc()
	# for stream in audio_streams:
	# 	print(stream)
elif choice == 'b':
	stream = yt.streams.get_lowest_resolution()
	new_title = new_title + "_" + stream.resolution + '.mp4'
elif choice == 'c':
	stream = yt.streams.get_highest_resolution()
	new_title = new_title + "_" + stream.resolution + '.mp4'
elif choice == 'd':
	default_resolution = '720p'
	stream = yt.streams.filter(res=default_resolution, progressive=True).first()
	new_title = new_title + "_720p" + '.mp4'
	if not stream:
		print(f"No stream available at '{default_resolution}' resolution. Falling back to highest resolution.")
		stream = yt.streams.get_highest_resolution()
elif choice == 'e':
	print("")	
else:
	print("Invalid choice.")
	sys.exit(1)

if choice != 'e':
	if stream:
		print(BLU + '... Downloading: '  + RES, new_title)
		try:
			stream.download(filename=new_title, output_path=download_folder)
			print(GRN + 'Download complete' + RES)
		except Exception as e:
				print(GRN + f"Error during download {e}" + RES)
	else:
		print(RED + "No stream available" + RES)
		sys.exit(1)


print("Available captions:")
captions = yt.captions
if captions:
	# Access captions using dictionary syntax
	if 'en' in captions:
		# Generate and print English captions
		eng_captions = captions['en']
		print("English captions found:", eng_captions.name)
		print(eng_captions.generate_srt_captions())
	else:
		print("English captions not available.")
else:
	print("No captions available for this video.")




# THIS WORKS IF THERE ARE EXISTING SUBTITLES, BUT NOT FOR AUTO-GENERATED SUBTITLES
# if choice == 'e' or choice_subs == 'y':
# 	print(BLU + 'Downloading subtitles ...' + RES)
# 	captions = yt.captions.get('en')
# 	if captions:
# 		subtitles = captions.generate_srt_captions()
# 		with open(f"{new_title}_subtitles.srt", "w", encoding="utf-8") as file:
# 			file.write(subtitles)
# 			print(GRN + 'Done!' + RES)
# 	else:
# 		print(RED + "No subtitles available for the specified language." + RES)


### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###   


# THIS IS ONLY FOR AUTO-GENERATED SUBTITLES, IF THEY EXIST (NOT FOR THE REAL SUBTITLES)
import glob
import os
def download_utube_captions(video_url, title, output_directory):
	output_path = os.path.join(output_directory, f"{title}.%(ext)s")
	command = [
		'yt-dlp',
		'--write-auto-sub',
		'--sub-lang', 'en',
		'--skip-download',
		'--output', output_path,  # Save the file with the video title
		video_url
	]
	# Run the command without capturing output, since the file is saved directly
	subprocess.run(command, text=True)
	vtt_files = glob.glob(os.path.join(output_directory, '*.vtt'))
	if vtt_files:
		return vtt_files[0]
	else:
		return None

# Not needed
# Clean the .vtt file (to be able to convert to .srt)
# def clean_vtt_headers(vtt_content):
# 	# Remove all <c> tags and other non-standard VTT tags
# 	cleaned_content = re.sub(r'<[^>]+>', '', vtt_content)
# 	# Remove extra metadata lines that are not needed
# 	cleaned_content = re.sub(r'Kind:.*\n', '', cleaned_content)
# 	cleaned_content = re.sub(r'Language:.*\n', '', cleaned_content)
# 	return cleaned_content



if choice == 'a' or choice == 'e':
	print(BLU + 'Downloading subtitles ...' + RES)
	vtt_file_path = download_utube_captions(video_url, new_title, "./")
	# os.rename(vtt_file_path, 'vvt-orig.vtt')
	# clean_vtt_headers(vtt_file_path)	# todo: not needed


### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###   

import webvtt
def convert_vtt_to_srt(vtt_file_path):
	vtt = webvtt.read(vtt_file_path)
	srt_content = ""
	for i, caption in enumerate(vtt):
		srt_content += f"{i+1}\n{caption.start} --> {caption.end}\n{caption.text}\n\n"
	return srt_content



def write_srt_content_to_file(srt_content, output_filename):
	# """
	# Writes the given SRT content to a file with the specified filename.

	# :param srt_content: The string containing the SRT formatted subtitles.
	# :param output_filename: The filename for the output SRT file.
	# """
	# Open the file in write mode
	with open(output_filename, 'w', encoding='utf-8') as file:
		file.write(srt_content)  # Write the SRT content to the file
		print(f"SRT file has been saved to {output_filename}")



# Convert .vtt to .srt
if vtt_file_path: # This was causing error when downloading audio only
    srt_content = convert_vtt_to_srt(vtt_file_path)
    try:
        # You can now write srt_content to a file or process it further
        write_srt_content_to_file(srt_content, new_title + ".srt")
        print(GRN + "Conversion successful." + RES)
        os.remove(vtt_file_path)
        print(GRN + f"Deleted the original VTT file: {vtt_file_path}" + RES)
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")
else:
    print("Failed to download subtitles.")


### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###   

def extract_text_from_srt(srt_file_path, output_filename):
    with open(srt_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    text_content = []
    last_line = None  # Keep track of the last added line to avoid duplicates
    collect_text = False

    for line in lines:
        stripped_line = line.strip()
        
        if stripped_line.isdigit():
            collect_text = False  # Reset on sequence number
        elif "-->" in stripped_line:
            collect_text = True   # Start collecting after timestamp
        elif stripped_line == '':
            collect_text = False  # Stop collecting on empty lines
        elif collect_text:
            # Add line only if it is not a duplicate of the last added line
            if stripped_line != last_line:
                text_content.append(stripped_line)
                last_line = stripped_line

    # Join all the collected text into a single string, separated by spaces or newlines
    pure_text = ' '.join(text_content)
    
    # Save the extracted text to a new file
    with open(output_filename, 'w', encoding='utf-8') as output_file:
        output_file.write(pure_text)

    print(f"Pure text has been saved to {output_filename}")


# Extract pure text and delete .srt
srt_file_path = new_title + '.srt'
output_filename = new_title + '.txt'
extract_text_from_srt(srt_file_path, output_filename) # This was causing error when downloading audio only

os.remove(srt_file_path)
