#!/usr/bin/env python3
"""
Radio and communication channel DSP effects for voice
"""

import numpy as np
from scipy import signal


def radio_effect(audio, sample_rate=22050, static_level=0.02, distortion=0.3):
    """
    Apply radio transmission effect (like Star Wars comlink)

    Args:
        audio: Input audio (numpy array, float -1.0 to 1.0)
        sample_rate: Audio sample rate (Hz)
        static_level: Amount of background static (0.0 to 0.1)
        distortion: Amount of distortion (0.0 to 1.0)

    Returns:
        Processed audio with radio effect
    """
    # 1. Band-pass filter (250Hz - 4000Hz, wider for clearer voice)
    # Still sounds like radio but preserves more speech intelligibility
    sos = signal.butter(4, [250, 4000], 'bandpass', fs=sample_rate, output='sos')
    filtered = signal.sosfilt(sos, audio)

    # 2. Add background static (white noise)
    static = np.random.normal(0, static_level, len(audio))
    with_static = filtered + static

    # 3. Add random crackle/pops (radio interference)
    crackle = np.zeros_like(audio)
    # Random pops at ~0.1% of samples
    pop_indices = np.random.choice(len(audio), size=max(1, len(audio)//1000), replace=False)
    crackle[pop_indices] = np.random.uniform(-0.3, 0.3, len(pop_indices))

    # 4. Apply soft distortion (radio overdriven effect)
    with_crackle = with_static + crackle * 0.1
    distorted = np.tanh(with_crackle * (1 + distortion))

    # 5. Simulate signal fade (slight volume variation)
    fade_freq = 0.5  # Hz (slow fade in/out)
    fade = 1 + 0.1 * np.sin(2 * np.pi * fade_freq * np.arange(len(audio)) / sample_rate)

    # Combine and normalize
    output = distorted * fade * 0.8

    # Prevent clipping
    max_val = np.abs(output).max()
    if max_val > 1.0:
        output = output / max_val

    return output


def comlink_effect(audio, sample_rate=22050):
    """
    Military comlink effect with squelch tones at start/end
    Clearer voice with radio character

    Args:
        audio: Input audio (numpy array, float -1.0 to 1.0)
        sample_rate: Audio sample rate (Hz)

    Returns:
        Audio with comlink effect and squelch tones
    """
    # Apply radio effect with reduced noise for clarity
    # Lower static and distortion for more defined voice
    processed = radio_effect(audio, sample_rate, static_level=0.015, distortion=0.2)

    # Generate squelch tone (short beep at 1200Hz)
    squelch_duration = int(0.15 * sample_rate)  # 150ms
    t = np.linspace(0, 0.15, squelch_duration)
    squelch = np.sin(2 * np.pi * 1200 * t) * 0.3

    # Fade in/out the squelch tone
    fade_len = squelch_duration // 4
    squelch[:fade_len] *= np.linspace(0, 1, fade_len)
    squelch[-fade_len:] *= np.linspace(1, 0, fade_len)

    # Add squelch at start and end
    output = np.concatenate([squelch, processed, squelch])

    return output


def hologram_effect(audio, sample_rate=22050):
    """
    Hologram transmission effect (like Leia's message in Star Wars)
    Glitchy, stuttering, tinny - but more defined voice (50% clearer)

    Args:
        audio: Input audio (numpy array, float -1.0 to 1.0)
        sample_rate: Audio sample rate (Hz)

    Returns:
        Audio with hologram effect
    """
    # High-pass filter for tinny sound (lowered from 800Hz to 600Hz for more voice)
    sos = signal.butter(3, 600, 'highpass', fs=sample_rate, output='sos')
    tinny = signal.sosfilt(sos, audio)

    # Add random dropouts (glitches) - reduced from 8% to 4% for clearer voice
    mask = np.random.random(len(audio)) > 0.04
    glitchy = tinny * mask

    # Add digital artifact noise (reduced by 50%)
    artifacts = np.random.choice([0, 0, 0, 1], len(audio)) * \
                np.random.uniform(-0.075, 0.075, len(audio))

    output = glitchy + artifacts

    # Normalize
    max_val = np.abs(output).max()
    if max_val > 1.0:
        output = output / max_val

    return output


def generate_squelch_tone(sample_rate=22050, duration=0.15, frequency=1200):
    """
    Generate a squelch tone (beep) for channel open/close

    Args:
        sample_rate: Audio sample rate (Hz)
        duration: Tone duration (seconds)
        frequency: Tone frequency (Hz)

    Returns:
        Squelch tone audio
    """
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples)
    tone = np.sin(2 * np.pi * frequency * t) * 0.3

    # Fade in/out
    fade_len = samples // 4
    tone[:fade_len] *= np.linspace(0, 1, fade_len)
    tone[-fade_len:] *= np.linspace(1, 0, fade_len)

    return tone


# Demo
if __name__ == "__main__":
    import sounddevice as sd

    print("=" * 60)
    print("RADIO EFFECTS DEMO")
    print("=" * 60)
    print()

    # Generate a test tone (440 Hz for 1 second)
    sample_rate = 22050
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    test_audio = np.sin(2 * np.pi * 440 * t) * 0.5

    print("1. Playing original tone...")
    sd.play(test_audio, sample_rate)
    sd.wait()
    print()

    print("2. Playing with radio effect...")
    radio_audio = radio_effect(test_audio, sample_rate)
    sd.play(radio_audio, sample_rate)
    sd.wait()
    print()

    print("3. Playing with comlink effect (with squelch)...")
    comlink_audio = comlink_effect(test_audio, sample_rate)
    sd.play(comlink_audio, sample_rate)
    sd.wait()
    print()

    print("4. Playing with hologram effect (glitchy)...")
    hologram_audio = hologram_effect(test_audio, sample_rate)
    sd.play(hologram_audio, sample_rate)
    sd.wait()
    print()

    print("=" * 60)
    print("Demo complete!")
    print("=" * 60)
