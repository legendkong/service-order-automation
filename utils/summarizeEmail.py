# Function to summarize given email content.

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI()

def summarize_email(combined_message):
    prompt = f'''Summarize the following email content, meant as a descriptive note to be attached for a service order:\n\n{combined_message}. 
                It should go something like: 'The customer has requested a service order for the following issue: XXXX... The customer mentioned that.... The customer has also attached images....'''
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to summarize email content and convert it into a descriptive note meant for a service order."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract the summary from the response
    summary = response.choices[0].message.content
    
    return summary
