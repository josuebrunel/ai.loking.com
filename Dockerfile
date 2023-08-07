FROM        python:3.11-slim

RUN         mkdir /opt/app
WORKDIR     /opt/app
ADD         . /opt/app
RUN         pip install -r requirements.txt
EXPOSE      8080
CMD         ["uvicorn", "--host", "0.0.0.0", "--port", "8080", "--workers", "10",  "app:app"]
