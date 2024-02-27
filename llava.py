from dotenv import load_dotenv
load_dotenv()
from ollama_aicore import ChatOllama, Ollama
import base64

# Function to encode an image file to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image file
image_path = "C:\\temp\\serviceOrderImages\\0987865.jpg"  
image_base64 = encode_image_to_base64(image_path)

# Initialize the LLM class with the model and other parameters
llm = Ollama(
    model="llava:13b-v1.6",
    temperature=0,
    images=[image_base64],  # Pass the base64-encoded image as a list
)

response = llm.generate(
    prompts=["The customer sent in this image in an email as an attachment, requesting for a service order. It is highly likely damaged in one way or another. Explain what is wrong with the equipment in the image."]
)

for gen in response.generations:
    print (gen[0].text)

