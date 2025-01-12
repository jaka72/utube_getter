import argparse
import openai

def main():
    parser = argparse.ArgumentParser(description="Process text with OpenAI GPT-3")
    parser.add_argument("--input", required=True, help="Path to the input text file")
    parser.add_argument("--output", required=True, help="Path to the output text file")
    parser.add_argument("--title", required=True, help="Title to be added at the top of the output text")
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as file:
        input_text = file.read()

    # Call OpenAI API to process the text
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=input_text,
        max_tokens=1024
    )

    processed_text = response.choices[0].text.strip()

    # Add the title at the top of the processed text
    final_text = f"{args.title}\n\n{processed_text}"

    with open(args.output, 'w', encoding='utf-8') as file:
        file.write(final_text)

    print(f"Processed text has been saved to {args.output}")

# Remove the if __name__ == "__main__": block
# if __name__ == "__main__":
#     main()
