
import asyncio
import os
import discord
import youtube_dl
#use env variables for token
TOKEN = os.environ.get('DISCORD_TOKEN')

client = discord.Client(intents=discord.Intents.all())

ytdl_opts = {
    'format': 'worstaudio/worst',
    'outtmpl': '%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': False,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ytdl = youtube_dl.YoutubeDL(ytdl_opts)
song_queue = []


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!play'):
        channel = message.author.voice.channel
        if channel:
            print(message.content[6:])
            url = message.content[6:]
            file_name = await DownloadVideo(url)
            song_queue.append(file_name)
            if os.path.exists(file_name):
                if len(song_queue) > 0:
                    #NEED RECURSION HERE
                    #if bot not connected to voice channel
                    if not client.voice_clients:
                        vc = await channel.connect()
                    else :
                        return
                    
                    while len(song_queue) > 0:
                        print(song_queue)
                        x = song_queue[0]
                        await message.channel.send('Playing ' + x)
                        vc.play(discord.FFmpegPCMAudio(x))
                        while vc.is_playing():
                            await asyncio.sleep(1)
                        vc.stop()
                        song_queue.pop(0)
                        
                    await vc.disconnect()
                else:
                    if not client.voice_clients:
                        vc = await channel.connect()
                    else :
                        vc = client.voice_clients[0]
                    while vc.is_playing():
                            await asyncio.sleep(1)
                    await message.channel.send('Playing ' + url)
                    
                    vc.play(discord.FFmpegPCMAudio(file_name))
                    while vc.is_playing():
                        await asyncio.sleep(1)
                    vc.stop()
                    await vc.disconnect()
                vc.stop()
                await vc.disconnect()
        else:
            await message.channel.send('You are not connected to a voice channel')
    elif message.content.startswith('!stop'):
        song_queue.clear()
        for x in client.voice_clients:
            if (x.guild == message.guild):
                await x.disconnect()
                break
    elif message.content.startswith('!download'):
        url = message.content[10:]
        file_name = await DownloadVideo(url)
        await message.channel.send("Downloaded " + url + "You can Now play it with !play " + url)


async def DownloadVideo(url):
    info = ytdl.extract_info(url, download=False)
    file_name = ytdl.prepare_filename(info)
    if os.path.exists(file_name):
        return file_name
    else:
        # Download the video as file_name
        ytdl.download([url])
    print(file_name)
    return file_name

client.run(TOKEN)
