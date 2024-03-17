#%%
import os
CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
os.chdir(CURRENT_FOLDER)

#%%
import random
import string
import tempfile
import time
from fake_useragent import UserAgent
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from smsactivate.api import SMSActivateAPI
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
import re
import os
from dotenv import load_dotenv
import pyperclip
import easyocr
load_dotenv()

#%%

USE_PROXY = False
USE_TEMP_MAIL = True
USE_SMS_ACTIVE = False

DB_HOST = os.getenv("DB_HOST")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = int(os.getenv('DB_PORT'))
APIKEY = os.getenv('API_KEY')

min_wait_time = 5
max_wait_time = 7

max_accounts = 10

#%%

db_params = {
    'host': DB_HOST,
    'database': DB_DATABASE,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'port': DB_PORT,
}

connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=1,
    **db_params
)

#%%

############################# DB UTILS #############################
@contextmanager
def connect_to_database():
    connection = connection_pool.getconn()
    try:
        # Provide the connection to the caller
        yield connection
    finally:
        # Release the connection back to the pool
        connection_pool.putconn(connection)



def create_insta_user_in_db(user_info):
    try:
        # Connect to the database using the context manager
        with connect_to_database() as connection:
            # Create a cursor to interact with the database
            with connection.cursor() as cursor:
                # SQL query to select a user with less than three videos uploaded
                insert_query = """
                    INSERT INTO public.insta_accounts 
                    (email, "password", in_use, last_used, videos_uploaded) 
                    VALUES (%s, %s, false, CURRENT_TIMESTAMP, 0);
                """

                # Execute the SELECT query
                cursor.execute(insert_query, (user_info['email'], user_info['password']))
                connection.commit()
    except Exception as e:
        pass



############################# SELENIUM UTILS #############################
def open_browser(user_agent=False, proxy=False):
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--enable-clipboard")
    if user_agent:
        ua = UserAgent()
        user_agent = ua.random
        chrome_options.add_argument(f'user-agent={user_agent}')
    if proxy:
        chrome_options.add_argument(f"--load-extension={CURRENT_FOLDER}/proxies/proxy_isp")
    driver = webdriver.Chrome(options=chrome_options)
    return driver



def random_time_delay(start=10, end=20):
    time.sleep(random.uniform(start, end))



def go_to_instagram_signup(driver):
    driver.get('https://www.instagram.com')
    random_time_delay(min_wait_time*2, max_wait_time*2)

    try:
        driver.find_element(By.XPATH, "//*[text()='Decline optional cookies']").click()
    except Exception:
        pass
    try:
        driver.find_element(By.XPATH, "//button[text()='Sign Up']").click()
    except Exception as e:
        driver.find_element(By.XPATH, "//a[@href='/accounts/emailsignup/']").click()

    random_time_delay(min_wait_time*2, max_wait_time*2)

    return driver



############################# SMSActivateAPI for Phone Number #############################
# def get_phone_sms_activate():
#     sa = SMSActivateAPI(APIKEY)
#     sa_response = sa.getNumber(service='ig',country=22)
#     return sa_response


# def get_phone_otp_sms_activate(activation_code):
#     sa = SMSActivateAPI(APIKEY)
#     sa_response = sa.getStatus(id=activation_code)
#     return sa_response



############################# SMSActivateAPI for EmailID #############################
def get_email_sms_activate():
    email_url = 'https://api.sms-activate.org/stubs/handler_api.php?api_key={}&action=buyMailActivation&site=instagram.com&mail_type=2&mail_domain=hotmail.com'.format(APIKEY)
    sa_response = requests.get(email_url)
    return sa_response



def get_otp_sms_activate(activation_id):
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



############################# TempMail for EmailID #############################
def get_email_tempmail(driver):
    driver.get('https://temp-mail.org/en/')
    random_time_delay(min_wait_time*2, max_wait_time*2)

    try:
        driver.find_element(By.XPATH, '//*[@id="tm-body"]/div[1]/div/div/div[2]/div[1]/form/div[2]/button').click()
        random_time_delay(min_wait_time, max_wait_time)
        email_id = pyperclip.paste()

    except Exception as e:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            ## Save screenshot in the temporary file
            temp_filename = temp_file.name
            driver.save_screenshot(temp_filename)

            ## Use EasyOCR to read text from the screenshot
            reader = easyocr.Reader(['en'], gpu=False)
            result = reader.readtext(temp_filename)

        extracted_text = ' '.join([entry[1] for entry in result])
        email_id = f"{next(i for i in extracted_text.split() if '@' in i)}"
        if not email_id.endswith(".com"):
            email_id += ".com"

    return email_id



def get_otp_tempmail(temp_mail_driver):
    try:
        temp_mail_driver.execute_script("window.scrollBy(0, 700);")
        random_time_delay(min_wait_time, max_wait_time)
                
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            ## Save screenshot in the temporary file
            temp_filename = temp_file.name
            temp_mail_driver.save_screenshot(temp_filename)
        
            ## Use EasyOCR to read text from the screenshot
            reader = easyocr.Reader(['en'], gpu=False)
            result = reader.readtext(temp_filename)
        
        extracted_text = ' '.join([entry[1] for entry in result])
        otp = re.search(r'\b\d{6}\b', extracted_text).group()
        return otp
            
    except Exception as e:
        return None



############################# GENERAL UTILS #############################
def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation  
    password = ''.join(random.choice(characters) for i in range(length))
    return password



def generate_user_info():
    firstnames = ["Bibek","Vivek","Jignesh","Chirag","Jignesh","Raul","Vivek","Mayank","Nipendra","Nishant"]
    lastnames = ["Mittal","Bansal","Aggarwal","Rathore","Bhola","Kalwar","Gupta","Garg"]
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    
    firstname = firstnames[random.randint(0,len(firstnames)-1)]
    lastname = lastnames[random.randint(0,len(lastnames)-1)]
    year = random.randint(1980, 1998)  # Random year between 1950 and 2005
    month = random.choice(months)      # Random month from the list of months
    day = random.randint(1, 28)         # Random day between 1 and 28 (assuming February)
    password = generate_random_password()
    unique_id = str(int(time.time()))
    
    info = {
        'firstname': firstname, 
        'lastname': lastname,
        'year': str(year),
        'month': month,
        'day': str(day),
        'user_name': firstname + "_" + lastname + "_" + unique_id[:4:-1],
        'password':password
    }
    return info



############################# MAIN FUNCTION #############################
def create_account(driver, user_info):
    try:
        email = ""
        otp = None
        
        if USE_SMS_ACTIVE and USE_TEMP_MAIL:
            print("#### CANNOT USE BOTH SMS-ACTIVE and TEMP-MAIL ####")
            return False
    
        
        if USE_SMS_ACTIVE:
            email_info = get_email_sms_activate()
            email_info_response = email_info.json()['response']
            email = email_info_response['email']
            activation_id = email_info_response['id']
            user_info['email'] = email
            user_info['activation_id'] = activation_id
    
    
        if USE_TEMP_MAIL:
            temp_mail_driver = open_browser(user_agent=False, proxy=False)
            random_time_delay(min_wait_time, max_wait_time)
            email = get_email_tempmail(temp_mail_driver)
            user_info['email'] = email
    
    
        go_to_instagram_signup(driver)
        random_time_delay(min_wait_time, max_wait_time)
        driver.find_element(By.XPATH, "//input[@name='emailOrPhone']").send_keys(user_info['email'])
        random_time_delay(min_wait_time, max_wait_time)
        driver.find_element(By.XPATH, "//input[@name='fullName']").send_keys(user_info['firstname']+" "+user_info['lastname'])
        random_time_delay(min_wait_time, max_wait_time)
        driver.find_element(By.XPATH, "//input[@name='username']").send_keys(user_info['user_name'])
        random_time_delay(min_wait_time, max_wait_time)
        driver.find_element(By.XPATH, "//input[@name='password']").send_keys(user_info['password'])
        random_time_delay(min_wait_time, max_wait_time)
        driver.find_element(By.XPATH, "//*[text()='Sign up']").click()
        random_time_delay(min_wait_time*2, max_wait_time*2)
        
        month_dropdown = Select(driver.find_element(By.XPATH, "//select[@title='Month:']"))
        month_dropdown.select_by_visible_text(user_info['month'])
        random_time_delay(min_wait_time, max_wait_time)
        day_dropdown = Select(driver.find_element(By.XPATH, "//select[@title='Day:']"))
        day_dropdown.select_by_visible_text(user_info['day'])
        random_time_delay(min_wait_time, max_wait_time)
        year_dropdown = Select(driver.find_element(By.XPATH, "//select[@title='Year:']"))
        year_dropdown.select_by_visible_text(user_info['year'])
        random_time_delay(min_wait_time, max_wait_time)
        driver.find_element(By.XPATH, "//*[text()='Next']").click()
        random_time_delay(min_wait_time*2, max_wait_time*2)
    
    
        if USE_SMS_ACTIVE:
            for _ in range(5):
                try:
                    otp = get_otp_sms_activate(user_info['activation_id'])
                    if otp is None:
                        random_time_delay(min_wait_time*3, max_wait_time*3)
                        continue
                    break
                except Exception as e:
                    pass
        
        
        if USE_TEMP_MAIL:
            random_time_delay(min_wait_time, max_wait_time)
            for _ in range(5):
                try:
                    otp = get_otp_tempmail(temp_mail_driver)
                    if otp is None:
                        random_time_delay(min_wait_time*3, max_wait_time*3)
                        continue
                    break
                except Exception as e:
                    pass
        
        
        random_time_delay(min_wait_time,max_wait_time)
        driver.find_element(By.NAME, "email_confirmation_code").send_keys(otp)
        random_time_delay(min_wait_time*3,max_wait_time*3)
        driver.find_element(By.XPATH, "//*[text()='Confirm']").click()
        random_time_delay(min_wait_time*3,max_wait_time*3)
    
        return True, user_info
    
    except Exception as e:
        print(e)
        return False, user_info


#%%

if __name__ == '__main__':
    
    account_count = 1
    while account_count <= max_accounts:
        try:
            try:
                driver.quit()
            except Exception as e:
                pass

            driver = open_browser(user_agent=True, proxy=USE_PROXY)
            
            user_info = generate_user_info()
            
            account_created, user_info = create_account(driver, user_info)
            
            if account_created:
                print(f'No. of accounts created: {account_count}')
                account_count += 1
                create_insta_user_in_db(user_info)

        except Exception as e:
            pass
        
        finally:
            random_time_delay(min_wait_time*10,max_wait_time*10)

    print(f'Total no. of accounts created: {account_count}')