
import asyncio
import datetime
import os
import random
import subprocess
import discord
import yt_dlp as youtube_dl
import praw
import time
import requests
import urllib.parse
import sys
import openai

# Set up the model and prompt
model_engine = "text-davinci-003"
""" import lyrics_fetcher """
ADMIN_MODE = True
# use env variables for token
TOKEN = os.environ.get('DISCORD_TOKEN')
openai.api_key = os.environ.get('OPENAI_TOKEN')
song_queue = []
REPEAT = False
if TOKEN is None:
    print("No token found use export DISCORD_TOKEN='your_token'")
    exit()
if openai.api_key is None:
    print("No OPENAI token found use export OPENAI_TOKEN='your_token'")
    exit()

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

""" async def GetLyrics(song_name):
    # Get the lyrics of the song using the genius api
    lyrics_fetcher.set_access_token(os.environ.get('GENIUS_TOKEN'))
    lyrics = lyrics_fetcher.get_lyrics(song_name)
    return lyrics """
# print(GetLyrics("The Weeknd - Blinding Lights"))
def CreateQueueFile():
    if not os.path.exists("queue.txt"):
        # Create a file to store the queue
        file = open("queue.txt", "w")
        file.close()
def WriteSongToQueueFile(SongName):
    # Write the queue to the file
    file = open("queue.txt", "a")
    file.write(SongName+"\n")
    file.close()
def ReadQueueFile():
    # Read the queue from the file
    file = open("queue.txt", "r")
    lines = file.readlines()
    file.close()
    for line in lines:
        song_queue.append(line.strip())
def PopSongFromQueueFile():
    # Remove the first song from the queue
    file = open("queue.txt", "r")
    lines = file.readlines()
    file.close()
    file = open("queue.txt", "w")
    for line in lines[1:]:
        file.write(line)
    file.close()
def RewriteQueueFile(song_queue):
    #Remove all songs from the queuefile
    file = open("queue.txt", "w")
    file.truncate(0) #remove all content
    for song in song_queue:
        file.write(song+"\n")
    file.close()
    
    


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    CreateQueueFile()
    ReadQueueFile()


@client.event
async def on_message(message):
    await HandleMessageEvent(message, song_queue)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await DefaultStatus()


async def DefaultStatus():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help"))


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


async def play_song(vc, message, url, channel):
    global REPEAT
    while len(song_queue) > 0:

        print(song_queue)
        if not client.voice_clients:
            vc = await channel.connect()
        x = song_queue[0]
        await message.channel.send(':play_pause: Playing ' + x[:(len(x) - 5)])
        await ChangeStatus(x)
        vc.play(discord.FFmpegPCMAudio(x))
        while vc.is_playing() or vc.is_paused():
            await asyncio.sleep(1)
        vc.stop()
        if not REPEAT:
            song_queue.pop(0)
            PopSongFromQueueFile()
    await vc.disconnect()
    await DefaultStatus()


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


def fileNameFormatted(fileName):
    fileName = fileName.replace("_", " ")
    fileName = fileName.replace(".mp3", "")
    fileName = fileName.replace(".webm", "")
    fileName = fileName.replace(".m4a", "")
    fileName = fileName.replace(".mp4", "")
    fileName = fileName.replace(".wav", "")
    fileName = fileName.replace(".ogg", "")
    fileName = fileName.replace(".flac", "")
    fileName = fileName.replace(".aac", "")
    fileName = fileName.replace(".opus", "")
    fileName = fileName.replace(".wma", "")
    fileName = fileName.replace(".3gp", "")
    fileName = fileName.replace(".mkv", "")
    fileName = fileName.replace(".avi", "")
    fileName = fileName.replace(".mov", "")
    fileName = fileName.replace(".wmv", "")
    fileName = fileName.replace(".flv", "")
    return fileName


CurrentSong = None


async def HandleMessageEvent(message, song_queue):
    global CurrentSong
    channel = None
    if message.author == client.user:
        return
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
                await message.channel.send('Downloading ' + url)
                file_name, url = search_and_download_music(url)
                await message.channel.send('Found ' + url)
            else:
                file_name, url = await DownloadVideo(url)
                if file_name is None:
                    await message.channel.send('Could not find ' + url)
                    return
                await message.channel.send(':magnet: Downloaded ' + url)
            song_queue.append(file_name)
            WriteSongToQueueFile(file_name)
            CurrentSong = file_name
            if os.path.exists(file_name):
                if len(song_queue) > 0:
                    # if bot not connected to voice channel
                    if not client.voice_clients:
                        vc = await channel.connect()
                    else:
                        await message.channel.send(url+' Added to queue')
                        return
                    await play_song(vc, message, url, channel)
                else:
                    vc = await GetVocalClient(client, channel, message)
                    await message.channel.send(':arrow_forward: Playing ' + file_name)

                    vc.play(discord.FFmpegPCMAudio(file_name))
                    while vc.is_playing():
                        await asyncio.sleep(1)
                    vc.stop()
                    # remove song from folder
                    # os.remove(file_name)
                    await vc.disconnect()
                    await DefaultStatus()
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
            await message.channel.send('Could not find ' + url)
            return
        await message.channel.send(":magnet: Downloaded " + url + "You can Now play it with !play " + url)
    elif message.content.startswith('!queue') or message.content.startswith('!q '):
        # remove the sended message from the channel
        song_queueFormatted = ""
        i = 0
        for x in song_queue:
            if i == 0:
                song_queueFormatted += "Now Playing: "+x+"\n"
                i += 1
                continue
            song_queueFormatted += str(i)+": " + x + "\n"
            i += 1
        if song_queueFormatted == "":
            song_queueFormatted = "Queue is empty"
        await message.channel.send(song_queueFormatted)
    elif message.content.startswith('!skip'):
        await message.delete()
        for x in client.voice_clients:
            if (x.guild == message.guild):
                if x.is_playing():
                    x.stop()
                    await message.channel.send(':fast_forward: Skipped')
                    if len(song_queue) == 0:
                        await x.disconnect()
                    await DefaultStatus()
                """ song_queue.pop(0) """
                break
    elif message.content.startswith('!pause'):
        await message.delete()
        for x in client.voice_clients:
            if (x.guild == message.guild):
                x.pause()
                break
        await message.channel.send(':pause_button: Paused')
    elif message.content.startswith('!resume'):
        await message.delete()
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
            await message.channel.send('Queue is empty')
    elif message.content.startswith('!reset'):
        await message.delete()
        for x in client.voice_clients:
            await x.disconnect()
        song_queue.clear()
    elif message.content.startswith('!help'):
        await message.channel.send('!play or !p [url] - Plays the song from the url\n!stop - Stops the bot and clears the queue\n!download [url] - Downloads the song from the url\n!queue - Shows the queue\n!skip - Skips the current song\n!pause - Pauses the current song\n!resume - Resumes the current song\n!help - Shows this message\n!alredydl - Print all files already downloaded\n!remove [url] - Removes the song from the queue\n!dplremove - Removes duplicate songs from the queue\n!clear - Clears the queue\n!shuffle - Shuffles the queue\n!reset - Resets the bot')
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
            os.remove(file_name)
        song_queue.clear()
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
        for file in os.listdir():
            # if file is webm
            if file.endswith(".webm"):
                # remove .webm
                file = file.replace(".webm", "")
                # add to result
                result += file + "\n"
        await message.channel.send(result)
    elif message.content.startswith('!status'):
        await message.channel.send("Playing " + song_queue[0])
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
    elif message.content.startswith('!volume'):
        volume = message.content[8:]
        for x in client.voice_clients:
            if (x.guild == message.guild):
                x.source = discord.PCMVolumeTransformer(x.source)
                x.source.volume = float(volume)
                break
    elif message.content.startswith('!creator'):
        await message.channel.send("Created by: ZiRa_Omega")
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
        await message.channel.send("Playing " + random_song)
        if len(song_queue) == 0:
            song_queue.append(random_song)
            WriteSongToQueueFile(random_song)
            await PlaySong(random_song, channel, message)
        else:
            song_queue.append(random_song)
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
        await message.channel.send("Restarting...")
        # os.system("bash restart.sh") using subprocess
        subprocess.Popen(["bash", "restart.sh"])
        exit()
    elif message.content.startswith('!createpl'):
        playlist_name = message.content[10:]
        # Create file like playlist_name_playlist.txt
        file = open(playlist_name+"_playlist.txt", "w")
        file.close()
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
        # Open file like playlist_name_playlist.txt if not exist create it
        file = open(playlist_name+"_playlist.txt", "a")
        file.write(song_name+"\n")
        file.close()
        await message.channel.send("Added "+song_name+" to "+playlist_name)
    elif message.content.startswith('!pl '):
        plsong_queue = []
        playlist_name = message.content[4:]
        # Open file like playlist_name_playlist.txt if not exist create it
        file = open(playlist_name+"_playlist.txt", "r")
        for line in file:
            print(line)
            song_name = line.strip()  # remove \n
            song_name, url = search_and_download_music(song_name)
            song_queue.append(song_name)
            plsong_queue.append(song_name)
        file.close()
        if len(plsong_queue) == 0:
            await message.channel.send("Playlist is empty")
            return
        else:
            vc = await GetVocalClient(client, channel, message)
            await message.channel.send("Playing playlist "+playlist_name)
            while len(plsong_queue) > 0:
                await message.channel.send("Playing "+plsong_queue[0])
                await PlayUniqueSong(vc, plsong_queue[0])
                plsong_queue.pop(0)
                song_queue.pop(0)
                PopSongFromQueueFile()
            await play_song(vc, message, song_queue[0], channel)
            await message.channel.send("Playlist Ended")
    elif message.content.startswith('!rmpl'):
        playlist_name = message.content[6:]
        # Remove file like playlist_name_playlist.txt
        os.remove(playlist_name+"_playlist.txt")
        await message.channel.send("Playlist removed")
    elif message.content == ('!pllist'):
        # List all playlist
        playlists = []
        for file in os.listdir("."):
            if file.endswith("_playlist.txt"):
                playlists.append(file[:-13])
        await message.channel.send("Playlists: "+", ".join(playlists))
    elif message.content.startswith('!readpl '):
        playlist_name = message.content[8:]
        # Open file like playlist_name_playlist.txt if not exist send message to channel
        if not os.path.exists(playlist_name+"_playlist.txt"):
            await message.channel.send("Playlist not found")
            return
        file = open(playlist_name+"_playlist.txt", "r")
        toSend = playlist_name+":\n"
        i = 0
        for line in file:
            if line != "":
                toSend += str(i)+": "+line+"\n"
                i += 1
        file.close()
        await message.channel.send(toSend)
    elif message.content.startswith('!playforce'):
        if len(song_queue) == 0:
            await message.channel.send("Queue is empty")
            return
        else:
            await message.channel.send("Playing "+song_queue[0])
            vc = await GetVocalClient(client, channel, message)
            await play_song(vc, message, song_queue[0], channel)
    elif message.content == ('!history'):
        await ReadHistoryFile(message)
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
        print(str(REPEAT))
        await message.channel.send("Repeat is now "+str(REPEAT))
    elif message.content.startswith('!deletesong '):
        songtodelete = message.content[12:]
        if songtodelete.isdigit():
            songtodelete = int(songtodelete)
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
            
        
        


async def PlayUniqueSong(vc, song_name):
    vc.play(discord.FFmpegPCMAudio(song_name))
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


def CreateHistoryFile():
    # Create a file called history.txt if not exist
    if not os.path.exists("history.txt"):
        file = open("history.txt", "w")
        file.close()


def WriteHistoryFile(userinput, username):
    timeNow = datetime.datetime.now()
    timeNowFormatted = timeNow.strftime("%d/%m/%Y %H:%M:%S")
    # Write the userinput and username to history.txt
    file = open("history.txt", "a")
    file.write(username+" "+userinput+" "+timeNowFormatted+"\n")
    file.close()


async def ReadHistoryFile(message):
    # Read the history.txt file and get the username and userinput each line like(username userinput)
    i = 0
    result = ""
    for line in open("history.txt"):
        Credentials = line.split(" ")
        Username = Credentials[0]
        Userinput = " ".join(Credentials[1:])
        result = str(i)+": |" + Username+"| "+Userinput+"\n"
        await message.channel.send(result)
        i += 1


async def PlaySong(song_name, channel, message):
    if not client.voice_clients:
        vc = await channel.connect()
    else:
        for x in client.voice_clients:
            if (x.guild == message.guild):
                vc = x
                break
    vc.play(discord.FFmpegPCMAudio(song_name))
    while vc.is_playing():
        await asyncio.sleep(1)
    # song finished
    vc.stop()
    await vc.disconnect()


def GetPassword(username):
    # Read the ZONE01.txt file and get the username and password each line like(username password)
    for line in open("ZONE01.txt"):
        Credentials = line.split(" ")
        Username = Credentials[0]
        Password = Credentials[1]
        if Username == username:
            # if username is found return the password
            return Password


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

session = requests.Session()
Pseudo01 = None
Password01 = None
ADMIN = None
URL = "http://10.10.0.30/"
URL = "http://localhost:3000/"


def login(username=None):
    password = GetPassword(username)
    global Pseudo01  # global variable to be used in the function and outside the function
    global Password01
    global ADMIN
    if Pseudo01 != None and Password01 != None and ADMIN == None:
        ADMIN = "Connected"
        Pseudo01 = None
        Password01 = None
        return session.get(URL+"sign_z01/PHP/sign.php?" + urllib.parse.urlencode({  # login to the website with the credentials in the ZONE01.txt file return is used to check if the login is successful and end the function
            "pseudo": Pseudo01,
            "password": Password01,
            "submit": "Connexion",
        })).status_code == 200, "You are now connected"
    elif username != None and password != None:
        pseudo01 = username
        password01 = password
        ADMIN = None
        return session.get(URL+"sign_z01/PHP/sign.php?" + urllib.parse.urlencode({
            "pseudo": pseudo01,
            "password": password01,
            "submit": "Connexion",
        })).status_code == 200, "You are now connected"
    elif username == None or password == None:
        return "Error", "Please ask an admin to add your credentials in the ZONE01.txt file"


def SwitchDoor(PushTRUEorPullFALSE):  # Enter (alias Push) or Exit (alias Pull)
    # switch PushTRUEorPullFALSE to 1 or 0
    # ping 10.10.0.30 if down return
    ping = os.system("ping -c 1 10.10.0.30")
    if PushTRUEorPullFALSE == "ENTER":
        if ping != 0:
            return "Door is locked"
        else:
            EnterFuck01()
    elif PushTRUEorPullFALSE == "EXIT":
        if ping != 0:
            print()
        else:
            ExitLove01()


def logout():
    session.get(URL+"sign_z01/PHP/deco.php")


def EnterFuck01():
    if not login():
        sys.exit(1)
    print("Enter...")
    session.get(URL+"sign_z01/PHP/enter.php")
    logout()


def ExitLove01():
    if not login():
        return "Error", "Please ask an admin to add your credentials in the ZONE01.txt file"
    print("Exit...")
    session.get(URL+"sign_z01/PHP/exit.php")
    logout()
    return "Success", "You have left the zone"


def ExportedCredentials___():
    if Pseudo01 == None or Password01 == None:
        return False
    else:
        return True


StartBot(TOKEN)
