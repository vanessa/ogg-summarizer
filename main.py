from pydub import AudioSegment
import speech_recognition as sr
from openai import OpenAI
import os
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

console = Console()
client = OpenAI()

SYSTEM_PROMPT = """
You are a helpful assistant that summarizes transcriptions.
- Separate the important topics into sections.
- List all actions needed at the end of the summary.
- Respond in Brazilian Portuguese.
- Format the response as Markdown.
- If there are no actions needed, respond with 'No actions needed.'
- Do not add any other text than the ones specified above.
"""


def get_audio_files_paths():
    paths = []
    for file in os.listdir(os.path.join(os.path.dirname(__file__), "audios")):
        if file.endswith(".ogg"):
            paths.append(os.path.join(os.path.dirname(__file__), "audios", file))
    result = sorted(paths)
    console.log(f"Found [bold]{len(result)}[/bold] audio files.")
    console.log("Paths:")
    for path in result:
        console.log(f"  - [bold]{path}[/bold]")
    prompt = Prompt.ask("Do you want to continue?")
    if prompt != "y":
        console.log("Exiting...")
        exit()
    return result


def convert_audios_to_wav(paths: list[str]):
    # Check if there's a wav file in the converted folder
    converted_folder = os.path.join(os.path.dirname(__file__), "converted")
    if not os.path.exists(converted_folder):
        os.makedirs(converted_folder)

    output_paths = []

    for audio_file in paths:
        audio_file_name = audio_file.split("/")[-1]
        wav_file_name = audio_file_name.replace(".ogg", ".wav")
        output_path = os.path.join(converted_folder, wav_file_name)
        output_paths.append(output_path)

        # If wav file already exists with the same name, skip
        if os.path.exists(output_path):
            console.log(
                f"Wav file already exists. Skipping {audio_file_name}...",
                style="bold yellow",
            )
            continue

        audio = AudioSegment.from_file(audio_file)
        audio.export(output_path, format="wav")
        console.log(f"Converted {audio_file_name} to wav...")

    return output_paths


def transcribe_audios(paths: list[str]):
    # Check if there's a transcription file in the cache folder
    transcription_path = os.path.join(
        os.path.dirname(__file__), "cache/transcription.txt"
    )

    if os.path.exists(transcription_path):
        with open(transcription_path, "r") as f:
            transcription = f.read()
        console.log("Transcription already exists. Loading from cache...")
        return transcription

    recognizer = sr.Recognizer()
    transcription = ""

    for path in paths:
        filename = path.split("/")[-1]
        console.log(f"Transcribing [bold]{filename}[/bold]...")
        with sr.AudioFile(path) as source:
            audio = recognizer.record(source)
            transcription += recognizer.recognize_google(audio, language="pt-BR")  # type: ignore
        console.log(f"Finished transcribing [bold]{filename}[/bold]...")

    # Create the cache folder if it doesn't exist
    cache_folder = os.path.join(os.path.dirname(__file__), "cache")
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)

    with open(transcription_path, "w") as f:
        console.log("Writing transcription to cache...")
        f.write(transcription)

    return transcription


def summarize_transcriptions(transcription: str):
    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            {"role": "user", "content": transcription},
        ],
    )
    return response.output_text


def main():
    audio_files_paths = get_audio_files_paths()
    output_paths = convert_audios_to_wav(audio_files_paths)
    transcription = transcribe_audios(output_paths)
    summary = summarize_transcriptions(transcription)

    console.log(Markdown(summary))


if __name__ == "__main__":
    main()
