FROM python:3.7

#ADD . /bot

RUN mkdir /bot
ADD ./requirements.txt /bot/requirements.txt

RUN pip install -r /bot/requirements.txt
WORKDIR "/bot/src"

CMD ["python", "./bot.py"]