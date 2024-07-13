import hashlib
import logging
from collections import Counter

from dahuffman import HuffmanCodec
from dahuffman.codetableio import json_save, pickle_save
from train.train_utils import CODECS, download

_log = logging.getLogger()


def main():
    logging.basicConfig(level=logging.INFO)

    # XML data sets from https://www.data.gov/
    urls = [
        "https://data.cityofnewyork.us/api/views/kku6-nxdu/rows.xml",
        "https://data.cdc.gov/api/views/bi63-dtpu/rows.xml",
        "https://data.cdc.gov/api/views/cjae-szjv/rows.xml",
        "https://data.cityofnewyork.us/api/views/25th-nujf/rows.xml",
        "https://data.ct.gov/api/views/kbxi-4ia7/rows.xml",
        "https://data.cityofchicago.org/api/views/pfsx-4n4m/rows.xml",
        "https://data.cdc.gov/api/views/6vp6-wxuq/rows.xml",
        "https://www.sba.gov/sites/default/files/data.xml",
        "https://data.cdc.gov/api/views/e6fc-ccez/rows.xml",
        "https://data.cityofnewyork.us/api/views/jb7j-dtam/rows.xml",
        "https://data.cityofnewyork.us/api/views/zt9s-n5aj/rows.xml",
        "https://gisdata.nd.gov/Metadata/ISO/xml/metadata_Roads_MileMarkers.xml",
        "https://data.cityofchicago.org/api/views/kn9c-c2s2/rows.xml",
        "https://data.cityofnewyork.us/api/views/5t4n-d72c/rows.xml",
        "https://data.cdc.gov/api/views/6rkc-nb2q/rows.xml",
        "https://gisdata.nd.gov/Metadata/ISO/xml/metadata_Airports.xml",
        "https://data.sfgov.org/api/views/j4sj-j2nf/rows.xml",
        "https://data.kingcounty.gov/api/views/gmen-63jm/rows.xml",
        "https://data.mo.gov/api/views/vpge-tj3s/rows.xml",
    ]

    _log.info("Building frequency tables")
    frequencies = Counter()
    for url in urls:
        path = download(
            url, "xml-data/" + hashlib.md5(url.encode("utf-8")).hexdigest() + ".xml"
        )
        with path.open("r") as f:
            # Only take first N bytes.
            # Large files probably have a lot of structural repetition, which skews the frequencies
            raw = f.read(100000)
        frequencies.update(raw)

    # TODO add more metadata
    _log.info(f"Frequencies raw {len(frequencies)}: {frequencies}")
    codec = HuffmanCodec.from_frequencies(frequencies)
    pickle_save(
        codec=codec, path=CODECS / "xml.pickle", metadata={"frequencies": frequencies}
    )
    json_save(
        codec=codec, path=CODECS / "xml.json", metadata={"frequencies": frequencies}
    )


if __name__ == "__main__":
    main()
