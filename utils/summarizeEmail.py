# Function to summarize given email content.
from dotenv import load_dotenv
load_dotenv()

from gen_ai_hub.proxy import GenAIHubProxyClient
gen_ai_hub_proxy_client = GenAIHubProxyClient()
from gen_ai_hub.proxy.native.openai import OpenAI

def summarize_email(combined_message):
    prompt = f'''Summarize the following email content, meant as a descriptive note to be attached for a service order:\n\n{combined_message}. 
                It should go something like: 'The customer has requested a service order for the following issue: XXXX... The customer mentioned that.... The customer has also attached images....'''
    
    response = OpenAI(proxy_client=gen_ai_hub_proxy_client).chat.completions.create(
        model="gpt-4-32k",
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to summarize email content and convert it into a descriptive note meant for a service order."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract the summary from the response
    summary = response.choices[0].message.content
    
    return summary
