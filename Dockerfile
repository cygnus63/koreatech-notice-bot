FROM python:3.12.8-slim

WORKDIR /python-docker/koreatech_notice/

ADD . /python-docker/koreatech_notice/

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

CMD [ "python3", "/python-docker/koreatech_notice/main.py" ]