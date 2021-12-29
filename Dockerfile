FROM python:3.10-slim

RUN groupadd --gid 5000 user && useradd --home-dir /home/user --create-home --uid 5000 --gid 5000 --shell /bin/sh --skel /dev/null user && chmod 755 /home/user
RUN apt-get update && apt-get install -y curl
RUN curl https://raw.githubusercontent.com/lacework/go-sdk/main/cli/install.sh | bash

RUN python -m pip install --upgrade pip
COPY requirements.txt ./
RUN pip install -r requirements.txt

USER user

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PATH "$PATH:/home/user/.local/bin"

WORKDIR /app

COPY src/lacework_custom_reports ./lacework_custom_reports
# COPY reports ./reports
# COPY templates ./templates

ENTRYPOINT [ "python3", "-m", "lacework_custom_reports" ]