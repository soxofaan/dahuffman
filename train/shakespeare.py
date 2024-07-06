"""

Build codecs based on Shakespeare' work

"""

import logging
import re
from collections import Counter

from dahuffman import HuffmanCodec
from train.train_utils import CODECS, download

_log = logging.getLogger()


def main():
    logging.basicConfig(level=logging.INFO)
    # Shakespeare Complete Work from Project Gutenberg
    url = "http://www.gutenberg.org/files/100/100-0.txt"
    path = download(url, "shakespeare.txt")

    with path.open("r", encoding="utf-8-sig") as f:
        raw = f.read()

    _log.info("Building codec from raw data")
    frequencies = Counter(raw)
    _log.info(f"Frequencies {len(frequencies)}: {frequencies}")
    codec = HuffmanCodec.from_frequencies(frequencies)
    codec.save(CODECS / "shakespeare-raw.pickle", metadata={"frequencies": frequencies})

    _log.info("Doing white space clean up")
    clean = raw
    clean = re.sub(r"\s*\n+\s*", "\n", clean)
    clean = re.sub(r" +", " ", clean)
    frequencies = Counter(clean)
    _log.info(f"Frequencies {len(frequencies)}: {frequencies}")
    codec = HuffmanCodec.from_frequencies(frequencies)
    codec.save(CODECS / "shakespeare.pickle", metadata={"frequencies": frequencies})

    _log.info("Only handling lower case")
    lower = clean.lower()
    frequencies = Counter(lower)
    _log.info(f"Frequencies {len(frequencies)}: {frequencies}")
    codec = HuffmanCodec.from_frequencies(frequencies)
    codec.save(
        CODECS / "shakespeare-lower.pickle", metadata={"frequencies": frequencies}
    )


if __name__ == "__main__":
    main()
