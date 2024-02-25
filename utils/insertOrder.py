# Function to insert service order to S/4HANA

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

load_dotenv()
SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")


def post_to_s4hana(json_data):
    # Define the URL for the CSRF token fetch and the endpoint for the POST request
    token_fetch_url = "https://my300181-api.s4hana.ondemand.com/sap/opu/odata/sap/API_SERVICE_ORDER_SRV/A_ServiceOrder"
    post_url = "https://my300181-api.s4hana.ondemand.com/sap/opu/odata/sap/API_SERVICE_ORDER_SRV/A_ServiceOrder"
    
    # Start a session
    session = requests.Session()
    session.auth = HTTPBasicAuth(SAP_USERNAME, SAP_PASSWORD)
    
    # Fetch CSRF token
    token_response = session.get(token_fetch_url, headers={"X-CSRF-Token": "Fetch"})
    csrf_token = token_response.headers.get("x-csrf-token")
    
    if not csrf_token:
        print("Failed to fetch CSRF token")
        return False
    
    # Make the POST request with the fetched CSRF token and JSON data
    headers = {
        "Content-Type": "application/json",
        "X-CSRF-Token": csrf_token,
        "Accept": "application/json"
    }
    
    post_response = session.post(post_url, headers=headers, json=json_data)
    
    if post_response.status_code == 201:
        print("Successfully posted to S/4HANA")
        return True
    else:
        print(f"Failed to post: {post_response.status_code} {post_response.text}")
        return False
