#bord paramaters
GRID_SIZE = 7
PERCENTAGE_SQUARES = 0.7
PERCENTAGE_PATHS = 0.5
PROBABILITY_ONE_WAY = 0.1

#game settings
NUM_PLAYERS = 3
STARTING_GOLD = 3
STARTING_HAND = []
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