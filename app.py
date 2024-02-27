from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from utils.processEmail import process_email_content
from utils.summarizeEmail import summarize_email
from utils.insertOrder import post_to_s4hana
from utils.insertAttachments import upload_recent_images, get_image_description, find_most_recent_images

load_dotenv()

app = Flask(__name__)

@app.route('/processemail', methods=['POST'])
def process_email():
    # Parse the JSON data sent to the server
    data = request.get_json() 

    # Extract fields from the parsed JSON
    mail_sender = data.get('mailSender', 'No Sender')
    mail_subject = data.get('mailSubject', 'No Subject')
    mail_body = data.get('mailBody', 'No Body')
    mail_date_and_time = data.get('mailDateandTime', 'No Date and Time')
    attachments_count = data.get('attachmentsCount', 0)

    # Combine the fields
    combined_message = f"Sender: {mail_sender}\nSubject: {mail_subject}\nBody: {mail_body}\nDate and Time: {mail_date_and_time}"
    
    # Handling multiple images
    if attachments_count > 0:
        directory = "C:\\temp\\serviceOrderImages"
        images_paths = find_most_recent_images(directory, count=attachments_count)
        image_descriptions = []
        for image_path in images_paths:
            image_name = os.path.basename(image_path)
            image_description = get_image_description(image_path)
            image_descriptions.append(f"{image_name}: {image_description}")
        
        if attachments_count > 1:
            images_description_str = "\n".join(image_descriptions)
            fileDescription = f"Multiple images attached: \n{images_description_str}"
            modified_combined_message = f"{combined_message}\n\nMultiple images attached:\n{images_description_str}"
            # print(fileDescription)
        else:
            modified_combined_message = f"{combined_message}\n\nAttached Image Description: {image_descriptions[0]}"
            fileDescription = f"Attached Image Description: \n{image_descriptions[0]}"
            # print(fileDescription)
    else:
        print("No image file found in the directory.")
        modified_combined_message = combined_message
        
    email_summary = summarize_email(modified_combined_message)
    # Get most recent image description
    # directory = "C:\\temp\\serviceOrderImages"
    # image_path, slug = find_most_recent_image(directory)
    
    # if image_path:
    #     image_description = get_image_description(image_path)
    #     # Include the image description in the combined message or process it as needed
    #     modified_combined_message = f"{combined_message}\n\nAttached Image Description: {image_description}"
        
    #     # Proceed with summarizing the email and further processing
    #     email_summary = summarize_email(modified_combined_message)
    #     # Continue with your logic to process the email content and post to S/4HANA
    # else:
    #     print("No recent image file found in the directory.")
    #     # Handle the case where no image is found as appropriate
    
    # print("Combined Message:\n", combined_message)
    structured_json = process_email_content(combined_message, email_summary, fileDescription)
    post_success = post_to_s4hana(structured_json)
    
    # problem_description = summarize_email(combined_message)
    # # print(structured_json)
    # print("\nThis is the problem description: " + problem_description )
    
    if post_success:
        # Attempt to upload the most recent image
        image_post_success = upload_recent_images(email_summary, attachments_count)
        
        if image_post_success:
            message = "Data received, posted successfully, and image uploaded."
        else:
            message = "Data received and posted successfully, but image upload failed."
        
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": "Failed to post data to S/4HANA"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)



