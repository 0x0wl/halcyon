#!/usr/bin/python3
import socket
from time import sleep
import ladder
from random import choice
from sys import exit

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "irc.dtella.net"  # Server
port = 6667
channel = "#dtella"  # Channel
botnick = "halcyon"  # Your bots nick
admins = ["kes", "dragonfyre"]
exitcode = "bye " + botnick
msglog = []
logcap = 100
dictionary_file = "words.txt"
# Build the graph for the given dictionary
g = ladder.constructGraph(dictionary_file)


def pong(id):  # respond to server Pings.
    ircsock.send(bytes("PONG :" + id + "\n", "UTF-8"))


def sendmsg(msg, target=channel):  # sends messages to the target.
    ircsock.send(bytes("PRIVMSG " + target + " :" + msg + "\n", "UTF-8"))
    logmsg(botnick, msg)


def logmsg(nick, msg):
    msglog.append("<"+nick+"> "+msg)
    if len(msglog) > logcap:
        msglog.pop(0)


def getsimilarword(word):
    word = word.lower()
    if g.getVertex(word) and len(ladder.pullNeighbors(g, word)) > 0:
        new_word = choice(ladder.pullNeighbors(g, word))
        return new_word
    else:
        return word


def msglogsearch(word):
    i = len(msglog)-1
    while i >= 0:
        if word.lower() in msglog[i].lower():
            return msglog[i]
        i = i - 1
    return ""

def fetchNeighbors(word):
    response = ""
    nbrs = ladder.pullNeighbors(g, word)
    for nbr in nbrs:
        response += nbr + ", "
    if len(response) > 0:
        return response[:-2]
    else:
        return "no neighbors for "+word


def parsemsg(msg, nick):
    # check for commands
    isAdmin = 0
    if nick in admins:
        isAdmin = 1
    try:
        if msg[0:2] == "y/":  # y/word/ -> ward, just queries the bot for the passed word
            print("<"+nick+"> "+msg)
            word = msg[2:]
            word = word.strip("/")
            if word.find(" ") != -1:
                sendmsg("Only single words are supported")
                return
            sendmsg(getsimilarword(word))

        elif msg[0:2] == "x/":  # x/word/ -> that's my favorite ward, finds recent message with passed word and prints message with replaced word
            print("<"+nick+"> "+msg)
            word = msg[2:]
            word = word.strip("/")
            if word.find(" ") != -1:
                sendmsg("Only single words are supported")
                return
            oldmsg = ""
            oldmsg = msglogsearch(word)
            if len(oldmsg) > 0:
                split = oldmsg.find(word.lower())
                if split >= 0:
                    sendmsg(oldmsg[:split] + getsimilarword(word) + oldmsg[split+len(word):])
                else:
                    sendmsg("[ERR] bot is just literally bad sry.")
            else:
                sendmsg("can't find any recent messages containing " + word)
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
            words = msg[4:].split()
            if len(words) == 1:
                newmsg = fetchNeighbors(words[0])
            elif len(words) == 2:
                if len(words[0]) == len(words[1]):
                    try:
                        newmsg = wordLadder(words[0], words[1])
                    except:
                        newmsg = "[ERR] command not formatted properly."
                else:
                    newmsg = words[0] + " and " + words[1] + " are not the same length."
            sendmsg(newmsg)
            
        
        #elif msg[0:3] == "log":
        #print("<"+nick+"> "+msg)
        #printlog = " "
        #i = 0
        #while i < len(msglog):
            #printlog = printlog + "|" + msglog[i]
            #i = i + 1
        #sendmsg(printlog)
        #elif msg[0:2] == "ll":
        #sendmsg(str(len(msglog)))
        
        else:  # if not a command, log the msg
            logmsg(nick, msg)
    except Exception as e:
        print(e)
        sendmsg("malformatted request")


def calcPath(y):
    x = y
    msg = ""
    while (x.getPred()):
        msg += x.getId() + " -> "
        x = x.getPred()
    msg += x.getId()
    return msg


def wordLadder(word1, word2):
    global g
    global dictionary_file
    if "Vertex" in str(type(g.getVertex(word1.lower()))) and "Vertex" in str(type(g.getVertex(word2.lower()))):
        cache = []
        cache = ladder.bfs(g, g.getVertex(word2.lower()))
        path = calcPath(g.getVertex(word1.lower()))
        ladder.wipe(cache)
        #g = ladder.constructGraph(dictionary_file)
        if path.find("->") != -1:
            return path
        else:
            return "no path between " + word1 + " and " + word2 + "."
    else:
        w1 = 0
        w2 = 0
        if not "Vertex" in str(type(g.getVertex(word1))):
            w1 = 1
        if not "Vertex" in str(type(g.getVertex(word2))):
            w2 = 1
        if w1 and not w2:
            return word1 + " not in dictionary."
        elif w2 and not w1:
            return word2 + " not in dictionary."
        elif w1 and w2:
            return "neither " + word1 + " nor " + word2 + " in dictionary."
        else:
            return "[ERR] outlier catch. Please contact Kes."


def main():

    # Here we connect to the server using the port
    ircsock.connect((server, port))
    # We are basically filling out a form with this line and saying to set all the fields to the bot nickname.
    ircsock.send(bytes("USER " + botnick + " " + botnick +
                       " " + botnick + " " + botnick + "\n", "UTF-8"))
    # assign the nick to the bot
    ircsock.send(bytes("NICK " + botnick + "\n", "UTF-8"))
    #ircsock.send(bytes("NICKSERV IDENTIFY " + botnickpass + "\n", "UTF-8"))
    sleep(5)
    # set the bot mode
    ircsock.send(bytes("MODE " + botnick + " +B\n", "UTF-8"))
    # Join channel specified in globals
    ircsock.send(bytes("JOIN " + channel + "\n", "UTF-8"))
    while 1:
        try:
            ircmsg = ircsock.recv(2048).decode("UTF-8")
        except KeyboardInterrupt:
            exit()
        except:
            print("could not decode message")
        ircmsg = ircmsg.strip('\n\r')
        if ircmsg.find("PRIVMSG") != -1:
            name = ircmsg.split('!', 1)[0][1:]
            message = ircmsg.split('PRIVMSG', 1)[1].split(':', 1)[1]
            parsemsg(message, name)
        if ircmsg.find("PING :") != -1:
            id = ircmsg[ircmsg.find("PING")+6:]
            pong(id)


main()
