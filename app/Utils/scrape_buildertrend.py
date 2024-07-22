import requests
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
from concurrent.futures import ThreadPoolExecutor
import time
import subprocess
import re
import json

from app.Utils.Requests import send_buildertrend, send_xactanalysis

import socket
import subprocess

def extract_length(content: str):
    # Regular expression to find numbers
    numbers = re.findall(r'\d+', content)

    # Assuming there is at least one number, get the first one
    number = numbers[0] if numbers else 0
    return number

class WebScraper:
    # Create a WebScraper instance
    def __init__(self, builder_user, builder_pass, xact_user, xact_pass):
        self.driver = self.initialize_driver()
        self.wait = WebDriverWait(self.driver, 5)  # Added explicit wait
        self.reports = []
        self.builder_user = builder_user
        self.builder_pass = builder_pass
        self.xact_user = xact_user
        self.xact_pass = xact_pass

    # Init the WebScraper instance
    def initialize_driver(self):
        # command = [
        # "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        # f"--user-data-dir={profile}",
        # "--remote-debugging-port=9222"
        # ]
        # subprocess.Popen(command)
    
        chrome_options = Options()
        # chrome_options.add_argument("--headless")

        chrome_options.add_argument("--user-data-dir=C:/SeleniumChromeProfile")
        chrome_options.accept_untrusted_certs = True
        chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--ignore-certificate-errors')
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # chrome_options.add_experimental_option("prefs", prefs)
        webdriver_service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
        # driver.maximize_window()
        return driver
    
    
##############BuilderTrend################
    # Scrape the buildertrend website
    async def scrape_buildertrend_website(self, url):
        self.driver.get(url)
        try:
            email_element = self.wait.until(EC.presence_of_element_located((By.ID, 'userName')))
            email_element.clear()
            email_element.send_keys(self.builder_user)
            self.driver.find_element(By.ID, 'usernameSubmit').click()
        except Exception as e:
            print(e)
            print("no username field!")
            pass

        try:
            password_element = self.wait.until(EC.presence_of_element_located((By.ID, 'password')))
            password_element.clear()
            password_element.send_keys(self.builder_pass)
            self.driver.find_element(By.CSS_SELECTOR, '[data-testid="login"]').click()
            
        except:
            print("no pass field!")
            pass
        
        try:

            # Wait for webpage loaded correctly
            self.wait.until(   
                lambda d: d.execute_script("""return document.getElementsByClassName('ItemRowJobName flex-grow-1').length > 0""")
            )

            # Get the content that contains the lenthg of list (e.g: 'All 50 Listed Jobs')
            length_content = self.driver.execute_script(f"""return document.getElementsByClassName('ItemRowJobName flex-grow-1')[0].textContent""")
            total = extract_length(length_content)

            # Get the first job content from the list
            job_content = self.driver.find_element(By.CLASS_NAME, 'ItemRowJobName').text

            # Navigate to the first job
            self.driver.execute_script(f"""document.getElementsByClassName('ItemRowJobName flex-grow-1')[1].click()""")

            # Counter for scroll down
            counter = 0
            send_buildertrend(total, total)

            while 1:
                try:
                    print("========================counter========================", counter)
                    # if counter == 15:
                    #     break
                    # Scrape all necessary information from the job
                    self.scrape_listed_job()
                    send_buildertrend(total, counter + 1)
                    self.wait.until(   
                        lambda d: d.execute_script("""return document.getElementsByClassName('ItemRowJobName flex-grow-1').length > 0""")
                    )
                    # Current list existing job counts
                    job_len = self.driver.execute_script(f"""return document.getElementsByClassName('ItemRowJobName flex-grow-1').length""")
                    for j in range(job_len):
                        job_text = self.driver.execute_script(f"""return document.getElementsByClassName('ItemRowJobName flex-grow-1')[{j}].textContent""")
                        # Check if there's job list on there
                        # print("job_text ++", job_text)

                        if job_text == job_content:
                            counter = counter + 1
                            break
                    # Check if it is at the end of the part
                    if j == job_len - 1:
                        break
                    
                    # Extract the next job content from the list
                    job_content = self.driver.execute_script(f"""return document.getElementsByClassName('ItemRowJobName flex-grow-1')[{j + 1}].textContent""")
                    print("job_content --", job_content)
                    # Navigate to the following job
                    self.driver.execute_script(f"""document.getElementsByClassName('ItemRowJobName flex-grow-1')[{j + 1}].click()""")
                    
                    # Scroll down the job list
                    self.driver.execute_script(f"""document.getElementsByClassName('ReactVirtualized__Grid ReactVirtualized__List')[0].scrollTo(0, 26 * {counter})""")
                    
                    # Increase the counter for next scroll adjustment
                except Exception as ex:
                    print(ex)
            send_buildertrend(total, total)

                
                
        except Exception as e:
            import traceback
            print("An error occurred:", str(e))
            traceback.print_exc()  # This will print the stack trace to the console

    # Scrape detailed content of each job
    def scrape_listed_job(self):
        try:
            # Wait for webpage loaded correctly
            self.wait.until(   
                lambda d: d.execute_script("""return document.getElementsByClassName('BTLoading').length == 0""")
            )

            
            self.driver.execute_script(f"""document.querySelector('[data-testid="JobInfoIcon"]').click()""")

            self.wait.until(   
                lambda d: d.execute_script("""return document.getElementById('customFields.0.value') != null""")
            )

            claim_number = self.driver.execute_script(f"""return document.getElementById('customFields.0.value').value""")
            print("claim_number", claim_number)

            project_name = self.driver.execute_script(f"""return document.getElementById('customFields.8.value').value""")
            
            print('project_name', project_name)

            # Close Job Modal
            self.driver.execute_script(f"""document.querySelector('[data-testid="close"]').click()""")
            self.wait.until(
                EC.invisibility_of_element_located((By.ID, 'customFields.0.value'))
            )
            
            # Scrape Project Name


            # Open Customer Contact Modal
            self.driver.execute_script(f"""return document.getElementsByClassName('AbbreviateTitle')[0].click()""")
            self.wait.until(   
                lambda d: d.execute_script("""return document.getElementById('firstName') != null""")
            )
            first_name = self.driver.execute_script(f"""return document.getElementById('firstName').value""")
            last_name = self.driver.execute_script(f"""return document.getElementById('lastName').value""")
            
            customer_phone = self.driver.execute_script(f"""return document.getElementById('CellPhoneField-CellPhoneNumber').value""")
            customer_email = self.driver.execute_script(f"""return document.getElementById('primaryEmail.emailAddress') != null ? document.getElementById('primaryEmail.emailAddress').value : ''""")

            # Close Customer Contact Modal
            self.driver.execute_script(f"""document.querySelector('[data-testid="close"]').click()""")

            print("customer_email: ", customer_email)
            # Project Managers (Name + Phone Number)
            project_manager_len = self.driver.execute_script(f"""return document.getElementsByClassName('AbbreviateTitle').length - 1""")
            if project_manager_len:
                print('here0')
                self.driver.execute_script(f"""return document.getElementsByClassName('AbbreviateTitle')[1].click()""")
                self.wait.until(   
                    lambda d: d.execute_script("""return document.getElementById('firstName') != null""")
                )
                # print('here1')
                project_manager_first_name = self.driver.execute_script(f"""return document.getElementById('firstName').value""")
                project_manager_last_name = self.driver.execute_script(f"""return document.getElementById('lastName').value""")
                print("project_manager_last_name: ", project_manager_last_name)
                project_manager_phone = self.driver.execute_script(f"""return document.getElementById('phone').value""")
                project_manager_email = self.driver.execute_script(f"""return document.getElementById('primaryEmail.emailAddress').value""")
                self.driver.execute_script(f"""document.querySelector('[data-testid="close"]').click()""")
                self.wait.until(
                    EC.invisibility_of_element_located((By.ID, 'phone'))
                )
            
            # Address
            address = self.driver.execute_script(f"""return document.getElementsByClassName('Address')[0].textContent + ' ' + document.getElementsByClassName('Address')[1].textContent""")
            
            # print(f"claim_number: {claim_number}")
            # print(f"project_name: {project_name}")
            print(f"first_name: {first_name}")
            print(f"last_name: {last_name}")
            # print(f"customer_phone: {customer_phone}")
            # print(f"customer_email: {customer_email}")
            # print(f"address: {address}")
            res = {
                'first_name': first_name,
                'last_name': last_name,
                'project_name': project_name,
                'phone': customer_phone,
                'email': customer_email,
                'address': address,
                'claim_number': claim_number,
                'manager_name': project_manager_first_name + ' ' + project_manager_last_name,
                'manager_phone': project_manager_phone,
                'manager_email': project_manager_email,
                'reports': []
            }

            print(res)

            # Feed Items
            feed_items = self.driver.execute_script(f"""return document.getElementsByClassName("FeedItem")""")
            
            for i in range(len(feed_items)):
                # title of note
                try:
                    title = self.driver.execute_script(f"""return document.getElementsByClassName('FeedItem')[{i}].getElementsByTagName('h4')[0].textContent""")
                    if "new Daily Log" in title:
                        # date of note
                        date = self.driver.execute_script(f"""return document.getElementsByClassName('FeedItem')[{i}].getElementsByClassName('margin-left-sm')[0].textContent""")
                        # Daily Note
                        self.driver.execute_script(f"""document.getElementsByClassName('FeedItem')[{i}].getElementsByClassName('margin-left-sm')[0].click()""")
                        self.wait.until(   
                            lambda d: d.execute_script("""return document.getElementById('notes') != null""")
                        )
                        note = self.driver.execute_script(f"""return document.getElementById('notes').textContent""")
                        self.driver.execute_script(f"""document.querySelector('[data-testid="close"]').click()""")
                        print("i -- ", i)
                        self.wait.until(
                            EC.invisibility_of_element_located((By.ID, 'notes'))
                        )
                        
                        # print(f"title: {title}")
                        # print(f"date: {date}")
                        # print(f"sender: {sender}")
                        # print(f"note: {note}")
                        res['reports'].append({
                            'title': title,
                            'date': date,
                            'note': note
                        })
                except Exception as e:
                    print(e)
            print(res)
            # Append results into reports
            self.reports.append(res)
        except Exception as e:
            print(e)

    # Retrieve reports
    def get_results(self):
        return self.reports

    def clear_text(self, text):
        return re.sub(r'\s+', ' ', text).strip()

    # Close the WebDriver instance
    def close_driver(self):
        self.driver.close()

async def run_scraper(source, builder_user, builder_pass, xact_user, xact_pass):
    scraper = WebScraper(builder_user, builder_pass, xact_user, xact_pass)
    await scraper.scrape_buildertrend_website("https://buildertrend.net/")
    time.sleep(3)
    scraper.close_driver()

    results = scraper.get_results()


    # print(results)
    print("Scraping and storing data completed.")
    
    with open(f"{source}.json", 'w') as json_file:
        json.dump(results, json_file, indent=4)

    data = {}
    with open(f"{source}.json", 'r') as file:
        data = json.load(file)
    # print(data)
    url = 'https://backend.getdelmar.com/api/v1/get-scraped-result'
    requests.post(url, json=data)
    return True


