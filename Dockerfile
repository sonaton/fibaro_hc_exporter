FROM python:3-slim

RUN pip install requests prometheus_client

ADD parse.py /opt

EXPOSE 8000

CMD python /opt/parse.py
