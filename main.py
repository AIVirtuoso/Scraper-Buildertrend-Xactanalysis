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

from database_handler import DatabaseHandler

class WebScraper:
    # Create a WebScraper instance
    def __init__(self):
        self.driver = self.initialize_driver()
        self.wait = WebDriverWait(self.driver, 30)  # Added explicit wait
        self.reports = []
    # Init the WebScraper instance
    def initialize_driver(self):
        command = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "--user-data-dir=C:/SeleniumChromeProfile",
        "--remote-debugging-port=9222"
        ]
        subprocess.Popen(command)
    
        chrome_options = Options()
        chrome_options.accept_untrusted_certs = True
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument("--user-data-dir=C:/SeleniumChromeProfile")
        chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
        webdriver_service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
        driver.implicitly_wait(5)
        return driver
##############BuilderTrend################
    # Scrape the buildertrend website
    def scrape_buildertrend_website(self, url):
        try:
            # Navigate the url
            self.driver.get(url)
            # Get the first job content from the list
            job_content = self.driver.execute_script(f"""return document.getElementsByClassName('ItemRowJobName flex-grow-1')[1].textContent""")
            # Navigate to the first job
            self.driver.execute_script(f"""document.getElementsByClassName('ItemRowJobName flex-grow-1')[1].click()""")
            # Counter for scroll down
            counter = 0
            while 1:
                time.sleep(1)
                # Scrape all necessary information from the job
                self.scrape_listed_job()
                # Current list existing job counts
                job_len = self.driver.execute_script(f"""return document.getElementsByClassName('ItemRowJobName flex-grow-1').length""")
                for j in range(job_len):
                    job_text = self.driver.execute_script(f"""return document.getElementsByClassName('ItemRowJobName flex-grow-1')[{j}].textContent""")
                    # Check if there's job list on there
                    if job_text == job_content:
                        break
                # Check if it is at the end of the part
                if j == job_len - 1:
                    break
                # Extract the next job content from the list
                job_content = self.driver.execute_script(f"""return document.getElementsByClassName('ItemRowJobName flex-grow-1')[{j + 1}].textContent""")
                # Navigate to the following job
                self.driver.execute_script(f"""document.getElementsByClassName('ItemRowJobName flex-grow-1')[{j + 1}].click()""")
                # Scroll down the job list
                self.driver.execute_script(f"""document.getElementsByClassName('ReactVirtualized__Grid ReactVirtualized__List')[0].scrollTo(0, 36 * {counter})""")
                # Increase the counter for next scroll adjustment
                counter = counter + 1
        except Exception as e:
            self.driver.close()
            print(e)

    # Scrape detailed content of each job
    def scrape_listed_job(self):
        try:
            # Wait for webpage loaded correctly
            self.wait.until(   
                lambda d: d.execute_script("""return document.getElementsByClassName('BTLoading').length == 0""")
            )
            
            # Customer (First Name + Last Name + Phone Number)
            customer = self.driver.execute_script(f"""return document.getElementsByClassName('AbbreviateTitle')[0].textContent""")
            customer_phone = self.driver.execute_script(f"""return document.getElementsByClassName("ant-btn ant-btn-link ContactButton BTButton isolated NoShadow")[0].textContent""")

            # Project Managers (Name + Phone Number)
            project_manager_len = self.driver.execute_script(f"""return document.getElementsByClassName('AbbreviateTitle').length - 1""")
            for j in range(project_manager_len):
                project_manager = self.driver.execute_script(f"""return document.getElementsByClassName('AbbreviateTitle')[{j + 1}].textContent""")
                project_manager_phone = self.driver.execute_script(f"""return document.getElementsByClassName("ant-btn ant-btn-link ContactButton BTButton isolated NoShadow")[{j + 1}].textContent""")
                print(f"project_manager: {project_manager}")
                print(f"project_manager_phone: {project_manager_phone}")
            
            # Address
            address = self.driver.execute_script(f"""return document.getElementsByClassName('Address')[0].textContent + ' ' + document.getElementsByClassName('Address')[1].textContent""")
            
            print(f"customer: {customer}")
            print(f"customer_phone: {customer_phone}")
            print(f"address: {address}")
            res = {
                'name': customer,
                'phone': customer_phone,
                'address': address,
                'reports': []
            }
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
                    
                    print(f"title: {title}")
                    print(f"date: {date}")
                    print(f"sender: {sender}")
                    print(f"note: {note}")
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
            # Set email address
            # email_element = self.driver.find_element(By.NAME, "preAuthEmailField")
            # email_element.send_keys("Angelab@getdelmar.com")
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
            password_element.send_keys("Liamb0218.")
            # Click next button
            self.driver.execute_script(f"""document.getElementsByClassName('mat-focus-indicator ng-tns-c60-0 mat-raised-button mat-button-base')[0].click()""")
            # Wait for webpage loaded correctly
            self.wait.until(   
                lambda d: d.execute_script("""return document.getElementsByClassName('mdl-grid').length > 0""")
            )
            # Get claim list      
            claim_list = self.driver.execute_script(f"""return document.querySelector('[id="spage0"]').querySelectorAll('li')""")
            claim_length = len(claim_list)
            for index in range(1, claim_length):
                # Scrape each claim
                self.scrape_claim(index)
                # Navigate previous page
                self.driver.execute_script(f"""document.getElementById('header-home-link').click()""")
            self.driver.close()
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
        # Scrape customer name
        customer_name = self.driver.execute_script(f"""return document.querySelector('[id="insured-name"]').textContent""")
        customer_name = self.clear_text(customer_name)
        print(f"customer_name: {customer_name}")
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
        # Scrape mobile
        mobile_number = self.driver.execute_script(f"""return document.getElementById('dcp_owner_mobi_phone').textContent""")
        mobile_number = self.clear_text(mobile_number)
        print(f"mobile_number: {mobile_number}")
        # Append the customer list

        # Scrape node_list
        note_list = self.get_note_list()
        print("note_list: ", len(note_list))
        self.reports.append({
            'name': customer_name,
            'phone': mobile_number,
            'address': address,
            'reports': note_list
        })

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
        self.driver.quit()

def run_scraper():
    scraper = WebScraper()
    db = DatabaseHandler()
    db.create_tables()

    scraper.scrape_buildertrend_website("https://buildertrend.net/")
    scraper.scrape_xactanalysis_website("https://www.xactanalysis.com/")

    results = scraper.get_results()

    for result in results:
        db.insert_customer(result['name'], result['phone'], result['address'])
        for report in result['reports']:
            db.insert_report(result['name'], report['title'], report['note'], report['date'])

    scraper.close_driver()
    db.close()

    print("Scraping and storing data completed.")

if __name__ == "__main__":
    run_scraper()

    # Process exit command
    while True:
        should_exit = input("Type 'exit' to close the application: ")
        if should_exit.lower() == 'exit':
            break