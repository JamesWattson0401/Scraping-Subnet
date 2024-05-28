import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

COOKIE_ACCEPT_XPATHS = [
    "//span[text()='Accept all']",
    "//div[text()='Accept all']",
    "/html/body/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button/span",
    "/html/body/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button/div[3]"
]
SCROLL_TIMEOUT = 10
DIR = 'texts'

class TextScraper:

    def __init__(self, search_query, directory=DIR):
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--lang=en-GB")

        self.dir = directory
        self.query = search_query.replace(' ', '+')
        self.endpoint = f'https://www.google.com/search?q={self.query}'
        self.path = os.path.join(self.dir, self.query)

        self.driver = webdriver.Chrome(options=chrome_options)
        self.execute_scraping()

    def accept_cookies(self):
        for xpath in COOKIE_ACCEPT_XPATHS:
            try:
                cookies = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                cookies.click()
                return
            except (ElementClickInterceptedException, TimeoutException):
                continue
        print("Failed to accept cookies")

    def scroll_down(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def execute_scraping(self):
        try:
            os.makedirs(self.path, exist_ok=True)
        except OSError as error:
            print(f"Error creating directory: {error}")
            return

        self.driver.get(self.endpoint)
        self.accept_cookies()

        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < SCROLL_TIMEOUT:
            self.scroll_down()
            time.sleep(1)
        
        self.scrape_text_results()
        self.driver.quit()
        print('Scraping finished')

    def scrape_text_results(self):
        results = self.driver.find_elements(By.CSS_SELECTOR, 'div.g')
        print(f"Found {len(results)} text results")

        for counter, result in enumerate(results):
            try:
                url_element = result.find_element(By.CSS_SELECTOR, 'a')
                url = url_element.get_attribute('href')

                # Visit the URL and scrape the text content
                self.driver.execute_script("window.open('');")
                self.driver.switch_to.window(self.driver.window_handles[1])
                self.driver.get(url)

                time.sleep(2)  # Wait for the page to load

                text_content = self.get_text_content()
                self.save_text_result(counter, url, text_content)

                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            except NoSuchElementException as e:
                print(f"Error extracting information for result {counter}: {e}")

    def get_text_content(self):
        try:
            paragraphs = self.driver.find_elements(By.TAG_NAME, 'p')
            text_content = '\n'.join([para.text for para in paragraphs])
            return text_content
        except Exception as e:
            print(f"Failed to get text content: {e}")
            return ""

    def save_text_result(self, counter, url, text_content):
        try:
            with open(os.path.join(self.path, f"{self.query}_{counter}.txt"), 'w', encoding='utf-8') as file:
                file.write(f"URL: {url}\n")
                file.write(f"Content:\n{text_content}\n")
            print(f"Saved content from: {url}")
        except Exception as e:
            print(f"Failed to save text result {counter}: {e}")
