from logzero import logger
import logzero

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

import requests

import os, time, datetime
import imaplib, email, re, pyotp, pytz

MF_ID = "kuboken3398.trade@gmail.com"
MF_PASS = "AzureAssetApp"

class MoneyForward:
    def __init__(self) -> None:
        self.stock_price_cache: dict[str, float] = dict()

    def init(self):
        logger.info("selenium initializing...")
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=800x1000")
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-infobars")
        options.add_argument("--no-sandbox")
        options.add_argument("--hide-scrollbars")
        options.add_argument("--lang=ja-JP")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36")
        options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 5)
        self.driver.implicitly_wait(10)

    def login(self):
        self.driver.execute_script("window.open()")
        if not "MF_ID" in os.environ or not "MF_PASS" in os.environ:
            raise ValueError("env MF_ID and/or MF_PASS are not found.")
        mf_id = MF_ID #os.environ[""]
        mf_pass = MF_PASS #os.environ["MF_PASS"]

        # ログインページに移動
        self.driver.get("https://ssnb.x.moneyforward.com/users/sign_in")

        # ページロードを待機
        self.wait.until(ec.presence_of_all_elements_located)

        # 現在時刻を記録
        login_time = datetime.datetime.now(pytz.timezone("Asia/Tokyo"))

        # メールアドレス入力
        self.send_to_element('//input[@type="email"]', mf_id)

        # パスワード入力
        time.sleep(0.3)
        self.send_to_element('//input[@type="password"]', mf_pass)

        # ログインボタンをクリックする前に待機
        login_button = WebDriverWait(self.driver, 10).until(
            ec.element_to_be_clickable((By.XPATH, '//input[@id="login-btn-sumit"]'))
        )
        login_button.click()

        # ログイン後の待機
        self.wait.until(ec.presence_of_all_elements_located)


    def portfolio(self):
        self.driver.get("https://ssnb.x.moneyforward.com/bs/portfolio")
        self.wait.until(ec.presence_of_all_elements_located)
        #elements = self.driver.find_elements(by=By.XPATH, value='//*[@id="portfolio_det_eq"]/table/tbody/tr')
        elements = self.driver.find_elements(by=By.XPATH, value='//*[@id="portfolio_det_depo"]/section/table/tbody')
        print("element表示")
        print(elements)
        for i in range(len(elements)):
            tds = elements[i].find_elements(by=By.TAG_NAME, value="td")
            print("tds:", tds)
            name = tds[1].text
            no = tds[0].text
            print("no", no)
            print("name:", name)
            # if name[0:1] == "#":
            #     entry = name.split("-")
            #     stock_price = self.stock_price(entry[1])
            #     stock_count = int(entry[2])
            #     print(f"stock price:{stock_price}, stock_count: {stock_count}")
            #     logger.info(entry[0] + ": " + entry[1] + " is " + str(stock_price) + "USD (" + str(int(usdrate * stock_price)) + " JPY) x " + str(stock_count))
            #     img = tds[11].find_element(by=By.TAG_NAME, value="img")
            #     self.driver.execute_script("arguments[0].click();", img)
            #     det_value = tds[11].find_element(by=By.ID, value="user_asset_det_value")
            #     commit = tds[11].find_element(by=By.NAME, value="commit")
            #     time.sleep(1)
            #     self.send_to_element_direct(det_value, str(int(usdrate * stock_price) * stock_count))
            #     commit.click()
            #     time.sleep(1)
            #     logger.info(entry[0] + " is updated.")
            #     elements = self.driver.find_elements(by=By.XPATH, value='//*[@id="portfolio_det_eq"]/table/tbody/tr')  # avoid stale error


    def close(self):
        try:
            self.driver.close()
        except:
            logger.debug("Ignore exception (close)")
        try:
            self.driver.quit()
        except:
            logger.debug("Ignore exception (quit)")

    def send_to_element(self, xpath, keys):
        element = self.driver.find_element(by=By.XPATH, value=xpath)
        element.clear()
        logger.debug("[send_to_element] " + xpath)
        element.send_keys(keys)

    def send_to_element_direct(self, element, keys):
        element.clear()
        logger.debug("[send_to_element] " + element.get_attribute("id"))
        element.send_keys(keys)


if __name__ == "__main__":
    if "LOG_LEVEL" in os.environ:
        logzero.loglevel(int(os.environ["LOG_LEVEL"]))
    mf = MoneyForward()
    try:
        mf.init()
        mf.login()
        mf.portfolio()
    finally:
        mf.close()