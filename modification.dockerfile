FROM python:3

RUN mkdir -p /opt/src/modification
WORKDIR /opt/src/modification

COPY modification/application.py application.py
COPY modification/configuration.py configuration.py
COPY modification/models.py models.py
COPY modification/roleCheck.py roleCheck.py
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "./application.py"]