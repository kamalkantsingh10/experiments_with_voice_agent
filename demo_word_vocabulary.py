#!/usr/bin/env python3
"""
R2D2 Word Vocabulary Demo

Demonstrates the word-based approach where:
- Each word has a fixed sequence length (1-5 notes)
- Emotion controls which sounds are picked + pitch/speed
- 500 common words mapped, unknown words get 2-note sequences
"""

from r2d2_word_vocabulary import R2D2WordVocabulary
import time

print("=" * 70)
print("R2D2 WORD VOCABULARY DEMO")
print("=" * 70)
print("How it works:")
print("  - Each word has a fixed sequence length (1-5 notes)")
print("  - Emotion picks which sounds to use + modulates pitch/speed")
print("  - 500 common words mapped, unknown words = 2 random notes")
print()
print("12 Sound Primitives:")
print("  beep, boop, chirp, stutter, warble, buzz,")
print("  ping, blip, slide_down, chord, tremolo, sweep_up_down")
print("=" * 70)
print()

voice = R2D2WordVocabulary()

# Demo 1: Same sentence, all 10 emotions
print("=" * 70)
print("DEMO 1: Same Sentence, 10 Different Emotions")
print("=" * 70)
print("Sentence: 'I am happy to help you'")
print()

emotions = [
    ('neutral', 'Balanced, normal pitch/speed'),
    ('happy', 'High pitch (1.4x), fast (1.3x), chirpy sounds'),
    ('sad', 'Low pitch (0.7x), slow (0.6x), slide_down/boop'),
    ('angry', 'Low pitch (0.6x), fast (1.4x), buzz/stutter'),
    ('excited', 'High pitch (1.6x), very fast (1.8x), chirp/ping/blip'),
    ('curious', 'Med-high (1.3x), slow (0.9x), sweep_up_down/warble'),
    ('confused', 'Med-high (1.2x), slow (0.8x), warble/tremolo'),
    ('lazy', 'Low pitch (0.65x), very slow (0.5x), boop/slide_down'),
    ('afraid', 'High pitch (1.5x), fast (1.5x), stutter/tremolo'),
    ('naughty', 'Med-high (1.35x), fast (1.2x), chirp/sweep_up_down'),
]

for emotion, description in emotions:
    print(f"{emotion:12s} - {description}")
    voice.play_sentence("I am happy to help you", emotion=emotion)
    time.sleep(0.6)

print()

# Demo 2: Different sentences, happy emotion
print("=" * 70)
print("DEMO 2: Different Sentences - Happy Emotion")
print("=" * 70)
print("Notice: Same words always have same length, different sounds each time")
print()

happy_sentences = [
    "hello world",
    "how are you",
    "thank you very much",
    "I am excited",
    "this is great",
]

for i, sentence in enumerate(happy_sentences, 1):
    print(f"{i}. '{sentence}'")
    voice.play_sentence(sentence, emotion="happy")
    time.sleep(0.5)

print()

# Demo 3: Emotion contrast pairs
print("=" * 70)
print("DEMO 3: Emotion Contrast Pairs")
print("=" * 70)
print("Same sentence, extreme emotional differences")
print()

contrast_pairs = [
    ("excited", "lazy", "I will help you"),
    ("happy", "sad", "good morning"),
    ("angry", "afraid", "stop right now"),
    ("curious", "confused", "what is this"),
    ("naughty", "neutral", "I did it"),
]

for emotion1, emotion2, sentence in contrast_pairs:
    print(f"\nSentence: '{sentence}'")
    print(f"  {emotion1}:")
    voice.play_sentence(sentence, emotion=emotion1)
    time.sleep(0.4)
    print(f"  {emotion2}:")
    voice.play_sentence(sentence, emotion=emotion2)
    time.sleep(0.6)

print()

# Demo 4: Word length demonstration
print("=" * 70)
print("DEMO 4: Word Length Consistency")
print("=" * 70)
print("Each word always has the same number of notes (1-5)")
print()

test_words = ["the", "hello", "computer", "information", "yes", "world", "happy"]

print("Testing word lengths (neutral emotion):")
for word in test_words:
    length = voice.get_word_length(word)
    print(f"  '{word:12s}' = {length} notes")
    voice.play_sentence(word, emotion="neutral")
    time.sleep(0.5)

print()

# Demo 5: Unknown words
print("=" * 70)
print("DEMO 5: Unknown Words (Not in 500-word vocabulary)")
print("=" * 70)
print("Unknown words get random 2-note sequences")
print()

unknown_words = ["xyz", "blorgflorp", "zeebazop", "frobnicator"]

for word in unknown_words:
    length = voice.get_word_length(word)
    print(f"  '{word}' = {length} notes (unknown)")
    voice.play_sentence(word, emotion="curious")
    time.sleep(0.5)

print()

# Demo 6: Star Wars-style phrases with emotions
print("=" * 70)
print("DEMO 6: Star Wars R2D2 Phrases")
print("=" * 70)
print()

star_wars_phrases = [
    ("Affirmative", "confident"),
    ("At your service", "happy"),
    ("Danger detected", "afraid"),
    ("Mission complete", "excited"),
    ("Systems nominal", "neutral"),
    ("What is that", "curious"),
    ("Error error error", "confused"),
    ("Power low", "lazy"),
    ("Alert alert", "afraid"),
    ("Well done", "happy"),
    ("Not good", "angry"),
    ("Oh dear", "sad"),
    ("Ready to go", "excited"),
    ("Scanning area", "curious"),
    ("Feeling sleepy", "lazy"),
]

for i, (phrase, emotion) in enumerate(star_wars_phrases, 1):
    print(f"{i:2d}. '{phrase:20s}' ({emotion})")
    voice.play_sentence(phrase, emotion=emotion)
    time.sleep(0.4)

print()

# Demo 7: Save examples to files
print("=" * 70)
print("DEMO 7: Saving Examples to WAV Files")
print("=" * 70)
print()

save_examples = [
    ("hello world", "happy", "r2d2_hello_happy.wav"),
    ("danger ahead", "afraid", "r2d2_danger_afraid.wav"),
    ("mission complete", "excited", "r2d2_mission_excited.wav"),
    ("feeling tired", "lazy", "r2d2_tired_lazy.wav"),
]

for sentence, emotion, filename in save_examples:
    print(f"Saving: '{sentence}' ({emotion}) -> {filename}")
    voice.save_sentence(sentence, filename, emotion=emotion)

print()

# Summary
print("=" * 70)
print("DEMO COMPLETE!")
print("=" * 70)
print()
print("Key Features Demonstrated:")
print("  ✓ 10 emotions with unique sound preferences")
print("  ✓ Pitch modulation (0.6x - 1.6x)")
print("  ✓ Speed modulation (0.5x - 1.8x)")
print("  ✓ Word-based consistent sequence lengths")
print("  ✓ 500 common words mapped")
print("  ✓ Unknown word handling (2 random notes)")
print("  ✓ 12 distinct sound primitives")
print()
print("Try it yourself:")
print("  from r2d2_word_vocabulary import R2D2WordVocabulary")
print("  voice = R2D2WordVocabulary()")
print("  voice.play_sentence('your text here', emotion='happy')")
print()
print("=" * 70)
print("10 EMOTIONS REFERENCE")
print("=" * 70)
print()
print("Emotion   | Pitch | Speed | Preferred Sounds")
print("----------|-------|-------|------------------------------------------")
print("neutral   | 1.0x  | 1.0x  | Balanced (all sounds)")
print("happy     | 1.4x  | 1.3x  | chirp, ping, blip, chord")
print("sad       | 0.7x  | 0.6x  | slide_down, boop, tremolo")
print("angry     | 0.6x  | 1.4x  | buzz, stutter")
print("excited   | 1.6x  | 1.8x  | chirp, ping, blip, stutter, sweep_up_down")
print("curious   | 1.3x  | 0.9x  | sweep_up_down, warble, boop")
print("confused  | 1.2x  | 0.8x  | warble, sweep_up_down, tremolo, stutter")
print("lazy      | 0.65x | 0.5x  | boop, slide_down, buzz")
print("afraid    | 1.5x  | 1.5x  | stutter, tremolo, beep, warble")
print("naughty   | 1.35x | 1.2x  | chirp, blip, ping, sweep_up_down, warble")
print()
print("=" * 70)
