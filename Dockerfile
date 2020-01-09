FROM        python:3.7-slim
WORKDIR     /app
COPY        requirements.txt .
RUN         pip install -r requirements.txt
COPY        sidecar/* ./sidecar/
COPY        main.py ./
RUN         chmod 777 -R ./
ENV         PYTHONUNBUFFERED=1
CMD         [ "python", "-u", "/app/main.py" ]
