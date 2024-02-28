from flask import Flask, request, jsonify
from datetime import datetime
from dotenv import load_dotenv
from utils.processEmail import process_email_content
from utils.summarizeEmail import summarize_email
from utils.insertOrder import post_to_s4hana
from utils.insertAttachments import upload_recent_images, get_image_description, find_most_recent_images, rename_image

load_dotenv()

app = Flask(__name__)

@app.route('/processemail', methods=['POST'])
def process_email():
    data = request.get_json()

    mail_sender = data.get('mailSender', 'No Sender')
    mail_subject = data.get('mailSubject', 'No Subject')
    mail_body = data.get('mailBody', 'No Body')
    mail_date_and_time = data.get('mailDateandTime', 'No Date and Time')
    attachments_count = data.get('attachmentsCount', 0)

    combined_message = f"Sender: {mail_sender}\nSubject: {mail_subject}\nBody: {mail_body}\nDate and Time: {mail_date_and_time}"

    if attachments_count > 0:
        directory = "C:\\temp\\serviceOrderImages"
        images_paths = find_most_recent_images(directory, count=attachments_count)
        renamed_images_info = []

        for image_path in images_paths:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            new_file_path, new_slug = rename_image(image_path, mail_body, timestamp)  # Ensure this function returns the new path and filename
            image_description = get_image_description(new_file_path, mail_body)
            renamed_images_info.append((new_slug, image_description))

        if attachments_count > 1:
            images_description_str = "Multiple images attached.\n" + "\n".join([f"{index + 1}: {slug}: {desc}" for index, (slug, desc) in enumerate(renamed_images_info)])
        else:
            images_description_str = f"Attached Image Description: {renamed_images_info[0][1]}"

        fileDescription = images_description_str
        modified_combined_message = f"{combined_message}\n\n{fileDescription}"
    else:
        print("No image file found in the directory.")
        modified_combined_message = combined_message
        fileDescription = "No images attached."


    email_summary = summarize_email(modified_combined_message)
    structured_json = process_email_content(combined_message, email_summary, fileDescription)
    post_success = post_to_s4hana(structured_json)

    if post_success and attachments_count > 0:
        image_post_success = upload_recent_images(attachments_count)
        message = "Data received, posted successfully, and image uploaded." if image_post_success else "Data received and posted successfully, but image upload failed."
    elif post_success:
        message = "Data received and posted successfully."
    else:
        message = "Failed to post data to S/4HANA"

    return jsonify({"message": message}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
