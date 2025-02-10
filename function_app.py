import logging
import azure.functions as func
from mf import MoneyForward
from config import Config
from asset_processor import AssetProcessor
app = func.FunctionApp()

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def timer_trigger(myTimer: func.TimerRequest) -> None:
    mf = MoneyForward(Config.MF_ID, Config.MF_PASS)
    try:
        mf.init()
        mf.login()
        raw_asset = mf.portfolio()
    finally:
        mf.close()

        asset = AssetProcessor.add_timestamp(raw_asset)
        print("asset:",asset)
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')