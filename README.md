# AlphaDelta
A bot that does whatever their owner wants. Badly

# Installation

For the bot to work 100%, you need to FFmpeg and add the bin folder to path, yt-dlp and PyNaCl with discord Voice

**CHANGE THE data.txt INTO data.json**

## ffmpeg Installation Winows
- [ffmpeg link (Windows build by BtbN)](https://ffmpeg.org/download.html#build-windows)

- extract and rename to ffmpeg!

- Windows+S search for "System Environment"

- Environment Variables:

![2021-10-10 19_57_32-Window](https://user-images.githubusercontent.com/75881405/136694838-3b288ed4-f4fa-4fb4-9bc3-405712d4faa1.png)

- PATH -> Edit

![2021-10-10 19_57_44-Window](https://user-images.githubusercontent.com/75881405/136694839-a2887227-3c34-4e55-9857-2983d8beb23f.png)

- New -> Path to the ffmpeg\bin

![2021-10-10 19_57_57-Window](https://user-images.githubusercontent.com/75881405/136694845-49f313c1-3601-4d31-9341-6794b0304d02.png)

## Python libraries Installation

PyNaCl:
type this in a administrator command line or the terminal of pycharm:

`pip install -U discord.py[voice]`

Youtube-dl:

`pip install yt-dlp`

## Discord Bot Setup

Head to https://discord.com/developers/applications and create a new application

Head to the Bot tab and press Add new bot. The picture below is the required perms

![2021-10-10 20_24_12-Window](https://user-images.githubusercontent.com/75881405/136695665-bd2d8ced-a7af-48c1-8726-77d1e3142cae.png)

## Invite Discord Bot

create a link here, and paste it into your browser to invite the bot

![2021-10-10 20_22_59-Window](https://user-images.githubusercontent.com/75881405/136695727-8914b8df-868b-4261-8476-8063ee3fc15e.png)

## Data.json

Add your bot's token and and your discord's ID (enable developer mode in settings)

Copy your token here (Keep it secret!)
![2021-10-14 09_33_55-Window](https://user-images.githubusercontent.com/75881405/137235616-6094d016-0791-4ee9-be30-663a84b1d92c.png)

Copy your ID here
![2021-10-14 09_29_53-Discord](https://user-images.githubusercontent.com/75881405/137235705-3bf9dc20-60d0-4270-987f-7ccfc67a8f14.png)

![2021-10-14 09_32_53-bot-command - Discord](https://user-images.githubusercontent.com/75881405/137235726-c942bb1b-f4bc-4a9a-9fbf-7cd5339978ce.png)

and place the info into Data.json as such
![2021-10-14 09_35_56-data json - Notepad](https://user-images.githubusercontent.com/75881405/137235779-181e69ea-b10c-4afc-92a8-44de22103b5a.png)

## What does the JSON do

The headpats are just a way to keep track of the amount of times people complpimented the bot with !goodbot (prefix by default is !, changeable"

opID is to let the bot know who's able to do admin commands from discord chat, such as !unload or !reload the cogs

Token represents which bot is being run
