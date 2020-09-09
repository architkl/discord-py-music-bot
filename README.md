# discord-py-music-bot

A music bot for discord using discord.py and lavalink

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install pipenv.

```bash
pip install pipenv
```

And then install dependencies in pipfile.

```bash
pipenv install
```

Download [Lavalink.jar](https://github.com/Frederikam/Lavalink/releases). application.yml required for Lavalink

Download and install java 11+ (I used java openjdk 14 on Ubuntu)

## Usage

Run lavalink server
```bash
java -jar Lavalink.jar
```

Create a .env file in the src folder with the following-
```bash
BOT_TOKEN=[your bot token]
PREFIX=[prefix for your bot commands]
FILE_NAME_REGEX=^[a-zA-Z0-9_]*$ (alphanumeric names for playlists)
```

Run pipenv
```bash
pipenv shell
python ./src/bot.py
```

Or you can run with nodemon (default.js required)
```bash
pipenv shell
nodemon ./src/bot.py
```