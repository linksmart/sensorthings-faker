FROM python:2-alpine3.6
COPY requirements.txt /
RUN pip install -r /requirements.txt
