# R2D2 Chatbot Generator

**Bumblebee-Style Voice Assistant with Star Wars R2D2 Personality**

Build your own voice-activated chatbot that communicates like Bumblebee from Transformers - using expressive R2D2 beeps and chirps as primary communication, then switching to clear voice transmission when delivering specific information.

---

## 🌟 Features

- **🎤 Wake Word Activation** - "Hey Olaf" or "Alexa" to activate (customizable)
- **🎙️ Voice Activity Detection (VAD)** - Smart recording that stops when you finish speaking
- **🗣️ Speech Recognition** - Whisper-based STT (local, private, English-only)
- **🤖 AI-Powered Responses** - Groq Llama 3.1 (fast, free tier available)
- **🔊 Hybrid TTS Output**:
  - **Primary**: R2D2 chirps/beeps for reactions and acknowledgments
  - **Transmission**: High-quality voice (with radio effects) for specific information
- **🎭 Star Wars Audio Effects** - Radio transmission, comlink, hologram, dramatic narrator
- **🔇 Noise Filtering** - Ignores typing, objects falling, and other background sounds
- **💬 Natural Conversation** - Maintains context across multiple exchanges

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Linux/macOS (tested on Ubuntu)
- Microphone and speakers
- API keys: Groq (free), Picovoice (free tier available)

### Installation

\`\`\`bash
# Clone the repository
cd experiments_with_voice_agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys:
#   GROQ_API_KEY=your_groq_key
#   PICOVOICE_API_KEY=your_picovoice_key
\`\`\`

### Run Your First Chatbot

\`\`\`python
from r2d2_chatbot.agent import R2D2ChatbotAgent

# Create agent
agent = R2D2ChatbotAgent()

# Start chatbot (wake word activated)
agent.run()
\`\`\`

That's it! Say your wake word, then start talking.

---

## 📖 Usage Examples

### Example 1: Basic Usage

\`\`\`python
from r2d2_chatbot.agent import R2D2ChatbotAgent

# Use default configuration
agent = R2D2ChatbotAgent()
agent.run()

# Say wake word: "Hey Olaf"
# Bot responds with happy R2D2 beep
# Start conversation:
#   You: "What's the weather?"
#   Bot: [R2D2 chirp: "checking weather"]
#        [Transmission: "72 degrees, sunny, winds 10mph"]
#   You: "Thanks!"
#   Bot: [R2D2 chirp: "welcome commander"]
#   You: "Goodbye"
#   Bot goes to sleep
\`\`\`

### Example 2: Custom Configuration

\`\`\`python
from r2d2_chatbot.agent import R2D2ChatbotAgent
from r2d2_chatbot.config import Config

# Create custom config
config = Config()
config.TTS_VOICE = 'male'  # Use male voice instead of female
config.TTS_EFFECT = 'comlink'  # Different audio effect
config.USE_WAKE_WORD = False  # Press Enter instead of wake word
config.VAD_AGGRESSIVENESS = 3  # More aggressive noise filtering

# Create agent with custom config
agent = R2D2ChatbotAgent(config=config)
agent.run()
\`\`\`

### Example 3: Without Wake Word

\`\`\`python
from r2d2_chatbot.agent import R2D2ChatbotAgent
from r2d2_chatbot.config import Config

config = Config()
config.USE_WAKE_WORD = False  # Disable wake word

agent = R2D2ChatbotAgent(config=config)
agent.run()

# Press Enter to start each conversation
\`\`\`

---

## ⚙️ Configuration

Edit \`r2d2_chatbot/config.py\` or create custom Config objects:

### Wake Word Settings

\`\`\`python
USE_WAKE_WORD = True  # Enable/disable wake word
PICOVOICE_API_KEY = os.getenv('PICOVOICE_API_KEY')
PLATFORM = 'linux'  # 'linux' or 'raspberry-pi'
\`\`\`

### Voice Settings

\`\`\`python
TTS_VOICE = 'female'  # 'male' or 'female'
# female = en_US-ljspeech-high (HIGH quality, crystal clear)
# male = en_GB-alan-medium (British, clear)

TTS_EFFECT = 'clear_transmission'  # Audio effect
# Options:
#   'clear_transmission' - Clear + transmission feel (RECOMMENDED)
#   'comlink' - Radio transmission with squelch
#   'dramatic' - Deep narrator (Star Wars intro style)
#   'radio' - Vintage radio effect
#   'hologram' - Glitchy hologram
#   'clear' - No effect
\`\`\`

### LLM Settings

\`\`\`python
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
LLM_MODEL = 'llama-3.1-8b-instant'  # Fast and free!
\`\`\`

### Speech Recognition Settings

\`\`\`python
WHISPER_MODEL = 'small'  # 'tiny', 'base', 'small', 'medium', 'large'
WHISPER_DEVICE = 'cpu'  # 'cpu' or 'cuda'
WHISPER_COMPUTE_TYPE = 'int8'  # 'int8', 'int16', 'float16', 'float32'
\`\`\`

### VAD (Voice Activity Detection) Settings

\`\`\`python
VAD_AGGRESSIVENESS = 2  # 0-3, higher = more aggressive filtering
VAD_SPEECH_THRESHOLD = 8  # Frames needed to start recording (filters typing)
VAD_MIN_DURATION = 1.5  # Minimum recording duration (filters short noises)
\`\`\`

**Noise Filtering Tips:**
- Typing sounds? Increase \`VAD_SPEECH_THRESHOLD\` to 10
- Objects falling? Increase \`VAD_MIN_DURATION\` to 2.0
- Too sensitive? Increase \`VAD_AGGRESSIVENESS\` to 3
- Not picking up speech? Decrease values

---

## 🎯 How It Works

### Bumblebee-Style Communication

Like Bumblebee from Transformers, your chatbot:

1. **Listens** - Wake word activates, VAD records until you stop speaking
2. **Understands** - Whisper transcribes (English only)
3. **Thinks** - LLM generates structured response:
   - \`r2d2_message\`: 3-5 word droid-like reaction
   - \`info_message\`: Specific information (if needed)
4. **Responds**:
   - **R2D2 chirp/beep** - Acknowledges with emotion
   - **[Transition ping]** - Brief R2D2 tone
   - **Voice transmission** - Delivers information with radio effect
   - **R2D2 confirmation** - Affirms completion

### Example Flow

\`\`\`
You: "Tell me a pancake recipe"

Bot Response:
[R2D2 curious chirp: "recipe found"]
[Transition ping]
[TRANSMISSION: "1 cup flour, 2 tbsp sugar, 2 tsp baking powder,
half tsp salt, 1 cup milk, 1 egg, 2 tbsp butter. Mix dry,
add wet, cook medium heat, flip at bubbles"]
[R2D2 happy confirmation: "understood"]
\`\`\`

---

## 🔑 API Keys Setup

### Groq API Key (Required)

1. Go to https://console.groq.com/
2. Sign up for free account
3. Create API key
4. Add to \`.env\`:
   \`\`\`
   GROQ_API_KEY=gsk_your_key_here
   \`\`\`

**Free Tier**: 14,400 requests/day (plenty for personal use)

### Picovoice API Key (Required if using wake word)

1. Go to https://console.picovoice.ai/
2. Sign up for free account
3. Create access key
4. Add to \`.env\`:
   \`\`\`
   PICOVOICE_API_KEY=your_key_here
   \`\`\`

**Free Tier**: 3 wake word models, sufficient for personal projects

---

## 🐛 Troubleshooting

### Wake Word Not Detected

**Problem**: Bot doesn't respond to wake word

**Solutions**:
- Check microphone: \`python -c "import sounddevice; print(sounddevice.query_devices())"\`
- Verify API key in \`.env\`
- Try different sensitivity: Modify \`wakeword.py\` sensitivity (0.3-0.7)
- Test without wake word: Set \`USE_WAKE_WORD = False\`

### Bot Picks Up Background Noise

**Problem**: Activates from typing, objects falling, etc.

**Solutions**:
\`\`\`python
# Increase noise filtering
VAD_AGGRESSIVENESS = 3  # More aggressive (0-3)
VAD_SPEECH_THRESHOLD = 10  # More frames needed
VAD_MIN_DURATION = 2.0  # Longer minimum duration
\`\`\`

### Transcription in Wrong Language

**Problem**: Whisper transcribes in Hindi, Greek, etc. instead of English

**Solutions**:
- Already fixed in code: \`language='en'\` parameter forces English
- If still happening, check Whisper model: Use 'small' or larger

### LLM Responds in Non-English

**Problem**: Bot responds in Greek, Spanish, etc.

**Solutions**:
- Already fixed with fallback detection
- System prompt enforces English-only
- Check \`r2d2_chatbot/llm/groq_client.py\` for \`_is_likely_english()\` method

### Audio Quality Issues

**Problem**: Voice sounds robotic, choppy, or unclear

**Solutions**:
\`\`\`python
# Use highest quality voice
TTS_VOICE = 'female'  # en_US-ljspeech-high

# Use clearest effect
TTS_EFFECT = 'clear_transmission'  # or 'clear'
\`\`\`

---

## 📦 Project Structure

\`\`\`
experiments_with_voice_agent/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment template
├── .env                              # Your API keys (gitignored)
│
├── r2d2_chatbot/                     # Main package
│   ├── __init__.py
│   ├── agent.py                      # Main R2D2ChatbotAgent class
│   ├── config.py                     # Configuration settings
│   │
│   ├── audio/                        # Audio input components
│   │   ├── __init__.py
│   │   ├── wakeword.py              # Picovoice wake word detection
│   │   ├── vad.py                   # Voice activity detection
│   │   └── wake_models/             # Wake word model files (.ppn)
│   │
│   ├── speech/                       # Speech processing
│   │   ├── __init__.py
│   │   ├── stt.py                   # Whisper speech-to-text
│   │   │
│   │   └── tts/                     # Text-to-speech
│   │       ├── __init__.py
│   │       ├── piper.py             # Piper TTS (voice transmission)
│   │       ├── r2d2.py              # R2D2 sound generator
│   │       ├── effects.py           # Audio effects (radio, comlink, etc.)
│   │       └── piper_models/        # Piper voice models (auto-downloaded)
│   │
│   └── llm/                         # Language model
│       ├── __init__.py
│       └── groq_client.py           # Groq LLM client with structured responses
│
├── examples/                         # Usage examples
│   ├── basic.py                     # Simple example
│   └── bumblebee.py                 # Full-featured example
│
└── models/                          # Model storage (gitignored)
    ├── piper/                       # Piper TTS models
    └── whisper/                     # Whisper STT models (cached)
\`\`\`

---

## 🔧 Dependencies

Install via \`requirements.txt\`:

\`\`\`bash
pip install -r requirements.txt
\`\`\`

**Core Dependencies:**
- \`faster-whisper\` - Local speech-to-text (Whisper)
- \`piper-tts\` - High-quality neural TTS
- \`groq\` - LLM API client (Llama 3.1)
- \`pvporcupine\` - Wake word detection (Picovoice)
- \`webrtcvad\` - Voice activity detection
- \`sounddevice\` - Audio I/O
- \`numpy\` - Audio processing
- \`scipy\` - Signal processing (audio effects)
- \`python-dotenv\` - Environment variables

---

## 💡 Tips and Best Practices

### For Best Wake Word Detection:
- Speak clearly at normal volume
- Reduce background noise
- Place microphone 1-2 feet from mouth
- Adjust sensitivity if needed (0.3 = sensitive, 0.7 = less sensitive)

### For Best Speech Recognition:
- Speak naturally, don't rush
- Pause briefly before and after speaking
- Reduce echo (avoid empty rooms with hard surfaces)
- Use good quality microphone if possible

### For Best Conversations:
- Keep questions clear and specific
- Wait for full response before speaking again
- Use "goodbye" or "go to sleep" to end session properly
- Bot maintains context, so you can have multi-turn conversations

### For Noisy Environments:
\`\`\`python
# More aggressive filtering
config.VAD_AGGRESSIVENESS = 3
config.VAD_SPEECH_THRESHOLD = 12
config.VAD_MIN_DURATION = 2.0
\`\`\`

### For Quiet Environments:
\`\`\`python
# More sensitive
config.VAD_AGGRESSIVENESS = 1
config.VAD_SPEECH_THRESHOLD = 5
config.VAD_MIN_DURATION = 1.0
\`\`\`

---

## 🔒 Privacy

**All processing is local except LLM:**
- ✅ Wake word: Local (Picovoice Porcupine)
- ✅ VAD: Local (WebRTC)
- ✅ STT: Local (Faster Whisper)
- ❌ LLM: Cloud (Groq API)
- ✅ TTS: Local (Piper)
- ✅ R2D2: Local (synthetic generation)

**To maximize privacy:**
- Audio never leaves your device (except transcribed text to LLM)
- Groq doesn't store API requests beyond 30 days (per their policy)
- You can self-host LLM with Ollama for 100% local operation

---

## 🎓 Understanding the Response Format

The LLM returns structured JSON responses:

\`\`\`json
{
  "r2d2_message": "Brief 3-5 word reaction",
  "info_message": "Specific information" or null
}
\`\`\`

### When info_message is null:

Used for simple interactions that don't require specific information:
- Greetings: "How are you?" → \`"olaf feel good"\` + null
- Yes/no: "Are you there?" → \`"yes here"\` + null
- Thanks: "Thanks!" → \`"welcome commander"\` + null

### When info_message has content:

Used when delivering specific facts, data, or instructions:
- Weather: \`"checking weather"\` + \`"72 degrees, sunny, winds 10mph"\`
- Recipe: \`"recipe found"\` + \`"1 cup flour, 2 tbsp sugar, ..."\`
- Time: \`"time check"\` + \`"2:45 PM"\`

### Response Style Guidelines:

**R2D2 Message (3-5 words, broken English OK):**
- ✅ "olaf feel good"
- ✅ "checking weather"
- ✅ "data found"
- ✅ "recipe ready"
- ✅ "yes here"
- ❌ "I am feeling quite good today" (too long)
- ❌ "Let me check the weather for you" (too formal)

**Info Message (ultra brief, comma-separated):**
- ✅ "72 degrees, sunny, winds 10mph"
- ✅ "1 cup flour, 2 tbsp sugar, 1 egg, mix"
- ✅ "Park level, engage brake, loosen nuts, jack up, swap wheels"
- ❌ "The temperature is currently 72 degrees and it is sunny" (too wordy)
- ❌ "First you'll need 1 cup of flour, then add..." (too conversational)

---

## 💬 Example Conversations

### Example 1: Information Query
\`\`\`
You: "Hey Olaf"
Bot: [Happy R2D2 beep]

You: "What's the capital of France?"
Bot: [R2D2: "data found"]
     [Transmission: "Paris, France"]
     [R2D2: "understood"]

You: "Thanks!"
Bot: [R2D2: "welcome commander"]
\`\`\`

### Example 2: Recipe
\`\`\`
You: "Hey Olaf"
Bot: [Happy R2D2 beep]

You: "How do I make chocolate chip cookies?"
Bot: [R2D2: "recipe found"]
     [Transmission: "1 cup butter, 1 cup sugar, 2 eggs, 2 tsp vanilla,
      3 cups flour, 1 tsp baking soda, half tsp salt, 2 cups chocolate chips.
      Mix wet, add dry, fold chips, bake 375F, 10 minutes"]
     [R2D2: "understood"]
\`\`\`

### Example 3: Conversation
\`\`\`
You: "Hey Olaf"
Bot: [Happy R2D2 beep]

You: "How are you?"
Bot: [R2D2: "olaf feel good"]

You: "What can you do?"
Bot: [R2D2: "data ready"]
     [Transmission: "OLAF voice assistant, droid personality, handles queries"]
     [R2D2: "understood"]

You: "That's cool. Goodbye!"
Bot: [R2D2: "sleep mode"]
     [Transmission: "Say my wake word to activate"]
     [R2D2: "understood"]
\`\`\`

---

## 🎯 Roadmap

**Completed:**
- ✅ Bumblebee-style hybrid TTS
- ✅ Wake word activation
- ✅ Smart VAD with noise filtering
- ✅ English-only mode
- ✅ High-quality voices
- ✅ Audio effects
- ✅ Structured LLM responses
- ✅ Clean package structure

**Planned:**
- ⏳ Web interface
- ⏳ Docker container
- ⏳ Alternative LLM backends (Ollama, etc.)
- ⏳ Multi-language support
- ⏳ Mobile app
- ⏳ Home Assistant integration
- ⏳ Custom wake word training

---

## 🙏 Credits

**Built with:**
- [Faster Whisper](https://github.com/guillaumekln/faster-whisper) - Speech recognition
- [Piper TTS](https://github.com/rhasspy/piper) - Neural text-to-speech
- [Groq](https://groq.com/) - Fast LLM inference
- [Picovoice Porcupine](https://picovoice.ai/) - Wake word detection
- [WebRTC VAD](https://github.com/wiseman/py-webrtcvad) - Voice activity detection

**Inspired by:**
- R2D2 from Star Wars
- Bumblebee from Transformers
- JARVIS from Iron Man

---

**Ready to build your own R2D2 chatbot? Start with the Quick Start section above!** 🚀
