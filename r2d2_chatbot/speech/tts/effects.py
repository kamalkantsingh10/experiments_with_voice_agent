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
    Clearer voice with radio character (Bumblebee-style)

    Args:
        audio: Input audio (numpy array, float -1.0 to 1.0)
        sample_rate: Audio sample rate (Hz)

    Returns:
        Audio with comlink effect and squelch tones
    """
    # Apply radio effect with reduced noise for clarity
    # Lower static and distortion for more defined voice
    processed = radio_effect(audio, sample_rate, static_level=0.015, distortion=0.25)

    # Generate squelch tone (short beep at 1200Hz)
    squelch_duration = int(0.12 * sample_rate)  # 120ms
    t = np.linspace(0, 0.12, squelch_duration)
    squelch = np.sin(2 * np.pi * 1200 * t) * 0.35

    # Fade in/out the squelch tone
    fade_len = squelch_duration // 4
    squelch[:fade_len] *= np.linspace(0, 1, fade_len)
    squelch[-fade_len:] *= np.linspace(1, 0, fade_len)

    # Add brief silence before/after squelch for dramatic effect
    silence = np.zeros(int(0.04 * sample_rate))  # 40ms silence

    # Add squelch at start and end with silence padding
    output = np.concatenate([squelch, silence, processed, silence, squelch])

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


def dramatic_narrator_effect(audio, sample_rate=22050):
    """
    Dramatic narrator effect (like Star Wars opening crawl)
    Deep, booming voice with epic reverb

    Args:
        audio: Input audio (numpy array, float -1.0 to 1.0)
        sample_rate: Audio sample rate (Hz)

    Returns:
        Audio with dramatic narrator effect
    """
    # 1. Pitch shift down for deeper voice (about 15% lower)
    # Simple pitch shifting using resampling
    pitch_factor = 0.85  # Lower = deeper voice

    # Resample to lower pitch
    from scipy.interpolate import interp1d
    original_length = len(audio)
    new_length = int(original_length / pitch_factor)

    # Create interpolation function
    x_original = np.arange(original_length)
    x_new = np.linspace(0, original_length - 1, new_length)
    interpolator = interp1d(x_original, audio, kind='linear', fill_value='extrapolate')
    pitched = interpolator(x_new)

    # Resample back to original length to maintain timing
    x_resample = np.linspace(0, new_length - 1, original_length)
    interpolator2 = interp1d(np.arange(new_length), pitched, kind='linear', fill_value='extrapolate')
    pitched_audio = interpolator2(x_resample)

    # 2. Add bass boost for more depth
    # High-pass filter first to avoid muddiness
    sos_hp = signal.butter(2, 100, 'highpass', fs=sample_rate, output='sos')
    clean = signal.sosfilt(sos_hp, pitched_audio)

    # Then boost low-mids (200-800 Hz)
    sos_boost = signal.butter(2, [200, 800], 'bandpass', fs=sample_rate, output='sos')
    bass_boosted = signal.sosfilt(sos_boost, clean) * 0.3
    with_bass = clean + bass_boosted

    # 3. Create reverb effect (large hall/space ambience)
    # Simple reverb using multiple delayed copies with decay
    reverb_audio = with_bass.copy()

    delays = [0.03, 0.05, 0.08, 0.12, 0.18, 0.25]  # seconds
    decays = [0.3, 0.25, 0.2, 0.15, 0.1, 0.08]

    for delay, decay in zip(delays, decays):
        delay_samples = int(delay * sample_rate)
        if delay_samples < len(with_bass):
            delayed = np.pad(with_bass, (delay_samples, 0), mode='constant')[:len(with_bass)]
            reverb_audio += delayed * decay

    # 4. Add slight chorus effect for richness
    # Small pitch variations
    chorus = np.copy(with_bass)
    for offset in [0.002, 0.003]:  # milliseconds
        offset_samples = int(offset * sample_rate)
        if offset_samples < len(with_bass):
            delayed = np.pad(with_bass, (offset_samples, 0), mode='constant')[:len(with_bass)]
            chorus += delayed * 0.15

    # Mix original with effects
    output = (reverb_audio * 0.6 + chorus * 0.4) * 1.3

    # 5. Apply gentle compression for dramatic effect
    output = np.tanh(output * 1.2)

    # Normalize
    max_val = np.abs(output).max()
    if max_val > 0.95:
        output = output / max_val * 0.95

    return output


def clear_transmission_effect(audio, sample_rate=22050):
    """
    Clear transmission effect - clarity of dramatic with radio character
    Optimized for female voice with transmission aesthetic

    Args:
        audio: Input audio (numpy array, float -1.0 to 1.0)
        sample_rate: Audio sample rate (Hz)

    Returns:
        Audio with clear transmission effect
    """
    # 1. Clean up the audio first (remove low rumble, keep voice clear)
    sos_hp = signal.butter(2, 80, 'highpass', fs=sample_rate, output='sos')
    clean = signal.sosfilt(sos_hp, audio)

    # 2. Add subtle reverb for space/depth (less than dramatic, more than comlink)
    reverb_audio = clean.copy()
    delays = [0.02, 0.04, 0.07, 0.11]  # milliseconds
    decays = [0.2, 0.15, 0.1, 0.08]

    for delay, decay in zip(delays, decays):
        delay_samples = int(delay * sample_rate)
        if delay_samples < len(clean):
            delayed = np.pad(clean, (delay_samples, 0), mode='constant')[:len(clean)]
            reverb_audio += delayed * decay

    # 3. Enhance presence (boost vocal frequencies for female voice)
    # Boost 2-4 kHz range for clarity
    sos_presence = signal.butter(2, [2000, 4000], 'bandpass', fs=sample_rate, output='sos')
    presence = signal.sosfilt(sos_presence, reverb_audio) * 0.25
    enhanced = reverb_audio + presence

    # 4. Apply light radio character (bandpass but wider than comlink)
    sos_radio = signal.butter(3, [350, 4500], 'bandpass', fs=sample_rate, output='sos')
    radio_tone = signal.sosfilt(sos_radio, enhanced)

    # 5. Add very light static (just enough for transmission feel)
    static = np.random.normal(0, 0.008, len(audio))
    with_static = radio_tone + static

    # 6. Light compression for consistency
    compressed = np.tanh(with_static * 1.1) * 0.95

    # 7. Generate squelch tone (softer than comlink)
    squelch_duration = int(0.10 * sample_rate)  # 100ms
    t = np.linspace(0, 0.10, squelch_duration)
    squelch = np.sin(2 * np.pi * 1200 * t) * 0.25

    # Fade in/out the squelch tone
    fade_len = squelch_duration // 4
    squelch[:fade_len] *= np.linspace(0, 1, fade_len)
    squelch[-fade_len:] *= np.linspace(1, 0, fade_len)

    # 8. Add brief silence before/after squelch
    silence = np.zeros(int(0.03 * sample_rate))  # 30ms silence

    # Add squelch at start and end
    output = np.concatenate([squelch, silence, compressed, silence, squelch])

    # Normalize
    max_val = np.abs(output).max()
    if max_val > 0.95:
        output = output / max_val * 0.95

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
