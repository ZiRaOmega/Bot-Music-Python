# README

## Description
This code is a Discord bot that can play music, tell jokes and manage a queue of songs to play.

## Dependencies
- asyncio
- os
- random
- discord
- youtube_dl
- pyjokes

## Usage
This bot uses the DISCORD_TOKEN environment variable for the Discord API token. Use `export DISCORD_TOKEN='your_token'` to set the token. 

The bot has the following commands:
- !play [song name]: plays the first result of a YouTube search of the song name.
- !joke: tells a random joke.
- !stop: stops the current song and clears the queue.
- !add [song name]: adds the first result of a YouTube search to the queue.
- !queue: shows the current queue of songs.
- !skip: skips the current song and plays the next song in the queue.

## Note
You will need ffmpeg installed on your machine to play the audio.

