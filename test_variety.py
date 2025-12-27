#!/usr/bin/env python3
"""
Test sound variety - play same text multiple times to hear variation
"""

from r2d2_voice import R2D2Voice
import time

print("=" * 60)
print("R2D2 SOUND VARIETY TEST")
print("=" * 60)
print()
print("Playing the same text 3 times to demonstrate variation...")
print("Listen for different beeps, chirps, whistles, trills, etc.")
print()

voice = R2D2Voice()

text = "I am good"
emotion = 'happy'
speed = 2.0

for i in range(3):
    print(f"Iteration {i+1}: '{text}'")
    voice.play_text(text, emotion=emotion, speed=speed)
    time.sleep(0.5)
    print()

print("=" * 60)
print("Notice how each iteration sounds different!")
print("This is due to:")
print("  • Random sound selection from 3 options per phoneme")
print("  • ±15% frequency variation")
print("  • Built-in randomization in each sound generator")
print("=" * 60)
