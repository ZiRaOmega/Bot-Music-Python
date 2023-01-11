
import asyncio
import os
import random
import discord
import youtube_dl
import pyjokes
# use env variables for token
TOKEN = os.environ.get('DISCORD_TOKEN')
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
song_queue = []


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    await HandleMessageEvent(message)
    

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
        return file_name,url
    elif len(info) > 0:
        # Download the video as file_name
        ytdl.download([url])
    else:
        return None
    print(file_name)
    return file_name,url


async def play_song(vc, message, url):
    while len(song_queue) > 0:
        print(song_queue)
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
            return file_name,url 
        else:
            # Download the video as file_name
            ydl.download(["ytsearch:" + song_name])
            print(file_name)
            return file_name,url

def fileNameFormatted(fileName):
    fileName = fileName.replace("_"," " )
    fileName = fileName.replace(".mp3","" )
    fileName = fileName.replace(".webm","" )
    fileName = fileName.replace(".m4a","" )
    fileName = fileName.replace(".mp4","" )
    fileName = fileName.replace(".wav","" )
    fileName = fileName.replace(".ogg","" )
    fileName = fileName.replace(".flac","" )
    fileName = fileName.replace(".aac","" )
    fileName = fileName.replace(".opus","" )
    fileName = fileName.replace(".wma","" )
    fileName = fileName.replace(".3gp","" )
    fileName = fileName.replace(".mkv","" )
    fileName = fileName.replace(".avi","" )
    fileName = fileName.replace(".mov","" )
    fileName = fileName.replace(".wmv","" )
    fileName = fileName.replace(".flv","" )
    return fileName
async def HandleMessageEvent(message):
    if message.author == client.user:
        return

    channel = message.author.voice.channel
    if message.content.startswith('!play'):
        if channel:
            print(song_queue)
            print(message.content[6:])
            url = message.content[6:]
            # check if url is url or search term
            if not url.startswith('http') or not url.startswith('https'):
                await message.channel.send('Searching for ' + url)
                file_name,url = search_and_download_music(url)
                await message.channel.send('Found ' + url)
            else:
                file_name,url = await DownloadVideo(url)
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
                    await play_song(vc, message,url)
                else:
                    if not client.voice_clients:
                        vc = await channel.connect()
                    else:
                        vc = client.voice_clients[0]
                    await message.channel.send('Playing ' + url)

                    vc.play(discord.FFmpegPCMAudio(file_name))
                    while vc.is_playing():
                        await asyncio.sleep(1)
                    vc.stop()
                    # remove song from folder
                    os.remove(file_name)
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
        file_name,url = await DownloadVideo(url)
        if file_name is None:
            await message.channel.send('Could not find ' + url)
            return
        await message.channel.send("Downloaded " + url + "You can Now play it with !play " + url)
    elif message.content.startswith('!queue'):
        song_queueFormatted = ""
        for x in song_queue:
            song_queueFormatted += x + "\n"
        await message.channel.send(song_queueFormatted)
    elif message.content.startswith('!skip'):
        for x in client.voice_clients:
            if (x.guild == message.guild):
                x.stop()
                """ song_queue.pop(0) """
                break
    elif message.content.startswith('!pause'):
        for x in client.voice_clients:
            if (x.guild == message.guild):
                x.pause()
                break
    elif message.content.startswith('!resume'):
        for x in client.voice_clients:
            if (x.guild == message.guild):
                x.resume()
                break
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
        #remove duplicate songs from queue
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
        #read all files in folder
        for file in os.listdir():
            #if file is webm
            if file.endswith(".webm"):
                #remove .webm
                file = file.replace(".webm","" )
                #add to result
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
        #count time it takes to send message
        start = time.time()
        await message.channel.send('Pong!')
        end = time.time()
        await message.channel.send('Time: ' + str(end - start))
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
        await message.channel.send(pyjokes.get_joke())
    elif message.content.startswith('!random'):
        songs = []
        for file in os.listdir():
            if file.endswith(".webm"):
                songs.append(file)
        random_song = random.choice(songs)
        await message.channel.send("Playing " + random_song)
        #play song
        await PlaySong(random_song,channel,message)
            

async def PlaySong(song_name,channel,message):
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
    #song finished
    vc.stop()
    await vc.disconnect()
        

def StartBot(TOKEN):
    client.run(TOKEN)


StartBot(TOKEN)
