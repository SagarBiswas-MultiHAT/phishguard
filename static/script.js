const state = {
  currentEmail: null,
  score: 0,
  attempts: 0,
  timeLeft: 10,
  timerId: null,
  busy: false,
  answered: false,
  retryCount: 0,
  maxRetry: 2,
  paused: false,
};

const elements = {};

function updateStats() {
  elements.scoreValue.textContent = state.score.toString();
  elements.attemptsValue.textContent = state.attempts.toString();
}

function setStatus(message, tone = 'neutral') {
  elements.status.textContent = message;
  elements.status.dataset.tone = tone;
}

function updateTimer() {
  elements.timerValue.textContent = `${state.timeLeft}s`;
}

function startTimer() {
  clearInterval(state.timerId);
  state.timeLeft = 10;
  updateTimer();
  state.paused = false;
  elements.pauseButton.textContent = 'Pause Timer';
  state.timerId = setInterval(() => {
    if (state.paused) {
      return;
    }
    state.timeLeft -= 1;
    updateTimer();
    if (state.timeLeft <= 0) {
      clearInterval(state.timerId);
      handleTimeout();
    }
  }, 1000);
}

function handleTimeout() {
  if (state.answered || !state.currentEmail) {
    return;
  }
  state.answered = true;
  state.attempts += 1;
  updateStats();
  const label = state.currentEmail.label === 'legit' ? 'legitimate' : 'phishing';
  setStatus(`Time's up. That one was ${label}.`, 'warning');
  setTimeout(loadEmail, 1800);
}

function loadEmail() {
  if (state.busy) {
    return;
  }
  state.busy = true;
  setStatus('Crafting a new scenario...', 'neutral');
  const endpoint = '/get-email';

  fetch(endpoint)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      if (!data.text || !data.label) {
        throw new Error('Invalid email payload.');
      }
      state.retryCount = 0;
      state.currentEmail = data;
      state.answered = false;
      elements.emailContent.textContent = data.text;
      setStatus('Make your call: phishing or legitimate?', 'neutral');
      startTimer();
    })
    .catch((error) => {
      console.error('Error fetching email:', error);
      elements.emailContent.textContent = 'We could not load a message right now. Please try again shortly.';
      if (state.retryCount < state.maxRetry) {
        state.retryCount += 1;
        setStatus('Temporary service issue. Retrying now...', 'warning');
        setTimeout(loadEmail, 2000);
      } else {
        setStatus('Connection issue. Please refresh or try again in a moment.', 'error');
      }
    })
    .finally(() => {
      state.busy = false;
    });
}

function handleAnswer(choice) {
  if (state.answered || !state.currentEmail) {
    return;
  }
  state.answered = true;
  clearInterval(state.timerId);
  state.paused = false;
  elements.pauseButton.textContent = 'Pause Timer';
  const isCorrect = choice === state.currentEmail.label;
  state.attempts += 1;
  if (isCorrect) {
    state.score += 1;
  }
  updateStats();

  if (isCorrect) {
    setStatus('Correct! You spotted it.', 'success');
  } else {
    const label = state.currentEmail.label === 'legit' ? 'legitimate' : 'phishing';
    setStatus(`Close call. That message was ${label}.`, 'warning');
  }
  setTimeout(loadEmail, 1800);
}

function togglePause() {
  if (!state.currentEmail || state.answered) {
    return;
  }
  state.paused = !state.paused;
  elements.pauseButton.textContent = state.paused ? 'Resume Timer' : 'Pause Timer';
  if (state.paused) {
    setStatus('Timer paused. Make your call when ready.', 'neutral');
  } else {
    setStatus('Timer resumed. Make your call.', 'neutral');
  }
}

function submitFeedback(event) {
  event.preventDefault();
  const feedbackText = elements.feedbackInput.value.trim();
  if (!feedbackText) {
    setStatus('Add a quick note before sending feedback.', 'warning');
    return;
  }

  elements.feedbackButton.disabled = true;
  setStatus('Sending your feedback...', 'neutral');

  fetch('/submit-feedback', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ feedback: feedbackText }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      elements.feedbackInput.value = '';
      elements.feedbackCounter.textContent = '0 / 300';
      setStatus(data.message || 'Feedback received. Thank you!', 'success');
    })
    .catch((error) => {
      console.error('Error submitting feedback:', error);
      setStatus('Feedback failed to send. Please try again.', 'error');
    })
    .finally(() => {
      elements.feedbackButton.disabled = false;
    });
}

function updateCounter() {
  const count = elements.feedbackInput.value.length;
  elements.feedbackCounter.textContent = `${count} / 300`;
}

document.addEventListener('DOMContentLoaded', () => {
  elements.emailContent = document.getElementById('email-content');
  elements.timerValue = document.getElementById('timer-value');
  elements.scoreValue = document.getElementById('score-value');
  elements.attemptsValue = document.getElementById('attempts-value');
  elements.status = document.getElementById('status');
  elements.phishingButton = document.getElementById('phishing-button');
  elements.legitButton = document.getElementById('legit-button');
  elements.pauseButton = document.getElementById('pause-button');
  elements.feedbackForm = document.getElementById('feedback-form');
  elements.feedbackInput = document.getElementById('feedback-text');
  elements.feedbackButton = document.getElementById('feedback-submit');
  elements.feedbackCounter = document.getElementById('feedback-counter');

  elements.phishingButton.addEventListener('click', () => handleAnswer('phishing'));
  elements.legitButton.addEventListener('click', () => handleAnswer('legit'));
  elements.pauseButton.addEventListener('click', togglePause);
  elements.feedbackForm.addEventListener('submit', submitFeedback);
  elements.feedbackInput.addEventListener('input', updateCounter);

  updateStats();
  updateCounter();
  loadEmail();
});
