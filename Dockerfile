FROM jfloff/alpine-python:2.7-slim
COPY requirements.txt /
RUN pip install -r /requirements.txt
