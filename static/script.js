document.getElementById('chat-form').addEventListener('submit', async function (e) {
    e.preventDefault();
    
    const userInput = document.getElementById('user-input');
    const messageText = userInput.value.trim();
    if (messageText === '') return;
    
    // Append user message to chat box
    appendMessage('user', messageText);
    userInput.value = '';
  
    try {
      // Send the message to the backend
      const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: messageText })
      });
      
      const data = await response.json();
      if (data.reply) {
        // Append AI reply
        appendMessage('ai', data.reply);
      }
    } catch (error) {
      console.error('Error:', error);
      appendMessage('ai', "Sorry, something went wrong.");
    }
  });
  
  // Function to append a message to the chat box
  function appendMessage(sender, text) {
    const messageContainer = document.createElement('div');
    messageContainer.classList.add('message', sender);
    
    const bubble = document.createElement('div');
    bubble.classList.add('bubble');
    bubble.textContent = text;
    
    messageContainer.appendChild(bubble);
    
    const chatBox = document.getElementById('chat-box');
    chatBox.appendChild(messageContainer);
    // Scroll to the bottom each time a new message is added.
    chatBox.scrollTop = chatBox.scrollHeight;
  }
  