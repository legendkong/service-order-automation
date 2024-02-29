import json
from gen_ai_hub.proxy import GenAIHubProxyClient
from dotenv import load_dotenv

load_dotenv()

gen_ai_hub_proxy_client = GenAIHubProxyClient()
from gen_ai_hub.proxy.native.openai import OpenAI

def process_email_content(combined_message, email_summary, image_description):
    # Load the example JSON structure
    with open('serviceOrder.json', 'r') as file:
        example_json = json.load(file)
        
    # Convert the example JSON to a string and prepare it for the prompt
    example_json_str = json.dumps(example_json, indent=2)
    prompt = f'''Given the email content:\n{combined_message}\n\nExtract the necessary information and format it into the following JSON structure, 
                filling in the details in JSON accordingly:\n{example_json_str}\n\nEnsure the extracted values and dates accurately match the email's content. 
                The RequestedServiceStartDateTime, RequestedServiceEndDateTime, ServiceOrderDescription, ServiceReferenceProduct, and both LongText fields are mandatory to fill it.
                The ServiceOrderDescription field must be limited to 30 characters, including white space and punctuations. 
                The format of the date should be YYYY-MM-DDT00:00:00Z format, for example: 2024-03-20T12:31:00Z. 
                If no date is extracted, use 2024-03-27T12:31:00Z.
                For the ServiceReferenceProduct, only return either APJPIL202309050706 if it is a chainsaw, or APJPIL202309050605 if it is a shear. If not, default to APJPIL202309050605.
                For the LongText field with LongTextID of 'S001', extract the information from: {email_summary}.
                For the LongText field with LongTextID of 'S002', directly copy and paste from: {image_description}.
                For the LongText field with LongTextID of 'S003', directly copy and paste from: {combined_message}.
                The response must be a JSON structure in the following format, with the neccessary fields filled in:\n{example_json_str}
                Please give the response in a proper, pure JSON format as it will be passed into an API body.'''
                
                #   There should be no nextline characters in the JSON response.
                
                
                
    response = OpenAI(proxy_client=gen_ai_hub_proxy_client).chat.completions.create(
        model="gpt-4-32k",
        messages=[
            {"role": "system", "content": f'''You are a helpful assistant designed to output JSON in the following format: {example_json_str}.'''},
            {"role": "user", "content": prompt}
        ],
    )
    print(response.choices[0].message.content)
    structured_json_response = response.choices[0].message.content
    
    # Convert the string response to JSON if necessary
    try:
        structured_json = json.loads(structured_json_response)
        return structured_json
    except json.JSONDecodeError:
        # Handle cases where the response is not in JSON format
        print("Error: Response could not be converted to JSON.")
        return None