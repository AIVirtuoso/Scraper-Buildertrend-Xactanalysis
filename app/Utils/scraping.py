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

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def kill_process_on_port(port):
    command = f"netstat -ano | findstr :{port}"
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    lines = result.stdout.splitlines()
    for line in lines:
        parts = line.rstrip().split()
        if parts and parts[-1] == str(port):
            pid = parts[-2]
            subprocess.run(f"taskkill /PID {pid} /F", shell=True)

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
        self.wait = WebDriverWait(self.driver, 30)  # Added explicit wait
        self.reports = []
        self.builder_user = builder_user
        self.builder_pass = builder_pass
        self.xact_user = xact_user
        self.xact_pass = xact_pass

    # Init the WebScraper instance
    def initialize_driver(self):
        try:
            if is_port_in_use(9222):
                kill_process_on_port(9222)
        except:
            pass

        command = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "--user-data-dir=C:/SeleniumChromeProfile",
        "--remote-debugging-port=9222"
        ]
        subprocess.Popen(command)
    
        chrome_options = Options()
        chrome_options.accept_untrusted_certs = True
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--user-data-dir=C:/SeleniumChromeProfile")
        chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--ignore-certificate-errors')
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # chrome_options.add_experimental_option("prefs", prefs)
        webdriver_service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
        # driver.maximize_window()
        driver.implicitly_wait(5)
        return driver
    
    
##############BuilderTrend################
    # Scrape the buildertrend website
    def scrape_buildertrend_website(self, url):
        try:
            email_element = self.driver.find_element(By.ID, 'userName')
            email_element.clear()
            email_element.send_keys(self.builder_user)
            self.driver.execute_script(f"""document.getElementById('usernameSubmit').click()""")
        except:
            print("no username field!")
            pass

        try:
            email_element = self.driver.find_element(By.ID, 'password')
            email_element.clear()
            email_element.send_keys(self.builder_pass)
            
            self.driver.execute_script(f"""document.querySelectorAll('[data-testid="login"]').click()""")
            
        except:
            print("no pass field!")
            pass
        
        try:
            # Navigate the url
            self.driver.get(url)

            # Wait for webpage loaded correctly
            self.wait.until(   
                lambda d: d.execute_script("""return document.getElementsByClassName('ItemRowJobName flex-grow-1').length > 0""")
            )

            # Get the content that contains the lenthg of list (e.g: 'All 50 Listed Jobs')
            length_content = self.driver.execute_script(f"""return document.getElementsByClassName('ItemRowJobName flex-grow-1')[0].textContent""")
            total = extract_length(length_content)

            # Get the first job content from the list
            job_content = self.driver.execute_script(f"""return document.getElementsByClassName('ItemRowJobName flex-grow-1')[1].textContent""")

            # Navigate to the first job
            self.driver.execute_script(f"""document.getElementsByClassName('ItemRowJobName flex-grow-1')[1].click()""")

            # Counter for scroll down
            counter = 0
            send_buildertrend(total, 0)

            while 1:
                try:
                    print("========================counter========================", counter)
                    # if counter == 15:
                    #     break
                    time.sleep(1)
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
                        print("job_text ++", job_text)

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
                    self.driver.execute_script(f"""document.getElementsByClassName('ReactVirtualized__Grid ReactVirtualized__List')[0].scrollTo(0, 32 * {counter})""")
                    
                    # Increase the counter for next scroll adjustment
                except Exception as ex:
                    print(ex)
            send_buildertrend(counter + 1, counter + 1)
                
                
        except Exception as e:
            print("ending error:", e)

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


            # Project Managers (Name + Phone Number)
            project_manager_len = self.driver.execute_script(f"""return document.getElementsByClassName('AbbreviateTitle').length - 1""")
            if project_manager_len:
                self.driver.execute_script(f"""return document.getElementsByClassName('AbbreviateTitle')[1].click()""")
                project_manager_first_name = self.driver.execute_script(f"""return document.getElementById('firstName').value""")
                project_manager_last_name = self.driver.execute_script(f"""return document.getElementById('lastName').value""")

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
                title = self.driver.execute_script(f"""return document.getElementsByClassName('FeedItem')[{i}].getElementsByTagName('h4')[0].textContent""")
                if "new Daily Log" in title:
                    # date of note
                    date = self.driver.execute_script(f"""return document.getElementsByClassName('FeedItem')[{i}].getElementsByClassName('margin-left-sm')[0].textContent""")
                    # project manager
                    sender = self.driver.execute_script(f"""return document.getElementsByClassName('FeedItem')[{i}].getElementsByTagName('span')[2].textContent""")
                    # Daily Note
                    note = self.driver.execute_script(f"""return document.getElementsByClassName('FeedItem')[{i}].getElementsByClassName('ant-card-body')[0].textContent""")
                    
                    # print(f"title: {title}")
                    # print(f"date: {date}")
                    # print(f"sender: {sender}")
                    # print(f"note: {note}")
                    res['reports'].append({
                        'title': title,
                        'date': date,
                        'note': note
                    })
            # Append results into reports
            self.reports.append(res)
        except Exception as e:
            print(e)



##############XactAnalysis################
    # Scrape the website
    def scrape_xactanalysis_website(self, url):
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
        self.wait.until(   
            lambda d: d.execute_script("""return document.querySelector('[id="spage0"]').querySelectorAll('li').length > 0""")
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

def run_scraper(source, builder_user, builder_pass, xact_user, xact_pass):
    scraper = WebScraper(builder_user, builder_pass, xact_user, xact_pass)
    # db = DatabaseHandler()
    # db.create_tables()
    if source == "BuilderTrend":    
        scraper.scrape_buildertrend_website("https://buildertrend.net/")
        time.sleep(3)
        scraper.close_driver()
    else:
        scraper = WebScraper(builder_user, builder_pass, xact_user, xact_pass)
        scraper.scrape_xactanalysis_website("https://www.xactanalysis.com/")
        scraper.close_driver()

    results = scraper.get_results()


    # print(results)
    print("Scraping and storing data completed.")
    
    with open("scraped_results.json", 'w') as json_file:
        # Write the dictionary to the file as JSON  
        json.dump(results, json_file, indent=4)

    data = {}
    with open("scraped_results.json", 'r') as file:
        data = json.load(file)
    print(data)
    url = 'https://backend.getdelmar.com/api/v1/get-scraped-result'

    # Send a POST request to the FastAPI endpoint with the JSON data
    response = requests.post(url, json=data)
        
    return True