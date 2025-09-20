"""Download a file(s) from an Optic's backing Axon."""

import argparse
import logging
from typing import Any

import tqdm

import lib.log as log
import lib.optic as optic

LOG = logging.getLogger("download_file")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="download_sample", description=__doc__)
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug logging")
    parser.add_argument("-v", "--view", help="view to execute Storm query in")

    mg1 = parser.add_mutually_exclusive_group(required=True)
    mg1.add_argument("hashes", nargs="+", help="SHA256 hashes to download")
    mg1.add_argument("-q", "--query", help="Storm query to execute - returned file:bytes nodes with :sha256 set will be downloaded")

    args = parser.parse_args()
    for h in args.hashes:
        if len(h) != 64:
            parser.error(f"{h} isn't a sha256")
    
    if args.view and len(args.view) != 32:
        parser.error(f"{args.view=} is invalid, must be a GUID")
    
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

def handle_hashes(c: optic.Client, hashes: list[str]):
    if (l := len(hashes)) > 1:
        success = 0
        for h in tqdm.tqdm(hashes):
            if process_hash(c, h):
                success += 1
        LOG.info("successfully downloaded %d/%d files", success, l)
    else:
        h = hashes[0]
        if process_hash(c, h):
            LOG.info("successfully downloaded %s", h)

def get_hashes_via_storm(c: optic.Client, q: str, v: str | None) -> list[str]:
    opts: dict[str, Any] = {
        "readonly": True
    }
    if v:
        opts["view"] = v

    msgs = c.cortex_storm(q, opts)

    ret = []
    for m  in msgs:
        if m[0] != "node":
            continue
        n = m[1]
        if n[0][0] != "file:bytes":
            continue
        props = n[1].get("props", {})
        if h := props.get("sha256"):
            ret.append(h)
    return ret

def main() -> int:
    args = parse_args()
    log.init(args.debug)

    client = optic.Client()

    if args.hashes:
        hashes = args.hashes
    else:
        hashes = get_hashes_via_storm(client, args.query, args.view)
        LOG.info("got %d SHA256 hashes via storm query: %s", len(hashes), args.query)
    
    if len(hashes) > 0:
        handle_hashes(client, hashes)

    return 0

if __name__ == "__main__":
    main()