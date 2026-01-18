#!/usr/bin/env python3
"""
VAD-based Audio Recorder
Records until user stops speaking
"""

import webrtcvad
import sounddevice as sd
import numpy as np
import collections


class VADRecorder:
    """
    Voice Activity Detection-based recorder
    Records audio until user stops speaking
    """

    def __init__(self, sample_rate=16000, aggressiveness=2,
                 speech_frames_threshold=5, min_recording_duration=1.0):
        """
        Initialize VAD recorder

        Args:
            sample_rate: Audio sample rate (must be 8000, 16000, 32000, or 48000)
            aggressiveness: VAD aggressiveness (0-3, higher = more aggressive)
            speech_frames_threshold: Frames of consecutive speech needed to start recording (higher = less sensitive)
            min_recording_duration: Minimum recording duration in seconds (higher = filters short noises)
        """
        self.sample_rate = sample_rate
        self.vad = webrtcvad.Vad(aggressiveness)

        # Frame duration in ms (10, 20, or 30)
        self.frame_duration_ms = 30
        self.frame_size = int(sample_rate * self.frame_duration_ms / 1000)

        # Voice activity parameters
        self.silence_frames_threshold = 30  # ~1 second of silence to stop
        self.speech_frames_threshold = speech_frames_threshold  # Require N frames of speech to start
        self.min_recording_duration = min_recording_duration   # Minimum recording duration

    def is_speech(self, audio_frame):
        """
        Check if audio frame contains speech

        Args:
            audio_frame: Audio data as int16 numpy array

        Returns:
            bool: True if speech detected
        """
        # Convert to bytes
        audio_bytes = audio_frame.tobytes()

        # VAD requires exactly frame_size samples
        if len(audio_bytes) != self.frame_size * 2:  # *2 because int16 = 2 bytes
            return False

        try:
            return self.vad.is_speech(audio_bytes, self.sample_rate)
        except Exception:
            return False

    def record_with_vad(self, max_duration=30, pre_speech_buffer=0.5):
        """
        Record audio with VAD - stops when user stops speaking

        Args:
            max_duration: Maximum recording duration in seconds
            pre_speech_buffer: Seconds of audio to keep before speech detected

        Returns:
            numpy array of audio data (float32, -1.0 to 1.0)
        """
        print("🎤 Listening... (speak now, will stop when you finish)")

        # Buffer to store audio frames
        all_frames = []
        pre_speech_frames = collections.deque(
            maxlen=int(pre_speech_buffer * self.sample_rate / self.frame_size)
        )

        # State tracking
        speech_started = False
        silence_frame_count = 0
        speech_frame_count = 0

        # Calculate max frames
        max_frames = int(max_duration * self.sample_rate / self.frame_size)
        frame_count = 0

        # Audio stream
        stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='int16',
            blocksize=self.frame_size
        )

        stream.start()

        try:
            while frame_count < max_frames:
                # Read frame
                audio_frame, overflowed = stream.read(self.frame_size)

                if overflowed:
                    print("⚠ Audio buffer overflow")

                # Flatten to 1D
                audio_frame = audio_frame.flatten()

                # Check for speech
                is_speech = self.is_speech(audio_frame)

                if not speech_started:
                    # Before speech starts, keep in pre-speech buffer
                    pre_speech_frames.append(audio_frame)

                    if is_speech:
                        speech_frame_count += 1
                        if speech_frame_count >= self.speech_frames_threshold:
                            # Speech detected! Add pre-speech buffer
                            print("✓ Speech detected")
                            speech_started = True
                            all_frames.extend(list(pre_speech_frames))
                    else:
                        speech_frame_count = 0

                else:
                    # Speech has started
                    all_frames.append(audio_frame)

                    if is_speech:
                        # Reset silence counter
                        silence_frame_count = 0
                    else:
                        # Count silence frames
                        silence_frame_count += 1

                        # Check if enough silence to stop
                        if silence_frame_count >= self.silence_frames_threshold:
                            print("✓ Silence detected, stopping recording")
                            break

                frame_count += 1

        finally:
            stream.stop()
            stream.close()

        if not speech_started:
            print("⚠ No speech detected")
            return np.array([], dtype=np.float32)

        # Combine all frames
        if not all_frames:
            return np.array([], dtype=np.float32)

        audio = np.concatenate(all_frames)

        # Convert to float32 (-1.0 to 1.0)
        audio_float = audio.astype(np.float32) / 32768.0

        duration = len(audio_float) / self.sample_rate

        # Check minimum duration
        if duration < self.min_recording_duration:
            print(f"⚠ Recording too short ({duration:.1f}s), ignoring")
            return np.array([], dtype=np.float32)

        print(f"✓ Recording complete: {duration:.1f} seconds")

        return audio_float


# Demo
if __name__ == "__main__":
    print("=" * 60)
    print("VAD RECORDER DEMO")
    print("=" * 60)
    print()

    recorder = VADRecorder(sample_rate=16000, aggressiveness=2)

    print("This will record until you stop speaking.")
    print("Try saying a sentence and pause...")
    print()

    input("Press Enter to start recording...")

    audio = recorder.record_with_vad(max_duration=30)

    if len(audio) > 0:
        print(f"\nRecorded {len(audio)} samples ({len(audio)/16000:.2f} seconds)")
        print("Audio captured successfully!")
    else:
        print("\nNo audio captured")
