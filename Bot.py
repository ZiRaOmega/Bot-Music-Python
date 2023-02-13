
import asyncio
import datetime
import os
import random
import re
import subprocess
import discord
import yt_dlp as youtube_dl
import praw
import time
import requests
import urllib.parse
import sys
import openai
from utils import * # import all functions from utils.py
from z01 import * # import all functions from z01.py

# Set up the model and prompt
model_engine = "text-davinci-003"
""" import lyrics_fetcher """
ADMIN_MODE = True
# use env variables for token
TOKEN = os.environ.get('DISCORD_TOKEN')
openai.api_key = os.environ.get('OPENAI_TOKEN')
song_queue = []
mapsongurl = {}
REPEAT = False
SEEK = "0:00"
TokenStartCheck(openai,TOKEN)
client = discord.Client(intents=discord.Intents.all())

ytdl_opts = {
    'format': 'worstaudio/worst',
    'outtmpl': '%(title)s.%(ext)s',
    'restrictfilenames': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': False,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'max_downloads': 5,
    'source_address': '0.0.0.0'
}

ytdl = youtube_dl.YoutubeDL(ytdl_opts)


@client.event
async def on_message(message):
    await HandleMessageEvent(message, song_queue)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    CreateQueueFile()
    channel=None
    try:
        CHANNEL_ID = int(GetChannelID())
        channel = client.get_channel(CHANNEL_ID)
    except: 
        pass
    if channel is None:
        print("Channel not found")
    else:
        await channel.send(":green_circle: Bot is online")
    #ReadQueueFile()
    await DefaultStatus()


async def DefaultStatus():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help; Create a Channel named 'commands' to use the bot"))


async def ChangeStatus(music_name):
    print("Changing status to " + music_name)
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=fileNameFormatted(music_name)))


async def DownloadVideo(song_name):
    with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
        info = ydl.extract_info("ytsearch:" + song_name,
                                download=False)['entries'][0]
        file_name = ydl.prepare_filename(info)
        url = info['webpage_url']
        if os.path.exists(file_name):
            return file_name, url
        else:
            # Download the video as file_name
            subprocess.Popen(["python3", "downloadytb.py", song_name])
            print(file_name)
            return file_name, url

async def STREAM_play_song(vc, message, url, channel):
    global REPEAT
    global SEEK
    while len(song_queue) > 0:

        print(song_queue)
        if not client.voice_clients:
            vc = await channel.connect()
        x = mapsongurl[song_queue[0]]
        await message.channel.send(':play_pause: Playing ' + fileNameFormatted(x))
        await ChangeStatus(x)
        vc.play(discord.FFmpegPCMAudio(x,options="-vn -ss "+SEEK))
        SEEK = "0:00"
        while vc.is_playing() or vc.is_paused():
            await asyncio.sleep(1)
        vc.stop()
        if not REPEAT:
            song_queue.pop(0)
            PopSongFromQueueFile()
    await vc.disconnect()
    await DefaultStatus()
async def play_song(vc, message, url, channel):
    global REPEAT
    global SEEK
    while len(song_queue) > 0:

        print(song_queue)
        if not client.voice_clients:
            vc = await channel.connect()
        x=song_queue[0]
        await ChangeStatus(x)
        await message.channel.send(':play_pause: Playing ' + fileNameFormatted(x))
        x = mapsongurl[song_queue[0]]
        vc.play(discord.FFmpegPCMAudio(x,options="-vn -ss "+SEEK))
        vc.source = discord.PCMVolumeTransformer(vc.source)
        vc.source.volume = 0.1
        SEEK = "0:00"
        while vc.is_playing() or vc.is_paused():
            await asyncio.sleep(1)
        vc.stop()
        if not REPEAT:
            song_queue.pop(0)
            PopSongFromQueueFile()
    await vc.disconnect()
    await DefaultStatus()

async def STREAM_PlayUniqueSong(url,channel,message,client):
    print('Playing ' + url)
    vc = await GetVocalClient(client, channel, message)
    vc.play(discord.FFmpegPCMAudio(url,options="-vn"))
    while vc.is_playing() or vc.is_paused():
        await asyncio.sleep(1)
    vc.stop()
def search_and_download_music(song_name):
    # Search and download the first result
    with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
        info = ydl.extract_info("ytsearch:" + song_name,
                                download=False)['entries'][0]
        file_name = ydl.prepare_filename(info)
        url = info['webpage_url']
        if os.path.exists(file_name):
            return file_name, url
        else:
            # Download the video as file_name
            if len(song_queue) == 0:
                try:
                    ydl.download(["ytsearch:" + song_name])
                except:
                    ydl.download(["ytsearch:" + song_name])
            else:
                subprocess.Popen(["python3", "downloadytb.py", song_name])
            print(file_name)
            return file_name, url
def STREAM_search_and_download_music(song_name):
    # Search and download the first result
    with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
        info = ydl.extract_info("ytsearch:" + song_name,
                                download=False)['entries'][0]
        url = info['url']
        ytb_title = info['title']
        
    return url, ytb_title



CurrentSong = None


async def HandleMessageEvent(message, song_queue):
    global CurrentSong
    global mapsongurl
    channel = None
    if message.author == client.user or message.channel.name != "commands":
        return
    SetChannelID(str(message.channel.id))
    if message.author.voice is not None:
        # await message.channel.send('You are not in a voice channel')
        channel = message.author.voice.channel
    if message.content.startswith('!'):
        # Parse all old bot message and delete them
        i = 0
        async for msg in message.channel.history(limit=2):
            if message.content.startswith('!chatgpt '):
                continue
            if msg.author == client.user and msg != message and i < 2:
                try:
                    await msg.delete()
                except:
                    pass
            elif msg.content.startswith('!') and msg != message and i < 2:
                try:
                    await msg.delete()
                except:
                    pass
            i += 1
    if message.content.startswith('!play ') or message.content.startswith('!p '):
        CreateHistoryFile()
        if channel != None:
            print(song_queue)
            if message.content.startswith('!p '):
                message.content = '!play' + message.content[2:]
            print(message.content[6:])
            url = message.content[6:]
            username = message.author.name
            WriteHistoryFile(url, username)
            
            # check if url is url or search term
            if not url.startswith('http') or not url.startswith('https'):
                await message.channel.send(':magnet: Downloading ' + url)
                file_name, url = search_and_download_music(url)
                #url,file_name=STREAM_search_and_download_music(url)
                await message.channel.send(':mag: Found ' + file_name)
            else:
                file_name, url = await DownloadVideo(url)
                if file_name is None:
                    await message.channel.send(':mag: Could not find ' + url)
                    return
                await message.channel.send(':magnet: Downloaded ' + url)
            song_queue.append(file_name)
            
            mapsongurl[file_name]=file_name
            WriteSongToQueueFile(file_name)
            CurrentSong = file_name
            if os.path.exists(file_name):
                if len(song_queue) > 0:
                    # if bot not connected to voice channel
                    #vc = GetVocalClient(client, channel, message)
                    if not client.voice_clients:
                        vc = await channel.connect()
                    else:
                        await message.channel.send(":heavy_plus_sign: "+url+' Added to queue')
                        return
                    await play_song(vc, message, url, channel)
                else:
                    vc = await GetVocalClient(client, channel, message)
                    await message.channel.send(':arrow_forward: Playing ' + fileNameFormatted(file_name))

                    vc.play(discord.FFmpegPCMAudio(file_name))
                    while vc.is_playing():
                        await asyncio.sleep(1)
                    vc.stop()
                    
                    # remove song from folder
                    # os.remove(file_name)
                    await vc.disconnect()
                    await DefaultStatus()
            else:
                await message.channel.send(':arrow_forward: Playing ' + fileNameFormatted(file_name))
                #await STREAM_PlayUniqueSong(url, channel, message,client)
        else:
            await message.channel.send(':negative_squared_cross_mark: You are not connected to a voice channel')
    elif message.content.startswith('!stop') or message.content.startswith('!s '):
        for x in client.voice_clients:
            if (x.guild == message.guild):
                await x.pause()
                break
        for file_name in song_queue:
            os.remove(file_name)
        song_queue.clear()
        await DefaultStatus()
    elif message.content.startswith('!download') or message.content.startswith('!d '):
        url = message.content[10:]
        file_name, url = await DownloadVideo(url)
        if file_name is None:
            await message.channel.send(':negative_squared_cross_mark: Could not find ' + url)
            return
        await message.channel.send(":magnet: Downloaded " + url + "You can Now play it with !play " + url)
    elif message.content==('!queue') or message.content==('!q '):
        # remove the sended message from the channel
        song_queueFormatted = ""
        i = 0
        for x in song_queue:
            if i == 0:
                song_queueFormatted += "Now Playing: "+fileNameFormatted(x)+"\n"
                i += 1
                continue
            song_queueFormatted += str(i)+": " + fileNameFormatted(x) + "\n"
            i += 1
        if song_queueFormatted == "":
            song_queueFormatted = "Queue is empty"
        await message.channel.send(song_queueFormatted)
    elif message.content.startswith('!skip'):
        
        for x in client.voice_clients:
            if (x.guild == message.guild):
                if x.is_playing():
                    x.stop()
                    await message.channel.send(':fast_forward: Skipped')
                elif len(song_queue) > 0:
                    song_queue.pop(0)
                    await message.channel.send(':fast_forward: Skipped')
                break
        if len(song_queue) == 0:
            await x.disconnect()
        await DefaultStatus()
    elif message.content.startswith('!pause'):
        
        for x in client.voice_clients:
            if (x.guild == message.guild):
                x.pause()
                break
        await message.channel.send(':pause_button: Paused')
    elif message.content.startswith('!resume'):
        
        if len(song_queue) > 0:
            if not client.voice_clients:
                vc = await channel.connect()
                await play_song(vc, message, song_queue[0], channel)
            else:
                for x in client.voice_clients:
                    if (x.guild == message.guild):
                        x.resume()
                        break
            await message.channel.send(':arrow_forward: Resumed')
        else:
            await message.channel.send(':island: Queue is empty')
    elif message.content.startswith('!reset'):
        
        for x in client.voice_clients:
            await x.disconnect()
        song_queue.clear()
    elif message.content.startswith('!help'):
        await message.channel.send("Create a Channel named 'commands' to use the bot\n\nCommands:\n!play or !p [url] - Plays the song from the url\n!stop or !s - Stops the bot and clears the queue\n!download or !d [url] - Downloads the song from the url\n!queue or !q - Shows the queue\n!skip - Skips the current song\n!pause - Pauses the current song\n!resume - Resumes the current song\n!reset - Resets the bot\n!help - Shows this message\n!remove [url] - Removes the song from the queue\n!dplremove - Removes duplicate songs from the queue\n!clear - Clears the queue\n!shuffle - Shuffles the queue\n!alredydl - Prints all files already downloaded\n!volume - Change volume (Need to be between 0 and 1 like 0.5)\n!insert 'song position' 'position to insert' - insert a song currently in queue to position given \nAdditional commands: !status, !changestatus, !defaultstatus, !ping, !move, !leave,  !creator, !invite, !joke, !random, !resetstatus, !rickroll, !restart, !createpl, !addtopl, !pl, !rmpl, !readpl, !deletesong, !join, !playforce, !repeat")
    elif message.content.startswith('!remove'):
        songToRemove = message.content[8:]
        if songToRemove in song_queue:
            song_queue.remove(songToRemove)
            await message.channel.send(songToRemove + " removed from queue")
        else:
            await message.channel.send(songToRemove + " not found in queue")
    elif message.content.startswith('!dplremove'):
        # remove duplicate songs from queue
        song_queue = list(dict.fromkeys(song_queue))
        await message.channel.send("Removed duplicate songs from queue")
    elif message.content.startswith('!clear'):
        for file_name in song_queue:
            try:
                os.remove(file_name)
            except:
                continue
        Current=song_queue[0]
        song_queue.clear()
        song_queue.append(Current)
        RewriteQueueFile(song_queue)
        await message.channel.send("Cleared queue")
    elif message.content.startswith('!shuffle'):
        current_song = song_queue[0]
        song_queue.pop(0)
        random.shuffle(song_queue)
        song_queue.insert(0, current_song)
        RewriteQueueFile(song_queue)
        await message.channel.send("Shuffled queue")
    elif message.content.startswith('!alredydl'):
        result = ""
        # read all files in folder
        i=0
        for file in os.listdir():
            # if file is webm
            if file.endswith(".webm"):
                # remove .webm
                file = file.replace(".webm", "")
                # add to result
                result += file + "\n"
                i += 1
                if i == 10:
                    await message.channel.send(result)
                    result = ""
                    i = 0
        if i != 0:
            await message.channel.send(result)
    elif message.content.startswith('!status'):
        await message.channel.send(":play_pause: Playing " + fileNameFormatted(mapsongurl[song_queue[0]]))
    elif message.content.startswith('!changestatus'):
        status = message.content[14:]
        await client.change_presence(activity=discord.Game(name=status))
    elif message.content.startswith('!defaultstatus'):
        await DefaultStatus()
    elif message.content.startswith('!ping'):
        # count time it takes to send message
        start = time.time()
        await message.channel.send('Pong!')
        end = time.time()
        ping = round((end - start)*1000)
        await message.channel.send('Ping: ' + str(ping) + 'ms')
    elif message.content.startswith('!move'):
        channel = message.content[6:]
        for x in client.voice_clients:
            if (x.guild == message.guild):
                await x.move_to(channel)
                break
    elif message.content==('!join'):
        if not client.voice_clients:
            channel = message.author.voice.channel
            await channel.connect()

    elif message.content.startswith('!leave'):
        for x in client.voice_clients:
            if (x.guild == message.guild):
                await x.disconnect()
                break
    elif message.content.startswith('!volume') or message.content=='!volume':
        volume = message.content[8:]
        if volume == "":
            for x in client.voice_clients:
                if (x.guild == message.guild):
                    CurrentVolume = x.source.volume
                    await message.channel.send(":speaker: Volume is " + str(CurrentVolume))
                    return
        volume = float(volume)
        if volume >2:
            volume = 2
            await message.channel.send(":speaker: Volume needs to be between 0 and 1 like 0.5")
        for x in client.voice_clients:
            if (x.guild == message.guild):
                
                x.source = discord.PCMVolumeTransformer(x.source)
                x.source.volume = volume
                break
        await message.channel.send(":speaker: Volume set to " + str(volume))
    elif message.content.startswith('!creator'):
        await message.channel.send(":crown: Created by: ZiRa_Omega")
    elif message.content.startswith('!invite'):
        await message.channel.send("https://discord.com/api/oauth2/authorize?client_id=765308076500254730&permissions=8&scope=bot")
    elif message.content.startswith('!joke'):
        Joke = await JokefromReddit()
        toPrint = Joke.baseurl+"\n"+Joke.title + "\n" + Joke.body + "\n" + Joke.url
        await message.channel.send(toPrint)
    elif message.content.startswith('!random'):
        songs = []
        for file in os.listdir():
            if file.endswith(".webm") or file.endswith(".m4a"):
                songs.append(file)
        random_song = random.choice(songs)
        await message.channel.send(":play_pause: Playing " + fileNameFormatted(random_song))
        if len(song_queue) == 0:
            song_queue.append(random_song)
            
            mapsongurl[random_song]=random_song
            WriteSongToQueueFile(random_song)
            await PlaySong(random_song, channel, message)
        else:
            song_queue.append(random_song)
            
            mapsongurl[random_song]=random_song
            WriteSongToQueueFile(random_song)
    elif message.content.startswith('!resetstatus'):
        await DefaultStatus()
    elif message.content.startswith('!rickroll'):
        await message.channel.send("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        # if sender is connected to voice channel
        if message.author.voice:
            if not client.voice_clients:
                vc = await channel.connect()
            file_name, url = await DownloadVideo("rick astley never gonna give you up")
            await PlaySong(file_name, channel, message)
        else:
            rickLyrics = "Never gonna give you up\nNever gonna let you down\nNever gonna run around and desert you\nNever gonna make you cry\nNever gonna say goodbye\nNever gonna tell a lie and hurt you"
            await message.channel.send(rickLyrics)
    elif message.content.startswith('!fuck01'):
        # ping 10.10.0.30 if down return
        global ADMIN_MODE
        ping = os.system("ping -c 1 10.10.0.30")
        if ping != 0:
            await message.channel.send("Not in da hood")
            if not ADMIN_MODE:
                return
        else:
            await message.channel.send("In da hood")
        # if message doesnt contain username return
        if len(message.content) < 9:
            await message.channel.send("Please enter a username")
            return
        UserName = message.content[8:]
        Move = SwitchDoor(True)
        print("Move: "+str(Move))

    elif message.content.startswith('!love01'):

        # ping 10.10.0.30 if down return
        ping = os.system("ping -c 1 10.10.0.30")
        if ping != 0:
            await message.channel.send("Not in da hood")
            return
        else:
            await message.channel.send("In da hood")
        # if message doesnt contain username return
        if len(message.content) < 9:
            await message.channel.send("Please enter a username")
            return
        UserName = message.content[8:]
        errORsession, messer = login(UserName)
        if err != "Error":
            err = None
        elif err == "Error":
            await message.channel.send(messer)
            return
        else:
            await message.channel.send(messer)
            EnterFuck01(UserName)
    elif message.content.startswith('!restart'):
        # restart the bot
        await message.channel.send(":repeat: Restarting...")
        # os.system("bash restart.sh") using subprocess
        #subprocess.Popen(["bash", "StartBot.sh"])
        os.system("bash StartBot.sh")
        exit()
    elif message.content.startswith('!createpl'):
        playlist_name = message.content[10:]
        # Create file like playlist_name_playlist.txt
        CreatePlaylistFile(playlist_name)
    elif message.content.startswith('!addtopl'):
        query = message.content.split(" ")
        if len(query) < 3:
            await message.channel.send("Please enter a playlist name and a song name")
            return
        playlist_name = query[1]
        query.pop(0)
        query.pop(0)
        # Join the query to get the song name
        song_name = " ".join(query)
        WritePlaylistFile(playlist_name, song_name)
        await message.channel.send(":heavy_plus_sign: Added "+song_name+" to "+playlist_name)
    elif message.content.startswith('!pl '):
        
        playlist_name = message.content[4:]
        plsong_queue = StartPlaylist(playlist_name)
        if len(song_queue)>0:
            vc = await GetVocalClient(client, channel, message)
            if vc.is_playing():
                await message.channel.send("Playlist added to queue")
                return
        if len(plsong_queue) == 0:
            await message.channel.send("Playlist is empty")
            return
        else:
            vc = await GetVocalClient(client, channel, message)
            await message.channel.send("Playing playlist "+playlist_name)
            while len(song_queue) > 0:
                await message.channel.send("Playing "+fileNameFormatted(song_queue[0]))
                await PlayUniqueSong(vc, song_queue[0])
                plsong_queue.pop(0)
                song_queue.pop(0)
                PopSongFromQueueFile()
            await play_song(vc, message, song_queue[0], channel)
            await message.channel.send("Playlist Ended")
    elif message.content.startswith('!rmpl'):
        playlist_name = message.content[6:]
        # Remove file like playlist_name_playlist.txt
        RemovePlaylistFile(playlist_name)
        await message.channel.send("Playlist removed")
    elif message.content == ('!pllist'):
        # List all playlist
        toSend=ListPlaylist()
        await message.channel.send(toSend)
    elif message.content.startswith('!readpl '):
        playlist_name = message.content[8:]
        # Read playlist file
        toSend=ReadPlaylistFile(playlist_name)
        await message.channel.send(toSend)
    elif message.content==('!playforce'):
        if len(song_queue) == 0:
            await message.channel.send("Queue is empty")
            return
        else:
            await message.channel.send("Playing "+fileNameFormatted(song_queue[0]))
            vc = await GetVocalClient(client, channel, message)
            await play_song(vc, message, song_queue[0], channel)
    elif message.content == ('!history') or message.content.startswith('!history '):
        opts = message.content[9:]
        if opts == "":
            opts = "10"
        await ReadHistoryFile(message,opts)
    elif message.content == ('!createhistory'):
        CreateHistoryFile()
        await message.channel.send("History file created")
    elif message.content.startswith('!chatgpt '):
        prompt = message.content[9:]
        # Generate a response
        completion = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )

        response = completion.choices[0].text
        await message.channel.send(response)
    elif message.content=="!repeat":
        global REPEAT
        REPEAT = not REPEAT
        if REPEAT:
            await message.channel.send("Repeat is now on for "+fileNameFormatted(mapsongurl[song_queue[0]]))
        else:
            await message.channel.send("Repeat is now off")
    elif message.content.startswith('!deletesong '):
        songtodelete = message.content[12:]
        if songtodelete.isdigit():
            songtodelete = int(songtodelete)
            if songtodelete == 0:
                await message.channel.send("Can't delete the current song use !skip to skip the current song")
                return
            if songtodelete < len(song_queue):
                await message.channel.send("Song deleted : "+song_queue[songtodelete])
                song_queue.pop(songtodelete)
            else:
                await message.channel.send("Song not found try !queue to see the queue and use !deletesong <number>")
        else:
            for song in song_queue:
                if songtodelete in song:
                    song_queue.remove(song)
                    await message.channel.send("Song deleted : "+song)
                    return
    elif message.content.startswith("!seek "):
        seek = message.content[6:]
        global SEEK
        
        #Regex for 0:00
        if re.match("^[0-9][0-9]:[0-9][0-9]$", seek) or re.match("^[0-9]:[0-9][0-9]$", seek) or re.match("^[0-9][0-9]:[0-9]$", seek) or re.match("^[0-9]:[0-9]$", seek):
            await message.channel.send("Seeking to "+seek)
            vc=await GetVocalClient(client, channel, message)
            #stop the song
            
            if vc.is_playing():
                
                SEEK = seek
                #Insert at the index 1 of the queue the song at index 0 without removing the song at index 1
                if not REPEAT:
                    song_queue.insert(1, song_queue[0])
                vc.stop()
                
        else:
            await message.channel.send("Invalid seek format")
    elif message.content.startswith("!ps "):
        song_name=message.content[4:]
        url, title = STREAM_search_and_download_music(song_name)
        if len(song_queue)>0:
            await message.channel.send("Song added to queue : "+title)
            song_queue.append(title)
            mapsongurl[title]=url
            return
        song_queue.append(title)
        mapsongurl[title]=url
        await message.channel.send("Playing "+fileNameFormatted(title) )
        await STREAM_PlayUniqueSong(url,channel,message,client)
    elif message.content.startswith("!dallE "):
        prompt = message.content[7:]
        ImageCreation = openai.Image.create(
            prompt=prompt,
            n=1,
            size="256x256",
        )
        ImageUrl = ImageCreation["data"][0]["url"]
        embedVar = discord.Embed(title=prompt, description=prompt, color=0x00ff00)
        embedVar.set_image(url=ImageUrl)
        await message.channel.send(embed=embedVar)
    elif message.content.startswith("!insert "):
        query = message.content[8:]
        song_number = query.split(" ")[0]
        position = query.split(" ")[1]
        if not song_number.isdigit() or not position.isdigit():
            await message.channel.send("Invalid song number or position type !queue to see the queue")
            return
        else:
            song_number = int(song_number)
            position = int(position)
            if song_number >= len(song_queue) or position >= len(song_queue):
                await message.channel.send("Invalid song number or position type !queue to see the queue")
                return
            elif song_number == 0 or position == 0:
                await message.channel.send("Can't insert at position 0 or can't move the song currently playing")
                return
            song = song_queue[song_number]
            song_queue.pop(song_number)
            song_queue.insert(position, song)
            RewriteQueueFile(song_queue)
            await message.channel.send("Song inserted at position "+str(position)+" : "+song)
    elif message.content==("!quit"):
        exit()
    elif message.content=="!oldqueue":
        
        if ReadQueueFile():
            RewriteQueueFile([])
            await message.channel.send("Queue loaded")
        else:
            await message.channel.send("Old queue is empty")
            
def StartPlaylist(playlist_name):
    plsong_queue = []
    global song_queue
    # Open file like playlist_name_playlist.txt if not exist create it
    file = open(playlist_name+"_playlist.txt", "r")
    for line in file:
        print(line)
        song_name = line.strip()  # remove \n
        song_name, url = search_and_download_music(song_name)
        song_queue.append(song_name)
        global mapsongurl
        mapsongurl[song_name]=song_name
        plsong_queue.append(song_name)
    file.close()
    return plsong_queue
def ReadQueueFile():
    global song_queue
    #
    # Read the queue from the file
    file = open("queue.txt", "r")
    lines = file.readlines()
    file.close()
    if len(lines) == 0:
        return False
    for line in lines:
        song_queue.append(line.strip())
        global mapsongurl
        mapsongurl[line.strip()] = line.strip()
    return True
async def PlayUniqueSong(vc, song_name):
    vc.play(discord.FFmpegPCMAudio(song_name))
    vc.source = discord.PCMVolumeTransformer(vc.source)
    vc.source.volume = 0.1
    while vc.is_playing() or vc.is_paused():
        await asyncio.sleep(1)
    vc.stop()


async def GetVocalClient(client, channel, message):
    if not client.voice_clients:
        vc = await channel.connect()
    else:
        for x in client.voice_clients:
            if (x.guild == message.guild):
                vc = x
                break
    return vc

async def PlaySong(song_name, channel, message):
    if not client.voice_clients:
        vc = await channel.connect()
    else:
        for x in client.voice_clients:
            if (x.guild == message.guild):
                vc = x
                break
    vc.play(discord.FFmpegPCMAudio(song_name))
    vc.source = discord.PCMVolumeTransformer(vc.source)
    vc.source.volume = 0.1
    while vc.is_playing():
        await asyncio.sleep(1)
    # song finished
    vc.stop()
    await vc.disconnect()



def StartBot(TOKEN):
    client.run(TOKEN)


class Jokes:
    def __init__(self, title, url, body, baseurl):
        self.title = title
        self.url = url
        self.body = body
        self.baseurl = baseurl


async def JokefromReddit():
    # connect to reddit
    reddit = praw.Reddit(client_id='paXC2ZsdM_2-uGDNyoerNw',
                         client_secret='uC79rgQmD-xrF0lpGT-Cd5opFVEvcQ',
                         user_agent='user_agent')
    # fetch the subreddit
    jokes = reddit.subreddit('ProgrammerHumor')
    joke = jokes.hot(limit=30)
    jokes = []
    for element in joke:
        joke = Jokes(element.title, element.url,
                     element.selftext, element.link_flair_text)
        jokes.append(joke)
    # Random choose a jokes in a list
    num = random.randint(0, len(jokes)-1)
    for i in range(num):
        joke = jokes[i]
    toPrintJokes = joke
    # So joke must be 1 len long

    # return the first post
    return toPrintJokes



StartBot(TOKEN)
