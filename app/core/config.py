import os
from dotenv import load_dotenv

load_dotenv()

TMP_DIR = os.getenv("TMP_DIR", "")

if not TMP_DIR:
    raise ValueError("CRITICAL ERROR: TMP_DIR is not defined in the .env file")