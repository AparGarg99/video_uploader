# Installation
1. Download and Install [Anaconda](https://www.anaconda.com/download)

2. Open Anaconda prompt

3. Navigate to the project directory
```
cd <project path>
```

4. Create new anaconda environment
```
conda create -n "video_uploader" python==3.8.0
```

5. Activate anaconda environment
```
conda activate "video_uploader"
```

6. Install Spyder IDE
```
conda install -c anaconda spyder
```

7. Install the required dependencies
```
pip install -r requirements.txt
```

8. Go to Google Cloud Console 
    * **Create new project**
    ```
    Create new project -> Search "Google Drive API" -> Enable -> Manage
    ```

    * **Create OAuth Consent Screen**
    ```
    Credentials -> Configure Consent screen -> External -> Create -> Fill "App information" (App name must be same as project name) & "Developer contact information" sections -> Save and Continue ->
    Save and Continue -> Save and Continue -> Back to Dashboard -> Publish App
    ```

    * **Create OAuth Client ID**
    ```
    Credentials -> OAuth Client ID -> Select 'Application type' to be Web application. -> Enter an appropriate name -> Input http://localhost:8080 for 'Authorized JavaScript origins' -> Input http://localhost:8080/ for 'Authorized redirect URIs' -> Create -> Download `client_secrets.json`
    ```

11. Put `client_secrets.json` file inside project

12. Download [`settings.yaml`](https://github.com/pyGuru123/Youtube/blob/main/Google%20Services%20with%20Python/Google%20OAuth%202.0/settings.yaml) file

12. Copy "client_id" and "client_secret" from `client_secrets.json` and paste in `settings.yaml` file

13. Create `credentials.json` (oauth client secret) file by executing
```
python setup_credentials.py
```

14. Download and unzip [chrome-binary](https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/118.0.5993.70/win64/chrome-win64.zip) and [edge-binary](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/) folders.

# Usage

1. Go to Anaconda prompt

2. Navigate to the project directory
```
cd <project path>
```

3. Activate anaconda environment
```
conda activate "video_uploader"
```


## Instagram Account Creation

#### To run the bot, use this command
```
python 1_instagram_account_creation.py
```

### Description
This Python script automates the creation of Instagram accounts using Selenium WebDriver. It utilizes temporary email services or SMS activation APIs for verification purposes. Additionally, it interacts with a PostgreSQL database to manage account information.

### Flow
The bot will first open a chrome browser and open instagram.com, then head to the sign up page. For email it will rely on temp-mail or sms-activate. If temp-mail is used it will open a new window and open temp-mail site and get the email using clipboard. If the clipboard doesn't work it will take a screenshot and get the email from there. Then the email is used in the sign up page for instagram in a different window. Once the OTP is generated it will be used for account verification. Once the account is verified it will be saved to the db.

### Configuration
The bot can be configured to use `Proxy`, `SMS-Activate`, `Temp-mail`.

To enable proxy usage:
```
USE_PROXY = True
```

### You can only use either SMS-activate or Temp-mail 

To use SMS-Activate:
```
USE_SMS_ACTIVE = True
```

To use Temp-mail:
```
USE_TEMP_MAIL = True
```


## Instagram video uploading

#### To run the bot, use this command
```
python 2_instagram_upload.py
```


### Description
This bot automates the uploading of videos on Instagram accounts using Selenium WebDriver. It utilizes temporary email services or SMS activation APIs for verification purposes. Additionally, it interacts with a PostgreSQL database to manage account information.

### Flow
The bot will open a chrome browser and head towards instagram. It will then fetch the credentials saved in the insta_accounts table where it will check for the videos uploaded and is_use attribute. Then it will take any one account that can be used and updated the is_use attribute to True. Then it will login to the account on instagram start the upload process. If uploaded successfully it will set the value of in_use to False and increment the value of videos_uploaded to True. In case of failure it will revert back.

### Configuration
```
USE_PROXY : Set this to true if you want proxy to be used. 
```


# Database
There are 4 tables being used for the bots, 2 tables for instagram and 2 tables for youtube.

Tables:
- public.insta_accounts
- public.insta_video_metadata
- public.youtube_accounts
- public.youtube_video_metadata


### insta_accounts
___
| email | password | in_use | last_used | videos_uploaded

 - email -> the registered email id for the insta gram accounts
 - password -> the registered password for the instagram accounts
 - in_use -> this is field to represent a mutex lock, so multiple instances of uploading won't upload the same video.
 - last_used -> timestamp field of when the video account data was last used/updated.
 - video_uploaded -> The number of videos uploaded in the account. Defaults will be zero.

### insta_video_metadata
___
| url | title | tags | description | is_processed

- url -> The google drive link of the video to be uploaded
- title -> The title/caption of the video.
- tags -> The tags to be used.
- description -> Description of the video
- is_processed -> ENUM Value('Not processed', 'Downloading','Processed', 'Done')
    
    - Not processed: This is the default value. Video that have not processed and 
    - Downloading: When the video is downloading by the bot.
    - Processing: When the video upload process starts.
    - Done: The video has been uploaded and won't be processed.

### youtube_accounts
___
| email | password | in_use | last_used | videos_uploaded | number | activation_id | insta_account |

 - email -> the registered email id for the insta gram accounts
 - password -> the registered password for the instagram accounts
 - in_use -> this is field to represent a mutex lock, so multiple instances of uploading won't upload the same video.
 - last_used -> timestamp field of when the video account data was last used/updated.
 - video_uploaded -> The number of videos uploaded in the account. Defaults will be zero.
 - number -> The number, used to create youtube account if used. Number from sms-activate.
 - activation_id -> The activation_id for sms-activate.
 - insta_account -> If the account was used for instagram.

 #### Number, activation_id, insta_account are not used and are not necessary.

 ### youtube_video_metadata
___
| url | title | tags | description | is_processed

- url -> The google drive link of the video to be uploaded
- title -> The title/caption of the video.
- tags -> The tags to be used.
- description -> Description of the video
- is_processed -> ENUM Value('Not processed', 'Downloading','Processed', 'Done')
    
    - Not processed: This is the default value. Video that have not processed and 
    - Downloading: When the video is downloading by the bot.
    - Processing: When the video upload process starts.
    - Done: The video has been uploaded and won't be processed.


## Postgres Connection

The application is using Postgres database hosted in AWS RDS with the following config.

```
Host: opraah-database.c9qouuiwyuwx.ap-south-1.rds.amazonaws.com
Port: 5432
Database: opraah
Username: postgres
Password: VUFPZaluUQk
```

# Proxies:

The uploader service uses proxies from Brightdata.

The proxies are being used as an extension for the chrome browser. You can see them in the proxies folder. Inside this you will find different folders which are like different modules for an extension. 

The extension looks something like this:

```
proxy_isp
    - background.js
    - manifest.json
```

To change the credentials for proxy, simply go to the respective proxy and update it int the `background.js` file. There should be the username and password, update it there.

```
function callbackFn(details) {
    return {
        authCredentials: {
            username: "<USERNAME>",
            password: "<PASSWORD>"
        }
    };
}
```

The proxies folder already contains different type of proxy categories provided by `Brightdata.`

```
proxy_auth_plugin : These are datacenter IPs.
proxy_isp: These are IP provided by ISP.
proxy_residential: These are residential IPs used by actual people.
proxy_web_unlocker: This proxy when used can unlock any webpage, blocked by captchpas, but don't seem to work for login cases.
```

### Brighdata credits

To add credits to Brighdata:
- Go to https://brightdata.com
- Login in to brighdata.
- Go to billing, https://brightdata.com/cp/billing
- Click on add funds.
- Enter the amount and payment method and payout.
---


# References:
1. Install Anaconda - https://www.youtube.com/watch?v=Qve5JTd1OSA&ab_channel=GeekyScript
2. Google Drive API - https://www.youtube.com/watch?v=G_4KUbuwtlM&ab_channel=GeekySid