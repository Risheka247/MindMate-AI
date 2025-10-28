// Basic frontend logic to talk to the Flask backend
const chatEl = document.getElementById('chat');
const inputEl = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const modeToggle = document.getElementById('modeToggle');

function addMessage(text, who='ai') {
  const div = document.createElement('div');
  div.className = 'message ' + who;
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = text.replace(/\n/g, '<br/>');
  div.appendChild(bubble);
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
}

// initial greeting
addMessage("Hi — I'm MindMate. I'm here to listen. Tell me what's on your mind.");

// fetch chat response
async function sendMessage() {
  const text = inputEl.value.trim();
  if (!text) return;
  addMessage(text, 'you');
  inputEl.value = '';
  addMessage('...', 'ai'); // loader

  try {
    const resp = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({message: text})
    });
    const data = await resp.json();
    // remove loader
    const last = chatEl.lastElementChild;
    if (last && last.innerText === '...') chatEl.removeChild(last);

    if (data && data.reply) {
      addMessage(data.reply, 'ai');
      if (data.crisis) {
        // if crisis, highlight hotlines visible
        addMessage("If you are in immediate danger, call local emergency services now. See hotlines below.", 'ai');
      }
    } else {
      addMessage("Sorry — something went wrong. Try again.", 'ai');
    }
  } catch (err) {
    console.error(err);
    const last = chatEl.lastElementChild;
    if (last && last.innerText === '...') chatEl.removeChild(last);
    addMessage("Network error. Please try again later.", 'ai');
  }
}

// send button and Enter key
sendBtn.addEventListener('click', sendMessage);
inputEl.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendMessage(); });

// quick-tool buttons
document.getElementById('breatheBtn').addEventListener('click', () => {
  addMessage("Let's do one round of breathing together: inhale 4 — hold 4 — exhale 6. Follow my count: Inhale... 1,2,3,4...", 'ai');
});
document.getElementById('groundBtn').addEventListener('click', () => {
  addMessage("Grounding (5-4-3-2-1): Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste. Start when ready.", 'ai');
});
document.getElementById('smallActBtn').addEventListener('click', () => {
  addMessage("Small action ideas: 1) Drink a glass of water. 2) Step outside for 5 minutes. 3) Text one friend. Which one feels doable?", 'ai');
});

// mood buttons send quick prompts
document.querySelectorAll('.mood').forEach(btn=>{
  btn.addEventListener('click', () => {
    const mood = btn.getAttribute('data-mood');
    addMessage("I'm feeling " + mood, 'you');
    // send to backend for relevant reply
    fetch('/chat', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({message: mood})})
      .then(r=>r.json()).then(data => addMessage(data.reply, 'ai')).catch(()=>addMessage("Network error. Try again.", 'ai'));
  });
});

// dark/light mode
function setDark(enabled) {
  if (enabled) document.documentElement.classList.add('dark');
  else document.documentElement.classList.remove('dark');
  // update toggle icon
  modeToggle.textContent = enabled ? '☀️' : '🌙';
  localStorage.setItem('mindmate_dark', enabled ? '1' : '0');
}
modeToggle.addEventListener('click', () => {
  const enabled = !document.documentElement.classList.contains('dark');
  setDark(enabled);
});
window.addEventListener('load', () => {
  const saved = localStorage.getItem('mindmate_dark');
  setDark(saved === '1');
});