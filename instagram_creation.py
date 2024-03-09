import random
import string
import tempfile
import time
from fake_useragent import UserAgent
import requests
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.edge.service import Service
# from seleniumwire import webdriver
from selenium import webdriver
from datetime import datetime, timedelta
from smsactivate.api import SMSActivateAPI
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
import re

#tempmail imports
import pyperclip
import easyocr

APIKEY = '2417387b156062A9319d62191b4dcfAd'

USE_PROXY = False
USE_RANDOM_USER_AGENT = False
USE_TEMP_MAIL = True
USE_SMS_ACTIVE = False
USE_ANOTHER_BRWOSER_FOR_TEMP_MAIL = False
CLIPBOARD_FIRST = True

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
# password = "Opraahfx@1234"

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
                cursor.execute(insert_query, (user_info['email'], user_info['password'], user_info['number'], user_info['activation_id']))
                connection.commit()
    except Exception as e:
        pass

def open_new_browser(headless=False, user_agent=True, proxy=None, download_directory=None):

    # from seleniumwire import webdriver as wirewebdriver

    if proxy:
        options = {
            'proxy': {
                'http': 'http://krfYsk7fDNckFV7f:X90vuBO81YgGbVHu_session-9UDy8DOS_lifetime-30m_streaming-1@geo.iproyal.com:12321',
                'https': 'http://krfYsk7fDNckFV7f:X90vuBO81YgGbVHu_session-9UDy8DOS_lifetime-30m_streaming-1@geo.iproyal.com:12321',
            }
        }

        s_driver = webdriver.Chrome()
        return s_driver
    else:
        s_driver = webdriver.Chrome()
        return s_driver


def open_browser(headless=False, user_agent=False, proxy=None, download_directory=None):

    chrome_options = uc.ChromeOptions()
    # edge_options = webdriver.EdgeOptions()

    chrome_options.add_argument("--window-size=1920,1080")
    #chrome_options.add_argument("--start-minimized")  # Add this line to start in minimized mode
    # chrome_options.add_argument("--disable-extensions") # Disable Chrome extensions
    #chrome_options.add_argument('--disable-notifications') # Disable Chrome notifications
    chrome_options.add_argument("--mute-audio") # Mute system audio
    #chrome_options.add_argument('--disable-dev-shm-usage') # Disable the use of /dev/shm to store temporary data
    #chrome_options.add_argument('--ignore-certificate-errors') # Ignore certificate errors
    # chrome_options.add_argument("--incognito")  # Start Chrome in incognito mode
    #chrome_options.add_argument("--disable-geolocation")  # Disable geolocation in Chrome
    # chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument("--enable-clipboard")
    if headless:
        chrome_options.add_argument("--headless")
    if user_agent:
        ua = UserAgent()
        user_agent = ua.random
        chrome_options.add_argument(f'user-agent={user_agent}')
    if proxy:
        chrome_options.add_argument("--load-extension=./proxy_residential")  
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

def get_temp_email():

    email_url = 'https://api.sms-activate.org/stubs/handler_api.php?api_key={}&action=buyMailActivation&site=instagram.com&mail_type=2&mail_domain=hotmail.com'.format(APIKEY)

    sa_response = requests.get(email_url)
    return sa_response

def get_temp_email_otp(activation_id):
    # write code to get OTP via API using activation_id
    otp_url = 'https://api.sms-activate.org/stubs/handler_api.php?api_key={}&action=checkMailActivation&id={}'.format(APIKEY, activation_id)

    response = requests.get(otp_url, timeout=30)

    response_json = response.json()

    status = response_json.get('status',None)

    if status is None:
        return None

    email_response = response_json.get('response', None)

    if email_response is None:
        return None

    otp = email_response.get('value',None)    

    return otp

def get_otp(activation_code):
    sa = SMSActivateAPI(APIKEY)
    sa_response = sa.getStatus(id=activation_code)
    return sa_response

def random_time_delay(start=10, end=20):
    time.sleep(random.uniform(start, end))

def generate_user_info():
    
    firstnames = ["Bibek","Vivek","Jignesh","Chirag","Jignesh","Raul","Vivek","Mayank","Nipendra","Nishant"]
    lastnames = ["Mittal","Bansal","Aggarwal","Rathore","Bhola","Kalwar","Gupta","Garg"]
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    firstname = firstnames[random.randint(0,len(firstnames)-1)]
    lastname = lastnames[random.randint(0,len(lastnames)-1)]
    password = generate_random_password()
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
        'user_name': firstname + "_" + lastname + "_" + unique_id[:4:-1],
        'number': '',
        'activation_id': '',
        'password':password
    }
    
    return info

def go_to_instagram_signup(driver):

    driver.get('https://www.instagram.com')
    random_time_delay(min_wait_time, max_wait_time)
    random_time_delay(min_wait_time, max_wait_time)

    try:
        driver.find_element(By.XPATH, "//*[text()='Decline optional cookies']").click()
    except Exception:
        pass
    try:
        driver.find_element(By.XPATH, "//button[text()='Sign Up']").click()
    except Exception as e:
        driver.find_element(By.XPATH, "//a[@href='/accounts/emailsignup/']").click()

    random_time_delay(10, 12)
    random_time_delay(min_wait_time, max_wait_time)

    return driver

def get_from_email_from_temp_mail(driver):

    driver.get('https://temp-mail.org/en/')
    # random_time_delay(15, 20)

    if CLIPBOARD_FIRST:
        try:
            driver.find_element(By.XPATH, "//span[text()='Copy']").click()
            random_time_delay(min_wait_time, max_wait_time)
            random_time_delay(min_wait_time, max_wait_time)
            email_id = pyperclip.paste()

        except Exception as e:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as temp_file:
                ## Save screenshot in the temporary file
                temp_filename = temp_file.name
                driver.execute_script("window.scrollBy(0, 200);")
                driver.save_screenshot(temp_filename)

                ## Use EasyOCR to read text from the screenshot
                reader = easyocr.Reader(['en'], gpu=False)
                result = reader.readtext(temp_filename)

            extracted_text = ' '.join([entry[1] for entry in result])

            email_id = f"{next(i for i in extracted_text.split() if '@' in i)}"
            if not email_id.endswith(".com"):
                email_id += ".com"
    else:
        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as temp_file:
                ## Save screenshot in the temporary file
                temp_filename = temp_file.name
                driver.execute_script("window.scrollBy(0, 200);")
                driver.save_screenshot(temp_filename)

                ## Use EasyOCR to read text from the screenshot
                reader = easyocr.Reader(['en'], gpu=False)
                result = reader.readtext(temp_filename)

            extracted_text = ' '.join([entry[1] for entry in result])

            email_id = f"{next(i for i in extracted_text.split() if '@' in i)}"
            if not email_id.endswith(".com"):
                email_id += ".com"
        except Exception as e:
            # driver.find_element(By.XPATH, "//span[text()='Copy']").click()
            random_time_delay(min_wait_time, max_wait_time)
            random_time_delay(min_wait_time, max_wait_time)
            email_id = pyperclip.paste()

    random_time_delay(min_wait_time, max_wait_time)
    random_time_delay(min_wait_time, max_wait_time)

    return email_id

def generate_random_password(length=12):
    # Define the character set for the password
    # includes letters, digits, and punctuation symbols
    characters = string.ascii_letters + string.digits + string.punctuation  

    # Generate the password by randomly selecting characters from the character set
    password = ''.join(random.choice(characters) for i in range(length))

    return password

def create_account(driver, user_info):
    # VIA sms-activate API

    if USE_SMS_ACTIVE and USE_TEMP_MAIL:
        print("#### CANNOT USE BOTH SMS-ACTIVE and TEMP-MAIL ####")
        return False

    if USE_SMS_ACTIVE:
        email_info = get_temp_email()
        email_info_response = email_info.json()['response']
        email = email_info_response['email']
        activation_id = email_info_response['id']

        user_info['email'] = email
        user_info['activation_id'] = activation_id

    if USE_TEMP_MAIL:
    ## via temp mail
        if USE_ANOTHER_BRWOSER_FOR_TEMP_MAIL:
            another_driver = open_new_browser()
            email = get_from_email_from_temp_mail(another_driver)
            user_info['email'] = email
        else:
            email = get_from_email_from_temp_mail(driver)
            ## create new window for instagram
            driver.execute_script("window.open('about:blank', '_blank');")
            random_time_delay(min_wait_time, max_wait_time)
            driver.switch_to.window(driver.window_handles[-1])

            user_info['email'] = email

    go_to_instagram_signup(driver)
    random_time_delay(min_wait_time, max_wait_time)

    driver.find_element(By.XPATH, "//input[@name='emailOrPhone']").send_keys(user_info['email'])
    random_time_delay(start=1,end=3)
    driver.find_element(By.XPATH, "//input[@name='fullName']").send_keys(user_info['firstname']+" "+user_info['lastname'])
    random_time_delay(start=1,end=3)
    driver.find_element(By.XPATH, "//input[@name='username']").send_keys(user_info['user_name'])
    random_time_delay(start=1,end=3)
    driver.find_element(By.XPATH, "//input[@name='password']").send_keys(user_info['password'])
    random_time_delay(start=1,end=3)
    random_time_delay(start=7,end=11)
    driver.find_element(By.XPATH, "//button[text()='Sign Up' or text()='Next']").click()
    random_time_delay(start=4,end=7)
    # random_time_delay(start=4,end=7)
    random_time_delay(start=7,end=11)
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
    driver.find_element(By.XPATH, "//button[text()='Next' or text()='Sign Up']").click()
    random_time_delay(start=5,end=8)


    otp = None
    start_time = datetime.now()

    # VIA TEMP Mail
    if USE_TEMP_MAIL:
        # driver.execute_script("window.open('about:blank', '_blank');")
        temp_mail_driver = driver
        if USE_ANOTHER_BRWOSER_FOR_TEMP_MAIL:
            temp_mail_driver = another_driver
        else:
            temp_mail_driver.switch_to.window(temp_mail_driver.window_handles[0])
        random_time_delay(15, 20)
        while datetime.now() < start_time + timedelta(minutes=10):
            temp_mail_driver.execute_script("window.scrollBy(0, 700);")
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                ## Save screenshot in the temporary file
                temp_filename = temp_file.name
                temp_mail_driver.save_screenshot(temp_filename)

            ## Use EasyOCR to read text from the screenshot
                reader = easyocr.Reader(['en'], gpu=False)
                result = reader.readtext(temp_filename)

            extracted_text = ' '.join([entry[1] for entry in result])
            otp = re.search(r'\b\d{6}\b', extracted_text).group()
            if otp is None:
                random_time_delay(start=25,end=35)
                continue
            break
        if USE_ANOTHER_BRWOSER_FOR_TEMP_MAIL:
            driver.find_element(By.XPATH, "//input[@name='confirmationCode' or @name='email_confirmation_code']").send_keys(otp)
        else:
            temp_mail_driver.switch_to.window(driver.window_handles[-1])
        random_time_delay(start=5,end=8)
    if USE_SMS_ACTIVE:
    # For SMS-Activate API
        while datetime.now() <= start_time + timedelta(minutes=15):
            try:
                otp = get_temp_email_otp(user_info['activation_id'])
                if otp is None:
                    random_time_delay(start=25,end=35)
                    continue
                break
            except Exception as e:
                pass    
        random_time_delay(start=25,end=35)

    driver.find_element(By.XPATH, "//input[@name='confirmationCode' or @name='email_confirmation_code']").send_keys(otp)
    random_time_delay(start=5,end=8)

    try:
        driver.find_element(By.XPATH, "//*[text()='Confirm' or text()='Next']").click()
        random_time_delay(min_wait_time,max_wait_time)
    except Exception as e:
        pass
    try:
        try:
            driver.find_element(By.XPATH, "//*[text()='Not Now']").click()
            random_time_delay(min_wait_time, max_wait_time)
        except:
            pass

        random_time_delay(min_wait_time,max_wait_time)
        driver.find_element(By.XPATH,"//span[text()='Suggested for you']")
    except Exception as e:
        return False
    return True

if __name__ == '__main__':


    account_count = 1
    max_accounts = 10000
    flag = True

    while account_count <= max_accounts and flag:

        try:
            try:
                driver.quit()
            except Exception as e:
                pass

            driver = open_browser(user_agent=USE_RANDOM_USER_AGENT, proxy=USE_PROXY)
            # go_to_instagram_signup(driver)
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
        finally:
            random_time_delay(300,600)

    print("Accounts created: ",account_count)