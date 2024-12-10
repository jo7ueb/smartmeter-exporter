FROM python:3-slim-buster

WORKDIR /app
COPY . /app

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt && \
    pip3 uninstall -y pipenv virtualenv-clone virtualenv


CMD [ "python3", "/app/src/main.py" ]

EXPOSE 8000
