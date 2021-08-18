FROM python:3

RUN mkdir -p /opt/src/deamon
WORKDIR /opt/src/deamon

COPY applications/deamon/application.py application.py
COPY applications/deamon/configuration.py configuration.py
COPY applications/deamon/models.py models.py
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "./application.py"]