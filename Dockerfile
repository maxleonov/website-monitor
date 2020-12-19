FROM python:3.7

WORKDIR /app

COPY requirements.txt .
COPY dist/website_monitor-0.0.1-py3-none-any.whl .
COPY config ./config

RUN pip install -r requirements.txt
RUN pip install -v -t /app website_monitor-0.0.1-py3-none-any.whl
