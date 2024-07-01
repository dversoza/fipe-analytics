import json
import logging
import sys

from providers.fipe.crawler import FipeCrawler
from tqdm.contrib.logging import logging_redirect_tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s [%(levelname)s] %(message)s",
)


def main():
    _order = "ASC"
    if len(sys.argv) > 1:
        _order = sys.argv[1].upper().strip()

    checkpoint_file = f"{_order.lower()}_checkpoint.json"

    try:
        with open(checkpoint_file, "r") as f:
            checkpoint = json.load(f)
    except FileNotFoundError:
        checkpoint = {}

    crawler = FipeCrawler(order=_order, checkpoint=checkpoint)

    with logging_redirect_tqdm():
        try:
            crawler.populate_reference_tables(vehicle_type_id=1)
        except KeyboardInterrupt:
            logging.error("Process interrupted by the user")
            checkpoint = crawler.get_checkpoint()
            with open(checkpoint_file, "w") as f:
                json.dump(checkpoint, f)


if __name__ == "__main__":
    main()
