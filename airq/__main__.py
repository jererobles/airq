__version__ = "0.1.0"


import os
from dotenv import load_dotenv
from airq.app import App
from airq.api import Uhoo

load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


if __name__ == "__main__":
    app = App(Uhoo(USERNAME, PASSWORD))
    app.run()
