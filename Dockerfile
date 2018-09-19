FROM python:2.7-alpine
MAINTAINER NOSPAM <nospam@nnn.nnn>

COPY server-monitor.py /server-monitor.py
RUN chmod +x /server-monitor.py

ENV PYTHONUNBUFFERED=0

CMD ["sh", "-c", "PYTHONUNBUFFERED=0 eval python /server-monitor.py $OPTIONS"]
