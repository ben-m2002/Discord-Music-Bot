import os
import pickle
import urllib
import discord
import pafy
import youtube_dl
import yt_dlp
from discord.ext import commands
from youtube_dl import YoutubeDL
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from googleapiclient.discovery import build

#help(yt_dlp)

# norm functions

def read_token():
    with open('token', "r") as f:  # using with means you dont have to close the file, f is the variable
        lines = f.readlines()  # makes a string table of all the lines in the file
        return lines[0].strip()  # removes all leading and trailing whitespace if no arg is provided



token = read_token()

# discord stuff
youtube = build('youtube', 'v3', developerKey='AIzaSyAGx3B5fTzh0K_URSjpd3Z-fnj9Jw1D12w')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", case_insensitive=True,intents=intents)  # intents is like the amount of access your bot can have
music_Q = []
MusicFile = None

async def playMusic(ctx,voiceChannel,firstItem): #the item from the query
    vc = None
    voice_clients = bot.voice_clients
    in_vc = False  # check to see if in the correct vc

    print("Number of voice client is: " + str(len(voice_clients)))

    if len(voice_clients) > 0:
        for client in voice_clients:
            if client.channel == ctx.author.voice.channel:
                vc = client
                in_vc = True
        if not in_vc:
            vc = await voiceChannel.connect()
            in_vc = True
    else:
        vc = await voiceChannel.connect()
        in_vc = True

    # check if bot is currently playing music

    if vc.is_playing():
        vc.stop()

    file = downloadYoutubeUrl(firstItem['id']['videoId'])
    vc.play(discord.FFmpegPCMAudio(file), after=lambda e: queue(ctx,vc))



def queue (ctx,vc):

    # make sure there is stuff in queue
    if len(music_Q) == 0:
        return

    #get that first item

    file = music_Q.pop(0)

    # add some sort of vc check in the future

    for channel in bot.get_all_channels():
        if channel == vc.channel:
            print("Bot is in the right vcwww")

    vc.play(discord.FFmpegPCMAudio(file), after=lambda e: queue(ctx,vc))


def youtubeSearch (str): # returns the first search tab from the google search
    query = str
    req = youtube.search().list(q=query, part='snippet', type='video', maxResults=3)
    res = req.execute()
    firstItem = res['items'][0]
    title = firstItem['snippet']['title']
    id = firstItem['id']['videoId']
    print(title)
    return firstItem

def downloadYoutubeUrl (id):

    #create directory if one isnt there


    direc = "Music"

    path = os.path.join("./", direc )

    try:
        os.mkdir(path)
    except:
        print("Already exists")

    MusicFile = "./Music"

    absPath = os.path.abspath(path)

    ytdl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }
        ],
        'outtmpl' : absPath + '/%(title)s.%(ext)s'
    }

    url = "https://www.youtube.com/watch?v=" + str(id)
    print(url)

    meta_data = None
    videoName = ""
    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        meta_data = ydl.extract_info(url, download=True)
        videoName = meta_data.get('title',None)
        print("THIS IS FILE NAME: " + videoName)

    # change the song to a name we can use easily

    for file in os.listdir("./Music"):
        if file.startswith(videoName):
            if file.endswith('.mp3'):
                return "./Music/" + videoName + ".mp3"



@bot.event
async def on_ready():
    channel = bot.get_channel(802660327661502496)
    await channel.send("Ready for action!")


@bot.command(name="hey", description="Greet the user!")
async def hello(ctx):
    await ctx.send("Hey " + ctx.author.name + "!")

@bot.command(name = "play", description = "play music")
async def play(ctx):

    #check if user is in a vc

    if ctx.author.voice == None:
        await ctx.send("To use this command make sure you're in a voice channel")
        print("Must be in channel")
        return

    # get the search data and send it to youtube

    firstItem = youtubeSearch(ctx.message.content[5:])

    # send stuff to the discord

    #embedded image

    image = firstItem['snippet']['thumbnails']['high']['url']
    embed = discord.Embed()
    embed.url = "https://www.youtube.com/watch?v=" + str(firstItem['id']['videoId'])
    embed.set_image(url = image)
    embed.description = firstItem['snippet']['title']
    embed.set_footer(text = firstItem['snippet']['description'])


    # check for channel

    channel = ctx.channel
    voiceChannel = ctx.author.voice.channel
    await channel.send("Playing : " + firstItem['snippet']['title'])
    await ctx.send(embed = embed)

    #play

    await playMusic(ctx,voiceChannel,firstItem)



@bot.command(name = "stop", description = "stop playing music")
async def stopMusic(ctx):
    voice_clients = bot.voice_clients
    vc = None

    # make sure the user is in a client

    if ctx.author.voice == None:
        await ctx.send("To use this command make sure you're in a voice channel")
        print("Must be in channel")
        return

    for client in voice_clients:
        if client.channel == ctx.author.voice.channel:
            vc = client

    # stops the song from playing if it is in a voice channel

    try:
        vc.stop()
        await vc.disconnect()
    except:
        await ctx.send("What do you want me to stop doing?")

    # delete music files

    if MusicFile != None:
        for file in os.listdir(MusicFile):
            os.remove(os.path.join(MusicFile, file))



@bot.command(name = "q", description = "enqueue a song")
async def qMusic(ctx):

    # make sure you're in vc

    if ctx.author.voice == None:
        await ctx.send("To use this command make sure you're in a voice channel")
        print("Must be in channel")
        return

    nextSong = ctx.message.content[1:]

    item = youtubeSearch(nextSong)

    file = downloadYoutubeUrl(item['id']['videoId'])

    music_Q.append(file)










# entering and leaving

@bot.event
async def on_member_join(member):
    print("joined")
    guild = member.guild
    channel = bot.get_channel(936426320617943110)
    await channel.send("Oh My Gosh, guess who just showed up IT'S " + str(member.name) + "!!!")


bot.run(token)  # connects token to bot
