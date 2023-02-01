# README

## Description
This code is a Discord bot that can play music, tell jokes and manage a queue of songs to play.

## Dependencies
- asyncio
- datetime
- os
- random
- re
- subprocess
- discord
- yt_dlp as youtube_dl
- praw
- time
- requests
- urllib.parse
- sys
- openai

## Usage
This bot uses the DISCORD_TOKEN environment variable for the Discord API token. Use `export DISCORD_TOKEN='your_token'` to set the token. 
And the OPENAI_TOKEN environment variable for the OPENAI API token. Use `export OPENAI_TOKEN='your_token'` to set the token.

The bot has the following commands:
- !play or !p [url] - Plays the song from the url
- !stop or !s - Stops the bot and clears the queue
- !download or !d [url] - Downloads the song from the url
- !queue or !q - Shows the queue
- !skip - Skips the current song
- !pause - Pauses the current song
- !resume - Resumes the current song
- !reset - Resets the bot
- !help - Shows this message
- !remove [url] - Removes the song from the queue
- !dplremove - Removes duplicate songs from the queue
- !clear - Clears the queue
- !shuffle - Shuffles the queue
- !alredydl - Prints all files already downloaded
- !status -
- !changestatus -
- !defaultstatus -
- !ping -
- !move -
- !leave -
- !volume -
- !creator -
- !invite -
- !joke -
- !random -
- !resetstatus -
- !rickroll -
- !fuck01 -
- !love01 -
- !restart -
- !createpl -
- !addtopl -
- !pl -
- !rmpl -
- !readpl -
- !chatgpt -
- !deletesong -
- !join -
- !playforce -
- !repeat -

## Note
You will need ffmpeg installed on your machine to play the audio.

