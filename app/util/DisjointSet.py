"""Tracks connectedness of our board. Provides lightning fast lookups to see exactly
what squares are reachable from where."""

import numpy as np


class Node(object):
    """Represents an abstract node in a
    connected component."""

    def __init__(self, pos):
        self.pos = pos
        self.parent = None
        self.children = set()
        self.rank = 0


class DisjointSet:
    """The disjointed set that provides information
    on the connectedness of the board.

    Has following attributes:
    board           Board           - Board object
    map             {'[x,y]':Node}  - dict mapping coords to Node objects
    """

    def __init__(self, board):
        """
        Initialize the disjoint set.
        
        param1: Board - Board object
        """
        self.board = board
        self.map = np.empty((board.width, board.height), dtype=object) # maps coords to Node objects
        
    def update(self):
        """
        Update connectivity based on Snake objects.
        """
        self.map = np.empty((self.board.width, self.board.height), dtype=object)
        boardWidth = self.board.width
        boardHeight = self.board.height
        for x in range(boardWidth):
            for y in range(boardHeight):
                weight = self.board.getWeight([x, y])
                if weight is 0:
                    continue
                
                newNode = Node([x, y])
                self.map[x, y] = newNode
                
                surrounding = self.getSurrounding([x, y])                
                for coord in surrounding:
                    adjacentNode = self.map[coord[0], coord[1]]
                    if adjacentNode is not None:
                        self.union(adjacentNode, newNode)

    def getSurrounding(self, coord):
        """
        Find the squares surrounding a coordinate.
        
        param1: [x,y] - square to search around
        return: [[x,y]] - surrounding squares
        """
        x = coord[0]
        y = coord[1]
        surrounding = []
        if (x - 1) >= 0:
            surrounding.append([x - 1, y])
        if (x + 1) < self.board.width:
            surrounding.append([x + 1, y])
        if (y + 1) < self.board.height:
            surrounding.append([x, y + 1])
        if (y - 1) >= 0:
            surrounding.append([x, y - 1])
        return surrounding

    def find(self, child):
        """
        Determines the root of a given Node.

        param1: Node - child to find the root of
        return: Node - root of the child
        """
        if child is None:
            return None
        parent = child.parent
        if parent is None:
            return child
        else:
            return self.find(parent)

    def union(self, node1, node2):
        """
        Provides a way for 2 disconnected components to connect.

        param1: Node - first component to connect
        param2: Node - second component to connect
        """
        root1 = self.find(node1)
        rank1 = root1.rank
        root2 = self.find(node2)
        rank2 = root2.rank
        
        if root1 == root2: # already connected
            return
        
        if rank1 < rank2:
            root1.parent = root2
            root2.children.add(root1)
            root2.children.update(root1.children)
        elif rank1 > rank2:
            root2.parent = root1
            root1.children.add(root2)
            root1.children.update(root2.children)
        else:
            root1.parent = root2
            root2.rank = rank2 + 1
            root2.children.add(root1)
            root2.children.update(root1.children)

    def getConnectedToNode(self, coord):
        """
        Return list of squares connected to the provided non-wall position.

        param1: [x,y] - name of square to find connected components from
        return: [[x,y]] - list of connected squares
        """
        child = self.map[coord[0], coord[1]]
        if child is None:
            raise ValueError('Node is a wall')
        root = self.find(child)

        returnable = [node.pos for node in root.children] + [root.pos]
        returnable.remove(coord)
        return returnable

    def getConnectedToWall(self, coord):
        """
        Return list of squares connected to the provided wall position.

        param1: [x,y] - name of wall to find connected components from
        return: [[x,y]] - list of connected squares
        """
        child = self.map[coord[0], coord[1]]
        if child is not None:
            raise ValueError('Node is not a wall')

        surroundingCoords = self.getSurrounding(coord)
        surroundingRoots = [self.find(self.getNode(coord)) for coord in surroundingCoords]
        surroundingFiltered = set([node for node in surroundingRoots if node is not None])

        reachable = []
        for node in surroundingFiltered:
            reachable += self.getConnectedToNode(node)
        return reachable

    def pathExistsFromNode(self, coord1, coord2):
        """
        Determine if 2 non-wall squares are connected.

        param1: [x,y] - first node position
        param2: [x,y] - second node position
        return: bool - True if connected, False otherwise
        """
        node1 = self.map[coord1[0], coord1[1]]
        node2 = self.map[coord2[0], coord2[1]]
        if node1 is None or node2 is None:
            raise ValueError('One of the nodes is a wall')
        
        return self.find(node1) == self.find(node2)
    
    def pathExistsFromWall(self, coord1, coord2):
        """
        Determine if a wall square and a free square are connected.

        param1: [x,y] - wall node position
        param2: [x,y] - free-space node position
        return: bool - True if connected, False otherwise
        """
        node1 = self.map[coord1[0], coord1[1]]
        node2 = self.map[coord2[0], coord2[1]]
        if node1 is not None:
            raise ValueError('First node must be a wall')
        if node2 is None:
            raise ValueError('Second node cannot be a wall')

        surroundingCoords = self.getSurrounding(coord1)
        surroundingRoots = [self.find(self.getNode(coord)) for coord in surroundingCoords]
        surroundingFiltered = set([node for node in surroundingRoots if node is not None])
        
        connected = False
        for root in surroundingFiltered:
            if self.find(root) == self.find(node2):
                connected = True
                
        return connected

    def getNode(self, coord):
        """
        Return the Node object that corresponds to a gives square.

        param1: [x,y] - name of the square to find
        return: Node - object corresponding to square
        """
        return self.map[coord[0], coord[1]]

    def toString(self, root):
        """
        Provides a way to print out the tree in a human-readable format.

        param1: string - name of root to display from
        """
        print('\t'*(5 - root.rank) + str(root.pos)) # NOTE: Incredibly crude implementation
        for child in root.children:
            self.toString(child)
