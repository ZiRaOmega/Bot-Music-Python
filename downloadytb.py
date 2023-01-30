import os
import sys
import yt_dlp as youtube_dl
#use : python3 downloadytb.py "video name"
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

def GetArgs():
    #get the arguments from the command line
    args=sys.argv
    if len(args) == 1:
        print("No arguments")
        return
    video_url=args[1]
    return video_url

def DownloadVideo(song_name):
    #download the video
    with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
        info = ydl.extract_info("ytsearch:" + song_name,
                                download=False)['entries'][0]
        file_name = ydl.prepare_filename(info)
        url = info['webpage_url']
        if os.path.exists(file_name):
            return
        else:
            # Download the video as file_name
            try:
                ydl.download(["ytsearch:" + song_name])
            except:
                ydl.download(["ytsearch:" + song_name])
            print(file_name)

video_name=GetArgs()
DownloadVideo(video_name)
