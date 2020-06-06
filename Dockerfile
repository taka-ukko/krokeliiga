FROM python:3.8-buster

COPY . /bot
WORKDIR /bot
RUN pip install -r ./requirements.txt
ENTRYPOINT ["python"]
CMD ["/bot/krokebot.py"]