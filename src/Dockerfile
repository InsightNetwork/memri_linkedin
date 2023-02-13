# build python environment
FROM --platform=linux/amd64  python:3.9

# Adding trusting keys to apt for repositories,
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# get Google Chrome
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# update apt-get
RUN apt-get -y update

# install google-chrome-stable
RUN apt-get install -y google-chrome-stable

# get chromedriver
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip

# get unzip package
RUN apt-get install -yqq unzip

# unzip chromedriver
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/


COPY ./memri /app/memri
COPY ./linkedin /app/linkedin
COPY ./vis /app/vis

RUN pip3 install -r /app/memri/requirements.txt
RUN pip3 install -r /app/linkedin/requirements.txt

ENV PYTHONPATH=/app

EXPOSE 8080

ENTRYPOINT ["python3", "app/vis/start.py", "serve"]

# install git for pip to install from git
# RUN apt-get update && \
#     apt-get install -y git && \
#     rm -rf /var/lib/apt/lists/* && \
#     pip3 install --upgrade pip

# COPY ./memri /app/memri
# COPY ./linkedin /app/linkedin
# COPY ./vis /app/vis

# RUN pip3 install -r /app/memri/requirements.txt
# RUN pip3 install -r /app/linkedin/requirements.txt

# ENV PYTHONPATH=/app

# EXPOSE 8080

# ENTRYPOINT ["python3", "app/vis/start.py", "serve"]
