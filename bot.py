#!/usr/bin/python3
import socket
from time import sleep
import ladder
from random import choice

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "irc.dtella.net"  # Server
port = 6667
channel = "#bots"  # Channel
botnick = "halcyon"  # Your bots nick
admins = ["kes", "dragonfyre"]
exitcode = "bye " + botnick
msglog = []
logcap = 100
dictionary_file = "words.txt"
g = ladder.Graph()


def pong(id):  # respond to server Pings.
    ircsock.send(bytes("PONG :" + id + "\n", "UTF-8"))


def sendmsg(msg, target=channel):  # sends messages to the target.
    ircsock.send(bytes("PRIVMSG " + target + " :" + msg + "\n", "UTF-8"))
    logmsg(msg)


def logmsg(msg):
    msglog.append(msg)
    if len(msglog) > logcap:
        msglog.pop(0)


def getsimilarword(word):
    return choice(ladder.pullNeighbors(g, word))


def msglogsearch(word):
    i = len(msglog)-1
    while i >= 0:
        if word.lower() in msglog[i].lower():
            return msglog[i]
        i = i - 1


def parsemsg(msg, nick):
    # check for commands
    isAdmin = 0
    if nick in admins:
        isAdmin = 1

    if msg[0:2] == "y/":  # y/word/ -> ward, just queries the bot for the passed word
        print("<"+nick+"> "+msg)
        word = msg[2:]
        word = word[:word.find("/")]
        if word.find(" ") != -1:
            sendmsg("Only single words are supported")
            return
        sendmsg(getsimilarword(word))

    elif msg[0:2] == "x/":  # x/word/ -> that's my favorite ward, finds recent message with passed word and prints message with replaced word
        print("<"+nick+"> "+msg)
        word = msg[2:]
        word = word[:word.find("/")]
        if word.find(" ") != -1:
            sendmsg("Only single words are supported")
            return
        oldmsg = " "
        oldmsg = msglogsearch(word)
        if len(oldmsg) > 0:
            split = oldmsg.find(word)
            sendmsg(oldmsg[:split] + getsimilarword(word) +
                    oldmsg[split+len(word):])
    elif msg[0:2] == "?/":
        print("<"+nick+"> "+msg)
        word = msg[2:]
        word = word[:word.find("/")]
        if word.find(" ") != -1:
            sendmsg("Only single words are supported")
            return
        oldmsg = " "
        oldmsg = msglogsearch(word)
        sendmsg(oldmsg)
    elif msg[0:3] == "!wl":
        print("<"+nick+"> "+msg)
        words = word = msg[4:]
        split = words.find(" ")
        word1 = words[:split]
        word2 = words[split+1:]
        sendmsg(wordLadder(word1, word2))
    elif msg == "log":
      print("<"+nick+"> "+msg)
      printlog = " "
      i = 0
      while i < len(msglog):
        printlog = printlog + "," + msglog[i]
        i = i + 1
      sendmsg(printlog)
    else:  # if not a command, log the msg
        logmsg(msg)


def calcPath(y):
    x = y
    msg = ""
    while (x.getPred()):
        msg += x.getId() + " -> "
        x = x.getPred()
    msg += x.getId()
    return msg


def wordLadder(word1, word2):
    ladder.bfs(g, g.getVertex(word2))
    return calcPath(g.getVertex(word1))


def main():
    # Build the graph for the given dictionary
    g = ladder.constructGraph(dictionary_file)
    # Here we connect to the server using the port
    ircsock.connect((server, port))
    # We are basically filling out a form with this line and saying to set all the fields to the bot nickname.
    ircsock.send(bytes("USER " + botnick + " " + botnick +
                       " " + botnick + " " + botnick + "\n", "UTF-8"))
    # assign the nick to the bot
    ircsock.send(bytes("NICK " + botnick + "\n", "UTF-8"))
    #ircsock.send(bytes("NICKSERV IDENTIFY " + botnickpass + "\n", "UTF-8"))
    sleep(5)
    # Join channel specified in globals
    ircsock.send(bytes("JOIN " + channel + "\n", "UTF-8"))
    while 1:
        ircmsg = ircsock.recv(2048).decode("UTF-8")
        ircmsg = ircmsg.strip('nr')
        if ircmsg.find("PRIVMSG") != -1:
            name = ircmsg.split('!', 1)[0][1:]
            message = ircmsg.split('PRIVMSG', 1)[1].split(':', 1)[1]
            parsemsg(message, name)
        if ircmsg.find("PING :") != -1:
            id = ircmsg[ircmsg.find("PING")+6:]
            pong(id)


main()
