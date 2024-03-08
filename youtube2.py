import os
from urllib.parse import parse_qs, urlparse
import uuid
#CURRENT_FOLDER = r'C:\Users\aparg\Desktop\opraahfx'
# CURRENT_FOLDER = r'C:\Users\apar\Desktop\oprahfx'
CURRENT_FOLDER = './'
os.chdir(CURRENT_FOLDER)
# import subprocess
# The above code is setting the value of the `DISPLAY` environment variable to `:99`.
# os.environ['DISPLAY'] = ':99'
# command = "Xvfb :99 -screen 0 1024x768x16 &"
# subprocess.run(command, shell=True)

from datetime import date
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pynput.keyboard import Key, Controller
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
# from selenium import webdriver
from seleniumwire import webdriver
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from tqdm import tqdm
import pandas as pd
import time
import random
import psycopg2
from psycopg2 import pool
from sqlalchemy import create_engine
from contextlib import contextmanager
from datetime import datetime
from fake_useragent import UserAgent
#%%

#################### User input ####################
min_wait_time = 6
max_wait_time = 10

videos_per_account = 2

#################### File paths ####################
curr_date = date.today().strftime("%d-%m-%Y")

PATH_DICT = {
    'PROJECT_DIR': CURRENT_FOLDER,
    
    'ORIGINAL_VIDEO_DIR': os.path.join(CURRENT_FOLDER, 'input', 'videos'),
    'ACCOUNT_FILE': os.path.join(CURRENT_FOLDER, 'input', 'gmail_accounts_7.csv'),
    'VIDEO_METADATA_FILE': os.path.join(CURRENT_FOLDER, 'input', 'video_metadata.csv'),
    
    'OUTPUT_DIR':  os.path.join(CURRENT_FOLDER, f'output_{curr_date}'),
    'OUTPUT_FILE':  os.path.join(CURRENT_FOLDER, f'output_{curr_date}', 'output_youtube.csv')
    }

#%%
db_params = {
    'host': 'opraah-database.c9qouuiwyuwx.ap-south-1.rds.amazonaws.com',
    'database': 'opraah',
    'user': 'postgres',
    'password': 'VUFPZaluUQk',
    'port': '5432'
}

max_connections = 1

# Create a connection pool
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
                FROM public.youtube_accounts
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
                    UPDATE public.youtube_accounts
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
                SELECT * FROM public.youtube_video_metadata WHERE is_processed = 'NOT PROCESSED' LIMIT 1;
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
                    UPDATE public.youtube_video_metadata
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
                    UPDATE public.youtube_accounts
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

# open chrome browser
# Chrome browsers for Testing - c

def open_chrome_browser(headless=False, user_agent=True, proxy=None, download_directory=None):
    options = {
        'proxy': {
            'http': 'http://krfYsk7fDNckFV7f:X90vuBO81YgGbVHu_country-in_session-eWtuXDGW_lifetime-30m_streaming-1@geo.iproyal.com:11200',
            'https': 'http://krfYsk7fDNckFV7f:X90vuBO81YgGbVHu_country-in_session-eWtuXDGW_lifetime-30m_streaming-1@geo.iproyal.com:11200',
        }
    }
    
    driver = webdriver.Chrome(seleniumwire_options=options)

    return driver


def open_browser(headless=False, user_agent=True, proxy=None, download_directory=None):    
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
    # if user_agent:
    #     ua = UserAgent()
    #     user_agent = ua.chrome + ' ' + ua.os_linux
    #     chrome_options.add_argument(f'user-agent={user_agent}')
    if proxy:
        chrome_options.add_argument(f"--load-extension=./ip_royal_proxy")  
    if download_directory:
        preferences = {"download.default_directory": download_directory}
        chrome_options.add_experimental_option("prefs", preferences)
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def open_remote_browser(grid_url, headless=False, user_agent=None, proxy=None, download_directory=None):
    chrome_service = ChromeService(ChromeDriverManager().install())
    
    chrome_options = uc.ChromeOptions()
    # chrome_options.binary_location = chrome_binary_path
    
    chrome_options.add_argument("--window-size=1920,1080")
    #chrome_options.add_argument("--start-minimized")  # Add this line to start in minimized mode
    chrome_options.add_argument("--disable-extensions") # Disable Chrome extensions
    #chrome_options.add_argument('--disable-notifications') # Disable Chrome notifications
    chrome_options.add_argument("--mute-audio") # Mute system audio
    #chrome_options.add_argument('--disable-dev-shm-usage') # Disable the use of /dev/shm to store temporary data
    #chrome_options.add_argument('--ignore-certificate-errors') # Ignore certificate errors
    chrome_options.add_argument("--incognito")  # Start Chrome in incognito mode
    #chrome_options.add_argument("--disable-geolocation")  # Disable geolocation in Chrome
    chrome_options.add_argument('--disable-dev-shm-usage')
    if headless:
        chrome_options.add_argument("--headless")
    if user_agent:
        #user_agent = UserAgent()['google chrome']
        chrome_options.add_argument(f"--user-agent={user_agent}")
    if proxy:
        chrome_options.add_argument(f"--proxy-server={proxy}")
    if download_directory:
        preferences = {"download.default_directory": download_directory}
        chrome_options.add_experimental_option("prefs", preferences)
    
    driver = webdriver.Remote(command_executor=grid_url, options=chrome_options)
    
    return driver

# random time delay between requests (anti-blocking technique)
def random_time_delay(start=10, end=20):
    time.sleep(random.uniform(start, end))

def load_credentials_df():
    df = pd.read_csv(PATH_DICT['ACCOUNT_FILE'])
    df.columns = ['email_id', 'password']
    return df.reset_index(drop=True)

def load_video_df():
    df = pd.read_csv(PATH_DICT['VIDEO_METADATA_FILE'])
    df['filename'] = df['url'].apply(lambda x: x.split("/")[-2])
    df['tags'] = df['tags'].apply(lambda x: ", ".join(x.split(", ")[:10]))
    df['download_status'] = False
    return df.reset_index(drop=True)

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

def download_video_df(df):
    for i, row in tqdm(df.iterrows(), total=df.shape[0]):
        output_filepath = os.path.join(PATH_DICT['ORIGINAL_VIDEO_DIR'], row['filename']+'.mp4')
        if not os.path.exists(output_filepath):
            status = download_video(row['url'], output_filepath)
            df.at[i, 'download_status'] = status
        else:
            df.at[i, 'download_status'] = True
        
    return df.reset_index(drop=True)

def generate_task_df(df_account, df_video, n=3):
    df = []
    for _, row in df_account.iterrows():
        combined_rows = pd.concat([row] * n, ignore_index=True, axis=1).T
        
        random_rows = df_video.sample(n = n, ignore_index=True)
        
        combined_rows = pd.concat([combined_rows, random_rows], axis=1, ignore_index=True)
        
        df.append(combined_rows)
        
    df = pd.concat(df)
    df.columns = list(df_account.columns) + list(df_video.columns)
    
    df['login_status'] = False
    df['go_to_upload_page_status'] = False
    df['select_file_status'] = False
    df['upload_status'] = False
    
    return df.reset_index(drop=True)

def go_to_homepage():
    # go to homepage
    driver.get("https://www.youtube.com/")

    # wait to load
    random_time_delay(min_wait_time, max_wait_time)

def login(email_id, password):
    try:
        # We need this when we work with multiple accounts 
        driver.delete_all_cookies()
        
        # go to homepage
        go_to_homepage()
        
        # Find and click on the "Sign in" button
        driver.find_element(By.CSS_SELECTOR, '*[aria-label="Sign in"]').click()
       
        # wait to load
        random_time_delay(min_wait_time, max_wait_time)
       
        # Locate the email input field and enter your email
        driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys(email_id)
       
        # Click the "Next" button
        driver.find_element(By.XPATH, "//*[text()='Next']").click()
       
        # wait to load
        random_time_delay(min_wait_time, max_wait_time)
       
        # Locate the password input field and enter your password
        driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys(password)
       
        # Click the "Next" button to log in
        driver.find_element(By.XPATH, "//*[text()='Next']").click()
       
        # wait to load
        random_time_delay(min_wait_time, max_wait_time)
        
        # Skip suggestions page (if appears)
        try:
            driver.find_element(By.XPATH, "//*[text()='Not now']").click()
            random_time_delay(min_wait_time, max_wait_time)
        except:
            pass
        
        return True

    except Exception as e:
        print("Login Error - ", str(e))
        return False

def go_to_upload_page():
    try:
        # Click on 'Create' button in top right corner
        driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Create"]').click()
        
        # wait to load
        random_time_delay(min_wait_time, max_wait_time)
        
        # Choose 'Upload video' option from drop-down
        driver.find_element(By.LINK_TEXT, 'Upload video').click()
        
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
        random_time_delay(min_wait_time, 30)
    
        # Simulate keyboard to input filepath and press 'Enter'
        # keyboard = Controller()
        # keyboard.type(absolute_path)
        # keyboard.press(Key.enter)
        # keyboard.release(Key.enter)
        
        # wait to load
        random_time_delay(25, 60)
        
        return True
    
    except Exception as e:
        print("File selection failed - ", str(e))
        return False

def upload_video(title, description, tags):
    try:
        # Input video title
        driver.find_element(By.CSS_SELECTOR, 'div[aria-label*="Add a title"]').clear()
        driver.find_element(By.CSS_SELECTOR, 'div[aria-label*="Add a title"]').send_keys(title)
        
        # wait to load
        #random_time_delay(min_wait_time, max_wait_time)
        
        # Input video descrition
        driver.find_element(By.CSS_SELECTOR, 'div[aria-label*="Tell viewers"]').clear()
        driver.find_element(By.CSS_SELECTOR, 'div[aria-label*="Tell viewers"]').send_keys(description)
        
        
        # wait to load
        #random_time_delay(min_wait_time, max_wait_time)
        
        # Age restriction
        driver.find_element(By.CSS_SELECTOR, 'tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]').click()
        
        # wait to load
        random_time_delay(min_wait_time, max_wait_time)
        
        # Show more
        driver.find_element(By.XPATH, '//*[@id="toggle-button"]').click()
        
        # wait to load
        random_time_delay(min_wait_time, max_wait_time)
        
        # Input video tags
        driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Tags"]').send_keys(tags)
        driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Tags"]').send_keys(Keys.ENTER)
        
        # wait to load
        random_time_delay(min_wait_time, max_wait_time)
        
        # Click on 'Next' button to go to next page which is 'Video elements', then 'Checks', then 'Visibility'
        for _ in range(10):
            try:
                driver.find_element(By.CSS_SELECTOR, 'ytcp-button[id="next-button"]').click()
                
                # wait to load
                random_time_delay(min_wait_time, max_wait_time)
            except:
                pass

        
        # Make it 'public'
        driver.find_element(By.CSS_SELECTOR, 'tp-yt-paper-radio-button[name="PUBLIC"]').click()
        
        # wait to load
        random_time_delay(min_wait_time, max_wait_time)
        
        # Publish video
        driver.find_element(By.CSS_SELECTOR, 'ytcp-button[id="done-button"]').click()
        
        # wait to load
        random_time_delay(min_wait_time*2, max_wait_time*2)
        
        return True
    
    except Exception as e:
        print("Video upload failed - ", str(e))
        return False

def logout():
    try:
        # go to homepage
        go_to_homepage()
        
        # click on user profile button
        driver.find_element(By.CSS_SELECTOR, 'button[id="avatar-btn"]').click()
        
        # wait to load
        random_time_delay(min_wait_time, max_wait_time)
        
        # click on 'Sign out'
        driver.find_element(By.LINK_TEXT, 'Sign out').click()
        
        # wait to load
        random_time_delay(min_wait_time, max_wait_time)
        
        return True
    
    except Exception as e:
        #print("Logout Error - ", str(e))
        return False

def check_file_exists(file_path):
    return os.path.exists(file_path)
#%%
def create_channel(driver):
    driver.find_element(By.XPATH, ".//button[@aria-label='Create channel']").click()

if __name__=='__main__':
    
    for key, val in PATH_DICT.items():
        if 'DIR' in key:
            os.makedirs(val, exist_ok=True)


    # df_video = download_video_df(df_video)
    # df_task = generate_task_df(df_account, df_video, n = videos_per_account)
    
    # df_task.to_csv(PATH_DICT['OUTPUT_FILE'], index=False)
    
    #################### Pipeline execution ####################
    nerrors = 0
    current_login = ''
    file_path = None

    # email = user_info['email']
    # video_url = video_info['url']
    # user_videos_uploaded = user_info['videos_uploaded']
    while True:
        file_path = None
        try:
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
                    logout_status = logout()
                    try:
                        driver.quit()
                    except:
                        pass

                    driver = open_chrome_browser(proxy=True)
                        
                    # try login - can be successful or failed
                    login_status = login(email, password)
                    current_login = email

                # If encountered account before, then
                else:
                    # If login to account was successful, go to homepage
                    if login_status:
                        go_to_homepage()

                    # If login to account was failed, then skip task
                    else:
                        continue

                # If login to current account successful, then proceed to upload
                if login_status:
                    go_to_upload_page_status = go_to_upload_page()
                    ## ADD create channell code
                    try:
                        create_channel(driver)
                        random_time_delay()
                        go_to_upload_page_status = go_to_upload_page()
                    except Exception as e:
                        pass
                    select_file_status = select_file(os.path.join(PATH_DICT['ORIGINAL_VIDEO_DIR'], file_name+'.mp4'))

                    upload_status = upload_video(title=title, description=description, tags=tags)
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
                    # The above code is using the `os` module in Python to remove a file specified by
                    # the `file_path` variable.
                    # os.remove(file_path)
                    print(f"File '{file_path}' deleted successfully.")
            except Exception as e:
                print(f"Error deleting file '{file_path}': {e}")
            random_time_delay(min_wait_time, max_wait_time)