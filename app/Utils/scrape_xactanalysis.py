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

class WebScraper:
    # Create a WebScraper instance
    def __init__(self, builder_user, builder_pass, xact_user, xact_pass):
        self.driver = self.initialize_driver()
        self.wait = WebDriverWait(self.driver, 30)  # Added explicit wait
        self.reports = []
        self.builder_user = builder_user
        self.builder_pass = builder_pass
        self.xact_user = xact_user
        self.xact_pass = xact_pass

    # Init the WebScraper instance
    def initialize_driver(self):
        chrome_options = Options()
        chrome_options.accept_untrusted_certs = True
        extension_path = r'C:\SeleniumChromeProfile\Default\Extensions\gmlafnjffcblkipjaelgjdgdpmgmjbfp\1.0.0_0'
        chrome_options.add_argument('--load-extension={}'.format(extension_path))
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_experimental_option("prefs", {
            "permissions.default.stylesheet": 2,
        })
        chrome_options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.images": 2,  # Disable images
            "profile.managed_default_content_settings.stylesheets": 2,  # Disable CSS
        })
        webdriver_service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
        # driver.maximize_window()
        driver.implicitly_wait(5)
        return driver


##############XactAnalysis################
    # Scrape the website
    async def scrape_xactanalysis_website(self, url):
        try:
            # Navigate the url
            self.driver.get(url)

            try:
                # Set email address
                email_element = self.driver.find_element(By.NAME, "preAuthEmailField")
                email_element.clear()
                email_element.send_keys(self.xact_user)
            except:
                pass

            try:
                # Wait for the page
                self.wait.until(   
                    lambda d: d.execute_script("""return document.getElementsByClassName('mat-focus-indicator ng-tns-c60-0 mat-raised-button mat-button-base mat-primary').length > 0""")
                )
                
                # Click next button
                self.driver.execute_script(f"""document.getElementsByClassName('mat-focus-indicator ng-tns-c60-0 mat-raised-button mat-button-base mat-primary')[0].click()""")
                
                # Wait for next page
                self.wait.until(   
                    lambda d: d.execute_script("""return document.getElementsByClassName('mat-focus-indicator ng-tns-c60-0 mat-raised-button mat-button-base').length > 0""")
                )
            
                # Set password
                password_element = self.driver.find_element(By.NAME, "passwordField")
                password_element.send_keys(self.xact_pass)
                # Click next button
                self.driver.execute_script(f"""document.getElementsByClassName('mat-focus-indicator ng-tns-c60-0 mat-raised-button mat-button-base')[0].click()""")
            except:
                print("no password")
                pass
            
            print("pass password")
            # Wait for webpage loaded correctly

            self.wait.until(   
                lambda d: d.execute_script("""return document.getElementsByClassName('mdl-grid').length > 0""")
            )
            # Get claim list
            claim_list = self.driver.execute_script(f"""return document.querySelector('[id="spage0"]').querySelectorAll('li')""")
            claim_length = len(claim_list)
            print(f"claim_length: {claim_length}")
            send_xactanalysis(claim_length-1, 0)
            for index in range(1, claim_length):
                try:
                    # if index <=5:
                    #     continue
                    # if index >= 10:
                    #     break
                    print(f"index: {index}")
                    # Scrape each claim
                    self.scrape_claim(index)
                    # Navigate previous page
                    self.driver.execute_script(f"""document.getElementById('header-home-link').click()""")
                except Exception as e:
                    print(e)
                send_xactanalysis(claim_length-1, index)
        except Exception as e:
            # Close the webdriver
            print(e)

    # Scrape Each claim
    def scrape_claim(self, index):
        # Wait for webpage loaded correctly
        # self.wait.until(   
        #     lambda d: d.execute_script("""return document.querySelector('[id="spage0"]').querySelectorAll('li').length > 0""")
        # )
        self.wait.until(   
            lambda d: d.execute_script("""return document.getElementById('id="spage0') == null""")
        )
        # Click claim nth list target
        self.driver.execute_script(f"""document.querySelector('[id="spage0"]').querySelectorAll('li')[{index}].click()""")

        # Scrape project number
        project_name = self.driver.execute_script(f"""return document.querySelector('[class="data-point"]').getElementsByTagName('div')[0].textContent""")
        print(project_name)

        # Scrape claim number
        claim_number = self.driver.execute_script(f"""return document.querySelector('[id="assignment-id"]').textContent""")
        print(claim_number)

        # Scrape customer name
        customer_name = self.driver.execute_script(f"""return document.querySelector('[id="insured-name"]').textContent""")
        customer_name = self.clear_text(customer_name)
        print(f"customer_name: {customer_name}")



        if "&" in customer_name:
            parts = customer_name.split("&")
            # Extract first name from the first part
            last_name = parts[0].split(" ")[0].strip()
            # Extract last name from the second part
            first_name = parts[1].split("\"")[0].strip()
        else:
            if ',' in customer_name:
                parts = customer_name.split(",")
                last_name = parts[0].strip()
                first_name = parts[1].strip()
                # Extract last name from the second part
                f_parts = first_name.split(" ")
                first_name = f_parts[1].strip() if len(f_parts) > 1 else f_parts[0].strip()
            else:
                parts = customer_name.split(" ")
                # Extract first name from the first part
                first_name = parts[0].strip()
                # Extract last name from the second part
                last_name = parts[1].strip() if len(parts) > 1 else ""

        time.sleep(1)
        # Click "CLIENT/POLICY" tab
        self.driver.execute_script(f"""document.getElementById('d_clientpolicy-tab').click()""")
        # Wait for "CLIENT/POLICY" tab loaded correctly
        self.wait.until(   
            lambda d: d.execute_script("""return document.getElementsByClassName('client-policy').length > 0""")
        )
        # Scrape address
        address = self.driver.execute_script(f"""return document.getElementById('dcp_owner_addr').textContent""")
        address = self.clear_text(address)
        print(f"address: {address}")

        # Scrape email
        email = self.driver.execute_script(f"""return document.getElementById('dcp_owner_email').textContent""")
        email = self.clear_text(email)

        # Scrape mobile
        mobile_number = self.driver.execute_script(f"""return document.getElementById('dcp_owner_mobi_phone').textContent""")
        mobile_number = self.clear_text(mobile_number)
        # Remove non-digit characters except for '+' and ' '
        mobile_number = re.sub(r'[^\d\+ ]', '', mobile_number)

        # If the phone number doesn't start with '+', add '+1 '
        if not mobile_number.startswith('+'):
            mobile_number = '+1 ' + mobile_number
        print(f"mobile_number: {mobile_number}")
        # Append the customer list

        # Scrape node_list
        note_list = self.get_note_list()
        print("note_list: ", len(note_list))
        self.reports.append({
            'first_name': first_name,
            'last_name': last_name,
            'phone': mobile_number,
            'address': address,
            'email': email,
            'claim_number': claim_number,
            'project_name': project_name,
            'manager_name': "Angela Bermudez",
            'manager_phone': "+1 312 443 2120",
            'manager_email': "angelab@getdelmar.com",
            'reports': note_list
        })
        print("first_name", first_name)
        print("last_name", last_name)

    # Scrape notes from the table
    def get_note_list(self):
        # Click "NOTES" tab
        self.driver.execute_script(f"""document.getElementById('d_notes-tab').click()""")
        # Wait for "NOTES" tab loaded correctly
        self.wait.until(
            lambda d: d.execute_script("""return document.getElementsByClassName('mdl-data-table__cell--non-numeric wrap ').length > 0""")
        )
        time.sleep(1)
        # Extract rows
        rows = self.driver.execute_script(f"""return document.querySelectorAll('table')[1].querySelector('tbody').querySelectorAll('tr')""")
        note_list = []
        for row in rows:
            # Scrape Source
            source = self.driver.execute_script("return arguments[0].querySelectorAll('td')[1].innerHTML", row)
            source = re.sub(r'\s+', ' ', source).strip().split('<br>')
            source = '\n'.join(source)
            # Scrape Note
            note = self.driver.execute_script("return arguments[0].querySelectorAll('td')[2].querySelector('div').innerHTML", row)
            note = re.sub(r'\s+', ' ', note).strip().split('<br>')
            note = '\n'.join(note)
            # Scrape data
            date = self.driver.execute_script("return arguments[0].querySelectorAll('td')[3].textContent", row)
            date = self.clear_text(date)
            note_list.append({'title': source, 'note': note, 'date': date})
        return note_list
    
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
    await scraper.scrape_xactanalysis_website("https://www.xactanalysis.com/")
    scraper.close_driver()

    results = scraper.get_results()

    print("Scraping and storing data completed.")
    
    with open(f"{source}.json", 'w') as json_file:
        # Write the dictionary to the file as JSON  
        json.dump(results, json_file, indent=4)

    data = {}
    with open(f"{source}.json", 'r') as file:
        data = json.load(file)
    # print(data)
    url = 'https://backend.getdelmar.com/api/v1/get-scraped-result'
    requests.post(url, json=data)
    return True


