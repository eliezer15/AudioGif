FROM python:3.9-alpine

COPY requirements.txt requirements.txt

RUN apk update && apk upgrade && apk add build-base

RUN pip install --no-cache-dir -r requirements.txt

COPY audiogif/ .

ENTRYPOINT ["python", "app.py"]