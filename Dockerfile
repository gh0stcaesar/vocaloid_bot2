FROM python:2.7-slim
ADD . /src
WORKDIR /src
RUN pip install -r requirements.txt
rmi $(docker ps -a -q)
CMD python ./bot/slack_bot.py
