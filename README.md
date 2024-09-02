[![build](https://github.com/plasticuproject/pwnedBot/actions/workflows/python-app.yml/badge.svg)](https://github.com/plasticuproject/pwnedBot/actions/workflows/python-app.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-311/)
[![CodeQL](https://github.com/plasticuproject/pwnedBot/actions/workflows/codeql.yml/badge.svg)](https://github.com/plasticuproject/pwnedBot/actions/workflows/codeql.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=plasticuproject_pwnedBot&metric=alert_status)](https://sonarcloud.io/dashboard?id=plasticuproject_pwnedBot)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=plasticuproject_pwnedBot&metric=security_rating)](https://sonarcloud.io/dashboard?id=plasticuproject_pwnedBot)

# pwnedBot
pwnedBot is a Discord bot implementation of Troy Hunt's haveibeenpwned.com service, a free resource for anyone to quickly assess if they may have been put at risk due to an online account of theirs having been compromised or "pwned" in a data breach. This document outlines the steps required to build, run, and manage the bot using Docker.

## Prerequisites

Before proceeding, ensure you have Docker installed and running on your machine. You will also need Python installed if you plan to initialize the database manually before running the bot in a Docker container.

## Building the Bot

To build the Docker image for PwnedBot, navigate to the directory containing the Dockerfile and run the following command:

```sh
docker build -t pwnedbot .
``` 

This command builds a Docker image named `pwnedbot` based on the instructions in the `Dockerfile` located in the current directory.

## Configuring Environment Variables

Head over to [DiscordApp](https://discordapp.com/developers/applications/me "DiscordApp") and create a new app. Record your *Client_ID*. On the left, click **Bot**, and then **Add Bot**. Once you are done setting up your bot, save your *Client_ID*, *Token*, and *Client Secret* in a safe place.

Making calls to the haveibeenpwned API requires a key. You can purchase a HIBP-API-KEY [here](https://haveibeenpwned.com/API/Key "HIBP-API-KEY").

Create an `.env` file in the project root directory and add the required information:

```
HIBP_API_KEY="test-key"
APP_NAME="test-app"
DISCORD_TOKEN=TOKEN
DISCORD_CLIENT_ID=ID
BOT_PREFIX="!"
DEFAULT_ACCOUNT="test@example.com"
```

Make sure to replace the default information with your actual values. 

## Running the Bot

To start the bot, use the following command to run the Docker container. This command also mounts the necessary directories and files into the container and redirects all output to `output.log`:

```
docker run -it --rm -v $(pwd)/.env:/home/bot/.env pwnedbot > output.log 2>&1
``` 

This will log all output from the bot to `output.log`, allowing you to review it later for debugging and monitoring purposes.

## Running the bot in detached mode

If you wish to run the bot container in detached mode and still record its output to a log file, you may do so with the folloing commands:


Run the Docker container in detached mode:

```sh
PWNEDBOT_ID=$(docker run -d -it --rm -v $(pwd)/.env:/home/bot/.env pwnedbot)
```

Start logging to a file:

```sh
docker logs -f $PWNEDBOT_ID > output.log 2>&1 & PWNEDBOT_LOG_PID=$!
```

Stop the bot container:

```sh
docker stop $PWNEDBOT_ID
```

Kill the logging process if needed:

```sh
kill $PWNEDBOT_LOG_PID
```

## Usage
To add bot to server add your *Client_ID* to this URL and visit in browser:  <br />
`https://discordapp.com/oauth2/authorize?client_id= <Client_ID> &scope=bot` <br />
When bot is active in server type "(prefix)help" for a list of commands.

![HELP](https://github.com/plasticuproject/pwnedBot/raw/master/images/help.png)
![BREACH_NAME](https://github.com/plasticuproject/pwnedBot/raw/master/images/breach_name.png)
![PASSWORD](https://github.com/plasticuproject/pwnedBot/raw/master/images/password.png)
![SEARCH](https://github.com/plasticuproject/pwnedBot/raw/master/images/search.png)
![PASTES](https://github.com/plasticuproject/pwnedBot/raw/master/images/pastes.png)
![PASTE_ID](https://github.com/plasticuproject/pwnedBot/raw/master/images/paste_id.png)

## License
All data sourced from https://haveibeenpwned.com <br />
Visit https://haveibeenpwned.com/API/v3 to read the Acceptable Use Policy <br />
for rules regarding acceptable usage of this API. <br />

This work is licensed under a [Creative Commons Attribution 4.0 International License.](https://creativecommons.org/licenses/by/4.0/) <br />
![CCv4](https://haveibeenpwned.com/Content/Images/CreativeCommons.png) <br />
plasticuproject

