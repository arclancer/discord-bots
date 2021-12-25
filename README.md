# Overview

This is a simple script to run a Discord bot based on the scripts in `utils`. Currently, it supports the retrieval of upcoming DOTA 2 matches within the next 24 hours.

## Setting up

Start by setting up a virtual environment and installing the requirements.

```
python3 -m venv discord_bot
source discord_bot/bin/activate
pip install -r requirements.txt
```

First, you will need to create a Discord bot and retrieve its token. You can do so by reading Discord's documentation [here](https://docs.discord.red/en/stable/bot_application_guide.html).

Next, to retrieve the streams for ongoing matches, you will need a Twitch account and generate your Client ID & Client Secret. You can do so by following
Step 1 of Twitch's API documentation [here](https://dev.twitch.tv/docs/api/).

Once you have the tokens, make a copy of `.env.example`, paste your tokens in it and rename it to `.env`:

```
This is an example of what your .env file should look like.
# env variables
DISCORD_TOKEN = abcdefg
TWITCH_CLIENT_ID = hijklmn
TWITCH_CLIENT_SECRET = opqrstu
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

The bot should reply with a message similar to this (truncated; the score will be hidden as a spoiler in the actual Discord message reply):

```
Team MagMa vs iG Vitality | Huya Winter Invitational 2021 Closed Qualifier | Bo2 | Score: 0:1 | ONGOING | https://twitch.tv/m3traNeo [RU]
-----------
Summit Gaming vs UD Vessuwan | Top Clans 2021 Winter Invitational | Bo3 | Score: 0:1 | ONGOING | https://twitch.tv/TopClansEsports [EN]
-----------
Aster.Aries vs LBZS | Intel World Open Beijing: Closed Qualifier | Bo3 | Score: 0:0 | ONGOING | https://twitch.tv/M_A_S_H_I_N_A [RU]
-----------
Aster.Aries vs iG Vitality | Huya Winter Invitational 2021 Closed Qualifier | Bo2 | December 19, 2021 - 07:00 PM
-----------
Nemiga Gaming vs B8 | DPC EEU 2021/22 Tour 1: Division II | Bo3 | December 19, 2021 - 07:00 PM
-----------
Cheese Ta3 Djelloul vs 5Comrades | FroggedTV League Season 8 | Bo3 | December 19, 2021 - 09:00 PM
-----------
Natus Vincere vs Team Unique | DPC EEU 2021/22 Tour 1: Division I | Bo3 | December 19, 2021 - 10:00 PM
```

## Closing

The bot is a work in progress; more scripts may be added in the future to `utils` to accommodate more features.






