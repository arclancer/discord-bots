# Overview

This is a simple script to run a Discord bot based on the scripts in `utils`. Currently, it supports the retrieval of upcoming DOTA 2 matches.

## Setting up

Start by setting up a virtual environment and installing the requirements.

```
python3 -m venv virtual_env
source virtual_env/bin/activate
pip install -r requirements.txt
```

First, you will need to create a Discord bot and retrieve its token. You can do so by reading Discord's documentation [here](https://docs.discord.red/en/stable/bot_application_guide.html).

Once you have its token, make a copy of `.env.example`, paste your bot token in it and rename it to `.env`:

```
# env variables
DISCORD_TOKEN = YOUR_TOKEN_HERE
```

Next, you will need to invite the bot to your server to use it. In your application homepage, navigate to OAuth2, and click on URL Generator to generate an invite link
for your Discord bot. The link should look something like this: `https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&permissions={PERMISSIONS}&scope=bot`

Paste the link in your browser, and proceed with the invitation.

## Running the bot

With the bot in your server, simply run the script in your terminal:

```
python3 bot.py
```

## Output example

Once the bot is up and running, try it out by sending it a command, `!dota_matches`.

The bot should reply with a message similar to this:

```
Lilgun vs Talon Esports | DPC SEA 2021/22 Tour 1: Division II | Bo3 | December 15, 2021 - 01:00 PM | https://twitch.tv/Beyond_the_Summit
-----------
T1 vs Motivate.Trust Gaming | DPC SEA 2021/22 Tour 1: Division I | Bo3 | December 15, 2021 - 04:00 PM | https://twitch.tv/Beyond_the_Summit
-----------
BOOM Esports vs Team SMG | DPC SEA 2021/22 Tour 1: Division I | Bo3 | December 15, 2021 - 07:00 PM | https://twitch.tv/Beyond_the_Summit
-----------
Team Liquid vs Tundra Esports | DPC WEU 2021/22 Tour 1: Division I | Bo3 | December 15, 2021 - 10:00 PM | https://twitch.tv/DreamLeague
```

## Closing

The bot is a work in progress; more scripts may be added in the future to `utils` to accommodate more features.






