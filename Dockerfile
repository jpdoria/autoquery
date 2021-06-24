FROM python:3.9-alpine

RUN apk update \
    && apk add python3-dev \
    gcc \
    libc-dev

RUN mkdir /autoquery
COPY . /autoquery
WORKDIR /autoquery
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "autoquery.py"]
