import logging
import sys

from db.old_create_db import create_db, create_db_connection
from providers.fipe.crawler import FipeCrawler
from tqdm.contrib.logging import logging_redirect_tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s [%(levelname)s] %(message)s",
)


def main():
    conn = create_db_connection()

    create_db(conn)

    args = sys.argv[1:]

    crawler = FipeCrawler(conn)

    if len(args) == 0:
        with logging_redirect_tqdm():
            for year in range(2024, 2000, -1):
                crawler.populate_prices_for_year(year)

    elif len(args) == 1:
        crawler.populate_prices_for_year(args[0])

    else:
        logging.error("Invalid number of arguments")

        sys.exit(1)

    conn.close()


if __name__ == "__main__":
    main()
