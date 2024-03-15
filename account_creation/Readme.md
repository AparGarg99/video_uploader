# Instagram Account Creation

## Description

This Python script automates the creation of Instagram accounts using Selenium WebDriver. It utilizes temporary email services or SMS activation APIs for verification purposes. Additionally, it interacts with a PostgreSQL database to manage account information.

## Flow

The bot will first open a chrome browser and open instagram.com, then head to the sign up page. For email it will rely on temp-mail or sms-activate. If temp-mail is used it will open a new tab and open temp-mail site and get the email using clipboard. If the clipboard doesn't work it will take a screenshot and get the email from there. Then the email is used in the sign up page for instagram. Once the OTP is generated the OTP will be used for account verification. Once the account is verified it will be saved to the db.

## Prerequisites

### Installing Python

#### Windows

1. Visit the [Python Downloads](https://www.python.org/downloads/) page.
2. Download the latest version of Python for Windows.
3. Run the installer.
4. Check the box that says "Add Python to PATH" during installation.
5. Click "Install Now" and follow the installation wizard.

#### macOS

1. macOS typically comes with Python pre-installed. However, it's recommended to install a separate version using Homebrew or the official installer.
2. To install using Homebrew, open Terminal and run:

3. Alternatively, download the latest version of Python from the [Python Downloads](https://www.python.org/downloads/) page.
4. Run the installer and follow the instructions.

#### Linux

1. Most Linux distributions come with Python pre-installed. You can check by running:


Before running the script, ensure you have the following dependencies installed:

- Python 3.x
- Selenium WebDriver
- Undetected Chromedriver
- Fake User-Agent
- Requests
- SMSActivateAPI
- Psycopg2
- EasyOCR (for reading OTP from images)
- Pyperclip (for copying email addresses)

All the dependencies are in the requirements.txt file. Befor running the command ensure the working directory is the folder with the application code.

Install the dependencies using pip:

```bash
pip install -r requirements.txt
```

## Configuration

The bot can be configured to use `Proxy`, `SMS-Activate`, `Temp-mail`.

To enable proxy usage, set:

```
USE_PROXY = True
```


### You can only use either SMS-activate or Temp-mail 

To use SMS-Activate
```
USE_SMS_ACTIVE = True
```

To use Temp-mail
```
USE_TEMP_MAIL = True
```
