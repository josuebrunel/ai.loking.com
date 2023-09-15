# BUILD
FROM        python:3.11-slim AS build
RUN         mkdir /opt/app
RUN         python -m venv /opt/app/venv/
ENV         VIRTUAL_ENV=/opt/app/venv
ENV         PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR     /opt/app
COPY        requirements.txt /opt/app/requirements.txt
RUN         pip install -r requirements.txt

# RUN
FROM        python:3.11-slim AS run
RUN         apt update && apt upgrade -y
RUN         apt install tesseract-ocr -y
RUN         apt install poppler-utils -y
RUN         mkdir /opt/app
ENV         VIRTUAL_ENV=/opt/app/venv/
ENV         PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR     /opt/app/
COPY        app/ /opt/app/app/
COPY        --from=build /opt/app/venv/ /opt/app/venv/
EXPOSE      8080
CMD         ["uvicorn", "--host", "0.0.0.0", "--port", "8080", "--workers", "10",  "app:app"]
