# config.py
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

class Config:
    MF_ID = os.getenv("MF_ID")
    MF_PASS = os.getenv("MF_PASS")
    SELENIUM_REMOTE_URL = os.getenv("SELENIUM_REMOTE_URL")