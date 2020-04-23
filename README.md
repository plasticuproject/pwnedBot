# pwnedBot
A Heroku hosted Discord bot implementation of Troy Hunt's haveibeenpwned.com service,  <br />
a free resource for anyone to quickly assess if they may have been put <br />
at risk due to an online account of their's having been compromised or <br />
"pwned" in a data breach, using the hibpwned python library. <br />


## Prerequisites 
Head over to [DiscordApp](https://discordapp.com/developers/applications/me "DiscordApp") and create a new app. <br />
Record your *Client_ID*. On the left, click **Bot**, and then **Add Bot**. <br />
Once you are done setting up your bot, save your *Client_ID*, *Token*, and *Client Secret* in a safe place. <br />

Making calls to the haveibeenpwned API requires a key. You can purchase a HIBP-API-KEY
[here](https://haveibeenpwned.com/API/Key "HIBP-API-KEY"). <br />

Create a [Heroku](https://heroku.com "Heroku") account and install the [Heroku CLI Tool](https://devcenter.heroku.com/articles/heroku-cli#download-and-install "Heroku CLI Tool"). Follow the directions and to log into your account to authenticate. <br />
If [git](https://git-scm.com/downloads "git") is not already installed on your host, install it. <br />

## Heroku Deployment
Create a fork of this repository, then clone it to your local host with the `git clone` command. <br />
Navigate into the project's root directory and run `heroku create`. <br />
Set the environment variables that the application will use with the `heroku config:set` command, setting the following variables:
```
heroku config:set HIBP_API_KEY=<your HIBP-API-KEY>
heroku config:set APP_NAME=<a unique app name for haveibeenpwned to recognize your app/bot>
heroku config:set DISCORD_TOKEN=<your discord bot TOKEN>
heroku config:set DISCORD_CLIENT_ID=<your discord CLIENT_ID>
heroku config:set BOT_PREFIX=<a prefix for your bot commands>
```
To deploy, push the code to your Heroku account with the command `git push heroku master` <br />


## Development
### Requirements
- git >= 2.17.1
- Python >= 3.6.9
- python3-pip >= 20.0.2
    - hibpwned >= 1.1.1
    - Pillow >= 7.1.1
    - discord.py >= 1.3.3

Follow the steps above to deploy your application. <br />
Log into your **Heroku** account, choose your **app**, and under **Deploy** click **Connect to Github** and follow the directions to link your project. <br />
Now when you push changes to your Github project, they will automatically be deployed on your Heroku container. <br />


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
