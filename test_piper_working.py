#!/usr/bin/env python3
"""
Working Piper TTS test with proper AudioChunk usage
"""

import numpy as np
import sounddevice as sd
from piper.voice import PiperVoice

print("=" * 60)
print("PIPER TTS - WORKING TEST")
print("=" * 60)
print()

# Load voice
model = "./piper_models/en_GB-alba-medium.onnx"
print(f"Loading voice: {model}")
voice = PiperVoice.load(model)
print(f"✓ Voice loaded (sample rate: {voice.config.sample_rate})")
print()

# Text to speak
text = "Hello, I am a British female voice assistant."
print(f"Speaking: \"{text}\"")
print()

# Setup audio stream
stream = sd.OutputStream(
    samplerate=voice.config.sample_rate,
    channels=1,
    dtype='int16'
)
stream.start()

print("Playing audio...")

# Synthesize and play
for chunk in voice.synthesize(text):
    # Get int16 audio array from chunk
    audio_data = chunk.audio_int16_array
    stream.write(audio_data)

stream.stop()
stream.close()

print("✓ Done!")
print()
print("=" * 60)
