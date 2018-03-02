"""Process all game data. Handles interfacing with the hidden state machine,
passing data to the right places, and returning the best move given a game dictionary."""

import random
from app.obj.Snake import Snake
from app.obj.Food import Food
from app.util.StateMachine import StateMachine
from app.util.Processor import Processor
from app.util.DisjointSet import DisjointSet
from app.Board import Board


class Game:
    """
    World object has following top level attributes:

    weightGrid      (board)          - Board object
    width           (int)            - Board width
    height          (int)            - Board height
    you             (Snake)          - Snake object representing our snake
    food            (List<Point>]     - List object containing an array of points
    turn            (int)            - 0-indexed int representing completed turns
    snakes          (List<Snake>)    - dict of Snake objects currently in play
    """

    def __init__(self, data):
        """
        Initialize the Game class.

        param1: dict - all data from /start POST.
        """
        self.width = data['width']
        self.height = data['height']
        self.board = Board(self.width, self.height)

        self.snakes = {}
        self.us = None
        self.usName = ''
        self.food = None
        self.turn = 0
        self.set = None
        self.machine = None
        self.processor = None

    def firstMove(self, data):
        """
        Perform necessary actions upon receiving the first
        dictionary of the game

        param1: dictionary - all data from Battlesnake server.
        """
        for snake in data['snakes']['data']:
            snakeId = snake['id']
            self.snakes[snakeId] = Snake(snake)

        self.usName = data['you']['id']
        self.us = self.snakes[self.usName]
        self.food = Food(data['food'])
        self.set = DisjointSet(self.board)
        self.machine = StateMachine(self.board, self.set, self.snakes, self.us, self.food)
        self.processor = Processor(self.board, self.snakes, self.us, self.food)
        self.weightSnakes()

    def update(self, data):
        """
        Update game with current board from server.

        param1: dictionary - all data from Battlesnake server.
        """
        if data['turn'] is 0:
            self.firstMove(data)
            return

        """
        # update all of our snakes
        for snake in data['snakes']['data']:
            snakeId = snake['id']
            self.snakes[snakeId].update(snake)
        """

        #for each snake obj from last turn
        for snakeId in self.snakes:
            snakeFound = False

            #for each new snake obj
            for dataSnake in data['snakes']['data']:
                if dataSnake['id'] == snakeId:
                    #Update snake object
                    snakeFound = True
                    self.snakes[snakeId].update(dataSnake)

            if not snakeFound:
                del self.snakes[snakeId]

        self.food.update(data['food'])
        self.turn = data['turn']
        self.weightSnakes()

    def weightSnakes(self):
        """
        Perform state-independent weighting of snake bodies. If a specific state requires
        different waiting of snake heads or tails, then they may perform weighting manually.
        """
        self.board.resetWeights()

        for _, snake in self.snakes.items():
            self.board.setWeights(snake.getAllPositions(), 0)
            if snake != self.us and snake.getSize() < self.us.getSize():
                self.board.setWeights(self.set.getSurrounding(snake.getHeadPosition()), 0)

        self.set.update()

    def getTaunt(self):
        """
        Return taunt for the move request.
        """
        taunts = ['Do you have any non-GMO food?', 'War. War never changes', 'Sssssslithering',\
         'Snakes? I hate snakes', 'Where can a snake get a bite to eat around here', 'up', 'down',\
          'left', 'right', 'Trying to catch garter snakes']

        return random.choice(taunts)

    def getNextMove(self):
        """
        Use all algorithms to determine the next best move for our snake.
        """
        state = self.machine.getState()

        # Needs to be set to an [int, int]
        nextMove = []

        if state is 'IDLE':
            
            us = self.snakes[self.us]
            headPos = us.getHeadPosition()

            # we have already weighted snakes, so make sure we don't
            # make a turn that will trap us

            x = headPos[0]
            y = headPos[1]
            surrounding = []
            if (x - 1) >= 0:
                surrounding.append([x - 1, y])
            else:
                # empty lists ensure we know which direction corresponds
                # to which coordinate
                surrounding.append([])
            if (x + 1) < self.board.width:
                surrounding.append([x + 1, y])
            else:
                surrounding.append([])
            if (y + 1) < self.board.height:
                surrounding.append([x, y + 1])
            else:
                surrounding.append([])
            if (y - 1) >= 0:
                surrounding.append([x, y - 1])
            else:
                surrounding.append([])

            maxSpaceCoords = []
            maxSpaceLen = 0
            for coord in surrounding:
                if coord == []:
                    continue
                    
                # due to IDLE state, there must be at least 1 non-wall node
                weight = self.board.getWeight(coord)
                if weight == 0:
                    continue

                availableSpace = len(self.set.getConnectedToNode(coord))
                if maxSpaceLen < availableSpace:
                    maxSpaceCoords = [coord]
                    maxSpaceLen = availableSpace
                elif maxSpaceLen == availableSpace:
                    maxSpaceCoords.append(coord)

            # now we have a list of directions which will provide us with the
            # most maneuverability
            nextMove = maxSpaceCoords[0] # temporary

            
        elif state is 'HUNGRY':
            # eat food here
            pass
        elif state is 'TRAPPED':
            # be claustrophobic here
            pass
        elif state is 'STARVING':
            # stuff your face here
            pass
        elif state is 'CONFINED':
            # get out of here
            pass

        """
        THIS IS LEGACY CODE AND IS A CANDIDATE FOR REMOVAL

        self.processor.weightNotHitSnakes()
        self.processor.weightFood()
        self.processor.weightSmallSnakes()
        self.processor.weightLargeSnakes()

        self.board.setEdges()

        target = []
        ourSnake = self.snakes[self.us]

        priorityTarget = 0
        nodeValid = False

        while not nodeValid:
            topPriorityNode = self.board.getNodeWithPriority(priorityTarget)
            if self.board.isNodeWeightUnique(topPriorityNode):
                target = topPriorityNode
                priorityTarget += 1
            else:
                numDuplicates = self.board.countNodeWeightCopies(topPriorityNode)
                duplicateNodes = self.board.getNodesWithPriority(priorityTarget, \
                priorityTarget + numDuplicates - 1)
                closestLen = sys.maxsize
                closestPos = []

                for node in duplicateNodes:
                    tempPath = self.board.optimumPath(ourSnake.getHeadPosition(), node)
                    tempLen = len(tempPath)

                    if tempLen < closestLen and self.board.optimumPathLength(\
                    ourSnake.getHeadPosition(), node) != float('inf'):
                        closestLen = tempLen
                        closestPos = node

                priorityTarget += numDuplicates

                target = closestPos

            if target == []:
                nodeValid = False
            elif self.board.optimumPathLength(ourSnake.getHeadPosition(), target) != \
            float('inf'):
                nodeValid = True
        nextMove = self.processor.weightEnclosedSpaces(target)
        """
        direction = self.nodeToDirection(nextMove, self.us)
        return direction

    def nodeToDirection(self, node, snake):
        """
        Convert a coord array into an up, down, left, right direction.
        param1: [int,int] - x,y coords of a node.
        param2: Snake - snake in the game (ie, in snakes{})

        Raises: ValueError
            if: node is not adjacent to the snakes head

        return: string - direction to go
        """
        head = snake.getHeadPosition()

        if node[0] == (head[0] + 1):
            return 'right'
        if node[0] == (head[0] - 1):
            return 'left'
        if node[1] == (head[1] + 1):
            return 'down'
        if node[1] == (head[1] - 1):
            return 'up'
        else:
            raise ValueError('node must be adjacent')
