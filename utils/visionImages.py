# Function to get image description using Llava 13b.
from dotenv import load_dotenv
from ollama_aicore import Ollama
import base64

load_dotenv()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_description(image_path, email_context):
    base64_image = encode_image(image_path)

    ollama = Ollama(
        model="llava:13b-v1.6",
        temperature=0,
        images=[base64_image],  # Pass the base64-encoded image as a list
    )

    response = ollama(f"The customer sent in this image in an email as an attachment requesting for a service order. There can be multiple other attachments in the email. This is the context of the email: {email_context}. The equipment in the image is highly likely damaged in one way or another. Explain what is wrong specifically with the equipment in the image, without much referencing from the email.")

    # Check if the response is valid and not empty
    if response and len(response.strip()) > 0:
        return response
    else:
        return "Failed to get image description"