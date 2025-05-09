import assemblyai
from summarizer.config import config

assemblyai.settings.api_key = config.ASSEMBLYAI_API_KEY
assemblyai_config = assemblyai.TranscriptionConfig(
    speech_model=assemblyai.SpeechModel.best,
    entity_detection=True,
    speaker_labels=True,
    language_code="pt",
)


def get_assemblyai_audio_transcription(audio_file_path: str):
    transcriber = assemblyai.Transcriber(config=assemblyai_config)
    transcript = transcriber.transcribe(audio_file_path)

    if transcript.status == "error":
        raise RuntimeError(f"Error transcribing audio: {transcript.error}")

    return transcript
