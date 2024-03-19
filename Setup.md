# Create custom AMI Image for instagram uploader.

- For this you will first need to create an AWS EC2 instance.
- Access the EC2 instance via ssh
- Install all necessary packages and application
- Write a system file that will run the application in background whenever the instance starts.
- Take a snapshot and build a custom AMI.


## Creating AWS EC2 instance
- Go to AWS
- Login using credentials (shubham@opraahfx.com)
- Click on search bar and find EC2 and click on it.
- Click on launch instance.
    - Enter name of the instance.
    - In the Amazon Machine Image click on `Ubuntu Server 22.04 LTS`
    - Choose instance type `(t2.small or t2.medium)`
    - Choose key pair login `opraah`
    - In network settings choose security group:
        - Click on select exisiting security group
        - Choose `launch-wizard-1`
    - Configure storage
        - Give atleast 30 GB of volume.

## Access EC2 instance via SSH.

- Login to AWS console.
- Go to EC2.
- Go to `instances(running)`.
- Click on the `instance ID` you want to access.
- Click on connect.
- Click on `SSH client`.
- Copy the command `ssh -i "opraah.pem" ubuntu@<SUB_DOMAIN>.compute.amazonaws.com`
- Now run the command where you have the `opraah.pem` file 


## Installing necessary packages and application

#### Update the linux packages and install virtualenv
```
sudo apt-get update
sudo apt install virtualenv
```
---

#### Install display package

This package is required for selenium to run in head mode.

```
sudo apt install xvfb
```

---

#### Install postgres depenedent package
```
sudo apt-get install python3-psycopg2
sudo apt install python3-dev libpq-dev
```

#### Install Google chrome
```
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

This should install all OS packages

---

You need to fetch the application code, for this you will need to setup ssh keys on github to clone repo.

---

#### Setup github ssh keys

```
ssh-keygen -t ed25519 -C "<YOUR_EMAIL_ID>"
cat /home/ubuntu/.ssh/id_ed25519.pub
```

Copy the keys and login to github and it to your ssh keys.

#### Clone the repo
```
git clone git@github.com:shantamshrestha/video-uploader.git
```

#### Go inside directory
```
cd video-uploader
```

#### Setup virtual environment

```
virtualenv -p python3 venv 
source ./venv/bin/activate
pip install -r requirements.txt
```

## Write system file to run application in background

```
sudo vim /etc/systemd/system/instagram.service
```

Now copy the contents below to the file.

**To exit vim press Esc and then type :wq and then enter.**

---
```
[Unit]
Description=Instagram Uploader
After=network.target xvfb.service

[Service]
Environment="DISPLAY=:11"
User=ubuntu
Type=simple
ExecStart=/home/ubuntu/video-uploader/venv/bin/python /home/ubuntu/video-uploader/2_instagram_upload.py
WorkingDirectory=/home/ubuntu/video-uploader
StandardOutput=/home/ubuntu/video-uploader/logfile.log
StandardError=/home/ubuntu/video-uploader/errorlog.log


[Install]
WantedBy=multi-user.target
```
---

#### Now load the daemon and start the service
```
sudo systemctl daemon-reload.
sudo systemctl start instagram.service
```

To check the running service
```
sudo systemctl status instagram.service
```

### You are almost done.

## Create custom AMI for Instagram uploader.

- Go to AWS console.
- Login if not logged in.
- Go to the EC2.
- Go to instances.
- Click on the instance you want to use for AMI.
- Click on `Actions`.
- Click on `Images and Templates`.
- Click on `Create Image`.
- Give a meaningful `Image name`.
- Give a meanningful `Description`. (Optional)
- Click on `Create Image`.
---

**DONE**