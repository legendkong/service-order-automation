from dotenv import load_dotenv
load_dotenv()
from ollama_aicore import Ollama
import base64

# Function to encode an image file to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image file
image_path = "C:\\temp\\serviceOrderImages\\aaaaabccs.jpg"  
image_base64 = encode_image_to_base64(image_path)

# Initialize the LLM class with the model and other parameters
ollama = Ollama(
    model="llava:13b-v1.6",
    temperature=0,
    images=[image_base64],  # Pass the base64-encoded image as a list
)

response = ollama("The purpose of this image attached in an email sent by a customer for a service order request. Based on this image, give a suitable name for the image file, for example: 'BrokenMotorcycleSeat', so that the user can save it in the system and easily identify it. Do not output any other information, I just want the result to be below 20 characters, which is the single suitable file name.")

# response = llm.generate(
#     prompts=["The purpose of this image attached in an email sent by a customer for a service order request. This is the context of the email: {email_context}. Based on this, give a suitable name for the image appended with the customer name, for example: 'BrokenMotorcycleSeat_JonathanKong', so that the user can save it in the system and easily identify it. Do not output any other information."]
# )
print(response)

# for gen in response.generations:
#     print (gen[0].text)

