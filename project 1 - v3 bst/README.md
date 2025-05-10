# PhishGuard - Email Phishing Detection

PhishGuard is a web-based application designed to help users identify phishing emails. It provides a fun and interactive way to test your ability to distinguish between legitimate and phishing emails while also allowing users to provide feedback on the application.

## Features

- **Interactive Email Detection**: Users are presented with emails and must decide whether they are legitimate or phishing.
- **Timer-Based Gameplay**: Each email must be classified within a 10-second timer.
- **Score Tracking**: Tracks the user's score and total attempts.
- **Feedback Submission**: Users can submit feedback to improve the application.

## Project Structure

```
project 1/
├── app.py                     # Flask application backend
├── phishing_data.json         # Dataset of emails for phishing detection
├── FeedBack/                  # Folder to store user feedback
├── phishguard/
│   ├── static/
│   │   ├── script.js          # Frontend JavaScript logic
│   │   ├── style.css          # Styling for the application
│   ├── templates/
│       ├── index.html         # Main HTML template
```

## Prerequisites

- Python 3.7 or higher
- Flask library

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```

2. Navigate to the project directory:
   ```bash
   cd project 1
   ```

3. Install the required Python packages:
   ```bash
   pip install flask
   ```

## Usage

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

3. Interact with the application to classify emails as phishing or legitimate.

## API Endpoints

- `GET /`: Renders the main application page.
- `GET /get-email`: Fetches a random email from the dataset.
- `POST /submit-feedback`: Submits user feedback.

## Feedback Storage

User feedback is stored in the `FeedBack/` directory as JSON files, with each file named using a timestamp.

## Dataset

The `phishing_data.json` file contains a collection of emails labeled as either "phishing" or "legit". This dataset is used to present emails to the user for classification.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- Inspired by the need to raise awareness about phishing attacks.
- Special thanks to all contributors and testers.