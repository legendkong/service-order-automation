import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os
from utils.visionImages import get_image_description
from utils.renameFile import get_image_name
import time

load_dotenv()
SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")

# Define a session to reuse HTTP connections and keep cookies
session = requests.Session()
session.auth = HTTPBasicAuth({SAP_USERNAME}, {SAP_PASSWORD})

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
def find_most_recent_image(directory, extension="jpg"):
    """
    Finds the most recent image file in the specified directory with the given extension.
    
    Parameters:
    - directory: The directory to search in.
    - extension: The file extension to look for. Defaults to "jpg".
    
    Returns:
    - The path to the most recent image file found.
    - The filename (slug) of the most recent image file found.
    """
    # Create a list of files with the given extension
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith("." + extension)]
    if not files:
        return None, None  # Return None if no files are found
    
    # Find the most recent file
    latest_file = max(files, key=os.path.getmtime)
    slug = os.path.basename(latest_file)
    return latest_file, slug

# uploads the most recent image
def upload_recent_image():
    directory = "C:\\temp\\serviceOrderImages"
    file_path, original_slug = find_most_recent_image(directory)

    if file_path and original_slug:
        # Get a suitable name for the image from GPT-4
        imageName = get_image_name(file_path).strip()
        print(f"\nSuitable name for the image: {imageName}")
        # Prepare a new file name; ensure it's filesystem-safe
        new_slug = imageName.replace(" ", "_") + ".jpg" 
        new_file_path = os.path.join(directory, new_slug)

        # Rename the image file
        os.rename(file_path, new_file_path)
        print(f"File renamed to: {new_slug}")
        
        # Now that the file has been renamed, we should use new_file_path to get the description
        description = get_image_description(new_file_path)
        print(f"\nThis is the description of the attachment: {description}")
        
        # Fetch the CSRF token and cookies
        csrf_token, cookies = fetch_csrf_token()

        # Fetch the most recent service order number
        recent_serviceorder_number = fetch_most_recent_serviceorder_number()

        if recent_serviceorder_number:
            # Now call upload_serviceorder_image with the new file path and slug
            upload_serviceorder_image(csrf_token, cookies, new_file_path, new_slug, recent_serviceorder_number)
            return True
        else:
            print("Failed to fetch the most recent service order number.")
            return False
    else:
        print("No recent image file found to upload.")
        return False


def fetch_most_recent_serviceorder_number():
    
    time.sleep(10)
    
    url = ("https://my300181-api.s4hana.ondemand.com/sap/opu/odata/sap/API_SERVICE_ORDER_SRV/A_ServiceOrder?$orderby=ServiceOrder desc&$top=1")
    headers = {'Accept': 'application/json'}
    response = session.get(url, auth=session.auth, headers=headers)

    if response.status_code == 200:
        try:
            serviceorder_data = response.json()
            if serviceorder_data['d']['results']:
                recent_serviceorder = serviceorder_data['d']['results'][0]['ServiceOrder']
                print("This is the recent service order number: " + recent_serviceorder)
                return recent_serviceorder
            else:
                print("No service order found.")
                return None
        except ValueError as e:
            print("Failed to parse JSON response", e)
            return None
    else:
        print("Failed to fetch service order", response.status_code, response.text)
        return None


if __name__ == '__main__':
    directory = "C:\\temp\\serviceOrderImages"
    file_path, new_slug = find_most_recent_image(directory)
    
    if file_path and new_slug:
        csrf_token, cookies = fetch_csrf_token()
        recent_serviceorder_number = fetch_most_recent_serviceorder_number()  # Fetch the service order number
        if recent_serviceorder_number:
            upload_serviceorder_image(csrf_token, cookies, file_path, new_slug, recent_serviceorder_number)  # Pass the service order number
        else:
            print("Failed to fetch the most recent service order number.")
    else:
        print("No recent image file found to upload.")
