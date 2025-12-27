# Training Custom "Hi OLAF" Wake Word

This guide shows how to train a custom openWakeWord model for "Hi OLAF".

## Quick Start (Recommended Method)

### Option 1: Use openWakeWord's Synthetic Data Generator

```bash
# Install training dependencies
poetry add openwakeword[train]

# Generate synthetic training data (easier than recording yourself!)
# This uses text-to-speech to create variations
python -m openwakeword.train.generate_synthetic_data \
  --text "hi olaf" \
  --output_dir data/hi_olaf_synthetic \
  --num_samples 1000

# Train model
python -m openwakeword.train.train_model \
  --positive_data data/hi_olaf_synthetic \
  --negative_data <path_to_negative_samples> \
  --output models/hi_olaf.tflite
```

## Option 2: Record Your Own Voice (Most Accurate)

### Step 1: Record Positive Samples

Create `record_samples.py`:

```python
#!/usr/bin/env python3
"""Record wake word samples for training"""

import sounddevice as sd
import soundfile as sf
import numpy as np
import time
import os

SAMPLE_RATE = 16000
DURATION = 2  # seconds per recording
OUTPUT_DIR = "data/hi_olaf_positive"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 70)
print("WAKE WORD SAMPLE RECORDER")
print("=" * 70)
print(f"Will record {DURATION} second clips")
print(f"Say 'Hi OLAF' clearly when recording starts")
print()

num_samples = int(input("How many samples to record? (recommend 50-100): "))

for i in range(num_samples):
    input(f"\nPress Enter to record sample {i+1}/{num_samples}...")

    print("🔴 Recording in 3...")
    time.sleep(1)
    print("🔴 Recording in 2...")
    time.sleep(1)
    print("🔴 Recording in 1...")
    time.sleep(1)
    print("🔴 RECORDING - Say 'Hi OLAF' now!")

    # Record audio
    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype=np.float32
    )
    sd.wait()

    # Save to file
    filename = f"{OUTPUT_DIR}/hi_olaf_{i+1:03d}.wav"
    sf.write(filename, audio, SAMPLE_RATE)

    print(f"✓ Saved: {filename}")

print()
print("=" * 70)
print(f"✓ Recorded {num_samples} samples!")
print(f"   Location: {OUTPUT_DIR}/")
print("=" * 70)
```

Run it:
```bash
poetry run python record_samples.py
```

### Step 2: Download Negative Samples

You need examples of speech that is NOT "Hi OLAF":

```bash
# Create directory
mkdir -p data/negative_samples

# Download common speech dataset
# Option A: Use Google Speech Commands dataset
wget http://download.tensorflow.org/data/speech_commands_v0.02.tar.gz
tar -xzf speech_commands_v0.02.tar.gz -C data/negative_samples

# Option B: Record yourself saying other phrases
# Use record_samples.py but say random phrases (not "Hi OLAF")
```

### Step 3: Train the Model

```bash
# Install training dependencies
pip install tensorflow librosa matplotlib

# Clone openWakeWord repository for training scripts
git clone https://github.com/dscripka/openWakeWord.git
cd openWakeWord

# Train model
python openwakeword/train.py \
  --positive_dir ../data/hi_olaf_positive \
  --negative_dir ../data/negative_samples \
  --output_file ../models/hi_olaf.tflite \
  --epochs 30 \
  --batch_size 32
```

### Step 4: Test Your Custom Model

Update `test_wake_word.py`:

```python
# Load your custom model
oww_model = Model(
    wakeword_models=["models/hi_olaf.tflite"],
    inference_framework="tflite"
)
```

Run test:
```bash
poetry run python test_wake_word.py
```

## Quick Method: Use Pre-trained Base and Fine-tune

If training from scratch is too complex:

```bash
# Use transfer learning from existing model
python -m openwakeword.train.finetune \
  --base_model hey_mycroft \
  --positive_samples data/hi_olaf_positive \
  --output models/hi_olaf.tflite \
  --epochs 10
```

## Expected Results

After training:
- **False Accept Rate:** <0.5 per hour
- **False Reject Rate:** <5%
- **Model Size:** 10-30 MB
- **Latency:** 50-100ms

## Troubleshooting

**Issue: Model not accurate enough**
- Record more samples (100+ recommended)
- Ensure good audio quality
- Include variations (different speeds, tones)
- Add more negative samples

**Issue: Too many false positives**
- Increase detection threshold in test script
- Add more diverse negative samples
- Train longer (more epochs)

**Issue: Missing detections**
- Lower detection threshold
- Record samples more clearly
- Ensure consistent pronunciation

## Alternative: Use Existing Similar Model

If training is too complex, you can use a similar pre-trained model temporarily:

- "hey_mycroft" - similar 2-word pattern
- "alexa" - single word, different pattern
- "hey_jarvis" - if available

Then gradually work on training "Hi OLAF" in the background.

## Resources

- [openWakeWord GitHub](https://github.com/dscripka/openWakeWord)
- [Training Guide](https://github.com/dscripka/openWakeWord/tree/main/openwakeword/train)
- [Pre-trained Models](https://github.com/dscripka/openWakeWord/tree/main/openwakeword/resources/models)
