import logging

def init(debug: bool):
    """Initialize logging output in a CLI application."""

    logging.basicConfig(
        format="%(asctime)s [%(levelname)s:%(name)s] %(message)s",
        level=logging.DEBUG if debug else logging.INFO,
        datefmt="%Y/%m/%d %H:%M:%S",
        handlers=[
            logging.StreamHandler()
        ]
    )