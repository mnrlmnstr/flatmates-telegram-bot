FROM python:latest

WORKDIR /app
COPY . /app

# Update packages and intall libgl1 for opencv
RUN apt-get update && \
    apt-get install -yqq libgl1

# Install python requirements
RUN \
    pip install -U pip && \
    pip install -r requirements.txt

# Remove obsolete files:
RUN apt-get autoremove --purge -y \
    unzip \
    && apt-get clean \
    && rm -rf \
    /tmp/* \
    /usr/share/doc/* \
    /var/cache/* \
    /var/lib/apt/lists/* \
    /var/tmp/*
