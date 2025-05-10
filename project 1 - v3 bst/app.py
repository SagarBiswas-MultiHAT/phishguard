from flask import Flask, render_template, jsonify, request
import random
import json
import os
import time

app = Flask(__name__, template_folder='phishguard/templates', static_folder='phishguard/static') # specify template and static folder

# Get the absolute path to the phishing_data.json file
current_dir = os.path.dirname(os.path.abspath(__file__)) # __ file__ gives the path of the current file
phishing_data_path = os.path.join(current_dir, "phishing_data.json")

try:
    with open(phishing_data_path) as f:
        emails = json.load(f)
except FileNotFoundError:
    emails = []
    print("Error: phishing_data.json file not found.")
except json.JSONDecodeError:
    emails = []
    print("Error: Failed to parse phishing_data.json.")

@app.route('/') # use to render the index.html page
def index(): # function to render the index.html page
    try:
        return render_template("index.html")
    except Exception as e:
        return f"An error occurred while rendering the page: {str(e)}", 500 # 500 is the status code for internal server error

@app.route('/get-email') # use to get a random email from the phishing_data.json file
def get_email():
    try:
        if not emails:
            return jsonify({"error": "No email data available."}), 500 # jsonify is used to convert the data into JSON format
        email = random.choice(emails)
        return jsonify(email) # if the email is found, return the email
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/submit-feedback', methods=['POST']) # use to submit feedback
def submit_feedback():
    try:
        feedback = request.json
        if not feedback:
            return jsonify({"error": "Invalid feedback data."}), 400
        feedback_folder_path = os.path.join(current_dir, "FeedBack") # creating a folder to store the feedback
        os.makedirs(feedback_folder_path, exist_ok=True) # create the folder if it does not exist
        feedback_file_path = os.path.join(feedback_folder_path, f"feedback_{int(time.time())}.json") # creating a file to store the feedback; int(time.time()) gives the current time in seconds since the epoch
        with open(feedback_file_path, "w") as f: # open the file in write mode; f is the file object
            json.dump(feedback, f) # dump the feedback into the file
        return jsonify({"message": "Feedback submitted successfully!"}) # return a success message
    except json.JSONDecodeError: # if the JSON is not in the correct format
        return jsonify({"error": "Invalid JSON format."}), 400 # 400 is the status code for bad request
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500 # 500 is the status code for internal server error

if __name__ == '__main__':
    try:
        app.run(debug=True) # debug=True is used to enable the debug mode; it will automatically reload the server when changes are made to the code
    except Exception as e:
        print(f"Failed to start the server: {str(e)}")
