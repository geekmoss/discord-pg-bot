FROM python:3.7

#ADD . /bot

RUN mkdir /bot
RUN pip install -r /bot/requirements.txt
WORKDIR "/bot/src"

CMD ["python", "./bot.py"]