# gemini_transcribe.py
from google.cloud import speech_v1p1beta1 as speech
import os
import io

def transcribe_audio_google_cloud(audio_bytes, language_code="en-US", credentials_json=None):
    """
    audio_bytes: raw bytes of the uploaded file
    If you have a service account JSON, set GOOGLE_APPLICATION_CREDENTIALS env var to its path,
    or pass credentials_json path and set env var here.
    """
    if credentials_json:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_json

    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=audio_bytes)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
        sample_rate_hertz=16000,
        language_code=language_code,
        enable_automatic_punctuation=True,
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result(timeout=90)
    transcripts = []
    for result in response.results:
        transcripts.append(result.alternatives[0].transcript)
    return " ".join(transcripts)
