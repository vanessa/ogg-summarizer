import tempfile
from pydub import AudioSegment
import speech_recognition as sr
from openai import OpenAI
import os
from rich.console import Console
from rich.prompt import Confirm
import shutil
from pathlib import Path

console = Console()
client = OpenAI()

SYSTEM_PROMPT = """
You are a helpful assistant that summarizes transcriptions.
- Separate the important topics into sections.
- List all actions needed at the end of the summary.
- Respond in Brazilian Portuguese.
- Format the response as Markdown, in a way that is easy to read, and copy and paste.
- If there are no actions needed, respond with 'No actions needed.'
- Do not add any other text than the ones specified above.
"""


def get_audio_files_paths(audios_dir: str):
    paths = []
    for file in os.listdir(audios_dir):
        if file.endswith(".ogg"):
            paths.append(os.path.join(audios_dir, file))
    result = sorted(paths)
    console.log(f"Found [bold]{len(result)}[/bold] audio files.")
    console.log("Paths:")
    for path in result:
        console.log(f"  - [bold]{path}[/bold]")
    prompt = Confirm.ask("Do you want to continue?", default=True)
    if not prompt:
        console.log("Exiting...")
        exit()
    return result


def convert_audios_to_wav(paths: list[str]):
    converted_folder = tempfile.mkdtemp()
    output_paths = []

    with console.status("Converting audios to wav") as status:
        for audio_file in paths:
            audio_file_name = audio_file.split("/")[-1]
            wav_file_name = audio_file_name.replace(".ogg", ".wav")
            output_path = os.path.join(converted_folder, wav_file_name)
            output_paths.append(output_path)
            audio = AudioSegment.from_file(audio_file)
            audio.export(output_path, format="wav")
            status.update(f"Converted {audio_file_name} to wav")

    return output_paths


def transcribe_audios(paths: list[str]):
    recognizer = sr.Recognizer()
    transcription = ""

    with console.status("Transcribing audios...") as status:
        for path in paths:
            filename = path.split("/")[-1]
            status.update(f"Transcribing [bold]{filename}[/bold]...")
            with sr.AudioFile(path) as source:
                audio = recognizer.record(source)
                transcription += recognizer.recognize_google(  # type: ignore
                    audio, language="pt-BR"
                )
        status.update("Finished transcribing audios")

    with tempfile.NamedTemporaryFile(delete=False) as f:
        console.log(f"Writing transcription to cache [bold]{f.name}[/bold]...")
        f.write(transcription.encode("utf-8"))
        f.flush()

    return transcription


def summarize_transcriptions(transcription: str):
    with console.status("Summarizing transcriptions") as status:
        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT.strip()},
                {"role": "user", "content": transcription},
            ],
        )
        status.update("Finished summarizing transcriptions")
    return response.output_text


def sort_and_rename_files(directory_path, file_extension="ogg"):
    """
    Sorts files by creation timestamp and renames them to 'Audio {timestamp}'.
    """
    # Get all files in the directory
    files = []
    directory = Path(directory_path)

    # Collect all files or only files with specific extension
    for file_path in directory.iterdir():
        if file_path.is_file():
            if (
                file_extension is None
                or file_path.suffix.lower() == file_extension.lower()
            ):
                files.append(file_path)

    # Sort files by creation time
    files.sort(key=lambda x: os.path.getctime(x))

    # Rename files based on their creation timestamp
    for i, file_path in enumerate(files):
        # Get creation timestamp
        c_time = os.path.getctime(file_path)

        # Format timestamp as string (unix timestamp)
        timestamp = int(c_time)

        # Preserve file extension
        extension = file_path.suffix

        # Create new filename
        new_name = f"Audio {timestamp}{extension}"
        new_path = directory / new_name

        # Ensure we don't overwrite existing files
        counter = 1
        while new_path.exists():
            new_name = f"Audio {timestamp}_{counter}{extension}"
            new_path = directory / new_name
            counter += 1

        # Rename file
        console.log(
            f"Renaming [bold]{file_path.name}[/bold] to [bold]{new_name}[/bold]"
        )
        shutil.move(str(file_path), str(new_path))


def main(sort: bool = False):
    console.log("Starting...")
    audios_dir = os.path.join(os.path.dirname(__file__), "audios")

    if sort:
        sort_and_rename_files(audios_dir)
    else:
        console.log("Skipping sort because --sort flag was not provided...")

    audio_files_paths = get_audio_files_paths(audios_dir)
    output_paths = convert_audios_to_wav(audio_files_paths)
    transcription = transcribe_audios(output_paths)
    summary = summarize_transcriptions(transcription)

    console.log(summary)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sort",
        action="store_true",
        help="Sort and rename files before processing",
    )
    args = parser.parse_args()

    main(args.sort)
