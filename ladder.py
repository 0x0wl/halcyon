import sys

class Graph:
    def __init__(self):
        self.vertices = {}
        self.numVertices = 0

    def addVertex(self, key):
        self.numVertices = self.numVertices + 1
        newVertex = Vertex(key)
        self.vertices[key] = newVertex
        return newVertex

    def getVertex(self, n):
        if n in self.vertices:
            return self.vertices[n]
        else:
            return None

    def __contains__(self, n):
        return n in self.vertices

    def addEdge(self, f, t, cost=0):
        if f not in self.vertices:
            nv = self.addVertex(f)
        if t not in self.vertices:
            nv = self.addVertex(t)
        self.vertices[f].addNeighbor(self.vertices[t], cost)

    def getVertices(self):
        return list(self.vertices.keys())

    def __iter__(self):
        return iter(self.vertices.values())


class Vertex:
    def __init__(self, num):
        self.id = num
        self.connectedTo = {}
        self.color = 'white'
        self.dist = sys.maxsize
        self.pred = None
        self.disc = 0
        self.fin = 0

    def addNeighbor(self, nbr, weight=0):
        self.connectedTo[nbr] = weight

    def setColor(self, color):
        self.color = color

    def setDistance(self, d):
        self.dist = d

    def setPred(self, p):
        self.pred = p

    def setDiscovery(self, dtime):
        self.disc = dtime

    def setFinish(self, ftime):
        self.fin = ftime

    def getFinish(self):
        return self.fin

    def getDiscovery(self):
        return self.disc

    def getPred(self):
        return self.pred

    def getDistance(self):
        return self.dist

    def getColor(self):
        return self.color

    def getConnections(self):
        return self.connectedTo.keys()

    def getWeight(self, nbr):
        return self.connectedTo[nbr]

    def __str__(self):
        return str(self.id) + ":color " + self.color + ":disc " + str(self.disc) + ":fin " + str(self.fin) + ":dist " + str(self.dist) + ":pred \n\t[" + str(self.pred) + "]\n"

    def getId(self):
        return self.id

    def reset(self):
        #self.connectedTo = {}
        self.color = 'white'
        self.dist = sys.maxsize
        self.pred = None
        self.disc = 0
        self.fin = 0


class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)


def constructGraph(dictionary_file):
    g = Graph()
    category_list = {}
    english = open(dictionary_file, 'r')
    for word in english:
        word = word.strip('\n').lower()
        g.addVertex(word)
        for i in range(len(word)):
            category = word[:i] + "*" + word[i+1:]
            if category in category_list:
                category_list[category].append(word)
            else:
                category_list[category] = [word]
    for category in category_list.keys():
        for word1 in category_list[category]:
            for word2 in category_list[category]:
                if word1 != word2:
                    g.addEdge(word1, word2)

    return g


#build a tree for Vertex root
def bfs(g, root):
    cache = [root]
    root.setDistance(0)
    root.setPred(None)
    q = Queue()
    q.enqueue(root)
    while (q.size() > 0):
        currentVert = q.dequeue()
        for nbr in currentVert.getConnections():
            cache.append(nbr)
            if (nbr.getColor() == 'white'):
                nbr.setColor('grey')
                nbr.setDistance(currentVert.getDistance() + 1)
                nbr.setPred(currentVert)
                q.enqueue(nbr)
        currentVert.setColor('black')
    return cache

def wipe(cache):
    for vertex in cache:
        vertex.reset()

#debug
def printNeighbors(g, word):
    [print(nbr.getId()) for nbr in g.getVertex(word).getConnections()]

#for use with blake's function idea
def pullNeighbors(g, word):
    return [nbr.getId() for nbr in g.getVertex(word).getConnections()]