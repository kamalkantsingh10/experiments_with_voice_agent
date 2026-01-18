# R2D2-Like Chatbot

A voice assistant that communicates like Bumblebee from Transformers - using expressive R2D2 beeps and chirps for reactions, then switching to clear voice transmission for specific information.

## Features

- **Wake Word Activation** - "Hey Olaf" or "Alexa" to activate
- **Voice Activity Detection** - Smart recording that stops when you finish speaking
- **Speech Recognition** - Whisper-based STT (local, private, English-only)
- **AI-Powered Responses** - Groq Llama 3.1 (fast, free tier available)
- **Hybrid TTS Output**:
  - R2D2 chirps/beeps for reactions and acknowledgments
  - High-quality voice with radio effects for specific information
- **Star Wars Audio Effects** - Radio transmission, comlink, hologram styles
- **Noise Filtering** - Ignores typing and background sounds

## Quick Start

### Prerequisites

- Python 3.8+
- Linux/macOS
- Microphone and speakers
- API keys: Groq (free), Picovoice (free tier)

### Installation

```bash
cd r2d2-like-chatbot
pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your API keys:
#   GROQ_API_KEY=your_groq_key
#   PICOVOICE_API_KEY=your_picovoice_key
```

### Basic Usage

```python
from r2d2_chatbot.agent import R2D2ChatbotAgent

agent = R2D2ChatbotAgent()
agent.run()
```

Say your wake word, then start talking.

## Configuration

Edit `r2d2_chatbot/config.py` or create custom Config objects:

```python
from r2d2_chatbot.agent import R2D2ChatbotAgent
from r2d2_chatbot.config import Config

config = Config()
config.TTS_VOICE = 'male'           # 'male' or 'female'
config.TTS_EFFECT = 'comlink'       # 'clear_transmission', 'comlink', 'radio', 'hologram'
config.USE_WAKE_WORD = False        # Disable wake word (press Enter instead)
config.VAD_AGGRESSIVENESS = 3       # 0-3, higher = more noise filtering

agent = R2D2ChatbotAgent(config=config)
agent.run()
```

### Voice Settings

| Setting | Options |
|---------|---------|
| `TTS_VOICE` | `'female'` (ljspeech-high), `'male'` (alan-medium) |
| `TTS_EFFECT` | `'clear_transmission'`, `'comlink'`, `'radio'`, `'hologram'`, `'dramatic'`, `'clear'` |

### VAD Settings (Noise Filtering)

| Setting | Default | Description |
|---------|---------|-------------|
| `VAD_AGGRESSIVENESS` | 2 | 0-3, higher = more aggressive filtering |
| `VAD_SPEECH_THRESHOLD` | 8 | Frames needed to start recording |
| `VAD_MIN_DURATION` | 1.5 | Minimum recording duration in seconds |

**Tips:**
- Typing sounds? Increase `VAD_SPEECH_THRESHOLD` to 10
- Objects falling? Increase `VAD_MIN_DURATION` to 2.0
- Too sensitive? Increase `VAD_AGGRESSIVENESS` to 3

## How It Works

1. **Listens** - Wake word activates, VAD records until you stop speaking
2. **Understands** - Whisper transcribes speech to text
3. **Thinks** - LLM generates structured response with R2D2 reaction + optional info
4. **Responds**:
   - R2D2 chirp/beep (acknowledges with emotion)
   - Voice transmission (delivers information with radio effect)
   - R2D2 confirmation

### Example

```
You: "Tell me a pancake recipe"

Bot:
  [R2D2 chirp: "recipe found"]
  [TRANSMISSION: "1 cup flour, 2 tbsp sugar, 1 egg, 1 cup milk, mix, cook medium heat"]
  [R2D2: "understood"]
```

## API Keys Setup

### Groq (Required)

1. Go to https://console.groq.com/
2. Sign up and create API key
3. Add to `.env`: `GROQ_API_KEY=gsk_your_key_here`

Free tier: 14,400 requests/day

### Picovoice (Required for wake word)

1. Go to https://console.picovoice.ai/
2. Sign up and create access key
3. Add to `.env`: `PICOVOICE_API_KEY=your_key_here`

Free tier: 3 wake word models

## Project Structure

```
r2d2_chatbot/
├── agent.py              # Main R2D2ChatbotAgent class
├── config.py             # Configuration settings
├── audio/
│   ├── wakeword.py       # Picovoice wake word detection
│   └── vad.py            # Voice activity detection
├── speech/
│   ├── stt.py            # Whisper speech-to-text
│   └── tts/
│       ├── piper.py      # Piper TTS
│       ├── r2d2.py       # R2D2 sound generator
│       └── effects.py    # Audio effects
└── llm/
    └── groq_client.py    # Groq LLM client

examples/
├── basic.py              # Simple example
└── bumblebee.py          # Full-featured example
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Wake word not detected | Check mic, verify API key, try `USE_WAKE_WORD = False` |
| Picks up background noise | Increase `VAD_AGGRESSIVENESS` to 3 |
| Wrong language transcription | Already fixed with `language='en'` parameter |
| Audio quality issues | Use `TTS_VOICE = 'female'` and `TTS_EFFECT = 'clear_transmission'` |

## Privacy

All processing is local except LLM:

| Component | Location |
|-----------|----------|
| Wake word (Porcupine) | Local |
| VAD (WebRTC) | Local |
| STT (Whisper) | Local |
| TTS (Piper) | Local |
| R2D2 sounds | Local |
| LLM (Groq) | Cloud |

Audio never leaves your device - only transcribed text goes to the LLM.

## Credits

Built with [Faster Whisper](https://github.com/guillaumekln/faster-whisper), [Piper TTS](https://github.com/rhasspy/piper), [Groq](https://groq.com/), [Picovoice Porcupine](https://picovoice.ai/), and [WebRTC VAD](https://github.com/wiseman/py-webrtcvad).

Inspired by R2D2 (Star Wars) and Bumblebee (Transformers).
