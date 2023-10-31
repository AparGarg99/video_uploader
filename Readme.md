# Description


# Installation
1. Download and Install [Anaconda](https://www.anaconda.com/download)

2. Open Anaconda prompt

3. Navigate to the project directory
```
cd <project path>
```

4. Create new anaconda environment
```
conda create -n "video_uploader" python==3.7.6
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

12. Download `[settings.yaml](https://github.com/pyGuru123/Youtube/blob/main/Google%20Services%20with%20Python/Google%20OAuth%202.0/settings.yaml)` file

12. Copy "client_id" and "client_secret" from `client_secrets.json` and paste in `settings.yaml` file

13. Create oauth client secret file
```
python setup_credentials.py
```
This will create a `credentials.json` file

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

4. Execute
```
python youtube.py
```

OR

```
spyder
```
Then press 'F5' key to run file



# References:
1. Install Anaconda - https://www.youtube.com/watch?v=Qve5JTd1OSA&ab_channel=GeekyScript
2. Google Drive API - https://www.youtube.com/watch?v=G_4KUbuwtlM&ab_channel=GeekySid
