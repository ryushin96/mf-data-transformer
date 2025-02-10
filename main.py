from mf import MoneyForward
from config import Config
from asset_processor import AssetProcessor

mf = MoneyForward(Config.MF_ID, Config.MF_PASS)
try:
    mf.init()
    mf.login()
    raw_asset = mf.portfolio()
finally:
    mf.close()

    asset = AssetProcessor.add_timestamp(raw_asset)
    print("asset:",asset)