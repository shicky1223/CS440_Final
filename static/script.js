// script.js

// Cache DOM elements
const chatForm       = document.getElementById('chat-form');
const userInputEl    = document.getElementById('user-input');
const sendButton     = document.getElementById('send-button');
const chatBox        = document.getElementById('chat-box');
const spinnerIcon    = '<i class="fas fa-spinner fa-spin"></i>';

// Helper: show a transient toast error at bottom-right
function showToast(msg) {
  const toast = document.createElement('div');
  toast.className = 'toast toast-error';
  toast.textContent = msg;
  document.body.append(toast);
  setTimeout(() => toast.classList.add('show'), 10);
  setTimeout(() => toast.remove(), 4000);
}

// Helper: append a message bubble
function appendMessage(sender, text) {
  const container = document.createElement('div');
  container.classList.add('message', sender);

  const bubble = document.createElement('div');
  bubble.classList.add('bubble');
  bubble.textContent = text;

  container.append(bubble);
  chatBox.append(container);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Disable input + show spinner
function setLoading(loading) {
  if (loading) {
    sendButton.dataset.orig = sendButton.innerHTML;
    sendButton.innerHTML = spinnerIcon;
    sendButton.disabled = true;
    userInputEl.disabled = true;
  } else {
    sendButton.innerHTML = sendButton.dataset.orig;
    sendButton.disabled = false;
    userInputEl.disabled = false;
    userInputEl.focus();
  }
}

// Main submit handler
chatForm.addEventListener('submit', async e => {
  e.preventDefault();
  const msg = userInputEl.value.trim();
  if (!msg) return;

  appendMessage('user', msg);
  userInputEl.value = '';
  setLoading(true);

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type':'application/json' },
      body: JSON.stringify({ message: msg })
    });
    const data = await res.json();
    if (res.ok && data.reply) {
      appendMessage('ai', data.reply);
    } else {
      showToast(data.error || 'Server returned an error.');
      appendMessage('ai', 'Oops, something went wrong.');
    }
  } catch (err) {
    console.error(err);
    showToast('Network error. Please try again.');
    appendMessage('ai', 'Network error.');
  } finally {
    setLoading(false);
  }
});

// Also send on Enter key in the input
userInputEl.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    chatForm.requestSubmit();
  }
});
