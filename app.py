import boto3
from flask import Flask, request, render_template, jsonify
from datetime import datetime

app = Flask(__name__)

# Initialize the S3 client
s3 = boto3.client('s3',
                  aws_access_key_id='access key',
                  aws_secret_access_key='secret key')

def save_to_text_file(details, filename):
    with open(filename, "w") as file:
        for key, value in details.items():
            file.write(f"{key}: {value}\n")

def upload_to_s3(filename):
    bucket_name = 'chatbot-data-collection-bucket'
    s3.upload_file(filename, bucket_name, filename)

questions = [
    "What is your name?",
    "How old are you?",
    "What is your email address?",
    "What is your mobile number?",
    "What is your date of birth?",
]

class Chatbot:
    def __init__(self):
        self.step = 0  # Start with the first question
        self.personal_details = {}
        self.filename = None  # Added to store the filename separately

    def get_next_question(self):
        if self.step < len(questions):
            return questions[self.step]
        return None

    def process_user_response(self, user_response):
        current_question = self.get_next_question()
        if current_question:
            self.personal_details[current_question] = user_response
            self.step += 1
            next_question = self.get_next_question()
            return f"{next_question}" if next_question else self.complete_and_upload()
        else:
            return self.complete_and_upload()

    def complete_and_upload(self):
        # Use a unique identifier for the filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.filename = f"{self.personal_details['What is your name?']}_{timestamp}.txt"

        # Save details to the text file
        save_to_text_file(self.personal_details, self.filename)
        
        # Upload the text file to S3
        upload_to_s3(self.filename)

        # Reset the step and personal_details
        self.step = 0
        self.personal_details = {}

        return f"Data collected successfully and uploaded to Ms. Aditi S3. Start a new person record with the file name you want."

chatbot = Chatbot()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_message = request.form['user_message']
        response_message = chatbot.process_user_response(user_message)
        return jsonify({"message": response_message})

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
