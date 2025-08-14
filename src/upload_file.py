"""Upload a file(s) to an Optic's backing Axon."""

import argparse
import logging
import pprint
import os

import tqdm

import lib.log as log
import lib.optic as optic

LOG = logging.getLogger("upload_file")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="upload_sample", description=__doc__)
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug logging")
    parser.add_argument("-v", "--view", help="view to model files in")
    parser.add_argument("-m", "--model", action="store_true", help="model uploaded files in the Cortex")
    parser.add_argument("files", nargs="*", help="paths to file(s) to upload. if -m/--model is set, the basename of the file will be written to the Cortex.")
    
    args = parser.parse_args()
    if args.view and len(args.view) != 32:
        parser.error(f"{args.view=} is invalid, must be a GUID")
    
    return args

def handle_file(c: optic.Client, fn: str) -> str | None:
    """Upload a file. Returns the sha2 from server if successfully, otherwise None"""

    try:
        with open(fn, "rb") as f:
            content = f.read()

        r = c.axon_files_put(content)
        return str(r["sha256"])
    except:
        LOG.exception("failed to upload %s", fn)
        return None
    
def model_upload(c: optic.Client, v: str, fn: str, h: str):
    vars = {"fn": os.path.basename(fn), "h": f"sha256:{h}"}
    opts = {"vars": vars, "view": v}
    # - model the file:bytes node
    # - model the filename
    # - set the name on the file:bytes node only if one isn't already set
    # - run the fileparser in the background
    q = f"[(file:bytes=$h)] | [(file:filepath=($node, $fn))] | spin | file:bytes=$h -:name [:name=$fn] | spin | background {{ file:bytes=$h | fileparser.parse}}"
    
    for msg in c.cortex_storm(q, opts):
        if msg[0] == "err":
            LOG.error("failed to model upload: %s", pprint.pformat(msg[1]))

def main() -> int:
    args = parse_args()
    log.init(args.debug)

    client = optic.Client()

    LOG.info("starting file uploads")
    hashes: dict[str, str] = {}
    for fn in tqdm.tqdm(args.files):
        if h := handle_file(client, fn):
            hashes[fn] = h
    LOG.info("successfully uploaded %d/%d files", len(hashes), len(args.files))
    LOG.info(pprint.pformat(hashes))

    if args.model:
        LOG.info("modeling successful uploads in the Cortex; fileparsing will be done asynchronously")
        if args.view:
            LOG.info("files will be modeled in view %s", args.view)
        for fn, h in tqdm.tqdm(hashes.items()):
            model_upload(client, args.view, fn, h)

    return 0

if __name__ == "__main__":
    main()