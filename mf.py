from logzero import logger
import logzero

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


import time, datetime
import pytz


class MoneyForward:
    def __init__(self, mf_id, mf_pass) -> None:
        self.mf_id = mf_id
        self.mf_pass = mf_pass
        self.depo_keys = ["name", "balance", "institution"]
        self.eq_keys = ["code", "name", "owned_number", "get_value", "current_value", "valuation", "change_previousday", "valuation_profitloss", "valuation_profitloss_ratio", "institution"]
        self.mf_keys = ["name", "owned_number", "get_value", "current_value", "valuation", "change_previousday", "valuation_profitloss", "valuation_profitloss_ratio", "institution"]
        self.pns_keys = ["name", "get_value", "current_value", "valuation_profitloss", "valuation_profitloss_ratio", "acquisition_date"]
        self.po_keys = ["name", "kind", "point", "rate", "current_value", "institution"]

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
        mf_id = self.mf_id #os.environ[""]
        mf_pass = self.mf_pass #os.environ["MF_PASS"]

        # ログインページに移動
        self.driver.get("https://ssnb.x.moneyforward.com/users/sign_in")

        # ページロードを待機
        self.wait.until(ec.presence_of_all_elements_located)

        # 現在時刻を記録
        login_time = datetime.datetime.now(pytz.timezone("Asia/Tokyo"))

        # メールアドレス入力
        self.send_to_element('//input[@type="email"]', mf_id)

        # パスワード入力
        time.sleep(0.25)
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
        elements_depo = self.driver.find_elements(by=By.XPATH, value='//*[@id="portfolio_det_depo"]/section/table/tbody/tr')# 預貯金
        elements_eq = self.driver.find_elements(by=By.XPATH, value='//*[@id="portfolio_det_eq"]/table/tbody/tr')# 個別株
        elements_mf = self.driver.find_elements(by=By.XPATH, value='//*[@id="portfolio_det_mf"]/table/tbody/tr')# 投資信託
        elements_pns = self.driver.find_elements(by=By.XPATH, value='//*[@id="portfolio_det_pns"]/table/tbody/tr')# 年金
        elements_po = self.driver.find_elements(by=By.XPATH, value='//*[@id="portfolio_det_po"]/table/tbody/tr')# ポイント

        depo = self.format_table(elements_depo, self.depo_keys)
        eq = self.format_table(elements_eq, self.eq_keys)
        mf = self.format_table(elements_mf, self.mf_keys)
        pns = self.format_table(elements_pns, self.pns_keys)
        po = self.format_table(elements_po, self.po_keys)

        raw_asset = {
            "depo": depo,
            "eq": eq,
            "mf": mf,
            "pns": pns,
            "po": po
        }
        return raw_asset


    def format_table(self, elements, keys):
        element = {}
        for i in range(len(elements)):
            tds = elements[i].find_elements(by=By.TAG_NAME, value="td")
            name = tds[0].text
            if name not in element:
                element[name] = {} 

            for j in range(len(keys)):
                element[name][keys[j]] = tds[j].text
        return element
    
        

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

