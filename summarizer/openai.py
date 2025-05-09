from openai import OpenAI
from rich.console import Console

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
