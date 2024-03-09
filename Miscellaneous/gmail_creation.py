import random
import time
from fake_useragent import UserAgent
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.edge.service import Service
from datetime import datetime, timedelta
from smsactivate.api import SMSActivateAPI
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager

APIKEY = '2417387b156062A9319d62191b4dcfAd'

max_connections = 1

db_params = {
    'host': 'opraah-database.c9qouuiwyuwx.ap-south-1.rds.amazonaws.com',
    'database': 'opraah',
    'user': 'postgres',
    'password': 'VUFPZaluUQk',
    'port': '5432'
}

connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=max_connections,
    **db_params
)


min_wait_time = 5
max_wait_time = 7
email=""
password = "Opraahfx@1234"

@contextmanager
def connect_to_database():
    connection = connection_pool.getconn()

    try:
        yield connection  # Provide the connection to the caller
    finally:
        connection_pool.putconn(connection)  # Release the connection back to the pool

def create_gmail_user_in_db(user_info):
    try:
        # Connect to the database using the context manager
        with connect_to_database() as connection:
            # Create a cursor to interact with the database
            with connection.cursor() as cursor:
                # SQL query to select a user with less than three videos uploaded
                insert_query = """
                    INSERT INTO public.youtube_accounts 
                    (email, "password", in_use, last_used, videos_uploaded, "number", activation_id, insta_account) 
                    VALUES (%s, %s, false, CURRENT_TIMESTAMP, 0, %s, %s, false);
                """

                # Execute the SELECT query
                cursor.execute(insert_query, (user_info['email_id'], password, user_info['number'], user_info['activation_id']))
                connection.commit()
    except Exception as e:
        pass

def open_browser(driver_version='120.0.6099.234', headless=False, user_agent=False, proxy=None, download_directory=None):
    
    chrome_options = webdriver.ChromeOptions()
    # edge_options = webdriver.EdgeOptions()
    # chrome_options.binary_location = chrome_binary_path
    
    # chrome_options.add_argument("--window-size=1920,1080")
    #chrome_options.add_argument("--start-minimized")  # Add this line to start in minimized mode
    # chrome_options.add_argument("--disable-extensions") # Disable Chrome extensions
    #chrome_options.add_argument('--disable-notifications') # Disable Chrome notifications
    chrome_options.add_argument("--mute-audio") # Mute system audio
    #chrome_options.add_argument('--disable-dev-shm-usage') # Disable the use of /dev/shm to store temporary data
    #chrome_options.add_argument('--ignore-certificate-errors') # Ignore certificate errors
    chrome_options.add_argument("--incognito")  # Start Chrome in incognito mode
    #chrome_options.add_argument("--disable-geolocation")  # Disable geolocation in Chrome
    chrome_options.add_argument('--disable-web-security')
    
    if headless:
        chrome_options.add_argument("--headless")
    if user_agent:
        ua = UserAgent()
        user_agent = ua.chrome + ' ' + ua.os_linux
        chrome_options.add_argument(f'user-agent={user_agent}')
    # if proxy:
    #     chrome_options.add_argument(f"--load-extension=./proxy_isp")  
    if download_directory:
        preferences = {"download.default_directory": download_directory}
        chrome_options.add_experimental_option("prefs", preferences)
    
    driver = webdriver.Chrome(options=chrome_options)
    # driver = webdriver.Edge(service=edge_service)
    return driver


def get_number():
    sa = SMSActivateAPI(APIKEY)
    sa_response = sa.getNumber(service='go',country=22)
    return sa_response

def get_otp(activation_code):
    sa = SMSActivateAPI(APIKEY)
    sa_response = sa.getStatus(id=activation_code)
    return sa_response

def random_time_delay(start=10, end=20):
    time.sleep(random.uniform(start, end))

def go_to_gmail_account(driver):

    driver.get("https://www.google.com/gmail/about/")
    random_time_delay(min_wait_time, max_wait_time)

def go_to_account_signup(driver):
    driver.find_element(By.XPATH, ".//summary[@class='dropdown__summary']/div[@class='dropdown__icon']").click()
    random_time_delay(1,2)
    driver.find_element(By.XPATH, ".//a[@data-action='For my personal use']").click()
    return driver

def generate_user_info():
    
    firstnames = ["Umesh","Mukesh","Jignesh","Chirag","Jignesh","Raul","Vivek","Mayank","Nipendra"]
    lastnames = ["Mittal","Bansal","Aggarwal","Rathore","Bhola","Kalwar","Gupta"]
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    firstname = firstnames[random.randint(0,len(firstnames)-1)].lower()
    lastname = lastnames[random.randint(0,len(lastnames)-1)].lower()

    unique_id = str(int(time.time()))
    email_id = "{firstname}{lastname}{unique_id}@gmail.com".format(firstname=firstname, lastname=lastname, unique_id=unique_id)

    random_time_delay(2,4)
    
    year = random.randint(1980, 1998)  # Random year between 1950 and 2005
    month = random.choice(months)      # Random month from the list of months
    day = random.randint(1, 28)         # Random day between 1 and 28 (assuming February)

    
    info = {
        'firstname': firstname, 
        'lastname': lastname,
        'month': month,
        'day': str(day),
        'gender': 'Male',
        'year': year,
        'email_id': email_id,
        'number': '',
        'activation_id': '',
    }
    
    return info


def create_account(driver, user_info):

    unique_id = str(int(time.time()))
    email_id = user_info['email_id']
    first_name = user_info['firstname']
    last_name = user_info['lastname']
    month = user_info['month']
    day = user_info['day']
    gender = user_info['gender']
    year = user_info['year']
    driver.find_element(By.ID, "firstName").send_keys(first_name)
    driver.find_element(By.ID, "lastName").send_keys(last_name)
    driver.find_element(By.ID, "lastName").send_keys(Keys.ENTER)

    random_time_delay(start=5,end=10)
    month_dropdown = Select(driver.find_element(By.ID, "month"))
    month_dropdown.select_by_visible_text(month)
    driver.find_element(By.ID, "day").send_keys(day)
    random_time_delay(start=2,end=7)
    driver.find_element(By.ID, "year").send_keys(year)
    random_time_delay(start=2,end=7)
    gender_dropdown = Select(driver.find_element(By.ID, "gender"))
    gender_dropdown.select_by_visible_text(gender)
    random_time_delay(start=2,end=7)
    driver.find_element(By.ID, "day").send_keys(Keys.ENTER)
    random_time_delay(start=5,end=10)
    
    # Enter gmail account
    try:
        driver.find_element(By.XPATH, "//div[text()='Create your own Gmail address']").click()
    except:
        pass
    driver.find_element(By.XPATH, "//input[@name='Username']").send_keys(email_id.split("@")[0])
    driver.find_element(By.XPATH, "//input[@name='Username']").send_keys(Keys.ENTER)
    random_time_delay(start=5,end=10)
    
    # Enter password
    driver.find_element(By.XPATH, "//input[@type='password']").send_keys(password)
    driver.find_element(By.XPATH, "//input[@type='password']").send_keys(Keys.TAB)
    driver.switch_to.active_element.send_keys(password)
    driver.switch_to.active_element.send_keys(Keys.ENTER)
    
    random_time_delay(start=5,end=10)
    # ENTER CODE FOR MOBILE NUMBER IF DETECTED
    
    try:
        driver.find_element(By.XPATH, "//div[text()='Get a verification code sent to your phone']")
        flag = True
        while flag:
            number_detail = get_number()
            number = str(number_detail['phone'])
            if not number.startswith("+"):
                number = '+' + number
            activation_id = number_detail['activation_id']
            user_info['number'] = number
            user_info['activation_id'] = activation_id
            driver.find_element(By.XPATH, ".//input[@id='phoneNumberId']").send_keys(number)
            driver.find_element(By.XPATH, ".//input[@id='phoneNumberId']").send_keys(Keys.ENTER)
            random_time_delay()
            try:
                x = driver.find_element(By.XPATH, "//div[text()='This phone number has been used too many times']")
                if x:
                    driver.find_element(By.XPATH, ".//input[@id='phoneNumberId']").clear()
                    continue
            except Exception as e:
                flag = False
                pass
            
            start_time = datetime.now()
            otp_response = None
            otp = None
            while datetime.now() < start_time + timedelta(minutes=3):
                otp_response = get_otp(activation_code=activation_id)
                if otp_response == 'STATUS_WAIT_CODE':
                    otp_response = None
                    random_time_delay(start=5,end=15)
                elif otp_response.startswith('STATUS_OK'):
                    otp = otp_response.split(":")[1]
                    break
                
            # Return False as user was not created
            if not otp:
                flag=True
                driver.find_element(By.XPATH, "//span[text()='Get new code']").click()
                random_time_delay(start=5,end=9)
                driver.find_element(By.XPATH, ".//input[@id='phoneNumberId']").clear()

            else:
                flag=False
        
        driver.find_element(By.XPATH,"//span[text()='G-']/../div/input").send_keys(otp)
        driver.find_element(By.XPATH,"//span[text()='G-']/../div/input").send_keys(Keys.ENTER)

        random_time_delay()
        
        driver.find_element(By.XPATH,"//input[@id='recoveryEmailId']").click()
        driver.switch_to.active_element.send_keys(Keys.TAB)
        driver.switch_to.active_element.send_keys(Keys.TAB)
        driver.switch_to.active_element.click()
        
        try:
            driver.find_element(By.XPATH,"//button/span[text()='Skip']").click()
        except Exception as e:
            pass
            
        try:
            driver.find_element(By.XPATH,"//button/span[text()='Next']").click()
        except Exception as e:
            pass

        random_time_delay()
        
        # driver.find_element(By.XPATH,"//button[contains(@jsaction,'mouseenter')]").click()
    
        # random_time_delay()
        
        driver.find_element(By.XPATH, "//span[text()='I agree']").click()
        
    except:
        return False
    
    return True

if __name__ == '__main__':
    
    account_count = 1
    max_accounts = 10
    while account_count <= max_accounts:
        
        try:
            try:
                driver.quit()
            except Exception as e:
                pass

            driver = open_browser(proxy=True)
            go_to_gmail_account(driver)
            go_to_account_signup(driver)
            user_info = generate_user_info()
            account_created = False
            try:
                account_created = create_account(driver, user_info)
            except Exception as e:
                pass
            if account_created:
                account_count += 1
                create_gmail_user_in_db(user_info)
    
        except Exception as e:
            pass