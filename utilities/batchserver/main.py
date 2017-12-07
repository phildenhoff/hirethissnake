"""Server to rapidly simulate games to determine loss trends"""

import sys
import json
import requests
from State import State


def runGame():
    numSnakes = 1
    state = State(20, 20, numSnakes, 1)

    for i in range(0, numSnakes):
        response = requests.post("http://localhost:8080/start", data=json.dumps({"width": 20, "height": 20, "game_id": "gameid"}), headers={'content-type': 'application/json'})

    allDead = False
    while(not allDead):

        response = requests.post("http://localhost:8080/move", data=state.getState(), headers={'content-type': 'application/json'})
        move = eval(response.text)["move"]
        print(move)
        state.incrementState(stepSnakes(state))
        print(state.getState())
        state.setPos(0, [[20,19]])
        #contact servers and update state here
        print(state.getState())
        state.kill()
        print(state.getState())
        if state.numAlive() == 0:
            allDead = True
        print(state.getState())

    #print(state.getState())

def printGames(games, p, m):
    #given games[], print to file/directory p
    #if m(bool), print each game to a different file
    return

def stepSnakes(gameState):
    #send gameState to each snake and waits for a response
    #retruns an array of moves
    return []

def generateFood(numItems):
    #check to see if a random food item is due to be added
    return



## Accept command inputs ##
#-s 'game state to run from'
#   if not present, use default
#-n 'number of games to run'
#   will have hard upper limit
#-p 'path for game outcomes'
#   if not present, use default
#-m 'print separate files for each game'
#   if not present, all games in one file
#-f 'number of food items at any one time'
#   if not present, use default

## Generate game state to send to snakes ##
## Given a move, modify the game state to match ##
## Build in local snakes and web snakes ##

if __name__ == '__main__':
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        raise ValueError('Invalid arguments')
    for i in range(0, int(sys.argv[1])):
        runGame()
