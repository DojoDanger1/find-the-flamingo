import os
import copy
import math
import time
import pickle
import random
import datetime
import numpy as np
from names import get_first_name
from PIL import Image, ImageDraw, ImageColor, ImageFont

#bord paramaters
GRID_SIZE = 4
NUM_DIMENSIONS = 3
PERCENTAGE_SQUARES = 0.7
PERCENTAGE_PATHS = 0.5
PROBABILITY_ONE_WAY = 0.1
BIAS = 0.05

#game settings
NUM_PLAYERS = 5
ROLES_ENABLED = True
CHAOS_MODE = True
STARTING_INVENTORY = []
STARTING_GOLD = 3
STARTING_SPEED = 1
STARTING_FOOD_INVENTORY = {"meats": {}, "sauces": {}, "sides": {}, "dips": {}}
STALLER_WIN = 150
VOTING_FREQUENCY = 30
OTHERS_CANT_SEE_FLAMINGO = True
SHOP_PURCHACE_LIMIT = 3
CHANCE_OF_INFLATION = 0.5
CHANCE_OF_SUPER_INFLATION = 0.05
BLACKJACK_TARGET = 31
BLACKJACK_DEALER_CAUTION = 5
GYM_PROGRESS_REQUIRED = 3
WINGERIA_PROGRESS_REQUIRED = 4
MINIMUM_SPEED = 0.25
LYING_GAME_DIFFICULTY = 4
ACID_PRICE = 5
CONFIRM_STAY_HERE = True

#assertions
assert GRID_SIZE >= 3, 'grid size must be greater than or equal to 3!'
assert 2 <= NUM_DIMENSIONS and NUM_DIMENSIONS <= 26, 'number of dimensions must be in between 2 and 26!'
assert 0 < PERCENTAGE_SQUARES and PERCENTAGE_SQUARES <= 1, 'percentage squares must be between 0 and 1!'
assert 0 < PERCENTAGE_PATHS and PERCENTAGE_PATHS <= 1, 'percentage paths must be between 0 and 1!'
assert 0 < PROBABILITY_ONE_WAY and PROBABILITY_ONE_WAY <= 1, 'probability one way must be between 0 and 1!'
assert 0 < BIAS and BIAS <= 1-PERCENTAGE_PATHS, f'bias must be between 0 and {1-PERCENTAGE_PATHS}'
assert NUM_PLAYERS >= 1, 'number of players must be greater than or equal to 1!'
assert ROLES_ENABLED == False or (ROLES_ENABLED == True and NUM_PLAYERS > 3), 'games with less than 4 players cannot have roles enabled!'
assert CHAOS_MODE == False or (CHAOS_MODE == True and ROLES_ENABLED == True), 'if chaos mode is enabled, roles must also be enabled!'
assert STALLER_WIN % VOTING_FREQUENCY == 0, 'staller win must be an integer multiple of voting frequency!'
assert STARTING_SPEED > 0, 'starting speed must be positive!'
assert SHOP_PURCHACE_LIMIT > 0, 'shop purchase limit must be positive!'
assert 0 <= CHANCE_OF_INFLATION and CHANCE_OF_INFLATION <= 1, 'chance of inflation must be between 0 and 1!'
assert 0 <= CHANCE_OF_SUPER_INFLATION and CHANCE_OF_SUPER_INFLATION <= 1, 'chance of super inflation must be between 0 and 1!'
assert BLACKJACK_TARGET >= 21, 'blackjack target must be greater than or equal to 21!'
assert 0 <= BLACKJACK_DEALER_CAUTION and BLACKJACK_DEALER_CAUTION <= BLACKJACK_TARGET, f'blackjack dealer caution must be in between 0 and {BLACKJACK_TARGET}!'
assert GYM_PROGRESS_REQUIRED > 0, 'gym progress required must be positive!'
assert WINGERIA_PROGRESS_REQUIRED > 0, 'wingeria progress required must be positive!'
assert MINIMUM_SPEED >= 0, 'minimum speed must be non negative!'
assert LYING_GAME_DIFFICULTY >= 0, 'lying game difficulty must be non negative!'

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
PINK = getColour(227, 61, 208)
DARK_GREEN = getColour(0, 153, 36)

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
INFORMATION_SPACE = getColour(175, 175, 175)

#wingeria ingredients
WINGERIA_INGREDIENTS = ingredients = {"allTime": {"meats": ["Chicken Wings", "Boneless Wings", "Chicken Strips", "Shrimp", "Tofu Skewers", "Hog Wings"], "sauces": ["BBQ Sauce", "Buffalo Sauce", "Spicy Garlic Sauce", "Calypso Sauce", "Atomic Sauce", "Honey Mustard Sauce", "Teriyaki Sauce", "Medium Sauce", "Parmesan Sauce", "Wild Onion Sauce", "Wasabi Sauce", "Smoky Bacon Sauce", "Thai Chili Sauce", "Blazeberry Sauce", "Alabama BBQ Sauce", "Nashville Hot Sauce", "Peri Peri Sauce", "Aji Amarillo Sauce", "Carolina Sauce", "Tikka Masala Sauce", "Sriracha Sauce", "Adobo Sauce"], "sides": ["Carrots", "Celery", "Red Peppers", "Green Peppers", "French Fries", "Cheese Cubes", "Curly Fries", "Potato Skins", "Taquitos"], "dips": ["Blue Cheese Dip", "Ranch Dip", "Awesome Sauce Dip", "Kung Pao Dip", "Zesty Pesto Dip", "Lemon Butter", "Southwest Dip", "Hummus", "Artichoke Dip", "Guacamole", "Blackberry Remoulade"]}, "january": [{"name": "New Year", "sauces": ["Rainbow-livian Sauce", "Poutine Sauce"], "sides": ["Pizza Poppers"], "dips": ["Cheezy Whip"]}], "february": [{"name": "Mardi Gras", "sauces": ["Muffuletta Sauce", "Vieux Carr\u00e9 Sauce"], "sides": ["Crawdads"], "dips": ["Creole Crab Dip"]}], "march": [{"name": "Lucky Lucky Matsuri", "sauces": ["Gochujang Sauce", "Ginger Miso Sauce"], "sides": ["Kobumaki"], "dips": ["Karashi Mayo"]}], "april": [{"name": "Big Top Carnival", "sauces": ["Salted Caramel Sauce", "Candy Apple Sauce"], "sides": ["Corn Dogs"], "dips": ["PB&J Dip"]}], "may": [{"name": "OnionFest", "sauces": ["Sarge's Revenge Sauce"], "sides": ["Cocktail Onions"], "dips": ["French Onion Dip"]}], "june": [{"name": "Summer Luau", "sauces": ["Kilauea Sauce", "Hulu Hula Sauce"], "sides": ["Luau Musubi"], "dips": ["Mango-Chili Dip"]}], "july": [{"name": "Starlight BBQ", "sauces": ["Lone Star Pit Sauce", "Mambo Sauce"], "sides": ["BBQ Ribs"], "dips": ["Coleslaw"]}], "august": [{"name": "BavariaFest", "sauces": ["Doppelbock Sauce", "W\u00fcrzig Sauce"], "sides": ["Wiesswurst"], "dips": ["Bierk\u00e4se Dip"]}], "september": [{"name": "Maple Mornings", "sauces": ["Maple Glaze", "Sunrise Sauce"], "sides": ["Bacon"], "dips": ["Shirred Egg"]}], "october": [{"name": "Halloween", "sauces": ["La Catrina Sauce", "Ecto Sauce"], "sides": ["Mummy Dogs"], "dips": ["Purple Pesto"]}], "november": [{"name": "Thanksgiving", "sauces": ["Peppered Pumpkin Sauce", "Wojapi Sauce"], "sides": ["Sweet Potato Wedges"], "dips": ["Gravy"]}], "december": [{"name": "Christmas", "sauces": ["Cranberry Chili Sauce", "Krampus Sauce"], "sides": ["Roasted Asparagus"], "dips": ["Risalamande"]}]}

def convertLanguageDirectionsToLetters(directions):
    if 'up' in directions:
        directions[directions.index('up')] = '-y'
    if 'down' in directions:
        directions[directions.index('down')] = '+y'
    if 'right' in directions:
        directions[directions.index('right')] = '+x'
    if 'left' in directions:
        directions[directions.index('left')] = '-x'
    if 'forwards' in directions:
        directions[directions.index('forwards')] = '+z'
    if 'backwards' in directions:
        directions[directions.index('backwards')] = '-z'
    return directions

def getAxisOrderFromDirections(directions):
    directions = convertLanguageDirectionsToLetters(directions)
    directions = [d[1] for d in directions[::2]]
    directions.sort()
    if len(directions) == 2:
        return ['y', 'x']
    elif len(directions) == 3:
        return ['z', 'y', "x"]
    else:
        return directions[0:len(directions)-3] + directions[len(directions)-3:len(directions)][::-1]

if NUM_DIMENSIONS == 2:
    directions = ['up', 'down', 'left', 'right']
elif NUM_DIMENSIONS == 3:
    directions = ['up', 'down', 'left', 'right', 'forwards', 'backwards']
else:
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    directions = []
    for n in range(NUM_DIMENSIONS):
        directions.append(f'+{alphabet[25-n]}')
        directions.append(f'-{alphabet[25-n]}')

ALL_DIRECTIONS = directions
AXIS_ORDER = getAxisOrderFromDirections(copy.deepcopy(ALL_DIRECTIONS))

def fillSpaces(board, fillWith, howMany, toFill):
    initialIndexes = [tuple(x) for x in np.argwhere(board == toFill)]
    if len(initialIndexes) > 0:
        chosenSpaces = random.sample(list(initialIndexes), howMany)
        for space in chosenSpaces:
            board[space] = fillWith
    return board

def findPossiblePaths(board, endPos, oneWay, directions):
    possiblePaths = []
    directions = convertLanguageDirectionsToLetters(copy.deepcopy(directions))
    for direction in directions:
        sign = (1 if direction[0] == '+' else -1)
        axis = AXIS_ORDER.index(direction[1])
        done = False
        pos = list(copy.deepcopy(endPos))
        while not done:
            pos[axis] -= sign
            if pos[axis] < 0 or pos[axis] >= GRID_SIZE:
                done = True
            elif board[tuple(pos)] != None:
                done = True
                possiblePaths.append({"start": tuple(pos), "end": endPos, "oneWay": oneWay})
    return possiblePaths

def generateAValidHighway(board, paths):
    spaces = [tuple(x) for x in np.argwhere(board != None)]
    possibleIndexes = []
    for n, space in enumerate(spaces):
        if board[space] not in ['home', 'flamingo', 'shadow realm']:
            count = 0
            for path in paths:
                if path['start'] == space or path['end'] == space:
                    count += 1
            if count < 2 * NUM_DIMENSIONS:
                possibleIndexes.append(n)
    spaces = [space for (n, space) in enumerate(spaces) if n in possibleIndexes]
    if len(spaces) < 2:
        return -1
    validPath = False
    while not validPath:
        startPos = random.choice(spaces)
        endPos = random.choice([space for space in spaces if space != startPos])
        alreadyExisting = False
        if len([path for path in paths if (startPos == path['start'] or startPos == path['end']) and (endPos == path['start'] or endPos == path['end'])]) != 0:
            alreadyExisting = True
        path = {"start": startPos, "end": endPos, "oneWay": False}
        if (not alreadyExisting) and isThisPathAHighway(path):
            validPath = True
            return path

def generateBoard():
    print('generating board...')
    print(' attemtpting to fill in the the map...')
    reallyPossible = False
    while not reallyPossible:
        #initialise board
        print('  creating board array...')
        board = np.full(tuple([GRID_SIZE]*NUM_DIMENSIONS), None)
        decorators = np.empty(tuple([GRID_SIZE]*NUM_DIMENSIONS), dtype=object)
        for cell in [tuple(x) for x in np.argwhere(decorators == None)]:
            decorators[cell] = []
        #add empty spaces
        print('  adding empty spaces...')
        numEmpties = 0
        for n, cell in np.ndenumerate(board):
            if random.random() < PERCENTAGE_SQUARES:
                board[n] = 'empty'
                numEmpties += 1
        #add home space
        print('  adding home space...')
        midpoint = tuple([GRID_SIZE // 2]*NUM_DIMENSIONS)
        board[midpoint] = 'home'
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
        board = fillSpaces(board, 'information', numEmpties // 10, 'empty')
        #get positions of flamingo and shadow realm and home
        flamingoPos = tuple(np.argwhere(board == "flamingo")[0])
        shadowRealmPos = tuple(np.argwhere(board == "shadow realm")[0])
        homePos = tuple(np.argwhere(board == "home")[0])
        #repeat until game is possible
        print('  attempting to add pathways...')
        possible = False
        bias = 0
        while not possible:
            print('   adding paths to flamingo, home, shadow realm...')
            #initialise paths
            paths = []
            #add path to flamingo
            possiblePaths = [path for path in findPossiblePaths(board, flamingoPos, False, ALL_DIRECTIONS) if board[path['start']] != 'shadow realm']
            paths.append(random.choice(possiblePaths))
            #add paths to shadow realm
            possiblePaths = [path for path in findPossiblePaths(board, shadowRealmPos, False, ALL_DIRECTIONS) if board[path['start']] != 'flamingo']
            paths += possiblePaths
            #add paths from home
            possiblePaths = [path for path in findPossiblePaths(board, homePos, False, ALL_DIRECTIONS) if board[path['start']] not in ['flamingo', 'shadow realm']]
            paths += possiblePaths
            #add internal paths
            print(f'   adding internal paths with chance {PERCENTAGE_PATHS + bias}...')
            spaces = [tuple(x) for x in np.argwhere(board != None)]
            for pos in spaces:
                if board[pos] not in ['home', 'flamingo', 'shadow realm']:
                    for direction in AXIS_ORDER:
                        if random.random() < (PERCENTAGE_PATHS + bias):
                            oneWay = random.random() < PROBABILITY_ONE_WAY
                            possiblePaths = [path for path in findPossiblePaths(board, pos, oneWay, [f'+{direction}']) if board[path['start']] not in ['home', 'flamingo', 'shadow realm']]
                            if len(possiblePaths) != 0:
                                newPossiblePaths = [possiblePaths[0], {"start": possiblePaths[0]['end'], "end": possiblePaths[0]['start'], "oneWay": oneWay}]
                                paths.append(random.choice(newPossiblePaths))
            print('   checking if this is possible...')
            if isPossibleToGetEverywhere(board, paths, homePos, False, []) and not areThereAnyPurgatories(board, paths, False, []):
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
    for _ in range((numEmpties // 10)):
        highway = generateAValidHighway(board, paths)
        if highway != -1:
            paths.append(highway)
    #generate additional highways to shadow realm
    print(' adding additional highways to the shadow realm...')
    spaces = [tuple(x) for x in np.argwhere(board != None)]
    possibleIndexes = []
    for n, space in enumerate(spaces):
        if board[space] not in ['home', 'flamingo', 'shadow realm']:
            count = 0
            for path in paths:
                if path['start'] == space or path['end'] == space:
                    count += 1
            if count < 2 * NUM_DIMENSIONS:
                possibleIndexes.append(n)
    cellsWithLessThan4Paths = [space for (n, space) in enumerate(spaces) if n in possibleIndexes]
    numNewPaths = len(cellsWithLessThan4Paths)//8
    connectingCells = random.sample(cellsWithLessThan4Paths, numNewPaths)
    for cell in connectingCells:
        proposedPath = {"start": cell, "end": shadowRealmPos, "oneWay": False}
        if isThisPathAHighway(proposedPath):
            paths.append(proposedPath)
    #add pathDecorators
    pathDecorators = []
    for _ in paths:
        pathDecorators.append(copy.deepcopy([]))
    #return
    print('done!')
    print('generating image...')
    return board, paths, decorators, pathDecorators

def generateImage(board, paths, quantumEntanglements, debug=False):
    os.system('rm -rf map')
    os.mkdir('map')
    axisFont = ImageFont.truetype('font/Montserrat-SemiBold.ttf', 40)
    for axis1 in AXIS_ORDER:
        for axis2 in AXIS_ORDER[AXIS_ORDER.index(axis1)+1:]:
            if debug:
                print(f' generating image {axis1}{axis2}...')
            allImgs = {}
            
            axis1Num = AXIS_ORDER.index(axis1)
            axis2Num = AXIS_ORDER.index(axis2)
            consts = [axis for axis in AXIS_ORDER if axis not in [axis1, axis2]]
            for constNums, _ in np.ndenumerate(np.full([GRID_SIZE]*len(consts), None)):
                width = GRID_SIZE*100+100
                height = GRID_SIZE*100+100

                if NUM_DIMENSIONS > 2:
                    mainImg = Image.new('RGBA', (width,height), ImageColor.getcolor('#ffffff00', 'RGBA'))
                else:
                    mainImg = Image.new('RGBA', (width,height), ImageColor.getcolor('#ffffff', 'RGBA'))
                draw = ImageDraw.Draw(mainImg)
                
                draw.line((65,15,65,GRID_SIZE*100-45), fill=ImageColor.getcolor('#000000', 'RGBA'), width=15)
                draw.regular_polygon((65,GRID_SIZE*100-45, 30), 3, 180, fill=ImageColor.getcolor('#000000', 'RGBA'))
                draw.text((10,(GRID_SIZE*100)//2-20), axis1, fill=ImageColor.getcolor('#000000', 'RGBA'), font=axisFont)
                
                draw.line((100+15,GRID_SIZE*100+35,100+GRID_SIZE*100-45,GRID_SIZE*100+35), fill=ImageColor.getcolor('#000000', 'RGBA'), width=15)
                draw.regular_polygon((100+GRID_SIZE*100-45,GRID_SIZE*100+35, 30), 3, 270, fill=ImageColor.getcolor('#000000', 'RGBA'))
                draw.text((100+(GRID_SIZE*100)//2-(axisFont.getlength(axis2))//2,GRID_SIZE*100+45), axis2, fill=ImageColor.getcolor('#000000', 'RGBA'), font=axisFont)

                for path in paths:
                    rectCoords = (path['start'][axis2Num]*100+50+100, path['start'][axis1Num]*100+50, path['end'][axis2Num]*100+50+100, path['end'][axis1Num]*100+50)
                    if isThisPathAHighway(path):
                        startIsInPlane = True
                        endIsInPlane = True
                        for n, const in enumerate(consts):
                            if path['start'][AXIS_ORDER.index(const)] != constNums[n]:
                                startIsInPlane = False
                            if path['end'][AXIS_ORDER.index(const)] != constNums[n]:
                                endIsInPlane = False
                        if startIsInPlane and endIsInPlane:
                            draw.line(rectCoords, fill=ImageColor.getcolor('#0000ff', 'RGBA'), width=10)
                    else:
                        isInPlane = True
                        for n, const in enumerate(consts):
                            if path['start'][AXIS_ORDER.index(const)] != constNums[n] or path['end'][AXIS_ORDER.index(const)] != constNums[n]:
                                isInPlane = False
                        if isInPlane:
                            if path['oneWay']:
                                draw.line(rectCoords, fill=ImageColor.getcolor('#696969', 'RGBA'), width=10)
                                if path['end'][axis2Num] > path['start'][axis2Num] and path['end'][axis1Num] == path['start'][axis1Num]: #right
                                    draw.regular_polygon((math.ceil((path['end'][axis2Num]+path['start'][axis2Num])/2)*100+100, int(path['start'][axis1Num]*100+50), 15), 3, 270, fill=ImageColor.getcolor('#696969', 'RGBA'))
                                if path['end'][axis2Num] < path['start'][axis2Num] and path['end'][axis1Num] == path['start'][axis1Num]: #left
                                    draw.regular_polygon((math.ceil((path['end'][axis2Num]+path['start'][axis2Num])/2)*100+100, int(path['start'][axis1Num]*100+50), 15), 3, 90, fill=ImageColor.getcolor('#696969', 'RGBA'))
                                if path['end'][axis2Num] == path['start'][axis2Num] and path['end'][axis1Num] > path['start'][axis1Num]: #down
                                    draw.regular_polygon((int(path['start'][axis2Num]*100+50+100), math.ceil((path['end'][axis1Num]+path['start'][axis1Num])/2)*100, 15), 3, 180, fill=ImageColor.getcolor('#696969', 'RGBA'))
                                if path['end'][axis2Num] == path['start'][axis2Num] and path['end'][axis1Num] < path['start'][axis1Num]: #up
                                    draw.regular_polygon((int(path['start'][axis2Num]*100+50+100), math.ceil((path['end'][axis1Num]+path['start'][axis1Num])/2)*100, 15), 3, 0, fill=ImageColor.getcolor('#696969', 'RGBA'))
                            else:
                                draw.line(rectCoords, fill=ImageColor.getcolor('#000000', 'RGBA'), width=10)
                if NUM_DIMENSIONS == 2:
                    for entanglement in quantumEntanglements:
                        if entanglement[0][0] == entanglement[1][0]:
                            draw.line((entanglement[0][1]*100+50+100, entanglement[0][0]*100+50+15, entanglement[1][1]*100+50+100, entanglement[1][0]*100+50+15), fill=ImageColor.getcolor('#ff580a', 'RGBA'), width=10)
                        elif entanglement[0][1] == entanglement[1][1]:
                            draw.line((entanglement[0][1]*100+50+100+15, entanglement[0][0]*100+50, entanglement[1][1]*100+50+100+15, entanglement[1][0]*100+50), fill=ImageColor.getcolor('#ff580a', 'RGBA'), width=10)
                        elif {"start": entanglement[0], "end": entanglement[1], "oneWay": False} in paths or {"start": entanglement[1], "end": entanglement[0], "oneWay": False} in paths:
                            draw.line((entanglement[0][1]*100+50+100+15, entanglement[0][0]*100+50+15, entanglement[1][1]*100+50+100+15, entanglement[1][0]*100+50+15), fill=ImageColor.getcolor('#ff580a', 'RGBA'), width=10)
                        else:
                            draw.line((entanglement[0][1]*100+50+100, entanglement[0][0]*100+50, entanglement[1][1]*100+50+100, entanglement[1][0]*100+50), fill=ImageColor.getcolor('#ff580a', 'RGBA'), width=10)
                spaces = [tuple(x) for x in np.argwhere(board != None)]
                for space in spaces:
                    isInPlane = True
                    for n, const in enumerate(consts):
                        if space[AXIS_ORDER.index(const)] != constNums[n] or space[AXIS_ORDER.index(const)] != constNums[n]:
                            isInPlane = False
                    if isInPlane:
                        cell = board[space]
                        if cell == 'empty':
                            colour = '#8a8a8a'
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
                        if cell == 'information':
                            colour = '#ffffff'
                        draw.rectangle((space[axis2Num]*100+15+100, space[axis1Num]*100+15, space[axis2Num]*100+85+100, space[axis1Num]*100+85), fill=ImageColor.getcolor(colour, 'RGBA'), outline=ImageColor.getcolor('#000000', 'RGBA'), width=5)
                
                if NUM_DIMENSIONS > 2:
                    name = f'{axis1}{axis2},{",".join([f"{const}={constNums[n]+1}" for (n, const) in enumerate(consts)])}'
                else:
                    name = f'{axis1}{axis2}'
                allImgs[name] = mainImg
                if NUM_DIMENSIONS == 2:
                    mainImg.save(f'map/{name}.png', 'PNG')
            
            highways = [path for path in paths if isThisPathAHighway(path)]
            highwayCoords = []
            for n, highway in enumerate(highways):
                highwayCoords.append([highway['start'][axis2Num]*100+50+100, highway['start'][axis1Num]*100+50, highway['end'][axis2Num]*100+50+100, highway['end'][axis1Num]*100+50])
            entanglementCoords = []
            for n, entanglement in enumerate(quantumEntanglements):
                entanglementCoords.append([entanglement[0][axis2Num]*100+50+100, entanglement[0][axis1Num]*100+50, entanglement[1][axis2Num]*100+50+100, entanglement[1][axis1Num]*100+50])
            
            width = GRID_SIZE*100+100
            height = GRID_SIZE*100+100
            doneConsts = []
            for n, const in enumerate(consts):
                doneConsts.append(const)
                remainingConsts = [c for c in consts if c not in doneConsts]
                remainingConstNums = np.ndenumerate(np.full([GRID_SIZE]*len(remainingConsts), None))
                if n % 2 == 0: #stack horizontal
                    newHighwayCoords = []
                    for m, highway in enumerate(highwayCoords):
                        newHighwayCoords.append([highways[m]['start'][AXIS_ORDER.index(const)]*width+highway[0], highway[1], highways[m]['end'][AXIS_ORDER.index(const)]*width+highway[2], highway[3]])
                    highwayCoords = newHighwayCoords
                    newEntanglementCoords = []
                    for m, entanglement in enumerate(entanglementCoords):
                        newEntanglementCoords.append([quantumEntanglements[m][0][AXIS_ORDER.index(const)]*width+entanglement[0], entanglement[1], quantumEntanglements[m][1][AXIS_ORDER.index(const)]*width+entanglement[2], entanglement[3]])
                    entanglementCoords = newEntanglementCoords
                    for remainingConstNum, _ in remainingConstNums:
                        img = Image.new('RGBA', (width*GRID_SIZE,height+100), ImageColor.getcolor('#ffffff00', 'RGBA'))
                        draw = ImageDraw.Draw(img)
                        relevantImgs = []
                        relevantKeys = []
                        for key in allImgs:
                            relevant = True
                            if f'{const}=' in key:
                                if len(remainingConsts) > 0:
                                    for m, rConst in enumerate(remainingConsts):
                                        if f'{rConst}={remainingConstNum[m]+1}' not in key:
                                            relevant = False
                                else:
                                    relevant = True
                            else:
                                relevant = False
                            if relevant:
                                relevantImgs.append(allImgs[key])
                                relevantKeys.append(key)
                        if len(remainingConsts) == 0:
                            draw.rectangle((0,0,width*GRID_SIZE,height+100), fill=ImageColor.getcolor('#ffffff', 'RGBA'))
                            for highway in highwayCoords:
                                draw.line(highway, fill=ImageColor.getcolor('#0000ff', 'RGBA'), width=10)
                            for n, entanglement in enumerate(entanglementCoords):
                                if entanglement[0] == entanglement[2]:
                                    draw.line((entanglement[0]+15, entanglement[1], entanglement[2]+15, entanglement[3]), fill=ImageColor.getcolor('#ff580a', 'RGBA'), width=10)
                                elif entanglement[1] == entanglement[3]:
                                    draw.line((entanglement[0], entanglement[1]+15, entanglement[2], entanglement[3]+15), fill=ImageColor.getcolor('#ff580a', 'RGBA'), width=10)
                                elif {"start": quantumEntanglements[n][0], "end": quantumEntanglements[n][1], "oneWay": False} in paths or {"start": quantumEntanglements[n][1], "end": quantumEntanglements[n][0], "oneWay": False} in paths:
                                    draw.line((entanglement[0]+15, entanglement[1]+15, entanglement[2]+15, entanglement[3]+15), fill=ImageColor.getcolor('#ff580a', 'RGBA'), width=10)
                                else:
                                    draw.line(entanglement, fill=ImageColor.getcolor('#ff580a', 'RGBA'), width=10)
                        for m, relevantImg in enumerate(relevantImgs):
                            img.paste(relevantImg, (m*width, 0), mask=relevantImg)
                        draw.line((15,height+35,GRID_SIZE*width-45,height+35), fill=ImageColor.getcolor('#000000', 'RGBA'), width=15)
                        draw.regular_polygon((GRID_SIZE*width-45,height+35, 30), 3, 270, fill=ImageColor.getcolor('#000000', 'RGBA'))
                        draw.text(((width*GRID_SIZE)//2-(axisFont.getlength(const))//2,height+45), const, fill=ImageColor.getcolor('#000000', 'RGBA'), font=axisFont)
                        for key in relevantKeys:
                            del allImgs[key]
                        if len(remainingConsts) > 0:
                            name = f'{axis1}{axis2},{",".join([f"{rConst}={remainingConstNum[m]+1}" for (m, rConst) in enumerate(remainingConsts)])}'
                        else:
                            name = f'{axis1}{axis2}'
                        allImgs[name] = img
                        if len(remainingConsts) == 0:
                            img.save(f'map/{name}.png', 'PNG')
                    width = width*GRID_SIZE
                    height = height+100
                else: #stack vertical
                    newHighwayCoords = []
                    for m, highway in enumerate(highwayCoords):
                        newHighwayCoords.append([highway[0]+100, highways[m]['start'][AXIS_ORDER.index(const)]*height+highway[1], highway[2]+100, highways[m]['end'][AXIS_ORDER.index(const)]*height+highway[3]])
                    highwayCoords = newHighwayCoords
                    newEntanglementCoords = []
                    for m, entanglement in enumerate(entanglementCoords):
                        newEntanglementCoords.append([entanglement[0]+100, quantumEntanglements[m][0][AXIS_ORDER.index(const)]*height+entanglement[1], entanglement[2]+100, quantumEntanglements[m][1][AXIS_ORDER.index(const)]*height+entanglement[3]])
                    entanglementCoords = newEntanglementCoords
                    for remainingConstNum, _ in remainingConstNums:
                        img = Image.new('RGBA', (width+100,height*GRID_SIZE), ImageColor.getcolor('#ffffff00', 'RGBA'))
                        draw = ImageDraw.Draw(img)
                        relevantImgs = []
                        relevantKeys = []
                        for key in allImgs:
                            relevant = True
                            if f'{const}=' in key:
                                if len(remainingConsts) > 0:
                                    for m, rConst in enumerate(remainingConsts):
                                        if f'{rConst}={remainingConstNum[m]+1}' not in key:
                                            relevant = False
                                else:
                                    relevant = True
                            else:
                                relevant = False
                            if relevant:
                                relevantImgs.append(allImgs[key])
                                relevantKeys.append(key)
                        if len(remainingConsts) == 0:
                            draw.rectangle((0,0,width+100,height*GRID_SIZE), fill=ImageColor.getcolor('#ffffff', 'RGBA'))
                            for highway in highwayCoords:
                                draw.line(tuple(highway), fill=ImageColor.getcolor('#0000ff', 'RGBA'), width=10)
                            for n, entanglement in enumerate(entanglementCoords):
                                if entanglement[0] == entanglement[2]:
                                    draw.line((entanglement[0]+15, entanglement[1], entanglement[2]+15, entanglement[3]), fill=ImageColor.getcolor('#ff580a', 'RGBA'), width=10)
                                elif entanglement[1] == entanglement[3]:
                                    draw.line((entanglement[0], entanglement[1]+15, entanglement[2], entanglement[3]+15), fill=ImageColor.getcolor('#ff580a', 'RGBA'), width=10)
                                elif {"start": quantumEntanglements[n][0], "end": quantumEntanglements[n][1], "oneWay": False} in paths or {"start": quantumEntanglements[n][1], "end": quantumEntanglements[n][0], "oneWay": False} in paths:
                                    draw.line((entanglement[0]+15, entanglement[1]+15, entanglement[2]+15, entanglement[3]+15), fill=ImageColor.getcolor('#ff580a', 'RGBA'), width=10)
                                else:
                                    draw.line(entanglement, fill=ImageColor.getcolor('#ff580a', 'RGBA'), width=10)
                        for m, relevantImg in enumerate(relevantImgs):
                            img.paste(relevantImg, (100, m*height), mask=relevantImg)
                        draw.line((65,15,65,GRID_SIZE*height-45), fill=ImageColor.getcolor('#000000', 'RGBA'), width=15)
                        draw.regular_polygon((65,GRID_SIZE*height-45, 30), 3, 180, fill=ImageColor.getcolor('#000000', 'RGBA'))
                        draw.text((10,(GRID_SIZE*height)//2-20), const, fill=ImageColor.getcolor('#000000', 'RGBA'), font=axisFont)
                        for key in relevantKeys:
                            del allImgs[key]
                        if len(remainingConsts) > 0:
                            name = f'{axis1}{axis2},{",".join([f"{rConst}={remainingConstNum[m]+1}" for (m, rConst) in enumerate(remainingConsts)])}'
                        else:
                            name = f'{axis1}{axis2}'
                        allImgs[name] = img
                        if len(remainingConsts) == 0:
                            img.save(f'map/{name}.png', 'PNG')
                    width = width+100
                    height = height*GRID_SIZE

def isThisPathAHighway(path):
    for dimension in range(NUM_DIMENSIONS):
        if path['start'][dimension] == path['end'][dimension]:
            return False
    return True

def decideHighwayInformation(board, paths):
    highways = [path for path in paths if isThisPathAHighway(path)]
    highwayInformation = []
    for highway in highways:
        thisHighwaysInformation = []
        for startEnd in ['start', 'end']:
            moves = findPossibleMoves(paths, highway[startEnd], False, highwayInformation)
            if board[highway[startEnd]] == 'shadow realm':
                thisHighwaysInformation.append({"space": highway[startEnd], "direction": 'shadow realm'})
            else:
                possibleDirections = copy.deepcopy(ALL_DIRECTIONS)
                for move in moves:
                    possibleDirections.remove(move['direction'])
                for information in highwayInformation:
                    for subInformation in information:
                        if subInformation['space'] == highway[startEnd]:
                            possibleDirections.remove(subInformation['direction'])
                thisHighwaysInformation.append({"space": highway[startEnd], "direction": random.choice(possibleDirections)})
        highwayInformation.append(thisHighwaysInformation)
    return highwayInformation

def findPossibleMoves(paths, position, includeHighways, highwayInformation):
    possibleMoves = []
    possiblePaths = [(n, path) for n, path in enumerate(paths) if path['start'] == position or (path['end'] == position and path['oneWay'] == False)]
    numNonHighways = len([path for path in paths if not isThisPathAHighway(path)])
    for (n, path) in possiblePaths:
        if path['start'] == position:
            destination = path['end']
        else:
            destination = path['start']
        if isThisPathAHighway(path) and includeHighways:
            highway = highwayInformation[n-numNonHighways]
            if highway[0]['space'] == position:
                direction = highway[0]['direction']
            elif highway[1]['space'] == position:
                direction = highway[1]['direction']
        elif not isThisPathAHighway(path):
            for axis in AXIS_ORDER:
                if destination[AXIS_ORDER.index(axis)] > position[AXIS_ORDER.index(axis)]:
                    direction = f'+{axis}'
                elif destination[AXIS_ORDER.index(axis)] < position[AXIS_ORDER.index(axis)]:
                    direction = f'-{axis}'
        if (isThisPathAHighway(path) and includeHighways) or (not isThisPathAHighway(path)):
            if NUM_DIMENSIONS <= 3:
                if direction == '-y':
                    direction = 'up'
                elif direction == '+y':
                    direction = 'down'
                elif direction == '+x':
                    direction = 'right'
                elif direction == '-x':
                    direction = 'left'
                elif direction == '+z':
                    direction = 'forwards'
                elif direction == '-z':
                    direction = 'backwards'
            possibleMoves.append({"direction": direction, "destination": destination, "path": path})
    return sorted(possibleMoves, key=lambda x: x['direction'])

def findShadowRealm(board):
    return tuple(np.argwhere(board == "shadow realm")[0])

def findShortestPathToFlamingo(board, paths, startPos, highwayInformation):
    if board[startPos] == 'flamingo':
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
                if board[path['end']] == 'flamingo':
                    done = True
                    return [path]
        else:
            newPathChains = []
            for pathChain in allPathChains:
                position = pathChain[-1]['end']
                if board[position] != 'shadow realm':
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
                            if board[path['end']] == 'flamingo':
                                done = True
                                return newPathChain
            if len(newPathChains) == 0:
                done = True
                return 'impossible'
            allPathChains = newPathChains

def findPossibleMoves(paths, position, includeHighways, highwayInformation):
    possibleMoves = []
    possiblePaths = [(n, path) for n, path in enumerate(paths) if path['start'] == position or (path['end'] == position and path['oneWay'] == False)]
    numNonHighways = len([path for path in paths if not isThisPathAHighway(path)])
    for (n, path) in possiblePaths:
        if path['start'] == position:
            destination = path['end']
        else:
            destination = path['start']
        if isThisPathAHighway(path) and includeHighways:
            highway = highwayInformation[n-numNonHighways]
            if highway[0]['space'] == position:
                direction = highway[0]['direction']
            elif highway[1]['space'] == position:
                direction = highway[1]['direction']
        elif not isThisPathAHighway(path):
            for axis in AXIS_ORDER:
                if destination[AXIS_ORDER.index(axis)] > position[AXIS_ORDER.index(axis)]:
                    direction = f'+{axis}'
                elif destination[AXIS_ORDER.index(axis)] < position[AXIS_ORDER.index(axis)]:
                    direction = f'-{axis}'
        if (isThisPathAHighway(path) and includeHighways) or (not isThisPathAHighway(path)):
            if NUM_DIMENSIONS <= 3:
                if direction == '-y':
                    direction = 'up'
                elif direction == '+y':
                    direction = 'down'
                elif direction == '+x':
                    direction = 'right'
                elif direction == '-x':
                    direction = 'left'
                elif direction == '+z':
                    direction = 'forwards'
                elif direction == '-z':
                    direction = 'backwards'
            possibleMoves.append({"direction": direction, "destination": destination, "path": path})
    return sorted(possibleMoves, key=lambda x: x['direction'])

def isPossibleToGetEverywhere(board, paths, startPos, includeHighways, highwayInformation):
    previouslySearched = []
    currentlySearching = [startPos]
    nextSearching = ['something is in here']
    while len(nextSearching) > 0:
        nextSearching = []
        for space in currentlySearching:
            if board[space] != 'shadow realm':
                possibleMoves = findPossibleMoves(paths, space, includeHighways, highwayInformation)
                for move in possibleMoves:
                    destination = move['destination']
                    if destination not in previouslySearched and destination not in nextSearching and destination not in currentlySearching:
                        nextSearching.append(destination)
            if space not in previouslySearched:
                previouslySearched.append(space)
        currentlySearching = copy.deepcopy(nextSearching)
    numPossibleSpaces = len(previouslySearched)
    numSpaces = len(np.argwhere(board != None))
    return numPossibleSpaces == numSpaces

def areThereAnyPurgatories(board, paths, includeHighways,  highwayInformation):
    spaces = [tuple(x) for x in np.argwhere(board != None)]
    for pos in spaces:
        if board[pos] != None:
            possibleMoves = findPossibleMoves(paths, pos, includeHighways, highwayInformation)
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
    candidates = [player for player in list(range(1,NUM_PLAYERS+1)) if player not in eliminatedPlayers]
    if not includeSelf:
        candidates = [player for player in candidates if player != currentPlayer]
    if len(candidates) == 0:
        return -1
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
        if option in eliminatedPlayers:
            indent += 1
            print(f'{" "*indent}{ERROR}Invalid Answer! This player has been eliminated!{CLEAR}')
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

def selectRandomSpace(board):
    validSpace = False
    while not validSpace:
        space = random.choice([tuple(x) for x in np.argwhere(board != None)])
        if board[space] != 'flamingo':
            validSpace = True
    return space

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
    hasBeenEliminated = False
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
            playerPositions[currentPlayer] = tuple(np.argwhere(board == "home")[0])
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
        player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who will be randomly teleported (1-{NUM_PLAYERS}):{CLEAR} ', True))
        if player == -1:
            print(f'{" "*indent}{RED}Unfortunately, there is no one to choose.{CLEAR}')
        else:
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
        player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who will be sent back (1-{NUM_PLAYERS}):{CLEAR} ', True))
        if player == -1:
            print(f'{" "*indent}{RED}Unfortunately, there is no one to choose.{CLEAR}')
        else:
            targetTime = min(1+3*(NUM_PLAYERS-len(eliminatedPlayers)),len(prevPlayerPositions))
            playerPositions[player] = prevPlayerPositions[-targetTime][player]
            playerInventories[player] = prevPlayerInventories[-targetTime][player]
            playerGolds[player] = prevPlayerGolds[-targetTime][player]
            playerSpeeds[player] = prevPlayerSpeeds[-targetTime][player]
            playerFoodInventories[player] = prevPlayerFoodInventories[-targetTime][player]
            playerProgress[player] = prevPlayerProgress[-targetTime][player]
            playerStealBonus[player] = prevPlayerStealBonus[-targetTime][player]
            playerInvestmentBonus[player] = prevPlayerInvestmentBonus[-targetTime][player]
            playerQuests[player] = prevPlayerQuests[-targetTime][player]
            playerWaitingForEvents[player] = prevPlayerWaitingForEvents[-targetTime][player]
            playerFrozens[player] = prevPlayerFrozens[-targetTime][player]
            playerQuantumNotifications[player] = prevPlayerQuantumNotifications[-targetTime][player]
            playerGreenPotionTurns[player] = prevPlayerGreenPotionTurns[-targetTime][player]
            for _ in range(targetTime-1):
                for i in range(1, len(prevPlayerPositions)):
                    prevPlayerPositions[(-1)*i][player] = copy.deepcopy(prevPlayerPositions[(-1)*(i+1)][player])
                    prevPlayerInventories[(-1)*i][player] = copy.deepcopy(prevPlayerInventories[(-1)*(i+1)][player])
                    prevPlayerGolds[(-1)*i][player] = copy.deepcopy(prevPlayerGolds[(-1)*(i+1)][player])
                    prevPlayerSpeeds[(-1)*i][player] = copy.deepcopy(prevPlayerSpeeds[(-1)*(i+1)][player])
                    prevPlayerFoodInventories[(-1)*i][player] = copy.deepcopy(prevPlayerFoodInventories[(-1)*(i+1)][player])
                    prevPlayerProgress[(-1)*i][player] = copy.deepcopy(prevPlayerProgress[(-1)*(i+1)][player])
                    prevPlayerStealBonus[(-1)*i][player] = copy.deepcopy(prevPlayerStealBonus[(-1)*(i+1)][player])
                    prevPlayerInvestmentBonus[(-1)*i][player] = copy.deepcopy(prevPlayerInvestmentBonus[(-1)*(i+1)][player])
                    prevPlayerQuests[(-1)*i][player] = copy.deepcopy(prevPlayerQuests[(-1)*(i+1)][player])
                    prevPlayerWaitingForEvents[(-1)*i][player] = copy.deepcopy(prevPlayerWaitingForEvents[(-1)*(i+1)][player])
                    prevPlayerFrozens[(-1)*i][player] = copy.deepcopy(prevPlayerFrozens[(-1)*(i+1)][player])
                    prevPlayerQuantumNotifications[(-1)*i][player] = copy.deepcopy(prevPlayerQuantumNotifications[(-1)*(i+1)][player])
                    prevPlayerGreenPotionTurns[(-1)*i][player] = copy.deepcopy(prevPlayerGreenPotionTurns[(-1)*(i+1)][player])
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
        entanglementSpace()
    if spaceType == 'information':
        hasBeenEliminated = spinTheInformationWheel()
    indent -= 1
    return hasBeenEliminated

def evaluateDecorators():
    global indent
    decoratorsToRemove = []
    goblinsToAdd = []
    for n, decorator in enumerate(decorators[playerPositions[currentPlayer]]):
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
            possibleMoves = findPossibleMoves(paths, playerPositions[currentPlayer], True, highwayInformation)
            chosenDestination = random.choice(possibleMoves)['destination']
            decoratorsToRemove.append(n)
            print(f'{" "*indent}{RED}Player {decorator["placedBy"]}\'s goblin{CLEAR} has moved!')
            if board[chosenDestination] == 'shadow realm':
                indent += 1
                print(f'{" "*indent}The goblin {RED}got lost{CLEAR} in the {SHADOW_REALM_SPACE}shadow realm{CLEAR} and died.')
                indent -= 1
            else:
                goblinsToAdd.append((chosenDestination, decorator))
            indent -= 2
        if decorator['type'] == 'flamingo':
            indent += 1
            print(f'{" "*indent}{RED}Player {decorator["placedBy"]}\'s {FLAMINGO_SPACE}flamingo{CLEAR} is on this space!')
            indent -= 1
        if decorator['type'] == 'acid' and decorator['placedBy'] != currentPlayer:
            indent += 1
            print(f'{" "*indent}Fortunately, you landed on {RED}Player {decorator["placedBy"]}\'s acid{CLEAR}!')
            indent += 1
            print(f'{" "*indent}They must give you {YELLOW}{decorator["reward"]} gold{CLEAR}.')
            playerGolds[decorator['placedBy']] -= decorator["reward"]
            playerGolds[currentPlayer] += decorator["reward"]
            print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR} and {RED}Player {decorator["placedBy"]}{CLEAR} now has {YELLOW}{playerGolds[decorator["placedBy"]]} gold{CLEAR}.')
            decoratorsToRemove.append(n)
            indent -= 2
        time.sleep(0.5)
    for decorator in sorted(decoratorsToRemove, reverse=True):
        decorators[playerPositions[currentPlayer]].pop(decorator)
    for goblin in goblinsToAdd:
        decorators[goblin[0]].append(goblin[1])

def evaluatePathDecorators(chosenPath):
    global indent
    global allowedToMove
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
                            code = int(askOptions(f'{" "*indent}{TURQUOISE}Enter the code for this {CYAN}padlock{TURQUOISE} ({getColourFromFraction(attempts/3)}{attempts} attempt{"s" if attempts != 1 else ""}{TURQUOISE} remaining) (0-9999):{CLEAR} ', 9999))
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

def checkForFatPeople(destination):
    global indent
    global allowedToMove
    for player in range(1,NUM_PLAYERS+1):
        if playerPositions[player] == destination and random.random() < max(1.5-playerSpeeds[player]-playerSpeeds[currentPlayer], 0) and player != currentPlayer:
            indent += 1
            print(f'{" "*indent}Unfortunately, due to your and {YELLOW}Player {player}\'s{CLEAR} {GRAY}(statistically speaking){CLEAR} {PAPAS_WINGERIA_SPACE}fat asses{CLEAR}, you {RED}cannot{CLEAR} move onto this space, as there is no room.')
            allowedToMove = False
            indent -= 1

def checkForSquashedPeople():
    global indent
    for player in range(1,NUM_PLAYERS+1):
        if playerPositions[player] == playerPositions[currentPlayer] and random.random() < 2*(max(0.75-playerSpeeds[currentPlayer], 0)) and playerSpeeds[currentPlayer] < playerSpeeds[player] and player != currentPlayer:
            indent += 1
            print(f'{" "*indent}{RED}Uh oh!{CLEAR} It looks like you have {PAPAS_WINGERIA_SPACE}squished{CLEAR} {YELLOW}Player {player}{CLEAR}! {GRAY}(you didn\'t see them under all your belly fat){CLEAR}')
            indent += 1
            print(f'{" "*indent}{YELLOW}Player {player}{CLEAR}, you have been {RED}eliminated{CLEAR} for {ORANGE}1 round{CLEAR}.')
            eliminatedPlayers.append(player)
            if player < currentPlayer:
                playerEliminationReturns[player] = roundNum+2
            else:
                playerEliminationReturns[player] = roundNum+1
            indent -= 2

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
        if NUM_PLAYERS - len(eliminatedPlayers) > 1:
            players = list(range(1,NUM_PLAYERS+1))
            players = [player for player in players if player != currentPlayer and player not in eliminatedPlayers]
            player = random.choice(players)
            temp = playerPositions[player]
            playerPositions[player] = playerPositions[currentPlayer]
            playerPositions[currentPlayer] = temp
        else:
            print(f'{" "*indent}{RED}Unfortunately, there is no one to swap with.{CLEAR}')
    if result == f'{" "*indent}You must give away {YELLOW}all gold{CLEAR}. {YELLOW}({playerGolds[currentPlayer]}){CLEAR}':
        indent += 1
        player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who you will give your {YELLOW}gold{TURQUOISE} to (1-{NUM_PLAYERS}):{CLEAR} ', False))
        if player == -1:
            print(f'{" "*indent}{RED}Unfortunately, there is no one to choose.{CLEAR}')
        else:
            playerGolds[player] += playerGolds[currentPlayer]
            playerGolds[currentPlayer] = 0
            print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR} and {RED}Player {player}{CLEAR} now has {YELLOW}{playerGolds[player]} gold{CLEAR}.')
        indent -= 1
    if result == f'{" "*indent}You must return to the {HOME_SPACE}Home{CLEAR} space.':
        playerPositions[currentPlayer] = tuple(np.argwhere(board == "home")[0])
    if result == f'{" "*indent}You must give away {YELLOW}3 gold{CLEAR}.':
        indent += 1
        player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who you will give {YELLOW}3 gold{TURQUOISE} to (1-{NUM_PLAYERS}):{CLEAR} ', False))
        if player == -1:
            print(f'{" "*indent}{RED}Unfortunately, there is no one to choose.{CLEAR}')
        else:
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
            if ';' in item:
                itemName = item.split(';')[0]
            else:
                itemName = item
            player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who you will give the {CYAN}{itemName.title()}{TURQUOISE} to (1-{NUM_PLAYERS}):{CLEAR} ', False))
            if player == -1:
                print(f'{" "*indent}{RED}Unfortunately, there is no one to choose who to give it to.{CLEAR}')
            else:
                playerInventories[currentPlayer].remove(item)
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
        indent += 1
        print(f'{" "*indent}{GRAY}(regenerating map image...){CLEAR}')
        indent -= 1
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
        f'{" "*indent}You must either {GAMBLING_SPACE}gamble{CLEAR}, or make {RED}another player{CLEAR} {GAMBLING_SPACE}gamble{CLEAR}.',
        f'{" "*indent}You get to spin the {QUEST_SPACE}quest wheel{CLEAR}!',
    ]
    result = spinWheelVisually(options)
    print(f'\x1B[A\x1B[2K{result}')
    time.sleep(1)
    if result == f'{" "*indent}You can {CYAN}send a player{CLEAR} to the {SHADOW_REALM_SPACE}Shadow Realm{CLEAR}!':
        indent += 1
        player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who will be sent to the {SHADOW_REALM_SPACE}Shadow Realm{TURQUOISE} (1-{NUM_PLAYERS}):{CLEAR} ', True))
        if player == -1:
            print(f'{" "*indent}{RED}Unfortunately, there is no one to choose.{CLEAR}')
        else:
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
            player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who will {GAMBLING_SPACE}gamble{TURQUOISE} at the start of their next turn (1-{NUM_PLAYERS}):{CLEAR} ', False))
            if player == -1:
                print(f'{" "*indent}{RED}Unfortunately, there is no one to choose.{CLEAR}')
            else:
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
        player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who will be sent to the {SHADOW_REALM_SPACE}Shadow Realm{TURQUOISE} (1-{NUM_PLAYERS}):{CLEAR} ', False))
        if player == -1:
            print(f'{" "*indent}{RED}Unfortunately, there is no one to choose.{CLEAR}')
        else:
            playerPositions[player] = findShadowRealm(board)
        indent -= 1
    if result == f'{" "*indent}You can now spin the {GREEN}Good Wheel{CLEAR}!':
        spinTheGoodWheel()
    if result == f'{" "*indent}You must return to the {HOME_SPACE}Home{CLEAR} space.':
        playerPositions[currentPlayer] = tuple(np.argwhere(board == "home")[0])
    if result == f'{" "*indent}All other players gain {YELLOW}2 gold{CLEAR}':
        indent += 1
        for player in range(1, NUM_PLAYERS+1):
            if player != currentPlayer and player not in eliminatedPlayers:
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
        {"type": 'spendMoney', "requirement": (spendMoney := random.randint(7,15)), "reward": int((spendMoney*1.25)//1), "progress": 0, "timeLeft": int((spendMoney*1.5)//1)}
    ]
    if NUM_PLAYERS - len(eliminatedPlayers) >= 2:
        actualOptions += [{"type": 'shootPeople', "requirement": (peopleToShoot := random.randint(2, min(NUM_PLAYERS, 5))), "reward": peopleToShoot*4, "progress": 0, "timeLeft": 15}]
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

def spinTheInformationWheel():
    global indent
    indent += 1
    print(f'{" "*indent}You get {INFORMATION_SPACE}information{CLEAR} about:')
    indent += 1
    options = []
    for axis in AXIS_ORDER:
        options += [
            f'{" "*indent}The {ORANGE}{axis}{CLEAR}-coordinate of the {FLAMINGO_SPACE}flamingo space{CLEAR}.',
            f'{" "*indent}The number of spaces in a {ORANGE}{axis}{CLEAR}-plane.',
            f'{" "*indent}The {ORANGE}{axis}{CLEAR}-coordinate of the space {ORANGE}adjacent{CLEAR} to the {FLAMINGO_SPACE}flamingo space{CLEAR}.',
        ]
    options += [
        f'{" "*indent}The {ORANGE}total{CLEAR} number of spaces on the board',
        f'{" "*indent}The number of spaces of a {ORANGE}certain type{CLEAR}.',
        f'{" "*indent}The space at {ORANGE}specific coordinates{CLEAR}.',
        f'{" "*indent}The space {ORANGE}adjacent{CLEAR} to the {FLAMINGO_SPACE}flamingo space{CLEAR}.',
        f'{" "*indent}The number of {SHOP_SPACE}highways{CLEAR}.',
        f'{" "*indent}The number of {SHOP_SPACE}highways{CLEAR} into the {SHADOW_REALM_SPACE}shadow realm{CLEAR}.',
        f'{" "*indent}The number of {ENTANGLEMENT_SPACE}quantum entanglements{CLEAR}.',
        f'{" "*indent}The position of a {ENTANGLEMENT_SPACE}quantum-entangled{CLEAR} space.'
    ]
    result = spinWheelVisually(options)
    print(f'\x1B[A\x1B[2K{result}')
    time.sleep(1)
    indent += 1
    for axis in AXIS_ORDER:
        if result == f'{" "*(indent-1)}The {ORANGE}{axis}{CLEAR}-coordinate of the {FLAMINGO_SPACE}flamingo space{CLEAR}.':
            flamingoPos = tuple(np.argwhere(board == "flamingo")[0])
            choices = [x for x in list(range(0,GRID_SIZE)) if x != flamingoPos[AXIS_ORDER.index(axis)]]
            print(f'{" "*indent}The {FLAMINGO_SPACE}flamingo space{CLEAR} is {RED}not{CLEAR} in {ORANGE}{axis} = {random.choice(choices)+1}{CLEAR}.')
        if result == f'{" "*(indent-1)}The number of spaces in a {ORANGE}{axis}{CLEAR}-plane.':
            axisNum = random.randint(1, GRID_SIZE)
            count = len([space for space in [tuple(x) for x in np.argwhere(board != None)] if space[AXIS_ORDER.index(axis)] == axisNum-1])
            print(f'{" "*indent}There {"are" if count != 1 else "is"} {GREEN}{count}{CLEAR} space{"s" if count != 1 else ""} in {ORANGE}{axis} = {axisNum}{CLEAR}.')
        if result == f'{" "*(indent-1)}The {ORANGE}{axis}{CLEAR}-coordinate of the space {ORANGE}adjacent{CLEAR} to the {FLAMINGO_SPACE}flamingo space{CLEAR}.':
            flamingoPos = tuple(np.argwhere(board == "flamingo")[0])
            possibleMoves = findPossibleMoves(paths, flamingoPos, True, highwayInformation)
            destination = possibleMoves[0]['destination']
            choices = [x for x in list(range(0,GRID_SIZE)) if x != destination[AXIS_ORDER.index(axis)]]
            print(f'{" "*indent}The space {ORANGE}adjacent{CLEAR} to the {FLAMINGO_SPACE}flamingo space{CLEAR} is {RED}not{CLEAR} in {ORANGE}{axis} = {random.choice(choices)+1}{CLEAR}.')
    if result == f'{" "*(indent-1)}The {ORANGE}total{CLEAR} number of spaces on the board':
        count = len([tuple(x) for x in np.argwhere(board != None)])
        print(f'{" "*indent}In {ORANGE}total{CLEAR}, there {"are" if count != 1 else "is"} {GREEN}{count}{CLEAR} space{"s" if count != 1 else ""}.')
    if result == f'{" "*(indent-1)}The number of spaces of a {ORANGE}certain type{CLEAR}.':
        spaceType = random.choice(['empty', 'flamingo', 'home', 'shadow realm', 'good', 'bad', 'shop', 'teleport', 'gambling', 'timewarp', 'papas wingeria', 'gym', 'quest', 'entanglement', 'information'])
        count = len([tuple(x) for x in np.argwhere(board == spaceType)])
        print(f'{" "*indent}There {"are" if count != 1 else "is"} {GREEN}{count}{CLEAR} {grammatiseSpaceType(spaceType, article=False)}{"s" if count != 1 else ""}.')
    if result == f'{" "*(indent-1)}The space at {ORANGE}specific coordinates{CLEAR}.':
        coords = tuple([random.randint(0, GRID_SIZE-1) for _ in range(NUM_DIMENSIONS)])
        space = board[coords]
        coordinates = ", ".join([f"{ORANGE}{axis}{CLEAR}: {GREEN}{coords[n]+1}{CLEAR}" for (n, axis) in enumerate(AXIS_ORDER)])
        if space == None:
            print(f'{" "*indent}At ({coordinates}) there is no space.')
        else:
            print(f'{" "*indent}At ({coordinates}) there is {grammatiseSpaceType(space)}.')
    if result == f'{" "*(indent-1)}The space {ORANGE}adjacent{CLEAR} to the {FLAMINGO_SPACE}flamingo space{CLEAR}.':
        flamingoPos = tuple(np.argwhere(board == "flamingo")[0])
        possibleMoves = findPossibleMoves(paths, flamingoPos, True, highwayInformation)
        destination = possibleMoves[0]['destination']
        print(f'{" "*indent}The space {ORANGE}adjacent{CLEAR} to the {FLAMINGO_SPACE}flamingo space{CLEAR} is {grammatiseSpaceType(board[destination])}.')
    if result == f'{" "*(indent-1)}The number of {SHOP_SPACE}highways{CLEAR}.':
        count = len([path for path in paths if isThisPathAHighway(path)])
        print(f'{" "*indent}There {"are" if count != 1 else "is"} {GREEN}{count}{CLEAR} {SHOP_SPACE}highway{"s" if count != 1 else ""}{CLEAR}.')
    if result == f'{" "*(indent-1)}The number of {SHOP_SPACE}highways{CLEAR} into the {SHADOW_REALM_SPACE}shadow realm{CLEAR}.':
        count = len([path for path in paths if isThisPathAHighway(path) and board[path['end']] == 'shadow realm'])
        print(f'{" "*indent}There {"are" if count != 1 else "is"} {GREEN}{count}{CLEAR} {SHOP_SPACE}highway{"s" if count != 1 else ""}{CLEAR} leading to the {SHADOW_REALM_SPACE}shadow realm{CLEAR}.')
    if result == f'{" "*(indent-1)}The number of {ENTANGLEMENT_SPACE}quantum entanglements{CLEAR}.':
        count = len(quantumEntanglements)
        print(f'{" "*indent}There {"are" if count != 1 else "is"} {GREEN}{count}{CLEAR} {ENTANGLEMENT_SPACE}quantum entanglement{"s" if count != 1 else ""}{CLEAR}.')
    if result == f'{" "*(indent-1)}The position of a {ENTANGLEMENT_SPACE}quantum-entangled{CLEAR} space.':
        if len(quantumEntanglements) == 0:
            print(f'{" "*indent}No spaces are {ENTANGLEMENT_SPACE}quantum-entangled{CLEAR}.')
        else:
            space = random.choice(random.choice(quantumEntanglements))
            coordinates = ", ".join([f"{ORANGE}{axis}{CLEAR}: {GREEN}{space[n]+1}{CLEAR}" for (n, axis) in enumerate(AXIS_ORDER)])
            print(f'{" "*indent}The space at ({coordinates}) has been {ENTANGLEMENT_SPACE}quantum-entangled{CLEAR}.')
    indent -= 3

def spinTheFlamingoWheel():
    global indent
    indent += 1
    options = [
        f'{" "*indent}The {FLAMINGO_SPACE}Number Game{CLEAR}',
        f'{" "*indent}The {FLAMINGO_SPACE}Board Quiz{CLEAR}',
        f'{" "*indent}The {FLAMINGO_SPACE}Logic Game{CLEAR}',
        f'{" "*indent}The {FLAMINGO_SPACE}Date Quiz{CLEAR}',
        f'{" "*indent}The {FLAMINGO_SPACE}Lying Game{CLEAR}',
        f'{" "*indent}The {FLAMINGO_SPACE}Mixed Game{CLEAR}'
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
        result = playBoardQuiz(questions, only=False)
    if result == f'{" "*indent}The {FLAMINGO_SPACE}Logic Game{CLEAR}':
        print(f'{" "*indent}You must simplify {GREEN}5{CLEAR} logic expressions in {RED}increasing difficulty{CLEAR}.')
        result = playLogicGame(5, only=False)
    if result == f'{" "*indent}The {FLAMINGO_SPACE}Date Quiz{CLEAR}':
        print(f'{" "*indent}You must identify the {ORANGE}day of the week{CLEAR} of {GREEN}5{CLEAR} dates in {RED}increasing difficulty{CLEAR}.')
        result = playDateQuiz(questions='all')
    if result == f'{" "*indent}The {FLAMINGO_SPACE}Lying Game{CLEAR}':
        questions = random.randint(4, 9)
        print(f'{" "*indent}You must identify the {RED}number of liars{CLEAR} in {GREEN}{questions}{CLEAR} sets of {CYAN}people{CLEAR} making statements about each other.')
        result = playLyingGame(questions, only=False)
    if result == f'{" "*indent}The {FLAMINGO_SPACE}Mixed Game{CLEAR}':
        print(f'{" "*indent}You must answer {GREEN}1{CLEAR} question from each of the other {FLAMINGO_SPACE}flamingo games{CLEAR}.')
        order = ['board', 'logic', 'date', 'lying']
        random.shuffle(order)
        for n, game in enumerate(order):
            if game == 'board':
                result = playBoardQuiz(n+1, only=True)
            if game == 'logic':
                result = playLogicGame(n+1, only=True)
            if game == 'date':
                result = playDateQuiz(questions=n+1)
            if game == 'lying':
                result = playLyingGame(n+1, only=True)
            if result == False:
                break
        if result == True:
            unit = random.randint(3,9)
            limit = random.randint(25,100)
            print(f'{" "*indent}You must count to {GREEN}{limit}{CLEAR} {RED}excluding numbers{CLEAR} that follow these rules:\n{" "*(indent+1)}{RED}Cannot{CLEAR} be a multiple of {GREEN}{unit}{CLEAR}.\n{" "*(indent+1)}{RED}Cannot{CLEAR} contain the number {GREEN}{unit}{CLEAR}.\n{" "*(indent+1)}{RED}Cannot{CLEAR} have {GREEN}{unit}{CLEAR} digits.\n{" "*(indent+1)}Digits {RED}cannot{CLEAR} sum to {GREEN}{unit}{CLEAR}.\n{" "*(indent+1)}{RED}Cannot{CLEAR} have {GREEN}{unit}{CLEAR} letters. {GRAY}(in english, excluding spaces and hyphens){CLEAR}\n{" "*(indent+1)}{RED}Cannot{CLEAR} have {GREEN}{unit}{CLEAR} syllables. {GRAY}(in english){CLEAR}\n{" "*indent}Start at {GREEN}1{CLEAR}, unless it breaks some rules.')
            result = playNumberGame(unit, limit)
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
            if item != 'ingredient bundle':
                if item in itemRewards.keys():
                    playerInventories[currentPlayer].append(f'{item};{itemRewards[item]+playerStealBonus[currentPlayer]}')
                elif item == 'time machine':
                    numTimeMachines += 1
                    playerInventories[currentPlayer].append(f'{item};{numTimeMachines}')
                else:
                    playerInventories[currentPlayer].append(item)
            else:
                addToFoodInventory(itemPrices['ingredient bundle']*3)
            if random.random() < CHANCE_OF_SUPER_INFLATION:
                itemPrices[item] *= 2
                if item in itemRewards.keys() and item != 'green potion':
                    itemRewards[item] *= 2
                    itemDescriptions = redefineItemDescriptions()
            elif random.random() < CHANCE_OF_INFLATION:
                itemPrices[item] += 1
                if item in itemRewards.keys() and item != 'green potion':
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
    global playerRoles
    global playerSpecialAbilities
    global playerPositions
    global playerInventories
    global playerFoodInventories
    global playerGolds
    global playerSpeeds
    global playerProgress
    global playerStealBonus
    global playerInvestmentBonus
    global playerQuests
    global playerWaitingForEvents
    global playerFrozens
    global playerQuantumNotifications
    global playerEliminationReturns
    global playerPoisoneds
    global playerHealedPoisons
    global playerGreenPotionTurns
    global itemPrices
    global itemRewards
    global itemDescriptions
    global decorators
    global pathDecorators
    global board
    global quantumEntanglements
    global blackHolePos
    global blackHoleRadius
    global eliminatedPlayers
    global mewChance
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
                            if board[playerPositions[currentPlayer]] == 'shadow realm':
                                print(f'{" "*indent}The compass is {RED}useless{CLEAR} in the {SHADOW_REALM_SPACE}shadow realm{CLEAR}. No information was given.')
                            else:
                                possibleMoves = findPossibleMoves(paths, playerPositions[currentPlayer], True, highwayInformation)
                                print(f'{" "*indent}Here is all of the information about the {ORANGE}Adjacent Spaces{CLEAR}:')
                                indent += 1
                                message = f'You are currently on {grammatiseSpaceType(board[playerPositions[currentPlayer]], punctuation=False)}.'
                                for player, playerPosition in enumerate(playerPositions):
                                    if playerPosition == playerPositions[currentPlayer] and player != currentPlayer and player not in eliminatedPlayers:
                                        message += f' {RED}Player {player}{CLEAR} is also on this space.'
                                for decorator in decorators[playerPositions[currentPlayer]]:
                                    message += f' There is also a {CYAN}{decorator["type"]}{CLEAR} on this space.'
                                print(f'{" "*indent}{message}')
                                for move in possibleMoves:
                                    destinationSpaceType = board[move['destination']]
                                    if NUM_DIMENSIONS < 4:
                                        message = f'If you move {GREEN}{move["direction"]}{CLEAR}, you will land on {grammatiseSpaceType(destinationSpaceType, punctuation=False)}.'
                                    else:
                                        message = f'If you move in the {GREEN}{move["direction"]} direction{CLEAR}, you will land on {grammatiseSpaceType(destinationSpaceType, punctuation=False)}.'
                                    for player, playerPosition in enumerate(playerPositions):
                                        if playerPosition == move['destination'] and player not in eliminatedPlayers:
                                            message += f' {RED}Player {player}{CLEAR} is on this space.'
                                    for decorator in decorators[move['destination']]:
                                        message += f' There is also a {CYAN}{decorator["type"]}{CLEAR} on this space.'
                                    print(f'{" "*indent}{message}')
                                indent -= 1
                            indent -= 1
                        if item == 'f3 menu':
                            indent += 1
                            coordinates = ", ".join([f"{ORANGE}{axis}{CLEAR}: {GREEN}{playerPositions[currentPlayer][n]+1}{CLEAR}" for (n, axis) in enumerate(AXIS_ORDER)])
                            print(f'{" "*indent}Your coordinates are: ({coordinates}).')
                            indent -= 1
                        if item == 'safeword':
                            playerPositions[currentPlayer] = tuple(np.argwhere(board == "home")[0])
                        #where's the flamingo
                        if item == 'red potion':
                            indent += 1
                            if board[playerPositions[currentPlayer]] == 'shadow realm':
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
                            playerGreenPotionTurns[currentPlayer] += reward
                            print(f'{" "*indent}For the next {GREEN}{playerGreenPotionTurns[currentPlayer]}{CLEAR} round{"s" if playerGreenPotionTurns[currentPlayer] != 1 else ""}, you will know how many moves away the {FLAMINGO_SPACE}flamingo{CLEAR} space is!')
                            indent -= 1
                        if item == 'flamingo':
                            indent += 1
                            print(f'{" "*indent}Successfully placed a {FLAMINGO_SPACE}flamingo{CLEAR} on {GREEN}This Space{CLEAR}!')
                            if board[playerPositions[currentPlayer]] == 'shadow realm':
                                indent += 1
                                print(f'{" "*indent}The {FLAMINGO_SPACE}flamingo{CLEAR} {RED}got lost{CLEAR} in the {SHADOW_REALM_SPACE}shadow realm{CLEAR} and died.')
                                indent -= 1
                            else:
                                decorators[playerPositions[currentPlayer]].append({"type": 'flamingo', "placedBy": currentPlayer, "reward": 0})
                            indent -= 1
                        #violence is always the answer
                        if item == 'knife':
                            indent += 1
                            playersOnCurrentSpot = [n for n, pos in enumerate(playerPositions) if pos == playerPositions[currentPlayer] and n != currentPlayer and n not in eliminatedPlayers]
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
                            options = -1
                            for direction in sorted(copy.deepcopy(ALL_DIRECTIONS)):
                                options += 1
                                if NUM_DIMENSIONS < 4:
                                    print(f'{" "*indent}{options}: {GREEN}{direction.title()}{CLEAR}')
                                else:
                                    print(f'{" "*indent}{options}: In the {GREEN}{direction} direction{CLEAR}')
                            indent -= 1
                            direction = askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', options)
                            direction = convertLanguageDirectionsToLetters([sorted(copy.deepcopy(ALL_DIRECTIONS))[int(direction)]])[0]
                            plusOrMinus = (1 if direction[0] == '+' else -1)
                            axis = AXIS_ORDER.index(direction[1])
                            pos = list(copy.deepcopy(playerPositions[currentPlayer]))
                            foundSomeone = False
                            consts = [a for a in AXIS_ORDER if a != direction[1]]
                            possibleTargets = []
                            for m, playerPos in enumerate(playerPositions[1:]):
                                isInAxis = True
                                for n, const in enumerate(consts):
                                    if playerPos[AXIS_ORDER.index(const)] != playerPositions[currentPlayer][AXIS_ORDER.index(const)]:
                                        isInAxis = False
                                if isInAxis:
                                    possibleTargets.append((m+1, playerPos))
                            peopleShot = 0
                            while not foundSomeone:
                                pos[axis] += plusOrMinus
                                if pos[axis] >= GRID_SIZE:
                                    pos[axis] = 0
                                if pos[axis] <= -1:
                                    pos[axis] = GRID_SIZE-1
                                for player, playerPosition in possibleTargets:
                                    if playerPosition == tuple(pos):
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
                            decorators[playerPositions[currentPlayer]].append({"type": 'trap', "placedBy": currentPlayer, "reward": reward})
                            print(f'{" "*indent}Successfully placed a trap on {GREEN}This Space{CLEAR}!')
                            indent -= 1
                        if item == 'goblin':
                            indent += 1
                            print(f'{" "*indent}Successfully placed a goblin on {GREEN}This Space{CLEAR}!')
                            if board[playerPositions[currentPlayer]] == 'shadow realm':
                                indent += 1
                                print(f'{" "*indent}The goblin {RED}got lost{CLEAR} in the {SHADOW_REALM_SPACE}shadow realm{CLEAR} and died.')
                                indent -= 1
                            else:
                                decorators[playerPositions[currentPlayer]].append({"type": 'goblin', "placedBy": currentPlayer, "reward": reward})
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
                            playersOnCurrentSpot = [n for n, pos in enumerate(playerPositions) if pos == playerPositions[currentPlayer] and n != currentPlayer and n not in eliminatedPlayers]
                            if len(playersOnCurrentSpot) == 0:
                                print(f'{" "*indent}Unfortunately, {RED}No one{CLEAR} shares a space with you.')
                            else:
                                for player in playersOnCurrentSpot:
                                    playerSpeeds[player] -= 0.1
                                    playerSpeeds[player] = round(playerSpeeds[player], 4)
                                    if playerSpeeds[player] < MINIMUM_SPEED:
                                        playerSpeeds[player] = MINIMUM_SPEED
                                    print(f'{" "*indent}{RED}Player {player}{CLEAR} now has {GYM_SPACE}{playerSpeeds[player]} speed{CLEAR}.')
                            indent -= 1
                        if item == 'freeze ray':
                            indent += 1
                            player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the  player to be {CYAN}frozen{TURQUOISE} (1-{NUM_PLAYERS}):{CLEAR} ', False))
                            if player == -1:
                                print(f'{" "*indent}{RED}Unfortunately, there is no one to choose.{CLEAR}')
                            else:
                                playerFrozens[player] = True
                            indent -= 1
                        if item == 'swap':
                            indent += 1
                            candidates = [player for player in list(range(1,NUM_PLAYERS+1)) if player not in eliminatedPlayers]
                            if len(candidates) <= 1:
                                print(f'{" "*indent}{RED}Unfortunately, there is no one to choose.{CLEAR}')
                            else:
                                player1 = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the first player to be {TELEPORT_SPACE}swapped{TURQUOISE} (1-{NUM_PLAYERS}):{CLEAR} ', True))
                                valid = False
                                while not valid:
                                    player2 = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the second player to be {TELEPORT_SPACE}swapped{TURQUOISE} (1-{NUM_PLAYERS}):{CLEAR} ', True))
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
                            if board[playerPositions[currentPlayer]] == 'shadow realm':
                                print(f'{" "*indent}The gold potion is {RED}useless{CLEAR} in the {SHADOW_REALM_SPACE}shadow realm{CLEAR}. No {YELLOW}gold{CLEAR} was placed.')
                            else:
                                possibleMoves = findPossibleMoves(paths, playerPositions[currentPlayer], True, highwayInformation)
                                chosenSpace = random.choice(possibleMoves)['destination']
                                decorators[chosenSpace].append({"type": 'gold', "placedBy": currentPlayer, "reward": reward})
                                print(f'{" "*indent}Successfully placed {reward} gold on a random {ORANGE}Adjacent Space{CLEAR}!')
                            indent -= 1
                        if item == 'wand':
                            indent += 1
                            player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who will spin the {RED}Bad Wheel{TURQUOISE} at the start of their next turn (1-{NUM_PLAYERS}):{CLEAR} ', True))
                            if player == -1:
                                print(f'{" "*indent}{RED}Unfortunately, there is no one to choose.{CLEAR}')
                            else:   
                                playerWaitingForEvents[player].append('bad wheel')
                            indent -= 1
                        if item == 'time machine':
                            timeMachineIndex = reward
                            numEliminated = len(eliminatedPlayers)
                            if len(prevPlayerPositions) >= 1+NUM_PLAYERS-numEliminated:
                                playerRoles = prevPlayerRoles[-1-NUM_PLAYERS+numEliminated]
                                playerSpecialAbilities = prevPlayerSpecialAbilities[-1-NUM_PLAYERS+numEliminated]
                                playerPositions = prevPlayerPositions[-1-NUM_PLAYERS+numEliminated]
                                playerInventories = prevPlayerInventories[-1-NUM_PLAYERS+numEliminated]
                                playerGolds = prevPlayerGolds[-1-NUM_PLAYERS+numEliminated]
                                playerSpeeds = prevPlayerSpeeds[-1-NUM_PLAYERS+numEliminated]
                                playerFoodInventories = prevPlayerFoodInventories[-1-NUM_PLAYERS+numEliminated]
                                playerProgress = prevPlayerProgress[-1-NUM_PLAYERS+numEliminated]
                                playerStealBonus = prevPlayerStealBonus[-1-NUM_PLAYERS+numEliminated]
                                playerInvestmentBonus = prevPlayerInvestmentBonus[-1-NUM_PLAYERS+numEliminated]
                                playerQuests = prevPlayerQuests[-1-NUM_PLAYERS+numEliminated]
                                playerWaitingForEvents = prevPlayerWaitingForEvents[-1-NUM_PLAYERS+numEliminated]
                                playerFrozens = prevPlayerFrozens[-1-NUM_PLAYERS+numEliminated]
                                playerQuantumNotifications = prevPlayerQuantumNotifications[-1-NUM_PLAYERS+numEliminated]
                                playerEliminationReturns = prevPlayerEliminationReturns[-1-NUM_PLAYERS+numEliminated]
                                playerPoisoneds = prevPlayerPoisoneds[-1-NUM_PLAYERS+numEliminated]
                                playerHealedPoisons = prevPlayerHealedPoisons[-1-NUM_PLAYERS+numEliminated]
                                playerGreenPotionTurns = prevPlayerGreenPotionTurns[-1-NUM_PLAYERS+numEliminated]
                                itemPrices = prevItemPrices[-1-NUM_PLAYERS+numEliminated]
                                itemRewards = prevItemRewards[-1-NUM_PLAYERS+numEliminated]
                                decorators = prevDecorators[-1-NUM_PLAYERS+numEliminated]
                                pathDecorators = prevPathDecorators[-1-NUM_PLAYERS+numEliminated]
                                board = prevBoards[-1-NUM_PLAYERS+numEliminated]
                                quantumEntanglements = prevQuantumEntanglements[-1-NUM_PLAYERS+numEliminated]
                                blackHolePos = prevBlackHolePos[-1-NUM_PLAYERS+numEliminated]
                                blackHoleRadius = prevBlackHoleRadius[-1-NUM_PLAYERS+numEliminated]
                                eliminatedPlayers = prevEliminatedPlayers[-1-NUM_PLAYERS+numEliminated]
                                mewChance = prevMewChance[-1-NUM_PLAYERS+numEliminated]
                                for _ in range(NUM_PLAYERS-numEliminated):
                                    prevPlayerRoles.pop(-1)
                                    prevPlayerSpecialAbilities.pop(-1)
                                    prevPlayerPositions.pop(-1)
                                    prevPlayerInventories.pop(-1)
                                    prevPlayerGolds.pop(-1)
                                    prevPlayerSpeeds.pop(-1)
                                    prevPlayerFoodInventories.pop(-1)
                                    prevPlayerProgress.pop(-1)
                                    prevPlayerStealBonus.pop(-1)
                                    prevPlayerInvestmentBonus.pop(-1)
                                    prevPlayerQuests.pop(-1)
                                    prevPlayerWaitingForEvents.pop(-1)
                                    prevPlayerFrozens.pop(-1)
                                    prevPlayerQuantumNotifications.pop(-1)
                                    prevPlayerEliminationReturns.pop(-1)
                                    prevPlayerPoisoneds.pop(-1)
                                    prevPlayerHealedPoisons.pop(-1)
                                    prevPlayerGreenPotionTurns.pop(-1)
                                    prevItemPrices.pop(-1)
                                    prevItemRewards.pop(-1)
                                    prevDecorators.pop(-1)
                                    prevPathDecorators.pop(-1)
                                    prevBoards.pop(-1)
                                    prevQuantumEntanglements.pop(-1)
                                    prevBlackHolePos.pop(-1)
                                    prevBlackHoleRadius.pop(-1)
                                    prevEliminatedPlayers.pop(-1)
                                if f'time machine;{timeMachineIndex}' in playerInventories[currentPlayer]:
                                    playerInventories[currentPlayer].remove(f'time machine;{timeMachineIndex}')
                                for gameState in prevPlayerInventories:
                                    if f'time machine;{timeMachineIndex}' in gameState[currentPlayer]:
                                        gameState[currentPlayer].remove(f'time machine;{timeMachineIndex}')
                                itemDescriptions = redefineItemDescriptions()
                                indent += 1
                                print(f'{" "*indent}{GRAY}(regenerating map image...){CLEAR}')
                                indent -= 1
                                generateImage(board, paths, quantumEntanglements)
                                indent -= 2
                                return 'continue'
                            else:
                                indent += 1
                                print(f'{" "*indent}{RED}Unfortunately, the game has not existed long enough to rewind 1 round.{CLEAR}')
                                indent -= 1
                        if item == 'padlock':
                            indent += 1
                            code = int(askOptions(f'{" "*indent}{TURQUOISE}Enter the code for this {CYAN}padlock{TURQUOISE} (0-9999):{CLEAR} ', 9999))
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

def generateWingPlatter():
    global indent
    
    month = datetime.datetime.today().strftime('%B').lower()
    holiday = random.choice(WINGERIA_INGREDIENTS[month])
    meats = WINGERIA_INGREDIENTS['allTime']['meats']
    sauces = WINGERIA_INGREDIENTS['allTime']['sauces'] + holiday['sauces']
    sides = WINGERIA_INGREDIENTS['allTime']['sides'] + holiday['sides']
    dips = WINGERIA_INGREDIENTS['allTime']['dips'] + holiday['dips']
    
    output = 'a Wing Platter with\n'
    cost = 0
    totalMeats = 0
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
        cost += qty*0.0035
        totalMeats += qty
    numDips = random.randint(0,4)
    if numDips != 0:
        slots -= 1
    for _ in range(slots):
        side = random.choice(['on the left', '', 'on the right'])
        qty = random.randint(2,12)
        items.append(f'{GREEN}{qty}{CLEAR} {RED}{random.choice(sides)}{CLEAR}{" " if side != "" else ""}{side}')
        cost += qty*0.0005
    for _ in range(numDips):
        items.append(f'{CYAN}{random.choice(dips)}{CLEAR}')
        cost += 0.001
    newline = '\n'
    indent += 1
    for n, item in enumerate(items):
        output += f'{" "*indent}{item}{" and" if n == len(items)-2 else "," if n != len(items)-1 else ""}{newline if n != len(items)-1 else ""}'
    indent -= 1
    return output, cost, totalMeats

def addToFoodInventory(numIngredients):
    month = datetime.datetime.today().strftime('%B').lower()
    for _ in range(numIngredients):
        ingredientType = random.choice(['meats', 'meats', 'sauces', 'sides', 'dips'])
        if ingredientType != 'meats':
            ingredient = random.choice(WINGERIA_INGREDIENTS['allTime'][ingredientType] + random.choice(WINGERIA_INGREDIENTS[month])[ingredientType])
        else:
            ingredient = random.choice(WINGERIA_INGREDIENTS['allTime'][ingredientType])
        qty = (random.choice([1, 1, 2]) if ingredientType in ['sauces', 'dips'] else random.randint(4,12))
        if ingredient not in playerFoodInventories[currentPlayer][ingredientType].keys():
            playerFoodInventories[currentPlayer][ingredientType][ingredient] = qty
        else:
            playerFoodInventories[currentPlayer][ingredientType][ingredient] += qty

def constructOwnWingPlatter():
    global indent
    def printCurrentOrder(order):
        global indent
        print(f'{" "*indent}The current plate is:')
        indent += 1
        for n, item in enumerate(order):
            print(f'{" "*indent}{item}{"" if n == len(order)-1 else " and" if n == len(order)-2 else ","}')
        indent -= 1
    
    def askAboutMeat():
        global indent
        
        print(f'{" "*indent}Which {PAPAS_WINGERIA_SPACE}meat{CLEAR} would you like to add?')
        indent += 1
        for n, meat in enumerate(playerFoodInventories[currentPlayer]['meats'].keys()):
            print(f'{" "*indent}{n}: {meat}')
        indent -= 1
        choice = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your choice:{CLEAR} ', len(playerFoodInventories[currentPlayer]['meats'].keys())))
        meat = list(playerFoodInventories[currentPlayer]['meats'].keys())[choice]
        
        print(f'{" "*indent}How many {PAPAS_WINGERIA_SPACE}{meat}{CLEAR} would you like to add?')
        maxMeats = min(playerFoodInventories[currentPlayer]["meats"][meat], 12)
        qty = 0
        while qty == 0:
            qty = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your choice (1-{maxMeats}):{CLEAR} ', maxMeats))
        playerFoodInventories[currentPlayer]["meats"][meat] -= qty
        if playerFoodInventories[currentPlayer]["meats"][meat] == 0:
            del playerFoodInventories[currentPlayer]["meats"][meat]
        
        print(f'{" "*indent}Which {ORANGE}sauce{CLEAR} would you like to coat these {PAPAS_WINGERIA_SPACE}{meat}{CLEAR}?')
        indent += 1
        for n, sauce in enumerate(playerFoodInventories[currentPlayer]['sauces'].keys()):
            print(f'{" "*indent}{n}: {sauce}')
        indent -= 1
        choice = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your choice:{CLEAR} ', len(playerFoodInventories[currentPlayer]['sauces'].keys())-1))
        sauce = list(playerFoodInventories[currentPlayer]['sauces'].keys())[choice]
        playerFoodInventories[currentPlayer]["sauces"][sauce] -= 1
        if playerFoodInventories[currentPlayer]["sauces"][sauce] == 0:
            del playerFoodInventories[currentPlayer]["sauces"][sauce]
        
        return meat, qty, sauce
    
    def askAboutSides():
        global indent
        
        print(f'{" "*indent}Which {RED}side{CLEAR} would you like to add?')
        indent += 1
        for n, side in enumerate(playerFoodInventories[currentPlayer]['sides'].keys()):
            print(f'{" "*indent}{n}: {side}')
        indent -= 1
        choice = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your choice:{CLEAR} ', len(playerFoodInventories[currentPlayer]['sides'].keys())-1))
        side = list(playerFoodInventories[currentPlayer]['sides'].keys())[choice]
        
        print(f'{" "*indent}How many {RED}{side}{CLEAR} would you like to add?')
        maxSides = min(playerFoodInventories[currentPlayer]["sides"][side], 12)
        qty = 0
        while qty == 0:
            qty = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your choice (1-{maxSides}):{CLEAR} ', maxSides))
        playerFoodInventories[currentPlayer]["sides"][side] -= qty
        if playerFoodInventories[currentPlayer]["sides"][side] == 0:
            del playerFoodInventories[currentPlayer]["sides"][side]
        
        return side, qty
    
    def askAboutDips():
        global indent
        
        print(f'{" "*indent}Which {CYAN}dip{CLEAR} would you like to add?')
        indent += 1
        for n, dip in enumerate(playerFoodInventories[currentPlayer]['dips'].keys()):
            print(f'{" "*indent}{n}: {dip}')
        indent -= 1
        choice = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your choice:{CLEAR} ', len(playerFoodInventories[currentPlayer]['dips'].keys())))
        dip = list(playerFoodInventories[currentPlayer]['dips'].keys())[choice]
        playerFoodInventories[currentPlayer]["dips"][dip] -= 1
        if playerFoodInventories[currentPlayer]["dips"][dip] == 0:
            del playerFoodInventories[currentPlayer]["dips"][dip]
        
        return dip
    
    indent += 1
    currentOrder = []
    slotsRemaining = 7 + playerInvestmentBonus[currentPlayer]
    cost = 0
    
    print(f'{" "*indent}You have {GREEN}{slotsRemaining}{CLEAR} slots remaining.')
    indent += 1
    print(f'{" "*indent}{GRAY}(Each {PAPAS_WINGERIA_SPACE}meat{GRAY} takes up {GREEN}2{GRAY} slots, each {RED}side{GRAY} takes up {GREEN}1{GRAY} slot, and all {CYAN}dips{GRAY} collectively take up {GREEN}1{GRAY} slot, max {GREEN}4{CLEAR} {CYAN}dips{GRAY}){CLEAR}')
    indent -= 1
    
    meat, qty, sauce = askAboutMeat()
    cost += qty*0.0035
    currentOrder.append(f'{GREEN}{qty}{CLEAR} {PAPAS_WINGERIA_SPACE}{meat}{CLEAR} coated in {ORANGE}{sauce}{CLEAR}')
    slotsRemaining -= 2
    printCurrentOrder(currentOrder)
    print(f'{" "*indent}You have {GREEN}{slotsRemaining}{CLEAR} slots remaining.')
    if sum(playerFoodInventories[currentPlayer]['meats'].values()) > 0 and sum(playerFoodInventories[currentPlayer]['sauces'].values()) > 0 and slotsRemaining >= 2:
        meatsNotDone = True
    else:
        meatsNotDone = False
    while meatsNotDone:
        print(f'{" "*indent}Would you like to add more {PAPAS_WINGERIA_SPACE}meat{CLEAR}?')
        indent += 1
        print(f'{" "*indent}0: No')
        print(f'{" "*indent}1: Yes')
        indent -= 1
        choice = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your choice:{CLEAR} ', 1))
        if choice == 0:
            meatsNotDone = False
        else:
            indent += 1
            meat, qty, sauce = askAboutMeat()
            indent -= 1
            cost += qty*0.0035
            currentOrder.append(f'{GREEN}{qty}{CLEAR} {PAPAS_WINGERIA_SPACE}{meat}{CLEAR} coated in {ORANGE}{sauce}{CLEAR}')
            slotsRemaining -= 2
            printCurrentOrder(currentOrder)
            print(f'{" "*indent}You have {GREEN}{slotsRemaining}{CLEAR} slot{"s" if slotsRemaining > 1 else ""} remaining.')
            if not(sum(playerFoodInventories[currentPlayer]['meats'].values()) > 0 and sum(playerFoodInventories[currentPlayer]['sauces'].values()) > 0 and slotsRemaining >= 2):
                meatsNotDone = False
    
    if sum(playerFoodInventories[currentPlayer]['sides'].values()) > 0 and slotsRemaining >= 1:
        sidesNotDone = True
    else:
        sidesNotDone = False
    while sidesNotDone:
        print(f'{" "*indent}Would you like to a {RED}side{CLEAR}?')
        indent += 1
        print(f'{" "*indent}0: No')
        print(f'{" "*indent}1: Yes')
        indent -= 1
        choice = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your choice:{CLEAR} ', 1))
        if choice == 0:
            sidesNotDone = False
        else:
            indent += 1
            side, qty = askAboutSides()
            indent -= 1
            cost += qty*0.0005
            currentOrder.append(f'{GREEN}{qty}{CLEAR} {RED}{side}{CLEAR}')
            slotsRemaining -= 1
            printCurrentOrder(currentOrder)
            print(f'{" "*indent}You have {GREEN}{slotsRemaining}{CLEAR} slot{"s" if slotsRemaining > 1 else ""} remaining.')
            if not(sum(playerFoodInventories[currentPlayer]['sides'].values()) > 0 and slotsRemaining >= 1):
                sidesNotDone = False
    
    dipSlotsRemaining = 4
    if sum(playerFoodInventories[currentPlayer]['dips'].values()) > 0 and slotsRemaining >= 1:
        dipsNotDone = True
    else:
        dipsNotDone = False
    while dipsNotDone:
        print(f'{" "*indent}Would you like to add a {CYAN}dip{CLEAR}?')
        indent += 1
        print(f'{" "*indent}0: No')
        print(f'{" "*indent}1: Yes')
        indent -= 1
        choice = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your choice:{CLEAR} ', 1))
        if choice == 0:
            dipsNotDone = False
        else:
            indent += 1
            dip = askAboutDips()
            indent -= 1
            cost += 0.001
            currentOrder.append(f'{CYAN}{dip}{CLEAR}')
            dipSlotsRemaining -= 1
            printCurrentOrder(currentOrder)
            if not(sum(playerFoodInventories[currentPlayer]['dips'].values()) > 0 and dipSlotsRemaining >= 1):
                dipsNotDone = False
    
    indent -= 1
    return cost

def visitWingeria():
    global indent
    indent += 1
    for player, bonus in enumerate(playerInvestmentBonus):
        if player != 0 and player != currentPlayer and bonus != 0 and player not in eliminatedPlayers:
            print(f'{" "*indent}You must pay {RED}Player {player}{CLEAR} {YELLOW}{bonus} gold{CLEAR}!')
            playerGolds[currentPlayer] -= bonus
            playerGolds[player] += bonus
            indent += 1
            print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR} and {RED}Player {player}{CLEAR} now has {YELLOW}{playerGolds[player]} gold{CLEAR}.')
            indent -= 1
            time.sleep(0.5)
    order, cost, totalMeats = generateWingPlatter()
    print(f'{" "*indent}You ordered {order}.')
    playerSpeeds[currentPlayer] -= cost
    playerSpeeds[currentPlayer] = round(playerSpeeds[currentPlayer], 4)
    if playerSpeeds[currentPlayer] < MINIMUM_SPEED:
        playerSpeeds[currentPlayer] = MINIMUM_SPEED
    print(f'{" "*indent}You {RED}gained some weight{CLEAR}, so your speed is now {GYM_SPACE}{playerSpeeds[currentPlayer]}{CLEAR}.')
    updateQuests('eatChicken', totalMeats)
    if sum(playerFoodInventories[currentPlayer]['meats'].values()) > 0 and sum(playerFoodInventories[currentPlayer]['sauces'].values()) > 0:
        time.sleep(0.5)
        print(f'{" "*indent}Would you like to build your own {PAPAS_WINGERIA_SPACE}wing platter{CLEAR} to feed to {RED}another player{CLEAR}?')
        indent += 1
        print(f'{" "*indent}0: No')
        print(f'{" "*indent}1: Yes')
        indent -= 1
        choice = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your choice:{CLEAR} ', 1))
        if choice == 1:
            cost = round(constructOwnWingPlatter(), 4)
            player = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who you will {RED}feed this plate to{TURQUOISE}, to lose {GYM_SPACE}{cost}{TURQUOISE} speed (1-{NUM_PLAYERS}):{CLEAR} ', False))
            if player == -1:
                print(f'{" "*indent}{RED}Unfortunately, there is no one to choose who to give the plate to.{CLEAR}')
            else:
                playerSpeeds[player] -= cost
                playerSpeeds[player] = round(playerSpeeds[player], 4)
                if playerSpeeds[player] < MINIMUM_SPEED:
                    playerSpeeds[player] = MINIMUM_SPEED
            indent += 1
            print(f'{" "*indent}{RED}Player {player}{CLEAR} now has {GYM_SPACE}{playerSpeeds[player]} speed{CLEAR}.')
            indent -= 1
    if playerGolds[currentPlayer] > 0:
        time.sleep(0.5)
        print(f'{" "*indent}Would you like to {YELLOW}invest{CLEAR} in {PAPAS_WINGERIA_SPACE}papa\'s wingeria{CLEAR}? (you have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR})')
        indent += 1
        print(f'{" "*indent}Once you invest {YELLOW}{WINGERIA_PROGRESS_REQUIRED} gold{CLEAR} you will recieve {YELLOW}1 gold{CLEAR} each time someone visits the {PAPAS_WINGERIA_SPACE}wingeria{CLEAR}!')
        print(f'{" "*indent}You will also recieve an {GREEN}additional slot{CLEAR} when building your {PAPAS_WINGERIA_SPACE}own platter{CLEAR} for another player.')
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
            print(f'{" "*indent}{GREEN}Congratulations!{CLEAR} You now have {GREEN}{7+playerInvestmentBonus[currentPlayer]}{CLEAR} {PAPAS_WINGERIA_SPACE}platter slots{CLEAR} and steal {YELLOW}{playerInvestmentBonus[currentPlayer]} gold{CLEAR} each time a player visits the {PAPAS_WINGERIA_SPACE}wingeria{CLEAR}!')
            indent -= 1
        indent -= 2
    indent -= 1
    
def visitGym():
    global indent
    global mewChance
    indent += 1
    print(f'{" "*indent}Which workout would you like to do?')
    indent += 1
    print(f'{" "*indent}0: Squats - Increase your {GYM_SPACE}speed{CLEAR}.')
    print(f'{" "*indent}1: Bicep Curls - Increase the {YELLOW}gold{CLEAR} you get from stealing and {CYAN}green potion{CLEAR} duration.')
    print(f'{" "*indent}2: Mewing - {RED}{int(mewChance*100)}% chance{CLEAR} of doubling {GYM_SPACE}speed{CLEAR} and {YELLOW}gold{CLEAR}.')
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
            playerProgress[currentPlayer]["gym"] = 0
            playerStealBonus[currentPlayer] += 1
            print(f'{" "*indent}{GREEN}Congratulations!{CLEAR} You now steal one more {YELLOW}gold{CLEAR} and your {CYAN}green potions{CLEAR} last {ORANGE}{1+playerStealBonus[currentPlayer]} rounds{CLEAR}.')
            for n, item in enumerate(playerInventories[currentPlayer]):
                if ';' in item and 'time machine' not in item:
                    split = item.split(';')
                    playerInventories[currentPlayer][n] = f'{split[0]};{int(split[1])+1}'
            indent -= 1
        indent -= 1
    if choice == 2:
        indent += 1
        if random.random() <= mewChance:
            print(f'{" "*indent}{GREEN}Your mewing paid off!{CLEAR}')
            playerSpeeds[currentPlayer] *= 2
            print(f'{" "*indent}Your speed is now {GYM_SPACE}{playerSpeeds[currentPlayer]}{CLEAR}.')
            playerGolds[currentPlayer] *= 2
            print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
        else:
            print(f'{" "*indent}{RED}Unfortunately,{CLEAR} your {GYM_SPACE}{random.randint(1, 24)} hour mewing exercise{CLEAR} did nothing!')
        indent -= 1
    indent -= 1

def entanglementSpace():
    global indent
    global blackHolePos
    global blackHoleRadius
    hasBeenEliminated = False
    indent += 1
    print(f'{" "*indent}2 random spaces have now become {ENTANGLEMENT_SPACE}quantum-entangled{CLEAR}!')
    print(f'{" "*indent}If you are on a space that has been {ENTANGLEMENT_SPACE}quantum-entangled{CLEAR}, there is a {RED}50% chance{CLEAR} you will be {TELEPORT_SPACE}teleported{CLEAR} to the other one.')
    firstSpace = selectRandomSpace(board)
    secondSpace = firstSpace
    while firstSpace == secondSpace:
        secondSpace = selectRandomSpace(board)
    quantumEntanglements.append([firstSpace, secondSpace])
    indent += 1
    print(f'{" "*indent}{GRAY}(regenerating map image...){CLEAR}')
    indent -= 1
    generateImage(board, paths, quantumEntanglements)
    indent += 1
    if len(quantumEntanglements) == 5:
        print(f'{" "*indent}{GRAY}Hmmm.... Something feels a little {SHADOW_REALM_SPACE}off{GRAY}...{CLEAR}')
    if len(quantumEntanglements) == 10:
        print(f'{" "*indent}{GRAY}You begin to feel something {SHADOW_REALM_SPACE}strange{GRAY}...{CLEAR}')
    if len(quantumEntanglements) == 15:
        print(f'{" "*indent}{RED}Uh oh!{GRAY} What you were feeling is the {SHADOW_REALM_SPACE}destabilising of reality{GRAY}! If you create more {ENTANGLEMENT_SPACE}entanglements{GRAY} it will only get worse...{CLEAR}')
    if len(quantumEntanglements) == 20:
        print(f'{" "*indent}{GRAY}Reality has been {SHADOW_REALM_SPACE}destabilised{GRAY} quite a bit now... do {RED}NOT{GRAY} keep making {ENTANGLEMENT_SPACE}entanglements{GRAY}.{CLEAR}')
    if len(quantumEntanglements) == 25:
        print(f'{" "*indent}{GRAY}Reality has been {SHADOW_REALM_SPACE}destabilised{GRAY} too far... A {SHADOW_REALM_SPACE}black hole{GRAY} has formed on this space.{CLEAR}')
        blackHolePos = playerPositions[currentPlayer]
        blackHoleRadius = 0
        indent += 1
        print(f'{" "*indent}{YELLOW}Player {currentPlayer},{RED} You have been swallowed by the {SHADOW_REALM_SPACE}black hole{RED} and have been permanently ELIMINATED.{CLEAR}')
        eliminatedPlayers.append(currentPlayer)
        hasBeenEliminated = True
        indent -= 1
    indent -= 1
    if playerGolds[currentPlayer] >= 3 and not hasBeenEliminated:
        print(f'{" "*indent}Would you like to pay {YELLOW}3 gold{CLEAR} to be {GREEN}notified{CLEAR} the next 2 times you get {ENTANGLEMENT_SPACE}quantum teleported{CLEAR}?')
        indent += 1
        print(f'{" "*indent}0: No')
        print(f'{" "*indent}1: Yes')
        indent -= 1
        choice = askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', 1)
        if choice == '1':
            indent += 1
            playerQuantumNotifications[currentPlayer] += 2
            playerGolds[currentPlayer] -= 3
            print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
            indent -= 1
    indent -= 1
    return hasBeenEliminated

def printRoles(roles, specialAbilities):
    global indent
    os.system('clear')
    for player in range(1, NUM_PLAYERS+1):
        print(f'{" "*17}{ORANGE}Role Assignment{CLEAR}')
        print('-'*50)
        print(f'{YELLOW}Player {player}{CLEAR}, it is time to reveal your role.')
        indent += 1
        print(f'{" "*indent}Ensure that {RED}no other player{CLEAR} can see the screen.')
        indent -= 1
        input(f'{TURQUOISE}Press Enter when you are ready {CLEAR}')
        print(f'{"-"*50}')
        indent += 1
        print(f'{" "*indent}Your role is the {grammatiseRole(roles[player])}.')
        if playerRoles[player] == 'Finder':
            indent += 1
            print(f'{" "*indent}To {GREEN}win the game{CLEAR}, you must find the {FLAMINGO_SPACE}flamingo space{CLEAR} and play a {FLAMINGO_SPACE}flamingo game{CLEAR}.')
            print(f'{" "*indent}If you are {RED}voted out{CLEAR}, you will be {RED}eliminated{CLEAR} for {ORANGE}{VOTING_FREQUENCY//4} rounds{CLEAR}.')
            indent += 1
            print(f'{" "*indent}{GRAY}The purpose of this sentence is to make the length of each description roughly the same.')
            print(f'{" "*indent}This is so that you can\'t determine anything based on the length of time reading the rules.{CLEAR}')
            indent -= 2
        if playerRoles[player] == 'Staller':
            indent += 1
            print(f'{" "*indent}To {GREEN}win the game{CLEAR}, the game must last for {ORANGE}{STALLER_WIN} rounds{CLEAR}.')
            print(f'{" "*indent}After your {ORANGE}{STALLER_WIN}th round{CLEAR}, and every subsequent {ORANGE}5 rounds{CLEAR}, you will play a {FLAMINGO_SPACE}flamingo game{CLEAR} to {GREEN}win the game{CLEAR}.')
            print(f'{" "*indent}If you are {RED}voted out{CLEAR}, you will be {RED}eliminated{CLEAR} for {ORANGE}{VOTING_FREQUENCY//4} rounds{CLEAR}.')
            indent += 1
            print(f'{" "*indent}The {RED}Staller{CLEAR} role will also be passed onto one of the {CYAN}Finders{CLEAR}.')
            indent -= 1
            if OTHERS_CANT_SEE_FLAMINGO:
                print(f'{" "*indent}For you, the {FLAMINGO_SPACE}flamingo space{CLEAR} will act as an {EMPTY_SPACE}empty space{CLEAR}.')
            indent -= 1
        if playerRoles[player] == 'Jester':
            indent += 1
            print(f'{" "*indent}To {GREEN}win the game{CLEAR}, you must get {RED}voted out{CLEAR}.')
            print(f'{" "*indent}If you are {RED}voted out{CLEAR}, you will play a {FLAMINGO_SPACE}flamingo game{CLEAR} to {GREEN}win the game{CLEAR}.')
            indent += 1
            print(f'{" "*indent}If you fail the {FLAMINGO_SPACE}flamingo game{CLEAR}, the {PINK}Jester{CLEAR} role will be passed onto one of the {CYAN}Finders{CLEAR}.')
            indent -= 1
            if OTHERS_CANT_SEE_FLAMINGO:
                print(f'{" "*indent}For you, the {FLAMINGO_SPACE}flamingo space{CLEAR} will act as an {EMPTY_SPACE}empty space{CLEAR}.')
            indent -= 1
        if CHAOS_MODE:
            print(f'{"-"*50}')
            if specialAbilities[player] == 'None':
                print(f'{" "*indent}You {RED}do not{CLEAR} have a special ability.')
            else:
                print(f'{" "*indent}Your special ability is the {grammatiseRole(specialAbilities[player])}.')
                if specialAbilities[player] == 'Murderer':
                    indent += 1
                    print(f'{" "*indent}During the vote, you will have the option to {getAbilityDescription(specialAbilities[player])}.')
                    print(f'{" "*indent}They will be {RED}eliminated from the game{CLEAR} for {ORANGE}{VOTING_FREQUENCY//4} rounds{CLEAR}.')
                    indent += 1
                    if 'Medic' in specialAbilities:
                        print(f'{" "*indent}A {GREEN}Medic{CLEAR} may shield the {YELLOW}chosen player{CLEAR} from {RED}murder{CLEAR}')
                    indent -= 1
                    print(f'{" "*indent}The {YELLOW}remaining players{CLEAR} will be alerted during the {ORANGE}voting results{CLEAR}.')
                    indent -= 1
                if specialAbilities[player] == 'Toxicologist':
                    indent += 1
                    print(f'{" "*indent}During the vote, you will have the option to {getAbilityDescription(specialAbilities[player])}.')
                    indent += 1
                    print(f'{" "*indent}The {YELLOW}chosen player{CLEAR} will not be notified.')
                    indent -= 1
                    print(f'{" "*indent}The {YELLOW}chosen player{CLEAR} will begin to feel various {DARK_GREEN}symptoms{CLEAR} over the next {ORANGE}{VOTING_FREQUENCY} rounds{CLEAR}.')
                    print(f'{" "*indent}{DARK_GREEN}Symptoms{CLEAR} will be given at random, including:')
                    indent += 1
                    print(f'{" "*indent}Not being able to move,')
                    print(f'{" "*indent}Loosing {GYM_SPACE}speed{CLEAR},')
                    print(f'{" "*indent}Throwing up {GREEN}acid{CLEAR}, which will act the same as a {CYAN}trap{CLEAR} but in reverse,',)
                    indent -= 1
                    print(f'{" "*indent}And will end with them being {RED}eliminated{CLEAR} for {ORANGE}{VOTING_FREQUENCY//6} rounds{CLEAR} before the next vote.')
                    if 'Medic' in specialAbilities:
                        print(f'{" "*indent}A {GREEN}Medic{CLEAR} will be able to heal a {DARK_GREEN}poisoned{CLEAR} player by occupying the {ORANGE}same space{CLEAR} as them.')
                    indent -= 1
                if specialAbilities[player] == 'Seer':
                    indent += 1
                    print(f'{" "*indent}During the vote, you will have the option to {getAbilityDescription(specialAbilities[player])}.')
                    print(f'{" "*indent}You will find out the {YELLOW}chosen player\'s{CLEAR} role {GREEN}and{CLEAR} special ability.')
                    indent += 1
                    print(f'{" "*indent}Only you will see this {INFORMATION_SPACE}information{CLEAR}.')
                    indent -= 2
                if specialAbilities[player] == 'Guesser':
                    indent += 1
                    print(f'{" "*indent}During the vote, you will have the option to {getAbilityDescription(specialAbilities[player])}.')
                    indent += 1
                    print(f'{" "*indent}You {RED}cannot{CLEAR} choose yourself.')
                    indent -= 1
                    print(f'{" "*indent}If you guess {GREEN}correctly{CLEAR}, you will also be able to use {YELLOW}that player\'s{CLEAR} special ability.')
                    print(f'{" "*indent}If you guess {RED}incorrectly{CLEAR}, you will be {RED}eliminated from the game{CLEAR} for {ORANGE}{VOTING_FREQUENCY//4} rounds{CLEAR}.')
                    if 'Murderer' in specialAbilities:
                        indent += 1
                        print(f'{" "*indent}It will look the same as if the {RED}Murderer{CLEAR} had {RED}murdered{CLEAR} you.')
                        indent -= 1
                    indent -= 1
                if specialAbilities[player] == 'Medic':
                    indent += 1
                    if 'Murderer' in specialAbilities:
                        print(f'{" "*indent}During the vote, you will have the option to {getAbilityDescription(specialAbilities[player])}.')
                        indent += 1
                        print(f'{" "*indent}The {YELLOW}other players{CLEAR} will see that someone tried to {RED}murder{CLEAR} the {YELLOW}chosen player{CLEAR}, and that it was {GREEN}shielded{CLEAR}')
                        indent -= 1
                    if 'Toxicologist' in specialAbilities:
                        print(f'{" "*indent}If you land on the {ORANGE}same space{CLEAR} as a player who has been {DARK_GREEN}poisoned{CLEAR} by the {DARK_GREEN}Toxicologist{CLEAR},')
                        print(f'{" "*indent}They will be {GREEN}healed{CLEAR} {ORANGE}{VOTING_FREQUENCY//10} to {VOTING_FREQUENCY//3} rounds{CLEAR} later.')
                    indent -= 1
                if specialAbilities[player] == 'Cleaner':
                    indent += 1
                    print(f'{" "*indent}During the vote, you will have the option to {getAbilityDescription(specialAbilities[player])}.')
                    indent -= 1
                if specialAbilities[player] == 'Mewer':
                    indent += 1
                    print(f'{" "*indent}During the vote, you will have the option to {getAbilityDescription(specialAbilities[player])}.')
                    indent -= 1
                if specialAbilities[player] == 'Swapper':
                    indent += 1
                    print(f'{" "*indent}During the vote, you will have the option to {getAbilityDescription(specialAbilities[player])}.')
                    indent += 1
                    print(f'{" "*indent}You may choose yourself.')
                    indent -= 2
        indent -= 1
        print('-'*50)
        input(f'{TURQUOISE}Press Enter to Continue {CLEAR}')
        os.system('clear')

def evaluateVote(final):
    global indent
    global currentPlayer
    global voteSwaps
    global murderedPlayers
    global shieldedPlayers
    global guesserFailed
    #voting preamble
    os.system('clear')
    if final:
        print(f'{" "*19}{ORANGE}Final Voting{CLEAR}')
    else:
        print(f'{" "*23}{ORANGE}Voting{CLEAR}')
    print('-'*50)
    print(f'{" "*indent}{YELLOW}Players{CLEAR}, it is time to vote on who you believe is the {RED}Staller{CLEAR}.')
    indent += 1
    if final:
        print(f'{" "*indent}If you correctly identify the {RED}Staller{CLEAR}, they will be {RED}permanently eliminated{CLEAR} from the game.')
        indent += 1
        print(f'{" "*indent}Every {ORANGE}5 rounds{CLEAR}, a random {CYAN}Finder{CLEAR} will be picked to play a {FLAMINGO_SPACE}flamingo game{CLEAR} to {GREEN}win the game{CLEAR}.')
        print(f'{" "*indent}If they fail, they will be {RED}permanently eliminated{CLEAR}.')
        print(f'{" "*indent}The {PINK}Jester{CLEAR} will be picked last to attempt the {FLAMINGO_SPACE}flamingo game{CLEAR}.')
        indent -= 1
        print(f'{" "*indent}Otherwise, the {RED}Staller{CLEAR} will have a chance every {ORANGE}5 rounds{CLEAR} to {GREEN}win the game{CLEAR} by playing a {FLAMINGO_SPACE}flamingo game{CLEAR}.')
        print(f'{" "*indent}If you instead vote out a {CYAN}Finder{CLEAR}, they will be {RED}eliminated{CLEAR} from the game for {ORANGE}{VOTING_FREQUENCY//4} rounds{CLEAR}.')
        print(f'{" "*indent}The {PINK}Jester{CLEAR} will also able to find the {FLAMINGO_SPACE}flamingo space{CLEAR} after this vote.')
    else:
        print(f'{" "*indent}The player you vote out will be {RED}eliminated{CLEAR} from the game for {ORANGE}{VOTING_FREQUENCY//4} rounds{CLEAR}.')
        print(f'{" "*indent}If you correctly identify the {RED}Staller{CLEAR}, the {RED}Staller{CLEAR} role will be passed onto one of the {CYAN}Finders{CLEAR}.')
    print(f'{" "*indent}If you vote for the {PINK}Jester{CLEAR}, they will have a chance to {GREEN}win the game{CLEAR} by playing a {FLAMINGO_SPACE}flamingo game{CLEAR}.')
    print(f'{" "*indent}If there is a {ORANGE}tie{CLEAR}, no one will be {RED}eliminated{CLEAR}.')
    indent += 1
    print(f'{" "*indent}You will vote in {RED}private{CLEAR}, in a {ORANGE}random order{CLEAR} and then all votes will be {RED}revealed{CLEAR}.')
    indent -= 2
    print('-'*50)
    input(f'{TURQUOISE}Press Enter when you are ready to vote {CLEAR}')
    #actual voting
    voteOrder = list(range(1, NUM_PLAYERS+1))
    random.shuffle(voteOrder)
    votes = [None]
    individualVotes = [None]
    for _ in range(NUM_PLAYERS):
        votes.append(0)
        individualVotes.append(0)
    voteSwaps = []
    murderedPlayers = []
    shieldedPlayers = []
    guesserFailed = False
    for player in voteOrder:
        if player not in eliminatedPlayers:
            currentPlayer = player
            os.system('clear')
            if final:
                print(f'{" "*19}{ORANGE}Final Voting{CLEAR}')
            else:
                print(f'{" "*23}{ORANGE}Voting{CLEAR}')
            print('-'*50)
            print(f'{YELLOW}Player {player}{CLEAR}, ensure that {RED}no other player{CLEAR} can see the screen.')
            indent += 1
            vote = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who you think is the {RED}Staller{TURQUOISE} (1-{NUM_PLAYERS}): {CLEAR}', False))
            votes[vote] += 1
            individualVotes[player] = vote
            indent -= 1
            if CHAOS_MODE:
                if (playerSpecialAbilities[player] != 'None') and not ('Toxicologist' in playerSpecialAbilities and playerSpecialAbilities[player] == 'Medic'):
                    print('-'*50)
                    print(f'Due to your special ability ({grammatiseRole(playerSpecialAbilities[player])}), you now have the option to {getAbilityDescription(playerSpecialAbilities[player])}')
                    indent += 1
                    print(f'{" "*indent}Would you like to use your special ability?')
                    indent += 1
                    print(f'{" "*indent}0: No')
                    print(f'{" "*indent}1: Yes')
                    indent -= 1
                    useAbility = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', 1))
                    if useAbility == 1:
                        indent += 1
                        evalSpecialAbility(playerSpecialAbilities[player])
                        indent -= 1
                    indent -= 1
            print('-'*50)
            input(f'{TURQUOISE}Press Enter to Continue {CLEAR}')
    currentPlayer = 1
    #make swaps from the swapper
    for swap in voteSwaps:
        temp = votes[swap[0]]
        votes[swap[0]] = votes[swap[1]]
        votes[swap[1]] = temp
        for n, individualVote in enumerate(individualVotes):
            if individualVote == swap[0]:
                individualVotes[n] = swap[1]
            elif individualVote == swap[1]:
                individualVotes[n] = swap[0]
    #reveal voting results
    os.system('clear')
    if final:
        print(f'{" "*19}{ORANGE}Final Voting{CLEAR}')
    else:
        print(f'{" "*23}{ORANGE}Voting{CLEAR}')
    print('-'*50)
    tie = False
    voted = votes.index(max([vote for vote in votes if vote != None]))
    if votes.count(max([vote for vote in votes if vote != None])) > 1:
        tie = True
    input(f'{TURQUOISE}Press Enter to see the results {CLEAR}')
    indent += 1
    for player in range(1, NUM_PLAYERS+1):
        if player not in eliminatedPlayers:
            print(f'{" "*indent}{YELLOW}Player {player}{CLEAR} voted for...')
            time.sleep(1.5)
            print(f'\x1B[A\x1B[2K{" "*indent}{YELLOW}Player {player}{CLEAR} voted for {YELLOW}Player {individualVotes[player]}{CLEAR}')
            time.sleep(0.75)
    indent -= 1
    #evaluation
    rearrangeRoles = False
    jesterWon = False
    if tie:
        print(f'That means there was a {ORANGE}tie{CLEAR}, so no one will be {RED}eliminated{CLEAR}!')
    else:
        print(f'That means {YELLOW}Player {voted}{CLEAR} was voted out.')
        input(f'{TURQUOISE}Press Enter to reveal the identity of {YELLOW}Player {voted}{TURQUOISE} {CLEAR}')
        indent += 1
        print(f'{" "*indent}{YELLOW}Player {voted}{CLEAR} is a...')
        time.sleep(2)
        print(f'\x1B[A\x1B[2K{" "*indent}{YELLOW}Player {voted}{CLEAR} is a {grammatiseRole(playerRoles[voted])}!')
        time.sleep(0.75)
        if playerRoles[voted] == 'Finder':
            indent += 1
            print(f'{" "*indent}{RED}Unfortunately{CLEAR}, you have voted out a {CYAN}Finder{CLEAR}!')
            print(f'{" "*indent}{YELLOW}Player {voted}{CLEAR}, you have been {RED}eliminated{CLEAR} for {ORANGE}{VOTING_FREQUENCY//4} rounds{CLEAR} and will return on {ORANGE}round {roundNum+(VOTING_FREQUENCY//4)}{CLEAR}.')
            eliminatedPlayers.append(voted)
            playerEliminationReturns[voted] = roundNum+(VOTING_FREQUENCY//4)
            if final:
                indent += 1
                print(f'{" "*indent}The {PINK}Jester{CLEAR} is now also able to find the {FLAMINGO_SPACE}flamingo space{CLEAR}.')
                indent -= 1
            indent -= 1
        if playerRoles[voted] == 'Staller':
            indent += 1
            print(f'{" "*indent}{GREEN}Congratulations!{CLEAR} You have correctly identified the {RED}Staller{CLEAR}!')
            if not final:
                print(f'{" "*indent}{YELLOW}Player {voted}{CLEAR}, you have been {RED}eliminated{CLEAR} for {ORANGE}{VOTING_FREQUENCY//4} rounds{CLEAR} and will return on {ORANGE}round {roundNum+(VOTING_FREQUENCY//4)}{CLEAR}.')
                eliminatedPlayers.append(voted)
                playerEliminationReturns[voted] = roundNum+(VOTING_FREQUENCY//4)
                print(f'{" "*indent}The role of {RED}Staller{CLEAR} must now be reassinged.')
                oldStaller = playerRoles.index('Staller')
                finders = [n for n, role in enumerate(playerRoles) if role == 'Finder']
                newStaller = random.choice(finders)
                playerRoles[newStaller] = 'Staller'
                playerRoles[oldStaller] = 'Finder'
                if CHAOS_MODE:
                    playerSpecialAbilities[newStaller] = random.choice(['Murderer', 'Toxicologist'])
                    playerSpecialAbilities[oldStaller] = random.choice(['Medic', 'Cleaner', 'Mewer', 'Swapper', 'None', 'None'])
                rearrangeRoles = True
            else:
                print(f'{" "*indent}{YELLOW}Player {voted}{CLEAR}, you have been {RED}permanently eliminated{CLEAR} from the game.')
                eliminatedPlayers.append(voted)
                print(f'{" "*indent}{CYAN}Finders{CLEAR}, every {ORANGE}5 rounds{CLEAR} one of you will be picked to play a {FLAMINGO_SPACE}flamingo game{CLEAR} to {GREEN}win the game{CLEAR}!')
                print(f'{" "*indent}If you fail, you will be {RED}permanently eliminated{CLEAR}.')
                indent += 1
                print(f'{" "*indent}The {PINK}Jester{CLEAR} will be picked last to attempt the {FLAMINGO_SPACE}flamingo game{CLEAR}.')
                print(f'{" "*indent}The {PINK}Jester{CLEAR} is now also able to find the {FLAMINGO_SPACE}flamingo space{CLEAR}.')
                indent -= 1
            indent -= 1
        if playerRoles[voted] == 'Jester':
            indent += 1
            print(f'{" "*indent}{RED}Unfortunately{CLEAR}, you have voted out the {PINK}Jester{CLEAR}!')
            print(f'{" "*indent}{YELLOW}Player {voted}{CLEAR}, you now have a chance to {GREEN}win the game{CLEAR} by playing a {FLAMINGO_SPACE}flamingo game{CLEAR}.')
            time.sleep(1)
            won = spinTheFlamingoWheel()
            if not won:
                print(f'{" "*indent}{RED}You lost!{CLEAR}')
                if not final:
                    print(f'{" "*indent}The role of {PINK}Jester{CLEAR} must now be reassinged.')
                    oldJester = playerRoles.index('Jester')
                    finders = [n for n, role in enumerate(playerRoles) if role == 'Finder']
                    newJester = random.choice(finders)
                    playerRoles[newJester] = 'Jester'
                    playerRoles[oldJester] = 'Finder'
                    if CHAOS_MODE:
                        playerSpecialAbilities[newJester] = random.choice(['Seer', 'Guesser'])
                        playerSpecialAbilities[oldJester] = random.choice(['Medic', 'Cleaner', 'Mewer', 'Swapper', 'None', 'None'])
                    rearrangeRoles = True
                else:
                    print(f'{" "*indent}The {PINK}Jester{CLEAR} is now also able to find the {FLAMINGO_SPACE}flamingo space{CLEAR}.')
            else:
                print(f'{" "*indent}{GREEN}Congratulations! You Win!{CLEAR}')
                jesterWon = True
            indent -= 1
        indent -= 1
    #evaluate murder
    for player in range(1, NUM_PLAYERS+1):
        if player not in eliminatedPlayers:
            if player in murderedPlayers and player not in shieldedPlayers:
                print(f'{" "*indent}{YELLOW}Player {player}{CLEAR} has been {RED}murdered{CLEAR}!')
                indent += 1
                print(f'{" "*indent}They have been {RED}eliminated{CLEAR} for {ORANGE}{VOTING_FREQUENCY//4} rounds{CLEAR} and will return on {ORANGE}round {roundNum+(VOTING_FREQUENCY//4)}{CLEAR}.')
                eliminatedPlayers.append(player)
                playerEliminationReturns[player] = roundNum+(VOTING_FREQUENCY//4)
                indent -= 1
            elif player in murderedPlayers and player in shieldedPlayers:
                print(f'{" "*indent}The {RED}Murderer{CLEAR} tried to {RED}murder{CLEAR} {YELLOW}Player {player}{CLEAR}, but they were {GREEN}shielded{CLEAR}!')
            elif guesserFailed:
                if player == playerSpecialAbilities.index('Guesser'):
                    print(f'{" "*indent}{YELLOW}Player {player}{CLEAR} has been {RED}murdered{CLEAR}!')
                    indent += 1
                    print(f'{" "*indent}They have been {RED}eliminated{CLEAR} for {ORANGE}{VOTING_FREQUENCY//4} rounds{CLEAR} and will return on {ORANGE}round {roundNum+(VOTING_FREQUENCY//4)}{CLEAR}.')
                    eliminatedPlayers.append(player)
                    playerEliminationReturns[player] = roundNum+(VOTING_FREQUENCY//4)
                    indent -= 1
    #continue to game
    print('-'*50)
    if not jesterWon:
        if rearrangeRoles:
            input(f'{TURQUOISE}Press Enter when you are ready to reveal the new roles {CLEAR}')
            printRoles(playerRoles, playerSpecialAbilities)
        else:
            input(f'{TURQUOISE}Press Enter to return back to the game {CLEAR}')
        os.system('clear')
    return jesterWon

def evalSpecialAbility(specialAbility):
    global indent
    global mewChance
    global guesserFailed
    if specialAbility == 'Murderer':
        chosenPlayer = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who you want to {RED}murder{TURQUOISE} (1-{NUM_PLAYERS}): {CLEAR}', False))
        murderedPlayers.append(chosenPlayer)
    if specialAbility == 'Toxicologist':
        chosenPlayer = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who you want to {DARK_GREEN}poison{TURQUOISE} (1-{NUM_PLAYERS}): {CLEAR}', False))
        playerPoisoneds[chosenPlayer] = {"symptomStart": roundNum+VOTING_FREQUENCY//6, "elimination": roundNum+5*(VOTING_FREQUENCY//6), "eliminationReturn": roundNum+6*(VOTING_FREQUENCY//6)}
    if specialAbility == 'Seer':
        chosenPlayer = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who you want to {CYAN}see the role{TURQUOISE} of (1-{NUM_PLAYERS}): {CLEAR}', False))
        indent += 1
        print(f'{" "*indent}{YELLOW}Player {chosenPlayer}{CLEAR} is a {grammatiseRole(playerRoles[chosenPlayer])}.')
        if playerSpecialAbilities[chosenPlayer] == 'None':
            print(f'{" "*indent}They {RED}do not{CLEAR} have a special ability.')
        else:
            print(f'{" "*indent}Their special ability is a {grammatiseRole(playerSpecialAbilities[chosenPlayer])}.')
        indent -= 1
    if specialAbility == 'Guesser':
        chosenPlayer = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who you want to {YELLOW}guess the special ability{TURQUOISE} of (1-{NUM_PLAYERS}): {CLEAR}', False))
        allAbilities = ['None', 'Murderer', 'Toxicologist', 'Seer', 'Guesser', 'Medic', 'Cleaner', 'Mewer', 'Swapper']
        indent += 1
        print(f'{" "*indent}What special ability do you think {YELLOW}Player {chosenPlayer}{CLEAR} has?')
        indent += 1
        for n, ability in enumerate(allAbilities):
            print(f'{" "*indent}{n}: {grammatiseRole(ability)}')
        indent -= 1
        guess = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', len(allAbilities)))
        indent += 1
        if allAbilities[guess] == playerSpecialAbilities[chosenPlayer]:
            if playerSpecialAbilities[chosenPlayer] == 'None':
                print(f'{" "*indent}That is {GREEN}correct{CLEAR}!')
            else:
                print(f'{" "*indent}That is {GREEN}correct{CLEAR}! You now must use the ability of the {grammatiseRole(playerSpecialAbilities[chosenPlayer])}.')
            indent += 1
            if playerSpecialAbilities[chosenPlayer] == 'None' or (playerSpecialAbilities[chosenPlayer] == 'Medic' and 'Toxicologist' in playerSpecialAbilities):
                print(f'{" "*indent}{RED}Unfortunately,{CLEAR} this player does not have anything to do right now...')
            else:
                evalSpecialAbility(playerSpecialAbilities[chosenPlayer])
            indent -= 1
        else:
            print(f'{" "*indent}That is {RED}incorrect{CLEAR}! you have been {RED}eliminated{CLEAR} for {ORANGE}{VOTING_FREQUENCY//4} rounds{CLEAR} and will return on {ORANGE}round {roundNum+(VOTING_FREQUENCY//4)}{CLEAR}.')
            guesserFailed = True
        indent -= 2
    if specialAbility == 'Medic':
        chosenPlayer = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the player who you want to {GREEN}shield{TURQUOISE} (1-{NUM_PLAYERS}): {CLEAR}', True))
        shieldedPlayers.append(chosenPlayer)
    if specialAbility == 'Cleaner':
        for _ in range(len(quantumEntanglements)//2):
            quantumEntanglements.remove(random.choice(quantumEntanglements))
        print(f'{" "*indent}There are now {GREEN}{len(quantumEntanglements)}{CLEAR} {ENTANGLEMENT_SPACE}quantum entanglements{CLEAR}.')
        indent += 1
        print(f'{" "*indent}{GRAY}(regenerating map image...){CLEAR}')
        indent -= 1
        generateImage(board, paths, quantumEntanglements)
    if specialAbility == 'Mewer':
        if mewChance != 1:
            mewChance = round(mewChance+0.01, 2)
        print(f'{" "*indent}The {GREEN}chance{CLEAR} of a successful {GYM_SPACE}mew{CLEAR} is now {RED}{int(mewChance*100)}%{CLEAR}.')
    if specialAbility == 'Swapper':
        candidates = [player for player in list(range(1,NUM_PLAYERS+1)) if player not in eliminatedPlayers]
        if len(candidates) <= 1:
            print(f'{" "*indent}{RED}Unfortunately, there is no one to choose.{CLEAR}')
        else:
            player1 = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the first player to have their votes {TELEPORT_SPACE}swapped{TURQUOISE} (1-{NUM_PLAYERS}):{CLEAR} ', True))
            valid = False
            while not valid:
                player2 = int(askForPlayer(f'{" "*indent}{TURQUOISE}Enter the second player to have their votes {TELEPORT_SPACE}swapped{TURQUOISE} (1-{NUM_PLAYERS}):{CLEAR} ', True))
                if player2 == player1:
                    indent += 1
                    print(f'{" "*indent}{ERROR}The 2 players cannot be the same! Please try again{CLEAR}')
                    indent -= 1
                else:
                    valid = True
            voteSwaps.append([player1, player2])

def evaluatePoison():
    global indent
    global allowedToMove
    if roundNum == playerHealedPoisons[currentPlayer] and playerPoisoneds[currentPlayer] != {"symptomStart": -1, "elimination": -1, "eliminationReturn": -1}:
        indent += 1
        print(f'{" "*indent}It appears you recently crossed paths with a {GREEN}Medic{CLEAR}, and so you are no longer {DARK_GREEN}poisoned{CLEAR}!')
        playerPoisoneds[currentPlayer] = {"symptomStart": -1, "elimination": -1, "eliminationReturn": -1}
        playerHealedPoisons[currentPlayer] = -1
        indent -= 1
    if playerPoisoneds[currentPlayer]['symptomStart'] <= roundNum and roundNum < playerPoisoneds[currentPlayer]['elimination']:
        poisonEffect = random.choice(['nothing','nothing','nothing','nothing','nothing','no move','no move','loose speed','loose speed','acid'])
        if poisonEffect == 'no move' and board[playerPositions[currentPlayer]] != 'shadow realm':
            indent += 1
            print(f'{" "*indent}Unfortunately, as you have been {DARK_GREEN}poisoned{CLEAR}, you {RED}cannot move{CLEAR} this turn.')
            allowedToMove = False
            indent -= 1
        if poisonEffect == 'loose speed':
            indent += 1
            lostSpeed = round(random.randint(2,7)/100,2)
            print(f'{" "*indent}Unfortunately, as you have been {DARK_GREEN}poisoned{CLEAR}, you have lost {GYM_SPACE}{lostSpeed} speed{CLEAR}.')
            playerSpeeds[currentPlayer] -= lostSpeed
            playerSpeeds[currentPlayer] = round(playerSpeeds[currentPlayer], 4)
            if playerSpeeds[currentPlayer] < MINIMUM_SPEED:
                playerSpeeds[currentPlayer] = MINIMUM_SPEED
            print(f'{" "*indent}Your speed is now {GYM_SPACE}{playerSpeeds[currentPlayer]}{CLEAR}.')
            indent -= 1
        if poisonEffect == 'acid':
            indent += 1
            print(f'{" "*indent}Unfortunately, as you have been {DARK_GREEN}poisoned{CLEAR}, you have thrown up {GREEN}acid{CLEAR} on this space!')
            decorators[playerPositions[currentPlayer]].append({"type": 'acid', "placedBy": currentPlayer, "reward": ACID_PRICE})
            indent += 1
            print(f'{" "*indent}The next time {ORANGE}someone{CLEAR} lands on this space, you must pay them {YELLOW}{ACID_PRICE} gold{CLEAR}. (as an apology)')
            print(f'{" "*indent}The {GREEN}acid{CLEAR} will be removed afer.')
            indent -= 2
    elif roundNum == playerPoisoneds[currentPlayer]['elimination']:
        indent += 1
        print(f'{" "*indent}Unfortunately, as you have been {DARK_GREEN}poisoned{CLEAR}, you have been {RED}eliminated{CLEAR} for {ORANGE}{VOTING_FREQUENCY//6} rounds{CLEAR} and will return on {ORANGE}round {roundNum+(VOTING_FREQUENCY//6)}{CLEAR}.')
        indent += 1
        print(f'{" "*indent}You will return right before the vote.')
        indent -= 1
        eliminatedPlayers.append(currentPlayer)
        playerEliminationReturns[currentPlayer] = roundNum+(VOTING_FREQUENCY//6)
        playerPoisoneds[currentPlayer] = {"symptomStart": -1, "elimination": -1, "eliminationReturn": -1}
        allowedToMove = False
        indent -= 1

def checkForMedicHeal():
    for player in range(1,NUM_PLAYERS+1):
        if playerPositions[player] == playerPositions[currentPlayer]:
            if playerSpecialAbilities[currentPlayer] == 'Medic' and playerPoisoneds[player] != {"symptomStart": -1, "elimination": -1, "eliminationReturn": -1}:
                playerHealedPoisons[player] = roundNum + random.randint(3,10)
            elif playerSpecialAbilities[player] == 'Medic' and playerPoisoneds[currentPlayer] != {"symptomStart": -1, "elimination": -1, "eliminationReturn": -1}:
                playerHealedPoisons[currentPlayer] = roundNum + random.randint(3,10)

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

def playBoardQuiz(numQuestions, only=False):
    global indent
    indent += 1
    result = True
    for roundNum in range(1,numQuestions+1):
        if only == True:
            if roundNum != numQuestions:
                continue
        print(f'{" "*indent}Question {getColourFromFraction((numQuestions-roundNum)/numQuestions)}{roundNum}{CLEAR}:')
        valid = False
        while not valid:
            moves = []
            pureMoves = []
            currentSpace = tuple(np.argwhere(board == "home")[0])
            valid = True
            for n in range(roundNum):
                if valid:
                    possibleMoves = findPossibleMoves(paths, currentSpace, True, highwayInformation)
                    if len(moves) > 0:
                        if 'down' == pureMoves[-1]:
                            avoid = 'up'
                        if 'up' == pureMoves[-1]:
                            avoid = 'down'
                        if 'left' == pureMoves[-1]:
                            avoid = 'right'
                        if 'right' == pureMoves[-1]:
                            avoid = 'left'
                        if 'forwards' == pureMoves[-1]:
                            avoid = 'backwards'
                        if 'backwards' == pureMoves[-1]:
                            avoid = 'forwards'
                        if '-' in pureMoves[-1]:
                            avoid = f'+{pureMoves[-1][1]}'
                        if '+' in pureMoves[-1]:
                            avoid = f'-{pureMoves[-1][1]}'
                        possibleMoves = [move for move in possibleMoves if move['direction'] != avoid]
                    if len(possibleMoves) == 0:
                        valid = False
                    else:
                        move = random.choice(possibleMoves)
                        moves.append(f'{getColourFromFraction((numQuestions-n-1)/numQuestions)}{move["direction"]}{CLEAR}')
                        pureMoves.append(move['direction'])
                        currentSpace = move['destination']
                        if board[currentSpace] in ['shadow realm', 'flamingo']:
                            valid = False
        correctAnswer = board[currentSpace]
        possibleAnswers = [correctAnswer]
        for _ in range(3):
            possibleAnswers.append(random.choice([x for x in ['empty', 'home', 'good', 'bad', 'shop', 'teleport', 'gambling', 'timewarp', 'papas wingeria', 'gym', 'quest', 'entanglement', 'information'] if x not in possibleAnswers]))
        random.shuffle(possibleAnswers)
        if NUM_DIMENSIONS < 4:
            print(f'{" "*indent}If you move {", ".join(moves)} from the {HOME_SPACE}home{CLEAR} space, what space do you land on?')
        else:
            print(f'{" "*indent}If you move in the {", ".join(moves)} direction{"s" if len(moves) > 1 else ""} from the {HOME_SPACE}home{CLEAR} space, what space do you land on?')
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

def playLogicGame(numQuestions, only=False):
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
        if only == True:
            if roundNum != numQuestions:
                continue
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
        print(f'{" "*indent}Simplify {convertToHumanReadable(expression)}')
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

def playDateQuiz(questions='all'):
    global indent
    indent += 1
    result = True
    today = datetime.datetime.today()
    for roundNum in range(1,6):
        if questions != 'all':
            if questions != roundNum:
                continue
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
        print(f'{" "*indent}What day of the week is {chosenDate.strftime(f"{CYAN}%B{CLEAR} {GREEN}%-d{CLEAR}, {ORANGE}%Y{CLEAR}")}?')
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
            print(f'{" "*indent}{RED}Incorrect!{CLEAR} The correct answer was {GREEN}{correctAnswer}{CLEAR}')
            indent -= 1
            result = False
            break
    indent -= 1
    return result

def playLyingGame(numQuestions, only=False):
    global indent
    indent += 1
    result = True
    
    def generateValidQuestion(numPeople):
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        people = list(range(1,numPeople+1))
        numLiars = random.randint(0,numPeople)
        liars = random.sample(people, numLiars)
        people = [None] + [True if x not in liars else False for x in people]
        statements = [None]
        complexPeople = random.sample(list(range(1,numPeople+1)), int((numPeople*0.35)//1))
        for person, truthy in enumerate(people):
            if person != 0:
                nextPerson = person + 1
                if nextPerson == len(people):
                    nextPerson = 1
                if truthy:
                    regularBit = {"person": nextPerson, "statement": people[nextPerson]}
                    if person not in complexPeople:
                        statements.append([regularBit])
                    else:
                        newBit = {"person": random.randint(1,numPeople), "statement": random.choice([True, False])}
                        statement = [regularBit, newBit]
                        random.shuffle(statement)
                        if people[newBit['person']] == newBit['statement']:
                            logic = ['or', 'and']
                        else:
                            logic = ['or']
                        statements.append(statement + [random.choice(logic)])
                else:
                    regularBit = {"person": nextPerson, "statement": not people[nextPerson]}
                    if person not in complexPeople:
                        statements.append([regularBit])
                    else:
                        newBit = {"person": random.randint(1,numPeople), "statement": random.choice([True, False])}
                        statement = [regularBit, newBit]
                        random.shuffle(statement)
                        if people[newBit['person']] != newBit['statement']:
                            logic = ['and', 'or']
                        else:
                            logic = ['and']
                        statements.append(statement + [random.choice(logic)])
        names = list(alphabet[:(numPeople)])
        random.shuffle(names)
        names = [None] + names
        question = {}
        for n, name in enumerate(names):
            if n != 0:
                if len(statements[n]) == 1:
                    question[name] = [{"person": names[statement['person']], "statement": statement['statement']} for statement in statements[n]]
                else:
                    logic = statements[n].pop(-1)
                    question[name] = [{"person": names[statement['person']], "statement": statement['statement']} for statement in statements[n]] + [logic]
                    statements[n].append(logic)
        question = dict(sorted(question.items()))
        
        otherWayWorks = True
        otherPeople = [None if person == None else not person for person in people]
        for n, statement in enumerate(statements):
            if n != 0:
                if len(statement) == 1:
                    if otherPeople[n]:
                        if otherPeople[statement[0]['person']] != statement[0]['statement']:
                            otherWayWorks = False
                            break
                    else:
                        if otherPeople[statement[0]['person']] == statement[0]['statement']:
                            otherWayWorks = False
                            break
                else:
                    if otherPeople[n]:
                        if statement[2] == 'or':
                            if otherPeople[statement[0]['person']] != statement[0]['statement'] and otherPeople[statement[1]['person']] != statement[1]['statement']:
                                otherWayWorks = False
                                break
                        else:
                            if otherPeople[statement[0]['person']] != statement[0]['statement'] or otherPeople[statement[1]['person']] != statement[1]['statement']:
                                otherWayWorks = False
                                break
                    else:
                        if statement[2] == 'or':
                            if otherPeople[statement[0]['person']] == statement[0]['statement'] or otherPeople[statement[1]['person']] == statement[1]['statement']:
                                otherWayWorks = False
                                break
                        else:
                            if otherPeople[statement[0]['person']] == statement[0]['statement'] and otherPeople[statement[1]['person']] == statement[1]['statement']:
                                otherWayWorks = False
                                break
            
        return numLiars, question, otherWayWorks
    
    for roundNum in range(1,numQuestions+1):
        if only == True:
            if roundNum != numQuestions:
                continue
        numPeople = roundNum + LYING_GAME_DIFFICULTY
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        names = {}
        for letter in alphabet[:(numPeople)]:
            name = '.'
            while name[0] != letter:
                name = get_first_name()
            names[letter] = name
        print(f'{" "*indent}Question {getColourFromFraction((numQuestions-roundNum)/numQuestions)}{roundNum}{CLEAR}:')
        numLiars, statements, otherWayWorks = generateValidQuestion(numPeople)
        indent += 1
        for person in statements:
            statement = statements[person]
            if len(statement) == 1:
                statement = statement[0]
                print(f'{" "*indent}{CYAN}{names[person]}{CLEAR} says: "{CYAN}{names[statement["person"]]}{CLEAR} is {f"telling the {GREEN}Truth{CLEAR}" if statement["statement"] else f"{RED}Lying{CLEAR}"}"')
            else:
                print(f'{" "*indent}{CYAN}{names[person]}{CLEAR} says: "{CYAN}{names[statement[0]["person"]]}{CLEAR} is {f"telling the {GREEN}Truth{CLEAR}" if statement[0]["statement"] else f"{RED}Lying{CLEAR}"} {ORANGE}{statement[2]}{CLEAR} {CYAN}{names[statement[1]["person"]]}{CLEAR} is {f"telling the {GREEN}Truth{CLEAR}" if statement[1]["statement"] else f"{RED}Lying{CLEAR}"}"')
        indent -= 1
        print(f'{" "*indent}How many people are {RED}Lying{CLEAR}?')
        choice = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice (0-{numPeople}):{CLEAR} ', numPeople))
        if choice == numLiars or (choice == numPeople-numLiars and otherWayWorks):
            indent += 1
            print(f'{" "*indent}{GREEN}Correct!{CLEAR}')
            indent -= 1
        else:
            indent += 1
            if numLiars == numPeople-numLiars or not otherWayWorks:
                print(f'{" "*indent}{RED}Incorrect!{CLEAR} The correct answer was {GREEN}{min([numLiars])}{CLEAR}')
            else:
                print(f'{" "*indent}{RED}Incorrect!{CLEAR} The correct answer was {GREEN}{min([numLiars, numPeople-numLiars])}{CLEAR} or {GREEN}{max([numLiars, numPeople-numLiars])}{CLEAR}')
            indent -= 1
            result = False
            break
    indent -= 1
    return result

def grammatiseSpaceType(spaceType, punctuation=False, title=False, article=True):
    if spaceType == 'empty':
        return f'{"an " if article else ""}{EMPTY_SPACE}{"Empty" if title else "empty"}{CLEAR} space{"." if punctuation else ""}'
    if spaceType == 'flamingo':
        return f'{"the " if article else ""}{FLAMINGO_SPACE}{"Flamingo" if title else "flamingo"}{CLEAR} space{"!" if punctuation else ""}'
    if spaceType == 'home':
        return f'{"the " if article else ""}{HOME_SPACE}{"Home" if title else "home"}{CLEAR} space{"." if punctuation else ""}'
    if spaceType == 'shadow realm':
        return f'{"the " if article else ""}{SHADOW_REALM_SPACE}{"Shadow Realm" if title else "shadow realm"}{CLEAR} space{"." if punctuation else ""}'
    if spaceType == 'good':
        return f'{"a " if article else ""}{GOOD_SPACE}{"Good" if title else "good"}{CLEAR} space{"!" if punctuation else ""}'
    if spaceType == 'bad':
        return f'{"a " if article else ""}{BAD_SPACE}{"Bad" if title else "bad"}{CLEAR} space{"." if punctuation else ""}'
    if spaceType == 'shop':
        return f'{"a " if article else ""}{SHOP_SPACE}{"Shop" if title else "shop"}{CLEAR} space{"!" if punctuation else ""}'
    if spaceType == 'teleport':
        return f'{"a " if article else ""}{TELEPORT_SPACE}{"Teleport" if title else "teleport"}{CLEAR} space{"!" if punctuation else ""}'
    if spaceType == 'gambling':
        return f'{"a " if article else ""}{GAMBLING_SPACE}{"Gambling" if title else "gambling"}{CLEAR} space{"!" if punctuation else ""}'
    if spaceType == 'timewarp':
        return f'{"a " if article else ""}{TIMEWARP_SPACE}{"Time Warp" if title else "time warp"}{CLEAR} space{"!" if punctuation else ""}'
    if spaceType == 'papas wingeria':
        apostrophe = '\''
        return f'{PAPAS_WINGERIA_SPACE}{f"Papa{apostrophe}s Wingeria" if title else f"papa{apostrophe}s wingeria"}{CLEAR}{"!" if punctuation else ""}'
    if spaceType == 'gym':
        return f'{"a " if article else ""}{GYM_SPACE}{"Gym" if title else "gym"}{CLEAR} space{"!" if punctuation else ""}'
    if spaceType == 'quest':
        return f'{"a " if article else ""}{QUEST_SPACE}{"Quest" if title else "quest"}{CLEAR} space{"!" if punctuation else ""}'
    if spaceType == 'entanglement':
        return f'{"an " if article else ""}{ENTANGLEMENT_SPACE}{"Entanglement" if title else "entanglement"}{CLEAR} space{"!" if punctuation else ""}'
    if spaceType == 'information':
        return f'{"an " if article else ""}{INFORMATION_SPACE}{"Information" if title else "information"}{CLEAR} space{"!" if punctuation else ""}'

def grammatiseRole(role):
    if role == 'Finder':
        return f'{CYAN}Finder{CLEAR}'
    if role == 'Staller':
        return f'{RED}Staller{CLEAR}'
    if role == 'Jester':
        return f'{PINK}Jester{CLEAR}'
    if role == 'None':
        return 'None'
    if role == 'Murderer':
        return f'{RED}Murderer{CLEAR}'
    if role == 'Toxicologist':
        return f'{DARK_GREEN}Toxicologist{CLEAR}'
    if role == 'Seer':
        return f'{CYAN}Seer{CLEAR}'
    if role == 'Guesser':
        return f'{YELLOW}Guesser{CLEAR}'
    if role == 'Medic':
        return f'{GREEN}Medic{CLEAR}'
    if role == 'Cleaner':
        return f'{SHOP_SPACE}Cleaner{CLEAR}'
    if role == 'Mewer':
        return f'{GYM_SPACE}Mewer{CLEAR}'
    if role == 'Swapper':
        return f'{ORANGE}Swapper{CLEAR}'

def getAbilityDescription(specialAbility):
    if specialAbility == 'Murderer':
        return f'choose a player to {RED}murder{CLEAR}'
    if specialAbility == 'Toxicologist':
        return f'choose a player to {DARK_GREEN}poison{CLEAR}'
    if specialAbility == 'Seer':
        return f'choose a player to {CYAN}have their role revealed{CLEAR}'
    if specialAbility == 'Guesser':
        return f'guess a player\'s {YELLOW}special ability{CLEAR}'
    if specialAbility == 'Medic':
        return f'choose a player to {GREEN}sheild{CLEAR} from {RED}murder{CLEAR}'
    if specialAbility == 'Cleaner':
        return f'{SHOP_SPACE}remove half{CLEAR} of the {ENTANGLEMENT_SPACE}quantum entanglements{CLEAR}'
    if specialAbility == 'Mewer':
        return f'{GREEN}increase the chance{CLEAR} of a successful {GYM_SPACE}mew{CLEAR} by {RED}1%{CLEAR}'
    if specialAbility == 'Swapper':
        return f'{ORANGE}swap{CLEAR} the votes that any {YELLOW}2 players{CLEAR} recieve'

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
        "roundNum": roundNum,
        "board": board,
        "paths": paths,
        "highwayInformation": highwayInformation,
        "decorators": decorators,
        "pathDecorators": pathDecorators,
        "quantumEntanglements": quantumEntanglements,
        "blackHolePos": blackHolePos,
        "blackHoleRadius": blackHoleRadius,
        "eliminatedPlayers": eliminatedPlayers,
        "mewChance": mewChance,
        "playerRoles": playerRoles,
        "playerSpecialAbilities": playerSpecialAbilities,
        "playerPositions": playerPositions,
        "playerInventories": playerInventories,
        "playerGolds": playerGolds,
        "playerSpeeds": playerSpeeds,
        "playerFoodInventories": playerFoodInventories,
        "playerProgress": playerProgress,
        "playerStealBonus": playerStealBonus,
        "playerInvestmentBonus": playerInvestmentBonus,
        "playerQuests": playerQuests,
        "playerWaitingForEvents": playerWaitingForEvents,
        "playerFrozens": playerFrozens,
        "playerQuantumNotifications": playerQuantumNotifications,
        "playerEliminationReturns": playerEliminationReturns,
        "playerPoisoneds": playerPoisoneds,
        "playerHealedPoisons": playerHealedPoisons,
        "playerGreenPotionTurns": playerGreenPotionTurns,
        "itemPrices": itemPrices,
        "itemRewards": itemRewards,
        "prevBoards": prevBoards,
        "prevDecorators": prevDecorators,
        "prevPathDecorators": prevPathDecorators,
        "prevQuantumEntanglements": prevQuantumEntanglements,
        "prevBlackHolePos": prevBlackHolePos,
        "prevBlackHoleRadius": prevBlackHoleRadius,
        "prevEliminatedPlayers": prevEliminatedPlayers,
        "prevMewChance": prevMewChance,
        "prevPlayerRoles": prevPlayerRoles,
        "prevPlayerSpecialAbilities": prevPlayerSpecialAbilities,
        "prevPlayerPositions": prevPlayerPositions,
        "prevPlayerInventories": prevPlayerInventories,
        "prevPlayerGolds": prevPlayerGolds,
        "prevPlayerSpeeds": prevPlayerSpeeds,
        "prevPlayerFoodInventories": prevPlayerFoodInventories,
        "prevPlayerProgress": prevPlayerProgress,
        "prevPlayerStealBonus": prevPlayerStealBonus,
        "prevPlayerInvestmentBonus": prevPlayerInvestmentBonus,
        "prevPlayerQuests": prevPlayerQuests,
        "prevPlayerWaitingForEvents": prevPlayerWaitingForEvents,
        "prevPlayerFrozens": prevPlayerFrozens,
        "prevPlayerQuantumNotifications": prevPlayerQuantumNotifications,
        "prevPlayerEliminationReturns": prevPlayerEliminationReturns,
        "prevPlayerPoisoneds": prevPlayerPoisoneds,
        "prevPlayerHealedPoisons": prevPlayerHealedPoisons,
        "prevPlayerGreenPotionTurns": prevPlayerGreenPotionTurns,
        "prevItemPrices": prevItemPrices,
        "prevItemRewards": prevItemRewards
    }
    with open(f'saves/{filename}.pkl', 'wb') as f:
        pickle.dump(data,f)

def redefineItemDescriptions():
    itemDescriptions = {
        #help i'm lost
        "compass": f'See all {ORANGE}adjacent{CLEAR} spaces and players.',
        "f3 menu": f'Tells you your current {ORANGE}coordinates{CLEAR}.',
        "safeword": f'Return to the {HOME_SPACE}home space{CLEAR}.',
        #where's the flamingo
        "red potion": f'Tells you where to go to get closer to the {FLAMINGO_SPACE}flamingo space{CLEAR}.',
        "green potion": f'Tells you how many moves away the {FLAMINGO_SPACE}flamingo space{CLEAR} is for the next {ORANGE}{itemRewards["green potion"]} round{"s" if itemRewards["green potion"] != 1 else ""}{CLEAR}.',
        "flamingo": f'Moves towards the {FLAMINGO_SPACE}flamingo space{CLEAR} at the end of the {RED}last player\'s{CLEAR} turn.',
        #violence is always the answer
        "knife": f'Steal {YELLOW}{itemRewards["knife"]} gold{CLEAR} from another player if they are on the same space as you.',
        "gun": f'Shoot in a direction and steal {YELLOW}{itemRewards["gun"]} gold{CLEAR} if it hits someone.',
        "trap": f'Sets a {RED}trap{CLEAR} that will steal {YELLOW}{itemRewards["trap"]} gold{CLEAR} when landed on.',
        "goblin": f'Randomly moves around the map. If a player lands on a space with your goblin, you steal {YELLOW}{itemRewards["goblin"]} gold{CLEAR}.',
        #movement stuff
        "dumbells": f'Increase your {GYM_SPACE}speed{CLEAR} by {GYM_SPACE}0.1{CLEAR}.',
        "fat injection": f'Decrease another player\'s {GYM_SPACE}speed{CLEAR} by {GYM_SPACE}0.1{CLEAR} if they are on the same space as you.',
        "freeze ray": f'Make another player lose the {ORANGE}ability to move{CLEAR} for 1 turn.',
        "swap": f'{TELEPORT_SPACE}Swap{CLEAR} the positions of 2 chosen players.',
        #miscellaneous
        "gold potion": f'Places {YELLOW}{itemRewards["gold potion"]} gold{CLEAR} on a random {ORANGE}adjacent{CLEAR} space.',
        "wand": f'Make a player spin the {RED}Bad Wheel{CLEAR} at the start of their next turn.',
        "time machine": f'{TIMEWARP_SPACE}Rewind time{CLEAR} to the start of your {ORANGE}previous turn{CLEAR}.',
        "padlock": f'Place this on an adjacent path. When travelling along this path, you must enter a {RED}4-digit{CLEAR} code.',
        "ingredient bundle": f'A collection of {ORANGE}{itemPrices["ingredient bundle"]*3} ingredients{CLEAR} to make a {PAPAS_WINGERIA_SPACE}wing platter{CLEAR} at {PAPAS_WINGERIA_SPACE}papa\'s wingeria{CLEAR}.',
        "portable shop": f'Visit the {SHOP_SPACE}shop{CLEAR} no matter where you are.'
    }
    return itemDescriptions

board, paths, decorators, pathDecorators = generateBoard()
quantumEntanglements = []

generateImage(board, paths, quantumEntanglements, debug=True)
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
    "padlock": 3,
    "ingredient bundle": 2,
    "portable shop": 3,
}

itemRewards = {
    #where's the flamingo
    "green potion": 1,
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
    "7": "violence is always the answer",
    "11": "movement stuff",
    "15": "miscellaneous"
}

itemDescriptions = redefineItemDescriptions()

playerRoles = [None]
playerSpecialAbilities = [None]
playerPositions = [None]
playerInventories = [None]
playerGolds = [None]
playerSpeeds = [None]
playerFoodInventories = [None]
playerProgress = [None]
playerStealBonus = [None]
playerInvestmentBonus = [None]
playerQuests = [None]
playerWaitingForEvents = [None]
playerFrozens = [None]
playerQuantumNotifications = [None]
playerEliminationReturns = [None]
playerPoisoneds = [None]
playerHealedPoisons = [None]
playerGreenPotionTurns = [None]
for _ in range(NUM_PLAYERS):
    playerRoles.append('Finder')
    playerSpecialAbilities.append('None')
    playerPositions.append(tuple(np.argwhere(board == "home")[0]))
    playerInventories.append(copy.deepcopy(STARTING_INVENTORY))
    playerGolds.append(STARTING_GOLD)
    playerSpeeds.append(STARTING_SPEED)
    playerFoodInventories.append(copy.deepcopy(STARTING_FOOD_INVENTORY))
    playerProgress.append(copy.deepcopy({"gym": 0, "wingeria": 0}))
    playerStealBonus.append(0)
    playerInvestmentBonus.append(0)
    playerQuests.append(copy.deepcopy([]))
    playerWaitingForEvents.append(copy.deepcopy([]))
    playerFrozens.append(False)
    playerQuantumNotifications.append(0)
    playerEliminationReturns.append(-1)
    playerPoisoneds.append({"symptomStart": -1, "elimination": -1, "eliminationReturn": -1})
    playerHealedPoisons.append(-1)
    playerGreenPotionTurns.append(0)

numTimeMachines = 0

blackHolePos = tuple([-1]*NUM_DIMENSIONS)
blackHoleRadius = -1

eliminatedPlayers = []

mewChance = 0.01

prevPlayerRoles = [copy.deepcopy(playerRoles)]
prevPlayerSpecialAbilities = [copy.deepcopy(playerSpecialAbilities)]
prevPlayerPositions = [copy.deepcopy(playerPositions)]
prevPlayerInventories = [copy.deepcopy(playerInventories)]
prevPlayerGolds = [copy.deepcopy(playerGolds)]
prevPlayerSpeeds = [copy.deepcopy(playerSpeeds)]
prevPlayerFoodInventories = [copy.deepcopy(playerFoodInventories)]
prevPlayerProgress = [copy.deepcopy(playerProgress)]
prevPlayerStealBonus = [copy.deepcopy(playerStealBonus)]
prevPlayerInvestmentBonus = [copy.deepcopy(playerInvestmentBonus)]
prevPlayerQuests = [copy.deepcopy(playerQuests)]
prevPlayerWaitingForEvents = [copy.deepcopy(playerWaitingForEvents)]
prevPlayerFrozens = [copy.deepcopy(playerFrozens)]
prevPlayerQuantumNotifications = [copy.deepcopy(playerQuantumNotifications)]
prevPlayerEliminationReturns = [copy.deepcopy(playerEliminationReturns)]
prevPlayerPoisoneds = [copy.deepcopy(playerPoisoneds)]
prevPlayerHealedPoisons = [copy.deepcopy(playerHealedPoisons)]
prevPlayerGreenPotionTurns = [copy.deepcopy(playerGreenPotionTurns)]
prevItemPrices = [copy.deepcopy(itemPrices)]
prevItemRewards = [copy.deepcopy(itemRewards)]
prevDecorators = [copy.deepcopy(decorators)]
prevPathDecorators = [copy.deepcopy(pathDecorators)]
prevBoards = [copy.deepcopy(board)]
prevQuantumEntanglements = [copy.deepcopy(quantumEntanglements)]
prevBlackHolePos = [copy.deepcopy(blackHolePos)]
prevBlackHoleRadius = [copy.deepcopy(blackHoleRadius)]
prevEliminatedPlayers = [copy.deepcopy(eliminatedPlayers)]
prevMewChance = [copy.deepcopy(mewChance)]

indent = 0

#give roles out
if ROLES_ENABLED:
    playerRoles[random.randint(1,NUM_PLAYERS)] = 'Staller'
    playerRoles[random.choice([x for x in list(range(1,NUM_PLAYERS+1)) if playerRoles[x] == 'Finder'])] = 'Jester'
    if CHAOS_MODE:
        for player, role in enumerate(playerRoles):
            if role == 'Staller':
                playerSpecialAbilities[player] = random.choice(['Murderer', 'Toxicologist'])
            elif role == 'Jester':
                playerSpecialAbilities[player] = random.choice(['Seer', 'Guesser'])
            elif role == 'Finder':
                playerSpecialAbilities[player] = random.choice(['Medic', 'Cleaner', 'Mewer', 'Swapper', 'None', 'None'])
    printRoles(playerRoles, playerSpecialAbilities)

running = True
currentPlayer = 1
roundNum = 1
winner = None
os.system('clear')
while running:
    padding = math.floor((50-6-len(str(roundNum)))/2)
    print(f'{" "*padding}{ORANGE}Round {roundNum}{CLEAR}')
    print('-'*50)
    print(f'{YELLOW}Player {currentPlayer}{CLEAR}, it is your turn!')
    indent += 1
    print(f'{" "*indent}You currently have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
    indent -= 1
    if len(playerQuests[currentPlayer]) > 0:
        indent += 1
        print(f'{" "*indent}Your current {QUEST_SPACE}quests{CLEAR} are:')
        indent += 1
        for quest in playerQuests[currentPlayer]:
            print(f'{" "*indent}{questTextFromDict(quest, progress=True)}')
        indent -= 2
    if playerGreenPotionTurns[currentPlayer] > 0 and board[playerPositions[currentPlayer]] != 'shadow realm':
        indent += 1
        shortestPathToFlamingo = findShortestPathToFlamingo(board, paths, playerPositions[currentPlayer], highwayInformation)
        print(f'{" "*indent}The {FLAMINGO_SPACE}flamigo space{CLEAR} is {GREEN}{len(shortestPathToFlamingo)}{CLEAR} moves away.')
        playerGreenPotionTurns[currentPlayer] -= 1
        indent -= 1
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
    timeTravelled = False
    #conditions on allowed to move
    allowedToMove = True
    evaluatePoison()
    currentSpaceType = board[playerPositions[currentPlayer]]
    if currentSpaceType == 'shadow realm':
        allowedToMove = False
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
    if playerFrozens[currentPlayer] and allowedToMove:
        allowedToMove = False
        indent += 1
        print(f'{" "*indent}Unfortunately, you are {CYAN}frozen{CLEAR}! You cannot move this turn.')
        playerFrozens[currentPlayer] = False
        indent -= 1
    if allowedToMove:
        if random.random() < round(playerSpeeds[currentPlayer]%1, 4):
            moves = math.ceil(playerSpeeds[currentPlayer])
        else:
            moves = math.floor(playerSpeeds[currentPlayer])
        if moves == 0:
            allowedToMove = False
            indent += 1
            print(f'{" "*indent}Due to your {RED}immense weight{CLEAR}, you unfortunately cannot move this turn. (your speed is {GYM_SPACE}{playerSpeeds[currentPlayer]}{CLEAR})')
            indent -= 1
        elif moves >= 2:
            indent += 1
            print(f'{" "*indent}Due to your {GYM_SPACE}speed ({playerSpeeds[currentPlayer]}){CLEAR}, you get {GREEN}{moves}{CLEAR} moves this turn!')
            indent -= 1
        for _ in range(moves):
            if board[playerPositions[currentPlayer]] != 'shadow realm' and winner == None and currentPlayer not in eliminatedPlayers:
                indent += 1
                #display move options
                sure = False
                while not sure:
                    print(f'{" "*indent}Where would you like to move?')
                    possibleMoves = findPossibleMoves(paths, playerPositions[currentPlayer], True, highwayInformation)
                    options = 0
                    indent += 1
                    print(f'{" "*indent}{options}: Stay Here')
                    for move in possibleMoves:
                        options += 1
                        if NUM_DIMENSIONS < 4:
                            print(f'{" "*indent}{options}: Move {GREEN}{move["direction"]}{CLEAR}')
                        else:
                            print(f'{" "*indent}{options}: Move in the {GREEN}{move["direction"]} direction{CLEAR}')
                    indent -= 1
                    choice = askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', options)
                    if int(choice) != 0 or CONFIRM_STAY_HERE == False:
                        sure = True
                    else:
                        print(f'{" "*indent}Are you sure?')
                        indent += 1
                        print(f'{" "*indent}0: No')
                        print(f'{" "*indent}1: Yes')
                        indent -= 1
                        sure = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', 1))
                #evaluate option
                hasBeenEliminated = False
                if int(choice) != 0:
                    evaluatePathDecorators(possibleMoves[int(choice)-1]['path'])
                    checkForFatPeople(possibleMoves[int(choice)-1]['destination'])
                    if allowedToMove:
                        #move
                        playerPositions[currentPlayer] = possibleMoves[int(choice)-1]['destination']
                        checkForMedicHeal()
                        checkForSquashedPeople()
                        evaluateDecorators()
                        spaceType = board[playerPositions[currentPlayer]]
                        if spaceType == 'flamingo' and OTHERS_CANT_SEE_FLAMINGO:
                            if (roundNum <= STALLER_WIN and playerRoles[currentPlayer] in ['Staller', 'Jester']) or (roundNum > STALLER_WIN and playerRoles[currentPlayer] == 'Staller'):
                                spaceType = 'empty'
                        if math.sqrt(sum([(playerPositions[currentPlayer][x]-blackHolePos[x])**2 for x in range(NUM_DIMENSIONS)])) <= blackHoleRadius:
                            print(f'{" "*indent}{YELLOW}Player {currentPlayer},{RED} You have been swallowed by the {SHADOW_REALM_SPACE}black hole{RED} and have been permanently ELIMINATED.{CLEAR}')
                            eliminatedPlayers.append(currentPlayer)
                            hasBeenEliminated = True
                        if not hasBeenEliminated:
                            hasBeenEliminated = evaluateSpaceType(spaceType)
                indent -= 1
                #ask for item use
                if not hasBeenEliminated:
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
    if len(eliminatedPlayers) == NUM_PLAYERS:
        winner = 0
        running = False
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
                with open(f'saves/{dir[int(choice)-1]}', 'rb') as f:
                    data = pickle.load(f)
                currentPlayer = data["currentPlayer"]
                roundNum = data["roundNum"]
                board = data["board"]
                paths = data["paths"]
                highwayInformation = data["highwayInformation"]
                decorators = data["decorators"]
                pathDecorators = data["pathDecorators"]
                quantumEntanglements = data["quantumEntanglements"]
                blackHolePos = data["blackHolePos"]
                blackHoleRadius = data["blackHoleRadius"]
                eliminatedPlayers = data["eliminatedPlayers"]
                mewChance = data["mewChance"]
                playerRoles = data["playerRoles"]
                playerSpecialAbilities = data["playerSpecialAbilities"]
                playerPositions = data["playerPositions"]
                playerInventories = data["playerInventories"]
                playerGolds = data["playerGolds"]
                playerSpeeds = data["playerSpeeds"]
                playerFoodInventories = data["playerFoodInventories"]
                playerProgress = data["playerProgress"]
                playerStealBonus = data["playerStealBonus"]
                playerInvestmentBonus = data["playerInvestmentBonus"]
                playerQuests = data["playerQuests"]
                playerWaitingForEvents = data["playerWaitingForEvents"]
                playerFrozens = data["playerFrozens"]
                playerQuantumNotifications = data["playerQuantumNotifications"]
                playerEliminationReturns = data["playerEliminationReturns"]
                playerPoisoneds = data["playerPoisoneds"]
                playerHealedPoisons = data["playerHealedPoisons"]
                playerGreenPotionTurns = data["playerGreenPotionTurns"]
                itemPrices = data["itemPrices"]
                itemRewards = data["itemRewards"]
                prevBoards = data["prevBoards"]
                prevDecorators = data["prevDecorators"]
                prevPathDecorators = data["prevPathDecorators"]
                prevQuantumEntanglements = data["prevQuantumEntanglements"]
                prevBlackHolePos = data["prevBlackHolePos"]
                prevBlackHoleRadius = data["prevBlackHoleRadius"]
                prevEliminatedPlayers = data["prevEliminatedPlayers"]
                prevMewChance = data["prevMewChance"]
                prevPlayerRoles = data["prevPlayerRoles"]
                prevPlayerSpecialAbilities = data["prevPlayerSpecialAbilities"]
                prevPlayerPositions = data["prevPlayerPositions"]
                prevPlayerInventories = data["prevPlayerInventories"]
                prevPlayerGolds = data["prevPlayerGolds"]
                prevPlayerSpeeds = data["prevPlayerSpeeds"]
                prevPlayerFoodInventories = data["prevPlayerFoodInventories"]
                prevPlayerProgress = data["prevPlayerProgress"]
                prevPlayerStealBonus = data["prevPlayerStealBonus"]
                prevPlayerInvestmentBonus = data["prevPlayerInvestmentBonus"]
                prevPlayerQuests = data["prevPlayerQuests"]
                prevPlayerWaitingForEvents = data["prevPlayerWaitingForEvents"]
                prevPlayerFrozens = data["prevPlayerFrozens"]
                prevPlayerQuantumNotifications = data["prevPlayerQuantumNotifications"]
                prevPlayerEliminationReturns = data["prevPlayerEliminationReturns"]
                prevPlayerPoisoneds = data["prevPlayerPoisoneds"]
                prevPlayerHealedPoisons = data["prevPlayerHealedPoisons"]
                prevPlayerGreenPotionTurns = data["prevPlayerGreenPotionTurns"]
                prevItemPrices = data["prevItemPrices"]
                prevItemRewards = data["prevItemRewards"]
                os.remove(f'saves/{dir[int(choice)-1]}')
                generateImage(board, paths, quantumEntanglements)
            indent -= 1
        saveToFile('current')
        os.system('clear')
        #store backups
        prevPlayerRoles.append(copy.deepcopy(playerRoles))
        prevPlayerSpecialAbilities.append(copy.deepcopy(playerSpecialAbilities))
        prevPlayerPositions.append(copy.deepcopy(playerPositions))
        prevPlayerInventories.append(copy.deepcopy(playerInventories))
        prevPlayerGolds.append(copy.deepcopy(playerGolds))
        prevPlayerSpeeds.append(copy.deepcopy(playerSpeeds))
        prevPlayerFoodInventories.append(copy.deepcopy(playerFoodInventories))
        prevPlayerProgress.append(copy.deepcopy(playerProgress))
        prevPlayerStealBonus.append(copy.deepcopy(playerStealBonus))
        prevPlayerInvestmentBonus.append(copy.deepcopy(playerInvestmentBonus))
        prevPlayerQuests.append(copy.deepcopy(playerQuests))
        prevPlayerWaitingForEvents.append(copy.deepcopy(playerWaitingForEvents))
        prevPlayerFrozens.append(copy.deepcopy(playerFrozens))
        prevPlayerQuantumNotifications.append(copy.deepcopy(playerQuantumNotifications))
        prevPlayerEliminationReturns.append(copy.deepcopy(playerEliminationReturns))
        prevPlayerPoisoneds.append(copy.deepcopy(playerPoisoneds))
        prevPlayerHealedPoisons.append(copy.deepcopy(playerHealedPoisons))
        prevPlayerGreenPotionTurns.append(copy.deepcopy(playerGreenPotionTurns))
        prevItemPrices.append(copy.deepcopy(itemPrices))
        prevItemRewards.append(copy.deepcopy(itemPrices))
        prevDecorators.append(copy.deepcopy(decorators))
        prevPathDecorators.append(copy.deepcopy(pathDecorators))
        prevBoards.append(copy.deepcopy(board))
        prevQuantumEntanglements.append(copy.deepcopy(quantumEntanglements))
        prevBlackHolePos.append(copy.deepcopy(blackHolePos))
        prevBlackHoleRadius.append(copy.deepcopy(blackHoleRadius))
        prevEliminatedPlayers.append(copy.deepcopy(eliminatedPlayers))
        prevMewChance.append(copy.deepcopy(mewChance))
        #expand black hole
        if blackHoleRadius > -1:
            if random.random() <= 0.5:
                blackHoleRadius += 1
                print(f'{" "*indent}The {SHADOW_REALM_SPACE}black hole{CLEAR} has grown to a radius of {blackHoleRadius} space{"s" if blackHoleRadius != 1 else ""}.')
                for n, playerPos in enumerate(playerPositions):
                    if n != 0 and n not in eliminatedPlayers:
                        if math.sqrt(sum([(playerPositions[currentPlayer][x]-blackHolePos[x])**2 for x in range(NUM_DIMENSIONS)])) <= blackHoleRadius:
                            print(f'{" "*indent}{YELLOW}Player {n},{RED} You have been swallowed by the {SHADOW_REALM_SPACE}black hole{RED} and have been permanently ELIMINATED.{CLEAR}')
                            eliminatedPlayers.append(n)
                            if len(eliminatedPlayers) == NUM_PLAYERS:
                                winner = 0
                                running = False
        if running == True:
            #change turn order
            loopedOver = False
            currentPlayer += 1
            if currentPlayer > NUM_PLAYERS:
                currentPlayer = 1
                loopedOver = True
            for player, returnRound in enumerate(playerEliminationReturns):
                if player != 0:
                    if returnRound == roundNum or (returnRound == roundNum+1 and loopedOver):
                        eliminatedPlayers.remove(player)
                        playerEliminationReturns[player] = -1
            while currentPlayer in eliminatedPlayers:
                currentPlayer += 1
                if currentPlayer > NUM_PLAYERS:
                    currentPlayer = 1
                    loopedOver = True
            if loopedOver:
                roundNum += 1
                if (roundNum % VOTING_FREQUENCY == 1) and ROLES_ENABLED and (roundNum <= STALLER_WIN + 1) and (NUM_PLAYERS - len(eliminatedPlayers) >= 3):
                    if roundNum == STALLER_WIN + 1:
                        jesterWon = evaluateVote(final=True)
                    else:
                        jesterWon = evaluateVote(final=False)
                    if jesterWon:
                        winner = playerRoles.index('Jester')
                        running = False
                    elif NUM_PLAYERS - len(eliminatedPlayers) == 0:
                        winner = 0
                        running = False
                if running == True:
                    while currentPlayer in eliminatedPlayers:
                        currentPlayer += 1
                if roundNum > STALLER_WIN and roundNum % 5 == 1 and running == True:
                    padding = math.floor((50-6-len(str(roundNum)))/2)
                    print(f'{" "*padding}{ORANGE}Round {roundNum}{CLEAR}')
                    print('-'*50)
                    if 'Staller' in [role for player, role in enumerate(playerRoles) if player not in eliminatedPlayers]:
                        staller = playerRoles.index('Staller')
                        print(f'{" "*indent}{YELLOW}Player {staller}{CLEAR}, as you are the {RED}Staller{CLEAR}, you have a chance to {GREEN}win the game{CLEAR}.')
                        won = spinTheFlamingoWheel()
                        if not won:
                            print(f'{" "*indent}{RED}You lost!{CLEAR}')
                            print('-'*50)
                            input(f'{TURQUOISE}Press Enter to return back to the game {CLEAR}')
                            os.system('clear')
                        else:
                            winner = staller
                            running = False
                    else:
                        finders = [player for player, role in enumerate(playerRoles) if role == 'Finder' and player not in eliminatedPlayers]
                        if len(finders) == 0:
                            chosen = playerRoles.index('Jester')
                        else:
                            chosen = random.choice(finders)
                        print(f'{" "*indent}{YELLOW}Player {chosen}{CLEAR}, you have been picked to have a chance to {GREEN}win the game{CLEAR}.')
                        won = spinTheFlamingoWheel()
                        if not won:
                            print(f'{" "*indent}{RED}You lost!{CLEAR}')
                            print(f'{" "*indent}{YELLOW}Player {chosen}{CLEAR}, you have been {RED}permanently eliminated{CLEAR}.')
                            eliminatedPlayers.append(chosen)
                            if len(eliminatedPlayers) == NUM_PLAYERS:
                                winner = 0
                                running = False
                            else:
                                print('-'*50)
                                input(f'{TURQUOISE}Press Enter to return back to the game {CLEAR}')
                                os.system('clear')
                        else:
                            winner = chosen
                            running = False
                if running == True:
                    #evaluate misc turns
                    decoratorsToRemove = []
                    goblinsToAdd = []
                    flamingosToAdd = []
                    printed = False
                    for cell in np.ndindex(board.shape):
                        for n, decorator in enumerate(decorators[cell]):
                            if decorator['type'] == 'goblin':
                                possibleMoves = findPossibleMoves(paths, cell, True, highwayInformation)
                                chosenDestination = random.choice(possibleMoves)['destination']
                                decoratorsToRemove.append((cell, n))
                                print(f'{" "*indent}{RED}Player {decorator["placedBy"]}\'s goblin{CLEAR} has moved!')
                                if board[chosenDestination] == 'shadow realm':
                                    indent += 1
                                    print(f'{" "*indent}The goblin {RED}got lost{CLEAR} in the {SHADOW_REALM_SPACE}shadow realm{CLEAR} and died.')
                                    indent -= 1
                                else:
                                    goblinsToAdd.append((chosenDestination, decorator))
                                printed = True
                            if decorator['type'] == 'flamingo':
                                shortestPathToFlamingo = findShortestPathToFlamingo(board, paths, cell, highwayInformation)
                                decoratorsToRemove.append((cell, n))
                                if len(shortestPathToFlamingo) == 1:
                                    print(f'{" "*indent}{RED}Player {decorator["placedBy"]}\'s {FLAMINGO_SPACE}flamingo{CLEAR} has reached the {FLAMINGO_SPACE}flamingo space{CLEAR} and will be despawned.')
                                else:
                                    firstPath = shortestPathToFlamingo[0]
                                    chosenDestination = firstPath['end']
                                    flamingosToAdd.append((chosenDestination, decorator))
                                    print(f'{" "*indent}{RED}Player {decorator["placedBy"]}\'s {FLAMINGO_SPACE}flamingo{CLEAR} has moved!')
                                printed = True
                    for decorator in sorted(decoratorsToRemove, reverse=True):
                        decorators[decorator[0]].pop(decorator[1])
                    for goblin in goblinsToAdd:
                        decorators[goblin[0]].append(goblin[1])
                    for flamingo in flamingosToAdd:
                        decorators[flamingo[0]].append(flamingo[1])
                    if printed:
                        print('-'*50)

if winner != 0:
    print(f'{GREEN}Player {winner} wins!{CLEAR}')
else:
    print(f'{RED}Everyone has been eliminated. No one wins.{CLEAR}')