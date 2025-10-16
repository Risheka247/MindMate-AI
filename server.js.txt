// server.js
require('dotenv').config();
const express = require('express');
const axios = require('axios');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const bodyParser = require('body-parser');

const app = express();
app.use(helmet());
app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public'));

// Rate limit: adjust as needed
const limiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 30, // max requests per IP per window
  standardHeaders: true,
  legacyHeaders: false,
});
app.use(limiter);

// Crisis keywords (simple detector)
const CRISIS_KEYWORDS = [
  'kill myself','suicide','end my life','want to die','cant go on',
  'no reason to live','i will die','hurt myself','self harm','cut myself'
];

function detectCrisis(text) {
  if(!text) return false;
  const normalized = text.toLowerCase();
  return CRISIS_KEYWORDS.some(k => normalized.includes(k));
}

// Therapist system prompt (tune as needed)
const SYSTEM_PROMPT = `
You are a compassionate, non-judgmental AI therapist here to provide emotional support, grounding exercises, and evidence-based coping techniques (CBT, DBT, mindfulness).
Rules:
- Never diagnose or prescribe medication.
- Use short, clear supportive language.
- If user indicates self-harm or suicide, respond with immediate crisis guidance and encourage contacting emergency services or a hotline.
- Offer grounding exercises, breathing, and steps to seek human help.
- Keep responses concise and practical when the user is distressed.
`;

// POST /chat -> { message: "..." }
app.post('/chat', async (req, res) => {
  try {
    const userMessage = (req.body.message || '').trim();
    if (!userMessage) return res.status(400).json({ error: 'Missing message' });

    // Crisis detection
    if (detectCrisis(userMessage)) {
      const crisisReply = `I’m really sorry you’re feeling this way. If you are in immediate danger, please call your local emergency number right now. 
Here are some crisis resources you can use: 
- India: 1800 599 0019
- USA: 988
- UK: 0800 689 5652

Would you like breathing grounding steps now? I can guide you through a 1-minute grounding exercise.`;
      return res.json({ reply: crisisReply, crisis: true });
    }

    // Build messages for OpenAI
    const messages = [
      { role: "system", content: SYSTEM_PROMPT },
      { role: "user", content: userMessage }
    ];

    // Call OpenAI
    const apiKey = process.env.OPENAI_API_KEY;
    if(!apiKey) return res.status(500).json({ error: 'Missing OpenAI API key on server' });

    const resp = await axios.post('https://api.openai.com/v1/chat/completions', {
      model: "gpt-5-mini",
      messages,
      max_tokens: 450,
      temperature: 0.7
    }, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      }
    });

    const aiText = resp.data.choices?.[0]?.message?.content || "Sorry, I couldn't form a response. Try again.";
    return res.json({ reply: aiText, crisis: false });

  } catch (err) {
    console.error(err?.response?.data || err.message || err);
    return res.status(500).json({ error: 'Server error' });
  }
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));