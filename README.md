# Voice Agent for Raspberry Pi 5

A local voice agent running on Raspberry Pi 5 with local speech processing and cloud LLM integration.

## Overview

This project implements a voice-activated AI agent that:
- 🎤 Listens and transcribes speech locally using Faster-Whisper
- 🧠 Processes requests using Claude API (cloud)
- 🤖 Responds with R2D2-style phonetic speech (text-to-beeps with rhythm hints)
- 🎵 Pure procedural audio synthesis - no models required
- ⚡ Runs entirely on Raspberry Pi 5 with ~1-2 second latency

## Features

- **Privacy-focused**: All speech processing happens locally on your Pi
- **Low latency**: Optimized for real-time conversation
- **Modular**: Easy to swap components (STT, TTS, LLM)
- **Hailo-ready**: Prepared for NPU acceleration (future optimization)

## Hardware Requirements

- Raspberry Pi 5 (8GB recommended)
- USB microphone
- Speaker or headphones
- Optional: Hailo AI Kit for acceleration

## Quick Start

1. **Install system dependencies:**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y portaudio19-dev python3-pyaudio git espeak-ng
```

2. **Install Python dependencies:**
```bash
poetry install
```

3. **Configure API key:**
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

4. **Run the voice agent:**
```bash
poetry run python voice_agent.py
```

## R2D2 Phonetic Text-to-Speech

The R2D2 voice synthesizer now supports phonetic text-to-speech, converting text into R2D2 sounds with subtle rhythmic hints:

```python
from r2d2_voice import R2D2Voice

voice = R2D2Voice()

# Play phonetic speech directly (no saving needed!)
# Default is 3x speed - snappy R2D2 responses!
voice.play_text("I am good", emotion='happy')

# Generate audio without playing
audio = voice.speak_text("I am good", emotion='happy')
# → Returns audio with 3 word clusters, high pitch, fast

# EXTREME emotion differences!
voice.play_text("Hello", emotion='excited')   # Pitch 3.0x, Speed 0.5x (2x faster)
voice.play_text("Hello", emotion='sleepy')    # Pitch 0.5x, Speed 3.0x (3x slower)
voice.play_text("Hello", emotion='happy')     # Pitch 2.5x, bouncy
voice.play_text("Hello", emotion='sad')       # Pitch 0.6x, very slow
voice.play_text("Hello", emotion='afraid')    # Pitch 2.2x, jittery

# Control speed (optional - default is 3.0)
voice.play_text("Testing")                   # Default 3x speed
voice.play_text("Testing", speed=1.0)        # 3x slower
voice.play_text("Testing", speed=5.0)        # 1.67x faster

# Control clarity (phonetic hints vs emotion)
voice.play_text("Testing", emotion='happy', clarity=0.1)  # More emotion
voice.play_text("Testing", emotion='happy', clarity=0.8)  # More phonetic

# Save to file if needed
voice.save_text("I am good", "output.wav", emotion='happy')

# Backward compatible - old API still works
voice.play(emotion='excited')  # Random excited sounds
```

### How it Works

1. **Text → Phonemes**: Uses `phonemizer` library with `espeak-ng` to convert text to IPA phonemes
2. **Phoneme Categories**: Groups phonemes (vowels, plosives, fricatives, nasals, approximants)
3. **Sound Mapping**: Maps each category to R2D2 sounds (beeps, boops, whistles, chirps, etc.)
4. **Emotion Blending**: Applies pitch shifts and speed changes based on emotion
5. **Rhythm**: Word boundaries create recognizable structure through timing gaps

### API Reference

```python
R2D2Voice.speak_text(
    text: str,
    emotion: str = 'happy',         # 10 emotions with EXTREME variations
    intensity: float = 1.0,         # Volume level (0.0-2.0)
    clarity: float = 0.3,           # Phonetic hints (0.0=pure emotion, 1.0=pure phonetics)
    speed: float = 3.0              # Playback speed (default: 3.0 = snappy!)
) -> np.ndarray
```

**Parameters:**
- `speed=3.0` - **Default** - Snappy R2D2 responses!
- `speed=1.0` - 3x slower (drawn out)
- `speed=5.0` - 1.67x faster (very quick)

**10 EXTREME Emotions (Pitch: 0.5x-3x, Speed: 0.5x-3x):**

| Emotion | Pitch | Speed | Character |
|---------|-------|-------|-----------|
| excited | 3.0x ⬆⬆⬆ | 0.5x ⚡⚡ | Extremely high & rapid |
| happy | 2.5x ⬆⬆ | 0.6x ⚡ | Very high & bouncy |
| afraid | 2.2x ⬆⬆ | 0.65x ⚡ | High & jittery |
| surprised | 1.9x ⬆ | 0.7x ⚡ | High & sudden |
| playful | 1.7x ⬆ | 0.8x ⚡ | High & bouncy |
| curious | 1.5x ⬆ | 1.2x ⏱ | Med-high & thoughtful |
| confident | 1.2x | 0.9x | Steady & assertive |
| angry | 0.7x ⬇ | 0.75x ⚡ | Low & aggressive |
| sad | 0.6x ⬇⬇ | 2.0x ⏱⏱ | Very low & slow |
| sleepy | 0.5x ⬇⬇⬇ | 3.0x ⏱⏱⏱ | Extremely low & drowsy |

### System Requirements

- **espeak-ng**: Required for phoneme conversion
  ```bash
  sudo apt-get install espeak-ng
  ```
- **phonemizer**: Automatically installed via poetry
  ```bash
  poetry install
  ```

### Testing

Run the test suite to verify installation:

```bash
# Basic structure test (no espeak-ng needed)
poetry run python test_basic_structure.py

# Full phonetic speech tests (requires espeak-ng)
poetry run python test_phonetic_speech.py

# Original emotion-only tests
poetry run python test_r2d2.py
```

## Documentation

See [TUTORIAL.md](TUTORIAL.md) for detailed step-by-step instructions.

## Tech Stack

- **Orchestration**: [Pipecat](https://github.com/pipecat-ai/pipecat)
- **Speech-to-Text**: [Faster-Whisper](https://github.com/guillaumekln/faster-whisper)
- **Voice Output**: Custom R2D2-style procedural synthesis
- **LLM**: [Claude API](https://www.anthropic.com/api)

## Project Status

🚧 In development - See [TUTORIAL.md](TUTORIAL.md) for current progress

## License

MIT

## Acknowledgments

Built for experimentation with local voice agents and AI acceleration on edge devices.
