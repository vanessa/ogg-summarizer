from dotenv import load_dotenv
import os
from rich.console import Console

console = Console()

load_dotenv()


console.log("Loading config...")


class Config:
    ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


config = Config()
