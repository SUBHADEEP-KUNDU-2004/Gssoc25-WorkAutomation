FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY Contributors-Point/requirements.txt /app/Contributors-Point/requirements.txt
COPY Projects-Guide/requirements.txt /app/Projects-Guide/requirements.txt

RUN pip install --upgrade pip \
    && pip install -r /app/Contributors-Point/requirements.txt \
    && pip install -r /app/Projects-Guide/requirements.txt

COPY Contributors-Point /app/Contributors-Point
COPY Projects-Guide /app/Projects-Guide

CMD ["python", "--version"]
