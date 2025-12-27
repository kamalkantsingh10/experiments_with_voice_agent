#!/usr/bin/env python3
"""
Test openWakeWord Detection

For now, uses pre-trained models as placeholder.
To use "Hi OLAF", you'll need to train a custom model.
"""

import sounddevice as sd
import numpy as np
from openwakeword.model import Model
import sys

# Audio settings
SAMPLE_RATE = 16000
CHUNK_SIZE = 1280  # 80ms chunks (optimal for openWakeWord)

print("=" * 70)
print("OPENWAKEWORD TEST - 'Hi OLAF' Wake Word")
print("=" * 70)
print()

# Initialize openWakeWord model
print("Loading openWakeWord models...")
try:
    # Load default models
    # Note: For custom "hi olaf" model, you'll train and add it here
    oww_model = Model(
        inference_framework="tflite",  # Use TFLite for efficiency
        # wakeword_models=["path/to/hi_olaf.tflite"]  # Use this for custom model
    )

    print("✓ Models loaded successfully!")
    print()
    print("Available wake words:")
    for wake_word in oww_model.models.keys():
        print(f"  - {wake_word}")
    print()
    print("=" * 70)
    print("NOTE: Custom 'Hi OLAF' model not yet trained.")
    print("For testing, try saying one of the pre-trained wake words above.")
    print()
    print("To create 'Hi OLAF' wake word:")
    print("  1. Record 50-100 samples of yourself saying 'Hi OLAF'")
    print("  2. Use openWakeWord training scripts")
    print("  3. Generate hi_olaf.tflite model")
    print("  4. Update this script to load custom model")
    print("=" * 70)

except Exception as e:
    print(f"✗ Error loading models: {e}")
    print()
    print("Troubleshooting:")
    print("  1. Install: poetry add openwakeword")
    print("  2. Models download automatically on first run (needs internet)")
    print("  3. Check: ~/.local/share/openwakeword/ for downloaded models")
    sys.exit(1)

print()
print("Listening for wake word...")
print("Press Ctrl+C to stop.")
print("=" * 70)
print()

# Detection parameters
DETECTION_THRESHOLD = 0.5  # Adjust between 0.0-1.0 (lower = more sensitive)
detection_count = 0

def audio_callback(indata, frames, time_info, status):
    """Process audio for wake word detection"""
    global detection_count

    if status:
        print(f"[Warning] Audio status: {status}")

    # Convert audio to format expected by model (float32, mono)
    audio_data = indata.copy().flatten().astype(np.float32)

    # Get predictions from all loaded models
    predictions = oww_model.predict(audio_data)

    # Check each wake word
    for wake_word, score in predictions.items():
        if score >= DETECTION_THRESHOLD:
            detection_count += 1
            print(f"\n")
            print("=" * 70)
            print(f"🎯 WAKE WORD DETECTED: {wake_word}")
            print("=" * 70)
            print(f"   Confidence: {score:.3f}")
            print(f"   Detection #{detection_count}")
            print(f"   (Imagine this was 'Hi OLAF'!)")
            print("=" * 70)
            print()
        else:
            # Show progress for scores above 0.1
            if score > 0.1:
                bar_length = int(score * 40)
                bar = "▌" * bar_length + " " * (40 - bar_length)
                # Truncate long wake word names for display
                display_name = wake_word[:20]
                print(f"\r{display_name:<20} [{bar}] {score:.3f}", end="", flush=True)

try:
    # Start audio stream
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        blocksize=CHUNK_SIZE,
        dtype=np.float32,
        callback=audio_callback
    ):
        print("💤 Listening...")
        print()

        # Keep running
        while True:
            sd.sleep(100)

except KeyboardInterrupt:
    print("\n")
    print("=" * 70)
    print("WAKE WORD TEST COMPLETE")
    print("=" * 70)
    print(f"Total detections: {detection_count}")
    print()
    print("Next steps:")
    print("  1. Train custom 'Hi OLAF' model (see training guide below)")
    print("  2. Test with your custom model")
    print("  3. Integrate into voice pipeline")
    print()

except Exception as e:
    print(f"\n✗ Error: {e}")
    print()
    print("Troubleshooting:")
    print("  1. Check microphone: poetry run python -c \"import sounddevice; print(sounddevice.query_devices())\"")
    print("  2. Adjust DETECTION_THRESHOLD if too sensitive (increase) or insensitive (decrease)")
    print("  3. Ensure models downloaded: ls ~/.local/share/openwakeword/")
