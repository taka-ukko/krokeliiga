# krokeliiga
Telegram bot for [Konklaavi's](https://www.ayy.fi/fi/yhdistyslistaus/harrastukset-ja-pelit) kesäliiga scoring.

![Konklaavi logo](https://www.ayy.fi/sites/g/files/flghsv231/files/styles/o_567w_ah_d/public/2019-05/krokettikonklaavi_logo.jpg?itok=enFgO2yi)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development or production purposes.

### Prerequisites

Things that you need to install the software

```
SQLite
```
The bot uses a Sqlite3 database for data handling. To run the bot, you need either python 3 or Docker. 
It is suggested that development testing is done by running with python and production deployment by Docker.
This is because building Docker images takes rather long and most bugs can be seen already in the python environment.
```
For development:
Python

For deployment:
Docker
```

### Installing

A step by step series of examples that tell you how to get a development env running
Proceed with these instructions after you have installed Python3 on your machine and cloned this Git repository.
If you are looking for instructions on running the bot with Docker, see [Deployment](#deployment)

1. Create python virtual environment and install required packages
See tutorial for virtual environments [here](https://docs.python.org/3/tutorial/venv.html).

Example commands for Windows:
```
python3 -m venv tutorial-env
```
Activate virtual environment
```
tutorial-env\Scripts\activate.bat
```
Install packages
```
(cd \path\to\git-repo)
pip install -r requirements.txt
```

2. Set an enviromnent variable `KROKE_BOT` that is equal to the bot token you received from BotFather while creating your own bot in telegram.
On linux you can instead just give the environment variable each time you launch the bot:
```
KROKE_BOT=lha9837489jkah python krokebot.py
```

3. Launch the bot
```
python krokebot.py
```


## Deployment

This section provides you with instructions on how to deploy the bot in a Docker container

1. Install Docker and docker-compose on target system
2. Set environment variables `KROKE_BOT` and `DATABASE` where KROKE_BOT contains bot token and DATABASE contains absolute filepath to the `files` folder that will contain a log file, the SQLite database file and a list of permitted admins.
An easy way to execute the previous step is to write the environment variables to a `.env` file and provide it to docker-compose at launch. 
Example contents of a `.env` file :
```
DATABASE=/path/to/files-folder
KROKE_BOT=kja79834nksan3k4j
```
3. Launch bot with docker-compose
> You must execute the next docker-compose launch command from the same folder where your .env file is!

To make sure your docker container has the latest files and edits, you should use `--build` argument, which causes docker-compose to build a new docker image if any file has changed. This also necessary when launching the bot for the first time.
```
docker-compose -f /path/to/git-repo/docker-compose.yml up -d --build krokeliigabot
```
If any already have the latest docker image, that is, a docker image that was build with the latest python files, you may omit `--build` arguiment.
```
docker-compose -f /path/to/git-repo/docker-compose.yml up -d krokeliigabot
```
