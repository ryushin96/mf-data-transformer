from logzero import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
import time


class MoneyForward:
    def __init__(self, mf_id=None, mf_pass=None):
        self.mf_id = mf_id or os.getenv("MF_ID")
        self.mf_pass = mf_pass or os.getenv("MF_PASS")
        self.depo_keys = ["name", "balance", "institution"]
        self.eq_keys = ["code", "name", "owned_number", "get_value", "current_value", "valuation", "change_previousday", "valuation_profitloss", "valuation_profitloss_ratio", "institution"]
        self.mf_keys = ["name", "owned_number", "get_value", "current_value", "valuation", "change_previousday", "valuation_profitloss", "valuation_profitloss_ratio", "institution"]
        self.pns_keys = ["name", "get_value", "current_value", "valuation_profitloss", "valuation_profitloss_ratio", "acquisition_date"]
        self.po_keys = ["name", "kind", "point", "rate", "current_value", "institution"]
        self.driver = None
        self.wait = None

    def init(self, selenium_remote_url):
        """Initialize Selenium WebDriver."""
        logger.info("Initializing Selenium WebDriver...")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=800x1000")
        chrome_options.add_argument("--disable-application-cache")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--lang=ja-JP")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36")


        # Seleniumが立ち上がるまで待機（最大30秒）
        max_wait_time = 30
        for _ in range(max_wait_time):
            try:
                self.driver = webdriver.Remote(command_executor=selenium_remote_url, options=chrome_options)
                self.wait = WebDriverWait(self.driver, 10)
                self.driver.implicitly_wait(10)
                logger.info("Selenium WebDriver initialized.")
                break  # WebDriverが正常に初期化できたらループを抜ける
            except Exception as e:
                logger.warning(f"Selenium initialization failed: {e}")
                time.sleep(1)  # 1秒待機して再試行
        else:
            logger.error("Failed to initialize Selenium WebDriver after waiting for 30 seconds.")

    def login(self):
        """MoneyForwardのウェブサイトにログインする"""
        if not self.mf_id or not self.mf_pass:
            logger.error("MF_IDまたはMF_PASSが設定されていません。")
            return False

        self.driver.execute_script("window.open()")
        self.driver.get("https://ssnb.x.moneyforward.com/users/sign_in")
        
        self.wait.until(ec.presence_of_all_elements_located)
        self._send_to_element('//input[@type="email"]', self.mf_id)
        time.sleep(0.25)
        self._send_to_element('//input[@type="password"]', self.mf_pass)


        try:
            login_button = WebDriverWait(self.driver, 10).until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, "input[name='commit'][type='submit']"))
            )
            login_button.click()
        except Exception as e:
            logger.error(f"ログインボタンが見つからないか、クリックできません: {e}")
            return False

        self.wait.until(ec.presence_of_all_elements_located)
        logger.info("ログインに成功しました。")
        return True

    def wait_until_element_present(self, xpath, timeout):
        """XPathで指定された要素が現れるのを待つ"""
        try:
            self.wait.until(ec.presence_of_element_located((By.XPATH, xpath)))
        except Exception as e:
            logger.error(f"要素{xpath}の待機中にエラーが発生しました: {e}")

    def reload(self):
        """MoneyForwardのデータ更新"""
        self.driver.get("https://ssnb.x.moneyforward.com/accounts")
        # IDを持つ 'tr' 要素数取得
        rows = self.driver.find_elements(By.XPATH, "//tr[@id]")  
        # print(f"IDを持つ行の数: {len(rows)}")
        # 各行の「更新」ボタンをクリック
        for row in rows:
            row_id = row.get_attribute("id")
            try:
                # # 「更新」ボタンを検索（その `tr` 内で `input` を探す）
                # update_button = row.find_element(By.XPATH, ".//input[@type='submit' and contains(@class, 'ga-refresh-account-button')]")
                # 「更新」ボタンの XPath を作成（'tr' 内にある 'input'を探す）
                update_button_xpath = ".//input[@type='submit' and contains(@class, 'ga-refresh-account-button')]"
                self.wait_until_element_present(update_button_xpath,10)
                update_button = row.find_element(By.XPATH, update_button_xpath)
                update_button.click()
                print(f"update success: {row_id} の更新ボタンをクリックしました")
                time.sleep(1)  # クリック間隔
            except Exception as e:
                print(f"update failure: {row_id} の更新ボタンをクリックできませんでした: {e}")

    def close(self):
        """Selenium WebDriverを閉じる"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriverを正常に閉じました。")
            except Exception as e:
                logger.warning(f"WebDriverの終了中にエラーが発生しました: {e}")

    def _send_to_element(self, xpath, keys):
        """XPathで指定された入力要素にキーを送信する"""
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            element.clear()
            logger.debug(f"{xpath}にキーを送信しています")
            element.send_keys(keys)
        except Exception as e:
            logger.error(f"{xpath}にキーを送信できませんでした: {e}")

    def portfolio(self):
        """MoneyForwardからポートフォリオデータを取得する"""
        self.driver.get("https://ssnb.x.moneyforward.com/bs/portfolio")
        #self.wait_until_element_present((By.TAG_NAME, "body"), 10)
        self.wait_until_element_present("//body", 10)  
        asset_data = {
            "depo": self._extract_table_data('//*[@id="portfolio_det_depo"]/section/table/tbody/tr', self.depo_keys),
            "eq": self._extract_table_data('//*[@id="portfolio_det_eq"]/table/tbody/tr', self.eq_keys),
            "mf": self._extract_table_data('//*[@id="portfolio_det_mf"]/table/tbody/tr', self.mf_keys),
            "pns": self._extract_table_data('//*[@id="portfolio_det_pns"]/table/tbody/tr', self.pns_keys),
            "po": self._extract_table_data('//*[@id="portfolio_det_po"]/table/tbody/tr', self.po_keys)
        }
        return asset_data

    def _extract_table_data(self, xpath, keys):
        """XPathとキーを指定してテーブルデータを抽出する"""
        elements = self.driver.find_elements(By.XPATH, xpath)
        data = {}
        for row in elements:
            cells = row.find_elements(By.TAG_NAME, "td")
            name = cells[0].text
            if name not in data:
                data[name] = {}
            for idx, key in enumerate(keys):
                data[name][key] = cells[idx].text if idx < len(cells) else ""
        return data

    def close(self):
        """Selenium WebDriverを閉じる"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriverを正常に閉じました。")
            except Exception as e:
                logger.warning(f"WebDriverの終了中にエラーが発生しました: {e}")

    def _send_to_element(self, xpath, keys):
        """XPathで指定された入力要素にキーを送信する"""
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            element.clear()
            logger.debug(f"{xpath}にキーを送信しています")
            element.send_keys(keys)
        except Exception as e:
            logger.error(f"{xpath}にキーを送信できませんでした: {e}")