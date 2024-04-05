from dotenv import load_dotenv
import os

load_dotenv()


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from multiprocessing import Process
import time

class WebScraper:
    # Create a WebScraper instance
    def __init__(self):
        self.driver = self.initialize_driver()
        self.wait = WebDriverWait(self.driver, 30)  # Added explicit wait

    # Init the WebScraper instance
    def initialize_driver(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", {
            # "profile.managed_default_content_settings.images": 2,  # Disable images
            "profile.managed_default_content_settings.stylesheets": 2,  # Disable CSS
        })

        chrome_options.accept_untrusted_certs = True
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument('--ignore-certificate-errors')  # Equivalent to setAcceptInsecureCerts(true)
        # chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        webdriver_service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
        driver.implicitly_wait(20)
        return driver

    # Scrape the website
    def scrape_website(self, url):
        try:
            self.driver.set_window_size(1920, 1080)
            self.driver.get(url)
            # Wait for API requests and complete show on the page
            username_element = self.driver.find_element(By.ID, "userName")
            username_element.send_keys("Angelab@getdelmar.com")
            self.driver.execute_script(f"""document.getElementById('usernameSubmit').click()""")
            print(1)
            self.wait.until(   
                lambda d: d.execute_script("""return document.getElementById("password") != undefined""")
            )
            password_element = self.driver.find_element(By.ID, "password")
            password_element.send_keys("Liamb0218.")
            print(2)
            self.driver.execute_script(f"""document.getElementsByClassName("ant-btn ant-btn-primary Login-Form-SubmitButton margin-top-lg BTButton")[0].click()""")
            self.wait.until(   
                lambda d: d.execute_script("""return document.getElementsByClassName('FeedItem').length > 0""")
            )
            print(3)
            feed_items = self.driver.execute_script(f"""return document.getElementsByClassName("FeedItem")""")
            for i in range(len(feed_items)):
                title = self.driver.execute_script(f"""return document.getElementsByClassName('FeedItem')[{i}].getElementsByTagName('h4')[0].textContent""")
                date = self.driver.execute_script(f"""return document.getElementsByClassName('FeedItem')[{i}].getElementsByClassName('margin-left-sm')[0].textContent""")
                sender = self.driver.execute_script(f"""return document.getElementsByClassName('FeedItem')[{i}].getElementsByTagName('span')[2].textContent""")

                print(title)
                print(date)
                print(sender)
                
            #job_lists = self.driver.execute_script(f"""return document.getElementsByClassName("ant-list-item JobListItem")[0].textContent""")

        except Exception as e:
            print(e)

    # Close the WebDriver instance
    def close_driver(self):
        self.driver.quit()


def run_scraper():
    scraper = WebScraper()
    url = "https://buildertrend.net/"
    scraper.scrape_website(url)
    scraper.close_driver()

if __name__ == "__main__":
    run_scraper()

    # Process exit command
    while True:
        should_exit = input("Type 'exit' to close the application: ")
        if should_exit.lower() == 'exit':
            break