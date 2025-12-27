
#!/usr/bin/env python3
"""Test Whisper transcription with microphone input"""

from faster_whisper import WhisperModel
import sounddevice as sd
import numpy as np
import time
import wave
import tempfile
import os

print("Downloading Whisper Small model (first run only)...")
print("This may take a few minutes depending on your internet connection.\n")

# Initialize model - downloads on first run
model = WhisperModel("small", device="cpu", compute_type="int8")

print("✓ Model loaded successfully!")
print(f"  Model: whisper-small")
print(f"  Device: CPU")
print(f"  Compute type: int8 (optimized for CPU)\n")

# Audio recording parameters
SAMPLE_RATE = 16000  # Whisper expects 16kHz
DURATION = 5  # seconds

print("=" * 60)
print("AUDIO RECORDING TEST")
print("=" * 60)
print(f"\nRecording {DURATION} seconds of audio...")
print("Speak now: 'Hello, this is a test'\n")
print("Recording starts in 3 seconds...")
time.sleep(3)

# Record audio
print("🔴 RECORDING...")
audio_data = sd.rec(int(DURATION * SAMPLE_RATE),
                    samplerate=SAMPLE_RATE,
                    channels=1,
                    dtype='int16')
sd.wait()  # Wait until recording is finished
print("✓ Recording complete!\n")

# Save to temporary WAV file
temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
temp_filename = temp_file.name
temp_file.close()

with wave.open(temp_filename, 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)  # 16-bit
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(audio_data.tobytes())

print("Transcribing audio...")
start_time = time.time()

# Transcribe
segments, info = model.transcribe(temp_filename, beam_size=5)

transcription_time = time.time() - start_time

print("\n" + "=" * 60)
print("TRANSCRIPTION RESULTS")
print("=" * 60)

# Print transcription
full_text = ""
for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
    full_text += segment.text

print("\n" + "=" * 60)
print(f"Full transcription: {full_text.strip()}")
print("=" * 60)

print(f"\n⏱️  Transcription time: {transcription_time:.2f} seconds")
print(f"📊 Audio duration: {DURATION} seconds")
print(f"🚀 Real-time factor: {transcription_time/DURATION:.2f}x")

if transcription_time < DURATION:
    print("✓ Faster than real-time! Good performance.")
else:
    print("⚠️  Slower than real-time. Consider using a smaller model.")

# Cleanup
os.unlink(temp_filename)

print("\n✓ Test complete!")