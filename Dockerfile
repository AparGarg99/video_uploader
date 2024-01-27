FROM ubuntu:20.04

RUN apt-get update && apt-get install -y python3-pip

RUN pip3 install selenium undetected_chromedriver pynput google-auth-oauthlib google-auth-httplib2 google-api-python-drive pandas tqdm

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . /usr/src/app

WORKDIR /usr/src/app

CMD ["python3", "youtube.py"]