const loggedInUser = {
    firstName: "Rajan",
    lastName: "Sharma",
    avatar: "🧑‍🌾",
    location: "Rangpo, Sikkim, India"
  };

  document.getElementById('user-name-display').innerText = `${loggedInUser.firstName} ${loggedInUser.lastName}`;
  document.getElementById('user-avatar-display').innerText = loggedInUser.avatar;
  document.getElementById('user-location-display').innerText = loggedInUser.location;

  const currentHour = new Date().getHours();
  let greetingText = "Good Evening";
  if (currentHour < 12) greetingText = "Good Morning";
  else if (currentHour < 18) greetingText = "Good Afternoon";
  document.getElementById('greeting-display').innerText = greetingText;

  const cropData = {
    wheat: {
      advisory: "Apply nitrogen fertilizer to Wheat (Field A) before evening. Rain expected in 36 hrs.",
      fert: { val: "NPK", unit: " needed", trend: "⚠ Apply within 2 days", class: "trend-ok" },
      temp: { val: "18", unit: " °C avg", trend: "⚠ Slightly above optimal", class: "trend-ok" },
      rain: { val: "36", unit: " mm/36h", trend: "✓ Skip irrigation", class: "trend-up" },
      soil: { val: "pH 6.5", unit: " · Optimal", trend: "✓ Optimal conditions", class: "trend-up" }
    },
    rice: {
      advisory: "Maintain water level at 5cm. Watch out for signs of stem borer in Field B.",
      fert: { val: "Urea", unit: " needed", trend: "⚠ Apply today", class: "trend-ok" },
      temp: { val: "25", unit: " °C avg", trend: "✓ Perfect range", class: "trend-up" },
      rain: { val: "10", unit: " mm/48h", trend: "⚠ Monitor level", class: "trend-ok" },
      soil: { val: "pH 6.0", unit: " · Flooded", trend: "✓ Optimal status", class: "trend-up" }
    },
    potato: {
      advisory: "Apply earthing up to cover exposed tubers. Monitor for late blight due to current humidity.",
      fert: { val: "Potash", unit: " essential", trend: "⚠ Apply soon", class: "trend-ok" },
      temp: { val: "20", unit: " °C avg", trend: "✓ Good range", class: "trend-up" },
      rain: { val: "10", unit: " mm/24h", trend: "✓ Moderate impact", class: "trend-up" },
      soil: { val: "pH 5.8", unit: " · Loam", trend: "✓ Well drained", class: "trend-up" }
    },
    onion: {
      advisory: "Stop irrigation 10-15 days before harvesting to ensure proper curing of bulbs.",
      fert: { val: "Sulfur", unit: " required", trend: "⚠ Check levels", class: "trend-ok" },
      temp: { val: "22", unit: " °C avg", trend: "✓ Perfect range", class: "trend-up" },
      rain: { val: "0", unit: " mm/48h", trend: "⚠ Needs irrigation", class: "trend-down" },
      soil: { val: "pH 6.5", unit: " · 40% Moist", trend: "⚠ Slightly dry", class: "trend-ok" }
    },
    moong: {
      advisory: "Spray neem seed kernel extract (NSKE) to manage whitefly population and prevent YMV.",
      fert: { val: "Phosphorus", unit: " optimal", trend: "✓ Up to date", class: "trend-up" },
      temp: { val: "30", unit: " °C avg", trend: "✓ Ideal for growth", class: "trend-up" },
      rain: { val: "5", unit: " mm/72h", trend: "✓ Minimal impact", class: "trend-up" },
      soil: { val: "pH 7.0", unit: " · Neutral", trend: "✓ Optimal status", class: "trend-up" }
    }
  };

  const cropOrder = ['wheat', 'rice', 'potato', 'onion', 'moong'];
  let currentCropIndex = 0;

  function nextCrop() {
    currentCropIndex = (currentCropIndex + 1) % cropOrder.length;
    selectCrop(cropOrder[currentCropIndex]);
  }

  function prevCrop() {
    currentCropIndex = (currentCropIndex - 1 + cropOrder.length) % cropOrder.length;
    selectCrop(cropOrder[currentCropIndex]);
  }

  function selectCrop(cropKey) {
    if (!cropData[cropKey]) return;
    currentCropIndex = cropOrder.indexOf(cropKey);

    document.querySelectorAll('.hero-slide').forEach(slide => slide.classList.remove('active'));
    document.getElementById(`slide-${cropKey}`).classList.add('active');

    const data = cropData[cropKey];
    document.getElementById('advisory-text').innerText = data.advisory;
    
    document.getElementById('val-fert').innerHTML = `${data.fert.val} <span class="info-unit">${data.fert.unit}</span>`;
    updateTrend('trend-fert', data.fert.trend, data.fert.class);

    document.getElementById('val-temp').innerHTML = `${data.temp.val} <span class="info-unit">${data.temp.unit}</span>`;
    updateTrend('trend-temp', data.temp.trend, data.temp.class);

    document.getElementById('val-rain').innerHTML = `${data.rain.val} <span class="info-unit">${data.rain.unit}</span>`;
    updateTrend('trend-rain', data.rain.trend, data.rain.class);

    document.getElementById('val-soil').innerHTML = `${data.soil.val} <span class="info-unit">${data.soil.unit}</span>`;
    updateTrend('trend-soil', data.soil.trend, data.soil.class);
  }

  function updateTrend(id, text, className) {
    const el = document.getElementById(id);
    el.innerText = text;
    el.className = `info-trend ${className}`;
  }

  const searchInput = document.getElementById('search-input');
  searchInput.addEventListener('input', (e) => {
    const val = e.target.value.toLowerCase().trim();
    if (cropData[val]) {
      selectCrop(val);
    }
  });

  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function() {
      document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
      this.classList.add('active');
    });
  });

  function createCalendarEvents(cropKey) {
    const location = document.getElementById('user-location-display')?.innerText || 'Kolkata';
    const query = new URLSearchParams({ crop: cropKey, location }).toString();
    window.location.href = `/showYield?${query}`;
  }
// --- BENGALI VOICE SEARCH & AUTO-TRANSLATION ---
const micBtn = document.getElementById('mic-btn');
// (searchInput is already declared earlier in your script.js)

// Check if the browser supports the Web Speech API
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

// 1. The Custom Dictionary: Maps Bengali spoken words to your English crop IDs
const bengaliToEnglishMap = {
    "গম": "wheat",
    "ধান": "rice",
    "চাল": "rice",
    "আলু": "potato",
    "পেঁয়াজ": "onion",
    "পেয়াজ": "onion",
    "মুগ": "moong",
    "মুগ ডাল": "moong",
    "ডাল": "moong"
};

if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.continuous = false; 
    recognition.lang = 'bn-IN'; // 2. CHANGED: Now listens specifically for Bengali!

    // When the user clicks the microphone
    micBtn.addEventListener('click', () => {
        recognition.start();
        
        // Visual feedback: Turn the mic green and update placeholder
        micBtn.style.color = '#4caf50'; 
        searchInput.placeholder = "শুনছি... (Listening...)"; // Bengali UI feedback
        searchInput.value = ""; 
    });

    // When the AI understands the speech
    recognition.onresult = (event) => {
        // Grab the spoken Bengali text and clean it up
        let transcript = event.results[0][0].transcript.trim();
        transcript = transcript.replace(/[.,]/g, ''); 
        
        console.log("🎤 Heard in Bengali: ", transcript);

        // 3. TRANSLATION: Look up the Bengali word in our dictionary map
        // If it doesn't find a match, it just uses what the user said
        let englishTranslation = bengaliToEnglishMap[transcript] || transcript.toLowerCase();

        // Put the ENGLISH translated word into the search box
        searchInput.value = englishTranslation;
        
        // Reset the visual feedback
        micBtn.style.color = 'rgba(255,255,255,0.7)';
        searchInput.placeholder = "Search crops (e.g. rice, moong)...";

        // MAGIC TRICK: Trigger your existing search logic automatically
        searchInput.dispatchEvent(new Event('input'));
    };

    // If there is an error (e.g., they deny microphone permissions)
    recognition.onerror = (event) => {
        console.warn("Speech recognition error: ", event.error);
        micBtn.style.color = '#f44336'; // Turn red on error
        setTimeout(() => {
            micBtn.style.color = 'rgba(255,255,255,0.7)';
            searchInput.placeholder = "Search crops (e.g. rice, moong)...";
        }, 2000);
    };

    // Clean up when they stop talking
    recognition.onspeechend = () => {
        recognition.stop();
    };

} else {
    // If they are on an old browser that doesn't support it, hide the button
    micBtn.style.display = 'none';
}
// --- BENGALI WELCOME GREETING ---
let hasGreeted = false;

document.body.addEventListener('click', () => {
    // Only play this once, and only if the browser supports it
    if (!hasGreeted && 'speechSynthesis' in window) {
        // Bengali Text: "Hello! To search, press the mic button and say your crop's name."
        const greetingText = "নমস্কার! সার্চ করার জন্য মাইক বোতাম টিপুন এবং আপনার ফসলের নাম বলুন।";
        
        const speech = new SpeechSynthesisUtterance(greetingText);
        speech.lang = 'bn-IN'; // Set voice to Indian Bengali
        speech.rate = 0.9;     // Speak slightly slower
        
        window.speechSynthesis.speak(speech);
        hasGreeted = true; // Make sure it never plays again
    }
}, { once: true }); // This listener destroys itself after the first click

// --- CHATBOT FUNCTIONALITY ---
const chatBtn = document.getElementById('chat-btn');
const chatModal = document.getElementById('chat-modal');
const closeChat = document.getElementById('close-chat');
const chatInput = document.getElementById('chat-input');
const sendChat = document.getElementById('send-chat');
const chatMessages = document.getElementById('chat-messages');

// Add entrance animation to chat button
setTimeout(() => {
  chatBtn.style.animation = 'chatEntrance 0.8s ease-out';
}, 1000);

// Open chat modal with enhanced interaction
chatBtn.addEventListener('click', () => {
  chatModal.style.display = 'flex';
  chatBtn.style.animation = 'chatClick 0.2s ease, chatPop 0.6s ease';
  setTimeout(() => {
    chatBtn.style.animation = 'chatPulse 2s infinite';
  }, 600);
  
  // Add haptic feedback simulation (visual bounce)
  document.body.style.animation = 'bodyShake 0.1s ease';
  setTimeout(() => {
    document.body.style.animation = '';
  }, 100);
});

// Enhanced hover effects
chatBtn.addEventListener('mouseenter', () => {
  chatBtn.style.transform = 'scale(1.05) rotate(5deg)';
});

chatBtn.addEventListener('mouseleave', () => {
  chatBtn.style.transform = 'scale(1) rotate(0deg)';
});

// Close chat modal
closeChat.addEventListener('click', () => {
  chatModal.style.display = 'none';
});

// Close modal when clicking outside
chatModal.addEventListener('click', (e) => {
  if (e.target === chatModal) {
    chatModal.style.display = 'none';
  }
});

// Send message function
async function sendMessage() {
  const message = chatInput.value.trim();
  if (!message) return;

  // Add user message
  addMessage(message, 'user');
  chatInput.value = '';

  try {
    const response = await fetch('/dashboard/chatbot', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: message })
    });

    const data = await response.json();
    addMessage(data.response, 'bot');
  } catch (error) {
    addMessage('Sorry, I encountered an error. Please try again.', 'bot');
  }
}

// Add message to chat
function addMessage(text, sender) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${sender}-message`;
  
  const avatar = document.createElement('div');
  avatar.className = 'message-avatar';
  avatar.textContent = sender === 'bot' ? '🤖' : '👤';
  
  const content = document.createElement('div');
  content.className = 'message-content';
  content.textContent = text;
  
  messageDiv.appendChild(avatar);
  messageDiv.appendChild(content);
  
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Send on button click
sendChat.addEventListener('click', sendMessage);

// Send on Enter key
chatInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    sendMessage();
  }
});