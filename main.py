import discord
import logging # for debugging
import os # for environment variables
from replit import db # imports the db, which will store data like tasks and meetings
import asyncio # for async sleep
from datetime import datetime, timezone, timedelta
from discord.ext import tasks
import requests
import json
from keep_alive import keep_alive

# VARIABLES
# setting up stuff
logging.basicConfig(level=logging.INFO) # set up debugging
botToken = os.environ['botToken'] # takes environment variable
client = discord.Client()

# variables ??
continuePomodoro = False
DATETIMEFORMATINPUT = "%Y-%m-%d %I:%M %p"
userID = ""

# OUR BEAUTIFUL FUNCTIONS
# database 
def help():
  return 0
def displayDB():
  print("DISPLAYING DB:")
  for key in db.keys():
    print(key + " = " + str(db[key]))

def clearDB():
  for key in db.keys():
    del db[key]

def getServerInfo(serverID):  # retrieves server info entry in database, requires message.guild.id to be passed to it, returns an array with num of tasks followed by num of meetings
  serverID = str(serverID)
  try: #tries to get server info
    return list(map(int, db["serverInfo" + serverID].split(',')))
  except KeyError: # if not it tries to generate
    db["serverInfo" + serverID] = "0,0"
    return list(map(int, db["serverInfo" + serverID].split(',')))

# tasks and meetings
def newItemKey(message, item): # for tasks, item=0; for meetings, item=1
  serverID = message.guild.id
  serverInfo = getServerInfo(serverID)
  if item == 0:
    key = "task" + str(serverID) + str(serverInfo[item])
  elif item == 1:
    key = "meeting" + str(serverID) + str(serverInfo[item])
  serverInfo[item] += 1
  db["serverInfo" + str(serverID)] = ",".join(list(map(str, serverInfo))) #increments
  return key



# task
def addTask(message): #!addTask task name, task description, due date, @person#1234
  try:
    key = newItemKey(message, 0)
    messageData = message.content.split(', ')
    messageData[0] = messageData[0][9:]
    messageData[3] = message.raw_mentions
    db[key] = messageData
    return messageData
  except:
    return 0


def sortTasksByDate(usersTasks):
  return sorted(usersTasks,key=lambda l:l[2])

def sortMeetingsByDate(usersMeetings):
  return sorted(usersMeetings,key=lambda l:l[3])

def getTaskEmbed(message):
  embed = discord.Embed(title=message.author.name + ", here are your current tasks!", color=0x96BDC6)
  embed.set_thumbnail(url="https://i.ibb.co/jMG9jCz/tasks-thumb.png")
  # retrieve tasks & add them as a field
  # first get all tasks from the server, then filter through all of them with the user containing the authors user id
  serverTasks = db.prefix("task" + str(message.guild.id))
  usersTasks = []
  for task in serverTasks:
    taskInfo = db[task]
    if message.author.id in taskInfo[3]:
      usersTasks.append(db[task])
  for task in sortTasksByDate(usersTasks):
      embed.add_field(name=task[0], value=task[1], inline=True)
      embed.add_field(name="Due date: ", value=task[2], inline=True)
      embed.add_field(name='\u200b', value='\u200b')
  return embed

def deleteTask(message): #!deleteTask task title
  taskTitle = message.content[12:].lower().strip(' ')
  serverTasks = db.prefix("task" + str(message.guild.id))
  for task in serverTasks:
    if db[task][0].lower().strip(' ') == taskTitle:
      del db[task]

# meetings
def addMeeting(message): #!addMeeting meeting name, meeting desc, meeting link, meeting date, person
  key = newItemKey(message, 1)
  messageData = message.content[12:].split(', ')
  try:
    datetime.strptime(messageData[3], DATETIMEFORMATINPUT)
  except:
    return 0
  messageData[4] = message.raw_mentions
  db[key] = messageData
  return messageData

def generateQuote(message):
  key = requests.get("https://zenquotes.io/api/random")
  quote_data = json.loads(key.text)
  quote = quote_data[0]['q']

  embed = discord.Embed(description = f'{message.author.mention} {quote}', color=0xE8CCBF)
  return embed
  

def getMeetingEmbed(message):
  embed = discord.Embed(title=message.author.name + ", here are your upcoming meetings!", color=0xCFB9A5)
  embed.set_thumbnail(url="https://i.ibb.co/n0qsNHV/Discord-Bot-Symbols.png")
  serverMeetings = db.prefix("meeting" + str(message.guild.id))
  usersMeetings = []
  for meeting in serverMeetings:
    meetingInfo = db[meeting]
    if message.author.id in meetingInfo[4]:
      usersMeetings.append(db[meeting])
    for meeting in sortMeetingsByDate(usersMeetings):
      embed.add_field(name=meetingInfo[0], value=meetingInfo[1], inline=True)
      embed.add_field(name="Meeting Date: ", value=meetingInfo[3], inline=True)
      embed.add_field(name="Meeting Link: ", value="https://"+meetingInfo[2], inline=True)
      embed.add_field(name='\u200b', value='\u200b', inline=False)
  return embed

def descriptionEmbed():
  embed = discord.Embed(title="EasyManage Bot Commands", description="Welcome to the EasyManage, the productivity manager which allows you to be stress-free!! We currently offer systems to deal with: tasks, meetings, reminders, pomodoro timers, and daily inspiration. With this bot, you can begin commands with the prefix ! and separate arguments with , (a comma followed by a space). https://github.com/Ishneet0710 ", color = 0xCFB9A5)
  return embed
      

def checkMeetings(message):
  serverMeetings = db.prefix("meeting" + str(message.guild.id))
  for meeting in serverMeetings:
    if datetime.strptime(db[meeting][3], DATETIMEFORMATINPUT) < datetime.now()-timedelta(days=1):
      del db[meeting]
  
# EVENTS
@client.event
async def on_ready():
  print("ready")

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Hi {member.name}, welcome to my Discord server!')
    await member.dm_channel.send(embed=descriptionEmbed())
    #documentation for users

# LOOPS
@tasks.loop(hours=24)
async def dailyUpdate():
  embed = discord.Embed(title="On today's agenda...", color=0xCFB9A5)
  serverMeetings = db.prefix("meeting875923634479321098")
  for meeting in serverMeetings:
    meetingInfo = db[meeting]
    if datetime.strptime(meetingInfo[3], DATETIMEFORMATINPUT).date() == datetime.now().date():
      embed.add_field(name=meetingInfo[0], value=meetingInfo[1], inline=True)
      embed.add_field(name="Meeting Date: ", value=meetingInfo[3], inline=True)
      embed.add_field(name="Meeting Link: ", value="https://"+meetingInfo[2], inline=True)
      participantsValue=""
      for i in range(len(meetingInfo[4])):
         participantsValue += "<@!" + str(meetingInfo[4][i]) + "> "
      embed.add_field(name="Participants: ", value=participantsValue, inline=True)
      embed.add_field(name='\u200b', value='\u200b', inline=False)
  try:
    await summaryChannel.send(embed=embed)
  except:
    print("Could not send summary. Has the summary channel been set?")
  
dailyUpdate.start()


# USER COMMANDS
@client.event
async def on_message(message):
  checkMeetings(message)
  if message.content.startswith("!"):
    # debugging
    if message.content.startswith("!debug"):
      displayDB()
    if message.content.startswith("!cleardb"):
      clearDB()
    ### TASKS
    # addTask
    if message.content.startswith("!addTask"):
      messageData = addTask(message)
      if messageData!=0:
        finalMessage = "Task added successfully! "
        for i in range(len(messageData[3])):
          finalMessage += "<@!" + str(messageData[3][i]) + "> "
        finalMessage += "are responsible for the **\"" + messageData[0] + "\"** task."
        await message.channel.send(finalMessage)
      else:
        await message.channel.send("Could not add task. Have you filled all of the parameters?")
    # viewTasks
    elif message.content.startswith("!viewTasks"):
      await message.channel.send(embed=getTaskEmbed(message))

    # deleteTasks
    elif message.content.startswith("!deleteTask"):
      deleteTask(message)
      await message.channel.send("Task deleted successfully!")
    ### MEETINGS
    elif message.content.startswith("!addMeeting"):
      
      if addMeeting(message) != 0:
        await message.channel.send("Added meeting!")
      else:
        await message.channel.send("There was an error adding this meeting. Make sure the date and time of the meeting is formatted correctly.")
    elif message.content.startswith("!viewMeetings"):
      await message.channel.send(embed=getMeetingEmbed(message))
    ###
    elif message.content.startswith("!quote"):
      await message.channel.send(embed=generateQuote(message))

    elif message.content.startswith("!reminder"): #!reminder amountoftime, thingtodo
      messageData = message.content.split(', ')
      time = messageData[0][10:]
      time = int(time)
      time = time*60
      reminder = messageData[1]
      await asyncio.sleep(time)
      await message.channel.send(f'{message.author.mention}, it\'s time to {reminder}!')


    elif message.content.startswith("!pomodoro"):
      global userID
      messageData = message.content.split(' ')
      userID = messageData[1]
      rounds = int(messageData[2])


      for round in range(rounds):
        embed = discord.Embed(title = f'Session #{round + 1}', color=0xE9D6EC)
        embed.add_field(name = "25 min Pomodoro Session", value = f'It\'s time to study, {message.author.mention}!')
        await message.channel.send(embed=embed)
        await asyncio.sleep(10)

        embedBreak = discord.Embed(title = f'Session #{round + 1}', color=0xE9D6EC)
        embedBreak.add_field(name = "5 min Break", value = f'Take a break, {message.author.mention}, you deserve it!', inline = False)
        await message.channel.send(embed=embedBreak)
        await asyncio.sleep(2)

      embedEnd = discord.Embed(title = f'Congratulations!', description = f'{message.author.mention}, your pomodoro sessions have ended!', color=0xE9D6EC)
      await message.channel.send(embed = embedEnd)


    elif message.content.startswith("!help"):
      await message.channel.send(embed = descriptionEmbed())
    elif message.content.startswith("!set_summary_channel"):
      global summaryChannel
      summaryChannel = message.channel
      await message.channel.send("Summary channel set! A daily meeting summary will be sent here.")
    
    else:
      await message.channel.send("Could not find that command; please try again.")



  else:
    return 0    


keep_alive()
client.run(botToken)