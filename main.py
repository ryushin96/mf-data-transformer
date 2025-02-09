from logzero import logger
import logzero
import os

from mf import MoneyForward
from config import Config
from asset_processor import AssetProcessor

if "LOG_LEVEL" in os.environ:
    logzero.loglevel(int(os.environ["LOG_LEVEL"]))
mf = MoneyForward(Config.MF_ID, Config.MF_PASS)
try:
    mf.init()
    mf.login()
    raw_asset = mf.portfolio()
finally:
    mf.close()

    asset = AssetProcessor.add_timestamp(raw_asset)
    print("asset:",asset)