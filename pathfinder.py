import bisect

class Node(object):
    """A node used by the pathfinder.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None
        self.children = []
        self.f = 0  # "fitness" - total cost
        self.g = 0  # cost of getting to this point
        self.h = 0  # distance from the goal

    def initialize(self, distance, g):
        self.h = distance
        self.g = g
        self.f = self.h + self.g

    def __cmp__(self, other):
        return cmp(self.f, other.f)
    
    def setParent(self, parent):
        self.parent = parent
        
class Pathfinder(object):
    """Pathfinder that works on a grid.
    """
    directions = [(-1,0),  (1,0),
                  (0,-1),  (0,1),
                  (1,1),   (-1,-1),
                  (1,-1),  (-1,1) ]

    COST = 1
    
    FOUND_GOAL = 1
    NOT_DONE = 0
    NOT_RUNNING = -1
    IMPOSSIBLE = -2
    
    def __init__(self, cbValid):
        self.startX = 0
        self.startY = 0
        self.goalX = 0
        self.goalY = 0
        self.cbValid = cbValid
        self.running = 0
        self.clearNodes()

    def clearNodes(self):
        self.openSet = []
        self.closedSet = []
        self.best = None

    def setupPath(self, startX, startY, goalX, goalY):
        """setup the pathfinder to find a path.
        """
        print 'setting up path from: ',startX,' ',startY,'  to ',goalX, goalY
        if self.cbValid(goalX, goalY) == 0:
            return 0
        
        self.startX = startX
        self.startY = startY
        self.goalX = goalX
        self.goalY = goalY
        self.clearNodes()
        
        startNode = Node(startX, startY)
        startNode.initialize((goalX-startX)**2 + (goalY-startY)**2, 0)

        self.openSet.append(startNode)
        self.running = 1
        return 1

    def iteratePath(self):
        """Run a single iteration of the path finder.
        """
        if self.running == 0:
            return self.NOT_RUNNING
        if len(self.openSet) == 0:
            return self.IMPOSSIBLE
        
        # get the fittest node
        self.best = self.openSet.pop(0)
        self.closedSet.append(self.best)

        # check if we found the goal
        if self.best.x == self.goalX and self.best.y == self.goalY:
            return self.FOUND_GOAL

        # explore the new node
        for d in self.directions:
            x = self.best.x + d[0]
            y = self.best.y + d[1]
            if  self.cbValid(x, y):
                self.processAdjacent(self.best, x, y)
                
        return self.NOT_DONE
        
    def processAdjacent(self, parent, x, y):
        """calculate the costs and parent for a node.
        """
        g = parent.g + self.COST 
        checkNode = self.findNode(self.openSet, x, y) or self.findNode(self.closedSet, x, y)
        if checkNode:
            parent.children.append(checkNode)
            if g < checkNode.g:
                # update node with better route                
                checkNode.setParent(parent)
                checkNode.g = g
                checkNode.f = g + checkNode.h
        else:
            # unknow node. create it
            newNode = Node(x,y)
            newNode.setParent(parent)
            newNode.initialize((self.goalX-x)**2 + (self.goalY-y)**2, g)
            bisect.insort_right(self.openSet, newNode)


    def findNode(self, checklist, x, y):
        """check if a node is in the list"""
        for node in checklist:
            if node.x == x and node.y == y:
                return node
        return None
        
    def finishPath(self):
        """traverse backwards to build the correct path
        """
        node = self.best
        path = []
        i = 0
        while node:
            i = i + 1
            if i % 20 == 0:
                print "pathfinder traversing path backwards...", i, node.x, node.y
            path.insert(0, (node.x, node.y))
            node = node.parent
        self.running = 0
        print 'return path: ',path
        return path
