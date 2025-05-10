let currentEmail = {}; // Initialize currentEmail to an empty object
let score = 0;
let totalAttempts = 0;
let timer; // Initialize timer variable to store the interval ID 
let timeLeft = 10;
let isAnswerSubmitted = false; // Flag to prevent multiple submissions

function loadEmail() {
  fetch('/get-email') // fetches a random email from the server and returns a random email
    .then(res => { // .then() method returns a promise that resolves to the response of the request
      if (!res.ok) { // Check if not the response is ok (status code 200-299)
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      return res.json(); // Parse the response as JSON and return it if the response is ok
    })
    .then(data => { // .then() method returns a promise that resolves to the parsed JSON data
      if (!data.text) { // Check if not the email data is valid
        throw new Error("Invalid email data received.");
      }
      currentEmail = data; // Store the current email data if the email data is valid
      document.getElementById('email-content').textContent = data.text; // Display the email content in the HTML element with ID 'email-content'
      document.getElementById('feedback').textContent = ''; // Clear previous feedback message
      isAnswerSubmitted = false; // Reset the flag
      startTimer(); // Start the timer for the new email
    })
    .catch(error => { // .catch() method returns a promise that resolves to the error of the request
      document.getElementById('email-content').textContent = "Failed to load email. Please try again later."; // Display an error message if the email data is invalid
      console.error("Error fetching email:", error); // Log the error to the console
    });
}

function startTimer() {
  clearInterval(timer); // Ensure no duplicate timers are running
  timeLeft = 10;
  document.getElementById('timer').textContent = `Time left: ${timeLeft}s`;
  timer = setInterval(() => { // setInterval() method calls a function or executes a code snippet repeatedly, with a fixed time delay between each call
    timeLeft--;
    document.getElementById('timer').textContent = `Time left: ${timeLeft}s`; // Update the timer display
    if (timeLeft <= 0) { // Check if the time is up
      clearInterval(timer); // Clear the timer
      document.getElementById('feedback').textContent = "Time's up!"; // Display a message when time is up
      setTimeout(loadEmail, 2000); // Load a new email after 2 seconds
    }
  }, 1000); // 1000 milliseconds = 1 second
}

function updateScore(isCorrect) { // Function to update the score
  if (isCorrect) score++; // Increment score if the answer is correct
  totalAttempts++; // Increment total attempts if the answer is submitted
  document.getElementById('score').textContent = `Score: ${score}/${totalAttempts}`; // Update the score display
}

function submitAnswer(userChoice) {
  if (isAnswerSubmitted) return; // Prevent multiple submissions
  isAnswerSubmitted = true; // Set the flag to true if the answer is submitted

  clearInterval(timer); // Clear the timer when the answer is submitted
  const isCorrect = userChoice === currentEmail.label; // currentEmail.label values are 'phishing' or 'legit' of the json object
  const result = isCorrect ? "Correct!" : "Oops! That was actually " + currentEmail.label; // Display the result message based on the user's choice
  document.getElementById('feedback').textContent = result; // Display the feedback message in the HTML element with ID 'feedback'
  updateScore(isCorrect); // Update the score based on the user's choice
  setTimeout(loadEmail, 2000); // Load a new email after 2 seconds
}

function submitFeedback() {
  const feedbackText = document.getElementById('feedback-text').value; // Get the feedback text from the input field
  if (!feedbackText.trim()) { // Check if not the feedback text is empty; .trim() removes whitespace from both ends of a string
    alert('Please enter your feedback before submitting.');
    return; // Exit the function if feedback is empty
  }

  fetch('/submit-feedback', { // Send the feedback to the server; the server that serves the static files; /submit-feedback is the endpoint that handles the feedback submission by the server 
    method: 'POST', // Specify the HTTP method as POST coz we are sending data to the server
    headers: {
      'Content-Type': 'application/json', // Set the content type to JSON 
    },
    body: JSON.stringify({ feedback: feedbackText }), // Convert the feedback text to a JSON string
  })
    .then((response) => { // Handle the response from the server
      if (!response.ok) { // Check if not the response is ok (status code 200-299)
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json(); // Parse the response as JSON and return it if the response is ok
    })
    .then((data) => {
      alert(data.message || 'Feedback submitted successfully!');
      document.getElementById('feedback-text').value = ''; // Clear the feedback input field after submission
    })
    .catch((error) => { // Handle any errors that occur during the fetch
      console.error('Error submitting feedback:', error);
      alert('Failed to submit feedback. Please try again later.');
    });
}

window.onload = () => { // This function runs when the window is fully loaded
  loadEmail(); // calling the loadEmail function to fetch and display a random email
  const scoreDiv = document.createElement('div'); // Create a new div element to display the score
  scoreDiv.id = 'score';
  document.body.appendChild(scoreDiv); // Append the score div to the body of the document

  const timerDiv = document.createElement('div'); // Create a new div element to display the timer
  timerDiv.id = 'timer';
  document.body.appendChild(timerDiv);

  const feedbackButton = document.getElementById('submit-feedback-button'); // Get the feedback button element by its ID
  if (feedbackButton) { // Check if the feedback button exists
    feedbackButton.addEventListener('click', submitFeedback); // Add a click event listener to the feedback button to call the submitFeedback function
  }
};
