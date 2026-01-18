#!/usr/bin/env python3
"""
R2D2 Word-Based Vocabulary System

Maps common English words to unique sound sequence lengths (1-5 notes each).
Emotion controls which specific sounds are selected, plus pitch/speed modulation.
"""

import numpy as np
import random
from typing import List, Optional, Dict
from dataclasses import dataclass


@dataclass
class SoundParams:
    """Global parameters for sound generation"""
    freq_min: float = 200
    freq_max: float = 5000
    sample_rate: int = 44100
    amplitude: float = 0.4


class R2D2WordVocabulary:
    """
    Word-based R2D2 speaker with emotion-influenced sound selection.

    Each word maps to a consistent sequence length (1-5 notes).
    Emotion determines which sounds are selected + pitch/speed.
    """

    # 12 sound primitives
    SOUNDS = [
        'beep', 'boop', 'chirp', 'stutter', 'warble', 'buzz',
        'ping', 'blip', 'slide_down', 'chord', 'tremolo', 'sweep_up_down'
    ]

    # Emotion-based sound preferences (weights for selection)
    EMOTION_SOUND_WEIGHTS = {
        'neutral': {
            'beep': 1.0, 'boop': 1.0, 'chirp': 1.0, 'stutter': 0.5,
            'warble': 0.8, 'buzz': 0.5, 'ping': 1.0, 'blip': 1.0,
            'slide_down': 0.5, 'chord': 0.8, 'tremolo': 0.5, 'sweep_up_down': 0.8
        },
        'happy': {
            'beep': 1.5, 'boop': 0.8, 'chirp': 2.5, 'stutter': 0.3,
            'warble': 1.2, 'buzz': 0.2, 'ping': 2.0, 'blip': 2.2,
            'slide_down': 0.1, 'chord': 2.0, 'tremolo': 0.5, 'sweep_up_down': 1.5
        },
        'sad': {
            'beep': 0.5, 'boop': 2.0, 'chirp': 0.2, 'stutter': 0.3,
            'warble': 1.5, 'buzz': 0.8, 'ping': 0.2, 'blip': 0.3,
            'slide_down': 2.5, 'chord': 0.5, 'tremolo': 2.0, 'sweep_up_down': 0.5
        },
        'angry': {
            'beep': 1.5, 'boop': 1.0, 'chirp': 0.5, 'stutter': 2.0,
            'warble': 1.0, 'buzz': 2.5, 'ping': 1.2, 'blip': 0.8,
            'slide_down': 0.5, 'chord': 0.3, 'tremolo': 1.5, 'sweep_up_down': 1.0
        },
        'excited': {
            'beep': 2.0, 'boop': 0.5, 'chirp': 2.5, 'stutter': 2.2,
            'warble': 1.5, 'buzz': 0.8, 'ping': 2.5, 'blip': 2.5,
            'slide_down': 0.2, 'chord': 1.5, 'tremolo': 1.0, 'sweep_up_down': 2.0
        },
        'curious': {
            'beep': 1.2, 'boop': 1.5, 'chirp': 1.5, 'stutter': 0.8,
            'warble': 2.0, 'buzz': 0.5, 'ping': 1.5, 'blip': 1.3,
            'slide_down': 0.8, 'chord': 1.2, 'tremolo': 1.0, 'sweep_up_down': 2.5
        },
        'confused': {
            'beep': 1.0, 'boop': 1.5, 'chirp': 0.8, 'stutter': 1.8,
            'warble': 2.5, 'buzz': 1.0, 'ping': 1.0, 'blip': 1.2,
            'slide_down': 1.2, 'chord': 0.5, 'tremolo': 2.0, 'sweep_up_down': 2.5
        },
        'lazy': {
            'beep': 0.8, 'boop': 2.5, 'chirp': 0.2, 'stutter': 0.1,
            'warble': 1.8, 'buzz': 1.5, 'ping': 0.3, 'blip': 0.2,
            'slide_down': 2.0, 'chord': 1.0, 'tremolo': 1.5, 'sweep_up_down': 0.5
        },
        'afraid': {
            'beep': 2.0, 'boop': 0.8, 'chirp': 1.5, 'stutter': 2.5,
            'warble': 2.0, 'buzz': 1.2, 'ping': 1.8, 'blip': 2.0,
            'slide_down': 1.0, 'chord': 0.5, 'tremolo': 2.5, 'sweep_up_down': 1.8
        },
        'naughty': {
            'beep': 1.5, 'boop': 1.2, 'chirp': 2.0, 'stutter': 1.8,
            'warble': 1.8, 'buzz': 1.5, 'ping': 2.0, 'blip': 2.2,
            'slide_down': 0.8, 'chord': 1.5, 'tremolo': 1.2, 'sweep_up_down': 2.2
        },
    }

    # Emotion pitch shifts (multipliers applied to all frequencies)
    EMOTION_PITCH = {
        'neutral': 1.0,
        'happy': 1.4,
        'sad': 0.7,
        'angry': 0.6,
        'excited': 1.6,
        'curious': 1.3,
        'confused': 1.2,
        'lazy': 0.65,
        'afraid': 1.5,
        'naughty': 1.35,
    }

    # Emotion speed multipliers (higher = faster)
    EMOTION_SPEED = {
        'neutral': 1.0,
        'happy': 1.3,
        'sad': 0.6,
        'angry': 1.4,
        'excited': 1.8,
        'curious': 0.9,
        'confused': 0.8,
        'lazy': 0.5,
        'afraid': 1.5,
        'naughty': 1.2,
    }

    # Top 500 most common English words (from Google Trillion Word Corpus)
    COMMON_WORDS = [
        "the", "of", "and", "to", "a", "in", "for", "is", "on", "that",
        "by", "this", "with", "i", "you", "it", "not", "or", "be", "are",
        "from", "at", "as", "your", "all", "have", "new", "more", "an", "was",
        "we", "will", "home", "can", "us", "about", "if", "page", "my", "has",
        "search", "free", "but", "our", "one", "other", "do", "no", "information", "time",
        "they", "site", "he", "up", "may", "what", "which", "their", "news", "out",
        "use", "any", "there", "see", "only", "so", "his", "when", "contact", "here",
        "business", "who", "web", "also", "now", "help", "get", "pm", "view", "online",
        "c", "e", "first", "am", "been", "would", "how", "were", "me", "s",
        "services", "some", "these", "click", "its", "like", "service", "x", "than", "find",
        "price", "date", "back", "top", "people", "had", "list", "name", "just", "over",
        "state", "year", "day", "into", "email", "two", "health", "n", "world", "re",
        "next", "used", "go", "b", "work", "last", "most", "products", "music", "buy",
        "data", "make", "them", "should", "product", "system", "post", "her", "city", "t",
        "add", "policy", "number", "such", "please", "available", "copyright", "support", "message", "after",
        "best", "software", "then", "jan", "good", "video", "well", "d", "where", "info",
        "rights", "public", "books", "high", "school", "through", "m", "each", "links", "she",
        "review", "years", "order", "very", "privacy", "book", "items", "company", "r", "read",
        "group", "need", "many", "user", "said", "de", "does", "set", "under", "general",
        "research", "university", "january", "mail", "full", "map", "reviews", "program", "life", "know",
        "games", "way", "days", "management", "p", "part", "could", "great", "united", "hotel",
        "real", "f", "item", "international", "center", "ebay", "must", "store", "travel", "comments",
        "made", "development", "report", "off", "member", "details", "line", "terms", "before", "hotels",
        "did", "send", "right", "type", "because", "local", "those", "using", "results", "office",
        "education", "national", "car", "design", "take", "posted", "internet", "address", "community", "within",
        "states", "area", "want", "phone", "dvd", "shipping", "reserved", "subject", "between", "forum",
        "family", "l", "long", "based", "w", "code", "show", "o", "even", "black",
        "check", "special", "prices", "website", "index", "being", "women", "much", "sign", "file",
        "link", "open", "today", "technology", "south", "case", "project", "same", "pages", "uk",
        "version", "section", "own", "found", "sports", "house", "related", "security", "both", "g",
        "county", "american", "photo", "game", "members", "power", "while", "care", "network", "down",
        "computer", "systems", "three", "total", "place", "end", "following", "download", "h", "him",
        "without", "per", "access", "think", "north", "resources", "current", "posts", "big", "media",
        "law", "control", "water", "history", "pictures", "size", "art", "personal", "since", "including",
        "guide", "shop", "directory", "board", "location", "change", "white", "text", "small", "rating",
        "rate", "government", "children", "during", "usa", "return", "students", "v", "shopping", "account",
        "times", "sites", "level", "digital", "profile", "previous", "form", "events", "love", "old",
        "john", "main", "call", "hours", "image", "department", "title", "description", "non", "k",
        "y", "insurance", "another", "why", "shall", "property", "class", "cd", "still", "money",
        "quality", "every", "listing", "content", "country", "private", "little", "visit", "save", "tools",
        "low", "reply", "customer", "december", "compare", "movies", "include", "college", "value", "article",
        "york", "man", "card", "jobs", "provide", "j", "food", "source", "author", "different",
        "press", "u", "learn", "sale", "around", "print", "course", "job", "canada", "process",
        "teen", "room", "stock", "training", "too", "credit", "point", "join", "science", "men",
        "categories", "advanced", "west", "sales", "look", "english", "left", "team", "estate", "box",
        "conditions", "select", "windows", "photos", "gay", "thread", "week", "category", "note", "live",
        "large", "gallery", "table", "register", "however", "june", "october", "november", "market", "library",
        "really", "action", "start", "series", "model", "features", "air", "industry", "plan", "human",
        "provided", "tv", "yes", "required", "second", "hot", "accessories", "cost", "movie", "forums",
        "march", "la", "september", "better", "say", "questions", "july", "yahoo", "going", "medical",
        "test", "friend", "come", "dec", "server", "pc", "study", "application", "cart", "staff",
        "articles", "san", "feedback", "again", "play", "looking", "issues", "april", "never", "users",
        "complete", "street", "topic", "comment", "financial", "things", "working", "against", "standard", "tax",
        "person", "below", "mobile", "less", "got", "blog", "party", "payment", "equipment", "login",
        "student"
    ]

    def __init__(self, sample_rate: int = 44100, seed: Optional[int] = None):
        """
        Initialize word vocabulary system.

        Args:
            sample_rate: Audio sample rate in Hz
            seed: Random seed for reproducible word-to-length mapping
        """
        self.params = SoundParams(sample_rate=sample_rate)
        self._word_lengths = {}

        # Set seed for reproducible word mappings
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        # Generate word-to-length mappings (1-5 notes per word)
        self._initialize_word_lengths()

    def _initialize_word_lengths(self):
        """Generate consistent sequence lengths for each common word"""
        for word in self.COMMON_WORDS:
            # Deterministic: use word hash to determine length
            word_hash = abs(hash(word))
            # Map hash to 1-5 note sequence
            length = (word_hash % 5) + 1
            self._word_lengths[word.lower()] = length

    def get_word_length(self, word: str) -> int:
        """
        Get sequence length for a word.

        Args:
            word: Input word (case-insensitive)

        Returns:
            Sequence length (1-5 notes)
        """
        word_lower = word.lower()
        if word_lower in self._word_lengths:
            return self._word_lengths[word_lower]
        else:
            # Unknown word: always 2 notes
            return 2

    def _select_sound_for_emotion(self, emotion: str) -> str:
        """
        Select a sound based on emotion preferences.

        Args:
            emotion: Emotion name

        Returns:
            Selected sound name
        """
        weights_dict = self.EMOTION_SOUND_WEIGHTS.get(emotion, self.EMOTION_SOUND_WEIGHTS['neutral'])

        # Extract sounds and weights
        sounds = list(weights_dict.keys())
        weights = list(weights_dict.values())

        # Normalize weights
        total = sum(weights)
        if total > 0:
            probabilities = [w / total for w in weights]
        else:
            probabilities = [1.0 / len(sounds)] * len(sounds)

        # Select sound
        return np.random.choice(sounds, p=probabilities)

    # ===== Sound Generation Methods =====

    def _apply_envelope(self, signal: np.ndarray,
                       attack: float = 0.05,
                       decay: float = 0.1,
                       sustain: float = 0.7,
                       release: float = 0.15) -> np.ndarray:
        """Apply ADSR envelope to signal"""
        n = len(signal)
        if n == 0:
            return signal

        envelope = np.ones(n)

        attack_samples = int(attack * n)
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

        decay_samples = int(decay * n)
        sustain_level = sustain
        if decay_samples > 0:
            decay_end = min(attack_samples + decay_samples, n)
            envelope[attack_samples:decay_end] = np.linspace(1, sustain_level, decay_end - attack_samples)

        sustain_start = attack_samples + decay_samples
        sustain_end = n - int(release * n)
        if sustain_end > sustain_start:
            envelope[sustain_start:sustain_end] = sustain_level

        release_samples = int(release * n)
        if release_samples > 0:
            envelope[-release_samples:] = np.linspace(sustain_level, 0, release_samples)

        return signal * envelope

    def beep(self, duration: float = 0.1, pitch_mult: float = 1.0) -> np.ndarray:
        """Generate clean beep"""
        freq = 1000 * pitch_mult
        t = np.linspace(0, duration, int(self.params.sample_rate * duration))
        signal = np.sin(2 * np.pi * freq * t)
        return self._apply_envelope(signal, attack=0.01, decay=0.05, sustain=0.8, release=0.14)

    def boop(self, duration: float = 0.12, pitch_mult: float = 1.0) -> np.ndarray:
        """Generate soft low boop"""
        freq = 300 * pitch_mult
        t = np.linspace(0, duration, int(self.params.sample_rate * duration))
        signal = np.sin(2 * np.pi * freq * t)
        return self._apply_envelope(signal, attack=0.1, decay=0.2, sustain=0.6, release=0.1)

    def chirp(self, duration: float = 0.08, pitch_mult: float = 1.0) -> np.ndarray:
        """Generate rapid high chirp"""
        freq = 2500 * pitch_mult
        t = np.linspace(0, duration, int(self.params.sample_rate * duration))
        vibrato = 50 * np.sin(2 * np.pi * 20 * t)
        signal = np.sin(2 * np.pi * (freq + vibrato) * t)
        return self._apply_envelope(signal, attack=0.02, decay=0.3, sustain=0.5, release=0.18)

    def stutter(self, duration: float = 0.2, pitch_mult: float = 1.0) -> np.ndarray:
        """Generate rapid repeated beeps"""
        num_bursts = 3
        freq = 1500 * pitch_mult
        burst_dur = duration / (num_bursts * 1.8)

        segments = []
        for i in range(num_bursts):
            t = np.linspace(0, burst_dur, int(self.params.sample_rate * burst_dur))
            burst = np.sin(2 * np.pi * freq * t)
            burst = self._apply_envelope(burst, attack=0.1, decay=0.2, sustain=0.6, release=0.1)
            segments.append(burst)
            if i < num_bursts - 1:
                gap = np.zeros(int(burst_dur * 0.5 * self.params.sample_rate))
                segments.append(gap)

        return np.concatenate(segments)

    def warble(self, duration: float = 0.35, pitch_mult: float = 1.0) -> np.ndarray:
        """Generate wobbly frequency modulation"""
        base_freq = 900 * pitch_mult
        t = np.linspace(0, duration, int(self.params.sample_rate * duration))

        mod1 = 150 * np.sin(2 * np.pi * 8 * t)
        mod2 = 80 * np.sin(2 * np.pi * 13 * t)
        freq_mod = base_freq + mod1 + mod2
        signal = np.sin(2 * np.pi * freq_mod * t)

        return self._apply_envelope(signal, attack=0.1, decay=0.15, sustain=0.65, release=0.1)

    def buzz(self, duration: float = 0.2, pitch_mult: float = 1.0) -> np.ndarray:
        """Generate harsh buzzing square wave"""
        freq = 300 * pitch_mult
        t = np.linspace(0, duration, int(self.params.sample_rate * duration))

        signal = np.sign(np.sin(2 * np.pi * freq * t))
        signal += 0.5 * np.sign(np.sin(2 * np.pi * freq * 2 * t))

        return self._apply_envelope(signal, attack=0.05, decay=0.15, sustain=0.7, release=0.1)

    def ping(self, duration: float = 0.06, pitch_mult: float = 1.0) -> np.ndarray:
        """Generate sharp metallic ping"""
        freq = 4000 * pitch_mult
        t = np.linspace(0, duration, int(self.params.sample_rate * duration))

        signal = np.sin(2 * np.pi * freq * t)
        signal += 0.4 * np.sin(2 * np.pi * freq * 1.5 * t)

        return self._apply_envelope(signal, attack=0.01, decay=0.2, sustain=0.4, release=0.39)

    def blip(self, duration: float = 0.03, pitch_mult: float = 1.0) -> np.ndarray:
        """Generate ultra-short beep"""
        freq = 3000 * pitch_mult
        t = np.linspace(0, duration, int(self.params.sample_rate * duration))
        signal = np.sin(2 * np.pi * freq * t)
        return self._apply_envelope(signal, attack=0.05, decay=0.3, sustain=0.5, release=0.15)

    def slide_down(self, duration: float = 0.4, pitch_mult: float = 1.0) -> np.ndarray:
        """Generate descending frequency slide"""
        f_start = 2000 * pitch_mult
        f_end = 600 * pitch_mult

        t = np.linspace(0, duration, int(self.params.sample_rate * duration))
        freq = np.linspace(f_start, f_end, len(t))
        phase = np.cumsum(freq) * 2 * np.pi / self.params.sample_rate

        signal = np.sin(phase)
        return self._apply_envelope(signal, attack=0.05, decay=0.1, sustain=0.7, release=0.15)

    def chord(self, duration: float = 0.3, pitch_mult: float = 1.0) -> np.ndarray:
        """Generate harmonic chord"""
        root_freq = 600 * pitch_mult
        t = np.linspace(0, duration, int(self.params.sample_rate * duration))

        signal = np.sin(2 * np.pi * root_freq * t)
        signal += 0.7 * np.sin(2 * np.pi * root_freq * 1.26 * t)  # Major third
        signal += 0.5 * np.sin(2 * np.pi * root_freq * 1.5 * t)   # Fifth

        return self._apply_envelope(signal, attack=0.05, decay=0.15, sustain=0.7, release=0.1)

    def tremolo(self, duration: float = 0.35, pitch_mult: float = 1.0) -> np.ndarray:
        """Generate amplitude-modulated tone"""
        freq = 1200 * pitch_mult
        tremolo_rate = 8  # Hz
        tremolo_depth = 0.6

        t = np.linspace(0, duration, int(self.params.sample_rate * duration))
        signal = np.sin(2 * np.pi * freq * t)

        tremolo_envelope = 1 - tremolo_depth * (0.5 + 0.5 * np.sin(2 * np.pi * tremolo_rate * t))
        signal = signal * tremolo_envelope

        return self._apply_envelope(signal, attack=0.1, decay=0.15, sustain=0.65, release=0.1)

    def sweep_up_down(self, duration: float = 0.25, pitch_mult: float = 1.0) -> np.ndarray:
        """Generate frequency rise then fall"""
        f_start = 1000 * pitch_mult
        f_peak = 2500 * pitch_mult
        f_end = 1100 * pitch_mult

        t = np.linspace(0, duration, int(self.params.sample_rate * duration))
        half = len(t) // 2

        freq_up = np.linspace(f_start, f_peak, half)
        freq_down = np.linspace(f_peak, f_end, len(t) - half)
        freq = np.concatenate([freq_up, freq_down])

        phase = np.cumsum(freq) * 2 * np.pi / self.params.sample_rate
        signal = np.sin(phase)

        return self._apply_envelope(signal, attack=0.05, decay=0.1, sustain=0.7, release=0.15)

    def _generate_sound(self, sound_name: str, duration: float, pitch_mult: float) -> np.ndarray:
        """Generate a specific sound by name"""
        sound_map = {
            'beep': lambda: self.beep(duration, pitch_mult),
            'boop': lambda: self.boop(duration, pitch_mult),
            'chirp': lambda: self.chirp(duration, pitch_mult),
            'stutter': lambda: self.stutter(duration, pitch_mult),
            'warble': lambda: self.warble(duration, pitch_mult),
            'buzz': lambda: self.buzz(duration, pitch_mult),
            'ping': lambda: self.ping(duration, pitch_mult),
            'blip': lambda: self.blip(duration, pitch_mult),
            'slide_down': lambda: self.slide_down(duration, pitch_mult),
            'chord': lambda: self.chord(duration, pitch_mult),
            'tremolo': lambda: self.tremolo(duration, pitch_mult),
            'sweep_up_down': lambda: self.sweep_up_down(duration, pitch_mult),
        }

        return sound_map.get(sound_name, lambda: self.beep(duration, pitch_mult))()

    def speak_sentence(self, sentence: str, emotion: str = 'neutral',
                       intensity: float = 1.0) -> np.ndarray:
        """
        Generate R2D2 speech for a sentence using word vocabulary.

        Args:
            sentence: Input sentence
            emotion: One of: happy, sad, angry, excited, curious, neutral,
                    confused, lazy, afraid, naughty
            intensity: Volume level (0.0-2.0)

        Returns:
            Audio samples as numpy float32 array
        """
        # Get emotion modulation parameters
        pitch_mult = self.EMOTION_PITCH.get(emotion, 1.0)
        speed_mult = self.EMOTION_SPEED.get(emotion, 1.0)

        # Split sentence into words
        words = sentence.lower().split()

        audio_segments = []

        for word_idx, word in enumerate(words):
            # Clean word (remove punctuation)
            word_clean = ''.join(c for c in word if c.isalnum())

            if not word_clean:
                continue

            # Get sequence length for this word
            seq_length = self.get_word_length(word_clean)

            # Generate sounds based on emotion preferences
            for _ in range(seq_length):
                # Select sound based on emotion
                sound_name = self._select_sound_for_emotion(emotion)

                # Base duration modified by speed
                base_duration = 0.12
                duration = base_duration / speed_mult

                # Generate sound with emotion modulation
                sound = self._generate_sound(sound_name, duration, pitch_mult)
                audio_segments.append(sound)

                # Small gap between sounds in same word
                gap_samples = int(0.05 * self.params.sample_rate / speed_mult)
                audio_segments.append(np.zeros(gap_samples))

            # Larger gap between words
            if word_idx < len(words) - 1:
                word_gap = int(0.15 * self.params.sample_rate / speed_mult)
                audio_segments.append(np.zeros(word_gap))

        if len(audio_segments) == 0:
            return np.zeros(int(0.1 * self.params.sample_rate), dtype=np.float32)

        # Concatenate all segments
        audio = np.concatenate(audio_segments)

        # Apply intensity
        audio = audio * min(intensity, 2.0)

        # Normalize
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val * self.params.amplitude

        return audio.astype(np.float32)

    def play_sentence(self, sentence: str, emotion: str = 'neutral',
                     intensity: float = 1.0) -> None:
        """Generate and play sentence"""
        try:
            import sounddevice as sd
            audio = self.speak_sentence(sentence, emotion, intensity)
            sd.play(audio, self.params.sample_rate)
            sd.wait()
        except ImportError:
            print("sounddevice not installed. Install with: pip install sounddevice")

    def save_sentence(self, sentence: str, filepath: str,
                     emotion: str = 'neutral', intensity: float = 1.0) -> None:
        """Generate and save sentence to WAV file"""
        import wave

        audio = self.speak_sentence(sentence, emotion, intensity)
        audio_int16 = (audio * 32767).astype(np.int16)

        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.params.sample_rate)
            wf.writeframes(audio_int16.tobytes())

        print(f"Saved sentence to {filepath}")


# Convenience functions
def speak_sentence(sentence: str, emotion: str = 'neutral',
                  intensity: float = 1.0) -> np.ndarray:
    """Quick generation without instantiating class"""
    voice = R2D2WordVocabulary()
    return voice.speak_sentence(sentence, emotion, intensity)


def play_sentence(sentence: str, emotion: str = 'neutral',
                 intensity: float = 1.0) -> None:
    """Quick playback without instantiating class"""
    voice = R2D2WordVocabulary()
    voice.play_sentence(sentence, emotion, intensity)
