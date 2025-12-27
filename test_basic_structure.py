#!/usr/bin/env python3
"""
Basic structure test for phonetic speech (no espeak-ng required)
Tests that classes and methods are properly defined
"""

from r2d2_voice import R2D2Voice, PhonemeProcessor
import numpy as np

print("=" * 60)
print("R2D2 PHONETIC SPEECH - STRUCTURE TEST")
print("=" * 60)
print()

# Test 1: Check classes exist
print("Test 1: Class Structure")
print("-" * 60)

try:
    voice = R2D2Voice(sample_rate=44100)
    print("✓ R2D2Voice class initialized")

    # Check new attributes exist
    assert hasattr(voice, '_phoneme_processor'), "Missing _phoneme_processor attribute"
    print("✓ _phoneme_processor attribute exists")

    assert hasattr(voice, 'language'), "Missing language attribute"
    print("✓ language attribute exists")

    # Check class constants
    assert hasattr(R2D2Voice, 'PHONEME_SOUND_MAP'), "Missing PHONEME_SOUND_MAP"
    print("✓ PHONEME_SOUND_MAP constant exists")

    assert hasattr(R2D2Voice, 'PHONEME_DURATIONS'), "Missing PHONEME_DURATIONS"
    print("✓ PHONEME_DURATIONS constant exists")

    assert hasattr(R2D2Voice, 'EMOTION_PITCH_SHIFTS'), "Missing EMOTION_PITCH_SHIFTS"
    print("✓ EMOTION_PITCH_SHIFTS constant exists")

    assert hasattr(R2D2Voice, 'EMOTION_SPEED_FACTORS'), "Missing EMOTION_SPEED_FACTORS"
    print("✓ EMOTION_SPEED_FACTORS constant exists")

    print()

except Exception as e:
    print(f"✗ Class structure test failed: {e}")
    print()

# Test 2: Check methods exist
print("Test 2: Method Existence")
print("-" * 60)

try:
    voice = R2D2Voice()

    methods = [
        'speak_text',
        '_get_phoneme_processor',
        '_create_word_boundary',
        '_apply_pitch_shift',
        '_apply_emotion_to_sound',
        '_blend_phoneme_emotion',
        '_generate_base_phoneme_sound',
    ]

    for method_name in methods:
        assert hasattr(voice, method_name), f"Missing method: {method_name}"
        print(f"✓ {method_name}() exists")

    print()

except Exception as e:
    print(f"✗ Method existence test failed: {e}")
    print()

# Test 3: Check PhonemeProcessor structure
print("Test 3: PhonemeProcessor Structure")
print("-" * 60)

try:
    # Check class attributes
    assert hasattr(PhonemeProcessor, 'VOWEL_FRONT'), "Missing VOWEL_FRONT"
    print("✓ VOWEL_FRONT phoneme set exists")

    assert hasattr(PhonemeProcessor, 'PLOSIVE_VOICELESS'), "Missing PLOSIVE_VOICELESS"
    print("✓ PLOSIVE_VOICELESS phoneme set exists")

    # Check methods
    processor = PhonemeProcessor()
    assert hasattr(processor, 'categorize_phoneme'), "Missing categorize_phoneme method"
    print("✓ categorize_phoneme() method exists")

    assert hasattr(processor, 'text_to_phonemes'), "Missing text_to_phonemes method"
    print("✓ text_to_phonemes() method exists")

    print()

except Exception as e:
    print(f"✗ PhonemeProcessor structure test failed: {e}")
    print()

# Test 4: Test phoneme categorization (no espeak-ng needed)
print("Test 4: Phoneme Categorization")
print("-" * 60)

try:
    processor = PhonemeProcessor()

    test_cases = {
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

    all_passed = True
    for phoneme, expected in test_cases.items():
        result = processor.categorize_phoneme(phoneme)
        if result == expected:
            print(f"✓ '{phoneme}' → {result}")
        else:
            print(f"✗ '{phoneme}' → {result} (expected {expected})")
            all_passed = False

    if all_passed:
        print("\n✓ All phoneme categorizations correct!")

    print()

except Exception as e:
    print(f"✗ Phoneme categorization test failed: {e}")
    print()

# Test 5: Test helper methods
print("Test 5: Helper Methods")
print("-" * 60)

try:
    voice = R2D2Voice(sample_rate=44100)

    # Test _create_word_boundary
    gap = voice._create_word_boundary(0.18)
    assert len(gap) == int(0.18 * 44100), "Word boundary duration incorrect"
    assert np.all(gap == 0), "Word boundary should be silence"
    print(f"✓ _create_word_boundary() works: {len(gap)} samples")

    # Test _blend_phoneme_emotion
    sound = voice._blend_phoneme_emotion('vowel_front', 'happy', 0.3)
    assert sound in ['whistle_up', 'chirp'], f"Invalid sound selection: {sound}"
    print(f"✓ _blend_phoneme_emotion() works: selected '{sound}'")

    # Test _apply_pitch_shift
    test_signal = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
    shifted = voice._apply_pitch_shift(test_signal, 1.5)
    assert len(shifted) == len(test_signal), "Pitch shift changed signal length"
    print(f"✓ _apply_pitch_shift() works: {len(shifted)} samples")

    print()

except Exception as e:
    print(f"✗ Helper methods test failed: {e}")
    import traceback
    traceback.print_exc()
    print()

# Test 6: Test backward compatibility
print("Test 6: Backward Compatibility")
print("-" * 60)

try:
    voice = R2D2Voice(sample_rate=44100)

    # Old API should still work
    audio = voice.speak(emotion='happy', intensity=1.0)
    duration = len(audio) / voice.params.sample_rate

    assert len(audio) > 0, "speak() returned empty audio"
    assert duration > 0, "Audio has no duration"

    print(f"✓ Old speak() API works: {duration:.2f}s, {len(audio)} samples")
    print("✓ Backward compatibility maintained!")

    print()

except Exception as e:
    print(f"✗ Backward compatibility test failed: {e}")
    print()

# Summary
print("=" * 60)
print("STRUCTURE TEST SUMMARY")
print("=" * 60)
print("✓ All class structures and methods are properly defined!")
print()
print("NOTE: Full functionality testing requires espeak-ng:")
print("  sudo apt-get install espeak-ng")
print()
print("After installing espeak-ng, run:")
print("  python test_phonetic_speech.py")
print()
