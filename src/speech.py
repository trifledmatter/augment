"""
docstring
"""

import json
import os
import queue
import sys
import threading
import time
from typing import Any

import numpy
import sounddevice
import vosk


class SpeechInputManager:
    """
    Manages speech input from microphone using Vosk.
    """

    def __init__(
        self,
        model: str = "models/small",
        sample_rate: int = 16000,
        threshold: int = -30,
        silence_timeout: float = 1.0,
        on_speech_start=None,  # Start Event
        on_speech_create=None,  # Callback that fires when speech is finalized
        on_partial_create=None,  # Callback that fires when each word individually is finalized
    ) -> None:
        """
        Initializes the speech input manager.
        """
        assert not os.path.exists(model), (
            f"vosk - model was not unpacked at path src/{model}"
            "download a model from here -> https://alphacephei.com/vosk/models"
        )

        self.model = model
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.silence_timeout = silence_timeout

        self.on_speech_start = on_speech_start
        self.on_speech_create = on_speech_create
        self.on_partial_create = on_partial_create

        self.audio_queue = queue.Queue()

        self.running = False
        self.transcribing = False
        self.last_sound_time = 0

        self.service = vosk.Model(model)
        self.recognizer = vosk.KaldiRecognizer(model, sample_rate)

        self.service_stream = None
        self.service_thread = None

    def audio_callback(self, indata: bytes = None, status: Any = None) -> None:
        """
        Processes incoming audio and handles transcription triggers.
        """
        if status:
            print(f"speech - audio callback status: {status}", file=sys.stderr)

        data = bytes(indata)
        audio = numpy.frombuffer(data, dtype=numpy.int16)
        rms = numpy.sqrt(numpy.mean(audio.astype(numpy.float32) ** 2))
        decibels = 20 * numpy.log10(rms) if rms > 0 else -numpy.inf

        current_time = time.time()

        if decibels > self.threshold:
            self.last_sound_time = current_time

            if not self.transcribing:
                self.transcribing = True

                if self.on_speech_start:
                    self.on_speech_start()

            self.audio_queue.put(data)
        else:
            if (
                self.transcribing
                and (current_time - self.last_sound_time) > self.silence_timeout
            ):
                self.transcribing = False
                self.audio_queue.put(None)  # this'll signal the recognizer to reset

    def run(self) -> None:
        """
        Starts the speech input manager.
        """
        if self.running:
            return

        self.running = True
        self.service_stream = sounddevice.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=0,
            dtype="int16",
            channels=1,
            callback=self.audio_callback,
        )

        self.service_stream.start()

        self.service_thread = threading.Thread(target=self._process_audio_queue)
        self.service_thread.start()

    def stop(self) -> None:
        """
        Stops the speech input manager.
        """

        if not self.running:
            return

        self.running = False

        if self.service_stream is not None:
            self.service_stream.stop()
            self.service_stream.close()
        if self.service_thread is not None:
            self.service_thread.join()

    def _process_audio_queue(self):
        """
        Processes audio data from the queue.
        """
        while self.running:
            try:
                data = self.audio_queue.get(timeout=0.1)

                if data is None:
                    self.recognizer.Reset()
                    continue

                if self.transcribing:
                    if self.recognizer.AcceptWaveform(data):
                        result = self.recognizer.Result()
                        text = json.loads(result).get("text", "")
                        if text and self.on_speech_create:
                            self.on_speech_create(text)
                    else:
                        partial = self.recognizer.PartialResult()
                        text = json.loads(partial).get("partial", "")
                        if text and self.on_partial_create:
                            self.on_partial_create(text)
            except queue.Empty:
                continue
            except Exception:
                print("sim - an error occured in processing thread")
                break
