import datetime

class AssetProcessor():
    @staticmethod
    def add_timestamp(raw_asset):
        time_now = datetime.datetime.now()
        time_str = time_now.strftime("%Y-%m-%d %H:%M:%S")
        raw_asset.update({"time": time_str})
        return raw_asset