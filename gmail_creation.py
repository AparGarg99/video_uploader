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


db_params = {
    'host': 'opraah-database.c9qouuiwyuwx.ap-south-1.rds.amazonaws.com',
    'database': 'opraah',
    'user': 'postgres',
    'password': 'VUFPZaluUQk',
    'port': '5432'
}

min_wait_time = 5
max_wait_time = 7
email=""
password = "Opraahfx@1234"

def open_browser(driver_version='120.0.6099.234', headless=False, user_agent=False, proxy=None, download_directory=None):
    chrome_service = ChromeService(ChromeDriverManager(driver_version=driver_version).install())
    
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.binary_location = chrome_binary_path
    
    chrome_options.add_argument("--window-size=1920,1080")
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
        chrome_options.add_argument(f"--load-extension=./proxy_isp")  
    if download_directory:
        preferences = {"download.default_directory": download_directory}
        chrome_options.add_experimental_option("prefs", preferences)
    
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    return driver



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
    
    firstnames = ["Umesh","Mukesh","Jignesh","Chirag"]
    lastnames = ["Mittal","Bansal","Aggarwal","Rathore"]
    
    firstname = firstnames[random.randint(0,len(firstnames)-1)].lower()
    lastname = lastnames[random.randint(0,len(lastnames)-1)].lower()

    unique_id = str(int(time.time()))
    email_id = "{firstname}{lastname}{unique_id}@gmail.com".format(firstname=firstname, lastname=lastname, unique_id=unique_id)

    random_time_delay(2,4)
    
    # month_dropdown = Select(driver.find_element(By.ID, "month"))
    # month_dropdown.select_by_visible_text("Feburary")
    # driver.find_element(By.ID, "day").send_keys("11")
    # driver.find_element(By.ID, "day").send_keys("11")
    # gender_dropdown = Select(driver.find_element(By.ID, "gender"))
    # gender_dropdown.select_by_visible_text("Male")
    # driver.find_element(By.ID, "day").send_keys(Keys.ENTER)
    info = {
        'firstname':firstname, 
        'lastname':lastname,
        'month': 'February',
        'day': '11',
        'gender': 'Male',
        'year': 1992,
        'email_id': email_id
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

    month_dropdown = Select(driver.find_element(By.ID, "month"))
    month_dropdown.select_by_visible_text(month)
    driver.find_element(By.ID, "day").send_keys(day)
    driver.find_element(By.ID, "year").send_keys(year)
    gender_dropdown = Select(driver.find_element(By.ID, "gender"))
    gender_dropdown.select_by_visible_text(gender)
    driver.find_element(By.ID, "day").send_keys(Keys.ENTER)
    flag = False
    try:
        driver.find_element(By.XPATH, "//div[text()='Create your own Gmail address']").click()
    except:
        flag = True
    driver.find_element(By.XPATH, "//input[@name='Username']").send_keys(email_id.split("@")[0])
    driver.find_element(By.XPATH, "//input[@name='Username']").send_keys(Keys.ENTER)
    driver.find_element(By.XPATH, "//input[@type='password']").send_keys(password)
    driver.find_element(By.XPATH, "//input[@type='password']").send_keys(Keys.TAB)
    driver.switch_to.active_element.send_keys(password)
    driver.switch_to.active_element.send_keys(Keys.ENTER)
    return driver

if __name__ == '__main__':
    
    for i in range(1):
        
        try:
            try:
                driver.quit()
            except Exception as e:
                pass

            driver = open_browser(proxy=True)
            go_to_gmail_account(driver)
            go_to_account_signup(driver)
            user_info = generate_user_info()
            create_account(driver, user_info)
            
    
        except Exception as e:
            pass