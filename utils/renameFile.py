import base64
from ollama_aicore import Ollama
from dotenv import load_dotenv

load_dotenv()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_name(image_path, email_context):
    base64_image = encode_image(image_path)

    # Initialize the LLM class with the model and other parameters
    ollama = Ollama(
        model="llava:13b-v1.6",
        temperature=0,
        images=[base64_image],  # Pass the base64-encoded image as a list
    )

    response = ollama(f"The purpose of this image attached in an email sent by a customer for a service order request. This is the context of the email: {email_context}. Based on this image, give a suitable name for the image appended with the customer name extracted from the email, for example: 'BrokenMotorcycleSeat_JonathanKong', so that the user can save it in the system and easily identify it. Do not output any other information, I just want the result to be below 40 characters, which is the single suitable file name.")
    
    # Check if the response is valid and not empty
    if response and len(response.strip()) > 0:
        return response
    else:
        return "Failed to get image description"
