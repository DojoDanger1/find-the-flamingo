import random
import time
import os
import copy
from PIL import Image, ImageDraw, ImageColor

#bord paramaters
GRID_SIZE = 7
PERCENTAGE_SQUARES = 0.7
PERCENTAGE_PATHS = 0.8
PROBABILITY_ONE_WAY = 0.1

#game settings
NUM_PLAYERS = 3
STARTING_GOLD = 3
CHANCE_OF_INFLATION = 0.5
BLACKJACK_TARGET = 31
BLACKJACK_DEALER_CAUTION = 5

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

def fillSpaces(board, fillWith, howMany):
    linearBoard = sum(board, [])
    emptyIndexes = [n for n, x in enumerate(linearBoard) if x == 'empty']
    chosenSpaces = random.sample(emptyIndexes, howMany)
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
    #initialise board
    board = []
    decorators = []
    for _ in range(GRID_SIZE):
        board.append([None]*GRID_SIZE)
        decoratorsRow = []
        for _ in range(GRID_SIZE):
            decoratorsRow.append([])
        decorators.append(decoratorsRow)
    #add empty spaces
    numEmpties = 0
    for n, row in enumerate(board):
        for m, _ in enumerate(row):
            if random.random() < PERCENTAGE_SQUARES:
                board[n][m] = 'empty'
                numEmpties += 1
    #add home space
    midpoint = GRID_SIZE // 2
    board[midpoint][midpoint] = 'home'
    #add other spaces
    board = fillSpaces(board, 'shadow realm', 1)
    board = fillSpaces(board, 'flamingo', 1)
    board = fillSpaces(board, 'good', numEmpties // 10)
    board = fillSpaces(board, 'bad', numEmpties // 10)
    board = fillSpaces(board, 'shop', numEmpties // 8)
    board = fillSpaces(board, 'teleport', numEmpties // 20)
    board = fillSpaces(board, 'gambling', numEmpties // 20)
    board = fillSpaces(board, 'timewarp', numEmpties // 20)
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
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            pos = {"row": row, "col": col}
            if board[row][col] not in [None, 'home', 'flamingo', 'shadow realm']:
                #down
                if random.random() < PERCENTAGE_PATHS:
                    possiblePaths = [path for path in findPossiblePaths(board, pos, random.random() < PROBABILITY_ONE_WAY, ['down']) if path['start'] != homePos and path['start'] != flamingoPos and path['start'] != shadowRealmPos]
                    if len(possiblePaths) != 0:
                        if possiblePaths[0]['oneWay'] == True:
                            newPossiblePaths = [possiblePaths[0], {"start": possiblePaths[0]['end'], "end": possiblePaths[0]['start'], "oneWay": True}]
                            paths.append(random.choice(newPossiblePaths))
                        else:
                            paths += possiblePaths
                #right
                if random.random() < PERCENTAGE_PATHS:
                    possiblePaths = [path for path in findPossiblePaths(board, pos, random.random() < PROBABILITY_ONE_WAY, ['right']) if path['start'] != homePos and path['start'] != flamingoPos and path['start'] != shadowRealmPos]
                    if len(possiblePaths) != 0:
                        if possiblePaths[0]['oneWay'] == True:
                            newPossiblePaths = [possiblePaths[0], {"start": possiblePaths[0]['end'], "end": possiblePaths[0]['start'], "oneWay": True}]
                            paths.append(random.choice(newPossiblePaths))
                        else:
                            paths += possiblePaths
    #add highways
    for _ in range((GRID_SIZE // 2)):
        paths.append(generateAValidHighway(board, paths))
    #generate additional highways to shadow realm
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
    highwayInformation = decideHighwayInformation(board, paths)
    #keep generating paths until game is possible
    possible = False
    while not possible:
        shortestPath = findShortestPathToFlamingo(board, paths, homePos, highwayInformation)
        if shortestPath != 'impossible':
            possible = True
        else:
            paths.append(generateAValidHighway(board, paths))
            highwayInformation = decideHighwayInformation(board, paths)
    #return
    return board, paths, decorators

def generateImage(board, paths):
    width = GRID_SIZE*100
    height = GRID_SIZE*100

    mainImg = Image.new('RGBA', (width,height), ImageColor.getcolor('#ffffff', 'RGBA'))
    draw = ImageDraw.Draw(mainImg)

    for n, path in enumerate(paths):
        if path['oneWay']:
            draw.line((path['start']['col']*100+50, path['start']['row']*100+50, path['end']['col']*100+50, path['end']['row']*100+50), fill=ImageColor.getcolor('#696969', 'RGBA'), width=10)
        elif path['start']['col'] != path['end']['col'] and path['start']['row'] != path['end']['row']:
            draw.line((path['start']['col']*100+50, path['start']['row']*100+50, path['end']['col']*100+50, path['end']['row']*100+50), fill=ImageColor.getcolor('#0000ff', 'RGBA'), width=10)
        else:
            draw.line((path['start']['col']*100+50, path['start']['row']*100+50, path['end']['col']*100+50, path['end']['row']*100+50), fill=ImageColor.getcolor('#000000', 'RGBA'), width=10)
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
            if cell != None:
                draw.rectangle((m*100+15, n*100+15, m*100+85, n*100+85), fill=ImageColor.getcolor(colour, 'RGBA'), outline=ImageColor.getcolor('#000000', 'RGBA'), width=5)
        
    mainImg.save(f'image.png', 'PNG')

def decideHighwayInformation(board, paths):
    highways = [path for path in paths if path['start']['row'] != path['end']['row'] and path['start']['col'] != path['end']['col']]
    highwayInformation = []
    for highway in highways:
        thisHighwaysInformation = []
        #print(f'highway: {highway}')
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
    #pprint(possiblePaths)
    #pprint(board)
    #pprint(paths)
    for (n, path) in possiblePaths:
        if path['start'] == position:
            destination = path['end']
        else:
            destination = path['start']
        #print(f'path: {path}, position: {position}')
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

def askOptions(prompt, numOptions):
    option = input(prompt)
    if option == '':
        option = '0'
    try:
        option = int(option)
        if option < 0:
            print(f'{ERROR}Invalid Answer! Must be a number from 0 to {numOptions}{CLEAR}')
            option = askOptions(prompt, numOptions)
        elif option > numOptions:
            print(f'{ERROR}Invalid Answer! Must be a number from 0 to {numOptions}{CLEAR}')
            option = askOptions(prompt, numOptions)
    except ValueError:
        print(f'{ERROR}Invalid Answer! Must be a number from 0 to {numOptions}{CLEAR}')
        option = askOptions(prompt, numOptions)
    return str(option)

def askForPlayer(prompt, includeSelf):
    option = input(prompt)
    try:
        option = int(option)
        if option < 1:
            print(f'{ERROR}Invalid Answer! Must be a number from 1 to {NUM_PLAYERS}{CLEAR}')
            option = askForPlayer(prompt, includeSelf)
        elif option > NUM_PLAYERS:
            print(f'{ERROR}Invalid Answer! Must be a number from 1 to {NUM_PLAYERS}{CLEAR}')
            option = askForPlayer(prompt, includeSelf)
        if not includeSelf:
            if option == currentPlayer:
                print(f'{ERROR}Invalid Answer! You cannot pick yourself!{CLEAR}')
                option = askForPlayer(prompt, includeSelf)
    except ValueError:
        print(f'{ERROR}Invalid Answer! Must be a number from 1 to {NUM_PLAYERS}{CLEAR}')
        option = askForPlayer(prompt, includeSelf)
    return str(option)
    

def spinTheBadWheel():
    options = [
        f'You have been sent to the {SHADOW_REALM_SPACE}Shadow Realm{CLEAR}.',
        f'You will be {TELEPORT_SPACE}teleported{CLEAR} to a random space.',
        f'You {TELEPORT_SPACE}swap places{CLEAR} with a random player.',
        f'You must give away {YELLOW}all gold{CLEAR}. {YELLOW}({playerGolds[currentPlayer]}){CLEAR}',
        f'You must return to the {HOME_SPACE}Home{CLEAR} space.',
        f'You must give away {YELLOW}3 gold{CLEAR}.',
        f'You must give away {CYAN}an item{CLEAR}.',
        f'You must spin the {RED}Bad Wheel{CLEAR} twice more.',
        f'You can now spin {GREEN}Good Wheel{CLEAR}!'
    ]
    print('')
    for _ in range(20):
        print(f'\033[A                                          \033[A')
        print(f'{random.choice(options)}')
        time.sleep(0.02)
    for _ in range(5):
        print(f'\033[A                                          \033[A')
        print(f'{random.choice(options)}')
        time.sleep(0.05)
    for _ in range(2):
        print(f'\033[A                                          \033[A')
        print(f'{random.choice(options)}')
        time.sleep(0.1)
    print('\033[A                                          \033[A')
    result =  random.choice(options)
    print(result)
    time.sleep(1)
    if result == f'You have been sent to the {SHADOW_REALM_SPACE}Shadow Realm{CLEAR}.':
        playerPositions[currentPlayer] = findShadowRealm(board)
    if result == f'You will be {TELEPORT_SPACE}teleported{CLEAR} to a random space.':
        playerPositions[currentPlayer] = selectRandomSpace(board)
    if result == f'You {TELEPORT_SPACE}swap places{CLEAR} with a random player.':
        players = list(range(1,NUM_PLAYERS+1))
        players.remove(currentPlayer)
        player = random.choice(players)
        temp = playerPositions[player]
        playerPositions[player] = playerPositions[currentPlayer]
        playerPositions[playecurrentPlayerr2] = temp
    if result == f'You must give away {YELLOW}all gold{CLEAR}. {YELLOW}({playerGolds[currentPlayer]}){CLEAR}':
        player = int(askForPlayer(f'{TURQUOISE}Enter the player who you will give your {YELLOW}gold{TURQUOISE} to: (1-{NUM_PLAYERS}){CLEAR} ', False))
        playerGolds[player] += playerGolds[currentPlayer]
        playerGolds[currentPlayer] = 0
        print(f'You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR} and {RED}Player {player}{CLEAR} now has {YELLOW}{playerGolds[player]} gold{CLEAR}.')
    if result == f'You must return to the {HOME_SPACE}Home{CLEAR} space.':
        playerPositions[currentPlayer] = {"row": GRID_SIZE // 2, "col": GRID_SIZE // 2}
    if result == f'You must give away {YELLOW}3 gold{CLEAR}.':
        player = int(askForPlayer(f'{TURQUOISE}Enter the player who you will give {YELLOW}3 gold{TURQUOISE} to: (1-{NUM_PLAYERS}){CLEAR} ', False))
        playerGolds[player] += 3
        playerGolds[currentPlayer] -= 3
        print(f'You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR} and {RED}Player {player}{CLEAR} now has {YELLOW}{playerGolds[player]} gold{CLEAR}.')
    if result == f'You must give away {CYAN}an item{CLEAR}.':
        if len(playerInventories[currentPlayer]) == 0:
            print(f'Luckily, {GREEN}You don\'t have any items{CLEAR}!')
        else:
            print(f'Which {CYAN}item{CLEAR} will you give away?')
            options = 0
            for item in playerInventories[currentPlayer]:
                options += 1
                print(f'{options}: {CYAN}{item.title()}{CLEAR} - {itemDescriptions[item]}')
            valid = False
            while not valid:
                choice = askOptions(f'{TURQUOISE}Enter your Choice:{CLEAR} ', options)
                if choice != '0':
                    valid = True
            item = playerInventories[currentPlayer][int(choice)-1]
            playerInventories[currentPlayer].remove(item)
            player = int(askForPlayer(f'{TURQUOISE}Enter the player who you will give the {CYAN}{item.title()}{TURQUOISE} to: (1-{NUM_PLAYERS}){CLEAR} ', False))
            playerInventories[player].append(item)
    if result == f'You must spin the {RED}Bad Wheel{CLEAR} twice more.':
        for _ in range(2):
            spinTheBadWheel()
    if result == f'You can now spin {GREEN}Good Wheel{CLEAR}!':
        spinTheGoodWheel()

def spinTheGoodWheel():
    options = [
        f'You can {CYAN}send a player{CLEAR} to the {SHADOW_REALM_SPACE}Shadow Realm{CLEAR}!',
        f'You gain {YELLOW}3 gold{CLEAR}!',
        f'You gain {YELLOW}2 gold{CLEAR}!',
        f'You must spin the {RED}Bad Wheel{CLEAR}.',
        f'You have {YELLOW}doubled{CLEAR} your gold!',
        f'You gain {YELLOW}5 gold{CLEAR}',
        f'You gain {CYAN}a compass{CLEAR}'
    ]
    print('')
    for _ in range(20):
        print(f'\033[A                                          \033[A')
        print(f'{random.choice(options)}')
        time.sleep(0.02)
    for _ in range(5):
        print(f'\033[A                                          \033[A')
        print(f'{random.choice(options)}')
        time.sleep(0.05)
    for _ in range(2):
        print(f'\033[A                                          \033[A')
        print(f'{random.choice(options)}')
        time.sleep(0.1)
    print('\033[A                                          \033[A')
    result =  random.choice(options)
    print(result)
    time.sleep(1)
    if result == f'You can {CYAN}send a player{CLEAR} to the {SHADOW_REALM_SPACE}Shadow Realm{CLEAR}!':
        player = int(askForPlayer(f'{TURQUOISE}Enter the player who will be sent to the {SHADOW_REALM_SPACE}Shadow Realm{TURQUOISE}: (1-{NUM_PLAYERS}){CLEAR} ', True))
        playerPositions[player] = findShadowRealm(board)
    if result == f'You gain {YELLOW}3 gold{CLEAR}!':
        playerGolds[currentPlayer] += 3
        print(f'You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
    if result == f'You gain {YELLOW}2 gold{CLEAR}!':
        playerGolds[currentPlayer] += 2
        print(f'You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
    if result == f'You must spin the {RED}Bad Wheel{CLEAR}.':
        spinTheBadWheel()
    if result == f'You have {YELLOW}doubled{CLEAR} your gold!':
        playerGolds[currentPlayer] *= 2
        print(f'You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
    if result == f'You gain {YELLOW}5 gold{CLEAR}':
        playerGolds[currentPlayer] += 5
        print(f'You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
    if result == f'You gain {CYAN}a compass{CLEAR}':
        playerInventories[currentPlayer].append('compass')

def spinTheShadowWheel():
    options = [
        f'You must {CYAN}Invite a Friend{CLEAR} to the {SHADOW_REALM_SPACE}Shadow Realm{CLEAR}!',
        f'You can now spin {GREEN}Good Wheel{CLEAR}!',
        f'You must return to the {HOME_SPACE}Home{CLEAR} space.',
        'Nothing happens.',
        f'All other players gain {YELLOW}2 gold{CLEAR}',
        f'You loose {YELLOW}1 gold{CLEAR}',
        f'You must spin the {RED}Bad Wheel{CLEAR}.'
    ]
    print('')
    for _ in range(20):
        print(f'\033[A                                                     \033[A')
        print(f'{random.choice(options)}')
        time.sleep(0.02)
    for _ in range(5):
        print(f'\033[A                                                     \033[A')
        print(f'{random.choice(options)}')
        time.sleep(0.05)
    for _ in range(2):
        print(f'\033[A                                                     \033[A')
        print(f'{random.choice(options)}')
        time.sleep(0.1)
    print(f'\033[A                                                     \033[A')
    result =  random.choice(options)
    print(result)
    time.sleep(1)
    if result == f'You must {CYAN}Invite a Friend{CLEAR} to the {SHADOW_REALM_SPACE}Shadow Realm{CLEAR}!':
        player = int(askForPlayer(f'{TURQUOISE}Enter the player who will be sent to the {SHADOW_REALM_SPACE}Shadow Realm{TURQUOISE}: (1-{NUM_PLAYERS}){CLEAR} ', False))
        playerPositions[player] = findShadowRealm(board)
    if result == f'You can now spin {GREEN}Good Wheel{CLEAR}!':
        spinTheGoodWheel()
    if result == f'You must return to the {HOME_SPACE}Home{CLEAR} space.':
        playerPositions[currentPlayer] = {"row": GRID_SIZE // 2, "col": GRID_SIZE // 2}
    if result == f'All other players gain {YELLOW}2 gold{CLEAR}':
        for player in range(1, NUM_PLAYERS+1):
            if player != currentPlayer:
                playerGolds[player] += 2
                print(f'{RED}Player {player}{CLEAR} now has {YELLOW}{playerGolds[player]} gold{CLEAR}.')
    if result == f'You loose {YELLOW}1 gold{CLEAR}':
        playerGolds[currentPlayer] -= 1
        print(f'You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
    if result == f'You must spin the {RED}Bad Wheel{CLEAR}.':
        spinTheBadWheel()

def goToTheShop():
    for _ in range(3):
        if playerGolds[currentPlayer] < min(itemPrices.values()):
            break
        print(f'You have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}. What would you like to buy?')
        options = 0
        print(f'{options}: {CYAN}Nothing{CLEAR}')
        for item in itemDescriptions.keys():
            options += 1
            if itemPrices[item] <= playerGolds[currentPlayer]:
                print(f'{options}: {CYAN}{item.title()}{CLEAR} - {YELLOW}{itemPrices[item]} gold{CLEAR} - {itemDescriptions[item]}')
            else:
                print(f'{GRAY}{options}: {item.title()} - {itemPrices[item]} gold{CLEAR} - {itemDescriptions[item]}')
        valid = False
        while not valid:
            choice = askOptions(f'{TURQUOISE}Enter your Choice:{CLEAR} ', options)
            if choice == '0':
                valid = True
            else:
                item = list(itemDescriptions.keys())[int(choice)-1]
                price = itemPrices[item]
                if price > playerGolds[currentPlayer]:
                    print(f'{ERROR}You do not have enough gold! Please select a different item')
                else:
                    valid = True
        if choice == '0':
            break
        else:
            playerGolds[currentPlayer] -= price
            playerInventories[currentPlayer].append(item)
            if random.random() < CHANCE_OF_INFLATION:
                itemPrices[item] += 1

def useItem():
    global playerPositions
    global playerInventories
    global playerGolds
    global playerWaitingForWheelSpins
    global itemPrices
    global decorators
    done = False
    while not done:
        if len(playerInventories[currentPlayer]) == 0:
            done = True
        else:
            print(f'Would you like to use an {CYAN}item{CLEAR}?')
            print('0: No')
            print('1: Yes')
            choice = askOptions(f'{TURQUOISE}Enter your Choice:{CLEAR} ', 1)
            if choice == '0':
                done = True
            else:
                print(f'Which {CYAN}item{CLEAR} would you like to use?')
                options = 0
                print(f'{options}: Nothing')
                for item in playerInventories[currentPlayer]:
                    options += 1
                    print(f'{options}: {CYAN}{item.title()}{CLEAR} - {itemDescriptions[item]}')
                choice = askOptions(f'{TURQUOISE}Enter your Choice:{CLEAR} ', options)
                if int(choice) != 0:
                    item = playerInventories[currentPlayer][int(choice)-1]
                    playerInventories[currentPlayer].remove(item)
                    if item == 'compass':
                        if board[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']] == 'shadow realm':
                            print(f'The compass is {RED}useless{CLEAR} in the {SHADOW_REALM_SPACE}shadow realm{CLEAR}. No information was given')
                        else:
                            possibleMoves = findPossibleMoves(paths, playerPositions[currentPlayer], True, highwayInformation)
                            print(f'Here is all of the information about the {ORANGE}Adjacent Spaces{CLEAR}:')
                            for move in possibleMoves:
                                destinationSpaceType = board[move['destination']['row']][move['destination']['col']]
                                message = f'If you move {GREEN}{move["direction"]}{CLEAR}, you will land on {grammatiseSpaceType(destinationSpaceType)}.'
                                for player, playerPosition in enumerate(playerPositions):
                                    if playerPosition == move['destination']:
                                        message += f' {RED}Player {player}{CLEAR} is on this space.'
                                for decorator in decorators[move['destination']['row']][move['destination']['col']]:
                                    message += f' There is also a {CYAN}{decorator["type"]}{CLEAR} on this space.'
                                print(message)
                    if item == 'swap':
                        player1 = int(askForPlayer(f'{TURQUOISE}Enter the first player to be {ORANGE}swapped{TURQUOISE}: (1-{NUM_PLAYERS}){CLEAR} ', True))
                        valid = False
                        while not valid:
                            player2 = int(askForPlayer(f'{TURQUOISE}Enter the second player to be {ORANGE}swapped{TURQUOISE}: (1-{NUM_PLAYERS}){CLEAR} ', True))
                            if player2 == player1:
                                print(f'{ERROR}The 2 players cannot be the same! Please try again{CLEAR}')
                            else:
                                valid = True
                        temp = playerPositions[player1]
                        playerPositions[player1] = playerPositions[player2]
                        playerPositions[player2] = temp
                    if item == 'trap':
                        decorators[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']].append({"type": 'trap', "placedBy": currentPlayer})
                        print(f'Successfully placed a trap on {GREEN}This Space{CLEAR}!')
                    if item == 'gold potion':
                        possibleMoves = findPossibleMoves(paths, playerPositions[currentPlayer], True, highwayInformation)
                        chosenSpace = random.choice(possibleMoves)['destination']
                        decorators[chosenSpace['row']][chosenSpace['col']].append({"type": 'gold', "placedBy": currentPlayer})
                        print(f'Successfully placed 3 gold on a random {ORANGE}Adjacent Space{CLEAR}!')
                    if item == 'knife':
                        playersOnCurrentSpot = [n for n, pos in enumerate(playerPositions) if pos == playerPositions[currentPlayer] and n != currentPlayer]
                        if len(playersOnCurrentSpot) == 0:
                            print(f'Unfortunately, {RED}No one{CLEAR} shares a space with you.')
                        else:
                            player = random.choice(playersOnCurrentSpot)
                            playerGolds[player] -= 4
                            playerGolds[currentPlayer] += 4
                            print(f'Stolen {YELLOW}4 gold{CLEAR} from {GREEN}Player {player}{CLEAR}')
                            print(f'You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR} and {RED}Player {player}{CLEAR} now has {YELLOW}{playerGolds[player]} gold{CLEAR}.')
                    if item == 'red potion':
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
                                print(f'To get closer to the {FLAMINGO_SPACE}flamigo{CLEAR}, you should go {GREEN}{move["direction"]}{CLEAR}.')
                    if item == 'goblin':
                        decorators[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']].append({"type": 'goblin', "placedBy": currentPlayer})
                        print(f'Successfully placed a goblin on {GREEN}This Space{CLEAR}!')
                    if item == 'wand':
                        player = int(askForPlayer(f'{TURQUOISE}Enter the player who will spin the {RED}Bad Wheel{TURQUOISE} at the start of their next turn: (1-{NUM_PLAYERS}){CLEAR} ', True))
                        playerWaitingForWheelSpins[player] = True
                    if item == 'time machine':
                        if len(prevPlayerPositions) >= 4:
                            playerPositions = prevPlayerPositions[-4]
                            playerInventories = prevPlayerInventories[-4]
                            playerGolds = prevPlayerGolds[-4]
                            playerWaitingForWheelSpins = prevPlayerWaitingForWheelSpins[-4]
                            itemPrices = prevItemPrices[-4]
                            decorators = prevDecorators[-4]
                            for _ in range(3):
                                prevPlayerPositions.pop(-1)
                                prevPlayerInventories.pop(-1)
                                prevPlayerGolds.pop(-1)
                                prevPlayerWaitingForWheelSpins.pop(-1)
                                prevItemPrices.pop(-1)
                                prevDecorators.pop(-1)
                            if len(playerInventories[currentPlayer]) >= int(choice):
                                if playerInventories[currentPlayer][int(choice)-1] == 'time machine':
                                    playerInventories[currentPlayer].remove(item)
                            return 'continue'
                        else:
                            print(f'{RED}Unfortunately, the game has not existed long enough to rewind 1 round.{CLEAR}')
                    return 'dont continue'

def playBlackjack():
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
        if person == 'dealer':
            print(f'{CYAN}The Dealer\'s hand is:{CLEAR}')
            for card in dealerhand:
                print(getCardColour(card))
            print(f'Dealer hand value is{getHandValueColour(dealerhandValue)}\n')
        if person == 'player':
            print(f'{CYAN}Your hand is:{CLEAR}')
            for card in hand:
                print(getCardColour(card))
            print(f'Your hand value is{getHandValueColour(handValue)}\n')
    
    def sayMostRecentCard():
        print(f'{CYAN}You drew a: {getCardColour(hand[-1])}{CLEAR}')
        print(f'Your hand value is now{getHandValueColour(handValue)}\n')

    suits = ['Hearts', 'Diamonds', 'Spades', 'Clubs']
    cards = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']

    bet = 0
    print(f'How much would you like to bet? (You have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR})')
    while bet == 0:
        bet = int(askOptions(f'{TURQUOISE}Enter your choice:{CLEAR} ', playerGolds[currentPlayer]))
        if bet == 0:
            print(f'{ERROR}You cannot bet 0!{CLEAR}')

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
    print(f'{ORANGE}The dealer has {dealercardAmount} cards{CLEAR}')
    print(f'One of the dealer\'s cards is: {getCardColour(dealerShownCard)}{CLEAR}\n')
    
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
            print(f'{GREEN}You scored Blackjack!{CLEAR}')
            input('Press Enter to see the results')
        else:
            print(f'Would you like to {GREEN}draw{CLEAR}?')
            print('0: Yes')
            print('1: No')
            draw = askOptions(f'{TURQUOISE}Enter your choice:{CLEAR} ', 1)
            if draw == '0':
                #draw
                cardAmount += 1
                globals()[f'card{cardAmount}'] = f'{random.choice(cards)} of {random.choice(suits)}'
                if 'Ace' in globals()[f'card{cardAmount}']:
                    acesInHand += 1
                globals()[f'card{cardAmount}Value'] = findValue(globals()[f'card{cardAmount}'])
                hand.append(globals()[f'card{cardAmount}'])
                handValue += globals()[f'card{cardAmount}Value']
                print('')
                if handValue > BLACKJACK_TARGET:
                    if acesInHand != 0:
                        handValue -= 10
                        acesInHand -= 1
                    else:
                        doneDrawing = True
                        youBusted = True
                        sayMostRecentCard()
                        print(f'{ORANGE}You busted!{CLEAR}')
                        time.sleep(0.5)
                elif handValue == BLACKJACK_TARGET:
                    doneDrawing = True
                    youBusted = False
                    sayMostRecentCard()
                    print(f'{GREEN}You scored Blackjack!{CLEAR}')
                    time.sleep(0.5)
            elif draw == '1':
                doneDrawing = True
                if handValue <= BLACKJACK_TARGET:
                    youBusted = False
    
    print(f'{CLEAR}\n---RESULTS---\n')
    sayHand('player')
    sayHand('dealer')

    if youBusted == True and dealerBusted == True:
        print(f'{YELLOW}Both of you busted, so no one wins!{CLEAR}')
    elif youBusted == True and dealerBusted == False:
        print(f'{RED}You busted! That means the dealer wins!{CLEAR}')
        playerGolds[currentPlayer] -= bet
        print(f'You lost {YELLOW}{bet} gold{CLEAR}!')
    elif youBusted == False and dealerBusted == True:
        print(f'{GREEN}The dealer busted! That means you win!{CLEAR}')
        playerGolds[currentPlayer] += bet
        print(f'You won {YELLOW}{bet} gold{CLEAR}!')
    elif youBusted == False and dealerBusted == False:
        print('No one busted, so the person with the highest number wins...')
        if handValue > dealerhandValue:
            print(f'{GREEN}You win!{CLEAR}')
            playerGolds[currentPlayer] += bet
            print(f'You won {YELLOW}{bet} gold{CLEAR}!')
        else:
            print(f'{RED}Dealer wins!{CLEAR}')
            playerGolds[currentPlayer] -= bet
            print(f'You lost {YELLOW}{bet} gold{CLEAR}!')
    
    print(f'You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')

def selectRandomSpace(board):
    validSpace = False
    while not validSpace:
        row = random.randint(0, GRID_SIZE-1)
        col = random.randint(0, GRID_SIZE-1)
        if board[row][col] not in [None, 'flamingo']:
            space = {"row": row, "col": col}
            validSpace = True
    return space

def grammatiseSpaceType(spaceType):
    if spaceType == 'empty':
        return f'an {EMPTY_SPACE}empty{CLEAR} space'
    if spaceType == 'flamingo':
        return f'the {FLAMINGO_SPACE}flamingo{CLEAR} space'
    if spaceType == 'home':
        return f'the {HOME_SPACE}home{CLEAR} space'
    if spaceType == 'shadow realm':
        return f'the {SHADOW_REALM_SPACE}shadow realm{CLEAR} space'
    if spaceType == 'good':
        return f'a {GOOD_SPACE}good{CLEAR} space'
    if spaceType == 'bad':
        return f'a {BAD_SPACE}bad{CLEAR} space'
    if spaceType == 'shop':
        return f'a {SHOP_SPACE}shop{CLEAR} space'
    if spaceType == 'teleport':
        return f'a {TELEPORT_SPACE}teleport{CLEAR} space'
    if spaceType == 'gambling':
        return f'a {GAMBLING_SPACE}gambling{CLEAR} space'
    if spaceType == 'timewarp':
        return f'a {TIMEWARP_SPACE}time warp{CLEAR} space'

board, paths, decorators = generateBoard()
generateImage(board, paths)
highwayInformation = decideHighwayInformation(board, paths)

itemDescriptions = {
    "compass": f'See all {ORANGE}adjacent{CLEAR} spaces and players',
    "swap": f'{TELEPORT_SPACE}Swap{CLEAR} the positions of 2 chosen players',
    "trap": f'Sets a {RED}trap{CLEAR} that will steal {YELLOW}2 gold{CLEAR} when landed on',
    "gold potion": f'Places {YELLOW}3 gold{CLEAR} on a random {ORANGE}adjacent{CLEAR} space',
    "knife": f'Steal {YELLOW}4 gold{CLEAR} from another player if they are on the same space as you',
    "red potion": f'Tells you where to go to get closer to the {FLAMINGO_SPACE}flamingo space{CLEAR}.',
    "goblin": f'Randomly moves around the map. If a player lands on a space with your goblin, you steal {YELLOW}1 gold{CLEAR}.',
    "wand": f'Make a player spin the {RED}Bad Wheel{CLEAR} at the start of their next turn',
    "time machine": f'{TIMEWARP_SPACE}Rewind time{CLEAR} to the start of your {ORANGE}previous turn{CLEAR}.'
}

itemPrices = {
    "compass": 2,
    "swap": 2,
    "trap": 2,
    "gold potion": 1,
    "knife": 2,
    "red potion": 2,
    "goblin": 4,
    "wand": 2,
    "time machine": 3
}

playerPositions = [None]
playerInventories = [None]
playerGolds = [None]
playerWaitingForWheelSpins = [None]
for _ in range(NUM_PLAYERS):
    playerPositions.append({"row": GRID_SIZE // 2, "col": GRID_SIZE // 2})
    playerInventories.append([])
    playerGolds.append(STARTING_GOLD)
    playerWaitingForWheelSpins.append(False)

prevPlayerPositions = [copy.copy(playerPositions)]
prevPlayerInventories = [copy.copy(playerInventories)]
prevPlayerGolds = [copy.copy(playerGolds)]
prevPlayerWaitingForWheelSpins = [copy.copy(playerWaitingForWheelSpins)]
prevItemPrices = [copy.copy(itemPrices)]
prevDecorators = [copy.copy(decorators)]

running = True
currentPlayer = 1
os.system('clear')
while running:
    print('-'*50)
    print(f'{YELLOW}Player {currentPlayer}{CLEAR}, it is your turn!')
    #check for waiting for wheel spins
    if playerWaitingForWheelSpins[currentPlayer]:
        print(f'You must spin the {RED}Bad Wheel{CLEAR}.')
        playerWaitingForWheelSpins[currentPlayer] = False
        spinTheBadWheel()
    #ask for item use
    if len(playerInventories[currentPlayer]) > 0:
        if useItem() == 'continue':
            os.system('clear')
            continue
    #if in shadow realm, dont move
    currentSpaceType = board[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']]
    if currentSpaceType == 'shadow realm':
        print(f'You must spin the {SHADOW_REALM_SPACE}Shadow Wheel{CLEAR}.')
        spinTheShadowWheel()
    else:
        #display move options
        print('Where would you like to move?')
        possibleMoves = findPossibleMoves(paths, playerPositions[currentPlayer], True, highwayInformation)
        options = 0
        print(f'{options}: Stay Here')
        for move in possibleMoves:
            options += 1
            print(f'{options}: Move {move["direction"]}')
        choice = askOptions(f'{TURQUOISE}Enter your Choice:{CLEAR} ', options)
        #evaluate option
        if int(choice) != 0:
            #move
            playerPositions[currentPlayer] = possibleMoves[int(choice)-1]['destination']
        #evaluate decorators
        decoratorsToRemove = []
        goblinsToAdd = []
        for n, decorator in enumerate(decorators[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']]):
            if decorator['type'] == 'trap' and decorator['placedBy'] != currentPlayer:
                print(f'Unfortunately, you landed on {RED}Player {decorator["placedBy"]}\'s trap{CLEAR}!')
                print(f'You must give them {YELLOW}2 gold{CLEAR}.')
                playerGolds[currentPlayer] -= 2
                playerGolds[decorator['placedBy']] += 2
                print(f'You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR} and {RED}Player {decorator["placedBy"]}{CLEAR} now has {YELLOW}{playerGolds[decorator["placedBy"]]} gold{CLEAR}.')
                time.sleep(0.5)
            if decorator['type'] == 'gold':
                print(f'There is {YELLOW}3 gold{CLEAR} on this space!')
                print(f'You gain {YELLOW}3 gold{CLEAR}!')
                print(f'You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
                playerGolds[currentPlayer] += 3
                decoratorsToRemove.append(n)
                time.sleep(0.5)
            if decorator['type'] == 'goblin' and decorator['placedBy'] != currentPlayer:
                print(f'Unfortunately, you have ran into {RED}Player {decorator["placedBy"]}\'s goblin{CLEAR}!')
                print(f'It steals {YELLOW}1 gold{CLEAR} for {RED}Player {decorator["placedBy"]}{CLEAR} and runs away {GREEN}1 space{CLEAR}.')
                playerGolds[currentPlayer] -= 1
                playerGolds[decorator['placedBy']] += 1
                print(f'You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR} and {RED}Player {decorator["placedBy"]}{CLEAR} now has {YELLOW}{playerGolds[decorator["placedBy"]]} gold{CLEAR}.')
                possibleMoves = findPossibleMoves(paths, {"row": playerPositions[currentPlayer]['row'], "col": playerPositions[currentPlayer]['col']}, True, highwayInformation)
                chosenDestination = random.choice(possibleMoves)['destination']
                decoratorsToRemove.append(n)
                goblinsToAdd.append((chosenDestination['row'], chosenDestination['col'], decorator))
                print(f'{RED}Player {decorator["placedBy"]}\'s goblin{CLEAR} has moved!')
                time.sleep(0.5)
        for decorator in sorted(decoratorsToRemove, reverse=True):
            decorators[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']].pop(decorator)
        for goblin in goblinsToAdd:
            decorators[goblin[0]][goblin[1]].append(goblin[2])
        if int(choice) != 0:
            #evaluate space type
            spaceType = board[playerPositions[currentPlayer]['row']][playerPositions[currentPlayer]['col']]
            if spaceType == 'empty':
                print(f'You landed on {grammatiseSpaceType(spaceType)}.')
                print('Nothing Happens.')
            if spaceType == 'flamingo':
                print(f'You landed on {grammatiseSpaceType(spaceType)}!')
                print(f'You {GREEN}win the game{CLEAR}!')
                running = False
                winner = currentPlayer
            if spaceType == 'home':
                print(f'You landed on {grammatiseSpaceType(spaceType)}.')
                print(f'You gain {YELLOW}1 gold{CLEAR}!')
                playerGolds[currentPlayer] += 1
                print(f'You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
            if spaceType == 'shadow realm':
                print(f'You landed on {grammatiseSpaceType(spaceType)}.')
                print(f'You are stuck here until you escape. Instead of moving, you will spin the {SHADOW_REALM_SPACE}Shadow Wheel{CLEAR}.')
            if spaceType == 'good':
                print(f'You landed on {grammatiseSpaceType(spaceType)}!')
                print(f'You get to spin the {GREEN}Good Wheel{CLEAR}!')
                spinTheGoodWheel()
            if spaceType == 'bad':
                print(f'You landed on {grammatiseSpaceType(spaceType)}.')
                print(f'You get to spin the {RED}Bad Wheel{CLEAR}.')
                spinTheBadWheel()
            if spaceType == 'shop':
                print(f'You landed on {grammatiseSpaceType(spaceType)}!')
                print(f'You get to buy from the {SHOP_SPACE}shop{CLEAR}!')
                if playerGolds[currentPlayer] < min(itemPrices.values()):
                    print(f'You don\'t have enough {YELLOW}gold{CLEAR} to buy anything! (You have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR})')
                else:
                    goToTheShop()
            if spaceType == 'teleport':
                print(f'You landed on {grammatiseSpaceType(spaceType)}.')
                print(f'You get to choose a player to randomly {TELEPORT_SPACE}teleport{CLEAR}!')
                player = int(askForPlayer(f'{TURQUOISE}Enter the player who will be randomly teleported: (1-{NUM_PLAYERS}){CLEAR} ', False))
                playerPositions[player] = selectRandomSpace(board)
            if spaceType == 'gambling':
                print(f'You landed on {grammatiseSpaceType(spaceType)}.')
                if playerGolds[currentPlayer] > 0:
                    print(f'You must play {ORANGE}Blackjack{CLEAR} with the computer (but up to {GREEN}{BLACKJACK_TARGET}{CLEAR} instead of {GREEN}21{CLEAR}).')
                    playBlackjack()
                else:
                    print(f'Unfortunately, you do not have any {YELLOW}gold{CLEAR} to gamble!')
            if spaceType == 'timewarp':
                print(f'You landed on {grammatiseSpaceType(spaceType)}!')
                print(f'You get to choose a player to be {TIMEWARP_SPACE}sent back in time{CLEAR} up to {GREEN}3 rounds{CLEAR}!')
                player = int(askForPlayer(f'{TURQUOISE}Enter the player who will be sent back: (1-{NUM_PLAYERS}){CLEAR} ', True))
                targetTime = min(10,len(prevPlayerPositions))
                playerPositions[player] = prevPlayerPositions[-targetTime][player]
                playerInventories[player] = prevPlayerInventories[-targetTime][player]
                playerGolds[player] = prevPlayerGolds[-targetTime][player]
                playerWaitingForWheelSpins[player] = prevPlayerWaitingForWheelSpins[-targetTime][player]
                for _ in range(targetTime-1):
                    for i in range(1, len(prevPlayerPositions)):
                        prevPlayerPositions[(-1)*i][player] = copy.copy(prevPlayerPositions[(-1)*(i+1)][player])
                        prevPlayerInventories[(-1)*i][player] = copy.copy(prevPlayerInventories[(-1)*(i+1)][player])
                        prevPlayerGolds[(-1)*i][player] = copy.copy(prevPlayerGolds[(-1)*(i+1)][player])
                        prevPlayerWaitingForWheelSpins[(-1)*i][player] = copy.copy(prevPlayerWaitingForWheelSpins[(-1)*(i+1)][player])
                    
    #ask for item use
    if running == True:
        if len(playerInventories[currentPlayer]) > 0:
            if useItem() == 'continue':
                os.system('clear')
                continue
    #change turn order
    print('-'*50)
    if running == True:
        input(f'{TURQUOISE}Press Enter to Continue to Next Player {CLEAR}')
        os.system('clear')
        #store backups
        prevPlayerPositions.append(copy.copy(playerPositions))
        prevPlayerInventories.append(copy.copy(playerInventories))
        prevPlayerGolds.append(copy.copy(playerGolds))
        prevPlayerWaitingForWheelSpins.append(copy.copy(playerWaitingForWheelSpins))
        prevItemPrices.append(copy.copy(itemPrices))
        prevDecorators.append(copy.copy(decorators))
        #change turn order
        currentPlayer += 1
        if currentPlayer > NUM_PLAYERS:
            currentPlayer = 1
            #evaluate misc turns
            decoratorsToRemove = []
            goblinsToAdd = []
            for n, row in enumerate(decorators):
                for m, cell in enumerate(row):
                    for l, decorator in enumerate(cell):
                        if decorator['type'] == 'goblin':
                            possibleMoves = findPossibleMoves(paths, {"row": n, "col": m}, True, highwayInformation)
                            chosenDestination = random.choice(possibleMoves)['destination']
                            decoratorsToRemove.append((n, m, l))
                            goblinsToAdd.append((chosenDestination['row'], chosenDestination['col'], decorator))
                            print(f'{RED}Player {decorator["placedBy"]}\'s goblin{CLEAR} has moved!')
            for decorator in sorted(decoratorsToRemove, reverse=True):
                decorators[decorator[0]][decorator[1]].pop(decorator[2])
            for goblin in goblinsToAdd:
                decorators[goblin[0]][goblin[1]].append(goblin[2])

print(f'{GREEN}Player {winner} wins!{CLEAR}')