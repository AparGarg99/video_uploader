import os
#CURRENT_FOLDER = r'C:\Users\aparg\Desktop\opraahfx'
CURRENT_FOLDER = r'C:\Users\apar\Desktop\oprahfx'
os.chdir(CURRENT_FOLDER)

from datetime import date
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pynput.keyboard import Key, Controller
from selenium.webdriver.common.by import By
from tqdm import tqdm
import pandas as pd
from msedge.selenium_tools import Edge, EdgeOptions
import random
import time

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
    'OUTPUT_FILE':  os.path.join(CURRENT_FOLDER, f'output_{curr_date}', 'output_instagram.csv')
    }

#%%

# open edge browser
# https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
def open_browser(executable_path, headless=False, user_agent=None, proxy=None, download_directory=None):
    options = EdgeOptions()
    options.use_chromium = True
    
    options.add_argument("--window-size=1920,1080")
    #options.add_argument("--start-minimized")  # Add this line to start in minimized mode
    #options.add_argument("--disable-extensions") # Disable Chrome extensions
    #options.add_argument('--disable-notifications') # Disable Chrome notifications
    #options.add_argument("--mute-audio") # Mute system audio
    #options.add_argument('--disable-dev-shm-usage') # Disable the use of /dev/shm to store temporary data
    #options.add_argument('--ignore-certificate-errors') # Ignore certificate errors
    options.add_argument("--incognito")  # Start Chrome in incognito mode
    #options.add_argument("--disable-geolocation")  # Disable geolocation in Chrome
    
    if headless:
        options.add_argument("--headless")
    if user_agent:
        #user_agent = UserAgent()['google chrome']
        options.add_argument(f"--user-agent={user_agent}")
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")
    if download_directory:
        preferences = {"download.default_directory": download_directory}
        options.add_experimental_option("prefs", preferences)
    
    driver = Edge(executable_path = executable_path, options = options)
    
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
    driver.get("https://www.instagram.com")
   
    # wait to load
    random_time_delay(min_wait_time, max_wait_time)



def login(email_id, password):
    try:
        # We need this when we work with multiple accounts 
        driver.delete_all_cookies()
        
        # go to homepage
        go_to_homepage()
       
        # Locate the email input field and enter your email
        driver.find_element(By.NAME, "username").send_keys(email_id)
       
        # Locate the password input field and enter your password
        driver.find_element(By.NAME, "password").send_keys(password)
       
        # Click the "Next" button to log in
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
       
        # wait to load
        random_time_delay(min_wait_time, max_wait_time)
        
        # Skip suggestions page (if appears)
        try:
            driver.find_element(By.XPATH, "//*[text()='Not Now']").click()
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
        driver.find_element(By.CSS_SELECTOR, 'svg[aria-label="New post"]').click()
        
        # wait to load
        random_time_delay(min_wait_time, max_wait_time)
        
        return True
        
    except Exception as e:
        print("Open upload page failed - ", str(e))
        return False


 
def select_file(video_path):
    try:
        # Click on 'Select files' button to choose files from desktop
        driver.find_element(By.XPATH, "//*[text()='Select from computer']").click()
        
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



def upload_video(captions):
    try:
        driver.find_element(By.XPATH, "//*[text()='OK']").click()
        
        # Click on 'Next' button to go to next page
        for _ in range(2):
            driver.find_element(By.XPATH, "//*[text()='Next']").click()
            
            random_time_delay(min_wait_time, max_wait_time)

        # Input captions
        driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Write a caption..."]').send_keys(captions)

        # Publish video
        driver.find_element(By.XPATH, "//*[text()='Share']").click()
        
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
                driver = open_browser(executable_path = os.path.join(PATH_DICT['PROJECT_DIR'], "edgedriver_win64", "msedgedriver.exe"),
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