FROM python:3-slim

ADD requirements.txt /
RUN pip install -r requirements.txt
ADD docker-entrypoint.sh bot.py /

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["bot"]