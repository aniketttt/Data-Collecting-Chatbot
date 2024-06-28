import boto3
from flask import Flask, request, render_template, jsonify
from datetime import datetime

app = Flask(__name__)

# Initialize the S3 client
s3 = boto3.client('s3',
                  aws_access_key_id='access key',
                  aws_secret_access_key='secret key')

class Chatbot:
    def __init__(self):
        self.step = 0
        self.questions = [
            "What is the file name you want?",
            "What is your name?",
            "How old are you?",
            "What is your email address?",
            "What is your mobile number?",
            "What is your date of birth?",
        ]
        self.personal_details = {}

    def get_next_question(self):
        return self.questions[self.step]

    def process_user_response(self, user_response):
        current_question = self.get_next_question()

        if current_question == "What is the file name you want?":
            # Start a new cycle
            self.personal_details = {}
            self.personal_details[current_question] = user_response
            self.step += 1
            return self.questions[self.step]
        
        if current_question == "What is your date of birth?":
            # Last question, save data to S3
            self.personal_details[current_question] = user_response
            self.save_and_upload_data()
            self.step = 0  # Reset to start a new cycle
            return f"Data submitted successfully. Starting a new record. {self.questions[self.step]}"
        
        # Collect user responses for each question
        self.personal_details[current_question] = user_response
        self.step += 1
        return self.questions[self.step]

    def save_and_upload_data(self):
        name = self.personal_details.get("What is your name?", "User")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{name}_personal_details_{timestamp}.txt"
        self.save_to_text_file(self.personal_details, filename)
        self.upload_to_s3(filename)

    def save_to_text_file(self, details, filename):
        with open(filename, "w") as file:
            for key, value in details.items():
                file.write(f"{key}: {value}\n")

    def upload_to_s3(self, filename):
        bucket_name = 'chatbot-data-collection-bucket'
        s3.upload_file(filename, bucket_name, filename)

chatbot = Chatbot()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_message = request.form['user_message']
        response_message = chatbot.process_user_response(user_message)
        return jsonify({"message": response_message})

    return render_template('index.html')

@app.route('/display-file/<filename>', methods=['GET'])
def display_file(filename):
    bucket_name = 'chatbot-data-collection-bucket'
    try:
        obj = s3.get_object(Bucket=bucket_name, Key=filename)
        file_content = obj['Body'].read().decode('utf-8')
        return render_template('display_file.html', filename=filename, file_content=file_content)
    except Exception as e:
        return f"Error fetching file: {str(e)}"

@app.route('/view-data', methods=['GET'])
def view_data():
    bucket_name = 'chatbot-data-collection-bucket'
    s3_objects = s3.list_objects_v2(Bucket=bucket_name)['Contents']
    files = [obj['Key'] for obj in s3_objects]
    return render_template('view_data.html', files=files)

if __name__ == '__main__':
    app.run(debug=True)
