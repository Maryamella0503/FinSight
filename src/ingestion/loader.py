import os
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

SEC_USER_AGENT = os.getenv("SEC_USER_AGENT")

if not SEC_USER_AGENT:
    raise ValueError(
        "SEC_USER_AGENT is not configured. "
        "Add it to your .env file."
    )


def download_filing(url: str, filename: str) -> Path:
    """
    Download an SEC filing and save it to data/raw/.
    """

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_path = RAW_DATA_DIR / filename

    headers = {
        "User-Agent": SEC_USER_AGENT,
        "Accept-Encoding": "gzip, deflate",
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    output_path.write_bytes(response.content)

    return output_path