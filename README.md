# ogg-summarizer

A simple script to automatically transcribe and summarize .ogg audio files (the format most commonly used for WhatsApp voice messages).

## Prerequisites

1. `OPENAI_API_KEY` set in your environment variables
1. [mise](https://mise.jdx.dev/getting-started.html) (optional, but recommended)

If you don't have mise installed:
1. Python 3.13+
1. [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Quickstart

1. Clone the repository, cd into it
1. Run `mise trust` and `mise install`
1. Install dependencies with `uv sync`
1. Copy the .ogg files to the `audio` folder
1. Run the script with `uv run main.py`

## Usage

```bash
python -m summarizer.main [--use-assemblyai] [--sort]
```

