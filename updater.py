import os
import subprocess
import sys

def run_command(command):
    """Runs a shell command and prints the output."""
    try:
        result = subprocess.run(command, text=True, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}\n{e.stderr}")

# Step 1: Update `pytube` and `yt-dlp`
print("\nUpdating pytube and yt-dlp...")
run_command("pip install --upgrade pytube yt-dlp")

# Step 2: Install/Update `webvtt-py`
print("\nInstalling/Updating webvtt-py...")
run_command("pip install --upgrade webvtt-py")

# Step 3: Verify and install SSL certificates (macOS-specific)
if sys.platform == "darwin":
    print("\nInstalling SSL certificates for macOS...")
    certificates_command = "/Applications/Python\\ 3.12/Install\\ Certificates.command"
    if os.path.exists(certificates_command):
        run_command(certificates_command)
    else:
        print("Certificate installation script not found. Ensure Python was installed from python.org.")

# Step 4: Check Python and pip versions
print("\nChecking Python and pip versions...")
run_command("python --version")
run_command("pip --version")

# Step 5: Verify yt-dlp installation
print("\nVerifying yt-dlp installation...")
run_command("yt-dlp --version")

# Step 6: Create a results directory if it doesn't exist
results_dir = "/Users/jmb/Desktop/projects/utube_getter/results"
print("\nEnsuring results directory exists...")
if not os.path.exists(results_dir):
    os.makedirs(results_dir)
    print(f"Created directory: {results_dir}")
else:
    print(f"Directory already exists: {results_dir}")

# Step 7: Print summary of updates
print("\nAll updates and checks are complete. You are ready to use the YouTube script!")
