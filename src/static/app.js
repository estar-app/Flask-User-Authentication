const messageContainer = document.getElementById('messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-btn');
const startRecordingButton = document.getElementById('start-recording-btn');

let recognition = null;


const addMessage = (text, sender) => {
    const messageElement = document.createElement("li");
    messageElement.classList.add("chat-message");
    messageElement.classList.add(sender);
  
    const textElement = document.createElement("p");
    messageElement.appendChild(textElement);
    messageContainer.appendChild(messageElement);
  
    if (sender === "bot") {
      const words = text.split(" ");
      let i = 0;
      const interval = setInterval(() => {
        if (i >= words.length) {
          clearInterval(interval);
          messageContainer.scrollTop = messageContainer.scrollHeight;
          return;
        }
  
        const word = words[i];
        const wordElement = document.createElement("span");
        wordElement.innerText = word;
        textElement.appendChild(wordElement);
        textElement.appendChild(document.createTextNode(" "));
  
        i++;
      }, 200); // adjust delay time between words as desired
  
      // Make AJAX request to get audio file path
      const xhr = new XMLHttpRequest();
      xhr.open("POST", "/get-audio");
      xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
      xhr.responseType = "json";
      xhr.onload = function () {
        if (xhr.status === 200) {
          const audioFilePath = xhr.response.audio_file_path;
          const audioElement = document.createElement("audio");
          audioElement.src = audioFilePath;
          audioElement.load();
          audioElement.play();
          messageElement.appendChild(audioElement);
        } else {
          console.error("Error:", xhr.statusText);
        }
      };
      xhr.onerror = function () {
        console.error("Error:", xhr.statusText);
      };
      xhr.send(JSON.stringify({ text }));
    } else {
      textElement.innerText = text;
      messageContainer.scrollTop = messageContainer.scrollHeight;
    }
  };
  


const sendMessage = () => {
    const message = userInput.value.trim();

    if (message !== '') {
        addMessage(message, 'user');

        fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        })
        .then(response => response.json())
        .then(data => {
            const botMessage = data.message;
            addMessage(botMessage, 'bot');
        });

        userInput.value = '';
    }
};


sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keydown', event => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});


startRecordingButton.addEventListener('click', () => {
  const recognition = new window.webkitSpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = 'en-US';

  let transcribedText = '';

  recognition.onresult = (event) => {
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const result = event.results[i];
      if (result.isFinal) {
        transcribedText += result[0].transcript + ' ';
      }
    }
  };

  recognition.onend = () => {
    addMessage(transcribedText.trim(), 'user');

    fetch('/send_message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message: transcribedText.trim() })
    })
    .then(response => response.json())
    .then(data => {
      const botMessage = data.message;
      addMessage(botMessage, 'bot');
    });
  };

  recognition.start();
});


