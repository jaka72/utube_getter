import subprocess
import os
import sys
import re
import webvtt

class Colors:
    PUR = '\033[95m'  # Purple
    BLU = '\033[94m'  # Blue
    GRN = '\033[92m'  # Green
    YEL = '\033[93m'  # Yellow
    RED = '\033[91m'  # Red
    RES = '\033[0m'   # Reset to default color

PUR = Colors.PUR
BLU = Colors.BLU
GRN = Colors.GRN
YEL = Colors.YEL
RED = Colors.RED
RES = Colors.RES

# Sanitize filenames
def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "_")

# Set the download folder
download_folder = "/Users/jmb/Desktop/projects/utube_getter/results"
os.makedirs(download_folder, exist_ok=True)

# Get video URL from command-line arguments
if len(sys.argv) < 2:
    print('Usage: python script_name.py "URL"')
    sys.exit(1)

video_url = sys.argv[1]
print("URL passed to yt-dlp:", video_url)

# Fetch video metadata using yt-dlp
try:
    print(BLU + "Fetching video metadata..." + RES)
    result = subprocess.run(
        [
            "yt-dlp",
            "--get-title",
            "--get-url",
            "--get-id",
            "--get-filename",
            video_url
        ],
        text=True,
        capture_output=True,
        check=True
    )
    metadata = result.stdout.split("\n")
    original_title = metadata[0]  # First line is the title
    new_title = sanitize_filename(original_title)
    print(BLU + "Chosen video: " + RES, new_title)
except subprocess.CalledProcessError as e:
    print(RED + "Error fetching video metadata:" + RES, e.stderr)
    sys.exit(1)

# Prompt user for download choice
print(PUR + "\n*** WELCOME TO JAKA'S UTUBE GETTER! ***\n" + RES)
print(BLU + "Choose download option:" + RES)
print("   a) Audio only")
print("   b) Lowest resolution")
print("   c) Highest resolution")
print("   d) Default resolution (720p)")
print("   e) Subtitles only")
choice = input(BLU + "Enter your choice: " + RES).strip().lower()

choice_subs = 'n'
if choice != 'e' and choice != 'a':
    choice_subs = input(BLU + "Do you also want subtitles? (y/n): " + RES).strip().lower()

# Build yt-dlp command
download_command = ["yt-dlp", "--output", f"{download_folder}/{new_title}.%(ext)s", video_url]

if choice == 'a':
    download_command += ["--format", "bestaudio"]
    new_title += "_audio"
elif choice == 'b':
    download_command += ["--format", "worst[ext=mp4]"]
    new_title += "_lowest"
elif choice == 'c':
    download_command += ["--format", "best[ext=mp4]"]
    new_title += "_highest"
elif choice == 'd':
    download_command += ["--format", "best[height<=720][ext=mp4]"]
    new_title += "_720p"
elif choice == 'e':
    download_command += ["--write-auto-sub", "--skip-download", "--sub-lang", "en"]
    #new_title += "_subtitles"
else:
    print(RED + "Invalid choice." + RES)
    sys.exit(1)

# Include subtitles if requested
if choice_subs == 'y' and choice != 'e':
    download_command += ["--write-auto-sub", "--sub-lang", "en"]

# Execute yt-dlp command
try:
    print(BLU + f"Downloading {choice} option..." + RES)
    subprocess.run(download_command, check=True)
    print(GRN + "Download complete!" + RES)
except subprocess.CalledProcessError as e:
    print(RED + "Error during download:" + RES, e.stderr)


# Subtitle conversion (if needed)
if choice == 'e' or choice_subs == 'y':
    vtt_file = os.path.join(download_folder, f"{new_title}.en.vtt")
    # srt_file = os.path.join(download_folder, f"{new_title}.srt")
    # print(BLU + "vtt_file:)" + vtt_file)
    # if os.path.exists(vtt_file):
    #     print(BLU + "B)")
    #     try:
    #         print(BLU + "Converting subtitles from VTT to SRT..." + RES)
    #         with open(vtt_file, "r", encoding="utf-8") as vtt, open(srt_file, "w", encoding="utf-8") as srt:
    #             counter = 1
    #             print(BLU + "C)")
    #             for line in vtt:
    #                 # Remove WEBVTT header and convert timestamps
    #                 if line.strip() == "WEBVTT" or line.strip() == "":
    #                     continue
    #                 if "-->" in line:
    #                     srt.write(f"{counter}\n")
    #                     counter += 1
    #                     srt.write(line)
    #                 else:
    #                     srt.write(line)
    #             print(GRN + f"Subtitles saved to {srt_file}" + RES)
    #         os.remove(vtt_file)
    #     except Exception as e:
    #         print(RED + f"Error converting subtitles: {e}" + RES)
    # else:
    #     print(RED + "No subtitles file found to convert." + RES)




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




if vtt_file:
    srt_content = convert_vtt_to_srt(vtt_file)
    try:
        write_srt_content_to_file(srt_content, new_title + ".srt")
        print(GRN + "Conversion successful." + RES)
        os.remove(vtt_file)
        print(GRN + f"Deleted the original VTT file: {vtt_file}" + RES)
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")
else:
    print("Failed to download subtitles.")



if choice == 'a' or choice == 'e':
    srt_file_path = new_title + '.srt'
    output_filename = download_folder + "/" + new_title + '.txt'
    if os.path.exists(srt_file_path):
        extract_text_from_srt(srt_file_path, output_filename)
        os.remove(srt_file_path)
    else:
        print("No SRT file found to extract text.")
