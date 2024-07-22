import logging
from pathlib import Path

import requests

DOWNLOADS = Path(__file__).parent / "data"
CODECS = Path(__file__).parent / "codecs"

_log = logging.getLogger()


def download(url: str, path: str) -> Path:
    path = DOWNLOADS / path
    if not path.exists():
        path.parent.mkdir(parents=True, exists_ok=True)
        _log.info(f"Downloading {url}")
        with requests.get(url) as r:
            r.raise_for_status()
            with path.open("wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)
        _log.info(f"Downloaded to {path}")
    else:
        _log.info(f"{path} already exists. (Not downloading from {url} again)")
    return path
