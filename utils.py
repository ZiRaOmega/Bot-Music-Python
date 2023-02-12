import os
import sys
import urllib.parse
import requests
import re
import time
import datetime

#Queue functions
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
############################################################################################################


#Playlist functions
def CreatePlaylistFile(playlist_name):
    # Create a file called playlist_name_playlist.txt if not exist
    if not os.path.exists(playlist_name+"_playlist.txt"):
        file = open(playlist_name+"_playlist.txt", "w")
        file.close()
def WritePlaylistFile(playlist_name, song_name):
    # Open file like playlist_name_playlist.txt if not exist create it
    file = open(playlist_name+"_playlist.txt", "a")
    file.write(song_name+"\n")
    file.close()

def ListPlaylist():
    # List all playlist
    toSend = ""
    i=0
    for file in os.listdir():
        if file.endswith("_playlist.txt"):
            toSend += str(i)+": "+file[:-12]+"\n" #
            i+=1
    return toSend
    
def ReadPlaylistFile(playlist_name):
    if not os.path.exists(playlist_name+"_playlist.txt"):
        return "Playlist not found"
    # Open file like playlist_name_playlist.txt if not exist create it
    file = open(playlist_name+"_playlist.txt", "r")
    toSend = playlist_name+":\n"
    i = 0
    for line in file:
        if line != "":
            toSend += str(i)+": "+line+"\n"
            i += 1
    file.close()
    return toSend
def RemovePlaylistFile(playlist_name):
    # Remove file like playlist_name_playlist.txt
    os.remove(playlist_name+"_playlist.txt")
############################################################################################################

#History functions
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


async def ReadHistoryFile(message,opts):
    # Read the history.txt file from the end and get the username and userinput each line like(username userinput)
    i = 0
    result = ""
    for line in reversed(list(open("history.txt"))):
        if i == int(opts):
            break
        i += 1
        result+=str(i) + ": " + line+"\n"
    await message.channel.send(result)
############################################################################################################

#Useful functions
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
