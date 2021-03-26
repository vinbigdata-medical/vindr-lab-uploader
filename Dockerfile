FROM python:3.8-buster

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./config /app/config
COPY connection /app/connection
COPY ./dbal /app/dbal
COPY ./middleware /app/middleware
COPY ./restapi /app/restapi
COPY ./tests /app/tests
COPY ./utils /app/utils

COPY ./app.py /app/app.py
COPY ./run.sh /app/run.sh
RUN chmod +x run.sh

ENTRYPOINT ["./run.sh"]
