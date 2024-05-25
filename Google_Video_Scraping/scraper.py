import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pytube import YouTube

COOKIE_ACCEPT_XPATHS = [
    "//span[text()='Accept all']",
    "//div[text()='Accept all']",
    "/html/body/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button/span",
    "/html/body/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button/div[3]"
]
SCROLL_TIMEOUT = 10
DIR = 'videos'
NUM_PAGES = 10

class Scraper:

    def __init__(self, search_query, directory=DIR):
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--lang=en-GB")

        self.dir = directory
        self.query = search_query.replace(' ', '+')
        self.endpoint = f'https://www.google.com/search?q={self.query}&tbm=vid'
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

        overall_counter = 0  # To keep track of video count across all pages

        for page in range(NUM_PAGES):
            print(f"Scraping page {page + 1}")
            start_time = datetime.now()
            while (datetime.now() - start_time).total_seconds() < SCROLL_TIMEOUT:
                self.scroll_down()
                time.sleep(1)
            
            self.scrape_video_results(overall_counter)
            overall_counter += len(self.driver.find_elements(By.CSS_SELECTOR, 'div.g'))

            try:
                next_button = self.driver.find_element(By.ID, 'pnnext')
                next_button.click()
                time.sleep(2)  # Wait for the next page to load
            except NoSuchElementException:
                print("No more pages found.")
                break
        
        self.driver.quit()
        print('Scraping finished')

    def scrape_video_results(self, overall_counter):
        results = self.driver.find_elements(By.CSS_SELECTOR, 'div.g')
        print(f"Found {len(results)} video results")

        for counter, result in enumerate(results, start=overall_counter):
            try:
                url_element = result.find_element(By.CSS_SELECTOR, 'a')
                url = url_element.get_attribute('href')

                if 'youtube.com' in url or 'youtu.be' in url:
                    self.download_youtube_video(url, counter)
            except NoSuchElementException as e:
                print(f"Error extracting information for result {counter}: {e}")

    def download_youtube_video(self, url, counter):
        try:
            yt = YouTube(url)
            video_stream = yt.streams.get_highest_resolution()
            video_stream.download(output_path=self.path, filename=f"{self.query}_{counter}.mp4")
            print(f"Downloaded: {yt.title}")
        except Exception as e:
            print(f"Failed to download video {url}: {e}")
