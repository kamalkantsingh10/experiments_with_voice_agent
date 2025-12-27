#!/usr/bin/env python3
"""
Quick demo of R2D2 phonetic text-to-speech with play_text()
Just run and listen - no file saving needed!
Default speed is 3x (snappy R2D2 responses!)
EXTREME emotional variations: Pitch 0.5x-3x, Speed 0.5x-3x
"""

from r2d2_voice import R2D2Voice
import time

print("=" * 60)
print("R2D2 PHONETIC SPEECH DEMO - EXTREME EMOTIONS")
print("=" * 60)
print("Pitch range: 0.5x (very low) to 3x (extremely high)")
print("Speed range: 0.5x (2x faster) to 3x (3x slower)")
print()

voice = R2D2Voice()

# Demo 1: Extreme emotion showcase with "Hello"
print("1. EXTREME Emotion Showcase with 'Hello':")
print("   Listen to the HUGE differences!")
print()

extreme_emotions = [
    ('excited', 'Pitch 3.0x (highest), Speed 0.5x (2x faster)'),
    ('happy', 'Pitch 2.5x, Speed 0.6x (1.67x faster)'),
    ('afraid', 'Pitch 2.2x, Speed 0.65x (jittery)'),
    ('surprised', 'Pitch 1.9x, Speed 0.7x (sudden)'),
    ('playful', 'Pitch 1.7x, Speed 0.8x (bouncy)'),
    ('curious', 'Pitch 1.5x, Speed 1.2x (thoughtful)'),
    ('confident', 'Pitch 1.2x, Speed 0.9x (steady)'),
    ('angry', 'Pitch 0.7x, Speed 0.75x (growly)'),
    ('sad', 'Pitch 0.6x, Speed 2.0x (2x slower)'),
    ('sleepy', 'Pitch 0.5x (lowest), Speed 3.0x (3x slower)'),
]

for emotion, desc in extreme_emotions:
    print(f"   {emotion:12s} - {desc}")
    voice.play_text("Hello", emotion=emotion)
    time.sleep(0.5)

print()

# Demo 2: Same text, extreme contrast
print("2. Extreme Contrast - 'I am good':")
print()

contrast_pairs = [
    ('excited', 'EXTREMELY high & fast'),
    ('sleepy', 'EXTREMELY low & slow'),
    ('happy', 'Very high & bouncy'),
    ('sad', 'Very low & drawn out'),
]

for emotion, desc in contrast_pairs:
    print(f"   {emotion:10s} - {desc}")
    voice.play_text("I am good", emotion=emotion)
    time.sleep(0.5)

print()

# Demo 3: Emotional range demonstration
print("3. Full Emotional Range - 'Sure thing':")
print()

for emotion, _ in extreme_emotions[:5]:  # First 5 emotions
    print(f"   {emotion}...")
    voice.play_text("Sure thing", emotion=emotion)
    time.sleep(0.4)

print()


# Demo 4: Star Wars Short Phrases with 10 Emotions
print("4. Star Wars Phrases with EXTREME Emotions:")
print("   Notice the huge emotional differences!")
print()

star_wars_phrases = [
    ("Sure thing", "confident"),
    ("Will do", "happy"),
    ("I not like", "angry"),
    ("So sweet", "playful"),
    ("I love you", "happy"),
    ("Help me", "afraid"),
    ("Look out", "surprised"),
    ("Good idea", "excited"),
    ("Bad feeling", "curious"),
    ("Too tired", "sleepy"),
    ("Thank you", "happy"),
    ("No way", "angry"),
    ("Oh no", "sad"),
    ("Yes sir", "confident"),
    ("Right away", "excited"),
    ("Never give up", "excited"),
    ("Trust me", "confident"),
    ("Watch out", "afraid"),
    ("I am ready", "confident"),
    ("Great shot", "playful"),
]

for i, (phrase, emotion) in enumerate(star_wars_phrases, 1):
    print(f"   {i:2d}. '{phrase:15s}' ({emotion})")
    voice.play_text(phrase, emotion=emotion)
    time.sleep(0.25)

print()
print("=" * 60)
print("DEMO COMPLETE!")
print("=" * 60)
print()
print("Try it yourself:")
print("  from r2d2_voice import R2D2Voice")
print("  voice = R2D2Voice()")
print("  voice.play_text('Your text', emotion='happy')")
print()
print("=" * 60)
print("10 EMOTIONS WITH EXTREME VARIATIONS")
print("=" * 60)
print()
print("Emotion      | Pitch    | Speed     | Character")
print("-------------|----------|-----------|------------------------")
print("excited      | 3.0x ⬆⬆⬆ | 0.5x ⚡⚡  | Extremely high & rapid")
print("happy        | 2.5x ⬆⬆  | 0.6x ⚡   | Very high & bouncy")
print("afraid       | 2.2x ⬆⬆  | 0.65x ⚡  | High & jittery")
print("surprised    | 1.9x ⬆   | 0.7x ⚡   | High & sudden")
print("playful      | 1.7x ⬆   | 0.8x ⚡   | High & bouncy")
print("curious      | 1.5x ⬆   | 1.2x ⏱   | Med-high & thoughtful")
print("confident    | 1.2x     | 0.9x     | Steady & assertive")
print("angry        | 0.7x ⬇   | 0.75x ⚡  | Low & aggressive")
print("sad          | 0.6x ⬇⬇  | 2.0x ⏱⏱  | Very low & slow")
print("sleepy       | 0.5x ⬇⬇⬇ | 3.0x ⏱⏱⏱ | Extremely low & drowsy")
print()
print("⬆ = Higher pitch  |  ⬇ = Lower pitch")
print("⚡ = Faster       |  ⏱ = Slower")
print()
