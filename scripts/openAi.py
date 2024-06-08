import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenAI API key from the environment
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("No OPENAI_API_KEY found in .env file")

openai.api_key = openai_api_key

def generate_response(prompt):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

if __name__ == "__main__":
    prompt = "Once upon a time"
    response = generate_response(prompt)
    print("Prompt:", prompt)
    print("Response:", response)
