FROM python:3.8-buster

COPY requirements.txt /bot
WORKDIR /bot
RUN pip install -r requirements.txt
COPY . /bot
ENTRYPOINT ["python"]
CMD ["/bot/krokebot.py"]
