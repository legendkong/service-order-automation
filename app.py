from flask import Flask, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv
from utils.processEmail import process_email_content
from utils.summarizeEmail import summarize_email
from utils.insertOrder import post_to_s4hana
from utils.insertAttachments import upload_recent_image

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI()

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

    # Combine the fields
    combined_message = f"Sender: {mail_sender}\nSubject: {mail_subject}\nBody: {mail_body}\nDate and Time: {mail_date_and_time}"
    # print("Combined Message:\n", combined_message)
    structured_json = process_email_content(combined_message)
    post_success = post_to_s4hana(structured_json)
    
    problem_description = summarize_email(combined_message)
    # print(structured_json)
    print("\nThis is the problem description: " + problem_description )
    
    if post_success:
        # Attempt to upload the most recent image
        image_post_success = upload_recent_image()
        
        if image_post_success:
            message = "Data received, posted successfully, and image uploaded."
        else:
            message = "Data received and posted successfully, but image upload failed."
        
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": "Failed to post data to S/4HANA"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)


