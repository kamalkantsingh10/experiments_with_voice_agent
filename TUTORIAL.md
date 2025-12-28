# Voice Agent Tutorial for Raspberry Pi 5

This tutorial will guide you through building a voice agent that runs on your Raspberry Pi 5. We'll use local speech recognition and R2D2-style emotive sounds for low latency and privacy, while leveraging cloud LLMs for intelligent responses.

**Stack:** Pipecat + Faster-Whisper + R2D2 Voice + Claude API

**Hardware:** Pi 5 (8GB), USB mic, speaker

**What you'll build:** A voice agent that listens to your voice, transcribes it locally, sends the text to Claude for processing, and responds with emotive R2D2-style sounds - all with ~1-2 second latency.

---

## Section 1: Install Pipecat

Pipecat is our orchestration framework that will tie together all the components. It's a Python framework designed specifically for building voice agents, and it runs entirely on your Pi.

**Prerequisites:** Poetry installed ([install guide](https://python-poetry.org/docs/#installation))

### System Dependencies

First, we need to install audio libraries that allow Python to interact with your microphone and speakers.

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y portaudio19-dev python3-pyaudio git
```

### Install Dependencies

All project dependencies are already defined in `pyproject.toml`. Simply run:

```bash
cd ~/Documents/Garage/experiments_with_voice_agent
poetry install
```

This installs everything you need in an isolated virtual environment:
- **pipecat-ai**: Voice agent orchestration framework
- **pyaudio & sounddevice**: Audio input/output handling
- **faster-whisper**: Local speech-to-text
- **anthropic**: Claude API client
- **python-dotenv**: Environment variable management

### Verify Installation

Let's make sure everything is working correctly.

```bash
poetry run python -c "import pipecat; print('✓ Pipecat installed successfully')"
```

You should see: `✓ Pipecat installed successfully`

### Test Audio Devices

This command lists all available microphones and speakers on your Pi. You'll need this information later when configuring audio input/output.

```bash
poetry run python -c "import sounddevice as sd; print(sd.query_devices())"
```

Look for your USB microphone in the input devices and your speaker in the output devices.

**Troubleshooting:**
- Audio permissions: `sudo usermod -a -G audio $USER` (then logout/login)
- Missing portaudio: `sudo apt install portaudio19-dev`

**Note:** All Python commands must be run with `poetry run` prefix, or you can enter the Poetry shell with `poetry shell`.

---

## Section 2: Setup Local STT (Whisper Small)

We'll use Faster-Whisper, an optimized implementation of OpenAI's Whisper model. The Small model provides a good balance between accuracy (~8-10% WER) and performance on Pi 5.

**Why Whisper Small:**
- Better accuracy than Tiny/Base models
- 244MB model size (manageable on Pi 5)
- ~500-800ms transcription latency
- Good multilingual support

**Note:** The Small model may cause some thermal load. Monitor your Pi's temperature during extended use.

### Verify Faster-Whisper Installation

Faster-Whisper is already installed via `poetry install`. Let's verify:

```bash
poetry run python -c "from faster_whisper import WhisperModel; print('✓ Faster-Whisper ready')"
```

### Download and Test Whisper Small Model

Run the provided test script to download the model and test transcription:

```bash
poetry run python test.py
```

**What happens:**
1. Downloads ~244MB Whisper Small model (first run only, cached afterward)
2. Loads the model with int8 optimization
3. Gives you a 3-second countdown
4. Records 5 seconds of audio from your microphone
5. Transcribes your speech and shows results with timestamps
6. Displays performance metrics (transcription time vs real-time)

**When prompted, speak clearly:** "Hello, this is a test"

The script will show you the transcription accuracy and whether it's running faster than real-time.

### Performance Expectations

| Metric | Value |
|--------|-------|
| Model Size | 244MB |
| First Load | ~5-10 seconds |
| Cached Load | ~2-3 seconds |
| Transcription (5s audio) | ~500-800ms |
| Word Error Rate | ~8-10% |

---

## Section 3: Setup R2D2 Voice Generator (TTS Alternative)

Instead of traditional text-to-speech, we're using an R2D2-style emotive droid voice. Your agent will communicate through expressive sounds - beeps, boops, whistles, and chirps - that vary based on emotion and create a unique "word vocabulary" for consistent personality.

**Why R2D2 Voice:**
- ✅ Zero model downloads (pure procedural synthesis)
- ✅ < 5MB code footprint vs 100s of MB for TTS models
- ✅ < 50ms generation latency (instant)
- ✅ More personality and character
- ✅ Unique companion experience
- ✅ Research-backed emotion mapping

**How it works:**
- **Word Vocabulary Approach:** Each of 500 common words maps to a unique 1-5 note "melody"
- **Emotion-Driven Selection:** Emotion controls which sounds are picked from 12 primitives
- **Pitch & Speed Modulation:** Emotions adjust pitch (0.6x-1.6x) and speed (0.5x-1.8x)
- **Psychoacoustic Design:** Based on published research linking pitch, brightness, and emotion
- **Consistent Identity:** Same word always has same length, creating recognizable patterns

### Verify Dependencies

The R2D2 voice generator needs numpy and scipy:

```bash
poetry install
```

This installs the required packages for audio synthesis.

### Test the R2D2 Word Vocabulary System

Run the comprehensive demo to hear the word-based system:

```bash
poetry run python demo_word_vocabulary.py
```

**What happens:**
1. **Demo 1:** Same sentence ("I am happy to help you") in all 10 emotions
2. **Demo 2:** Different sentences in happy emotion
3. **Demo 3:** Emotion contrast pairs (excited vs lazy, happy vs sad, etc.)
4. **Demo 4:** Word length consistency - each word has fixed note count
5. **Demo 5:** Unknown word handling - unmapped words get 2 random notes
6. **Demo 6:** Star Wars R2D2 phrases with emotions
7. **Demo 7:** Saves 4 example WAV files to disk

**You'll hear:**
- Each word has a unique "melody" (1-5 notes)
- Emotions dramatically change the character
- Happy sounds bright and chirpy (high pitch, fast)
- Sad sounds dull and slow (low pitch, slow)
- 12 different sound primitives creating rich expressiveness

### Understanding the 12 Sound Primitives

| Sound | Frequency | Character | Best For |
|-------|-----------|-----------|----------|
| `ping` | Very High (4590 Hz) | Sharp, metallic | Excited, alerts |
| `blip` | Very High (3005 Hz) | Quick, bright | Happy, playful |
| `buzz` | Very High (5454 Hz) | Harsh, rough | Angry, frustrated |
| `chirp` | High (2484 Hz) | Bird-like, cheerful | Happy, excited |
| `beep` | Medium (1017 Hz) | Clean, neutral | Affirmative |
| `stutter` | Medium (1515 Hz) | Rapid bursts | Nervous, afraid |
| `warble` | Medium (1133 Hz) | Wobbly, uncertain | Confused, curious |
| `tremolo` | Medium (1203 Hz) | Pulsing, trembling | Afraid, nervous |
| `slide_down` | Medium (1361 Hz) | Descending sweep | Sad, disappointed |
| `sweep_up_down` | Medium (1792 Hz) | Rise then fall | Confused, questioning |
| `boop` | Low (303 Hz) | Soft, mellow | Sad, lazy |
| `chord` | Low (724 Hz) | Harmonic, pleasant | Calm, content |

### Understanding the 10 Emotions

| Emotion | Pitch | Speed | Preferred Sounds | Use Cases |
|---------|-------|-------|------------------|-----------|
| `happy` | 1.4x (high) | 1.3x (fast) | chirp, ping, blip, chord | Positive responses |
| `sad` | 0.7x (low) | 0.6x (slow) | slide_down, boop, tremolo | Empathy, bad news |
| `angry` | 0.6x (low) | 1.4x (fast) | buzz, stutter | Frustration, warnings |
| `excited` | 1.6x (very high) | 1.8x (very fast) | chirp, ping, blip, stutter | Great news, achievements |
| `curious` | 1.3x (med-high) | 0.9x (slow) | sweep_up_down, warble, boop | Questions, exploring |
| `neutral` | 1.0x (normal) | 1.0x (normal) | Balanced mix | Default, informational |
| `confused` | 1.2x (med-high) | 0.8x (slow) | warble, sweep_up_down, tremolo | Uncertainty, errors |
| `lazy` | 0.65x (very low) | 0.5x (very slow) | boop, slide_down, buzz | Low energy, sleepy |
| `afraid` | 1.5x (high) | 1.5x (fast) | stutter, tremolo, beep, warble | Warnings, danger |
| `naughty` | 1.35x (med-high) | 1.2x (fast) | chirp, blip, ping, sweep_up_down | Playful, mischievous |

### Performance Expectations

| Metric | Value |
|--------|-------|
| Code Size | < 5MB |
| Generation Latency | < 50ms |
| Memory Usage | < 10MB |
| Model Downloads | None! |
| Audio Quality | 44.1kHz, 16-bit |
| Word Vocabulary | 500 common words |
| Sound Primitives | 12 unique sounds |

### Integration Preview

In Section 5, we'll use the word vocabulary system for responses:

```python
# User: "What's the weather?"
# Claude: "It's sunny and warm!"
# Emotion detection: "happy"
voice.play_sentence("sunny and warm", emotion="happy")
# R2D2: *3-word melody with chirpy, bright sounds*

# User: "My code has a bug"
# Claude: "Let me help you debug that"
# Emotion detection: "curious"
voice.play_sentence("help debug", emotion="curious")
# R2D2: *2-word melody with questioning, warble sounds*
```

### Validate Your Emotion Weights (Optional)

Want to see how your emotions align with psychoacoustic research? Run the validation:

```bash
poetry run python validate_emotion_weights.py
```

**What it shows:**
- Spectral analysis of all 10 emotions
- Sound primitive brightness/frequency measurements
- Alignment with published research (PNAS, Sage Journals, PMC)
- Recommendations for fine-tuning

**Research Validation:**
Your system is built on peer-reviewed findings:
- High pitch (>2000 Hz) → joy, excitement, fear ✓
- Low pitch (<1000 Hz) → sadness, calmness ✓
- Happy speech: mean 254 Hz, high registers ✓
- Sad speech: mean 212 Hz, low registers ✓

### Customization (Optional)

**Adjust Emotion Intensity:** Edit `r2d2_word_vocabulary.py`:

```python
# Make happy even brighter
EMOTION_PITCH = {
    'happy': 1.6,  # Was 1.4 (increase for higher pitch)
}

# Make excited faster
EMOTION_SPEED = {
    'excited': 2.0,  # Was 1.8 (increase for faster)
}
```

**Adjust Sound Selection Weights:** Edit emotion preferences:

```python
# Make happy use more chirps
EMOTION_SOUND_WEIGHTS = {
    'happy': {
        'chirp': 3.0,  # Was 2.5 (increase weight)
        'ping': 2.5,   # Was 2.0
    }
}
```

### Alternative: Phoneme-Based Approach

We also provide a phoneme-based system (`r2d2_voice.py`) that maps IPA phonemes to sounds. This creates more speech-like patterns but requires phonemizer installation:

```bash
sudo apt-get install espeak-ng
pip install phonemizer
poetry run python demo_play_text.py
```

The word vocabulary approach is recommended for most use cases.

### Troubleshooting

**Issue: No audio plays**
```bash
# Check audio output devices
poetry run python -c "import sounddevice as sd; print(sd.query_devices())"

# Test system audio
speaker-test -t wav -c 2
```

**Issue: Audio is clipped/distorted**
- Lower the `amplitude` parameter in `r2d2_word_vocabulary.py`
- Default is 0.4, try 0.3

**Issue: Validation shows low alignment**
- This is normal! Sound selection varies per sentence
- Try validation with different phrases
- The system is designed for variety and expressiveness

**Issue: Want different sound for a word**
- Words map deterministically via hash
- Change the seed in `R2D2WordVocabulary(seed=42)`
- Or modify `_initialize_word_lengths()` for custom mappings

---

## Section 3.5: Setup Piper TTS & Hybrid Voice System

Now we'll add **Piper TTS** for intelligible speech and combine it with R2D2 sounds to create the ultimate hybrid voice agent!

**Why Hybrid Voice:**
- ✅ **R2D2**: Instant emotional feedback (<50ms)
- ✅ **Piper TTS**: Clear, understandable responses
- ✅ **Best UX**: User hears acknowledgment immediately, then gets full answer
- ✅ **Star Wars Effects**: Comlink, hologram, radio transmission DSP

### Install Piper TTS

Piper is already in your dependencies. The models auto-download on first use:

```bash
poetry install  # Already done!
```

### Download Voice Models

Voice models download automatically when you first use them. We're using British voices:
- **Female**: `en_GB-alba-medium` (~150MB)
- **Male**: `en_GB-alan-medium` (~150MB)

### Test Piper TTS

Run the working test:

```bash
poetry run python test_piper_working.py
```

You should hear: "Hello, I am a British female voice assistant."

### Understanding the Hybrid System

The `HybridVoiceAgent` combines three components:

1. **R2D2 acknowledgment** - Instant emotional beep
2. **Piper TTS** - Clear speech generation
3. **Radio effects** - Star Wars-style DSP processing

**Flow:**
```
User speaks
    ↓
[Instant R2D2 beep] ← User hears this immediately!
    ↓
[Generate Piper TTS] ← Takes 500ms-1s
    ↓
[Apply comlink effect] ← Add radio character
    ↓
[Play response] ← User hears full answer
```

### Radio Effects Available

**Comlink** (Recommended - Clearest):
- Military radio with squelch tones
- Band-pass filter (250Hz-4000Hz)
- Minimal static for clarity
- Perfect for daily assistant use

**Hologram**:
- Glitchy transmission (like Leia's message)
- Random dropouts (4%)
- Tinny, futuristic sound
- Great for special messages

**Radio**:
- Classic radio transmission
- More static and distortion
- Vintage communication feel

### Test the Hybrid System

Run the complete demo with 20 Star Wars scenarios:

```bash
poetry run python demo_hybrid_voice.py
```

**What happens:**
1. OLAF responds to 20 daily tasks
2. Each starts with R2D2 acknowledgment
3. Then speaks clear response via comlink
4. Uses Star Wars terminology!

**Example outputs:**
- "Atmospheric conditions stable, 22 degrees celsius, no hostile weather detected"
- "Security protocols engaged, all entry points sealed"
- "Accessing your cantina music collection, preparing playback systems"

### Code Structure

**Key Files:**
- `piper_tts.py` - Piper TTS wrapper with British voices
- `radio_effects.py` - DSP effects (comlink, hologram, radio)
- `demo_hybrid_voice.py` - Complete hybrid voice agent
- `r2d2_word_vocabulary.py` - R2D2 sound generator

### Customization

**Change voice:**
```python
# Female voice (default)
agent = HybridVoiceAgent(tts_voice='female')

# Male voice
agent = HybridVoiceAgent(tts_voice='male')
```

**Change effect:**
```python
# Comlink (clearest)
agent.respond("Message", effect='comlink')

# Hologram (glitchy)
agent.respond("Message", effect='hologram')

# Clear (no effect)
agent.respond("Message", effect='clear')
```

**Change R2D2 emotion:**
```python
agent.respond("Message", acknowledge_emotion='excited')  # High-pitched beep
agent.respond("Message", acknowledge_emotion='curious')  # Questioning beep
agent.respond("Message", acknowledge_emotion='happy')    # Cheerful beep
```

### Performance

| Component | Latency | Size |
|-----------|---------|------|
| R2D2 acknowledgment | <50ms | <5MB |
| Piper voice model | - | ~150MB |
| TTS generation | 500ms-1s | - |
| Radio effect | <50ms | Negligible |
| **Total perceived latency** | <100ms | User hears beep instantly! |

### Integration Preview

In the full voice pipeline, this will work as:

```python
# User: "What's the weather?"

# 1. Whisper transcribes locally
# 2. Send to Claude API
# 3. Claude responds: "It's 72 degrees and sunny"
# 4. OLAF speaks:
agent.respond(
    "Atmospheric conditions stable, 72 degrees celsius.",
    effect='comlink',
    acknowledge_emotion='curious'
)
```

Perfect user experience - instant feedback + clear information!

### Troubleshooting

**Issue: Voice model download fails**
- Check internet connection
- Models are ~150MB each
- Downloaded to `./piper_models/` directory

**Issue: Static too loud**
- Edit `radio_effects.py`
- Reduce `static_level` parameter
- Comlink already optimized for clarity

**Issue: Voice not clear enough**
- Use `effect='clear'` (no DSP)
- Or adjust band-pass filter in `radio_effects.py`

**Issue: R2D2 too loud/quiet**
- Adjust in `r2d2_word_vocabulary.py`
- Or change volume in agent code

---

## Section 4: Setup VAD & Wake Word Detection

Before connecting to the cloud LLM, we need two critical components for proper voice interaction:

1. **VAD (Voice Activity Detection)** - Detects when user is speaking vs silence
2. **Wake Word Detection** - Triggers agent activation ("Hey OLAF")

**Why these are critical:**
- VAD prevents transcribing background noise and silence
- Wake word enables privacy (not always listening)
- Both reduce unnecessary cloud API calls
- Improves turn-taking and responsiveness
- Lower latency by only processing actual speech

### Architecture Overview

```
Microphone → Wake Word (openWakeWord) → VAD (Pipecat) → Whisper → Claude → R2D2
              ↓                          ↓
           "Hey OLAF" detected      Speech/Silence detection
```

### Our Stack

We'll use:
- **VAD:** Pipecat SileroVADAnalyzer (built-in, ONNX-based, accurate)
- **Wake Word:** openWakeWord (open source, free, customizable)

**Why this combination:**
- ✅ Pipecat VAD is built-in - seamless integration
- ✅ openWakeWord is fully open source - no API keys or limits
- ✅ Both run locally on Pi 5 - privacy preserved
- ✅ Combined CPU usage: ~10-15% on Pi 5
- ✅ Can train custom "Hey OLAF" wake word

**Alternatives considered:**
- Porcupine (more accurate but proprietary, requires API key)
- WebRTC VAD (lighter but less accurate than Pipecat's Silero)

### Install Dependencies

Pipecat already includes VAD. We just need to add openWakeWord:

```bash
poetry add openwakeword
```

This installs:
- openWakeWord library
- Pre-trained models (hey_mycroft, alexa, etc.)
- TFLite runtime for inference

**Note:** openWakeWord uses TFLite (lightweight TensorFlow), not full PyTorch!

### Understanding VAD (Voice Activity Detection)

**What it does:**
- Analyzes audio in real-time (frame by frame)
- Returns probability: 0.0 (silence) to 1.0 (speech)
- Typically use threshold ~0.5 to trigger "speech detected"

**Silero VAD specs:**
- Model size: ~2MB (tiny!)
- Latency: ~10-30ms per frame
- Accuracy: ~95%+ in normal conditions
- Works with 8kHz or 16kHz audio

### Test Silero VAD

Create `test_vad.py`:

```python
#!/usr/bin/env python3
"""Test Silero VAD (Voice Activity Detection)"""

import torch
import sounddevice as sd
import numpy as np

# Load Silero VAD model
model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                              model='silero_vad',
                              force_reload=False)

(get_speech_timestamps,
 save_audio,
 read_audio,
 VADIterator,
 collect_chunks) = utils

# Audio settings
SAMPLE_RATE = 16000
CHUNK_SIZE = 512  # 32ms chunks at 16kHz

print("=" * 60)
print("SILERO VAD TEST")
print("=" * 60)
print(f"Sample rate: {SAMPLE_RATE} Hz")
print(f"Chunk size: {CHUNK_SIZE} samples ({CHUNK_SIZE/SAMPLE_RATE*1000:.1f}ms)")
print()
print("Speak into your microphone. VAD will detect speech vs silence.")
print("Speech probability shown in real-time.")
print("Press Ctrl+C to stop.")
print("=" * 60)
print()

def audio_callback(indata, frames, time, status):
    """Process audio in real-time"""
    if status:
        print(f"Status: {status}")

    # Convert to torch tensor
    audio_chunk = torch.from_numpy(indata.copy().flatten())

    # Get speech probability
    speech_prob = model(audio_chunk, SAMPLE_RATE).item()

    # Visual indicator
    bar_length = int(speech_prob * 50)
    bar = "█" * bar_length + "░" * (50 - bar_length)

    # Color based on threshold
    if speech_prob > 0.5:
        indicator = "🎤 SPEECH"
    else:
        indicator = "🔇 SILENCE"

    print(f"\r{indicator} [{bar}] {speech_prob:.3f}", end="", flush=True)

try:
    with sd.InputStream(samplerate=SAMPLE_RATE,
                       channels=1,
                       blocksize=CHUNK_SIZE,
                       callback=audio_callback):
        print("Listening... (Ctrl+C to stop)")
        while True:
            sd.sleep(100)
except KeyboardInterrupt:
    print("\n\nVAD test complete!")
```

Run it:

```bash
poetry run python test_vad.py
```

**What you'll see:**
- Real-time bar graph showing speech probability
- 🎤 SPEECH indicator when you talk
- 🔇 SILENCE when quiet
- Values from 0.000 (silence) to 1.000 (definite speech)

### Understanding Wake Word Detection

**What it does:**
- Continuously listens for specific trigger phrase
- Only activates agent when wake word detected
- Runs locally (no cloud API needed)
- Low CPU usage (~5-10%)

**openWakeWord features:**
- Pre-trained models: "hey mycroft", "alexa", etc.
- Custom wake word training possible
- Model size: 10-50MB depending on wake word
- Latency: ~50-100ms detection delay

### Install openWakeWord

Already installed via `poetry add openwakeword`. Now download a wake word model:

```bash
# Create models directory
mkdir -p models/wake_word

# Download "hey mycroft" model (we'll use this as "hey OLAF" for now)
# You can train a custom "hey OLAF" model later
```

**Available pre-trained models:**
- `hey_mycroft_v0.1.tflite` - "Hey Mycroft"
- `alexa_v0.1.tflite` - "Alexa"
- Custom models can be trained on your voice

For now, we'll use a simple approach and create our own test.

### Test Wake Word Detection

Create `test_wake_word.py`:

```python
#!/usr/bin/env python3
"""Test Wake Word Detection using openWakeWord"""

import sounddevice as sd
import numpy as np
from openwakeword.model import Model

# Audio settings
SAMPLE_RATE = 16000
CHUNK_SIZE = 1280  # 80ms chunks

print("=" * 60)
print("WAKE WORD DETECTION TEST")
print("=" * 60)
print()

# Initialize model
# Default: uses "hey_mycroft" model
# For testing, we'll treat this as "hey OLAF"
try:
    oww_model = Model(
        wakeword_models=["hey_mycroft"],  # Use built-in model
        inference_framework="tflite"
    )
    print("✓ Wake word model loaded successfully")
    print(f"  Listening for: 'Hey Mycroft' (pretend it's 'Hey OLAF')")
except Exception as e:
    print(f"✗ Error loading model: {e}")
    print()
    print("Note: openWakeWord may need additional setup.")
    print("For now, we'll use a simple energy-based wake word.")
    print("You can train a custom 'Hey OLAF' model later.")
    exit(1)

print()
print("Speak the wake word to activate.")
print("Press Ctrl+C to stop.")
print("=" * 60)
print()

def audio_callback(indata, frames, time, status):
    """Process audio for wake word detection"""
    if status:
        print(f"Status: {status}")

    # Convert to format expected by model
    audio_chunk = indata.copy().flatten()

    # Predict wake word
    prediction = oww_model.predict(audio_chunk)

    # Check if wake word detected
    for wake_word, score in prediction.items():
        if score > 0.5:  # Threshold
            print(f"\n🎯 WAKE WORD DETECTED! ({wake_word}: {score:.3f})")
            print("Agent activated! (would start listening now)")
            print()
        else:
            # Show low scores occasionally
            if score > 0.1:
                bar = "▌" * int(score * 20)
                print(f"\r{wake_word}: [{bar:<20}] {score:.3f}", end="", flush=True)

try:
    with sd.InputStream(samplerate=SAMPLE_RATE,
                       channels=1,
                       blocksize=CHUNK_SIZE,
                       dtype=np.float32,
                       callback=audio_callback):
        print("Listening for wake word... (Ctrl+C to stop)")
        while True:
            sd.sleep(100)
except KeyboardInterrupt:
    print("\n\nWake word test complete!")
except Exception as e:
    print(f"\nError: {e}")
```

Run it:

```bash
poetry run python test_wake_word.py
```

**What you'll see:**
- Continuous monitoring for wake word
- Score bar showing detection confidence
- 🎯 Alert when wake word detected
- Low CPU usage while listening

### Alternative: Simple Energy-Based Wake Word

If openWakeWord setup is complex, here's a simple alternative using audio energy:

Create `test_simple_wake_word.py`:

```python
#!/usr/bin/env python3
"""Simple wake word using audio energy threshold"""

import sounddevice as sd
import numpy as np
import time

SAMPLE_RATE = 16000
CHUNK_SIZE = 1600  # 100ms

print("=" * 60)
print("SIMPLE WAKE WORD (Energy-Based)")
print("=" * 60)
print()
print("This detects a sharp, loud sound as wake trigger.")
print("Clap your hands or say 'HEY' loudly to trigger.")
print()
print("Press Ctrl+C to stop.")
print("=" * 60)
print()

# Activation state
activated = False
activation_time = 0

def audio_callback(indata, frames, time_info, status):
    global activated, activation_time

    # Calculate audio energy (RMS)
    energy = np.sqrt(np.mean(indata**2))

    # Threshold for wake trigger (adjust as needed)
    THRESHOLD = 0.1

    if energy > THRESHOLD and not activated:
        activated = True
        activation_time = time.time()
        print(f"\n🎯 WAKE TRIGGER! (energy: {energy:.3f})")
        print("Agent activated for 5 seconds!")

    # Deactivate after 5 seconds
    if activated and time.time() - activation_time > 5:
        activated = False
        print("\n💤 Agent deactivated (timeout)")

    # Visual feedback
    if activated:
        status_icon = "🎤 ACTIVE  "
    else:
        status_icon = "💤 SLEEPING"

    bar_length = int(min(energy / THRESHOLD, 1.0) * 40)
    bar = "█" * bar_length + "░" * (40 - bar_length)

    print(f"\r{status_icon} [{bar}] {energy:.3f}", end="", flush=True)

try:
    with sd.InputStream(samplerate=SAMPLE_RATE,
                       channels=1,
                       blocksize=CHUNK_SIZE,
                       callback=audio_callback):
        while True:
            sd.sleep(100)
except KeyboardInterrupt:
    print("\n\nSimple wake word test complete!")
```

Run it:

```bash
poetry run python test_simple_wake_word.py
```

This gives you instant wake word capability while you set up proper models later.

### Integration Preview

In Section 6, we'll combine VAD + Wake Word:

```python
# Pipeline flow:
# 1. Wait for wake word ("Hey OLAF")
# 2. Activate listening (R2D2 plays acknowledgment beep)
# 3. VAD detects speech start
# 4. Record audio while VAD detects speech
# 5. VAD detects speech end (silence threshold)
# 6. Send to Whisper for transcription
# 7. Send to Claude for response
# 8. Play R2D2 response
# 9. Return to wake word listening
```

### Performance Expectations

| Component | Model Size | Latency | CPU Usage |
|-----------|------------|---------|-----------|
| Silero VAD | ~2MB | ~10-30ms | ~5-10% |
| openWakeWord | ~10-50MB | ~50-100ms | ~5-10% |
| Combined | ~50-100MB | ~100ms | ~10-15% |

### Troubleshooting

**Issue: VAD model download fails**
```bash
# Clear torch hub cache
rm -rf ~/.cache/torch/hub/snakers4_silero-vad_*

# Retry download
poetry run python test_vad.py
```

**Issue: VAD too sensitive (triggers on background noise)**
- Increase threshold from 0.5 to 0.7 in code
- Reduce microphone gain
- Add noise gate in audio preprocessing

**Issue: VAD not sensitive enough (misses speech)**
- Lower threshold from 0.5 to 0.3
- Check microphone volume is adequate
- Ensure 16kHz sample rate

**Issue: Wake word not detecting**
- Speak clearly and enunciate
- Adjust threshold (try 0.3 instead of 0.5)
- Check microphone input level
- Consider training custom "Hey OLAF" model

**Issue: False wake word triggers**
- Increase threshold (try 0.7)
- Use longer, more unique wake phrase
- Add confirmation beep and require second trigger

### Custom Wake Word Training (Advanced)

To train a custom "Hey OLAF" wake word:

1. Record 100+ samples of yourself saying "Hey OLAF"
2. Record 100+ samples of other phrases (negative examples)
3. Use openWakeWord training scripts
4. Generate custom `.tflite` model

Documentation: [openWakeWord Training Guide](https://github.com/dscripka/openWakeWord)

For now, using "Hey Mycroft" or energy-based detection works fine!

---

## Section 5: Setup Cloud LLM (Claude API)

Coming next...

---

## Section 5: Build the Voice Pipeline

Coming next...

---

## Section 6: Test and Run

Coming next...

---

## Resources

- [Pipecat Docs](https://docs.pipecat.ai/)
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper)
- [Piper TTS](https://github.com/rhasspy/piper)
- [Claude API](https://docs.anthropic.com/)
