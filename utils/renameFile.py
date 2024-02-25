from openai import OpenAI
import base64
import requests
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_name(image_path, email_context):
    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"The purpose of this image attached in an email sent by a customer for a service order request. This is the context of the email: {email_context}. Based on this, give a suitable name for the image appended with the customer name, for example: 'BrokenMotorcycleSeat_JonathanKong', so that the user can save it in the system and easily identify it. Do not output any other information."                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    if response.status_code == 200:
        imageName = response.json()['choices'][0]['message']['content']
        return imageName
    else:
        return "Failed to get image name."
