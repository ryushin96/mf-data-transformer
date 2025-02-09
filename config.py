# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MF_ID = os.getenv("MF_ID")
    MF_PASS = os.getenv("MF_PASS")