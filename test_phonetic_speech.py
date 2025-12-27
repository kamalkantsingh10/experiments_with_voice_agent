#!/usr/bin/env python3
"""
Test R2D2 Phonetic Text-to-Speech
Tests the new speak_text() functionality
"""

from r2d2_voice import R2D2Voice, PhonemeProcessor
import time
import numpy as np

print("=" * 60)
print("R2D2 PHONETIC TEXT-TO-SPEECH TEST")
print("=" * 60)
print()

# Test 1: PhonemeProcessor initialization and phoneme categorization
print("Test 1: PhonemeProcessor Basic Functionality")
print("-" * 60)

try:
    processor = PhonemeProcessor(language='en-us')
    print("✓ PhonemeProcessor initialized")

    # Test phoneme categorization
    test_phonemes = {
        'i': 'vowel_front',
        'ə': 'vowel_central',
        'u': 'vowel_back',
        't': 'plosive_voiceless',
        'b': 'plosive_voiced',
        's': 'fricative_voiceless',
        'z': 'fricative_voiced',
        'm': 'nasal',
        'r': 'approximant',
    }

    all_correct = True
    for phoneme, expected_category in test_phonemes.items():
        category = processor.categorize_phoneme(phoneme)
        if category == expected_category:
            print(f"  ✓ '{phoneme}' → {category}")
        else:
            print(f"  ✗ '{phoneme}' → {category} (expected {expected_category})")
            all_correct = False

    if all_correct:
        print("✓ All phoneme categorizations correct!")
    print()

except Exception as e:
    print(f"✗ PhonemeProcessor test failed: {e}")
    print("  Make sure espeak-ng is installed: sudo apt-get install espeak-ng")
    print("  Make sure phonemizer is installed: pip install phonemizer")
    print()

# Test 2: Text-to-phonemes conversion
print("Test 2: Text-to-Phonemes Conversion")
print("-" * 60)

try:
    processor = PhonemeProcessor(language='en-us')
    test_text = "I am good"
    phonemes = processor.text_to_phonemes(test_text)

    print(f"Input text: '{test_text}'")
    print(f"Phonemes extracted: {len(phonemes)}")

    # Count word boundaries
    word_boundaries = sum(1 for _, is_boundary in phonemes if is_boundary)
    print(f"Word boundaries detected: {word_boundaries}")
    print(f"Expected words: 3")

    if word_boundaries == 3:
        print("✓ Word boundary detection working!")
    else:
        print("⚠ Word boundary count doesn't match (may vary by phonemizer)")

    # Show first few phonemes
    print("\nFirst 5 phonemes:")
    for i, (phoneme, is_boundary) in enumerate(phonemes[:5]):
        boundary_marker = " [WORD START]" if is_boundary else ""
        category = processor.categorize_phoneme(phoneme)
        print(f"  {i+1}. '{phoneme}' → {category}{boundary_marker}")

    print()

except Exception as e:
    print(f"✗ Text-to-phonemes test failed: {e}")
    print()

# Test 3: R2D2Voice initialization with text-to-speech
print("Test 3: R2D2Voice Text-to-Speech Initialization")
print("-" * 60)

try:
    voice = R2D2Voice(sample_rate=44100)
    print("✓ R2D2Voice initialized with text-to-speech support")
    print()
except Exception as e:
    print(f"✗ Initialization failed: {e}")
    print()

# Test 4: Basic speak_text() functionality
print("Test 4: Basic speak_text() Functionality")
print("-" * 60)

try:
    voice = R2D2Voice(sample_rate=44100)

    test_texts = [
        ("Hello", "greeting"),
        ("I am good", "happy"),
        ("Testing", "affirmative"),
    ]

    for text, emotion in test_texts:
        print(f"\nText: '{text}' | Emotion: {emotion}")

        start = time.time()
        audio = voice.speak_text(text, emotion=emotion)
        gen_time = time.time() - start

        duration = len(audio) / voice.params.sample_rate

        print(f"  ✓ Generated in {gen_time*1000:.1f}ms")
        print(f"  📊 Audio duration: {duration:.2f}s")
        print(f"  🔊 Audio samples: {len(audio)}")

        # Check audio is valid
        if len(audio) > 0 and np.max(np.abs(audio)) > 0:
            print(f"  ✓ Audio contains valid signal")
        else:
            print(f"  ✗ Audio appears to be empty")

    print()

except Exception as e:
    print(f"✗ speak_text() test failed: {e}")
    import traceback
    traceback.print_exc()
    print()

# Test 5: Text length proportionality
print("Test 5: Audio Duration Proportional to Text Length")
print("-" * 60)

try:
    voice = R2D2Voice(sample_rate=44100)

    short_text = "Hi"
    long_text = "Hello there, how are you doing today?"

    short_audio = voice.speak_text(short_text, emotion='affirmative')
    long_audio = voice.speak_text(long_text, emotion='affirmative')

    short_duration = len(short_audio) / voice.params.sample_rate
    long_duration = len(long_audio) / voice.params.sample_rate

    print(f"Short text: '{short_text}'")
    print(f"  Duration: {short_duration:.2f}s")
    print(f"\nLong text: '{long_text}'")
    print(f"  Duration: {long_duration:.2f}s")

    ratio = long_duration / short_duration
    print(f"\nDuration ratio: {ratio:.1f}x")

    if ratio > 3:
        print("✓ Long text is significantly longer (proportional)")
    else:
        print("⚠ Duration may not be proportional enough")

    print()

except Exception as e:
    print(f"✗ Proportionality test failed: {e}")
    print()

# Test 6: Emotion effects on same text
print("Test 6: Emotion Effects on Same Text")
print("-" * 60)

try:
    voice = R2D2Voice(sample_rate=44100, seed=42)  # Fixed seed for reproducibility

    text = "Hello world"
    emotions = ['happy', 'sad', 'excited']

    audio_samples = {}

    for emotion in emotions:
        audio = voice.speak_text(text, emotion=emotion)
        audio_samples[emotion] = audio
        duration = len(audio) / voice.params.sample_rate
        print(f"{emotion:10s}: {duration:.2f}s, {len(audio)} samples")

    # Check that different emotions produce different audio
    happy = audio_samples['happy']
    sad = audio_samples['sad']

    # Compare audio signals
    min_len = min(len(happy), len(sad))
    diff_ratio = np.mean(happy[:min_len] != sad[:min_len])

    print(f"\nDifference between happy and sad: {diff_ratio*100:.1f}% of samples")

    if diff_ratio > 0.3:
        print("✓ Emotions produce distinctly different audio")
    else:
        print("⚠ Emotions may not be distinct enough")

    print()

except Exception as e:
    print(f"✗ Emotion test failed: {e}")
    print()

# Test 7: Clarity parameter effects
print("Test 7: Clarity Parameter Effects")
print("-" * 60)

try:
    voice = R2D2Voice(sample_rate=44100)

    text = "Testing clarity"
    clarity_levels = [0.0, 0.3, 1.0]

    for clarity in clarity_levels:
        audio = voice.speak_text(text, emotion='happy', clarity=clarity)
        duration = len(audio) / voice.params.sample_rate
        print(f"Clarity {clarity:.1f}: {duration:.2f}s, {len(audio)} samples")

    print("✓ Clarity parameter accepted and processed")
    print()

except Exception as e:
    print(f"✗ Clarity test failed: {e}")
    print()

# Test 8: Backward compatibility
print("Test 8: Backward Compatibility (old speak() API)")
print("-" * 60)

try:
    voice = R2D2Voice(sample_rate=44100)

    # Test that old API still works
    audio = voice.speak(emotion='happy', intensity=1.0)
    duration = len(audio) / voice.params.sample_rate

    print(f"Old API speak(emotion='happy'):")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Samples: {len(audio)}")
    print("✓ Backward compatibility maintained!")
    print()

except Exception as e:
    print(f"✗ Backward compatibility test failed: {e}")
    print()

# Test 9: Performance benchmark
print("Test 9: Performance Benchmark")
print("-" * 60)

try:
    voice = R2D2Voice(sample_rate=44100)

    text = "The quick brown fox jumps over the lazy dog"
    iterations = 5

    times = []
    for i in range(iterations):
        start = time.time()
        audio = voice.speak_text(text, emotion='affirmative')
        elapsed = time.time() - start
        times.append(elapsed)

    avg_time = np.mean(times)
    print(f"Text: '{text}'")
    print(f"Average generation time: {avg_time*1000:.1f}ms (over {iterations} iterations)")

    if avg_time < 0.15:
        print("✓ Performance target met (<150ms)")
    elif avg_time < 0.30:
        print("⚠ Performance acceptable but slower than target")
    else:
        print("✗ Performance below target (>300ms)")

    print()

except Exception as e:
    print(f"✗ Performance test failed: {e}")
    print()

# Summary
print("=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("All core functionality tests completed!")
print()
print("Next steps:")
print("  1. Listen to generated audio files")
print("  2. Fine-tune durations and gaps based on audio quality")
print("  3. Test with various texts and emotions")
print("  4. Update README with usage examples")
print()
print("To test audio playback:")
print("  voice = R2D2Voice()")
print("  voice.speak_text('I am good', emotion='happy')")
print("  # Or use voice.play() method if sounddevice is installed")
print()
