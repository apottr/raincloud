FROM python:3
RUN apt-get update && apt-get -y install cron

ADD . /usr/local/src

WORKDIR /usr/local/src

RUN pip install --no-cache-dir -r requirements.txt

CMD cron && python ./app.py
