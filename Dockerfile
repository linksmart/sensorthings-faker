FROM python:3-alpine3.6

RUN pip install requests==2.18.4

COPY src /home/app
WORKDIR /home/app

ENTRYPOINT [ "python", "-u" ]
CMD [ "faker.py" ]
