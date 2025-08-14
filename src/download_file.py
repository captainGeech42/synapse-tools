"""Download a file(s) from an Optic's backing Axon."""

import argparse
import logging

import tqdm

import lib.log as log
import lib.optic as optic

LOG = logging.getLogger("download_file")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="download_sample", description=__doc__)

    parser.add_argument("hashes", nargs="+", help="SHA256 hashes to download")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable verbose/debug logging")

    args = parser.parse_args()
    for h in args.hashes:
        if len(h) != 64:
            parser.error(f"{h} isn't a sha256")
    
    return args

def process_hash(c: optic.Client, h: str) -> bool:
    try:
        d = c.axon_files_by_sha256(h)
    except:
        logging.exception("failed to download %s", h)
        return False

    with open(h, "wb") as f:
        f.write(d)
    return True

def main() -> int:
    args = parse_args()
    log.init(args.verbose)

    client = optic.Client()

    if (l := len(args.hashes)) > 1:
        success = 0
        for h in tqdm.tqdm(args.hashes):
            if process_hash(client, h):
                success += 1
        LOG.info("successfully downloaded %d/%d files", success, l)
    else:
        h = args.hashes[0]
        if process_hash(client, h):
            LOG.info("successfully downloaded %s", h)

    return 0

if __name__ == "__main__":
    main()