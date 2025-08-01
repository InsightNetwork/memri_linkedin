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

WORKDIR /app

COPY ./memri /app/memri
COPY ./linkedin /app/linkedin
COPY ./linkedin_plugin /app/linkedin_plugin

RUN pip3 install -r /app/memri/requirements.txt
RUN pip3 install -r /app/linkedin/requirements.txt

ARG VIS_OWNER_KEY
ARG VIS_DATABASE_KEY

ENV VIS_OWNER_KEY=${VIS_OWNER_KEY}
ENV VIS_DATABASE_KEY=${VIS_DATABASE_KEY}
ENV PYTHONPATH=/app

EXPOSE 8080

CMD ["run_plugin", "--read_args_from_env", "True"]

