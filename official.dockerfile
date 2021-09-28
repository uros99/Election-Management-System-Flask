FROM python:3

RUN mkdir -p /opt/src/official
WORKDIR /opt/src/official

COPY applications/official/application.py application.py
COPY applications/official/configuration.py configuration.py
COPY applications/official/models.py models.py
COPY applications/official/roleCheck.py roleCheck.py
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "./application.py"]