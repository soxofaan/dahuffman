import hashlib
import json
import logging
from collections import Counter

from dahuffman import HuffmanCodec
from train.train_utils import download, CODECS

_log = logging.getLogger()


def main():
    logging.basicConfig(level=logging.INFO)

    # JSON data sets from https://www.data.gov/
    urls = [
        "https://data.cityofnewyork.us/api/views/kku6-nxdu/rows.json",
        "https://data.cdc.gov/api/views/bi63-dtpu/rows.json",
        "https://data.cdc.gov/api/views/cjae-szjv/rows.json",
        "https://data.cityofnewyork.us/api/views/25th-nujf/rows.json",
        "https://data.ct.gov/api/views/kbxi-4ia7/rows.json",
        "https://data.cityofchicago.org/api/views/pfsx-4n4m/rows.json",
        "https://www.chapelhillopendata.org/api/v2/catalog/datasets/bicycle-crash-data-chapel-hill-region/exports/json",
        "https://data.cdc.gov/api/views/6vp6-wxuq/rows.json",
        "https://www.sba.gov/sites/default/files/data.json",
        "https://data.cdc.gov/api/views/e6fc-ccez/rows.json",
        "https://data.cityofnewyork.us/api/views/jb7j-dtam/rows.json",
        "https://data.cityofnewyork.us/api/views/zt9s-n5aj/rows.json",
    ]

    _log.info('Building frequency tables')
    frequencies_raw = Counter()
    frequencies_compact = Counter()
    for url in urls:
        path = download(url, 'json-' + hashlib.md5(url.encode('utf-8')).hexdigest() + '.json')
        with path.open('r') as f:
            raw = f.read()
        frequencies_raw.update(raw)

        # Parse and re-encode to compact JSON
        compact = json.dumps(json.loads(raw), separators=(',', ':'))
        frequencies_compact.update(compact)

    # TODO add more metadata
    _log.info(f'Frequencies raw {len(frequencies_raw)}: {frequencies_raw}')
    codec = HuffmanCodec.from_frequencies(frequencies_raw)
    codec.save(CODECS / "json.pickle", metadata={"frequencies": frequencies_raw})

    _log.info(f'Frequencies compact {len(frequencies_compact)}: {frequencies_compact}')
    codec = HuffmanCodec.from_frequencies(frequencies_compact)
    codec.save(CODECS / "json-compact.pickle", metadata={"frequencies": frequencies_compact})


if __name__ == '__main__':
    main()
