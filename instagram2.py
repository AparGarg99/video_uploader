from contextlib import contextmanager
import os
#CURRENT_FOLDER = r'C:\Users\aparg\Desktop\opraahfx'
# CURRENT_FOLDER = r'C:\Users\apar\Desktop\oprahfx'
CURRENT_FOLDER = './'
os.chdir(CURRENT_FOLDER)

from datetime import date, datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from selenium.webdriver.common.by import By
import pandas as pd
import random
import time
from selenium import webdriver
import psycopg2
from psycopg2 import pool
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from fake_useragent import UserAgent
#%%

#################### User input ####################
min_wait_time = 5
max_wait_time = 7

videos_per_account = 1

#################### File paths ####################
curr_date = date.today().strftime("%d-%m-%Y")

PATH_DICT = {
    'PROJECT_DIR': CURRENT_FOLDER,
    
    'ORIGINAL_VIDEO_DIR': os.path.join(CURRENT_FOLDER, 'input', 'videos'),
    'ACCOUNT_FILE': os.path.join(CURRENT_FOLDER, 'input', 'gmail_accounts_5.csv'),
    'VIDEO_METADATA_FILE': os.path.join(CURRENT_FOLDER, 'input', 'video_metadata.csv'),
    
    'OUTPUT_DIR':  os.path.join(CURRENT_FOLDER, f'output_{curr_date}'),
    'OUTPUT_FILE':  os.path.join(CURRENT_FOLDER, f'output_{curr_date}', 'output_instagram.csv')
    }

db_params = {
    'host': 'opraah-database.c9qouuiwyuwx.ap-south-1.rds.amazonaws.com',
    'database': 'opraah',
    'user': 'postgres',
    'password': 'VUFPZaluUQk',
    'port': '5432'
}

#%%


def open_browser(driver_version='120.0.6099.234', headless=False, user_agent=True, proxy=None, download_directory=None):
    chrome_service = ChromeService(ChromeDriverManager(driver_version=driver_version).install())
    
    chrome_options = uc.ChromeOptions()
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
        chrome_options.add_argument(f"--load-extension=./proxy_auth_plugin")  
    if download_directory:
        preferences = {"download.default_directory": download_directory}
        chrome_options.add_experimental_option("prefs", preferences)
    
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    # driver.execute_script("return document.querySelector('extensions-manager').shadowRoot.querySelector('#viewManager > extensions-detail-view.active').shadowRoot.querySelector('div#container.page-container > div.page-content > div#options-section extensions-toggle-row#allow-incognito').shadowRoot.querySelector('label#label input').click()")

    return driver


# random time delay between requests (anti-blocking technique)
def random_time_delay(start=10, end=20):
    time.sleep(random.uniform(start, end))
    


def download_video(gdrive_file_url, output_filename):
    try:
        # Authenticate with your Google Drive credentials
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()  # Opens a web page to authenticate
        drive = GoogleDrive(gauth)
    
        # Extract the file ID from the URL
        file_id = gdrive_file_url.split("/")[-2]
    
        # Get the file
        file = drive.CreateFile({'id': file_id})
        file.GetContentFile(output_filename)
    
        return True
    
    except Exception as e:
        print("Video download failed - ", str(e))
        return False

def go_to_homepage(driver):
    # go to homepage
    driver.get("https://www.instagram.com")

    # wait to load
    random_time_delay(min_wait_time, max_wait_time)
    
    
    # Click on cookies
    try:
        driver.find_element(By.XPATH, "//button[text()='Allow all cookies']").click()
    except:
        pass
    
    # Skip turn on notifications page (if appears)
    for _ in range(4):
        try:
            driver.find_element(By.XPATH, "//*[text()='Not Now']").click()
            random_time_delay(min_wait_time, max_wait_time)
        except:
            pass

def login(driver, email_id, password):
    try:
        # We need this when we work with multiple accounts 
        driver.delete_all_cookies()
        
        # go to homepage
        go_to_homepage(driver)

        # Locate the email input field and enter your email
        driver.find_element(By.NAME, "username").send_keys(email_id)

        # Locate the password input field and enter your password
        driver.find_element(By.NAME, "password").send_keys(password)

        # Click the "Next" button to log in
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # wait to load
        random_time_delay(min_wait_time, max_wait_time)
        
        # go to homepage
        go_to_homepage(driver)
        
        return True

    except Exception as e:
        print("Login Error - ", str(e))
        return False
    

def go_to_upload_page():
    try:
        # Click on 'Create' button in top right corner
        driver.find_element(By.CSS_SELECTOR, 'svg[aria-label="New post"]').click()
        
        # wait to load
        random_time_delay(min_wait_time, max_wait_time)
        
        return True
        
    except Exception as e:
        print("Open upload page failed - ", str(e))
        return False


def select_file(video_path):
    try:
        absolute_path = os.path.abspath(video_path)
        # Click on 'Select files' button to choose files from desktop
        driver.find_element(By.CSS_SELECTOR, "input[type='file']").send_keys(absolute_path)
        
        # wait to load
        random_time_delay(min_wait_time, max_wait_time)
        
        # wait to load
        random_time_delay(min_wait_time*2, max_wait_time*2)
        
        return True
    
    except Exception as e:
        print("File selection failed - ", str(e))
        return False



def upload_video(captions):
    try:
        # Info box - Video posts are now shared as reels
        try:
            driver.find_element(By.XPATH, "//*[text()='OK']").click()
            random_time_delay(min_wait_time, max_wait_time)
        except:
            pass
        
        # Click on 'Next' button to go to next page
        for _ in range(2):
            driver.find_element(By.XPATH, "//*[text()='Next']").click()
            random_time_delay(min_wait_time, max_wait_time)

        # Input captions
        driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Write a caption..."]').send_keys(captions)

        # Publish video
        driver.find_element(By.XPATH, "//*[text()='Share']").click()
        
        # wait until reel is shared
        while True:
            try:
                driver.find_element(By.XPATH, "//*[text()='Reel shared']")
                break
            except:
                random_time_delay(min_wait_time, max_wait_time)
                pass
            
        return True
    
    except Exception as e:
        print("Video upload failed - ", str(e))
        return False



def logout(driver):
    try:
        # go to homepage
        go_to_homepage(driver)
        
        # click on 'Settings' button
        driver.find_element(By.CSS_SELECTOR, 'svg[aria-label="Settings').click()
        
        # wait to load
        random_time_delay(min_wait_time, max_wait_time)
        
        # click on 'Sign out'
        driver.find_element(By.XPATH, "//*[text()='Log out']").click()
                
        # wait to load
        random_time_delay(min_wait_time, max_wait_time)
        
        return True
    
    except Exception as e:
        print("Logout Error - ", str(e))
        return False

max_connections = 1

connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=max_connections,
    **db_params
)

@contextmanager
def connect_to_database():
    connection = connection_pool.getconn()

    try:
        yield connection  # Provide the connection to the caller
    finally:
        connection_pool.putconn(connection)  # Release the connection back to the pool


def get_and_update_user():
    try:
        # Connect to the database using the context manager
        with connect_to_database() as connection:
            # Create a cursor to interact with the database
            with connection.cursor() as cursor:
                # SQL query to select a user with less than three videos uploaded
                select_query = """
                SELECT email, password, videos_uploaded
                FROM public.insta_accounts
                WHERE videos_uploaded < 3
                AND
                in_use = False
                ORDER BY last_used ASC
                LIMIT 1
                FOR UPDATE SKIP LOCKED;
                """

                # Execute the SELECT query
                cursor.execute(select_query)

                # Fetch the selected user
                user = cursor.fetchone()

                if user:
                    # Extract user information
                    email, password, videos_uploaded = user

                    # Update the in_use value and last_used timestamp
                    update_query = """
                    UPDATE public.insta_accounts
                    SET in_use = true, last_used = %s
                    WHERE email = %s;
                    """

                    # Execute the UPDATE query
                    cursor.execute(update_query, (datetime.now(), email))

                    # Commit the changes to the database
                    connection.commit()

                    print(f"User {email} is now in use.")

                    # Return information about the updated user
                    return {'email': email, 'password': password, 'videos_uploaded': videos_uploaded}

                else:
                    print("No eligible user found.")
                    return None

    except Exception as e:
        # Handle any exceptions
        print(f"Error: {e}")
        return None

def fetch_video():
    try:
        # Connect to the database using the context manager
        with connect_to_database() as connection:
            # Create a cursor to interact with the database
            with connection.cursor() as cursor:
                # SQL query to fetch one record with status 'NOT PROCESSED' from video_metadata table
                select_query = """
                SELECT * FROM public.insta_video_metadata WHERE is_processed = 'NOT PROCESSED' LIMIT 1;
                """

                # Execute the SELECT query
                cursor.execute(select_query)

                # Fetch one record
                record = cursor.fetchone()

                if record:
                    url, title, tags, description, is_processed = record
                    result_dict = {'url': url, 'title': title, 'tags': tags, 'description': description, 'is_processed': is_processed}
                    print("Fetched record:", result_dict)
                    return result_dict

                else:
                    print("No records with status 'NOT PROCESSED' found.")
                    return None

    except Exception as e:
        # Handle any exceptions
        print(f"Error: {e}")
        return None

def update_is_processed(url, new_status='DOWNLOADING'):
    try:
        # Connect to the database using the context manager
        with connect_to_database() as connection:
            # Create a cursor to interact with the database
            with connection.cursor() as cursor:
                # SQL UPDATE statement to set 'is_processed' to 'downloaded' based on exact URL match
                update_query = """
                    UPDATE public.insta_video_metadata
                    SET is_processed = %s
                    WHERE url = %s;
                """

                # Execute the UPDATE query
                cursor.execute(update_query, (new_status, url))

                # Commit the changes to the database
                connection.commit()

                print(f"Updated 'is_processed' to '{new_status}' for URL '{url}'.")

    except Exception as e:
        # Handle any exceptions
        print(f"Error: {e}")

def update_user_video_count(email, video_count):
    try:
        # Connect to the database using the context manager
        with connect_to_database() as connection:
            # Create a cursor to interact with the database
            with connection.cursor() as cursor:
                # SQL UPDATE statement to set 'is_processed' to 'downloaded' based on exact URL match
                update_query = """
                    UPDATE public.insta_accounts
                    SET videos_uploaded = %s,
                    in_use = False
                    WHERE email = %s;
                """

                # Execute the UPDATE query
                cursor.execute(update_query, (video_count, email))

                # Commit the changes to the database
                connection.commit()

                print(f"Updated 'videos_uploaded' to '{video_count}' for email '{email}'.")

    except Exception as e:
        # Handle any exceptions
        print(f"Error: {e}")

def extract_file_id(google_drive_link):
    link_parts = google_drive_link.split('/')
    # Extract the file ID from the next part in the link
    file_id = link_parts[-2]

    return file_id

def check_file_exists(file_path):
    return os.path.exists(file_path)

#%%
if __name__=='__main__':
    
    for key, val in PATH_DICT.items():
        if 'DIR' in key:
            os.makedirs(val, exist_ok=True)

    while True:
        try:
            current_login = ''
            user_info = get_and_update_user()
            video_info = None
            if user_info:
                video_info = fetch_video()

            if user_info is None:
                print("No user available")
            elif video_info is None:
                print("No video available")
            else:                
                email = user_info['email']
                password = user_info['password']
                user_videos_uploaded = user_info['videos_uploaded']
                title = video_info['title']
                description = video_info['description']
                tags = ','.join(video_info['tags'].split(",")[:10])
                is_processed = video_info['is_processed']
                video_url = video_info['url']
                file_name = extract_file_id(video_url)
                output_filepath = os.path.join(PATH_DICT['ORIGINAL_VIDEO_DIR'], file_name+'.mp4')
                file_path = output_filepath
                # Update it to downloading
                update_is_processed(video_url)
                if not check_file_exists(output_filepath):
                    download_video(video_url, output_filepath)
                if email != current_login:

                    try:
                        logout_status = logout(driver)
                        driver.quit()
                    except:
                        pass

                    driver = open_browser(proxy=True)
                    # try login - can be successful or failed
                    login_status = login(driver, email, password)
                    current_login = email

                # If encountered account before, then
                else:
                    # If login to account was successful, go to homepage
                    if login_status:
                        go_to_homepage(driver)

                    # If login to account was failed, then skip task
                    else:
                        continue

                # If login to current account successful, then proceed to upload
                if login_status:
                    go_to_upload_page_status = go_to_upload_page()
                    
                    select_file_status = select_file(os.path.join(PATH_DICT['ORIGINAL_VIDEO_DIR'], file_name+'.mp4'))
                    upload_status = upload_video(captions=title)
                    if upload_status:
                        update_is_processed(video_url,'DONE')
                        update_user_video_count(email,user_videos_uploaded+1)
                    else:
                        update_is_processed(video_url,'NOT PROCESSED')
                        update_user_video_count(email,user_videos_uploaded)
                else:
                    update_is_processed(video_url,'NOT PROCESSED')
                    update_user_video_count(email,user_videos_uploaded)
                try:
                    driver.quit()
                except:
                    pass

        except Exception as e:
            update_is_processed(video_url,'NOT PROCESSED')
            update_user_video_count(email,user_videos_uploaded)
            try:
                driver.quit()
            except:
                pass
        finally:
            try:
                if file_path:
                    os.remove(file_path)
                    print(f"File '{file_path}' deleted successfully.")
            except Exception as e:
                print(f"Error deleting file '{file_path}': {e}")
            random_time_delay(min_wait_time, max_wait_time)