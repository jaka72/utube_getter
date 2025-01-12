from jcolors import Colors as C

import os
import openai
import argparse
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

# File paths
original_text_file = "original_text.txt"
final_output_file = "final_file.txt"

# Chunk size (in words)
chunk_size = 500


def read_next_chunk(file, chunk_size, leftover, start_index):
    """
    Reads the next chunk of text from the file, adding any leftover text from the previous chunk.
    """
    with open(file, "r") as f:
        text = f.read()

    words = text.split()

    # Calculate the range for this chunk
    chunk_words = words[start_index : start_index + chunk_size]
    chunk = leftover + " " + " ".join(chunk_words) if leftover else " ".join(chunk_words)

    # Determine the new start index for the next chunk
    new_start_index = start_index + chunk_size

    return chunk, new_start_index


def call_chatgpt_to_process(chunk):
    """
    Sends the chunk to ChatGPT and receives the processed, readable text.
    """
    response = openai.chat.completions.create(
        # model="gpt-4o-mini-2024-07-18",
        # model="gpt-3.5-turbo",
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. Your task is to add punctuation, capitalization, "
                    "and paragraphs to make text readable for humans."
                    "A paragraph shall not contain more then 180 words."
                    "After every paragraph there should be a blank line."
                    "Do not change any words, omit any sentences."
                    "Only improve readability by adding punctuation, proper capitalization, and formatting."
                    "The only thing you can add, next to punctuation, proper capitalization, and formatting, are sub-titles."
                    "Add a subtitle every 300–500 words. Break up the text into logical paragraphs that focus on specific topics."
                    "Subtitles shall have a format like this: '### sub-title'."
                    "If a section starts to feel too long or dense, consider adding another subtitle. and should reflect the content of the text."
                    "Towards the end of each text chunk, please pay attention to where the last complete sentence ends. "
                    "In your output, do not include the sentence that is cut off."
                ),
            },
            {"role": "user", "content": chunk},
        ],
    )
    return response.choices[0].message.content


def get_leftover_text(processed_chunk):
    """
    Extracts the leftover text (the cut-off sentence) from the processed chunk.
    """
    sentences = processed_chunk.split(".")  # Split by periods to find full sentences
    leftover = sentences[-1].strip()  # The last part is likely the leftover
    completed_chunk = ".".join(sentences[:-1]).strip() + "."
    return completed_chunk, leftover


def main():
    # Parse the arguments that came from the utube_getter_0.2_yt-dlt.py script
    parser = argparse.ArgumentParser(description="Process text with OpenAI GPT-3")
    parser.add_argument("--input", required=True, help="Path to the input text file")
    parser.add_argument("--output", required=True, help="Path to the output text file")
    parser.add_argument("--title", required=True, help="Title to be added at the top of the output text")
    args = parser.parse_args()

    original_text_file = args.input
    final_output_file = args.output
    title = args.title

    # Extract the title from the file path
    title = os.path.basename(title).replace('.txt', '')

    # Ensure the final output file is empty initially
    open(final_output_file, "w").close()

    # Write the title to the final output file
    with open(final_output_file, "a") as f:
        f.write(f"# {title}\n\n")

    with open(original_text_file, "r") as f:
        text = f.read()

    words = text.split()
    total_size = len(words)
    print(C.BLU + "Processing the text of", total_size, " words ..." + C.RES)

    leftover = ""  # To track the cut-off sentence
    start_index = 0  # Track the word position in the original file

    while True:
        # Read the next chunk without modifying the original file
        chunk, start_index = read_next_chunk(original_text_file, chunk_size, leftover, start_index)

        if not chunk.strip():
            break  # Stop if no text remains

        # Process the chunk using ChatGPT
        processed_chunk = call_chatgpt_to_process(chunk)

        # Extract the completed text and the new leftover sentence
        completed_chunk, leftover = get_leftover_text(processed_chunk)

        # Append the completed text to the final output file
        with open(final_output_file, "a") as f:
            f.write(completed_chunk + "\n\n")

        # Calculate progress
        processed_size = len(" ".join(chunk.split()))  # Current chunk in characters
        progress = (start_index / total_size) * 100
        print(C.GRN + f"   ... done {start_index} words:  {progress:.0f}%" + C.RES)

    # At the end, if there is any leftover text, flush it to the final output
    if leftover.strip():
        with open(final_output_file, "a") as f:
            f.write(leftover.strip() + "\n\n")

    print(C.BLU + f"Finished and saved to file: \n{final_output_file}" + C.RES)
    


if __name__ == "__main__":
    main()
