"""
This module integrates speech recognition with conversational AI to create
an interactive voice-based system. It uses the Vosk library for speech-to-text,
a custom Model class for generating responses, and text-to-speech synthesis for
auditory feedback.

Workflow:
1. The user speaks into the microphone.
2. The `SpeechInputManager` processes the audio, converting it to text using Vosk.
3. Once speech is finalized, the text is passed to the `on_speech_create` callback.
4. The AI model (`Model`) generates a response, which is synthesized back into audio for playback.
"""

import os
import time
from dotenv import load_dotenv

from speech import SpeechInputManager
from base import Model


load_dotenv()


def on_speech_start():
    """Callback function called when user starts speaking."""

    with synth.synth_process_lock:
        if synth.synth_playback_process and synth.synth_playback_process.poll() is None:
            synth.synth_playback_process.terminate()
            synth.synth_playback_process = None

            if os.path.exists("response.wav"):
                os.remove("response.wav")


model = Model()
synth = SpeechInputManager(
    on_speech_start=on_speech_start,
    on_speech_create=lambda text=None: (
        print(f"\n me - '{text}'"),
        (response := model.ask(text=text)),
        print(f"\n llm - '{response}'"),
        synth.synthesize(response),
    ),
)

if __name__ == "__main__":
    synth.run()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        synth.stop()

        with synth.synth_process_lock:
            if (
                synth.synth_playback_process
                and synth.synth_playback_process.poll() is None
            ):
                synth.synth_playback_process.terminate()
            if os.path.exists("response.wav"):
                os.remove("response.wav")
