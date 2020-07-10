#!/usr/bin/python3
import socket
from pythonds.graphs import Graph
from time import sleep

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "irc.dtella.net" # Server
port = 6667
channel = "#bots" # Channel
botnick = "halcyon" # Your bots nick
admins = ["kes", "dragonfyre"]
exitcode = "bye " + botnick
msglog = []
logcap = 100
    
    
def pong(id): # respond to server Pings.
  ircsock.send(bytes("PONG :" + id + "\n", "UTF-8"))
  print("PONG :" + id + "\n")
  
def sendmsg(msg, target=channel): # sends messages to the target.
  ircsock.send(bytes("PRIVMSG "+ target +" :"+ msg +"\n", "UTF-8"))
  logmsg(msg)
  
def logmsg(msg):
  msglog.append(msg)
  if len(msglog)>logcap:
    msglog.pop(0)

def getsimilarword(word):
  return "poop"


def constructGraph(): # try this for serialization https://www.tutorialspoint.com/object_oriented_python/object_oriented_python_serialization.htm#:~:text=Pickle,a%20working%20Python%20object%20hierarchy.
  category_list = {}# should be [] ?
  english = open(dictionary_file, 'r') #define dictionary_file
  for word in english:
    word = word.strip('\n')
    for i in range(len(word)):
      category = word[:i] + "*" + word[i+1:]
      if category in category_list:
        category_list[category].append(word)
      else:
        category_list[category] = [word]
  for category in category_list.keys():
    for word1 in category_list[categories]:
      for word2 in category_list[categories]:
        if word1 != word2:
            g.addEdge(word1,word2)

def msglogsearch(word):
  for i in range(1, len(msglog)):
    if msglog[-i].find(word):
      return msglog[-i]
    
def parsemsg(msg, nick):
  #check for commands
  isAdmin = 0
  if nick in admins:
    isAdmin = 1
    
  if msg[0:2] == "y/": #y/word/ -> ward, just queries the bot for the passed word
    word = msg[2:]
    word = word[:word.find("/")]
    if word.find(" ") != -1:
      sendmsg("Only single words are supported")
      return
    sendmsg(getsimilarword(word))
      
  elif msg[0:2] == "x/": #x/word/ -> that's my favorite ward, finds recent message with passed word and prints message with replaced word
    word = msg[2:]
    word = word[:word.find("/")]
    if word.find(" ") != -1:
      sendmsg("Only single words are supported")
      return
    oldmsg = ""
    oldmsg = msglogsearch(word)
    if len(oldmsg) > 0:
      split = oldmsg.find(word)
      sendmsg(oldmsg[:split] + getsimilarword(word) + oldmsg[split+len(word):])
  else: # if not a command, log the msg
    logmsg(msg)
    
  
def main():
  ircsock.connect((server, port)) # Here we connect to the server using the port
  ircsock.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick + " " + botnick + "\n", "UTF-8")) #We are basically filling out a form with this line and saying to set all the fields to the bot nickname.
  ircsock.send(bytes("NICK "+ botnick +"\n", "UTF-8")) # assign the nick to the bot
  #ircsock.send(bytes("NICKSERV IDENTIFY " + botnickpass + "\n", "UTF-8"))
  sleep(5)
  ircsock.send(bytes("JOIN "+ channel +"\n", "UTF-8"))  # Join channel specified in globals
  while 1:
    ircmsg = ircsock.recv(2048).decode("UTF-8")
    ircmsg = ircmsg.strip('nr')
    print(ircmsg)
    if ircmsg.find("PRIVMSG") != -1:
      name = ircmsg.split('!',1)[0][1:]
      message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]
      parsemsg(message, name)
    if ircmsg.find("PING :") != -1:
      id = ircmsg[ircmsg.find("PING")+6:]
      pong(id)
      
main()