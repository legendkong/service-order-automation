import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os
from utils.visionImages import get_image_description
from utils.renameFile import get_image_name
import time
from datetime import datetime

load_dotenv()
SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")

# Define a session to reuse HTTP connections and keep cookies
session = requests.Session()
session.auth = HTTPBasicAuth(SAP_USERNAME, SAP_PASSWORD)

# to get csrf token
def fetch_csrf_token():
    token_fetch_url = "https://my300181-api.s4hana.ondemand.com/sap/opu/odata/sap/API_CV_ATTACHMENT_SRV/"
    headers = {"X-CSRF-Token": "Fetch"}
    response = session.get(token_fetch_url, headers=headers)
    csrf_token = response.headers.get("X-CSRF-Token")
    # Also capture and reuse any cookies sent by the server
    return csrf_token, response.cookies

def upload_serviceorder_image(csrf_token, cookies, file_path, slug, linked_sap_object_key):
    url = "https://my300181-api.s4hana.ondemand.com/sap/opu/odata/sap/API_CV_ATTACHMENT_SRV/AttachmentContentSet"
    headers = {
        "Content-Type": "image/jpeg",
        "Slug": slug,  # Filename used in the Slug header
        "LinkedSAPObjectKey": linked_sap_object_key,  # Adjust if this can also be dynamic
        "BusinessObjectTypeName": "BUS2000116",  # BUS for Service Order
        "X-CSRF-Token": csrf_token,
    }
    with open(file_path, 'rb') as file:
        file_content = file.read()

    response = session.post(url, headers=headers, data=file_content, cookies=cookies)

    if response.status_code == 201:
        print("Image uploaded successfully", response.status_code)
    else:
        print("Failed to upload image", response.status_code, response.text)

  
# find the most recent image from directory
def find_most_recent_images(directory, count=1, extension="jpg"):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith("." + extension)]
    if not files:
        return []
    files.sort(key=os.path.getmtime, reverse=True)
    return files[:count]

def rename_image(file_path, email_context, timestamp):
    imageName = get_image_name(file_path, email_context).strip()
    new_slug = f"{imageName}_{timestamp}.jpg".replace(" ", "_")
    new_file_path = os.path.join(os.path.dirname(file_path), new_slug)
    os.rename(file_path, new_file_path)
    return new_file_path, new_slug

def upload_serviceorder_image(csrf_token, cookies, file_path, slug, linked_sap_object_key):
    url = "https://my300181-api.s4hana.ondemand.com/sap/opu/odata/sap/API_CV_ATTACHMENT_SRV/AttachmentContentSet"
    headers = {
        "Content-Type": "image/jpeg",
        "Slug": slug,
        "LinkedSAPObjectKey": linked_sap_object_key,
        "BusinessObjectTypeName": "BUS2000116",
        "X-CSRF-Token": csrf_token,
    }
    with open(file_path, 'rb') as file:
        file_content = file.read()
    response = session.post(url, headers=headers, data=file_content, cookies=cookies)
    if response.status_code == 201:
        print("Image uploaded successfully", response.status_code)
    else:
        print("Failed to upload image", response.status_code, response.text)
        
  
def upload_recent_images(email_context, attachments_count):
    directory = "C:\\temp\\serviceOrderImages"
    files = find_most_recent_images(directory, count=attachments_count)
    csrf_token, cookies = fetch_csrf_token()
    recent_serviceorder_number = fetch_most_recent_serviceorder_number()
    if not recent_serviceorder_number:
        print("Failed to fetch the most recent service order number.")
        return False
    
    for file_path in files:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_file_path, new_slug = rename_image(file_path, email_context, timestamp)
        # description = get_image_description(new_file_path)  # Assuming this function is defined elsewhere
        upload_serviceorder_image(csrf_token, cookies, new_file_path, new_slug, recent_serviceorder_number)
    return True


def fetch_most_recent_serviceorder_number():
    time.sleep(10)  # Consider async or a more efficient way to handle this delay
    url = "https://my300181-api.s4hana.ondemand.com/sap/opu/odata/sap/API_SERVICE_ORDER_SRV/A_ServiceOrder?$orderby=ServiceOrder desc&$top=1"
    headers = {'Accept': 'application/json'}
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        try:
            serviceorder_data = response.json()
            return serviceorder_data['d']['results'][0]['ServiceOrder'] if serviceorder_data['d']['results'] else None
        except ValueError as e:
            print("Failed to parse JSON response", e)
            return None
    else:
        print("Failed to fetch service order", response.status_code, response.text)
        return None


# if __name__ == '__main__':
#     directory = "C:\\temp\\serviceOrderImages"
#     file_path, new_slug = find_most_recent_image(directory)
    
#     if file_path and new_slug:
#         csrf_token, cookies = fetch_csrf_token()
#         recent_serviceorder_number = fetch_most_recent_serviceorder_number()  # Fetch the service order number
#         if recent_serviceorder_number:
#             upload_serviceorder_image(csrf_token, cookies, file_path, new_slug, recent_serviceorder_number)  # Pass the service order number
#         else:
#             print("Failed to fetch the most recent service order number.")
#     else:
#         print("No recent image file found to upload.")
