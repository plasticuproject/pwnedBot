# pwnedBot
A Discord bot implementation of Troy Hunt's haveibeenpwned.com service,  <br />
a free resource for anyone to quickly assess if they may have been put <br />
at risk due to an online account of theirs having been compromised or <br />
'pwned' in a data breach, using the hibpwned python library. <br />


## Requirments
Python 3.6+, pip, and Curl
```
pip install -r requirements.txt
pip install -U discord.py
```

## Installation
Head over to [Discord](https://discordapp.com/developers/applications/me "Discord") and create a new app. <br />
Record your *Client_ID*. On the left, click *Bot*, and then *Add Bot*. <br />
Once you are done setting up your bot, record the *Token* and *Client Secret*. <br />

Making calls to the HIBP API requires a key. You can purchase an HIBP-API-Key at
https://haveibeenpwned.com/API/Key <br />

In pwned_bot.py replace all <...> with appropriate information. <br />

To start bot, run:
```
python pwned_bot.py
```
To add bot to server add your *Client_ID* to this URL and visit in browser:  <br />
https://discordapp.com/oauth2/authorize?client_id= *Client_ID* &scope=bot <br />

## Usage
When bot is active in server type "!help" for a list of commands.

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
