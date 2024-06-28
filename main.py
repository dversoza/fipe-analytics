import json
import logging

from providers.fipe.crawler import FipeCrawler
from tqdm.contrib.logging import logging_redirect_tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s [%(levelname)s] %(message)s",
)


def main():
    try:
        with open("checkpoint.json", "r") as f:
            checkpoint = json.load(f)
    except FileNotFoundError:
        checkpoint = {}

    crawler = FipeCrawler(checkpoint)

    with logging_redirect_tqdm():
        try:
            crawler.populate_reference_tables_in_ascending_order(year_lte=2025)
        except KeyboardInterrupt:
            logging.error("Process interrupted by the user")
            checkpoint = crawler.get_checkpoint()
            with open("checkpoint.json", "w") as f:
                json.dump(checkpoint, f)


if __name__ == "__main__":
    main()
