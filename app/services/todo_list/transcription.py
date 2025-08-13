import os
import openai

class VoiceTranscriber:
    def __init__(self, openai_api_key=None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        openai.api_key = self.openai_api_key

    def transcribe(self, audio_file_path):
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not provided.")
        # Uses OpenAI Whisper API. You can replace with your custom logic.
        with open(audio_file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe(
                file=audio_file, 
                model="whisper-1"
            )
        return transcript["text"]
