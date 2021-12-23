FROM python:3.10-slim

RUN groupadd --gid 5000 user && useradd --home-dir /home/user --create-home --uid 5000 --gid 5000 --shell /bin/sh --skel /dev/null user
RUN apt-get update && apt-get install -y curl
RUN python -m pip install --upgrade pip
RUN python -m pip install pipenv
RUN curl https://raw.githubusercontent.com/lacework/go-sdk/main/cli/install.sh | bash

USER user

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PATH "$PATH:/home/user/.local/bin"

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY reports.py ./
COPY jef ./jef
COPY reports ./reports
COPY templates ./templates

# ENTRYPOINT [ "python", "-u", "/app/reports.py" ]