import os
import copy
import json
import math
import time
import random
import datetime
import traceback
from PIL import Image, ImageDraw, ImageColor

#bord paramaters
GRID_SIZE = 7
PERCENTAGE_SQUARES = 0.7
PERCENTAGE_PATHS = 0.5
PROBABILITY_ONE_WAY = 0.1
BIAS = 0.05

#game settings
NUM_PLAYERS = 3
STARTING_INVENTORY = []
STARTING_GOLD = 3
STARTING_SPEED = 1
SHOP_PURCHACE_LIMIT = 3
CHANCE_OF_INFLATION = 0.5
CHANCE_OF_SUPER_INFLATION = 0.05
BLACKJACK_TARGET = 31
BLACKJACK_DEALER_CAUTION = 5
GYM_PROGRESS_REQUIRED = 2
WINGERIA_PROGRESS_REQUIRED = 4
MINIMUM_SPEED = 0.25

#assertions
assert GRID_SIZE > 3, 'grid size must be greater than 3!'
assert 0 < PERCENTAGE_SQUARES and PERCENTAGE_SQUARES <= 1, 'percentage squares must be between 0 and 1!'
assert 0 < PERCENTAGE_PATHS and PERCENTAGE_PATHS <= 1, 'percentage paths must be between 0 and 1!'
assert 0 < PROBABILITY_ONE_WAY and PROBABILITY_ONE_WAY <= 1, 'probability one way must be between 0 and 1!'
assert 0 < BIAS and BIAS <= 1-PERCENTAGE_PATHS, f'bias must be between 0 and {1-PERCENTAGE_PATHS}'
assert NUM_PLAYERS > 1, 'number of players must be more than 1!'
assert STARTING_SPEED > 0, 'starting speed must be positive!'
assert SHOP_PURCHACE_LIMIT > 0, 'shop purchase limit must be positive!'
assert 0 <= CHANCE_OF_INFLATION and CHANCE_OF_INFLATION <= 1, 'chance of inflation must be between 0 and 1!'
assert 0 <= CHANCE_OF_SUPER_INFLATION and CHANCE_OF_SUPER_INFLATION <= 1, 'chance of super inflation must be between 0 and 1!'
assert BLACKJACK_TARGET >= 21, 'blackjack target must be greater than or equal to 21!'
assert 0 <= BLACKJACK_DEALER_CAUTION and BLACKJACK_DEALER_CAUTION <= BLACKJACK_TARGET, f'blackjack dealer caution must be in between 0 and {BLACKJACK_TARGET}!'
assert GYM_PROGRESS_REQUIRED > 0, 'gym progress required must be positive!'
assert WINGERIA_PROGRESS_REQUIRED > 0, 'wingeria progress required must be positive!'
assert MINIMUM_SPEED >= 0, 'minimum speed must be non negative!'

#colourings
def getColour(r, g, b, background=False):
    return f'\033[{48 if background else 38};2;{r};{g};{b}m'

CLEAR = '\033[0m'

ERROR = getColour(255, 43, 89)

RED = getColour(255, 0, 0)
GREEN = getColour(0, 255, 0)
ORANGE = getColour(255, 123, 8)
YELLOW = getColour(255, 210, 8)
CYAN = getColour(0, 217, 255)
TURQUOISE = getColour(0, 255, 183)
GRAY = getColour(69, 69, 69)

EMPTY_SPACE = getColour(138, 138, 138)
FLAMINGO_SPACE = getColour(255, 0, 234)
HOME_SPACE = getColour(214, 179, 0)
SHADOW_REALM_SPACE = getColour(77, 9, 186)
GOOD_SPACE = getColour(17, 255, 0)
BAD_SPACE = getColour(255, 4, 0)
SHOP_SPACE = getColour(0, 98, 255)
TELEPORT_SPACE = getColour(255, 162, 0)
GAMBLING_SPACE = getColour(148, 14, 4)
TIMEWARP_SPACE = getColour(0, 97, 112)
PAPAS_WINGERIA_SPACE = getColour(133, 60, 1)
GYM_SPACE = getColour(0, 199, 192)
QUEST_SPACE = getColour(176, 0, 230)
ENTANGLEMENT_SPACE = getColour(255, 88, 10)

def fillSpaces(board, fillWith, howMany, initialState):
    linearBoard = sum(board, [])
    initialIndexes = [n for n, x in enumerate(linearBoard) if x == initialState]
    chosenSpaces = random.sample(initialIndexes, howMany)
    for n, _ in enumerate(linearBoard):
        if n in chosenSpaces:
            linearBoard[n] = fillWith
    return [linearBoard[x*GRID_SIZE:(x+1)*GRID_SIZE] for x in range(GRID_SIZE)]

def findPossiblePaths(board, endPos, oneWay, directions):
    possiblePaths = []
    #up
    if 'up' in directions:
        row = endPos['row']
        done = False
        while not done:
            row -= 1
            if row < 0:
                done = True
            elif board[row][endPos['col']] != None:
                done = True
                possiblePaths.append({"end": endPos, "start": {"row": row, "col": endPos['col']}, "oneWay": oneWay})
    #down
    if 'down' in directions:
        row = endPos['row']
        done = False
        while not done:
            row += 1
            if row >= GRID_SIZE:
                done = True
            elif board[row][endPos['col']] != None:
                done = True
                possiblePaths.append({"end": endPos, "start": {"row": row, "col": endPos['col']}, "oneWay": oneWay})
    #left
    if 'left' in directions:
        col = endPos['col']
        done = False
        while not done:
            col -= 1
            if col < 0:
                done = True
            elif board[endPos['row']][col] != None:
                done = True
                possiblePaths.append({"end": endPos, "start": {"row": endPos['row'], "col": col}, "oneWay": oneWay})
    #right
    if 'right' in directions:
        col = endPos['col']
        done = False
        while not done:
            col += 1
            if col >= GRID_SIZE:
                done = True
            elif board[endPos['row']][col] != None:
                done = True
                possiblePaths.append({"end": endPos, "start": {"row": endPos['row'], "col": col}, "oneWay": oneWay})
    return possiblePaths

def generateAValidHighway(board, paths):
    validPath = False
    while not validPath:
        validCell = False
        while not validCell:
            row = random.randint(0, GRID_SIZE-1)
            col = random.randint(0, GRID_SIZE-1)
            if board[row][col] not in [None, 'home', 'flamingo', 'shadow realm']:
                count = 0
                startPos = {"row": row, "col": col}
                for path in paths:
                    if path['start'] == startPos or path['end'] == startPos:
                        count += 1
                if count < 4:
                    validCell = True
        validCell = False
        while not validCell:
            row = random.randint(0, GRID_SIZE-1)
            col = random.randint(0, GRID_SIZE-1)
            if board[row][col] not in [None, 'home', 'flamingo', 'shadow realm']:
                count = 0
                endPos = {"row": row, "col": col}
                for path in paths:
                    if path['start'] == endPos or path['end'] == endPos:
                        count += 1
                if count < 4:
                    validCell = True
        path = {"start": startPos, "end": endPos, "oneWay": False}
        possiblePaths = [
            {"start": startPos, "end": endPos, "oneWay": True},
            {"start": startPos, "end": endPos, "oneWay": False},
            {"start": endPos, "end": startPos, "oneWay": True},
            {"start": endPos, "end": startPos, "oneWay": False},
        ]
        alreadyExisting = False
        for possiblePath in possiblePaths:
            if possiblePath in paths:
                alreadyExisting = True
        if (not alreadyExisting) and (startPos['row'] != endPos['row']) and (startPos['col'] != endPos['col']):
            validPath = True
            return path

def generateBoard():
    print('generating board...')
    print(' attemtpting to fill in the the map...')
    reallyPossible = False
    while not reallyPossible:
        #initialise board
        print('  creating board array...')
        board = []
        decorators = []
        for _ in range(GRID_SIZE):
            board.append([None]*GRID_SIZE)
            decoratorsRow = []
            for _ in range(GRID_SIZE):
                decoratorsRow.append([])
            decorators.append(decoratorsRow)
        #add empty spaces
        print('  adding empty spaces...')
        numEmpties = 0
        for n, row in enumerate(board):
            for m, _ in enumerate(row):
                if random.random() < PERCENTAGE_SQUARES:
                    board[n][m] = 'empty'
                    numEmpties += 1
        #add home space
        print('  adding home space...')
        midpoint = GRID_SIZE // 2
        board[midpoint][midpoint] = 'home'
        #add other spaces
        print('  adding other spaces...')
        board = fillSpaces(board, 'shadow realm', 1, 'empty')
        board = fillSpaces(board, 'flamingo', 1, 'empty')
        board = fillSpaces(board, 'good', numEmpties // 10, 'empty')
        board = fillSpaces(board, 'bad', numEmpties // 10, 'empty')
        board = fillSpaces(board, 'shop', numEmpties // 8, 'empty')
        board = fillSpaces(board, 'teleport', numEmpties // 20, 'empty')
        board = fillSpaces(board, 'gambling', numEmpties // 20, 'empty')
        board = fillSpaces(board, 'timewarp', numEmpties // 20, 'empty')
        board = fillSpaces(board, 'papas wingeria', numEmpties // 12, 'empty')
        board = fillSpaces(board, 'gym', numEmpties // 12, 'empty')
        board = fillSpaces(board, 'quest', numEmpties // 10, 'empty')
        board = fillSpaces(board, 'entanglement', numEmpties // 20, 'empty')
        #get positions of flamingo and shadow realm and home
        for n, row in enumerate(board):
            for m, cell in enumerate(row):
                if cell == 'flamingo':
                    flamingoPos = {"row": n, "col": m}
        for n, row in enumerate(board):
            for m, cell in enumerate(row):
                if cell == 'shadow realm':
                    shadowRealmPos = {"row": n, "col": m}
        homePos = {"row": midpoint, "col": midpoint}
        #repeat until game is possible
        print('  attempting to add pathways...')
        possible = False
        bias = 0
        while not possible:
            print('   adding paths to flamingo, home, shadow realm...')
            #initialise paths
            paths = []
            allDirections = ['up', 'down', 'left', 'right']
            #add path to flamingo
            possiblePaths = [path for path in findPossiblePaths(board, flamingoPos, False, allDirections) if path['start'] != shadowRealmPos]
            paths.append(random.choice(possiblePaths))
            #add paths to shadow realm
            possiblePaths = [path for path in findPossiblePaths(board, shadowRealmPos, False, allDirections) if path['start'] != flamingoPos]
            paths += possiblePaths
            #add paths from home
            possiblePaths = [path for path in findPossiblePaths(board, homePos, False, allDirections) if path['start'] != shadowRealmPos and path['start'] != flamingoPos]
            paths += possiblePaths
            #add internal paths
            print(f'   adding internal paths with chance {PERCENTAGE_PATHS + bias}...')
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    pos = {"row": row, "col": col}
                    if board[row][col] not in [None, 'home', 'flamingo', 'shadow realm']:
                        #down
                        if random.random() < (PERCENTAGE_PATHS + bias):
                            possiblePaths = [path for path in findPossiblePaths(board, pos, random.random() < PROBABILITY_ONE_WAY, ['down']) if path['start'] != homePos and path['start'] != flamingoPos and path['start'] != shadowRealmPos]
                            if len(possiblePaths) != 0:
                                if possiblePaths[0]['oneWay'] == True:
                                    newPossiblePaths = [possiblePaths[0], {"start": possiblePaths[0]['end'], "end": possiblePaths[0]['start'], "oneWay": True}]
                                    paths.append(random.choice(newPossiblePaths))
                                else:
                                    paths += possiblePaths
                        #right
                        if random.random() < (PERCENTAGE_PATHS + bias):
                            possiblePaths = [path for path in findPossiblePaths(board, pos, random.random() < PROBABILITY_ONE_WAY, ['right']) if path['start'] != homePos and path['start'] != flamingoPos and path['start'] != shadowRealmPos]
                            if len(possiblePaths) != 0:
                                if possiblePaths[0]['oneWay'] == True:
                                    newPossiblePaths = [possiblePaths[0], {"start": possiblePaths[0]['end'], "end": possiblePaths[0]['start'], "oneWay": True}]
                                    paths.append(random.choice(newPossiblePaths))
                                else:
                                    paths += possiblePaths
            print('   checking if this is possible...')
            highwayInformation = decideHighwayInformation(board, paths)
            if isPossibleToGetEverywhere(board, paths, homePos, highwayInformation) and not areThereAnyPurgatories(board, paths, highwayInformation):
                print('    it is!')
                possible = True
                reallyPossible = True
            else:
                bias += BIAS
                print(f'    its not... try again with path chance {PERCENTAGE_PATHS + bias}.')
                if PERCENTAGE_PATHS + bias > 1:
                    print('    path chance now above 1, so scrap the whole thing and try again...')
                    possible = True #this is a lie, it is to break out of the while loop to scrap this map and try again
    #add highways
    print(' adding highways...')
    for _ in range((GRID_SIZE // 2)):
        paths.append(generateAValidHighway(board, paths))
    #generate additional highways to shadow realm
    print(' adding additional highways to the shadow realm...')
    cellsWithLessThan4Paths = []
    for n, row in enumerate(board):
        for m, col in enumerate(row):
            count = 0
            cell = {"row": n, "col": m}
            for path in paths:
                if path['start'] == cell or path['end'] == cell:
                    count += 1
            if (count < 4) and (n != shadowRealmPos['row']) and (m != shadowRealmPos['col']) and col != None and col != 'flamingo':
                cellsWithLessThan4Paths.append(cell)
    numNewPaths = len(cellsWithLessThan4Paths)//8
    connectingCells = random.sample(cellsWithLessThan4Paths, numNewPaths)
    for cell in connectingCells:
        paths.append({"start": cell, "end": shadowRealmPos, "oneWay": False})
    #add pathDecorators
    pathDecorators = []
    for _ in paths:
        pathDecorators.append(copy.deepcopy([]))
    #return
    print('done!')
    print('generating image...')
    return board, paths, decorators, pathDecorators

def generateImage(board, paths, quantumEntanglements):
    width = GRID_SIZE*100
    height = GRID_SIZE*100

    mainImg = Image.new('RGBA', (width,height), ImageColor.getcolor('#ffffff', 'RGBA'))
    draw = ImageDraw.Draw(mainImg)

    for n, path in enumerate(paths):
        if path['oneWay']:
            draw.line((path['start']['col']*100+50, path['start']['row']*100+50, path['end']['col']*100+50, path['end']['row']*100+50), fill=ImageColor.getcolor('#696969', 'RGBA'), width=10)
            if path['end']['col'] > path['start']['col'] and path['end']['row'] == path['start']['row']: #right
                draw.regular_polygon((math.ceil((path['end']['col']+path['start']['col'])/2)*100, path['start']['row']*100+50, 15), 3, 270, fill=ImageColor.getcolor('#696969', 'RGBA'))
            if path['end']['col'] < path['start']['col'] and path['end']['row'] == path['start']['row']: #left
                draw.regular_polygon((math.ceil((path['end']['col']+path['start']['col'])/2)*100, path['start']['row']*100+50, 15), 3, 90, fill=ImageColor.getcolor('#696969', 'RGBA'))
            if path['end']['col'] == path['start']['col'] and path['end']['row'] > path['start']['row']: #down
                draw.regular_polygon((path['start']['col']*100+50, math.ceil((path['end']['row']+path['start']['row'])/2)*100, 15), 3, 180, fill=ImageColor.getcolor('#696969', 'RGBA'))
            if path['end']['col'] == path['start']['col'] and path['end']['row'] < path['start']['row']: #up
                draw.regular_polygon((path['start']['col']*100+50, math.ceil((path['end']['row']+path['start']['row'])/2)*100, 15), 3, 0, fill=ImageColor.getcolor('#696969', 'RGBA'))
        elif path['start']['col'] != path['end']['col'] and path['start']['row'] != path['end']['row']:
            draw.line((path['start']['col']*100+50, path['start']['row']*100+50, path['end']['col']*100+50, path['end']['row']*100+50), fill=ImageColor.getcolor('#0000ff', 'RGBA'), width=10)
        else:
            draw.line((path['start']['col']*100+50, path['start']['row']*100+50, path['end']['col']*100+50, path['end']['row']*100+50), fill=ImageColor.getcolor('#000000', 'RGBA'), width=10)
    for entanglement in quantumEntanglements:
        if entanglement[0]['col'] == entanglement[1]['col']:
            draw.line((entanglement[0]['col']*100+65, entanglement[0]['row']*100+50, entanglement[1]['col']*100+65, entanglement[1]['row']*100+50), fill=ImageColor.getcolor('#ff580a', 'RGBA'), width=10)
        elif entanglement[0]['row'] == entanglement[1]['row']:
            draw.line((entanglement[0]['col']*100+50, entanglement[0]['row']*100+65, entanglement[1]['col']*100+50, entanglement[1]['row']*100+65), fill=ImageColor.getcolor('#ff580a', 'RGBA'), width=10)
        else:
            draw.line((entanglement[0]['col']*100+50, entanglement[0]['row']*100+50, entanglement[1]['col']*100+50, entanglement[1]['row']*100+50), fill=ImageColor.getcolor('#ff580a', 'RGBA'), width=10)
    for n, row in enumerate(board):
        for m, cell in enumerate(row):
            if cell == 'empty':
                colour = '#8A8A8A'
            if cell == 'flamingo':
                colour = '#ff00ea'
            if cell == 'home':
                colour = '#d6b200'
            if cell == 'shadow realm':
                colour = '#4d09ba'
            if cell == 'good':
                colour = '#11ff00'
            if cell == 'bad':
                colour = '#ff0400'
            if cell == 'shop':
                colour = '#0062ff'
            if cell == 'teleport':
                colour = '#ffa200'
            if cell == 'gambling':
                colour = '#6b0a0a'
            if cell == 'timewarp':
                colour = '#006170'
            if cell == 'papas wingeria':
                colour = '#853c01'
            if cell == 'gym':
                colour = '#00c7c0'
            if cell == 'quest':
                colour = '#b000e6'
            if cell == 'entanglement':
                colour = '#ff580a'
            if cell != None:
                draw.rectangle((m*100+15, n*100+15, m*100+85, n*100+85), fill=ImageColor.getcolor(colour, 'RGBA'), outline=ImageColor.getcolor('#000000', 'RGBA'), width=5)
        
    mainImg.save(f'image.png', 'PNG')

def decideHighwayInformation(board, paths):
    highways = [path for path in paths if path['start']['row'] != path['end']['row'] and path['start']['col'] != path['end']['col']]
    highwayInformation = []
    for highway in highways:
        thisHighwaysInformation = []
        for startEnd in ['start', 'end']:
            moves = findPossibleMoves(paths, highway[startEnd], False, highwayInformation)
            if board[highway[startEnd]['row']][highway[startEnd]['col']] == 'shadow realm':
                thisHighwaysInformation.append({"row": highway[startEnd]['row'], "col": highway[startEnd]['col'], "direction": 'shadow realm'})
            else:
                possibleDirections = ['up', 'down', 'left', 'right']
                for move in moves:
                    possibleDirections.remove(move['direction'])
                for information in highwayInformation:
                    for subInformation in information:
                        if subInformation['row'] == highway[startEnd]['row'] and subInformation['col'] == highway[startEnd]['col']:
                            possibleDirections.remove(subInformation['direction'])
                thisHighwaysInformation.append({"row": highway[startEnd]['row'], "col": highway[startEnd]['col'], "direction": random.choice(possibleDirections)})
        highwayInformation.append(thisHighwaysInformation)
    return highwayInformation

def findPossibleMoves(paths, position, includeHighways, highwayInformation):
    possibleMoves = []
    possibleDirections = ['up', 'down', 'left', 'right']
    possiblePaths = [(n, path) for n, path in enumerate(paths) if path['start'] == position or (path['end'] == position and path['oneWay'] == False)]
    numNonHighways = len([path for path in paths if path['start']['row'] == path['end']['row'] or path['start']['col'] == path['end']['col']])
    for (n, path) in possiblePaths:
        if path['start'] == position:
            destination = path['end']
        else:
            destination = path['start']
        if destination['row'] > position['row'] and destination['col'] == position['col']:
            direction = 'down'
            possibleDirections.remove('down')
        elif destination['row'] < position['row'] and destination['col'] == position['col']:
            direction = 'up'
            possibleDirections.remove('up')
        elif destination['col'] > position['col'] and destination['row'] == position['row']:
            direction = 'right'
            possibleDirections.remove('right')
        elif destination['col'] < position['col'] and destination['row'] == position['row']:
            direction = 'left'
            possibleDirections.remove('left')
        elif includeHighways:
            highway = highwayInformation[n-numNonHighways]
            if highway[0]['col'] == position['col'] and highway[0]['row'] == position['row']:
                direction = highway[0]['direction']
            elif highway[1]['col'] == position['col'] and highway[1]['row'] == position['row']:
                direction = highway[1]['direction']
            possibleDirections.remove(direction)
        isHighway = destination['row'] != position['row'] and destination['col'] != position['col']
        if (isHighway and includeHighways) or (not isHighway):
            possibleMoves.append({"direction": direction, "destination": destination, "path": path})
    return sorted(possibleMoves, key=lambda x: x['direction'])

def findShadowRealm(board):
    for n, row in enumerate(board):
        for m, cell in enumerate(row):
            if cell == 'shadow realm':
                return {"row": n, "col": m}

def findShortestPathToFlamingo(board, paths, startPos, highwayInformation):
    if board[startPos['row']][startPos['col']] == 'flamingo':
        return []
    done = False
    allPathChains = []
    previouslySearched = [startPos]
    iterations = 0
    while not done:
        iterations += 1
        if len(allPathChains) == 0:
            possibleMoves = findPossibleMoves(paths, startPos, True, highwayInformation)
            for move in possibleMoves:
                if move['path']['start'] == startPos:
                    path = move['path']
                elif move['path']['end'] == startPos:
                    path = {"start": move['path']['end'], "end": move['path']['start'], "oneWay": move['path']['oneWay']}
                allPathChains.append([path])
                previouslySearched.append(path['end'])
                if board[path['end']['row']][path['end']['col']] == 'flamingo':
                    done = True
                    return [path]
        else:
            newPathChains = []
            for pathChain in allPathChains:
                position = pathChain[-1]['end']
                if board[position['row']][position['col']] != 'shadow realm':
                    possibleMoves = findPossibleMoves(paths, position, True, highwayInformation)
                    for move in possibleMoves:
                        if move['path']['start'] == position:
                            path = move['path']
                        elif move['path']['end'] == position:
                            path = {"start": move['path']['end'], "end": move['path']['start'], "oneWay": move['path']['oneWay']}
                        if path['end'] not in previouslySearched:
                            newPathChain = pathChain + [path]
                            newPathChains.append(newPathChain)
                            previouslySearched.append(path['end'])
                            if board[path['end']['row']][path['end']['col']] == 'flamingo':
                                done = True
                                return newPathChain
            if len(newPathChains) == 0:
                done = True
                return 'impossible'
            allPathChains = newPathChains

def isPossibleToGetEverywhere(board, paths, startPos, highwayInformation):
    previouslySearched = []
    currentlySearching = [startPos]
    nextSearching = ['something is in here']
    while len(nextSearching) > 0:
        nextSearching = []
        for space in currentlySearching:
            if board[space['row']][space['col']] != 'shadow realm':
                possibleMoves = findPossibleMoves(paths, space, True, highwayInformation)
                for move in possibleMoves:
                    destination = move['destination']
                    if destination not in previouslySearched and destination not in nextSearching and destination not in currentlySearching:
                        nextSearching.append(destination)
            if space not in previouslySearched:
                previouslySearched.append(space)
        currentlySearching = copy.deepcopy(nextSearching)
    numPossibleSpaces = len(previouslySearched)
    numSpaces = sum([sum([(0 if cell == None else 1) for cell in row]) for row in board])
    return numPossibleSpaces == numSpaces

def areThereAnyPurgatories(board, paths, highwayInformation):
    for n, row in enumerate(board):
        for m, cell in enumerate(row):
            space = {"row": n, "col": m}
            if cell != None:
                possibleMoves = findPossibleMoves(paths, space, True, highwayInformation)
                if len(possibleMoves) == 0:
                    return True
    return False

def askOptions(prompt, numOptions):
    global indent
    option = input(prompt)
    if option == '':
        option = '0'
    try:
        option = int(option)
        if option < 0:
            indent += 1
            print(f'{" "*indent}{ERROR}Invalid Answer! Must be a number from 0 to {numOptions}{CLEAR}')
            indent -= 1
            option = askOptions(prompt, numOptions)
        elif option > numOptions:
            indent += 1
            print(f'{" "*indent}{ERROR}Invalid Answer! Must be a number from 0 to {numOptions}{CLEAR}')
            indent -= 1
            option = askOptions(prompt, numOptions)
    except ValueError:
        indent += 1
        print(f'{" "*indent}{ERROR}Invalid Answer! Must be a number from 0 to {numOptions}{CLEAR}')
        indent -= 1
        option = askOptions(prompt, numOptions)
    return str(option)

def askForPlayer(prompt, includeSelf):
    global indent
    option = input(prompt)
    try:
        option = int(option)
        if option < 1:
            indent += 1
            print(f'{" "*indent}{ERROR}Invalid Answer! Must be a number from 1 to {NUM_PLAYERS}{CLEAR}')
            indent -= 1
            option = askForPlayer(prompt, includeSelf)
        elif option > NUM_PLAYERS:
            indent += 1
            print(f'{" "*indent}{ERROR}Invalid Answer! Must be a number from 1 to {NUM_PLAYERS}{CLEAR}')
            indent -= 1
            option = askForPlayer(prompt, includeSelf)
        if not includeSelf:
            if option == currentPlayer:
                indent += 1
                print(f'{" "*indent}{ERROR}Invalid Answer! You cannot pick yourself!{CLEAR}')
                indent -= 1
                option = askForPlayer(prompt, includeSelf)
    except ValueError:
        indent += 1
        print(f'{" "*indent}{ERROR}Invalid Answer! Must be a number from 1 to {NUM_PLAYERS}{CLEAR}')
        indent -= 1
        option = askForPlayer(prompt, includeSelf)
    return str(option)

def evaluateEntanglement():
    global indent
    if random.random() < 0.5:
        possibleSpaces = []
        for entanglement in quantumEntanglements:
            if playerPositions[currentPlayer] in entanglement:
                possibleSpaces.append(entanglement[1-entanglement.index(playerPositions[currentPlayer])])
        if len(possibleSpaces) >= 1:
            chosenSpace = random.choice(possibleSpaces)
            playerPositions[currentPlayer] = chosenSpace
            if playerQuantumNotifications[currentPlayer] >= 1:
                playerQuantumNotifications[currentPlayer] -= 1
                indent += 1
                print(f'{" "*indent}You have been {ENTANGLEMENT_SPACE}quantum teleported{CLEAR}!')
                indent -= 1
            
def evaluateSpaceType(spaceType):
    global indent
    global running
    global winner
    indent += 1
    print(f'{" "*indent}You landed on {grammatiseSpaceType(spaceType, punctuation=True)}')
    if spaceType == 'empty':
        indent += 1
        print(f'{" "*indent}Nothing Happens.')
        indent -= 1
    if spaceType == 'flamingo':
        indent += 1
        print(f'{" "*indent}You must play a {FLAMINGO_SPACE}flamingo game{CLEAR} to {GREEN}win the game{CLEAR}!')
        print(f'{" "*indent}{RED}If you lose{CLEAR}, you must return to the {HOME_SPACE}home{CLEAR} space.')
        time.sleep(1)
        print(f'{" "*indent}The {FLAMINGO_SPACE}flamingo game{CLEAR} you will play is:')
        if spinTheFlamingoWheel():
            print(f'{" "*indent}{GREEN}Congratulations! You Win!{CLEAR}')
            running = False
            winner = currentPlayer
        else:
            print(f'{" "*indent}{RED}You lost!{CLEAR} You must return to the {HOME_SPACE}home{CLEAR} space!')
            playerPositions[currentPlayer] = {"row": GRID_SIZE // 2, "col": GRID_SIZE // 2}
        indent -= 1
    if spaceType == 'home':
        indent += 1
        print(f'{" "*indent}You gain {YELLOW}1 gold{CLEAR}!')
        playerGolds[currentPlayer] += 1
        print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
        indent -= 1
    if spaceType == 'shadow realm':
        indent += 1
        print(f'{" "*indent}You are stuck here until you escape. Instead of moving, you will spin the {SHADOW_REALM_SPACE}Shadow Wheel{CLEAR}.')
        indent -= 1
    if spaceType == 'good':
        indent += 1
        print(f'{" "*indent}You get to spin the {GREEN}Good Wheel{CLEAR}!')
        spinTheGoodWheel()
        indent -= 1
        updateQuests('goodSpace', 1)
    if spaceType == 'bad':
        indent += 1
        print(f'{" "*indent}You get to spin the {RED}Bad Wheel{CLEAR}.')
        spinTheBadWheel()
        indent -= 1
        updateQuests('badSpace', 1)
    if spaceType == 'shop':
        indent += 1
        print(f'{" "*indent}You get to buy from the {SHOP_SPACE}shop{CLEAR}!')
        if playerGolds[currentPlayer] < min(itemPrices.values()):
            indent += 1
            print(f'{" "*indent}You don\'t have enough {YELLOW}gold{CLEAR} to buy anything! (You have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR})')
            indent -= 1
        else:
            goToTheShop()
        indent -= 1
    if spaceType == 'teleport':
        indent += 1
        print(f'{" "*indent}You get to choose a player to randomly {TELEPORT_SPACE}teleport{CLEAR}!')
        player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who will be randomly teleported: (1-{NUM_PLAYERS}){CLEAR} ', True))
        playerPositions[player] = selectRandomSpace(board)
        indent -= 1
    if spaceType == 'gambling':
        indent += 1
        if playerGolds[currentPlayer] > 0 or len(playerInventories[currentPlayer]) > 0:
            print(f'{" "*indent}You must play {ORANGE}Blackjack{CLEAR} with the computer (but up to {GREEN}{BLACKJACK_TARGET}{CLEAR} instead of {GREEN}21{CLEAR}).')
            playBlackjack()
        else:
            print(f'{" "*indent}Unfortunately, you do not have any {YELLOW}gold{CLEAR} or {CYAN}items{CLEAR} to gamble!')
        indent -= 1
    if spaceType == 'timewarp':
        indent += 1
        print(f'{" "*indent}You get to choose a player to be {TIMEWARP_SPACE}sent back in time{CLEAR} up to {GREEN}3 rounds{CLEAR}!')
        player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who will be sent back: (1-{NUM_PLAYERS}){CLEAR} ', True))
        targetTime = min(1+3*NUM_PLAYERS,len(prevPlayerPositions))
        playerPositions[player] = prevPlayerPositions[-targetTime][player]
        playerInventories[player] = prevPlayerInventories[-targetTime][player]
        playerGolds[player] = prevPlayerGolds[-targetTime][player]
        playerSpeeds[player] = prevPlayerSpeeds[-targetTime][player]
        playerProgress[player] = prevPlayerProgress[-targetTime][player]
        playerStealBonus[player] = prevPlayerStealBonus[-targetTime][player]
        playerInvestmentBonus[player] = prevPlayerInvestmentBonus[-targetTime][player]
        playerQuests[player] = prevPlayerQuests[-targetTime][player]
        playerWaitingForEvents[player] = prevPlayerWaitingForEvents[-targetTime][player]
        playerFrozens[player] = prevPlayerFrozens[-targetTime][player]
        playerQuantumNotifications[player] = prevPlayerQuantumNotifications[-targetTime][player]
        for _ in range(targetTime-1):
            for i in range(1, len(prevPlayerPositions)):
                prevPlayerPositions[(-1)*i][player] = copy.deepcopy(prevPlayerPositions[(-1)*(i+1)][player])
                prevPlayerInventories[(-1)*i][player] = copy.deepcopy(prevPlayerInventories[(-1)*(i+1)][player])
                prevPlayerGolds[(-1)*i][player] = copy.deepcopy(prevPlayerGolds[(-1)*(i+1)][player])
                prevPlayerSpeeds[(-1)*i][player] = copy.deepcopy(prevPlayerSpeeds[(-1)*(i+1)][player])
                prevPlayerProgress[(-1)*i][player] = copy.deepcopy(prevPlayerProgress[(-1)*(i+1)][player])
                prevPlayerStealBonus[(-1)*i][player] = copy.deepcopy(prevPlayerStealBonus[(-1)*(i+1)][player])
                prevPlayerInvestmentBonus[(-1)*i][player] = copy.deepcopy(prevPlayerInvestmentBonus[(-1)*(i+1)][player])
                prevPlayerQuests[(-1)*i][player] = copy.deepcopy(prevPlayerQuests[(-1)*(i+1)][player])
                prevPlayerWaitingForEvents[(-1)*i][player] = copy.deepcopy(prevPlayerWaitingForEvents[(-1)*(i+1)][player])
                prevPlayerFrozens[(-1)*i][player] = copy.deepcopy(prevPlayerFrozens[(-1)*(i+1)][player])
                prevPlayerQuantumNotifications[(-1)*i][player] = copy.deepcopy(prevPlayerQuantumNotifications[(-1)*(i+1)][player])
        indent -= 1
    if spaceType == 'papas wingeria':
        visitWingeria()
    if spaceType == 'gym':
        visitGym()
    if spaceType == 'quest':
        indent += 1
        print(f'{" "*indent}You must spin the {QUEST_SPACE}quest wheel{CLEAR} to recieve a random {QUEST_SPACE}quest{CLEAR}!')
        spinTheQuestWheel()
        indent -= 1
    if spaceType == 'entanglement':
        indent += 1
        print(f'{" "*indent}2 random spaces have now become {ENTANGLEMENT_SPACE}quantum-entangled{CLEAR}!')
        print(f'{" "*indent}If you are on a space that has been {ENTANGLEMENT_SPACE}quantum-entangled{CLEAR}, there is a {RED}50% chance{CLEAR} you will be {TELEPORT_SPACE}teleported{CLEAR} to the other one.')
        firstSpace = selectRandomSpace(board)
        secondSpace = firstSpace
        while firstSpace == secondSpace:
            secondSpace = selectRandomSpace(board)
        quantumEntanglements.append([firstSpace, secondSpace])
        generateImage(board, paths, quantumEntanglements)
        if playerGolds[currentPlayer] >= 5:
            print(f'{" "*indent}Would you like to pay {YELLOW}5 gold{CLEAR} to be {GREEN}notified{CLEAR} when you next get {ENTANGLEMENT_SPACE}quantum teleported{CLEAR}?')
            indent += 1
            print(f'{" "*indent}0: No')
            print(f'{" "*indent}1: Yes')
            indent -= 1
            choice = askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', 1)
            if choice == '1':
                indent += 1
                playerQuantumNotifications[currentPlayer] += 1
                playerGolds[currentPlayer] -= 5
                print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
                indent -= 1
        indent -= 1
    indent -= 1

def evaluateDecorators():
    global indent
    decoratorsToRemove = []
    goblinsToAdd = []
    for n, decorator in enumerate(decorators[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']]):
        if decorator['type'] == 'trap' and decorator['placedBy'] != currentPlayer:
            indent += 1
            print(f'{" "*indent}Unfortunately, you landed on {RED}Player {decorator["placedBy"]}\'s trap{CLEAR}!')
            indent += 1
            print(f'{" "*indent}You must give them {YELLOW}{decorator["reward"]} gold{CLEAR}.')
            playerGolds[currentPlayer] -= decorator["reward"]
            playerGolds[decorator['placedBy']] += decorator["reward"]
            print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR} and {RED}Player {decorator["placedBy"]}{CLEAR} now has {YELLOW}{playerGolds[decorator["placedBy"]]} gold{CLEAR}.')
            decoratorsToRemove.append(n)
            indent -= 2
        if decorator['type'] == 'gold':
            indent += 1
            print(f'{" "*indent}There is {YELLOW}{decorator["reward"]} gold{CLEAR} on this space!')
            indent += 1
            print(f'{" "*indent}You gain {YELLOW}{decorator["reward"]} gold{CLEAR}!')
            playerGolds[currentPlayer] += decorator["reward"]
            print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
            decoratorsToRemove.append(n)
            indent -= 2
        if decorator['type'] == 'goblin' and decorator['placedBy'] != currentPlayer:
            indent += 1
            print(f'{" "*indent}Unfortunately, you have ran into {RED}Player {decorator["placedBy"]}\'s goblin{CLEAR}!')
            indent += 1
            print(f'{" "*indent}It steals {YELLOW}{decorator["reward"]} gold{CLEAR} for {RED}Player {decorator["placedBy"]}{CLEAR} and runs away {GREEN}1 space{CLEAR}.')
            playerGolds[currentPlayer] -= decorator["reward"]
            playerGolds[decorator['placedBy']] += decorator["reward"]
            print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR} and {RED}Player {decorator["placedBy"]}{CLEAR} now has {YELLOW}{playerGolds[decorator["placedBy"]]} gold{CLEAR}.')
            possibleMoves = findPossibleMoves(paths, {"row": playerPositions[currentPlayer]['row'], "col": playerPositions[currentPlayer]['col']}, True, highwayInformation)
            chosenDestination = random.choice(possibleMoves)['destination']
            decoratorsToRemove.append(n)
            print(f'{" "*indent}{RED}Player {decorator["placedBy"]}\'s goblin{CLEAR} has moved!')
            if board[chosenDestination['row']][chosenDestination['col']] == 'shadow realm':
                indent += 1
                print(f'{" "*indent}The goblin {RED}got lost{CLEAR} in the {SHADOW_REALM_SPACE}shadow realm{CLEAR} and died.')
                indent -= 1
            else:
                goblinsToAdd.append((chosenDestination['row'], chosenDestination['col'], decorator))
            indent -= 2
        if decorator['type'] == 'flamingo':
            indent += 1
            print(f'{" "*indent}{RED}Player {decorator["placedBy"]}\'s {FLAMINGO_SPACE}flamingo{CLEAR} is on this space!')
            indent -= 1
        time.sleep(0.5)
    for decorator in sorted(decoratorsToRemove, reverse=True):
        decorators[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']].pop(decorator)
    for goblin in goblinsToAdd:
        decorators[goblin[0]][goblin[1]].append(goblin[2])

def evaluatePathDecorators():
    global indent
    global allowedToMove
    chosenPath = possibleMoves[int(choice)-1]['path']
    for n, path in enumerate(paths):
        if path == chosenPath:
            for decorator in pathDecorators[n]:
                if allowedToMove:
                    if decorator['type'] == 'padlock':
                        indent += 1
                        allowedToMove = False
                        print(f'{" "*indent}There is a {CYAN}padlock{CLEAR} on this path! You have 3 tries to guess the code.')
                        attempts = 3
                        done = False
                        while not done:
                            code = int(askOptions(f'{" "*indent}{TURQUOISE}Enter the code for this {CYAN}padlock{TURQUOISE} ({getColourFromFraction(attempts/3)}{attempts} attempt{"s" if attempts != 1 else ""}{TURQUOISE} remaining): (0-9999){CLEAR} ', 9999))
                            if code == decorator['code']:
                                indent += 1
                                print(f'{" "*indent}{GREEN}Successfuly entered code!{CLEAR}')
                                done = True
                                allowedToMove = True
                                indent -= 1
                            else:
                                indent += 1
                                print(f'{" "*indent}{RED}Incorrect code!{CLEAR}')
                                attempts -= 1
                                if attempts == 0:
                                    print(f'{" "*indent}Unfortunately, you have {RED}ran out of attempts{CLEAR} and cannot move this turn.')
                                    done = True
                                indent -= 1
                        indent -= 1

def spinWheelVisually(options):
    print('')
    for _ in range(20):
        print(f'\x1B[A\x1B[2K{random.choice(options)}')
        time.sleep(0.02)
    for _ in range(5):
        print(f'\x1B[A\x1B[2K{random.choice(options)}')
        time.sleep(0.05)
    for _ in range(2):
        print(f'\x1B[A\x1B[2K{random.choice(options)}')
        time.sleep(0.1)
    result = random.choice(options)
    return result

def spinTheBadWheel():
    global board
    global indent
    indent += 1
    options = [
        f'{" "*indent}You have been sent to the {SHADOW_REALM_SPACE}Shadow Realm{CLEAR}.',
        f'{" "*indent}You will be {TELEPORT_SPACE}teleported{CLEAR} to a random space.',
        f'{" "*indent}You {TELEPORT_SPACE}swap places{CLEAR} with a random player.',
        f'{" "*indent}You must give away {YELLOW}all gold{CLEAR}. {YELLOW}({playerGolds[currentPlayer]}){CLEAR}',
        f'{" "*indent}You must return to the {HOME_SPACE}Home{CLEAR} space.',
        f'{" "*indent}You must give away {YELLOW}3 gold{CLEAR}.',
        f'{" "*indent}You must give away {CYAN}an item{CLEAR}.',
        f'{" "*indent}You must spin the {RED}Bad Wheel{CLEAR} twice more.',
        f'{" "*indent}You can now spin {GREEN}Good Wheel{CLEAR}!',
        f'{" "*indent}One {RED}random change{CLEAR} will be made to the board.',
        f'{" "*indent}The sign of your {YELLOW}gold{CLEAR} has swapped!'
    ]
    result = spinWheelVisually(options)
    print(f'\x1B[A\x1B[2K{result}')
    time.sleep(1)
    if result == f'{" "*indent}You have been sent to the {SHADOW_REALM_SPACE}Shadow Realm{CLEAR}.':
        playerPositions[currentPlayer] = findShadowRealm(board)
    if result == f'{" "*indent}You will be {TELEPORT_SPACE}teleported{CLEAR} to a random space.':
        playerPositions[currentPlayer] = selectRandomSpace(board)
    if result == f'{" "*indent}You {TELEPORT_SPACE}swap places{CLEAR} with a random player.':
        players = list(range(1,NUM_PLAYERS+1))
        players.remove(currentPlayer)
        player = random.choice(players)
        temp = playerPositions[player]
        playerPositions[player] = playerPositions[currentPlayer]
        playerPositions[currentPlayer] = temp
    if result == f'{" "*indent}You must give away {YELLOW}all gold{CLEAR}. {YELLOW}({playerGolds[currentPlayer]}){CLEAR}':
        indent += 1
        player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who you will give your {YELLOW}gold{TURQUOISE} to: (1-{NUM_PLAYERS}){CLEAR} ', False))
        playerGolds[player] += playerGolds[currentPlayer]
        playerGolds[currentPlayer] = 0
        print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR} and {RED}Player {player}{CLEAR} now has {YELLOW}{playerGolds[player]} gold{CLEAR}.')
        indent -= 1
    if result == f'{" "*indent}You must return to the {HOME_SPACE}Home{CLEAR} space.':
        playerPositions[currentPlayer] = {"row": GRID_SIZE // 2, "col": GRID_SIZE // 2}
    if result == f'{" "*indent}You must give away {YELLOW}3 gold{CLEAR}.':
        indent += 1
        player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who you will give {YELLOW}3 gold{TURQUOISE} to: (1-{NUM_PLAYERS}){CLEAR} ', False))
        playerGolds[player] += 3
        playerGolds[currentPlayer] -= 3
        print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR} and {RED}Player {player}{CLEAR} now has {YELLOW}{playerGolds[player]} gold{CLEAR}.')
        indent -= 1
    if result == f'{" "*indent}You must give away {CYAN}an item{CLEAR}.':
        indent += 1
        if len(playerInventories[currentPlayer]) == 0:
            print(f'{" "*indent}Luckily, {GREEN}You don\'t have any items{CLEAR}!')
        else:
            print(f'{" "*indent}Which {CYAN}item{CLEAR} will you give away?')
            printItemList(playerInventories[currentPlayer])
            valid = False
            while not valid:
                choice = askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', len(playerInventories[currentPlayer]))
                if choice != '0':
                    valid = True
            item = playerInventories[currentPlayer][int(choice)-1]
            playerInventories[currentPlayer].remove(item)
            if ';' in item:
                itemName = item.split(';')[0]
            else:
                itemName = item
            player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who you will give the {CYAN}{itemName.title()}{TURQUOISE} to: (1-{NUM_PLAYERS}){CLEAR} ', False))
            playerInventories[player].append(item)
        indent -= 1
    if result == f'{" "*indent}You must spin the {RED}Bad Wheel{CLEAR} twice more.':
        for _ in range(2):
            spinTheBadWheel()
    if result == f'{" "*indent}You can now spin {GREEN}Good Wheel{CLEAR}!':
        spinTheGoodWheel()
    if result == f'{" "*indent}One {RED}random change{CLEAR} will be made to the board.':
        changeType = random.choice(['goodToBad', 'badToGood', 'addSpecialSpace', 'addShop', 'addSpeedSpace'])
        if changeType == 'goodToBad':
            board = fillSpaces(board, 'bad', 1, 'good')
        if changeType == 'badToGood':
            board = fillSpaces(board, 'good', 1, 'bad')
        if changeType == 'addSpecialSpace':
            board = fillSpaces(board, random.choice(['teleport', 'gambling', 'timewarp']), 1, 'empty')
        if changeType == 'addShop':
            board = fillSpaces(board, 'shop', 1, 'empty')
        if changeType == 'addSpeedSpace':
            board = fillSpaces(board, random.choice(['papas wingeria', 'gym']), 1, 'empty')
        generateImage(board, paths, quantumEntanglements)
    if result == f'{" "*indent}The sign of your {YELLOW}gold{CLEAR} has swapped!':
        playerGolds[currentPlayer] *= -1
        print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
    indent -= 1
                    
def spinTheGoodWheel():
    global indent
    indent += 1
    options = [
        f'{" "*indent}You can {CYAN}send a player{CLEAR} to the {SHADOW_REALM_SPACE}Shadow Realm{CLEAR}!',
        f'{" "*indent}You gain {YELLOW}3 gold{CLEAR}!',
        f'{" "*indent}You gain {YELLOW}2 gold{CLEAR}!',
        f'{" "*indent}You must spin the {RED}Bad Wheel{CLEAR}.',
        f'{" "*indent}You have {YELLOW}doubled{CLEAR} your gold!',
        f'{" "*indent}You gain {YELLOW}5 gold{CLEAR}',
        f'{" "*indent}You gain {CYAN}a compass{CLEAR}',
        f'{" "*indent}You can visit the {SHOP_SPACE}shop{CLEAR}!',
        f'{" "*indent}You get information about the {ORANGE}position{CLEAR} of the {FLAMINGO_SPACE}flamingo space{CLEAR}!',
        f'{" "*indent}You must either {GAMBLING_SPACE}gamble{CLEAR}, or make {RED}another player{CLEAR} {GAMBLING_SPACE}gamble{CLEAR}.',
        f'{" "*indent}You get to spin the {QUEST_SPACE}quest wheel{CLEAR}!',
    ]
    result = spinWheelVisually(options)
    print(f'\x1B[A\x1B[2K{result}')
    time.sleep(1)
    if result == f'{" "*indent}You can {CYAN}send a player{CLEAR} to the {SHADOW_REALM_SPACE}Shadow Realm{CLEAR}!':
        indent += 1
        player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who will be sent to the {SHADOW_REALM_SPACE}Shadow Realm{TURQUOISE}: (1-{NUM_PLAYERS}){CLEAR} ', True))
        playerPositions[player] = findShadowRealm(board)
        indent -= 1
    if result == f'{" "*indent}You gain {YELLOW}3 gold{CLEAR}!':
        playerGolds[currentPlayer] += 3
        print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
    if result == f'{" "*indent}You gain {YELLOW}2 gold{CLEAR}!':
        playerGolds[currentPlayer] += 2
        print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
    if result == f'{" "*indent}You must spin the {RED}Bad Wheel{CLEAR}.':
        spinTheBadWheel()
    if result == f'{" "*indent}You have {YELLOW}doubled{CLEAR} your gold!':
        playerGolds[currentPlayer] *= 2
        print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
    if result == f'{" "*indent}You gain {YELLOW}5 gold{CLEAR}':
        playerGolds[currentPlayer] += 5
        print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
    if result == f'{" "*indent}You gain {CYAN}a compass{CLEAR}':
        playerInventories[currentPlayer].append('compass')
    if result == f'{" "*indent}You can visit the {SHOP_SPACE}shop{CLEAR}!':
        if playerGolds[currentPlayer] < min(itemPrices.values()):
            indent += 1
            print(f'{" "*indent}Unfortunately, You don\'t have enough {YELLOW}gold{CLEAR} to buy anything! (You have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR})')
            indent -= 1
        else:
            goToTheShop()
    if result == f'{" "*indent}You get information about the {ORANGE}position{CLEAR} of the {FLAMINGO_SPACE}flamingo space{CLEAR}!':
        indent += 1
        for n, row in enumerate(board):
            for m, cell in enumerate(row):
                if cell == 'flamingo':
                    flamingoPos = (n+1, m+1)
        rowOrCol = random.choice(['row', 'col'])
        if rowOrCol == 'row':
            choices = [x for x in list(range(1,GRID_SIZE+1)) if x != flamingoPos[0]]
            print(f'{" "*indent}The {FLAMINGO_SPACE}flamingo space{CLEAR} is {RED}not{CLEAR} in {ORANGE}row {random.choice(choices)}{CLEAR}.')
        else:
            choices = [x for x in list(range(1,GRID_SIZE+1)) if x != flamingoPos[1]]
            print(f'{" "*indent}The {FLAMINGO_SPACE}flamingo space{CLEAR} is {RED}not{CLEAR} in {ORANGE}column {random.choice(choices)}{CLEAR}.')
        indent -= 1
    if result == f'{" "*indent}You must either {GAMBLING_SPACE}gamble{CLEAR}, or make {RED}another player{CLEAR} {GAMBLING_SPACE}gamble{CLEAR}.':
        indent += 1
        print(f'{" "*indent}What would you like to do?')
        indent += 1
        print(f'{" "*indent}0: Gamble (You have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR})')
        print(f'{" "*indent}1: Make another player gamble half of their {YELLOW}gold{CLEAR}')
        indent -= 1
        choice = askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', 1)
        if choice == '0':
            if playerGolds[currentPlayer] > 0 or len(playerInventories[currentPlayer]) > 0:
                playBlackjack()
            else:
                indent += 1
                print(f'{" "*indent}Unfortunately, you do not have any {YELLOW}gold{CLEAR} or {CYAN}items{CLEAR} to gamble!')
                indent -= 1
        if choice == '1':
            indent += 1
            player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who will {GAMBLING_SPACE}gamble{TURQUOISE} at the start of their next turn: (1-{NUM_PLAYERS}){CLEAR} ', False))
            playerWaitingForEvents[player].append('gamble')
            indent -= 1
        indent -= 1
    if result == f'{" "*indent}You get to spin the {QUEST_SPACE}quest wheel{CLEAR}!':
        spinTheQuestWheel()
    indent -= 1

def spinTheShadowWheel():
    global indent
    indent += 1
    options = [
        f'{" "*indent}You must {CYAN}Invite a Friend{CLEAR} to the {SHADOW_REALM_SPACE}Shadow Realm{CLEAR}!',
        f'{" "*indent}You can now spin the {GREEN}Good Wheel{CLEAR}!',
        f'{" "*indent}You must return to the {HOME_SPACE}Home{CLEAR} space.',
        f'{" "*indent}You must return to the {HOME_SPACE}Home{CLEAR} space.',
        f'{" "*indent}You must return to the {HOME_SPACE}Home{CLEAR} space.',
        f'{" "*indent}Nothing happens.',
        f'{" "*indent}All other players gain {YELLOW}2 gold{CLEAR}',
        f'{" "*indent}You lose {YELLOW}1 gold{CLEAR}',
        f'{" "*indent}You must spin the {RED}Bad Wheel{CLEAR}.'
    ]
    result = spinWheelVisually(options)
    print(f'\x1B[A\x1B[2K{result}')
    time.sleep(1)
    if result == f'{" "*indent}You must {CYAN}Invite a Friend{CLEAR} to the {SHADOW_REALM_SPACE}Shadow Realm{CLEAR}!':
        indent += 1
        player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who will be sent to the {SHADOW_REALM_SPACE}Shadow Realm{TURQUOISE}: (1-{NUM_PLAYERS}){CLEAR} ', False))
        playerPositions[player] = findShadowRealm(board)
        indent -= 1
    if result == f'{" "*indent}You can now spin the {GREEN}Good Wheel{CLEAR}!':
        spinTheGoodWheel()
    if result == f'{" "*indent}You must return to the {HOME_SPACE}Home{CLEAR} space.':
        playerPositions[currentPlayer] = {"row": GRID_SIZE // 2, "col": GRID_SIZE // 2}
    if result == f'{" "*indent}All other players gain {YELLOW}2 gold{CLEAR}':
        indent += 1
        for player in range(1, NUM_PLAYERS+1):
            if player != currentPlayer:
                playerGolds[player] += 2
                print(f'{" "*indent}{RED}Player {player}{CLEAR} now has {YELLOW}{playerGolds[player]} gold{CLEAR}.')
        indent -= 1
    if result == f'{" "*indent}You lose {YELLOW}1 gold{CLEAR}':
        playerGolds[currentPlayer] -= 1
        print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
    if result == f'{" "*indent}You must spin the {RED}Bad Wheel{CLEAR}.':
        spinTheBadWheel()
    indent -= 1

def questTextFromDict(quest, progress):
    if quest['type'] == 'goodSpace':
        output =  f'You must land on the {GOOD_SPACE}good space{CLEAR} {QUEST_SPACE}{quest["requirement"]}{CLEAR} times.'
    if quest['type'] == 'badSpace':
        output = f'You must land on the {BAD_SPACE}bad space{CLEAR} {QUEST_SPACE}{quest["requirement"]}{CLEAR} times.'
    if quest['type'] == 'shadowRealm':
        output = f'You must spend {QUEST_SPACE}{quest["requirement"]}{CLEAR} turns in the {SHADOW_REALM_SPACE}shadow realm{CLEAR}.'
    if quest['type'] == 'workout':
        output = f'You must {GYM_SPACE}workout{CLEAR} for {QUEST_SPACE}{quest["requirement"]}{CLEAR} hours at the {GYM_SPACE}gym{CLEAR}.'
    if quest['type'] == 'eatChicken':
        output = f'You must eat {QUEST_SPACE}{quest["requirement"]}{CLEAR} {PAPAS_WINGERIA_SPACE}chicken wings{CLEAR} at {PAPAS_WINGERIA_SPACE}papa\'s wingeria{CLEAR}.'
    if quest['type'] == 'stabPeople':
        output = f'You must {RED}stab{CLEAR} {QUEST_SPACE}{quest["requirement"]}{CLEAR} people using the {CYAN}knife{CLEAR} item.'
    if quest['type'] == 'gamble':
        output = f'You must win back {QUEST_SPACE}{quest["requirement"]}{CLEAR} {YELLOW}gold{CLEAR} by playing {GAMBLING_SPACE}blackjack{CLEAR}.'
    if quest['type'] == 'spendMoney':
        output = f'You must spend {QUEST_SPACE}{quest["requirement"]}{CLEAR} {YELLOW}gold{CLEAR} at the {SHOP_SPACE}shop{CLEAR}.'
    if quest['type'] == 'shootPeople':
        output = f'You must shoot {QUEST_SPACE}{quest["requirement"]}{CLEAR} people with {RED}1 bullet{CLEAR} using the {CYAN}gun{CLEAR} item.'
    output += f' - {YELLOW}{quest["reward"]} gold{CLEAR}'
    if progress:
        output += f' {getColourFromFraction(quest["progress"]/quest["requirement"])}({quest["progress"]}/{quest["requirement"]}){CLEAR}'
        output += f' {GRAY}[{getColourFromFraction((quest["timeLeft"]-1)/20)}{quest["timeLeft"]}{GRAY} turn{"" if quest["timeLeft"] == 1 else "s"} remaining]{CLEAR}'
    return output

def spinTheQuestWheel():
    global indent
    indent += 1
    actualOptions = [
        {"type": 'goodSpace', "requirement": (numGoodSpaces := random.randint(3, 5)), "reward": numGoodSpaces*2, "progress": 0, "timeLeft": numGoodSpaces*5},
        {"type": 'badSpace', "requirement": (numBadSpaces := random.randint(3, 5)), "reward": numBadSpaces*4, "progress": 0, "timeLeft": numBadSpaces*5},
        {"type": 'shadowRealm', "requirement": (timeInShadowRealm := random.randint(6,10)), "reward": timeInShadowRealm*2, "progress": 0, "timeLeft": timeInShadowRealm*3},
        {"type": 'workout', "requirement": (workoutHours := random.randint(40,70)), "reward": workoutHours//4, "progress": 0, "timeLeft": int(workoutHours//2.5)},
        {"type": 'eatChicken', "requirement": (chickenToEat := random.randint(40,70)), "reward": int(chickenToEat//3.5), "progress": 0, "timeLeft": int(workoutHours//2.5)},
        {"type": 'stabPeople', "requirement": (peopleToStab := random.randint(2, 4)), "reward": peopleToStab*5, "progress": 0, "timeLeft": peopleToStab*6},
        {"type": 'gamble', "requirement": (gambleWinnings := random.randint(8,16)), "reward": gambleWinnings, "progress": 0, "timeLeft": gambleWinnings*2},
        {"type": 'spendMoney', "requirement": (spendMoney := random.randint(7,15)), "reward": int((spendMoney*1.25)//1), "progress": 0, "timeLeft": int((spendMoney*1.5)//1)},
        {"type": 'shootPeople', "requirement": (peopleToShoot := random.randint(2, min(NUM_PLAYERS, 5))), "reward": peopleToShoot*4, "progress": 0, "timeLeft": 15}
    ]
    options = [f'{" "*indent}{questTextFromDict(option, progress=False)}' for option in actualOptions]
    spinWheelVisually(options)
    result = random.choice(actualOptions)
    print(f'\x1B[A\x1B[2K{" "*indent}{questTextFromDict(result, progress=False)}')
    time.sleep(0.75)
    playerQuests[currentPlayer].append(result)
    indent -= 1

def updateQuests(questType, qtyIncrease):
    global indent
    questsToRemove = []
    for n, quest in enumerate(playerQuests[currentPlayer]):
        if quest['type'] == questType:
            indent += 1
            quest['progress'] += qtyIncrease
            print(f'{" "*indent}{GRAY}(You have worked towards the quest: {CLEAR}{questTextFromDict(quest, progress=True)}{GRAY}){CLEAR}')
            if quest['progress'] >= quest['requirement']:
                indent += 1
                print(f'{" "*indent}{GREEN}Congratulations!{CLEAR} You have completed this {QUEST_SPACE}quest{CLEAR}!')
                questsToRemove.append(n)
                print(f'{" "*indent}You gain {YELLOW}{quest["reward"]} gold{CLEAR}!')
                playerGolds[currentPlayer] += quest['reward']
                print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
                indent -= 1
            else:
                if quest['type'] == 'shootPeople':
                    quest['progress'] = 0
            indent -= 1
    for quest in sorted(questsToRemove, reverse=True):
        playerQuests[currentPlayer].pop(quest)

def reduceTimeOnQuests():
    global indent
    questsToRemove = []
    for n, quest in enumerate(playerQuests[currentPlayer]):
        quest['timeLeft'] -= 1
        if quest['timeLeft'] == 0:
            indent += 1
            print(f'{" "*indent}{RED}Unfortunately,{CLEAR} you have ran out of time to complete the quest: {questTextFromDict(quest, progress=False)}')
            indent -= 1
            questsToRemove.append(n)
    for quest in sorted(questsToRemove, reverse=True):
        playerQuests[currentPlayer].pop(quest)

def spinTheFlamingoWheel():
    global indent
    indent += 1
    options = [
        f'{" "*indent}The {FLAMINGO_SPACE}Number Game{CLEAR}',
        f'{" "*indent}The {FLAMINGO_SPACE}Board Quiz{CLEAR}',
        f'{" "*indent}The {FLAMINGO_SPACE}Logic Game{CLEAR}',
        f'{" "*indent}The {FLAMINGO_SPACE}Date Quiz{CLEAR}'
    ]
    result = spinWheelVisually(options)
    print(f'\x1B[A\x1B[2K{result}')
    time.sleep(1)
    if result == f'{" "*indent}The {FLAMINGO_SPACE}Number Game{CLEAR}':
        unit = random.randint(3,9)
        limit = random.randint(50,200)
        print(f'{" "*indent}You must count to {GREEN}{limit}{CLEAR} {RED}excluding numbers{CLEAR} that follow these rules:\n{" "*(indent+1)}{RED}Cannot{CLEAR} be a multiple of {GREEN}{unit}{CLEAR}.\n{" "*(indent+1)}{RED}Cannot{CLEAR} contain the number {GREEN}{unit}{CLEAR}.\n{" "*(indent+1)}{RED}Cannot{CLEAR} have {GREEN}{unit}{CLEAR} digits.\n{" "*(indent+1)}Digits {RED}cannot{CLEAR} sum to {GREEN}{unit}{CLEAR}.\n{" "*(indent+1)}{RED}Cannot{CLEAR} have {GREEN}{unit}{CLEAR} letters. {GRAY}(in english, excluding spaces and hyphens){CLEAR}\n{" "*(indent+1)}{RED}Cannot{CLEAR} have {GREEN}{unit}{CLEAR} syllables. {GRAY}(in english){CLEAR}\n{" "*indent}Start at {GREEN}1{CLEAR}, unless it breaks some rules.')
        result = playNumberGame(unit, limit)
    if result == f'{" "*indent}The {FLAMINGO_SPACE}Board Quiz{CLEAR}':
        questions = random.randint(5,10)
        print(f'{" "*indent}You must answer {GREEN}{questions}{CLEAR} questions about the board in {RED}increasing difficulty{CLEAR}.')
        result = playBoardQuiz(questions)
    if result == f'{" "*indent}The {FLAMINGO_SPACE}Logic Game{CLEAR}':
        print(f'{" "*indent}You must simplify {GREEN}5{CLEAR} logic expressions in {RED}increasing difficulty{CLEAR}.')
        result = playLogicGame(5)
    if result == f'{" "*indent}The {FLAMINGO_SPACE}Date Quiz{CLEAR}':
        print(f'{" "*indent}You must identify the {ORANGE}day of the week{CLEAR} of {GREEN}5{CLEAR} dates in {RED}increasing difficulty{CLEAR}.')
        result = playDateQuiz()
    indent -= 1
    return result

def printShopList():
    global itemRewards
    global itemDescriptions
    global indent
    indent += 1
    options = 0
    for item in itemDescriptions.keys():
        actualItemRewards = copy.deepcopy(itemRewards)
        if item in itemRewards.keys():
            itemRewards[item] += playerStealBonus[currentPlayer]
            itemDescriptions = redefineItemDescriptions()
        options += 1
        if str(options) in itemSectionRanges.keys():
            indent -= 1
            print(f'{" "*indent}{GREEN}{"-"*5}{itemSectionRanges[str(options)].upper()}{"-"*5}{CLEAR}')
            indent += 1
        if itemPrices[item] <= playerGolds[currentPlayer]:
            print(f'{" "*indent}{options}: {CYAN}{item.title()}{CLEAR} - {YELLOW}{itemPrices[item]} gold{CLEAR} - {itemDescriptions[item]}')
        else:
            print(f'{" "*indent}{GRAY}{options}: {item.title()} - {itemPrices[item]} gold{CLEAR} - {itemDescriptions[item]}')
        itemRewards = copy.deepcopy(actualItemRewards)
        itemDescriptions = redefineItemDescriptions()
    indent -= 1
    print(f'{" "*indent}{GREEN}{"-"*15}{CLEAR}')

def goToTheShop(portable=False):
    global itemDescriptions
    global numTimeMachines
    global indent
    indent += 1
    tab = 0
    for _ in range(SHOP_PURCHACE_LIMIT):
        if playerGolds[currentPlayer] < min(itemPrices.values()):
            break
        print(f'{" "*indent}What would you like to buy?')
        printShopList()
        print(f'{" "*indent}You have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
        options = len(itemDescriptions.keys())
        valid = False
        while not valid:
            choice = askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', options)
            if choice == '0':
                valid = True
            else:
                item = list(itemDescriptions.keys())[int(choice)-1]
                price = itemPrices[item]
                if price > playerGolds[currentPlayer]:
                    indent += 1
                    print(f'{" "*indent}{RED}You do not have enough gold! Please select a different item.{CLEAR}')
                    indent -= 1
                elif portable == True and item == 'portable shop':
                    indent += 1
                    print(f'{" "*indent}{RED}You cannot buy a portable shop from a portable shop! Please select a different item.{CLEAR}')
                    indent -= 1
                else:
                    valid = True
        if choice == '0':
            break
        else:
            tab += price
            playerGolds[currentPlayer] -= price
            if item in itemRewards.keys():
                playerInventories[currentPlayer].append(f'{item};{itemRewards[item]+playerStealBonus[currentPlayer]}')
            elif item == 'time machine':
                numTimeMachines += 1
                playerInventories[currentPlayer].append(f'{item};{numTimeMachines}')
            else:
                playerInventories[currentPlayer].append(item)
            if random.random() < CHANCE_OF_SUPER_INFLATION:
                itemPrices[item] *= 2
                if item in itemRewards.keys():
                    itemRewards[item] *= 2
                    itemDescriptions = redefineItemDescriptions()
            elif random.random() < CHANCE_OF_INFLATION:
                itemPrices[item] += 1
                if item in itemRewards.keys():
                    itemRewards[item] += 1
                    itemDescriptions = redefineItemDescriptions()
    if tab > 0:
        updateQuests('spendMoney', tab)
    indent -= 1

def printItemList(itemList):
    global itemRewards
    global itemDescriptions
    global indent
    indent += 1
    options = 0
    for item in itemList:
        actualItemRewards = copy.deepcopy(itemRewards)
        if ';' in item:
            if 'time machine' not in item:
                split = item.split(';')
                item = split[0]
                reward = int(split[1])
                itemRewards[item] = reward
                itemDescriptions = redefineItemDescriptions()
            else:
                split = item.split(';')
                item = split[0]
        options += 1
        print(f'{" "*indent}{options}: {CYAN}{item.title()}{CLEAR} - {itemDescriptions[item]}')
        itemRewards = copy.deepcopy(actualItemRewards)
        itemDescriptions = redefineItemDescriptions()
    indent -= 1

def useItem():
    global indent
    global playerPositions
    global playerInventories
    global playerGolds
    global playerSpeeds
    global playerProgress
    global playerStealBonus
    global playerInvestmentBonus
    global playerQuests
    global playerWaitingForEvents
    global playerFrozens
    global playerQuantumNotifications
    global itemPrices
    global itemRewards
    global itemDescriptions
    global decorators
    global pathDecorators
    global board
    global quantumEntanglements
    done = False
    indent += 1
    itemsUsed = []
    while not done:
        if len(playerInventories[currentPlayer]) == 0:
            done = True
        else:
            print(f'{" "*indent}Would you like to use an {CYAN}item{CLEAR}?')
            indent += 1
            print(f'{" "*indent}0: No')
            print(f'{" "*indent}1: Yes')
            indent -= 1
            choice = askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', 1)
            if choice == '0':
                done = True
            else:
                indent += 1
                print(f'{" "*indent}Which {CYAN}item{CLEAR} would you like to use?')
                options = 0
                indent += 1
                print(f'{" "*indent}{options}: Nothing')
                indent -= 1
                printItemList(playerInventories[currentPlayer])
                choice = askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', len(playerInventories[currentPlayer]))
                if int(choice) != 0:
                    inventoryBackup = copy.deepcopy(playerInventories[currentPlayer])
                    item = playerInventories[currentPlayer].pop(int(choice)-1)
                    if ';' in item:
                        split = item.split(';')
                        item = split[0]
                        reward = int(split[1])
                    if item in itemsUsed:
                        indent += 1
                        print(f'{" "*indent}{RED}You have already used this item!{CLEAR} Try again at the next opportunity.')
                        playerInventories[currentPlayer] = inventoryBackup
                        indent -= 1
                    else:
                        itemsUsed.append(item)
                        #help i'm lost
                        if item == 'compass':
                            indent += 1
                            if board[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']] == 'shadow realm':
                                print(f'{" "*indent}The compass is {RED}useless{CLEAR} in the {SHADOW_REALM_SPACE}shadow realm{CLEAR}. No information was given.')
                            else:
                                possibleMoves = findPossibleMoves(paths, playerPositions[currentPlayer], True, highwayInformation)
                                print(f'{" "*indent}Here is all of the information about the {ORANGE}Adjacent Spaces{CLEAR}:')
                                indent += 1
                                message = f'You are currently on {grammatiseSpaceType(board[playerPositions[currentPlayer]["row"]][playerPositions[currentPlayer]["col"]], punctuation=False)}.'
                                for player, playerPosition in enumerate(playerPositions):
                                    if playerPosition == playerPositions[currentPlayer] and player != currentPlayer:
                                        message += f' {RED}Player {player}{CLEAR} is also on this space.'
                                for decorator in decorators[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']]:
                                    message += f' There is also a {CYAN}{decorator["type"]}{CLEAR} on this space.'
                                print(f'{" "*indent}{message}')
                                for move in possibleMoves:
                                    destinationSpaceType = board[move['destination']['row']][move['destination']['col']]
                                    message = f'If you move {GREEN}{move["direction"]}{CLEAR}, you will land on {grammatiseSpaceType(destinationSpaceType, punctuation=False)}.'
                                    for player, playerPosition in enumerate(playerPositions):
                                        if playerPosition == move['destination']:
                                            message += f' {RED}Player {player}{CLEAR} is on this space.'
                                    for decorator in decorators[move['destination']['row']][move['destination']['col']]:
                                        message += f' There is also a {CYAN}{decorator["type"]}{CLEAR} on this space.'
                                    print(f'{" "*indent}{message}')
                                indent -= 1
                            indent -= 1
                        if item == 'f3 menu':
                            indent += 1
                            print(f'{" "*indent}Your coordinates are: ({ORANGE}row{CLEAR}: {GREEN}{playerPositions[currentPlayer]["row"]+1}{CLEAR}, {ORANGE}column{CLEAR}: {GREEN}{playerPositions[currentPlayer]["col"]+1}{CLEAR}).')
                            indent -= 1
                        if item == 'safeword':
                            playerPositions[currentPlayer] = {"row": GRID_SIZE // 2, "col": GRID_SIZE // 2}
                        #where's the flamingo
                        if item == 'red potion':
                            indent += 1
                            if board[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']] == 'shadow realm':
                                print(f'{" "*indent}The red potion is {RED}useless{CLEAR} in the {SHADOW_REALM_SPACE}shadow realm{CLEAR}. No information was given.')
                            else:
                                shortestPathToFlamingo = findShortestPathToFlamingo(board, paths, playerPositions[currentPlayer], highwayInformation)
                                firstPath = shortestPathToFlamingo[0]
                                possibleMoves = findPossibleMoves(paths, playerPositions[currentPlayer], True, highwayInformation)
                                for move in possibleMoves:
                                    possiblePaths = [
                                        {"start": move['path']['start'], "end": move['path']['end'], "oneWay": False},
                                        {"start": move['path']['start'], "end": move['path']['end'], "oneWay": True},
                                        {"start": move['path']['end'], "end": move['path']['start'], "oneWay": False},
                                        {"start": move['path']['end'], "end": move['path']['start'], "oneWay": True},
                                    ]
                                    if firstPath in possiblePaths:
                                        print(f'{" "*indent}To get closer to the {FLAMINGO_SPACE}flamigo{CLEAR}, you should go {GREEN}{move["direction"]}{CLEAR}.')
                            indent -= 1
                        if item == 'green potion':
                            indent += 1
                            if board[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']] == 'shadow realm':
                                print(f'{" "*indent}The green potion is {RED}useless{CLEAR} in the {SHADOW_REALM_SPACE}shadow realm{CLEAR}. No information was given.')
                            else:
                                shortestPathToFlamingo = findShortestPathToFlamingo(board, paths, playerPositions[currentPlayer], highwayInformation)
                                print(f'{" "*indent}The {FLAMINGO_SPACE}flamigo space{CLEAR} is {GREEN}{len(shortestPathToFlamingo)}{CLEAR} moves away.')
                            indent -= 1
                        if item == 'flamingo':
                            indent += 1
                            print(f'{" "*indent}Successfully placed a {FLAMINGO_SPACE}flamingo{CLEAR} on {GREEN}This Space{CLEAR}!')
                            if board[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']] == 'shadow realm':
                                indent += 1
                                print(f'{" "*indent}The {FLAMINGO_SPACE}flamingo{CLEAR} {RED}got lost{CLEAR} in the {SHADOW_REALM_SPACE}shadow realm{CLEAR} and died.')
                                indent -= 1
                            else:
                                decorators[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']].append({"type": 'flamingo', "placedBy": currentPlayer, "reward": 0})
                            indent -= 1
                        if item == 'information':
                            indent += 1
                            for n, row in enumerate(board):
                                for m, cell in enumerate(row):
                                    if cell == 'flamingo':
                                        flamingoPos = (n+1, m+1)
                            rowOrCol = random.choice(['row', 'col'])
                            if rowOrCol == 'row':
                                choices = [x for x in list(range(1,GRID_SIZE+1)) if x != flamingoPos[0]]
                                print(f'{" "*indent}The {FLAMINGO_SPACE}flamingo space{CLEAR} is {RED}not{CLEAR} in {ORANGE}row {random.choice(choices)}{CLEAR}.')
                            else:
                                choices = [x for x in list(range(1,GRID_SIZE+1)) if x != flamingoPos[1]]
                                print(f'{" "*indent}The {FLAMINGO_SPACE}flamingo space{CLEAR} is {RED}not{CLEAR} in {ORANGE}column {random.choice(choices)}{CLEAR}.')
                            indent -= 1
                        #violence is always the answer
                        if item == 'knife':
                            indent += 1
                            playersOnCurrentSpot = [n for n, pos in enumerate(playerPositions) if pos == playerPositions[currentPlayer] and n != currentPlayer]
                            if len(playersOnCurrentSpot) == 0:
                                print(f'{" "*indent}Unfortunately, {RED}No one{CLEAR} shares a space with you.')
                            else:
                                for player in playersOnCurrentSpot:
                                    playerGolds[player] -= reward
                                    playerGolds[currentPlayer] += reward
                                    print(f'{" "*indent}Stolen {YELLOW}{reward} gold{CLEAR} from {GREEN}Player {player}{CLEAR}.')
                                    indent += 1
                                    print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR} and {RED}Player {player}{CLEAR} now has {YELLOW}{playerGolds[player]} gold{CLEAR}.')
                                    indent -= 1
                                    updateQuests('stabPeople', 1)
                            indent -= 1
                        if item == 'gun':
                            indent += 1
                            print(f'{" "*indent}Which direction would you like to shoot?')
                            indent += 1
                            print(f'{" "*indent}0: Down')
                            print(f'{" "*indent}1: Left')
                            print(f'{" "*indent}2: Right')
                            print(f'{" "*indent}3: Up')
                            indent -= 1
                            direction = askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', 3)
                            if direction == '0':
                                changing = 'row'
                                same = 'col'
                                plusOrMinus = 1
                            if direction == '1':
                                changing = 'col'
                                same = 'row'
                                plusOrMinus = -1
                            if direction == '2':
                                changing = 'col'
                                same = 'row'
                                plusOrMinus = 1
                            if direction == '3':
                                changing = 'row'
                                same = 'col'
                                plusOrMinus = 1
                            foundSomeone = False
                            currentPos = playerPositions[currentPlayer][changing]
                            possibleTargets = [(n+1, playerPos) for n, playerPos in enumerate(playerPositions[1:]) if playerPos[same] == playerPositions[currentPlayer][same]]
                            peopleShot = 0
                            while not foundSomeone:
                                currentPos += plusOrMinus
                                if currentPos >= GRID_SIZE:
                                    currentPos = 0
                                if currentPos <= -1:
                                    currentPos = GRID_SIZE-1
                                for player, playerPosition in possibleTargets:
                                    if playerPosition[changing] == currentPos:
                                        foundSomeone = True
                                        peopleShot += 1
                                        if player != currentPlayer:
                                            indent += 1
                                            print(f'{" "*indent}You hit {RED}Player {player}{CLEAR}!')
                                            playerGolds[player] -= reward
                                            playerGolds[currentPlayer] += reward
                                            indent += 1
                                            print(f'{" "*indent}Stolen {YELLOW}{reward} gold{CLEAR} from {GREEN}Player {player}{CLEAR}.')
                                            print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR} and {RED}Player {player}{CLEAR} now has {YELLOW}{playerGolds[player]} gold{CLEAR}.')
                                            indent -= 2
                                        else:
                                            indent += 1
                                            print(f'{" "*indent}The bullet wrapped around the map and {RED}hit you{CLEAR}!')
                                            playerGolds[currentPlayer] -= reward
                                            indent += 1
                                            print(f'{" "*indent}You lost {YELLOW}{reward} gold{CLEAR}.')
                                            print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
                                            indent -= 2
                            updateQuests('shootPeople', peopleShot)
                            indent -= 1
                        if item == 'trap':
                            indent += 1
                            decorators[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']].append({"type": 'trap', "placedBy": currentPlayer, "reward": reward})
                            print(f'{" "*indent}Successfully placed a trap on {GREEN}This Space{CLEAR}!')
                            indent -= 1
                        if item == 'goblin':
                            indent += 1
                            print(f'{" "*indent}Successfully placed a goblin on {GREEN}This Space{CLEAR}!')
                            if board[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']] == 'shadow realm':
                                indent += 1
                                print(f'{" "*indent}The goblin {RED}got lost{CLEAR} in the {SHADOW_REALM_SPACE}shadow realm{CLEAR} and died.')
                                indent -= 1
                            else:
                                decorators[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']].append({"type": 'goblin', "placedBy": currentPlayer, "reward": reward})
                            indent -= 1
                        #movement stuff
                        if item == 'dumbells':
                            indent += 1
                            playerSpeeds[currentPlayer] += 0.1
                            playerSpeeds[currentPlayer] = round(playerSpeeds[currentPlayer], 4)
                            print(f'{" "*indent}Your {GYM_SPACE}speed{CLEAR} is now {GYM_SPACE}{playerSpeeds[currentPlayer]}{CLEAR}')
                            indent -= 1
                        if item == 'fat injection':
                            indent += 1
                            playersOnCurrentSpot = [n for n, pos in enumerate(playerPositions) if pos == playerPositions[currentPlayer] and n != currentPlayer]
                            if len(playersOnCurrentSpot) == 0:
                                print(f'{" "*indent}Unfortunately, {RED}No one{CLEAR} shares a space with you.')
                            else:
                                for player in playersOnCurrentSpot:
                                    playerSpeeds[player] -= 0.15
                                    playerSpeeds[player] = round(playerSpeeds[player], 4)
                                    if playerSpeeds[player] < MINIMUM_SPEED:
                                        playerSpeeds[player] = MINIMUM_SPEED
                                    print(f'{" "*indent}{RED}Player {player}{CLEAR} now has {GYM_SPACE}{playerSpeeds[player]} speed{CLEAR}.')
                            indent -= 1
                        if item == 'freeze ray':
                            indent += 1
                            player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the  player to be {CYAN}frozen{TURQUOISE}: (1-{NUM_PLAYERS}){CLEAR} ', False))
                            playerFrozens[player] = True
                            indent -= 1
                        if item == 'swap':
                            indent += 1
                            player1 = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the first player to be {TELEPORT_SPACE}swapped{TURQUOISE}: (1-{NUM_PLAYERS}){CLEAR} ', True))
                            valid = False
                            while not valid:
                                player2 = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the second player to be {TELEPORT_SPACE}swapped{TURQUOISE}: (1-{NUM_PLAYERS}){CLEAR} ', True))
                                if player2 == player1:
                                    indent += 1
                                    print(f'{" "*indent}{ERROR}The 2 players cannot be the same! Please try again{CLEAR}')
                                    indent -= 1
                                else:
                                    valid = True
                            temp = playerPositions[player1]
                            playerPositions[player1] = playerPositions[player2]
                            playerPositions[player2] = temp
                            indent -= 1
                        #miscellaneous
                        if item == 'gold potion':
                            indent += 1
                            if board[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']] == 'shadow realm':
                                print(f'{" "*indent}The gold potion is {RED}useless{CLEAR} in the {SHADOW_REALM_SPACE}shadow realm{CLEAR}. No {YELLOW}gold{CLEAR} was placed.')
                            else:
                                possibleMoves = findPossibleMoves(paths, playerPositions[currentPlayer], True, highwayInformation)
                                chosenSpace = random.choice(possibleMoves)['destination']
                                decorators[chosenSpace['row']][chosenSpace['col']].append({"type": 'gold', "placedBy": currentPlayer, "reward": reward})
                                print(f'{" "*indent}Successfully placed {reward} gold on a random {ORANGE}Adjacent Space{CLEAR}!')
                            indent -= 1
                        if item == 'wand':
                            indent += 1
                            player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who will spin the {RED}Bad Wheel{TURQUOISE} at the start of their next turn: (1-{NUM_PLAYERS}){CLEAR} ', True))
                            playerWaitingForEvents[player].append('bad wheel')
                            indent -= 1
                        if item == 'time machine':
                            timeMachineIndex = reward
                            if len(prevPlayerPositions) >= 1+NUM_PLAYERS:
                                playerPositions = prevPlayerPositions[-1-NUM_PLAYERS]
                                playerInventories = prevPlayerInventories[-1-NUM_PLAYERS]
                                playerGolds = prevPlayerGolds[-1-NUM_PLAYERS]
                                playerSpeeds = prevPlayerSpeeds[-1-NUM_PLAYERS]
                                playerProgress = prevPlayerProgress[-1-NUM_PLAYERS]
                                playerStealBonus = prevPlayerStealBonus[-1-NUM_PLAYERS]
                                playerInvestmentBonus = prevPlayerInvestmentBonus[-1-NUM_PLAYERS]
                                playerQuests = prevPlayerQuests[-1-NUM_PLAYERS]
                                playerWaitingForEvents = prevPlayerWaitingForEvents[-1-NUM_PLAYERS]
                                playerFrozens = prevPlayerFrozens[-1-NUM_PLAYERS]
                                playerQuantumNotifications = prevPlayerQuantumNotifications[-1-NUM_PLAYERS]
                                itemPrices = prevItemPrices[-1-NUM_PLAYERS]
                                itemRewards = prevItemRewards[-1-NUM_PLAYERS]
                                decorators = prevDecorators[-1-NUM_PLAYERS]
                                pathDecorators = prevPathDecorators[-1-NUM_PLAYERS]
                                board = prevBoards[-1-NUM_PLAYERS]
                                quantumEntanglements = prevQuantumEntanglements[-1-NUM_PLAYERS]
                                for _ in range(NUM_PLAYERS):
                                    prevPlayerPositions.pop(-1)
                                    prevPlayerInventories.pop(-1)
                                    prevPlayerGolds.pop(-1)
                                    prevPlayerSpeeds.pop(-1)
                                    prevPlayerProgress.pop(-1)
                                    prevPlayerStealBonus.pop(-1)
                                    prevPlayerInvestmentBonus.pop(-1)
                                    prevPlayerQuests.pop(-1)
                                    prevPlayerWaitingForEvents.pop(-1)
                                    prevPlayerFrozens.pop(-1)
                                    prevPlayerQuantumNotifications.pop(-1)
                                    prevItemPrices.pop(-1)
                                    prevItemRewards.pop(-1)
                                    prevDecorators.pop(-1)
                                    prevPathDecorators.pop(-1)
                                    prevBoards.pop(-1)
                                    prevQuantumEntanglements.pop(-1)
                                if f'time machine;{timeMachineIndex}' in playerInventories[currentPlayer]:
                                    playerInventories[currentPlayer].remove(f'time machine;{timeMachineIndex}')
                                for gameState in prevPlayerInventories:
                                    if f'time machine;{timeMachineIndex}' in gameState[currentPlayer]:
                                        gameState[currentPlayer].remove(f'time machine;{timeMachineIndex}')
                                itemDescriptions = redefineItemDescriptions()
                                generateImage(board, paths, quantumEntanglements)
                                indent -= 2
                                return 'continue'
                            else:
                                indent += 1
                                print(f'{" "*indent}{RED}Unfortunately, the game has not existed long enough to rewind 1 round.{CLEAR}')
                                indent -= 1
                        if item == 'padlock':
                            indent += 1
                            code = int(askOptions(f'{" "*indent}{TURQUOISE}Enter the code for this {CYAN}padlock{TURQUOISE}: (0-9999){CLEAR} ', 9999))
                            print(f'{" "*indent}Where would you like to place the {CYAN}padlock{CLEAR}?')
                            possibleMoves = findPossibleMoves(paths, playerPositions[currentPlayer], True, highwayInformation)
                            options = 0
                            indent += 1
                            for move in possibleMoves:
                                options += 1
                                print(f'{" "*indent}{options}: {move["direction"].title()}')
                            indent -= 1
                            choice = '0'
                            while choice == '0':
                                choice = askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', options)
                            chosenPath = possibleMoves[int(choice)-1]['path']
                            for n, path in enumerate(paths):
                                if path == chosenPath:
                                    pathDecorators[n].append({'type': 'padlock', 'code': code})
                            print(f'{" "*indent}Successfully placed a {CYAN}padlock{CLEAR} on {GREEN}That Path{CLEAR}!')
                            indent -= 1
                        if item == 'portable shop':
                            if playerGolds[currentPlayer] < min([itemPrices[key] for key in itemPrices.keys() if key != 'portable shop']):
                                indent += 1
                                print(f'{" "*indent}You don\'t have enough {YELLOW}gold{CLEAR} to buy anything! (You have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR})')
                                indent -= 1
                            else:
                                goToTheShop(portable=True)
                indent -= 1
    indent -= 1
    return 'dont continue'

def visitWingeria():
    global indent
    indent += 1
    for player, bonus in enumerate(playerInvestmentBonus):
        if player != 0 and player != currentPlayer and bonus != 0:
            print(f'{" "*indent}You must pay {RED}Player {player}{CLEAR} {YELLOW}{bonus} gold{CLEAR}!')
            playerGolds[currentPlayer] -= bonus
            playerGolds[player] += bonus
            indent += 1
            print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR} and {RED}Player {player}{CLEAR} now has {YELLOW}{playerGolds[player]} gold{CLEAR}.')
            indent -= 1
            time.sleep(0.5)
    order, cost = generateWingPlatter()
    print(f'{" "*indent}You ordered {order}.')
    playerSpeeds[currentPlayer] -= cost*0.0035
    if playerSpeeds[currentPlayer] < MINIMUM_SPEED:
        playerSpeeds[currentPlayer] = MINIMUM_SPEED
    playerSpeeds[currentPlayer] = round(playerSpeeds[currentPlayer], 4)
    print(f'{" "*indent}You {RED}gained some weight{CLEAR}, so your speed is now {GYM_SPACE}{playerSpeeds[currentPlayer]}{CLEAR}.')
    updateQuests('eatChicken', cost)
    if playerGolds[currentPlayer] > 0:
        time.sleep(0.5)
        print(f'{" "*indent}Would you like to {YELLOW}invest{CLEAR} in {PAPAS_WINGERIA_SPACE}papa\'s wingeria{CLEAR}? (you have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR})')
        indent += 1
        print(f'{" "*indent}Once you invest {YELLOW}{WINGERIA_PROGRESS_REQUIRED} gold{CLEAR} you will recieve {YELLOW}1 gold{CLEAR} each time someone visits the {PAPAS_WINGERIA_SPACE}wingeria{CLEAR}!')
        investment = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your investment (0 for no investment):{CLEAR} ', playerGolds[currentPlayer]))
        playerGolds[currentPlayer] -= investment
        playerProgress[currentPlayer]["wingeria"] += investment
        indent += 1
        print(f'{" "*indent}You have invested {GREEN}{playerProgress[currentPlayer]["wingeria"]}{CLEAR} out of {YELLOW}{WINGERIA_PROGRESS_REQUIRED} gold{CLEAR}.')
        increased = False
        while playerProgress[currentPlayer]["wingeria"] >= WINGERIA_PROGRESS_REQUIRED:
            playerProgress[currentPlayer]["wingeria"] -= WINGERIA_PROGRESS_REQUIRED
            playerInvestmentBonus[currentPlayer] += 1
            increased = True
        if increased:
            indent += 1
            print(f'{" "*indent}{GREEN}Congratulations!{CLEAR} You now steal {YELLOW}{playerInvestmentBonus[currentPlayer]} gold{CLEAR} each time a player visits the {PAPAS_WINGERIA_SPACE}wingeria{CLEAR}!')
            indent -= 1
        indent -= 2
    indent -= 1
    
def visitGym():
    global indent
    indent += 1
    print(f'{" "*indent}Which workout would you like to do?')
    indent += 1
    print(f'{" "*indent}0: Squats - Increase your {GYM_SPACE}speed{CLEAR}.')
    print(f'{" "*indent}1: Bicep Curls - Increase the {YELLOW}gold{CLEAR} you get from stealing.')
    print(f'{" "*indent}2: Mewing - {RED}1 in 100 chance{CLEAR} of doubling {GYM_SPACE}speed{CLEAR} and {YELLOW}gold{CLEAR}.')
    indent -= 1
    choice = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your choice:{CLEAR} ', 2))
    if choice == 0:
        indent += 1
        workoutTime = random.randint(1, 24)
        print(f'{" "*indent}You worked out for {GYM_SPACE}{workoutTime} hour{"s" if workoutTime != 1 else ""}{CLEAR}.')
        playerSpeeds[currentPlayer] += workoutTime*0.0035
        playerSpeeds[currentPlayer] = round(playerSpeeds[currentPlayer], 4)
        print(f'{" "*indent}You {GREEN}lost some weight{CLEAR}, so your speed is now {GYM_SPACE}{playerSpeeds[currentPlayer]}{CLEAR}.')
        updateQuests('workout', workoutTime)
        indent -= 1
    if choice == 1:
        indent += 1
        playerProgress[currentPlayer]["gym"] += 1
        print(f'{" "*indent}Your {GYM_SPACE}gym progress{CLEAR} is now {GREEN}{playerProgress[currentPlayer]["gym"]}{CLEAR} out of {GREEN}{GYM_PROGRESS_REQUIRED}{CLEAR}')
        if playerProgress[currentPlayer]["gym"] == GYM_PROGRESS_REQUIRED:
            indent += 1
            print(f'{" "*indent}{GREEN}Congratulations!{CLEAR} You now steal one more {YELLOW}gold{CLEAR}.')
            playerProgress[currentPlayer]["gym"] = 0
            playerStealBonus[currentPlayer] += 1
            for n, item in enumerate(playerInventories[currentPlayer]):
                if ';' in item and 'time machine' not in item:
                    split = item.split(';')
                    playerInventories[currentPlayer][n] = f'{split[0]};{int(split[1])+1}'
            indent -= 1
        indent -= 1
    if choice == 2:
        indent += 1
        if random.random() <= 0.01:
            print(f'{" "*indent}{GREEN}Your mewing paid off!{CLEAR}')
            playerSpeeds[currentPlayer] *= 2
            print(f'{" "*indent}Your speed is now {GYM_SPACE}{playerSpeeds[currentPlayer]}{CLEAR}.')
            playerGolds[currentPlayer] *= 2
            print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
        else:
            print(f'{" "*indent}{RED}Unfortunately,{CLEAR} your {GYM_SPACE}{random.randint(1, 24)} hour mewing exercise{CLEAR} did nothing!')
        indent -= 1
    indent -= 1

def playBlackjack(bet=0):
    global indent
    indent += 1
    def getCardColour(card):
        if 'Hearts' in card or 'Diamonds' in card:
            return f'{getColour(219, 72, 72)}{card}\033[0m'
        else:
            return f'{getColour(148, 148, 148)}{card}\033[0m'

    def getHandValueColour(value):
        if value < BLACKJACK_TARGET-6:
            return f' {GREEN}{value}\033[0m'
        elif value < BLACKJACK_TARGET-1:
            return f' {YELLOW}{value}\033[0m'
        elif value < BLACKJACK_TARGET+1:
            return f' {ORANGE}{value}\033[0m'
        else:
            return f' {RED}{value}\033[0m'
    
    def findValue(card):
        card = card.replace(' of ', '')
        card = card.replace('Hearts', '')
        card = card.replace('Diamonds', '')
        card = card.replace('Spades', '')
        card = card.replace('Clubs', '')
        try:
            value = int(card)
        except:
            if card == 'Ace':
                value = 11
            else:
                value = 10
        return value

    def sayHand(person='player'):
        global indent
        if person == 'dealer':
            print(f'{" "*indent}{CYAN}The Dealer\'s hand is:{CLEAR}')
            indent += 1
            for card in dealerhand:
                print(f'{" "*indent}{getCardColour(card)}')
            indent -= 1
            print(f'{" "*indent}Dealer hand value is{getHandValueColour(dealerhandValue)}')
        if person == 'player':
            print(f'{" "*indent}{CYAN}Your hand is:{CLEAR}')
            indent += 1
            for card in hand:
                print(f'{" "*indent}{getCardColour(card)}')
            indent -= 1
            print(f'{" "*indent}Your hand value is{getHandValueColour(handValue)}')
    
    def sayMostRecentCard():
        global indent
        print(f'{" "*indent}{CYAN}You drew a: {getCardColour(hand[-1])}{CLEAR}')
        print(f'{" "*indent}Your hand value is now{getHandValueColour(handValue)}')

    def betGold():
        global indent
        indent += 1
        if playerGolds[currentPlayer] > 0:
            betType = 'gold'
            print(f'{" "*indent}How much would you like to bet? (You have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR})')
            goldBet = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your choice (0 to bet an {CYAN}item{TURQUOISE}):{CLEAR} ', playerGolds[currentPlayer]))
            if goldBet == 0:
                indent -= 1
                return betItem()
            indent -= 1
            return goldBet, betType
        else:
            indent += 1
            print(f'{" "*indent}Unfortunately, {RED}you do not have any {YELLOW}gold{RED} to gamble!{CLEAR} You must bet with {CYAN}items{CLEAR}.')
            indent -= 2
            return betItem()
    
    def betItem():
        global indent
        indent += 1
        if len(playerInventories[currentPlayer]) > 0:
            betType = 'item'
            print(f'{" "*indent}Which item would you like to bet?')
            printItemList(playerInventories[currentPlayer])
            itemBet = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice (0 to bet {YELLOW}gold{TURQUOISE}):{CLEAR} ', len(playerInventories[currentPlayer])))
            if itemBet == 0:
                indent -= 1
                return betGold()
            indent -= 1
            return itemBet-1, betType
        else:
            indent += 1
            print(f'{" "*indent}Unfortunately, {RED}you do not have any {CYAN}items{RED} to gamble!{CLEAR} You must bet with {YELLOW}gold{CLEAR}.')
            indent -= 2
            return betGold()
    
    suits = ['Hearts', 'Diamonds', 'Spades', 'Clubs']
    cards = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']

    if bet != 0:
        betType = 'gold'
    else:
        print(f'{" "*indent}How would you like to bet?')
        indent += 1
        print(f'{" "*indent}0: With {YELLOW}gold{CLEAR}')
        print(f'{" "*indent}1: With an {CYAN}item{CLEAR}')
        indent -= 1
        choice = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your choice:{CLEAR} ', 1))
        if choice == 0:
            bet, betType = betGold()
        else:
            bet, betType = betItem()

    youBusted = None
    dealerBusted = None

    acesInHand = 0
    card1 = f'{random.choice(cards)} of {random.choice(suits)}'
    card1Value = findValue(card1)
    if 'Ace' in card1:
        acesInHand += 1
    card2 = f'{random.choice(cards)} of {random.choice(suits)}'
    card2Value = findValue(card2)
    if 'Ace' in card2:
        acesInHand += 1
    cardAmount = 2
    hand = [card1, card2]
    handValue = card1Value + card2Value
    if handValue == BLACKJACK_TARGET+1:
        handValue -= 10
        acesInHand -= 1

    #set up dealer stuff
    dealeracesInHand = 0
    dealercard1 = f'{random.choice(cards)} of {random.choice(suits)}'
    dealercard1Value = findValue(dealercard1)
    if 'Ace' in dealercard1:
        dealeracesInHand += 1
    dealercard2 = f'{random.choice(cards)} of {random.choice(suits)}'
    dealercard2Value = findValue(dealercard2)
    if 'Ace' in dealercard2:
        dealeracesInHand += 1
    dealercardAmount = 2
    dealerhand = [dealercard1, dealercard2]
    dealerhandValue = dealercard1Value + dealercard2Value
    if dealerhandValue == BLACKJACK_TARGET+1:
        dealerhandValue -= 10
        dealeracesInHand -= 1

    #let dealer simulate game
    dealerdoneDrawing = False
    while dealerdoneDrawing == False:
        if dealerhandValue <= BLACKJACK_TARGET-BLACKJACK_DEALER_CAUTION:
            dealercardAmount += 1
            globals()[f'dealercard{dealercardAmount}'] = f'{random.choice(cards)} of {random.choice(suits)}'
            if 'Ace' in globals()[f'dealercard{dealercardAmount}']:
                dealeracesInHand += 1
            globals()[f'dealercard{dealercardAmount}Value'] = findValue(globals()[f'dealercard{dealercardAmount}'])
            dealerhand.append(globals()[f'dealercard{dealercardAmount}'])
            dealerhandValue += globals()[f'dealercard{dealercardAmount}Value']
            if dealerhandValue > BLACKJACK_TARGET-BLACKJACK_DEALER_CAUTION:
                if dealerhandValue > BLACKJACK_TARGET:
                    if dealeracesInHand != 0:
                        dealerhandValue -= 10
                        dealeracesInHand -= 1
                    else:
                        dealerdoneDrawing = True
                        dealerBusted = True
                elif dealerhandValue <= BLACKJACK_TARGET:
                    dealerdoneDrawing = True
                    dealerBusted = False
        else:
            dealerdoneDrawing = True
            dealerBusted = False
    dealerShownCard = random.choice(dealerhand)
    print(f'{" "*indent}{GAMBLING_SPACE}-------DEALER-------{CLEAR}')
    indent += 1
    print(f'{" "*indent}{ORANGE}The dealer has {dealercardAmount} cards{CLEAR}')
    print(f'{" "*indent}One of the dealer\'s cards is: {getCardColour(dealerShownCard)}{CLEAR}')
    indent -= 1
    print(f'{" "*indent}{GAMBLING_SPACE}--------GAME--------{CLEAR}')
    indent += 1
    doneDrawing = False
    while doneDrawing == False:
        if len(hand) == 2:
            sayHand()
        else:
            sayMostRecentCard()
        draw = ''
        if handValue == BLACKJACK_TARGET:
            doneDrawing = True
            youBusted = False
            indent += 1
            print(f'{GREEN}You scored Blackjack!{CLEAR}')
            indent -= 1
            time.sleep(0.75)
        else:
            print(f'{" "*(indent-1)}{GAMBLING_SPACE}--------------------{CLEAR}')
            print(f'{" "*indent}Would you like to {GREEN}draw{CLEAR}?')
            indent += 1
            print(f'{" "*indent}0: Yes')
            print(f'{" "*indent}1: No')
            indent -= 1
            draw = askOptions(f'{" "*indent}{TURQUOISE}Enter your choice:{CLEAR} ', 1)
            if draw == '0':
                #draw
                cardAmount += 1
                globals()[f'card{cardAmount}'] = f'{random.choice(cards)} of {random.choice(suits)}'
                if 'Ace' in globals()[f'card{cardAmount}']:
                    acesInHand += 1
                globals()[f'card{cardAmount}Value'] = findValue(globals()[f'card{cardAmount}'])
                hand.append(globals()[f'card{cardAmount}'])
                handValue += globals()[f'card{cardAmount}Value']
                if handValue > BLACKJACK_TARGET:
                    if acesInHand != 0:
                        handValue -= 10
                        acesInHand -= 1
                    else:
                        doneDrawing = True
                        youBusted = True
                        sayMostRecentCard()
                        indent += 1
                        print(f'{" "*indent}{ORANGE}You busted!{CLEAR}')
                        indent -= 1
                        time.sleep(0.75)
                elif handValue == BLACKJACK_TARGET:
                    doneDrawing = True
                    youBusted = False
                    sayMostRecentCard()
                    indent += 1
                    print(f'{" "*indent}{GREEN}You scored Blackjack!{CLEAR}')
                    indent -= 1
                    time.sleep(0.75)
            elif draw == '1':
                doneDrawing = True
                if handValue <= BLACKJACK_TARGET:
                    youBusted = False
    indent -= 1
    print(f'{" "*indent}{GAMBLING_SPACE}-------RESULTS------{CLEAR}')
    sayHand('player')
    time.sleep(0.75)
    print(f'{" "*indent}{GAMBLING_SPACE}--------------------{CLEAR}')
    sayHand('dealer')
    time.sleep(0.75)
    print(f'{" "*indent}{GAMBLING_SPACE}--------------------{CLEAR}')

    if betType == 'item':
        item = playerInventories[currentPlayer][bet]
        if ';' in item:
            itemName = item.split(';')[0].title()
        else:
            itemName = item.title()
    
    if youBusted == True and dealerBusted == True:    
        print(f'{" "*indent}{YELLOW}Both of you busted, so no one wins!{CLEAR}')
    elif youBusted == True and dealerBusted == False:
        print(f'{" "*indent}{RED}You busted! That means the dealer wins!{CLEAR}')
        indent += 1
        if betType == 'gold':
            playerGolds[currentPlayer] -= bet
            print(f'{" "*indent}You lost {YELLOW}{bet} gold{CLEAR}!')
        if betType == 'item':
            playerInventories[currentPlayer].pop(bet)
            print(f'{" "*indent}You lost the {CYAN}{itemName}{CLEAR}!')
        indent -= 1
    elif youBusted == False and dealerBusted == True:
        print(f'{" "*indent}{GREEN}The dealer busted! That means you win!{CLEAR}')
        indent += 1
        if betType == 'gold':
            playerGolds[currentPlayer] += bet
            print(f'{" "*indent}You won {YELLOW}{bet} gold{CLEAR}!')
            updateQuests('gamble', bet)
        if betType == 'item':
            playerInventories[currentPlayer].append(item)
            print(f'{" "*indent}You won another {CYAN}{itemName}{CLEAR}!')
        indent -= 1
    elif youBusted == False and dealerBusted == False:
        print(f'{" "*indent}No one busted, so the person with the highest value wins...')
        if handValue > dealerhandValue:
            print(f'{" "*indent}{GREEN}You win!{CLEAR}')
            indent += 1
            if betType == 'gold':
                playerGolds[currentPlayer] += bet
                print(f'{" "*indent}You won {YELLOW}{bet} gold{CLEAR}!')
                updateQuests('gamble', bet)
            if betType == 'item':
                playerInventories[currentPlayer].append(item)
                print(f'{" "*indent}You won another {CYAN}{itemName}{CLEAR}!')
            indent -= 1
        else:
            print(f'{" "*indent}{RED}Dealer wins!{CLEAR}')
            indent += 1
            if betType == 'gold':
                playerGolds[currentPlayer] -= bet
                print(f'{" "*indent}You lost {YELLOW}{bet} gold{CLEAR}!')
            if betType == 'item':
                playerInventories[currentPlayer].pop(bet)
                print(f'{" "*indent}You lost the {CYAN}{itemName}{CLEAR}!')
            indent -= 1
    
    if betType == 'gold' and not (youBusted == True and dealerBusted == True):
        indent += 1
        print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
        indent -= 1
    indent -= 1

def playNumberGame(gameUnit, gameStop):
    global indent
    indent += 1
    def numToWords(num):
        d = {0: 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten', 11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen', 15: 'fifteen', 16: 'sixteen', 17: 'seventeen', 18: 'eighteen', 19: 'nine-teen', 20: 'twenty', 30: 'thirty', 40: 'forty', 50: 'fifty', 60: 'sixty', 70: 'seventy', 80: 'eighty', 90: 'nine-ty'}
        if (num < 20):
            return d[num]
        if (num < 100):
            if num % 10 == 0: 
                return d[num]
            else: 
                return d[num // 10 * 10] + '-' + d[num % 10]
        if num % 100 == 0: 
            return d[num // 100] + ' hundred'
        else: 
            return d[num // 100] + ' hundred and ' + numToWords(num % 100)

    def syllable_count(word):
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        if word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        if word.endswith("e"):
            count -= 1
        if count == 0:
            count += 1
        return count

    def getSyllables(word):
        word = word.replace('-', ' ')
        if ' ' in word:
            count = 0
            words = word.split(' ')
            for subWord in words:
                count += syllable_count(subWord)
        else:
            count = syllable_count(word)
        return count
    
    def findNextNumber(num):
        numWord = numToWords(num)
        numWordCleansed = numWord.replace(' ', '')
        numWordCleansed = numWordCleansed.replace('-', '')
        numWordSyllables = getSyllables(numWord)
        numberPass = True
        foundNextNumber = False
        while foundNextNumber == False:
            num += 1
            numWord = numToWords(num)
            numWordCleansed = numWord.replace(' ', '')
            numWordCleansed = numWordCleansed.replace('-', '')
            numWordSyllables = getSyllables(numWord)
            numberPass = True
            if str(gameUnit) in str(num):
                numberPass = False
            if num % gameUnit == 0:
                numberPass = False
            if len(str(num)) == gameUnit:
                numberPass = False
            if sum([int(digit) for digit in str(num)]) == gameUnit:
                numberPass = False
            if len(numWordCleansed) == gameUnit:
                numberPass = False
            if numWordSyllables == gameUnit:
                numberPass = False
            if numberPass == True:
                foundNextNumber = True
                nextNumber = num
        return nextNumber

    def askNumber():
        global indent
        ans = input(f'{" "*indent}What is the {ORANGE}{"next" if internalClock != 0 else "first"} number{CLEAR}? ')
        try:
            ans = int(ans)
        except ValueError:
            indent += 1
            print(f'{" "*indent}{RED}Must be a number!{CLEAR}')
            indent -= 1
            ans = askNumber()
        return ans
    
    internalClock = 0
    done = False
    while done == False:
        nextNumber = findNextNumber(internalClock)
        if nextNumber > gameStop:
            done = True
            result =  True
        else:
            ans = askNumber()
            humanAnswer = ans
            indent += 1
            if nextNumber == humanAnswer:
                print(f'{" "*indent}{GREEN}Correct!{CLEAR}')
                correct = True
            else:
                numWord = numToWords(ans)
                numWordCleansed = numWord.replace(' ', '')
                numWordCleansed = numWordCleansed.replace('-', '')
                numWordSyllables = getSyllables(numWord)
                if nextNumber < humanAnswer:
                    failReason = f'There is a correct answer ({nextNumber}) before {humanAnswer}'
                elif str(gameUnit) in str(ans):
                    failReason = f'{humanAnswer} contains {gameUnit}'
                elif ans % gameUnit == 0:
                    failReason = f'{humanAnswer} is divisible by {gameUnit}'
                elif len(str(ans)) == gameUnit:
                    failReason = f'{humanAnswer} has {gameUnit} Digits'
                elif sum([int(digit) for digit in str(ans)]) == gameUnit:
                    failReason = f'{humanAnswer}\'s digits sum to {gameUnit}'
                elif len(numWordCleansed) == gameUnit:
                    failReason = f'{humanAnswer} has {gameUnit} Letters'
                elif numWordSyllables == gameUnit:
                    failReason = f'{humanAnswer} has {gameUnit} Syllables'
                else:
                    failReason = f'That was so stupid i\'m not even going to say what was wrong'
                print(f'{" "*indent}{RED}Incorrect! {failReason}.{CLEAR}')
                correct = False
            indent -= 1
            internalClock = humanAnswer
            if correct == False:
                done = True
                result = False
    indent -= 1
    return result

def playBoardQuiz(numQuestions):
    global indent
    indent += 1
    result = True
    for roundNum in range(1,numQuestions+1):
        print(f'{" "*indent}Question {getColourFromFraction((numQuestions-roundNum)/numQuestions)}{roundNum}{CLEAR}:')
        valid = False
        while not valid: 
            moves = []
            currentSpace = {"row": GRID_SIZE // 2, "col": GRID_SIZE // 2}
            valid = True
            for n in range(roundNum):
                if valid:
                    possibleMoves = findPossibleMoves(paths, currentSpace, True, highwayInformation)
                    if len(moves) > 0:
                        if 'down' in moves[-1]:
                            avoid = 'up'
                        if 'up' in moves[-1]:
                            avoid = 'down'
                        if 'left' in moves[-1]:
                            avoid = 'right'
                        if 'right' in moves[-1]:
                            avoid = 'left'
                        possibleMoves = [move for move in possibleMoves if move['direction'] != avoid]
                    if len(possibleMoves) == 0:
                        valid = False
                    else:
                        move = random.choice(possibleMoves)
                        moves.append(f'{getColourFromFraction((numQuestions-n-1)/numQuestions)}{move["direction"]}{CLEAR}')
                        currentSpace = move['destination']
                        if board[currentSpace['row']][currentSpace['col']] in ['shadow realm', 'flamingo']:
                            valid = False
        correctAnswer = board[currentSpace['row']][currentSpace['col']]
        possibleAnswers = [correctAnswer]
        for _ in range(3):
            possibleAnswers.append(random.choice([x for x in ['empty', 'home', 'good', 'bad', 'shop', 'teleport', 'gambling', 'timewarp', 'papas wingeria', 'gym', 'quest', 'entanglement'] if x not in possibleAnswers]))
        random.shuffle(possibleAnswers)
        print(f'{" "*indent}If you move {", ".join(moves)} from the {HOME_SPACE}home{CLEAR} space, what space do you land on?')
        indent += 1
        for n, answer in enumerate(possibleAnswers):
            print(f'{" "*indent}{n+1}: {grammatiseSpaceType(answer, title=True)}')
        indent -= 1
        choice = 0
        while choice == 0:
            choice = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', 4))
        if choice == possibleAnswers.index(correctAnswer)+1:
            indent += 1
            print(f'{" "*indent}{GREEN}Correct!{CLEAR}')
            indent -= 1
        else:
            indent += 1
            print(f'{" "*indent}{RED}Incorrect!{CLEAR} The correct answer was {grammatiseSpaceType(correctAnswer, title=True)}')
            indent -= 1
            result = False
            break
    indent -= 1
    return result

def playLogicGame(numQuestions):
    global indent
    indent += 1
    result = True
    def convertToHumanReadable(expression):
        expression = expression.replace('0', f'{RED}False{CLEAR}')
        expression = expression.replace('1', f'{GREEN}True{CLEAR}')
        expression = expression.replace('!', f'{CYAN}not{CLEAR} ')
        expression = expression.replace('&', f' {CYAN}and{CLEAR} ')
        expression = expression.replace('|', f' {CYAN}or{CLEAR} ')
        expression = expression.replace('^', f' {CYAN}xor{CLEAR} ')
        expression = expression.replace('<', f' {CYAN}nand{CLEAR} ')
        expression = expression.replace('>', f' {CYAN}nor{CLEAR} ')
        expression = expression.replace('v', f' {CYAN}xnor{CLEAR} ')
        return expression
    
    for roundNum in range(1,numQuestions+1):
        print(f'{" "*indent}Question {getColourFromFraction((numQuestions-roundNum)/numQuestions)}{roundNum}{CLEAR}:')
        correctAnswer = random.choice(['0', '1'])
        expression = correctAnswer
        for _ in range(roundNum):
            newExpression = ''
            for n, char in enumerate(expression):
                if char in ['(', ')', '!', '&', '|', '^', '<', '>', 'v']:
                    newExpression += char
                else: 
                    if char == '0':
                        newBit = random.choice(['!1', '!1', '!1', '0&0', '0&1', '1&0', '0|0', '0^0', '1^1', '1<1', '1>0', '0>1', '1>1', '0v1', '1v0'])
                    else:
                        newBit = random.choice(['!0', '!0', '!0', '1&1', '1|0', '0|1', '1|1', '0^1', '1^0', '0<0', '0<1', '1<0', '0>0', '0v0', '1v1'])
                    if newBit[0] == '!':
                        newExpression += newBit
                    elif n != 0:
                        if expression[n-1] in ['!', '&', '|', '^', '<', '>', 'v']:
                            newExpression += f'({newBit})'
                        else:
                            newExpression += newBit
                    else:
                        newExpression += newBit
            expression = newExpression
        print(f'{" "*indent}{convertToHumanReadable(expression)}')
        indent += 1
        print(f'{" "*indent}0: {RED}False{CLEAR}')
        print(f'{" "*indent}1: {GREEN}True{CLEAR}')
        indent -= 1
        choice = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', 1))
        if choice == int(correctAnswer):
            indent += 1
            print(f'{" "*indent}{GREEN}Correct!{CLEAR}')
            indent -= 1
        else:
            indent += 1
            print(f'{" "*indent}{RED}Incorrect!{CLEAR} The correct answer was {convertToHumanReadable(correctAnswer)}')
            indent -= 1
            result = False
            break
    indent -= 1
    return result

def playDateQuiz():
    global indent
    indent += 1
    result = True
    today = datetime.datetime.today()
    for roundNum in range(1,6):
        print(f'{" "*indent}Question {getColourFromFraction((5-roundNum)/5)}{roundNum}{CLEAR}:')
        if roundNum == 1:
            lowerBound = datetime.date(today.year, today.month, 1)
            if today.month == 12:
                upperBound = datetime.date(today.year + 1, 1, 1) - datetime.timedelta(days=1)
            else:
                upperBound = datetime.date(today.year, today.month + 1, 1) - datetime.timedelta(days=1)
        if roundNum == 2:
            lowerBound = datetime.date(today.year, 1, 1)
            upperBound = datetime.date(today.year, 12, 31)
        if roundNum == 3:
            lowerBound = datetime.date((today.year//10)*10, 1, 1)
            upperBound = datetime.date((today.year//10)*10+9, 12, 31)
        if roundNum == 4:
            lowerBound = datetime.date((today.year//100)*100, 1, 1)
            upperBound = datetime.date((today.year//100)*100+99, 12, 31)
        if roundNum == 5:
            lowerBound = datetime.date((today.year//100)*100-200, 1, 1)
            upperBound = datetime.date((today.year//100)*100+299, 12, 31)
        possibleDays = (upperBound-lowerBound).days
        chosenDate = lowerBound + datetime.timedelta(days=random.randrange(possibleDays))
        print(f'{" "*indent}{chosenDate.strftime(f"{CYAN}%B{CLEAR} {GREEN}%-d{CLEAR}, {ORANGE}%Y{CLEAR}")}')
        correctAnswer = chosenDate.strftime('%A')
        possibleAnswers = [correctAnswer]
        for _ in range(3):
            possibleAnswers.append(random.choice([x for x in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'] if x not in possibleAnswers]))
        random.shuffle(possibleAnswers)
        indent += 1
        for n, answer in enumerate(possibleAnswers):
            print(f'{" "*indent}{n+1}: {answer}')
        indent -= 1
        choice = 0
        while choice == 0:
            choice = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', 4))
        if choice == possibleAnswers.index(correctAnswer)+1:
            indent += 1
            print(f'{" "*indent}{GREEN}Correct!{CLEAR}')
            indent -= 1
        else:
            indent += 1
            print(f'{" "*indent}{RED}Incorrect!{CLEAR} The correct answer was {correctAnswer}')
            indent -= 1
            result = False
            break
    indent -= 1
    return result

def generateWingPlatter():
    global indent
    ingredients = {"allTime": {"meats": ["Chicken Wings", "Boneless Wings", "Chicken Strips", "Shrimp", "Tofu Skewers", "Hog Wings"], "sauces": ["BBQ Sauce", "Buffalo Sauce", "Spicy Garlic Sauce", "Calypso Sauce", "Atomic Sauce", "Honey Mustard Sauce", "Teriyaki Sauce", "Medium Sauce", "Parmesan Sauce", "Wild Onion Sauce", "Wasabi Sauce", "Smoky Bacon Sauce", "Thai Chili Sauce", "Blazeberry Sauce", "Alabama BBQ Sauce", "Nashville Hot Sauce", "Peri Peri Sauce", "Aji Amarillo Sauce", "Carolina Sauce", "Tikka Masala Sauce", "Sriracha Sauce", "Adobo Sauce"], "sides": ["Carrots", "Celery", "Red Peppers", "Green Peppers", "French Fries", "Cheese Cubes", "Curly Fries", "Potato Skins", "Taquitos"], "dips": ["Blue Cheese Dip", "Ranch Dip", "Mango Chili Dip", "Awesome Sauce Dip", "Kung Pao Dip", "Zesty Pesto Dip", "Lemon Butter", "Southwest Dip", "Hummus", "Artichoke Dip", "Guacamole", "Blackberry Remoulade"]}, "january": [{"name": "New Year", "sauces": ["Rainbow-livian Sauce", "Poutine Sauce"], "sides": ["Pizza Poppers"], "dips": ["Cheezy Whip"]}], "february": [{"name": "Mardi Gras", "sauces": ["Muffuletta Sauce", "Vieux Carr\u00e9 Sauce"], "sides": ["Crawdads"], "dips": ["Creole Crab Dip"]}], "march": [{"name": "Lucky Lucky Matsuri", "sauces": ["Gochujang Sauce", "Ginger Miso Sauce"], "sides": ["Kobumaki"], "dips": ["Karashi Mayo"]}], "april": [{"name": "Big Top Carnival", "sauces": ["Salted Caramel Sauce", "Candy Apple Sauce"], "sides": ["Corn Dogs"], "dips": ["PB&J Dip"]}], "may": [{"name": "OnionFest", "sauces": ["Sarge's Revenge Sauce"], "sides": ["Cocktail Onions"], "dips": ["French Onion Dip"]}], "june": [{"name": "Summer Luau", "sauces": ["Kilauea Sauce", "Hulu Hula Sauce"], "sides": ["Luau Musubi"], "dips": ["Mango-Chili Dip"]}], "july": [{"name": "Starlight BBQ", "sauces": ["Lone Star Pit Sauce", "Mambo Sauce"], "sides": ["BBQ Ribs"], "dips": ["Coleslaw"]}], "august": [{"name": "BavariaFest", "sauces": ["Doppelbock Sauce", "W\u00fcrzig Sauce"], "sides": ["Wiesswurst"], "dips": ["Bierk\u00e4se Dip"]}], "september": [{"name": "Maple Mornings", "sauces": ["Maple Glaze", "Sunrise Sauce"], "sides": ["Bacon"], "dips": ["Shirred Egg"]}], "october": [{"name": "Halloween", "sauces": ["La Catrina Sauce", "Ecto Sauce"], "sides": ["Mummy Dogs"], "dips": ["Purple Pesto"]}], "november": [{"name": "Thanksgiving", "sauces": ["Peppered Pumpkin Sauce", "Wojapi Sauce"], "sides": ["Sweet Potato Wedges"], "dips": ["Gravy"]}], "december": [{"name": "Christmas", "sauces": ["Cranberry Chili Sauce", "Krampus Sauce"], "sides": ["Roasted Asparagus"], "dips": ["Risalamande"]}]}
    month = random.choice(['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'])
    holiday = random.choice(ingredients[month])
    meats = ingredients['allTime']['meats']
    sauces = ingredients['allTime']['sauces'] + holiday['sauces']
    sides = ingredients['allTime']['sides'] + holiday['sides']
    dips = ingredients['allTime']['dips'] + holiday['dips']
    
    output = 'a Wing Platter with\n'
    cost = 0
    slots = 7
    numMeats = random.randint(1,3)
    slots -= (2 * numMeats)
    items = []
    for _ in range(numMeats):
        qty = random.randint(1,12)
        meat = random.choice(meats)
        side = random.choice(['on the left', '', 'on the right'])
        if qty == 1 and meat != 'Shrimp':
            meat = meat[:-1]
        items.append(f'{GREEN}{qty}{CLEAR} {PAPAS_WINGERIA_SPACE}{meat}{CLEAR} coated in {ORANGE}{random.choice(sauces)}{CLEAR}{" " if side != "" else ""}{side}')
        cost += qty
    numDips = random.randint(0,4)
    if numDips != 0:
        slots -= 1
    for _ in range(slots):
        side = random.choice(['on the left', '', 'on the right'])
        items.append(f'{GREEN}{random.randint(2,12)}{CLEAR} {RED}{random.choice(sides)}{CLEAR}{" " if side != "" else ""}{side}')
    for _ in range(numDips):
        items.append(f'{CYAN}{random.choice(dips)}{CLEAR}')
    newline = '\n'
    indent += 1
    for n, item in enumerate(items):
        output += f'{" "*indent}{item}{" and" if n == len(items)-2 else "," if n != len(items)-1 else ""}{newline if n != len(items)-1 else ""}'
    indent -= 1
    return output, cost

def selectRandomSpace(board):
    validSpace = False
    while not validSpace:
        row = random.randint(0, GRID_SIZE-1)
        col = random.randint(0, GRID_SIZE-1)
        if board[row][col] not in [None, 'flamingo']:
            space = {"row": row, "col": col}
            validSpace = True
    return space

def grammatiseSpaceType(spaceType, punctuation=False, title=False):
    if spaceType == 'empty':
        return f'an {EMPTY_SPACE}{"Empty" if title else "empty"}{CLEAR} space{"." if punctuation else ""}'
    if spaceType == 'flamingo':
        return f'the {FLAMINGO_SPACE}{"Flamingo" if title else "flamingo"}{CLEAR} space{"!" if punctuation else ""}'
    if spaceType == 'home':
        return f'the {HOME_SPACE}{"Home" if title else "home"}{CLEAR} space{"." if punctuation else ""}'
    if spaceType == 'shadow realm':
        return f'the {SHADOW_REALM_SPACE}{"Shadow Realm" if title else "shadow realm"}{CLEAR} space{"." if punctuation else ""}'
    if spaceType == 'good':
        return f'a {GOOD_SPACE}{"Good" if title else "good"}{CLEAR} space{"!" if punctuation else ""}'
    if spaceType == 'bad':
        return f'a {BAD_SPACE}{"Bad" if title else "bad"}{CLEAR} space{"." if punctuation else ""}'
    if spaceType == 'shop':
        return f'a {SHOP_SPACE}{"Shop" if title else "shop"}{CLEAR} space{"!" if punctuation else ""}'
    if spaceType == 'teleport':
        return f'a {TELEPORT_SPACE}{"Teleport" if title else "teleport"}{CLEAR} space{"!" if punctuation else ""}'
    if spaceType == 'gambling':
        return f'a {GAMBLING_SPACE}{"Gambling" if title else "gambling"}{CLEAR} space{"!" if punctuation else ""}'
    if spaceType == 'timewarp':
        return f'a {TIMEWARP_SPACE}{"Time Warp" if title else "time warp"}{CLEAR} space{"!" if punctuation else ""}'
    if spaceType == 'papas wingeria':
        apostrophe = '\''
        return f'{PAPAS_WINGERIA_SPACE}{f"Papa{apostrophe}s Wingeria" if title else f"papa{apostrophe}s wingeria"}{CLEAR}{"!" if punctuation else ""}'
    if spaceType == 'gym':
        return f'a {GYM_SPACE}{"Gym" if title else "gym"}{CLEAR} space{"!" if punctuation else ""}'
    if spaceType == 'quest':
        return f'a {QUEST_SPACE}{"Quest" if title else "quest"}{CLEAR} space{"!" if punctuation else ""}'
    if spaceType == 'entanglement':
        return f'an {ENTANGLEMENT_SPACE}{"Entanglement" if title else "entanglement"}{CLEAR} space{"!" if punctuation else ""}'

def getColourFromFraction(fraction):
    if fraction == 0:
        return RED
    elif fraction < 0.4:
        return ORANGE
    elif fraction < 0.7:
        return YELLOW
    else:
        return GREEN

def saveToFile(filename):
    data = {
        "currentPlayer": currentPlayer,
        "board": board,
        "paths": paths,
        "highwayInformation": highwayInformation,
        "decorators": decorators,
        "pathDecorators": pathDecorators,
        "quantumEntanglements": quantumEntanglements,
        "playerPositions": playerPositions,
        "playerInventories": playerInventories,
        "playerGolds": playerGolds,
        "playerSpeeds": playerSpeeds,
        "playerProgress": playerProgress,
        "playerStealBonus": playerStealBonus,
        "playerInvestmentBonus": playerInvestmentBonus,
        "playerQuests": playerQuests,
        "playerWaitingForEvents": playerWaitingForEvents,
        "playerFrozens": playerFrozens,
        "playerQuantumNotifications": playerQuantumNotifications,
        "itemPrices": itemPrices,
        "itemRewards": itemRewards,
        "prevBoards": prevBoards,
        "prevDecorators": prevDecorators,
        "prevPathDecorators": prevPathDecorators,
        "prevQuantumEntanglements": prevQuantumEntanglements,
        "prevPlayerPositions": prevPlayerPositions,
        "prevPlayerInventories": prevPlayerInventories,
        "prevPlayerGolds": prevPlayerGolds,
        "prevPlayerSpeeds": prevPlayerSpeeds,
        "prevPlayerProgress": prevPlayerProgress,
        "prevPlayerStealBonus": prevPlayerStealBonus,
        "prevPlayerInvestmentBonus": prevPlayerInvestmentBonus,
        "prevPlayerQuests": prevPlayerQuests,
        "prevPlayerWaitingForEvents": prevPlayerWaitingForEvents,
        "prevPlayerFrozens": prevPlayerFrozens,
        "prevPlayerQuantumNotifications": prevPlayerQuantumNotifications,
        "prevItemPrices": prevItemPrices,
        "prevItemRewards": prevItemRewards
    }
    with open(f'saves/{filename}.json', 'w') as f:
        json.dump(data,f)

def redefineItemDescriptions():
    itemDescriptions = {
        #help i'm lost
        "compass": f'See all {ORANGE}adjacent{CLEAR} spaces and players.',
        "f3 menu": f'Tells you your current {ORANGE}coordinates{CLEAR}.',
        "safeword": f'Return to the {HOME_SPACE}home space{CLEAR}.',
        #where's the flamingo
        "red potion": f'Tells you where to go to get closer to the {FLAMINGO_SPACE}flamingo space{CLEAR}.',
        "green potion": f'Tells you how many moves away the {FLAMINGO_SPACE}flamingo space{CLEAR} is.',
        "flamingo": f'Moves towards the {FLAMINGO_SPACE}flamingo space{CLEAR} at the end of the {RED}last player\'s{CLEAR} turn.',
        "information": f'Tells you a random {ORANGE}row{CLEAR} or {ORANGE}column{CLEAR} that the {FLAMINGO_SPACE}flamingo space{CLEAR} is {RED}not{CLEAR} in.',
        #violence is always the answer
        "knife": f'Steal {YELLOW}{itemRewards["knife"]} gold{CLEAR} from another player if they are on the same space as you.',
        "gun": f'Shoot in a direction and steal {YELLOW}{itemRewards["gun"]} gold{CLEAR} if it hits someone.',
        "trap": f'Sets a {RED}trap{CLEAR} that will steal {YELLOW}{itemRewards["trap"]} gold{CLEAR} when landed on.',
        "goblin": f'Randomly moves around the map. If a player lands on a space with your goblin, you steal {YELLOW}{itemRewards["goblin"]} gold{CLEAR}.',
        #movement stuff
        "dumbells": f'Increase your {GYM_SPACE}speed{CLEAR} by {GYM_SPACE}0.1{CLEAR}.',
        "fat injection": f'Decrease another player\'s {GYM_SPACE}speed{CLEAR} by {GYM_SPACE}0.15{CLEAR} if they are on the same space as you.',
        "freeze ray": f'Make another player lose the {ORANGE}ability to move{CLEAR} for 1 turn.',
        "swap": f'{TELEPORT_SPACE}Swap{CLEAR} the positions of 2 chosen players.',
        #miscellaneous
        "gold potion": f'Places {YELLOW}{itemRewards["gold potion"]} gold{CLEAR} on a random {ORANGE}adjacent{CLEAR} space.',
        "wand": f'Make a player spin the {RED}Bad Wheel{CLEAR} at the start of their next turn.',
        "time machine": f'{TIMEWARP_SPACE}Rewind time{CLEAR} to the start of your {ORANGE}previous turn{CLEAR}.',
        'padlock': f'Place this on an adjacent path. When travelling along this path, you must enter a {RED}4-digit{CLEAR} code.',
        "portable shop": f'Visit the {SHOP_SPACE}shop{CLEAR} no matter where you are.'
    }
    return itemDescriptions

board, paths, decorators, pathDecorators = generateBoard()
quantumEntanglements = []
generateImage(board, paths, quantumEntanglements)
highwayInformation = decideHighwayInformation(board, paths)

itemPrices = {
    #help i'm lost
    "compass": 3,
    "f3 menu": 2,
    "safeword": 2,
    #where's the flamingo
    "red potion": 3,
    "green potion": 3,
    "flamingo": 3,
    "information": 2,
    #violence is always the answer
    "knife": 2,
    "gun": 2,
    "trap": 2,
    "goblin": 2,
    #movement stuff
    "dumbells": 2,
    "fat injection": 3,
    "freeze ray": 3,
    "swap": 2,
    #miscellaneous
    "gold potion": 2,
    "wand": 2,
    "time machine": 3,
    'padlock': 3,
    "portable shop": 3,
}

itemRewards = {
    #violence is always the answer
    "knife": itemPrices['knife'] + 1,
    "gun": itemPrices['gun'] + 1,
    "trap": itemPrices['trap'] + 1,
    "goblin": itemPrices['goblin'] - 1,
    #miscellaneous
    "gold potion": itemPrices['gold potion'] + 1
}

itemSectionRanges = {
    "1": "help i'm lost",
    "4": "where's the flamingo",
    "8": "violence is always the answer",
    "12": "movement stuff",
    "16": "miscellaneous"
}

itemDescriptions = redefineItemDescriptions()

playerPositions = [None]
playerInventories = [None]
playerGolds = [None]
playerSpeeds = [None]
playerProgress = [None]
playerStealBonus = [None]
playerInvestmentBonus = [None]
playerQuests = [None]
playerWaitingForEvents = [None]
playerFrozens = [None]
playerQuantumNotifications = [None]
for _ in range(NUM_PLAYERS):
    playerPositions.append({"row": GRID_SIZE // 2, "col": GRID_SIZE // 2})
    playerInventories.append(copy.deepcopy(STARTING_INVENTORY))
    playerGolds.append(STARTING_GOLD)
    playerSpeeds.append(STARTING_SPEED)
    playerProgress.append(copy.deepcopy({"gym": 0, "wingeria": 0}))
    playerStealBonus.append(0)
    playerInvestmentBonus.append(0)
    playerQuests.append(copy.deepcopy([]))
    playerWaitingForEvents.append(copy.deepcopy([]))
    playerFrozens.append(False)
    playerQuantumNotifications.append(0)

numTimeMachines = 0

prevPlayerPositions = [copy.deepcopy(playerPositions)]
prevPlayerInventories = [copy.deepcopy(playerInventories)]
prevPlayerGolds = [copy.deepcopy(playerGolds)]
prevPlayerSpeeds = [copy.deepcopy(playerSpeeds)]
prevPlayerProgress = [copy.deepcopy(playerProgress)]
prevPlayerStealBonus = [copy.deepcopy(playerStealBonus)]
prevPlayerInvestmentBonus = [copy.deepcopy(playerInvestmentBonus)]
prevPlayerQuests = [copy.deepcopy(playerQuests)]
prevPlayerWaitingForEvents = [copy.deepcopy(playerWaitingForEvents)]
prevPlayerFrozens = [copy.deepcopy(playerFrozens)]
prevPlayerQuantumNotifications = [copy.deepcopy(playerQuantumNotifications)]
prevItemPrices = [copy.deepcopy(itemPrices)]
prevItemRewards = [copy.deepcopy(itemRewards)]
prevDecorators = [copy.deepcopy(decorators)]
prevPathDecorators = [copy.deepcopy(pathDecorators)]
prevBoards = [copy.deepcopy(board)]
prevQuantumEntanglements = [copy.deepcopy(quantumEntanglements)]

try:
    running = True
    currentPlayer = 1
    os.system('clear')
    while running:
        indent = 0
        print('-'*50)
        print(f'{YELLOW}Player {currentPlayer}{CLEAR}, it is your turn!')
        indent += 1
        print(f'{" "*indent}You curently have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
        indent -= 1
        if len(playerQuests[currentPlayer]) > 0:
            indent += 1
            print(f'{" "*indent}Your current {QUEST_SPACE}quests{CLEAR} are:')
            indent += 1
            for quest in playerQuests[currentPlayer]:
                print(f'{" "*indent}{questTextFromDict(quest, progress=True)}')
            indent -= 2
        evaluateEntanglement()
        #check for waiting events
        for event in playerWaitingForEvents[currentPlayer]:
            if event == 'bad wheel':
                indent += 1
                print(f'{" "*indent}You must spin the {RED}Bad Wheel{CLEAR}.')
                spinTheBadWheel()
                indent -= 1
            if event == 'gamble':
                indent += 1
                print(f'{" "*indent}You must {GAMBLING_SPACE}gamble{CLEAR} half of your {YELLOW}gold ({playerGolds[currentPlayer]//2}){CLEAR}.')
                if playerGolds[currentPlayer]//2 < 1:
                    indent += 1
                    print(f'{" "*indent}Luckily, {GREEN}You only have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}!')
                    indent -= 1
                else:
                    playBlackjack(playerGolds[currentPlayer]//2)
                indent -= 1
        playerWaitingForEvents[currentPlayer] = []
        #ask for item use
        if len(playerInventories[currentPlayer]) > 0:
            if useItem() == 'continue':
                os.system('clear')
                continue
        #if in shadow realm, dont move
        currentSpaceType = board[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']]
        if currentSpaceType == 'shadow realm':
            indent += 1
            print(f'{" "*indent}You must spin the {SHADOW_REALM_SPACE}Shadow Wheel{CLEAR}.')
            spinTheShadowWheel()
            updateQuests('shadowRealm', 1)
            indent -= 1
            #ask for item use
            if running == True:
                if len(playerInventories[currentPlayer]) > 0:
                    if useItem() == 'continue':
                        os.system('clear')
                        continue
        else:
            if playerFrozens[currentPlayer]:
                indent += 1
                print(f'{" "*indent}Unfortunately, you are {CYAN}frozen{CLEAR}! You cannot move this turn.')
                playerFrozens[currentPlayer] = False
                indent -= 1
            else:
                if random.random() < round(playerSpeeds[currentPlayer]%1, 4):
                    moves = math.ceil(playerSpeeds[currentPlayer])
                else:
                    moves = math.floor(playerSpeeds[currentPlayer])
                if moves == 0:
                    indent += 1
                    print(f'{" "*indent}Due to your {RED}immense weight{CLEAR}, you unfortunately cannot move this turn. (your speed is {GYM_SPACE}{playerSpeeds[currentPlayer]}{CLEAR})')
                    indent -= 1
                elif moves >= 2:
                    indent += 1
                    print(f'{" "*indent}Due to your {GYM_SPACE}speed ({playerSpeeds[currentPlayer]}){CLEAR}, you get {GREEN}{moves}{CLEAR} moves this turn!')
                    indent -= 1
                for _ in range(moves):
                    if board[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']] != 'shadow realm':
                        indent += 1
                        #display move options
                        print(f'{" "*indent}Where would you like to move?')
                        possibleMoves = findPossibleMoves(paths, playerPositions[currentPlayer], True, highwayInformation)
                        options = 0
                        indent += 1
                        print(f'{" "*indent}{options}: Stay Here')
                        for move in possibleMoves:
                            options += 1
                            print(f'{" "*indent}{options}: Move {move["direction"]}')
                        indent -= 1
                        choice = askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', options)
                        #evaluate option
                        if int(choice) != 0:
                            allowedToMove = True
                            evaluatePathDecorators()
                            if allowedToMove:
                                #move
                                playerPositions[currentPlayer] = possibleMoves[int(choice)-1]['destination']
                                evaluateDecorators()
                                spaceType = board[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']]
                                evaluateSpaceType(spaceType)
                        indent -= 1
                        #ask for item use
                        timeTravelled = False
                        if running == True:
                            if len(playerInventories[currentPlayer]) > 0:
                                if useItem() == 'continue':
                                    timeTravelled = True
                                    break
        if timeTravelled:
            os.system('clear')
            continue
        reduceTimeOnQuests()
        #change turn order
        print('-'*50)
        if running == True:
            next = input(f'{" "*indent}{TURQUOISE}Press Enter to Continue to Next Player {CLEAR}')
            if next == "SAVE":
                #save to json
                indent += 1
                filename = input(f'{" "*indent}{TURQUOISE}Enter the file name of the save file: {CLEAR}')
                saveToFile(filename)
                indent -= 1
            if next == "LOAD":
                #load from json
                indent += 1
                print(f'{" "*indent}Which file would you like to load?')
                indent += 1
                print(f'{" "*indent}0: Nothing')
                dir = os.listdir('saves')
                for n, filename in enumerate(dir):
                    print(f'{" "*indent}{n+1}: {filename}')
                indent -= 1
                choice = askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', len(dir))
                if choice != '0':
                    with open(f'saves/{dir[int(choice)-1]}', 'r') as f:
                        data = json.load(f)
                    currentPlayer = data["currentPlayer"]
                    board = data["board"]
                    paths = data["paths"]
                    highwayInformation = data["highwayInformation"]
                    decorators = data["decorators"]
                    pathDecorators = data["pathDecorators"]
                    quantumEntanglements = data["quantumEntanglements"]
                    playerPositions = data["playerPositions"]
                    playerInventories = data["playerInventories"]
                    playerGolds = data["playerGolds"]
                    playerSpeeds = data["playerSpeeds"]
                    playerProgress = data["playerProgress"]
                    playerStealBonus = data["playerStealBonus"]
                    playerInvestmentBonus = data["playerInvestmentBonus"]
                    playerQuests = data["playerQuests"]
                    playerWaitingForEvents = data["playerWaitingForEvents"]
                    playerFrozens = data["playerFrozens"]
                    playerQuantumNotifications = data["playerQuantumNotifications"]
                    itemPrices = data["itemPrices"]
                    itemRewards = data["itemRewards"]
                    prevBoards = data["prevBoards"]
                    prevDecorators = data["prevDecorators"]
                    prevPathDecorators = data["prevPathDecorators"]
                    prevQuantumEntanglements = data["prevQuantumEntanglements"]
                    prevPlayerPositions = data["prevPlayerPositions"]
                    prevPlayerInventories = data["prevPlayerInventories"]
                    prevPlayerGolds = data["prevPlayerGolds"]
                    prevPlayerSpeeds = data["prevPlayerSpeeds"]
                    prevPlayerProgress = data["prevPlayerProgress"]
                    prevPlayerStealBonus = data["prevPlayerStealBonus"]
                    prevPlayerInvestmentBonus = data["prevPlayerInvestmentBonus"]
                    prevPlayerQuests = data["prevPlayerQuests"]
                    prevPlayerWaitingForEvents = data["prevPlayerWaitingForEvents"]
                    prevPlayerFrozens = data["prevPlayerFrozens"]
                    prevPlayerQuantumNotifications = data["prevPlayerQuantumNotifications"]
                    prevItemPrices = data["prevItemPrices"]
                    prevItemRewards = data["prevItemRewards"]
                    os.remove(f'saves/{dir[int(choice)-1]}')
                    generateImage(board, paths, quantumEntanglements)
                indent -= 1
            saveToFile('current')
            os.system('clear')
            #store backups
            prevPlayerPositions.append(copy.deepcopy(playerPositions))
            prevPlayerInventories.append(copy.deepcopy(playerInventories))
            prevPlayerGolds.append(copy.deepcopy(playerGolds))
            prevPlayerSpeeds.append(copy.deepcopy(playerSpeeds))
            prevPlayerProgress.append(copy.deepcopy(playerProgress))
            prevPlayerStealBonus.append(copy.deepcopy(playerStealBonus))
            prevPlayerInvestmentBonus.append(copy.deepcopy(playerInvestmentBonus))
            prevPlayerQuests.append(copy.deepcopy(playerQuests))
            prevPlayerWaitingForEvents.append(copy.deepcopy(playerWaitingForEvents))
            prevPlayerFrozens.append(copy.deepcopy(playerFrozens))
            prevPlayerQuantumNotifications.append(copy.deepcopy(playerQuantumNotifications))
            prevItemPrices.append(copy.deepcopy(itemPrices))
            prevItemRewards.append(copy.deepcopy(itemPrices))
            prevDecorators.append(copy.deepcopy(decorators))
            prevPathDecorators.append(copy.deepcopy(pathDecorators))
            prevBoards.append(copy.deepcopy(board))
            prevQuantumEntanglements.append(copy.deepcopy(quantumEntanglements))
            #change turn order
            currentPlayer += 1
            if currentPlayer > NUM_PLAYERS:
                currentPlayer = 1
                #evaluate misc turns
                decoratorsToRemove = []
                goblinsToAdd = []
                flamingosToAdd = []
                for n, row in enumerate(decorators):
                    for m, cell in enumerate(row):
                        for l, decorator in enumerate(cell):
                            if decorator['type'] == 'goblin':
                                possibleMoves = findPossibleMoves(paths, {"row": n, "col": m}, True, highwayInformation)
                                chosenDestination = random.choice(possibleMoves)['destination']
                                decoratorsToRemove.append((n, m, l))
                                print(f'{" "*indent}{RED}Player {decorator["placedBy"]}\'s goblin{CLEAR} has moved!')
                                if board[chosenDestination['row']][chosenDestination['col']] == 'shadow realm':
                                    indent += 1
                                    print(f'{" "*indent}The goblin {RED}got lost{CLEAR} in the {SHADOW_REALM_SPACE}shadow realm{CLEAR} and died.')
                                    indent -= 1
                                else:
                                    goblinsToAdd.append((chosenDestination['row'], chosenDestination['col'], decorator))
                            if decorator['type'] == 'flamingo':
                                shortestPathToFlamingo = findShortestPathToFlamingo(board, paths, {"row": n, "col": m}, highwayInformation)
                                decoratorsToRemove.append((n, m, l))
                                if len(shortestPathToFlamingo) == 1:
                                    print(f'{" "*indent}{RED}Player {decorator["placedBy"]}\'s {FLAMINGO_SPACE}flamingo{CLEAR} has reached the {FLAMINGO_SPACE}flamingo space{CLEAR} and will be despawned.')
                                else:
                                    firstPath = shortestPathToFlamingo[0]
                                    chosenDestination = firstPath['end']
                                    flamingosToAdd.append((chosenDestination['row'], chosenDestination['col'], decorator))
                                    print(f'{" "*indent}{RED}Player {decorator["placedBy"]}\'s {FLAMINGO_SPACE}flamingo{CLEAR} has moved!')
                for decorator in sorted(decoratorsToRemove, reverse=True):
                    decorators[decorator[0]][decorator[1]].pop(decorator[2])
                for goblin in goblinsToAdd:
                    decorators[goblin[0]][goblin[1]].append(goblin[2])
                for flamingo in flamingosToAdd:
                    decorators[flamingo[0]][flamingo[1]].append(flamingo[2])

    print(f'{GREEN}Player {winner} wins!{CLEAR}')
except Exception as e: #i know this is bad practice shut up ok
    print(f'{ERROR}uh oh! something went wrong...{CLEAR}')
    print(f'Creating a save with the name {GREEN}quicksave{CLEAR}...')
    saveToFile('quicksave')
    print(traceback.format_exc())