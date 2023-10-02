import boto3
from decouple import config
from flask import Flask, request, render_template, jsonify
from datetime import datetime

app = Flask(__name__)

# Initialize the S3 client
s3 = boto3.client('s3',
                  aws_access_key_id='YOUR_ACCESS_KEY',
                  aws_secret_access_key='YOUR_SECRET_KEY')

def save_to_text_file(details, filename):
    with open(filename, "w") as file:
        for key, value in details.items():
            file.write(f"{key}: {value}\n")

def upload_to_s3(filename):
    bucket_name = 'chatbot-test-bucket-project'
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
        self.step = -1
        self.personal_details = {}

    def get_next_question(self):
        self.step += 1
        if self.step < len(questions):
            return questions[self.step]
        return None

    def process_user_response(self, user_response):
        current_question = self.get_next_question()
        if current_question:
            self.personal_details[current_question] = user_response
            return current_question
        else:
            name = self.personal_details["What is your name?"]
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{name}_personal_details_{timestamp}.txt"
            save_to_text_file(self.personal_details, filename)
            upload_to_s3(filename)
            self.step = -1
            self.personal_details = {}
            return "Data collected successfully and uploaded to Ms. Aditi S3. Start new person record with the txt file name you want."

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
