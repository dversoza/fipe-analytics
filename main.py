import logging
import sys

from providers.fipe.crawler import FipeCrawler
from tqdm.contrib.logging import logging_redirect_tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s [%(levelname)s] %(message)s",
)


def main():
    args = sys.argv[1:]

    crawler = FipeCrawler()

    if len(args) == 0:
        with logging_redirect_tqdm():
            crawler.populate_old_reference_tables(year_lte=2002)

    elif len(args) == 1:
        crawler.populate_prices_for_year(args[0])

    else:
        logging.error("Invalid number of arguments")

        sys.exit(1)


if __name__ == "__main__":
    main()
