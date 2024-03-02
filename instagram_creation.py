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
import re

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

def get_gmail_account():
    try:
        # Connect to the database using the context manager
        with connect_to_database() as connection:
            # Create a cursor to interact with the database
            with connection.cursor() as cursor:
                # SQL query to select a user with less than three videos uploaded
                select_query = """
                SELECT email, password, videos_uploaded
                FROM public.youtube_accounts
                WHERE insta_account = False
                ORDER BY last_used ASC
                LIMIT 1
                FOR UPDATE SKIP LOCKED;
                """

                # Execute the SELECT query
                cursor.execute(select_query)

                # Fetch the selected user
                user = cursor.fetchone()

                return user

    except Exception as e:
        # Handle any exceptions
        print(f"Error: {e}")
        return None


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
    # chrome_options.add_argument("--incognito")  # Start Chrome in incognito mode
    #chrome_options.add_argument("--disable-geolocation")  # Disable geolocation in Chrome
    chrome_options.add_argument('--disable-web-security')
    
    if headless:
        chrome_options.add_argument("--headless")
    if user_agent:
        ua = UserAgent()
        user_agent = ua.chrome + ' ' + ua.os_linux
        chrome_options.add_argument(f'user-agent={user_agent}')
    if proxy:
        chrome_options.add_argument(f"--load-extension=./proxy_auth_plugin")  
    if download_directory:
        preferences = {"download.default_directory": download_directory}
        chrome_options.add_experimental_option("prefs", preferences)
    
    driver = webdriver.Chrome(options=chrome_options)
    # driver = webdriver.Edge(service=edge_service)
    return driver

def get_number():
    sa = SMSActivateAPI(APIKEY)
    sa_response = sa.getNumber(service='ig',country=22)
    return sa_response

def get_otp(activation_code):
    sa = SMSActivateAPI(APIKEY)
    sa_response = sa.getStatus(id=activation_code)
    return sa_response

def random_time_delay(start=10, end=20):
    time.sleep(random.uniform(start, end))

def generate_user_info():
    
    firstnames = ["Umesh","Mukesh","Jignesh","Chirag","Jignesh","Raul","Vivek","Mayank","Nipendra"]
    lastnames = ["Mittal","Bansal","Aggarwal","Rathore","Bhola","Kalwar","Gupta"]
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    firstname = firstnames[random.randint(0,len(firstnames)-1)].lower()
    lastname = lastnames[random.randint(0,len(lastnames)-1)].lower()

    unique_id = str(int(time.time()))

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
        'user_name': firstname + unique_id + lastname,
        'number': '',
        'activation_id': '',
    }
    
    return info


def go_to_instagram_signup(driver):
    
    driver.get('https://www.instagram.com/accounts/emailsignup/')
    
    return driver

def create_account(driver, user_info):
    
    gmail_account = get_gmail_account()
    email = gmail_account[0]
    password = gmail_account[1]
    # number_info = get_number()
    # number = str(number_info['phone'])
    # if not number.startswith("+"):
    #     number = '+' + number
    # activation_id = number_info['activation_id']
    
    
    driver.find_element(By.XPATH, "//input[@name='emailOrPhone']").send_keys(email)
    random_time_delay(start=1,end=3)
    driver.find_element(By.XPATH, "//input[@name='fullName']").send_keys(user_info['firstname']+" "+user_info['lastname'])
    random_time_delay(start=1,end=3)
    driver.find_element(By.XPATH, "//input[@name='username']").send_keys(user_info['user_name'])
    random_time_delay(start=1,end=3)
    driver.find_element(By.XPATH, "//input[@name='password']").send_keys(password)
    random_time_delay(start=1,end=3)
    driver.find_element(By.XPATH, "//button[text()='Sign Up' or text()='Next']").click()
    random_time_delay(start=4,end=7)
    month = user_info['month']
    day = user_info['day']
    gender = user_info['gender']
    year = user_info['year']
    month_dropdown = Select(driver.find_element(By.XPATH, "//select[@title='Month:']"))
    month_dropdown.select_by_visible_text(month)
    random_time_delay(start=5,end=8)
    day_dropdown = Select(driver.find_element(By.XPATH, "//select[@title='Day:']"))
    day_dropdown.select_by_visible_text(day)
    random_time_delay(start=5,end=8)
    year_dropdown = Select(driver.find_element(By.XPATH, "//select[@title='Year:']"))
    year_dropdown.select_by_visible_text(str(year))
    random_time_delay(start=5,end=8)
    driver.find_element(By.XPATH, "//button[text()='Next']").click()
    random_time_delay(start=5,end=8)
    
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get('https://www.gmail.com')
    driver.find_element(By.XPATH, "//a[text()='Sign in']").click()
    random_time_delay(start=5,end=8)
    driver.find_element(By.XPATH, "//input[@type='email']").send_keys(email)
    driver.find_element(By.XPATH, "//span[text()='Next']").click()
    random_time_delay(start=5,end=8)
    driver.find_element(By.XPATH, "//input[@type='password']").send_keys(password)
    driver.find_element(By.XPATH, "//span[text()='Next']").click()
    random_time_delay(start=5,end=8)
    try:
        driver.find_element(By.XPATH, "//span[text()='Not now']").click()
    except Exception as e:
        pass
    random_time_delay(start=5,end=8)
    driver.get('https://mail.google.com/mail/u/0/#inbox')
    random_time_delay(start=10,end=12)
    xpath_expression = f"//span[contains(text(),'{email}')]"
    element = driver.find_element(By.XPATH, xpath_expression)
    element_html = element.get_attribute("outerHTML")
    
    otp_pattern = re.compile(r'\b\d{6}\b')
    otp_match = re.search(otp_pattern, element_html)
    otp = otp_match.group()
    
    driver.switch_to.window(driver.window_handles[0])
    random_time_delay(1,3)
    driver.find_element(By.XPATH, "//input[@name='email_confirmation_code']").send_keys(otp)
    driver.find_element(By.XPATH, "//div[text()='Next']").click()
    # user_info['number'] = number
    # user_info['activation_id'] = activation_id
    
    start_time = datetime.now()
    otp_response = None
    otp = None
    # while datetime.now() < start_time + timedelta(minutes=3):
    #     otp_response = get_otp(activation_code=activation_id)
    #     if otp_response == 'STATUS_WAIT_CODE':
    #         otp_response = None
    #         random_time_delay(start=5,end=15)
    #     elif otp_response.startswith('STATUS_OK'):
    #         otp = otp_response.split(":")[1]
    #         break
    
    if not otp:
        return False
    
    driver.find_element(By.XPATH, "//input[@name='confirmationCode']").send_keys(otp)
    random_time_delay(start=5,end=8)
    driver.find_element(By.XPATH, "//button[text()='Confirm']").click()
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

            driver = open_browser()
            go_to_instagram_signup(driver)
            user_info = generate_user_info()
            account_created = False
            try:
                account_created = create_account(driver, user_info)
            except Exception as e:
                pass
            if account_created:
                account_count += 1
                # create_gmail_user_in_db(user_info)
    
        except Exception as e:
            pass