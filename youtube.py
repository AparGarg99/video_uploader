import os
#CURRENT_FOLDER = r'C:\Users\aparg\Desktop\opraahfx'
CURRENT_FOLDER = r'C:\Users\apar\Desktop\oprahfx'
os.chdir(CURRENT_FOLDER)

from datetime import date
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pynput.keyboard import Key, Controller
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from tqdm import tqdm
import pandas as pd
import time
import random

#%%

#################### User input ####################
min_wait_time = 8
max_wait_time = 10

videos_per_account = 2

#################### File paths ####################
curr_date = date.today().strftime("%d-%m-%Y")

PATH_DICT = {
    'PROJECT_DIR': CURRENT_FOLDER,
    
    'ORIGINAL_VIDEO_DIR': os.path.join(CURRENT_FOLDER, 'input', 'videos'),
    'ACCOUNT_FILE': os.path.join(CURRENT_FOLDER, 'input', 'gmail_accounts_3.csv'),
    'VIDEO_METADATA_FILE': os.path.join(CURRENT_FOLDER, 'input', 'video_metadata.csv'),
    
    'OUTPUT_DIR':  os.path.join(CURRENT_FOLDER, f'output_{curr_date}'),
    'OUTPUT_FILE':  os.path.join(CURRENT_FOLDER, f'output_{curr_date}', 'output_youtube.csv')
    }

#%%


# open chrome browser
# Chrome browsers for Testing - https://googlechromelabs.github.io/chrome-for-testing/#stable
def open_browser(chrome_binary_path="chrome-win64/chrome.exe", driver_version='118', headless=False, user_agent=None, proxy=None, download_directory=None):
    chrome_service = ChromeService(ChromeDriverManager(driver_version=driver_version).install())
    
    chrome_options = uc.ChromeOptions()
    chrome_options.binary_location = chrome_binary_path
    
    chrome_options.add_argument("--window-size=1920,1080")
    #chrome_options.add_argument("--start-minimized")  # Add this line to start in minimized mode
    chrome_options.add_argument("--disable-extensions") # Disable Chrome extensions
    #chrome_options.add_argument('--disable-notifications') # Disable Chrome notifications
    chrome_options.add_argument("--mute-audio") # Mute system audio
    #chrome_options.add_argument('--disable-dev-shm-usage') # Disable the use of /dev/shm to store temporary data
    #chrome_options.add_argument('--ignore-certificate-errors') # Ignore certificate errors
    chrome_options.add_argument("--incognito")  # Start Chrome in incognito mode
    #chrome_options.add_argument("--disable-geolocation")  # Disable geolocation in Chrome
    
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
    
    driver = uc.Chrome(service = chrome_service, options = chrome_options)
    
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
        # Click on 'Select files' button to choose files from desktop
        driver.find_element(By.CSS_SELECTOR, 'ytcp-button[id="select-files-button"]').click()
        
        # wait to load
        random_time_delay(min_wait_time, max_wait_time)
    
        # Simulate keyboard to input filepath and press 'Enter'
        keyboard = Controller()
        keyboard.type(video_path)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        
        # wait to load
        random_time_delay(min_wait_time, max_wait_time)
        
        return True
    
    except Exception as e:
        print("File selection failed - ", str(e))
        return False



def upload_video(title, description, tags):
    try:
        # Input video title
        (driver.find_element(By.CSS_SELECTOR, 'div[aria-label*="Add a title"]').clear()).send_keys(title)
        
        # wait to load
        #random_time_delay(min_wait_time, max_wait_time)
        
        # Input video descrition
        (driver.find_element(By.CSS_SELECTOR, 'div[aria-label*="Tell viewers"]').clear()).send_keys(description)
        
        
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
        (driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Tags"]').send_keys(tags)).send_keys(Keys.ENTER)
        
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


#%%
if __name__=='__main__':
    
    for key, val in PATH_DICT.items():
        if 'DIR' in key:
            os.makedirs(val, exist_ok=True)
        
    df_account = load_credentials_df()
    df_video = load_video_df()
    df_video = download_video_df(df_video)
    df_task = generate_task_df(df_account, df_video, n = videos_per_account)
    
    df_task.to_csv(PATH_DICT['OUTPUT_FILE'], index=False)
    
    #################### Pipeline execution ####################
    nerrors = 0
    current_login = ''
    
    for i, row in tqdm(df_task.iterrows(), total = df_task.shape[0]):
        try:
            # If encountered a new account, then try login again with new account
            if row['email_id'] != current_login:
                # logout from old account (if driver open)
                logout_status = logout()
                
                # close existing brower (if any)
                try:
                    driver.quit()
                except:
                    pass
                
                # open browser again
                driver = open_browser(chrome_binary_path = os.path.join(PATH_DICT['PROJECT_DIR'], 'chrome-win64', 'chrome.exe'),
                                    driver_version = '118',
                                    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36')
                
                # try login - can be successful or failed
                login_status = login(row['email_id'], row['password'])
                
                # update current login account
                current_login = row['email_id']
                
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
                
                select_file_status = select_file(os.path.join(PATH_DICT['ORIGINAL_VIDEO_DIR'], row['filename']+'.mp4'))
    
                upload_status = upload_video(title=row['title'], description=row['description'], tags=row['tags'])
                
                df_task.at[i, 'login_status'] = login_status
                df_task.at[i, 'go_to_upload_page_status'] = go_to_upload_page_status
                df_task.at[i, 'select_file_status'] = select_file_status
                df_task.at[i, 'upload_status'] = upload_status
                
                df_task.to_csv(PATH_DICT['OUTPUT_FILE'], index=False)
                
            print(current_login)
            
        except Exception as e:
            print("Error in pipeline -", str(e))
            nerrors += 1
            if nerrors == 3:
                break
            pass
    
    
    # close existing brower (if any)
    try:
        driver.quit()
    except:
        pass