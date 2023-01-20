
import asyncio
import os
import random
import discord
import youtube_dl
import praw
import time
import requests
import urllib.parse
import sys
ADMIN_MODE = True
# use env variables for token
TOKEN = os.environ.get('DISCORD_TOKEN')
song_queue = []
if TOKEN is None:
    print("No token found use export DISCORD_TOKEN='your_token'")
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


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


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


async def DownloadVideo(url):
    info = ytdl.extract_info(url, download=False)
    file_name = ytdl.prepare_filename(info)
    url = info['webpage_url']
    if os.path.exists(file_name):
        return file_name, url
    elif len(info) > 0:
        # Download the video as file_name
        ytdl.download([url])
    else:
        return None, None
    print(file_name)
    return file_name, url


async def play_song(vc, message, url, channel):
    while len(song_queue) > 0:
        print(song_queue)
        if not client.voice_clients:
            vc = await channel.connect()
        x = song_queue[0]
        await message.channel.send('Playing ' + url)
        await ChangeStatus(x)
        vc.play(discord.FFmpegPCMAudio(x))
        while vc.is_playing():
            await asyncio.sleep(1)
        vc.stop()
        song_queue.pop(0)
    await vc.disconnect()


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
            ydl.download(["ytsearch:" + song_name])
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


async def HandleMessageEvent(message, song_queue):
    if message.author == client.user:
        return
    if message.author.voice is not None:
        # await message.channel.send('You are not in a voice channel')
        channel = message.author.voice.channel

    if message.content.startswith('!play'):
        if channel:
            print(song_queue)
            print(message.content[6:])
            url = message.content[6:]
            # check if url is url or search term
            if not url.startswith('http') or not url.startswith('https'):
                await message.channel.send('Searching for ' + url)
                file_name, url = search_and_download_music(url)
                await message.channel.send('Found ' + url)
            else:
                file_name, url = await DownloadVideo(url)
                if file_name is None:
                    await message.channel.send('Could not find ' + url)
                    return
                await message.channel.send('Downloaded ' + url)
            song_queue.append(file_name)
            if os.path.exists(file_name):
                if len(song_queue) > 0:
                    # NEED RECURSION HERE
                    # if bot not connected to voice channel
                    if not client.voice_clients:
                        vc = await channel.connect()
                    else:
                        await message.channel.send(url+' Added to queue')
                        return
                    await play_song(vc, message, url, channel)
                else:
                    if not client.voice_clients:
                        vc = await channel.connect()
                    else:
                        vc = client.voice_clients[0]
                    await message.channel.send('Playing ' + file_name)

                    vc.play(discord.FFmpegPCMAudio(file_name))
                    while vc.is_playing():
                        await asyncio.sleep(1)
                    vc.stop()
                    # remove song from folder
                    # os.remove(file_name)
                    await vc.disconnect()
                    await DefaultStatus()
        else:
            await message.channel.send('You are not connected to a voice channel')
    elif message.content.startswith('!stop'):
        for x in client.voice_clients:
            if (x.guild == message.guild):
                await x.disconnect()
                break
        for file_name in song_queue:
            os.remove(file_name)
        song_queue.clear()
        await DefaultStatus()
    elif message.content.startswith('!download'):
        url = message.content[10:]
        file_name, url = await DownloadVideo(url)
        if file_name is None:
            await message.channel.send('Could not find ' + url)
            return
        await message.channel.send("Downloaded " + url + "You can Now play it with !play " + url)
    elif message.content.startswith('!queue'):
        song_queueFormatted = ""
        i = 0
        for x in song_queue:
            if i == 0:
                song_queueFormatted += "Now Playing: "
            song_queueFormatted += str(i)+": " + x + "\n"
            i += 1
        await message.channel.send(song_queueFormatted)
    elif message.content.startswith('!skip'):
        for x in client.voice_clients:
            if (x.guild == message.guild):
                if x.is_playing():
                    x.stop()
                    song_queue.pop(0)
                    if len(song_queue) > 0:
                        await play_song(x, message, song_queue[0], channel)
                    else:
                        await x.disconnect()
                    await DefaultStatus()
                """ song_queue.pop(0) """
                break
    elif message.content.startswith('!pause'):
        for x in client.voice_clients:
            if (x.guild == message.guild):
                x.pause()
                break
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
    elif message.content.startswith('!reset'):
        for x in client.voice_clients:
            await x.disconnect()
        song_queue.clear()
    elif message.content.startswith('!help'):
        await message.channel.send('!play [url] - Plays the song from the url\n!stop - Stops the bot and clears the queue\n!download [url] - Downloads the song from the url\n!queue - Shows the queue\n!skip - Skips the current song\n!pause - Pauses the current song\n!resume - Resumes the current song\n!help - Shows this message')
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
        random.shuffle(song_queue)
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
    elif message.content.startswith('!join'):
        channel = message.content[6:]
        for x in client.voice_clients:
            if (x.guild == message.guild):
                await x.move_to(channel)
                break
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
        Joke = JokefromReddit()
        await message.channel.send(Joke)
    elif message.content.startswith('!random'):
        songs = []
        for file in os.listdir():
            if file.endswith(".webm"):
                songs.append(file)
        random_song = random.choice(songs)
        await message.channel.send("Playing " + random_song)
        if len(song_queue) == 0:
            song_queue.append(random_song)
            await PlaySong(random_song, channel, message)
        else:
            song_queue.append(random_song)
    elif message.content.startswith('!resetstatus'):
        await DefaultStatus()
    elif message.content.startswith('!rickroll'):
        await message.channel.send("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        # if sender is connected to voice channel
        if message.author.voice:
            if not client.voice_clients:
                vc = await channel.connect()
            file_name, url = await DownloadVideo("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
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
        Move=SwitchDoor(True)
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
        errORsession,messer=login(UserName)
        if err!="Error":
            err=None
        elif err=="Error":
            await message.channel.send(messer)
            return
        else:
            await message.channel.send(messer)
            EnterFuck01(UserName)


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
    vc.source.volume = 0.5
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


def JokefromReddit():
    # connect to reddit
    reddit = praw.Reddit(client_id='paXC2ZsdM_2-uGDNyoerNw',
                         client_secret='uC79rgQmD-xrF0lpGT-Cd5opFVEvcQ',
                         user_agent='user_agent')
    # fetch the subreddit
    jokes = reddit.subreddit('ProgrammerHumor')
    joke = jokes.hot(limit=30)
    jokes = []
    for element in joke:
        jokes.append(element.url)
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
    global Pseudo01 #global variable to be used in the function and outside the function
    global Password01
    global ADMIN
    if Pseudo01 != None and Password01 != None and ADMIN == None:
        ADMIN = "Connected"
        Pseudo01 = None
        Password01 = None 
        return session.get(URL+"sign_z01/PHP/sign.php?" + urllib.parse.urlencode({ #login to the website with the credentials in the ZONE01.txt file return is used to check if the login is successful and end the function
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

def SwitchDoor(PushTRUEorPullFALSE): #Enter (alias Push) or Exit (alias Pull)
    #switch PushTRUEorPullFALSE to 1 or 0
        #ping 10.10.0.30 if down return
    ping = os.system("ping -c 1 10.10.0.30")
    if PushTRUEorPullFALSE=="ENTER":
        if ping != 0:
            return "Door is locked"
        else:
            EnterFuck01()
    elif PushTRUEorPullFALSE=="EXIT":
        if ping!=0:
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
