import tkinter as tk
from subprocess import call

def run_utube_getter():
    # Get the URL from the entry widget
    video_url = url_entry.get()
    # Call the download script with the URL as an argument
    call(['python3', 'utube_getter.py', video_url])

# Set up the main window
root = tk.Tk()
root.title("Download YouTube Video")

# Create a label and entry widget for the URL
tk.Label(root, text="Enter YouTube URL:").pack(side="top")
url_entry = tk.Entry(root, width=50)
url_entry.pack(side="top")

# Create a button to trigger the download
download_button = tk.Button(root, text="Download", command=run_utube_getter)
download_button.pack(side="top")

# Start the Tkinter event loop
root.mainloop()
