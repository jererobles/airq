__version__ = "0.2.0"


import os
import logging
from dotenv import load_dotenv
from airq.app import App
from airq.api import Uhoo

logger = logging.getLogger(__name__)

load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


if __name__ == "__main__":
    logger.info("Starting AirQ v%s", __version__)
    app = App(Uhoo(USERNAME, PASSWORD))
    app.run()
    logger.info("Exiting AirQ v%s", __version__)
