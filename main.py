import logging
from src.mf import MoneyForward
from config.config import Config
from src.asset_processor import AssetProcessor


try:
    mf = MoneyForward(Config.MF_ID, Config.MF_PASS)
    mf.init(Config.SELENIUM_REMOTE_URL)
    mf.login()
    mf.reload()
    raw_asset = mf.portfolio()
    asset = AssetProcessor.add_timestamp(raw_asset)
    print(asset)
    logging.info(f"Asset data: {asset}")

except Exception as e:
    logging.error(f"Error occurred: {str(e)}", exc_info=True)

finally:
    try:
        mf.close()
    except Exception as e:
        logging.error(f"Error closing MoneyForward session: {str(e)}")



