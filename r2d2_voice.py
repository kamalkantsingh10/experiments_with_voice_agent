#!/usr/bin/env python3
"""
R2D2-Style Robot Voice Generator

Generates expressive droid vocalizations (beeps, boops, whistles) based on emotion.
No models required - pure procedural audio synthesis.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional, List, Tuple
import random
from functools import lru_cache


@dataclass
class SoundParams:
    """Global parameters for sound generation"""
    freq_min: float = 200      # Hz - lowest frequency
    freq_max: float = 4000     # Hz - highest frequency
    duration_min: float = 0.02 # seconds
    duration_max: float = 0.8  # seconds
    amplitude: float = 0.4     # 0.0-1.0
    sample_rate: int = 44100   # Hz


class PhonemeProcessor:
    """
    Converts text to IPA phonemes and categorizes them for R2D2 sound mapping.

    Uses phonemizer library with espeak-ng backend to convert text to
    International Phonetic Alphabet (IPA) representations, then categorizes
    phonemes into groups for mapping to R2D2 sound primitives.
    """

    # IPA Phoneme category sets
    # Front vowels (high tongue position, front of mouth)
    VOWEL_FRONT = {'i', 'ɪ', 'e', 'ɛ', 'æ', 'iː', 'ɪə', 'eɪ'}

    # Central vowels (mid tongue position)
    VOWEL_CENTRAL = {'ə', 'ʌ', 'ɜ', 'ɚ', 'ɝ', 'ɐ'}

    # Back vowels (low tongue position, back of mouth)
    VOWEL_BACK = {'u', 'ʊ', 'o', 'ɔ', 'ɑ', 'ɒ', 'uː', 'ʊə', 'oʊ', 'ɔɪ', 'aɪ', 'aʊ'}

    # Voiceless plosives/stops (air burst, no vibration)
    PLOSIVE_VOICELESS = {'p', 't', 'k', 'ʔ'}

    # Voiced plosives/stops (air burst with vibration)
    PLOSIVE_VOICED = {'b', 'd', 'g'}

    # Voiceless fricatives (continuous airflow, no vibration)
    FRICATIVE_VOICELESS = {'f', 'θ', 's', 'ʃ', 'h', 'ʍ'}

    # Voiced fricatives (continuous airflow with vibration)
    FRICATIVE_VOICED = {'v', 'ð', 'z', 'ʒ'}

    # Nasals (air through nose)
    NASAL = {'m', 'n', 'ŋ'}

    # Approximants and liquids (smooth, vowel-like consonants)
    APPROXIMANT = {'l', 'r', 'w', 'j', 'ɹ', 'ɫ'}

    def __init__(self, language: str = 'en-us'):
        """
        Initialize phoneme processor.

        Args:
            language: Language code for phonemizer (default: 'en-us')
        """
        self.language = language
        self._phonemizer = None

    def _get_phonemizer(self):
        """Lazy initialization of phonemizer backend"""
        if self._phonemizer is None:
            try:
                from phonemizer import phonemize
                from phonemizer.backend import EspeakBackend
                # Test that espeak-ng is available
                EspeakBackend.version()
                self._phonemizer = phonemize
            except ImportError:
                raise ImportError(
                    "phonemizer library not found. Install with: pip install phonemizer"
                )
            except RuntimeError:
                raise RuntimeError(
                    "espeak-ng not found. Install with: sudo apt-get install espeak-ng"
                )
        return self._phonemizer

    def text_to_phonemes(self, text: str) -> List[Tuple[str, bool]]:
        """
        Convert text to IPA phonemes.

        Args:
            text: Input text to convert

        Returns:
            List of (phoneme, is_word_boundary) tuples where is_word_boundary
            indicates if this phoneme starts a new word
        """
        phonemize = self._get_phonemizer()

        # Convert to IPA phonemes, preserving word boundaries
        ipa = phonemize(
            text,
            language=self.language,
            backend='espeak',
            strip=True,
            preserve_punctuation=False,
            with_stress=False
        )

        # Parse IPA string into phonemes with word boundaries
        phonemes_with_boundaries = []
        words = text.split()
        ipa_words = ipa.split()

        for word_idx, ipa_word in enumerate(ipa_words):
            # Clean IPA word (remove stress marks, etc.)
            cleaned = ipa_word.strip()

            # Extract individual phonemes from IPA word
            for phoneme_idx, char in enumerate(cleaned):
                if char.strip():  # Skip whitespace
                    # Mark first phoneme of each word
                    is_word_boundary = (phoneme_idx == 0)
                    phonemes_with_boundaries.append((char, is_word_boundary))

        return phonemes_with_boundaries

    def categorize_phoneme(self, phoneme: str) -> str:
        """
        Categorize an IPA phoneme into a sound category.

        Args:
            phoneme: Single IPA phoneme character

        Returns:
            Category string: 'vowel_front', 'vowel_central', 'vowel_back',
            'plosive_voiceless', 'plosive_voiced', 'fricative_voiceless',
            'fricative_voiced', 'nasal', 'approximant', or 'unknown'
        """
        # Check vowels
        if phoneme in self.VOWEL_FRONT:
            return 'vowel_front'
        if phoneme in self.VOWEL_CENTRAL:
            return 'vowel_central'
        if phoneme in self.VOWEL_BACK:
            return 'vowel_back'

        # Check plosives
        if phoneme in self.PLOSIVE_VOICELESS:
            return 'plosive_voiceless'
        if phoneme in self.PLOSIVE_VOICED:
            return 'plosive_voiced'

        # Check fricatives
        if phoneme in self.FRICATIVE_VOICELESS:
            return 'fricative_voiceless'
        if phoneme in self.FRICATIVE_VOICED:
            return 'fricative_voiced'

        # Check nasals
        if phoneme in self.NASAL:
            return 'nasal'

        # Check approximants
        if phoneme in self.APPROXIMANT:
            return 'approximant'

        # Unknown phoneme - default to central vowel (neutral)
        return 'vowel_central'


class R2D2Voice:
    """
    R2D2-style emotive droid voice synthesizer.

    Generates robot sounds (beeps, boops, whistles, chirps) mapped to emotions.
    Uses pure procedural synthesis - no audio files or models needed.
    """

    # Emotion-to-sound mapping (for old speak() API only)
    EMOTION_SOUNDS = {
        'happy': ['chirp', 'whistle_up', 'trill'],
        'sad': ['moan', 'boop'],
        'excited': ['chirp', 'chirp', 'trill'],
        'curious': ['boop', 'whistle_up'],
        'angry': ['growl', 'beep'],
        'sleepy': ['moan', 'moan', 'boop'],
        'afraid': ['beep', 'beep', 'whistle_up'],
        'surprised': ['whistle_up', 'beep'],
        'confident': ['beep', 'whistle_short'],
        'playful': ['chirp', 'trill', 'whistle_up'],
    }

    # Phoneme-to-sound mapping for text-to-speech (reduced chirp usage)
    PHONEME_SOUND_MAP = {
        'vowel_front': ['whistle_up', 'whistle_short', 'trill'],
        'vowel_central': ['boop', 'whistle_short', 'moan'],
        'vowel_back': ['moan', 'boop', 'growl'],
        'plosive_voiceless': ['beep', 'whistle_short', 'trill'],  # Removed chirp
        'plosive_voiced': ['boop', 'trill', 'moan'],  # Removed chirp
        'fricative_voiceless': ['whistle_short', 'whistle_up', 'trill'],
        'fricative_voiced': ['growl', 'moan', 'boop'],
        'nasal': ['boop', 'moan', 'whistle_short'],  # Reduced chirp
        'approximant': ['trill', 'whistle_short', 'whistle_up'],  # Removed chirp
    }

    # Phoneme duration constants (seconds)
    PHONEME_DURATIONS = {
        'vowel_front': 0.12,
        'vowel_central': 0.12,
        'vowel_back': 0.12,
        'plosive_voiceless': 0.06,
        'plosive_voiced': 0.06,
        'fricative_voiceless': 0.10,
        'fricative_voiced': 0.10,
        'nasal': 0.11,
        'approximant': 0.09,
    }

    # Timing constants for rhythm and word boundaries
    WORD_GAP = 0.18        # Seconds between words
    SYLLABLE_GAP = 0.05    # Seconds between sounds within word

    # Emotion pitch shift multipliers (EXTREME 0.5x - 3.0x range)
    EMOTION_PITCH_SHIFTS = {
        'sleepy': 0.5,       # Extremely low, drowsy
        'sad': 0.6,          # Very low
        'angry': 0.7,        # Low and growly
        'confident': 1.2,    # Slightly high, assertive
        'curious': 1.5,      # Medium-high, questioning
        'playful': 1.7,      # High, bouncy
        'surprised': 1.9,    # High, sharp
        'afraid': 2.2,       # Very high, nervous
        'happy': 2.5,        # Very high, cheerful
        'excited': 3.0,      # EXTREMELY high, rapid
    }

    # Emotion speed multipliers (EXTREME 0.5x - 3.0x duration range)
    EMOTION_SPEED_FACTORS = {
        'excited': 0.5,      # 2x faster - very rapid
        'happy': 0.6,        # 1.67x faster - quick and bouncy
        'afraid': 0.65,      # 1.5x faster - jittery, nervous
        'surprised': 0.7,    # 1.4x faster - sudden, quick
        'angry': 0.75,       # 1.3x faster - aggressive bursts
        'playful': 0.8,      # 1.25x faster - bouncy
        'confident': 0.9,    # 1.1x faster - steady, assertive
        'curious': 1.2,      # 1.2x slower - thoughtful
        'sad': 2.0,          # 2x slower - drawn out
        'sleepy': 3.0,       # 3x slower - very drowsy
    }

    def __init__(self, sample_rate: int = 44100, seed: Optional[int] = None, language: str = 'en-us'):
        """
        Initialize R2D2 voice generator.

        Args:
            sample_rate: Audio sample rate in Hz
            seed: Random seed for reproducible generation
            language: Language code for text-to-speech phonemizer (default: 'en-us')
        """
        self.params = SoundParams(sample_rate=sample_rate)
        self.language = language
        self._phoneme_processor = None  # Lazy initialization
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    def _apply_envelope(self, signal: np.ndarray,
                       attack: float = 0.05,
                       decay: float = 0.1,
                       sustain: float = 0.7,
                       release: float = 0.15) -> np.ndarray:
        """Apply ADSR envelope to signal"""
        n = len(signal)
        envelope = np.ones(n)

        # Attack
        attack_samples = int(attack * n)
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

        # Decay
        decay_samples = int(decay * n)
        sustain_level = sustain
        if decay_samples > 0:
            decay_end = attack_samples + decay_samples
            envelope[attack_samples:decay_end] = np.linspace(1, sustain_level, decay_samples)

        # Sustain (already at sustain_level)
        sustain_start = attack_samples + decay_samples
        sustain_end = n - int(release * n)
        if sustain_end > sustain_start:
            envelope[sustain_start:sustain_end] = sustain_level

        # Release
        release_samples = int(release * n)
        if release_samples > 0:
            envelope[-release_samples:] = np.linspace(sustain_level, 0, release_samples)

        return signal * envelope

    def beep(self, freq: float = 1000, duration: float = 0.1) -> np.ndarray:
        """Generate a clean single-frequency beep"""
        t = np.linspace(0, duration, int(self.params.sample_rate * duration))
        signal = np.sin(2 * np.pi * freq * t)
        return self._apply_envelope(signal, attack=0.01, decay=0.05, sustain=0.8, release=0.14)

    def boop(self) -> np.ndarray:
        """Generate a soft low-frequency boop"""
        freq = random.uniform(200, 400)
        duration = random.uniform(0.08, 0.15)
        t = np.linspace(0, duration, int(self.params.sample_rate * duration))
        signal = np.sin(2 * np.pi * freq * t)
        return self._apply_envelope(signal, attack=0.1, decay=0.2, sustain=0.6, release=0.1)

    def whistle(self, ascending: bool = True) -> np.ndarray:
        """Generate a frequency sweep whistle"""
        duration = random.uniform(0.2, 0.5)

        if ascending:
            f_start = random.uniform(800, 1200)
            f_end = random.uniform(2000, 3000)
        else:
            f_start = random.uniform(2000, 3000)
            f_end = random.uniform(800, 1200)

        t = np.linspace(0, duration, int(self.params.sample_rate * duration))

        # Linear frequency sweep
        freq = np.linspace(f_start, f_end, len(t))
        phase = np.cumsum(freq) * 2 * np.pi / self.params.sample_rate

        signal = np.sin(phase)
        return self._apply_envelope(signal, attack=0.05, decay=0.1, sustain=0.7, release=0.15)

    def chirp(self) -> np.ndarray:
        """Generate a rapid high-pitched chirp"""
        freq = random.uniform(2000, 3500)
        duration = random.uniform(0.05, 0.12)

        t = np.linspace(0, duration, int(self.params.sample_rate * duration))

        # Add some frequency modulation for character
        vibrato = 50 * np.sin(2 * np.pi * 20 * t)
        signal = np.sin(2 * np.pi * (freq + vibrato) * t)

        return self._apply_envelope(signal, attack=0.02, decay=0.3, sustain=0.5, release=0.18)

    def moan(self) -> np.ndarray:
        """Generate a low descending moan"""
        duration = random.uniform(0.3, 0.6)
        f_start = random.uniform(400, 600)
        f_end = random.uniform(200, 300)

        t = np.linspace(0, duration, int(self.params.sample_rate * duration))
        freq = np.linspace(f_start, f_end, len(t))
        phase = np.cumsum(freq) * 2 * np.pi / self.params.sample_rate

        signal = np.sin(phase)
        return self._apply_envelope(signal, attack=0.15, decay=0.2, sustain=0.5, release=0.15)

    def growl(self) -> np.ndarray:
        """Generate a low rumbling growl"""
        duration = random.uniform(0.15, 0.3)
        base_freq = random.uniform(150, 250)

        t = np.linspace(0, duration, int(self.params.sample_rate * duration))

        # Multiple harmonics for rough sound
        signal = np.sin(2 * np.pi * base_freq * t)
        signal += 0.5 * np.sin(2 * np.pi * base_freq * 2 * t)
        signal += 0.3 * np.sin(2 * np.pi * base_freq * 3 * t)

        # Add amplitude modulation for growl effect
        mod = 1 + 0.5 * np.sin(2 * np.pi * 30 * t)
        signal = signal * mod

        return self._apply_envelope(signal, attack=0.1, decay=0.2, sustain=0.6, release=0.1)

    def trill(self) -> np.ndarray:
        """Generate rapid pitch oscillations (laugh-like)"""
        duration = random.uniform(0.2, 0.4)
        base_freq = random.uniform(1500, 2500)

        t = np.linspace(0, duration, int(self.params.sample_rate * duration))

        # Rapid frequency modulation
        mod_freq = random.uniform(15, 25)
        mod_depth = random.uniform(200, 400)
        freq_mod = base_freq + mod_depth * np.sin(2 * np.pi * mod_freq * t)

        signal = np.sin(2 * np.pi * freq_mod * t)
        return self._apply_envelope(signal, attack=0.05, decay=0.15, sustain=0.7, release=0.1)

    def alarm(self) -> np.ndarray:
        """Generate an oscillating siren-like alarm"""
        duration = random.uniform(0.3, 0.5)
        f_low = random.uniform(800, 1000)
        f_high = random.uniform(1500, 2000)

        t = np.linspace(0, duration, int(self.params.sample_rate * duration))

        # Oscillate between two frequencies
        cycles = 3
        freq = f_low + (f_high - f_low) * (0.5 + 0.5 * np.sin(2 * np.pi * cycles * t / duration))

        signal = np.sin(2 * np.pi * freq * t)
        return self._apply_envelope(signal, attack=0.01, decay=0.1, sustain=0.8, release=0.09)

    def whistle_short(self) -> np.ndarray:
        """Short affirming whistle"""
        duration = 0.15
        f_start = random.uniform(900, 1500)
        f_end = random.uniform(1800, 2200)

        t = np.linspace(0, duration, int(self.params.sample_rate * duration))
        freq = np.linspace(f_start, f_end, len(t))
        phase = np.cumsum(freq) * 2 * np.pi / self.params.sample_rate

        signal = np.sin(phase)
        return self._apply_envelope(signal, attack=0.02, decay=0.1, sustain=0.7, release=0.18)

    def _get_phoneme_processor(self) -> PhonemeProcessor:
        """Lazy initialization of phoneme processor"""
        if self._phoneme_processor is None:
            self._phoneme_processor = PhonemeProcessor(self.language)
        return self._phoneme_processor

    def _create_word_boundary(self, duration: float) -> np.ndarray:
        """Create silence for word boundaries"""
        silence_samples = int(duration * self.params.sample_rate)
        return np.zeros(silence_samples, dtype=np.float32)

    def _apply_pitch_shift(self, signal: np.ndarray, pitch_factor: float) -> np.ndarray:
        """
        Apply pitch shift to audio signal.

        Simple implementation: resample and adjust playback rate.
        For more sophisticated pitch shifting, could use phase vocoder.
        """
        if pitch_factor == 1.0:
            return signal

        # Simple pitch shift via resampling
        # Higher pitch_factor = higher frequency (compress time, then stretch back)
        from scipy import signal as scipy_signal

        # Number of samples after pitch shift
        new_length = int(len(signal) / pitch_factor)

        # Resample to new length
        resampled = scipy_signal.resample(signal, new_length)

        # Stretch/compress back to original duration
        final = scipy_signal.resample(resampled, len(signal))

        return final.astype(np.float32)

    def _apply_emotion_to_sound(self, signal: np.ndarray, emotion: str,
                                clarity: float) -> np.ndarray:
        """
        Apply emotion modulation to a sound.

        Args:
            signal: Input audio signal
            emotion: Emotion type
            clarity: 0.0-1.0, how much to apply emotion (0=full emotion, 1=no emotion)

        Returns:
            Modulated audio signal
        """
        # Interpolate pitch shift based on clarity
        # clarity=0 means full emotion, clarity=1 means no emotion (neutral)
        emotion_pitch = self.EMOTION_PITCH_SHIFTS.get(emotion, 1.0)
        effective_pitch = 1.0 + (emotion_pitch - 1.0) * (1.0 - clarity)

        # Apply pitch shift
        signal = self._apply_pitch_shift(signal, effective_pitch)

        # Apply speed factor to duration (handled at generation time)

        return signal

    def _blend_phoneme_emotion(self, phoneme_category: str, emotion: str,
                               clarity: float) -> str:
        """
        Select R2D2 sound based on phoneme category and emotion.

        Args:
            phoneme_category: Phoneme category (e.g., 'vowel_front')
            emotion: Emotion type
            clarity: How much to emphasize phonetics vs emotion

        Returns:
            Selected R2D2 sound name
        """
        # Get possible sounds for this phoneme
        possible_sounds = self.PHONEME_SOUND_MAP.get(phoneme_category, ['boop'])

        if len(possible_sounds) == 1:
            return possible_sounds[0]

        # Emotion-based sound preferences (EXTREME biases for distinct emotions)
        emotion_preferences = {
            'happy': {'trill': 2.0, 'whistle_up': 1.8, 'whistle_short': 1.5},
            'sad': {'moan': 2.2, 'boop': 1.8, 'growl': 1.4},
            'excited': {'trill': 2.5, 'whistle_up': 2.0, 'beep': 1.6},
            'angry': {'growl': 2.3, 'beep': 1.7, 'moan': 1.3},
            'curious': {'whistle_up': 1.8, 'whistle_short': 1.5, 'trill': 1.3},
            'sleepy': {'moan': 2.5, 'boop': 2.0, 'growl': 1.5},
            'afraid': {'beep': 2.0, 'whistle_up': 1.8, 'whistle_short': 1.5},
            'surprised': {'whistle_up': 2.2, 'beep': 1.9, 'trill': 1.4},
            'confident': {'beep': 1.9, 'whistle_short': 1.6, 'trill': 1.3},
            'playful': {'trill': 2.0, 'whistle_up': 1.7, 'whistle_short': 1.4},
        }

        preferences = emotion_preferences.get(emotion, {})

        # Weight sounds by emotion preference, modulated by clarity
        # clarity=1 means ignore emotion (uniform random)
        # clarity=0 means full emotion bias (but still subtle)
        weights = []
        for sound in possible_sounds:
            base_weight = 1.0
            emotion_weight = preferences.get(sound, 1.0)
            # Blend between base and emotion weight based on clarity
            final_weight = base_weight * clarity + emotion_weight * (1.0 - clarity)
            weights.append(final_weight)

        # Normalize weights
        total = sum(weights)
        if total > 0:
            weights = [w / total for w in weights]
        else:
            weights = [1.0 / len(weights)] * len(weights)

        # Select sound based on weights
        return np.random.choice(possible_sounds, p=weights)

    @lru_cache(maxsize=512)
    def _generate_base_phoneme_sound(self, phoneme_category: str, sound_type: str,
                                     duration: float) -> np.ndarray:
        """
        Generate base R2D2 sound for phoneme (cached).

        Args:
            phoneme_category: Phoneme category
            sound_type: R2D2 sound type to generate
            duration: Sound duration in seconds

        Returns:
            Audio signal (before emotion modulation)
        """
        # Generate the appropriate R2D2 sound
        # Use duration-specific generation for each sound type

        sound_generators = {
            'beep': lambda: self.beep(freq=1000, duration=duration),
            'boop': lambda: self.boop(),
            'whistle_up': lambda: self.whistle(ascending=True),
            'whistle_down': lambda: self.whistle(ascending=False),
            'whistle_short': lambda: self.whistle_short(),
            'chirp': lambda: self.chirp(),
            'moan': lambda: self.moan(),
            'growl': lambda: self.growl(),
            'trill': lambda: self.trill(),
        }

        if sound_type in sound_generators:
            return sound_generators[sound_type]()
        else:
            # Default to beep
            return self.beep(freq=1000, duration=duration)

    def _generate_sound(self, sound_name: str) -> np.ndarray:
        """Generate a specific sound by name"""
        sound_map = {
            'beep': lambda: self.beep(),
            'boop': lambda: self.boop(),
            'whistle_up': lambda: self.whistle(ascending=True),
            'whistle_down': lambda: self.whistle(ascending=False),
            'whistle_short': lambda: self.whistle_short(),
            'chirp': lambda: self.chirp(),
            'moan': lambda: self.moan(),
            'growl': lambda: self.growl(),
            'trill': lambda: self.trill(),
            'alarm': lambda: self.alarm(),
        }

        if sound_name in sound_map:
            return sound_map[sound_name]()
        else:
            # Default to beep
            return self.beep()

    def speak(self, emotion: str, intensity: float = 1.0) -> np.ndarray:
        """
        Generate R2D2-style audio for given emotion.

        Args:
            emotion: One of the supported emotion labels
            intensity: Emotion strength (0.0-2.0), affects pitch range and speed

        Returns:
            Audio samples as numpy float32 array, normalized to [-1, 1]
        """
        # Get sound palette for this emotion
        if emotion not in self.EMOTION_SOUNDS:
            emotion = 'affirmative'  # Default

        sounds = self.EMOTION_SOUNDS[emotion]

        # Select 1-3 sounds from palette
        num_sounds = random.randint(1, min(3, len(sounds)))
        selected_sounds = random.sample(sounds, num_sounds)

        # Generate each sound
        audio_segments = []
        for sound_name in selected_sounds:
            segment = self._generate_sound(sound_name)
            audio_segments.append(segment)

            # Add gap between sounds
            gap_duration = random.uniform(0.05, 0.15)
            gap_samples = int(gap_duration * self.params.sample_rate)
            audio_segments.append(np.zeros(gap_samples))

        # Concatenate all segments
        audio = np.concatenate(audio_segments)

        # Apply intensity scaling
        audio = audio * min(intensity, 2.0)

        # Normalize
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val * self.params.amplitude

        return audio.astype(np.float32)

    def speak_text(self, text: str, emotion: str = 'affirmative',
                   intensity: float = 1.0, clarity: float = 0.3, speed: float = 3.0) -> np.ndarray:
        """
        Generate R2D2-style phonetic speech from text.

        Converts text to IPA phonemes, maps them to R2D2 sounds, and applies
        emotion modulation. Sound duration is proportional to text length,
        with word boundaries providing rhythmic structure.

        Args:
            text: Input text to speak
            emotion: Emotion to blend into phonetic sounds
                    Options: happy, sad, excited, angry, sleepy, afraid,
                            surprised, curious, confident, playful
            intensity: Overall volume/energy level (0.0-2.0)
            clarity: Phonetic emphasis vs emotion balance (0.0-1.0)
                    0.0 = pure emotion (like old speak())
                    1.0 = pure phonetics (maximum rhythm hints)
                    0.3 = recommended balance (default)
            speed: Playback speed multiplier (0.5-5.0)
                    3.0 = normal speed (default)
                    1.0 = 3x slower
                    5.0 = 1.67x faster

        Returns:
            Audio samples as numpy float32 array, normalized to [-1, 1]

        Example:
            voice = R2D2Voice()
            audio = voice.speak_text("I am good", emotion='happy')
            # → 3 word clusters, happy pitch, ~0.8s duration

            # Default 3x speed
            audio = voice.speak_text("I am good", emotion='happy')
        """
        # Get phoneme processor
        processor = self._get_phoneme_processor()

        # Convert text to phonemes with word boundaries
        phonemes_with_boundaries = processor.text_to_phonemes(text)

        # Get emotion speed factor and combine with user speed parameter
        emotion_speed = self.EMOTION_SPEED_FACTORS.get(emotion, 1.0)
        # Final speed: emotion affects base, then user speed multiplies
        # speed=2.0 means 2x faster (half the duration)
        speed_factor = emotion_speed / speed

        # Generate audio for each phoneme
        audio_segments = []

        for phoneme, is_word_boundary in phonemes_with_boundaries:
            # Add word boundary gap if this starts a new word
            if is_word_boundary and len(audio_segments) > 0:
                gap = self._create_word_boundary(self.WORD_GAP * speed_factor)
                audio_segments.append(gap)

            # Categorize phoneme
            category = processor.categorize_phoneme(phoneme)

            # Select R2D2 sound based on phoneme and emotion
            sound_type = self._blend_phoneme_emotion(category, emotion, clarity)

            # Get duration for this phoneme category
            base_duration = self.PHONEME_DURATIONS.get(category, 0.10)
            duration = base_duration * speed_factor

            # Generate base sound (this is cached)
            # Note: can't cache numpy arrays with lru_cache, so we'll generate fresh
            # Generate the sound with random frequency variations for more variety
            # Add ±15% random pitch variation to each sound
            freq_variation = random.uniform(0.85, 1.15)

            if sound_type == 'beep':
                base_freq = 1000 * freq_variation
                segment = self.beep(freq=base_freq, duration=duration)
            elif sound_type == 'boop':
                segment = self.boop()
            elif sound_type == 'whistle_up':
                segment = self.whistle(ascending=True)
            elif sound_type == 'whistle_down':
                segment = self.whistle(ascending=False)
            elif sound_type == 'whistle_short':
                segment = self.whistle_short()
            elif sound_type == 'chirp':
                segment = self.chirp()
            elif sound_type == 'moan':
                segment = self.moan()
            elif sound_type == 'growl':
                segment = self.growl()
            elif sound_type == 'trill':
                segment = self.trill()
            else:
                base_freq = 1000 * freq_variation
                segment = self.beep(freq=base_freq, duration=duration)

            # Apply emotion modulation (pitch shift)
            segment = self._apply_emotion_to_sound(segment, emotion, clarity)

            audio_segments.append(segment)

            # Add small gap between phonemes within same word
            syllable_gap = self._create_word_boundary(self.SYLLABLE_GAP * speed_factor)
            audio_segments.append(syllable_gap)

        # Concatenate all segments
        if len(audio_segments) == 0:
            # Empty text - return silence
            return np.zeros(int(0.1 * self.params.sample_rate), dtype=np.float32)

        audio = np.concatenate(audio_segments)

        # Apply intensity scaling
        audio = audio * min(intensity, 2.0)

        # Normalize
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val * self.params.amplitude

        return audio.astype(np.float32)

    def play(self, emotion: str, intensity: float = 1.0) -> None:
        """Generate and play audio for given emotion"""
        try:
            import sounddevice as sd
            audio = self.speak(emotion, intensity)
            sd.play(audio, self.params.sample_rate)
            sd.wait()
        except ImportError:
            print("sounddevice not installed. Cannot play audio.")
            print("Install with: pip install sounddevice")

    def play_text(self, text: str, emotion: str = 'affirmative',
                  intensity: float = 1.0, clarity: float = 0.3, speed: float = 3.0) -> None:
        """Generate and play phonetic speech from text"""
        try:
            import sounddevice as sd
            audio = self.speak_text(text, emotion, intensity, clarity, speed)
            sd.play(audio, self.params.sample_rate)
            sd.wait()
        except ImportError:
            print("sounddevice not installed. Cannot play audio.")
            print("Install with: pip install sounddevice")

    def save(self, emotion: str, filepath: str, intensity: float = 1.0) -> None:
        """Generate and save audio to WAV file"""
        import wave

        audio = self.speak(emotion, intensity)

        # Convert to 16-bit PCM
        audio_int16 = (audio * 32767).astype(np.int16)

        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.params.sample_rate)
            wf.writeframes(audio_int16.tobytes())

        print(f"✓ Saved audio to {filepath}")

    def save_text(self, text: str, filepath: str, emotion: str = 'affirmative',
                  intensity: float = 1.0, clarity: float = 0.3, speed: float = 3.0) -> None:
        """Generate phonetic speech and save to WAV file"""
        import wave

        audio = self.speak_text(text, emotion, intensity, clarity, speed)

        # Convert to 16-bit PCM
        audio_int16 = (audio * 32767).astype(np.int16)

        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.params.sample_rate)
            wf.writeframes(audio_int16.tobytes())

        print(f"✓ Saved phonetic speech to {filepath}")


# Convenience functions
def speak(emotion: str, intensity: float = 1.0) -> np.ndarray:
    """Quick generation without instantiating class"""
    voice = R2D2Voice()
    return voice.speak(emotion, intensity)


def play(emotion: str, intensity: float = 1.0) -> None:
    """Quick playback without instantiating class"""
    voice = R2D2Voice()
    voice.play(emotion, intensity)


def speak_text(text: str, emotion: str = 'affirmative',
               intensity: float = 1.0, clarity: float = 0.3, speed: float = 3.0) -> np.ndarray:
    """Quick phonetic speech generation without instantiating class"""
    voice = R2D2Voice()
    return voice.speak_text(text, emotion, intensity, clarity, speed)


def play_text(text: str, emotion: str = 'affirmative',
              intensity: float = 1.0, clarity: float = 0.3, speed: float = 3.0) -> None:
    """Quick phonetic speech playback without instantiating class"""
    voice = R2D2Voice()
    voice.play_text(text, emotion, intensity, clarity, speed)
