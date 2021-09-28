FROM python:3

RUN mkdir -p /opt/src/admin
WORKDIR /opt/src/admin

COPY applications/admin/application.py application.py
COPY applications/admin/configuration.py configuration.py
COPY applications/admin/models.py models.py
COPY applications/admin/roleCheck.py roleCheck.py
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "./application.py"]