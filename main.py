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
STALLER_ABILITIES = ['Murderer', 'Toxicologist']
JESTER_ABILITIES = ['Seer', 'Guesser']
FINDER_ABILITIES = ['Medic', 'Cleaner', 'Mewer', 'Swapper', 'None']
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

def definePapasColours(colouring):
    global PAPAS_CLEAR
    global PAPAS_BROWN
    global PAPAS_MAROON
    global PAPAS_RED
    global PAPAS_ORANGE
    global PAPAS_ORANGE_YELLOW
    global PAPAS_YELLOW
    global PAPAS_GREEN
    global PAPAS_DARK_GREEN
    global PAPAS_TURQUOISE
    global PAPAS_CYAN
    global PAPAS_BLUE
    global PAPAS_PURPLE
    global PAPAS_PINK
    global PAPAS_GRAY
    if colouring:
        PAPAS_CLEAR = '\033[0m'
        PAPAS_BROWN = getColour(133, 60, 1)
        PAPAS_MAROON = getColour(148, 14, 4)
        PAPAS_RED = getColour(255, 0, 0)
        PAPAS_ORANGE = getColour(255, 123, 8)
        PAPAS_ORANGE_YELLOW = getColour(255, 162, 0)
        PAPAS_YELLOW = getColour(255, 210, 8)
        PAPAS_GREEN = getColour(0, 255, 0) #game
        PAPAS_DARK_GREEN = getColour(0, 153, 36)
        PAPAS_TURQUOISE = getColour(0, 199, 192) #qty
        PAPAS_CYAN = getColour(0, 217, 255)
        PAPAS_BLUE = getColour(0, 98, 255) #cooks
        PAPAS_PURPLE = getColour(176, 0, 230) #positioning a
        PAPAS_PINK = getColour(227, 61, 208) #positioning b
        PAPAS_GRAY = getColour(69, 69, 69) #info
    else:
        PAPAS_CLEAR = ''
        PAPAS_BROWN = ''
        PAPAS_MAROON = ''
        PAPAS_RED = ''
        PAPAS_ORANGE = ''
        PAPAS_ORANGE_YELLOW = ''
        PAPAS_YELLOW = ''
        PAPAS_GREEN = ''
        PAPAS_DARK_GREEN = ''
        PAPAS_TURQUOISE = ''
        PAPAS_CYAN = ''
        PAPAS_BLUE = ''
        PAPAS_PURPLE = ''
        PAPAS_PINK = ''
        PAPAS_GRAY = ''

#wingeria ingredients
ALL_PAPAS_INGREDIENTS = {
    'freezeria': {'allTime': {'cups': ['Small', 'Medium', 'Large'], 'mixables': ['Blueberry', 'Nutty Butter Cup', 'Strawberry', 'Cookie Dough', 'Creameo Bits', 'Marshmallow', 'Pineapple', "Yum n' M", 'Birthday Cake', 'Fudge Brownie', 'Blackberry', 'Cherry Cordial', 'Cinnamon Roll', 'Cotton Puff', 'Kiwi', 'Peach', "S'more", 'Caramel Apple', 'Peppermint', 'Raspberry Crumble', 'Stroopwafel'], 'syrups': ['Chocolate Syrup', 'Vanilla Syrup', 'Strawberry Syrup', 'Mint Syrup', 'Banana Syrup', 'Rainbow Sherbert Syrup', 'Purple Burple Syrup', 'Cotton Candy Syrup', 'Pink Lemonade Syrup', 'Red Velvet Syrup', 'Pistachio Syrup', 'Neapolitan Syrup', 'Huckleberry Syrup', 'Blue Moon Syrup', 'Espresso Syrup', 'Pumpkin Pie Syrup', 'Chai Tea Syrup', 'Tutti Frutti Syrup', 'Ube Syrup', 'Dreamsicle Syrup', 'Moon Mist Syrup', 'Citri-Shock Syrup'], 'blends': ['Chunky', 'Regular', 'Smooth'], 'whippedCreams': ['Whipped Cream', 'Chocolate Mousse', 'Strawberry Fluff', 'Lemon Chiffon', 'Maui Meringue'], 'sauceToppings': ['Chocolate', 'Strawberry', 'Butterscotch', 'Blueberry', 'White Chocolate', 'Sugarplum', 'Dreamsicle', 'Key Lime', 'Mango', 'Luau Punch', 'Pawpaw', 'Birch Beer'], 'shakers': ['Nuts', 'Rainbow Sprinkles', 'Chocolate Chips', 'Shaved Mints', 'Tropical Charms', 'Wildberry Derps', 'Shaved Coconut', 'Pomegranate', 'Lollipop Bits'], 'placeableToppings': ['Cherry', 'Creameo', 'Banana', 'Cookie', 'Gummy Onion', 'Waffle Cone Wedge', 'Cloudberry', 'Hazlenut Swizzle', 'Gummy Worm', 'Dipped Pretzel', 'White Chocolate Truffle', 'Mint Square', 'Strawberry Wafers', 'Cotton Candy Creameo', 'Blondie']}, 'january': [{'name': 'New Year', 'mixables': ['Confetti Pie-Tart'], 'syrups': ['Tutti Frutti Syrup'], 'whippedCreams': ['Rainbow Whip'], 'sauceToppings': ['Flavor X'], 'shakers': ['Countdown Candies'], 'placeableToppings': ['Gummy Worm']}], 'february': [{'name': "Valentine's Day", 'mixables': ['Alexandertorte'], 'syrups': ['Cherry Cheesecake Syrup'], 'whippedCreams': ['Rose Hip Whip'], 'sauceToppings': ['Love Potion'], 'shakers': ['X and O Sprinkles'], 'placeableToppings': ['Candy Heart']}], 'march': [{'name': "St. Paddy's Day", 'mixables': ['Green Emerald Cake'], 'syrups': ['Pistachio Syrup'], 'whippedCreams': ['Irish Cream'], 'sauceToppings': ["Pot O' Gold"], 'shakers': ['Lucky Sevens'], 'placeableToppings': ['Clover Cookie']}], 'april': [{'name': 'Easter', 'mixables': ['Cotton Puff'], 'syrups': ['Wildberry Shake Syrup'], 'whippedCreams': ['Bubblegum Whip'], 'sauceToppings': ['Blue Nimbus'], 'shakers': ['Jelly Beans'], 'placeableToppings': ['Marshmallow Cheep']}], 'may': [{'name': 'Big Top Carnival', 'mixables': ['Animal Crackers'], 'syrups': ['SuperFan Syrup'], 'whippedCreams': ['Blue Raspberry Cream'], 'sauceToppings': ['Creameo'], 'shakers': ['Lollipop Bits'], 'placeableToppings': ['Saltwater Taffy']}], 'june': [{'name': 'Volcano Gala', 'mixables': ['Lava Cake'], 'syrups': ['Caramuri Syrup'], 'whippedCreams': ['Sainforest Whip'], 'sauceToppings': ['Buriti'], 'shakers': ['Pyroclastic Crunch'], 'placeableToppings': ['Sugar Glass Leaf']}], 'july': [{'name': 'Starlight Jubilee', 'mixables': ['Mulberry Medley'], 'syrups': ['Powsicle Syrup'], 'whippedCreams': ['Rocket Whip'], 'sauceToppings': ['Cherrybomb'], 'shakers': ['Star Sprinkles'], 'placeableToppings': ['Almond Snap Cookie']}], 'august': [{'name': 'Portallini Feast', 'mixables': ['Tiramisu'], 'syrups': ['Spumoni Syrup'], 'whippedCreams': ['Cannoli Cream'], 'sauceToppings': ['Amarena'], 'shakers': ['Portallini Confetti'], 'placeableToppings': ['Pizzelle']}], 'september': [{'name': 'Maple Mornings', 'mixables': ['Donut Pieces'], 'syrups': ['Honey Syrup'], 'whippedCreams': ['Mocha Cream'], 'sauceToppings': ['Maple'], 'shakers': ['Golden CinnaMunchies'], 'placeableToppings': ['Chocolate Bacon']}], 'october': [{'name': 'Halloween', 'mixables': ['Bonfire Toffee'], 'syrups': ['Tiger Tail Syrup'], 'whippedCreams': ['Scream Cream'], 'sauceToppings': ['Black Mist'], 'shakers': ['Spooky Sprinkles'], 'placeableToppings': ['Candy Jack-O-Lantern']}], 'november': [{'name': 'Thanksgiving', 'mixables': ['Candied Pecans'], 'syrups': ['Pumpkin Pie Syrup'], 'whippedCreams': ['Snickerdoodle Cream'], 'sauceToppings': ['Candy Corn'], 'shakers': ['Autumn Leaves'], 'placeableToppings': ['Haystack']}], 'december': [{'name': 'Christmas', 'mixables': ['Peppermints'], 'syrups': ['Wintergreen Frost Syrup'], 'whippedCreams': ['Eggnog Cream'], 'sauceToppings': ["Santa's Cookie"], 'shakers': ['Holly Tartz'], 'placeableToppings': ['Mini Candy Cane']}]},
    'mocharia': {'allTime': {'milks': ['Skim', 'Strawberry', 'Soy', 'Chocolate', 'Blueberry'], 'temperatures': ['Hot', 'Cold'], 'espressos': ['City Roast', 'Decaf Roast', 'French Roast', 'New England Roast'], 'cups': ['Small', 'Medium', 'Large'], 'syrups': ['Chocolate', 'Red Velvet', 'Salted Caramel', 'Sugarplum', 'Orance Mocha', 'Blue Nimbus', 'Cinnamon Dolce', 'Honey', 'Marshmallow'], 'ices': ['Ice Cubes', 'Crushed Ice'], 'powders': ['Matcha', 'Lavender', 'Hibiscus', 'Chai', 'Aprajita'], 'creams': ['Butterscotch', 'Strawberry', 'Whipped', 'Chocolate Mousse', 'Lemon Chiffon', 'Moon Mist', 'Wildberry Shake', 'Peach', 'Creameo'], 'toppings': ['Cinnamon Sugar', 'Cocoa Powder', 'Crushed Pistachios', 'Shaved Chocolate', 'Toasted Coconut', 'Mini Mallows', 'Ground Nutmeg', 'Citrus Zest', 'Rainbow Sprinkles'], 'canoliShells': ['Chocolate', 'Classic', 'Pizzelle', 'Battenberg', 'Caramel Apple', 'Pineapple Upside-Down']}, 'january': [{'name': 'New Year', 'milks': ['Unicorn'], 'syrups': ['Flavour X'], 'powders': ['Midnight Shimmer'], 'creams': ['Rainbow Meringue'], 'toppings': ['Fruity Hoops'], 'canoliShells': ['Dirt Cake']}], 'february': [{'name': "Valentine's Day", 'milks': ['Lollipop'], 'syrups': ['Cherry Cheesecake'], 'powders': ['White Chocolate'], 'creams': ['Neapolitan'], 'toppings': ['X and O Sprinkles'], 'canoliShells': ['Cupid']}], 'march': [{'name': "St. Paddy's Day", 'milks': ['Irish Cream'], 'syrups': ['Mint'], 'powders': ['Gold Rush'], 'creams': ['Green Emerald'], 'toppings': ['Shamrock Sprinkles'], 'canoliShells': ['Celtic']}], 'april': [{'name': 'Cherry Blossom Festival', 'milks': ['Shiruko Soy'], 'syrups': ['Honeydew'], 'powders': ['Sakura'], 'creams': ['Azuki Fluff'], 'toppings': ['Sugar Petals'], 'canoliShells': ['Egg Waffle']}], 'may': [{'name': 'Cinco de Mayo', 'milks': ['Horchata'], 'syrups': ['Mamey'], 'powders': ['Champurrado'], 'creams': ['Tres Leches Whipped'], 'toppings': ['Cinco Swirls'], 'canoliShells': ['Churro']}], 'june': [{'name': 'Summer Luau', 'milks': ['Piña Colada'], 'syrups': ['Luau Punch'], 'powders': ['Mango'], 'creams': ['Maui Meringue'], 'toppings': ['Tropcial Charms'], 'canoliShells': ['Sunburst']}], 'july': [{'name': 'Starlight Jubilee', 'milks': ['Cherrybomb'], 'syrups': ['Jubilee Jelly'], 'powders': ['Almond Snap'], 'creams': ['Powsicle'], 'toppings': ['Crackle Crumbs'], 'canoliShells': ['Starlight']}], 'august': [{'name': 'Groovstock', 'milks': ['Golden'], 'syrups': ['Ginger Haze'], 'powders': ["Rockin' Rooibos"], 'creams': ['Blues-berry'], 'toppings': ['Crimson and Clove'], 'canoliShells': ['Far Out']}], 'september': [{'name': 'SugarPlex FilmFest', 'milks': ['Root Beer Float'], 'syrups': ['Golden Age'], 'powders': ['Dr. Cherry'], 'creams': ['Dual Licorice Whipped'], 'toppings': ['Butterzinger Bits'], 'canoliShells': ['Shell Noir']}], 'october': [{'name': 'Halloween', 'milks': ['Screamsicle'], 'syrups': ["Witch's Brew"], 'powders': ['Shadowberry'], 'creams': ['Phantom Fluff'], 'toppings': ['Spooky Sprinkles'], 'canoliShells': ['Frankenoli']}], 'november': [{'name': 'Thanksgiving', 'milks': ['Pecan'], 'syrups': ['Pumpkin Spice'], 'powders': ['Snickerdoodle'], 'creams': ['Candy Corn'], 'toppings': ['Autumn Leaves Sprinkles'], 'canoliShells': ['Harvest Stripe']}], 'december': [{'name': 'Christmas', 'milks': ['Eggnog'], 'syrups': ['Santa Cookie'], 'powders': ['Peppermint'], 'creams': ['Snowpuff'], 'toppings': ['Elf Sugar'], 'canoliShells': ['Gingerbread']}]},
    'hotDoggeria': {'allTime': {'sausages': ['Frankfurter', 'Italian Sausage', 'Kielbasa', 'Veggie', 'Cheddarwurst'], 'buns': ['Regular Bun', 'Chigago Bun', 'Hoagie Roll', 'Pretzel Bun', 'Pumpernickel Roll'], 'toppings': ['Cheese', 'Chili', 'Relish', 'Onions', 'Marinara Sauce', 'Sauerkraut', 'Pineapple Relish', 'Fajita Veggies', 'Salsa', 'Mushrooms', 'Jalapeños', 'Ketchup', 'Mustard', "Papa's Ballpark Mustard", 'Mayo', 'Hot Sauce', 'Wild Onion Sauce', 'Southwest Sauce'], 'placeableToppings': ['3 Tomato Wedges', '3 Sport Peppers', 'a Pickle Slice', 'a Bacon Slice'], 'cups': ['Small', 'Medium', 'Large'], 'sodas': ['Fizzo', 'Hyper Green', 'Diet Fizzo', 'Dr. Cherry', 'Lemon Mist', 'Tangerine Pop', 'Root Beer', 'Purple Burple'], 'popcorn': ['Buttered Popcorn', 'Candy Jack Popcorn', 'Kettle Corn', 'Chocolate Popcorn', 'Red Hot Popcorn', 'Cinnamon Swirl Popcorn', 'Cheddar Corn', 'Cotton Puffs']}, 'january': [{'name': 'New Year', 'buns': ['Fried Chicken Bun'], 'toppings': ['Fruity Hoops', 'Cheezy Whip'], 'sodas': ['Fizzo Quartz'], 'popcorn': ['X Puffs']}], 'february': [{'name': 'Valentines Day', 'buns': ['Beetbread Bun'], 'toppings': ['Sundried Tomatoes', 'Strawberry Vinaigrette'], 'sodas': ['Razzle Dazzle'], 'popcorn': ['Cherry Cordial Corn']}], 'march': [{'name': "St. Paddy's Day", 'buns': ['Barmbrack Bun'], 'toppings': ['Sage Derby Cheese', 'Irish Parsley Sauce'], 'sodas': ['Shamrock Splash'], 'popcorn': ['Paddy Popcorn']}], 'april': [{'name': 'Easter', 'buns': ['Paska Bun'], 'toppings': ['Blue Cheese Crumbles', 'Blackberry Remoulade'], 'sodas': ['Lavender Frost'], 'popcorn': []}], 'may': [{'name': 'Cinco de Mayo', 'buns': ['Bollio Bun'], 'toppings': ['Fire Tortilla Strips', 'Enchilada Sauce'], 'sodas': ['Mango de Mayo'], 'popcorn': ['Cancha Corn']}, {'name': 'Cherry Blossom Festival', 'buns': ['Melon Pan Bun'], 'toppings': ['Radish Sprouts', 'Wasabi Mayo'], 'sodas': ['Sakura Spritz'], 'popcorn': ['Yomogi Popcorn']}], 'june': [{'name': 'Summer Luau', 'buns': ['Hawaiian Bun'], 'toppings': ['Poke', 'Calypso Sauce'], 'sodas': ["Poppin' Coolada"], 'popcorn': ['Tropical Charms Popcorn']}], 'july': [{'name': 'Starlight BBQ', 'buns': ['Somked Cheddar Bun'], 'toppings': ['Pulled Pork', 'Lone Star Pit Sauce'], 'sodas': ['Starlight Sparkler'], 'popcorn': ['Jubilee Popcorn']}], 'august': [{'name': 'Groovstock', 'buns': ['Campargain Bun'], 'toppings': ['Kale', 'Karmic Korma Sauce'], 'sodas': ['Ginger Haze'], 'popcorn': ['Artisanal Truffle Corn']}, {'name': 'Comet Con', 'buns': ['Lunar Loaf Bun'], 'toppings': ['Pulsar Pesto', 'Space Ration ZX85'], 'sodas': ['Hyper Green'], 'popcorn': ['Pluto Puffs']}], 'september': [{'name': 'Maple Mornings', 'buns': ['French Toast Bun'], 'toppings': ['Hash Browns', 'Sausage Gravy'], 'sodas': ['Breakfast Blast'], 'popcorn': ['Bacon Jack Popcorn']}, {'name': 'SugarPlex FilmFest', 'buns': ['Hollywood Bun'], 'toppings': ['Boston Beanies', 'Blockbuster Butter'], 'sodas': ['Fizzo Gold'], 'popcorn': ['Raisin Duds Popcorn']}], 'october': [{'name': 'Halloween', 'buns': ['Pan de Muerto Bun'], 'toppings': ['Spooky Slaw', 'La Catrina Sauce'], 'sodas': ['Black Mist'], 'popcorn': ['Tarantula Puffs']}], 'november': [{'name': 'Thanksgiving', 'buns': [], 'toppings': ['Stuffing', 'Gravy'], 'sodas': ['Dream Cream'], 'popcorn': ['Pumpkin Spice Popcorn']}], 'december': [{'name': 'Christmas', 'buns': ['Fruitcake Bun'], 'toppings': ['Cranbery Chutney', 'Eggnog Aioli'], 'sodas': ['Dr. Dasher'], 'popcorn': ['Frostcap Crunch']}]},
    'burgeria': {'allTime': {'grills': ['Rare', 'Regular', 'Well Done'], 'toppings': ['American Cheese', 'Lettuce', 'Onions', 'Pickles', 'Tomato', 'Bacon', 'Swiss Cheese', 'Mushrooms', 'Pepperjack Cheese', 'Onion Rings', 'Jalapeños', 'Fried Egg', 'BBQ Sauce', 'Ketchup', 'Mayo', 'Mustard', 'Awesome Sauce']}},
    'pastaria': {'allTime': {'pastas': ['Macaroni', 'Spaghetti', 'Gnocchi', 'Ravioli', 'Fettuchine', 'Bowtie', 'Penne', 'Radiatori'], 'cooks': ['Al-Dente', 'Regularly Done'], 'sauces': ['Creamy Alfredo', "Papa's Marinara", 'Three Cheese', 'Garlic Basil', 'Beefy Bolognese'], 'shakers': ['Parmesan Cheese', 'Grated Mozzarella', 'Crushida Pepper', 'Italian Seasoning', 'Black Pepper'], 'placeableToppings': ['Meatballs', 'Mushrooms', 'Chicken', 'Sausage', 'Tomatoes', 'Shrimp', 'Clams', 'Onions', 'Prosciutto', 'Fried Calamari', 'Green Peppers', 'Grilled Polenta'], 'breads': ['Garlic Breadstick', 'Cheesy Bread', 'Focaccia', 'Poppyseed Roll', 'Crescent Roll', 'Pepperoni Bread']}, 'january': [{'name': 'New Year', 'pastas': ['Rainbow Gramigna'], 'sauces': ['Midnight Marsala'], 'shakers': ['Rainbow Peppercorn'], 'placeableToppings': ['Cheese Cubes']}, {'name': 'Lunar New Year', 'pastas': ['Longevity Noodles'], 'sauces': ['XO Sauce'], 'shakers': ['Sesame Seeds'], 'placeableToppings': ['Potstickers']}], 'february': [{'name': "Valentine's Day", 'pastas': ['Valentini'], 'sauces': ['Heartbeet Arrabbiata'], 'shakers': ['Spiced Safron'], 'placeableToppings': ['Cherry Tomatoes']}, {'name': 'Mardi Gras', 'pastas': ['Jambalaya Rice'], 'sauces': ['Zydeco Gumbo'], 'shakers': ['Creole Rub'], 'placeableToppings': ['Gator Bites']}], 'march': [{'name': "St. Paddy's Day", 'pastas': ['Cloveroni'], 'sauces': ['Zesty Pesto'], 'shakers': ['Lucky Dust'], 'placeableToppings': ['Broccoli']}], 'april': [{'name': 'Romana Wedding', 'pastas': ['Fiori Risoni'], 'sauces': ['Cathedral Carbonara'], 'shakers': ['Bouquet Blend'], 'placeableToppings': ['Pickled Eggs']}], 'may': [{'name': 'ChiliFest', 'pastas': ['Cellentani'], 'sauces': ["Rico's Chili"], 'shakers': ['Cheddar Cheese'], 'placeableToppings': ['Chili Pepper']}], 'june': [{'name': 'Summer Luau', 'pastas': ['Shells'], 'sauces': ['Pineapple Pancetta'], 'shakers': ['Lemon Herb'], 'placeableToppings': ['Glazed Ham']}], 'july': [{'name': 'Starlight Jubilee', 'pastas': ['Stellini'], 'sauces': ['Rocket Ragu'], 'shakers': ['Blue Cheese'], 'placeableToppings': ['Provolone Stars']}], 'august': [{'name': "Neptune's Feast", 'pastas': ['Crab Mezzelune'], 'sauces': ['Ventian Vongole'], 'shakers': ['Creole Rub', 'Bottarga'], 'placeableToppings': ['Anchovies']}], 'september': [{'name': 'Gondola 500', 'pastas': ['Mafaldine'], 'sauces': ['Hurry Curry'], 'shakers': ['Garlic Rush'], 'placeableToppings': ['Fried Ravioli']}], 'october': [{'name': 'Halloween', 'pastas': ['Vermicelli'], 'sauces': ['Purple Pesto'], 'shakers': ['Cauldron Powder'], 'placeableToppings': ['Mussels']}], 'november': [{'name': 'Thanksgiving', 'pastas': ['Harvest Tortellini'], 'sauces': ['Pumpkin Pomodoro'], 'shakers': ['Crushed Croutons'], 'placeableToppings': ['Roasted Turkey']}], 'december': [{'name': 'Christmas', 'pastas': ['Festive Rotini'], 'sauces': ['Roasred Romana'], 'shakers': ['Yule Spice'], 'placeableToppings': ['Basil Leaves']}]},
    'cheeseria': {'allTime': {'breads': ['Flatbread', 'Marble Rye', 'Multigrain Bread', 'Sourdogh', 'Wheat Bread', 'White Bread', 'Rosemary Focaccia', 'Pumpernickel', 'Ciabatta', 'Three Cheese Bread', 'Pretzel Bread'], 'cheeses': ['American Cheese', 'Marble Colby Cheese', 'Pepperjack Cheese', 'Shredded Cheddar', 'Shredded Mozzarella', 'Swiss Cheese', 'Aged Gouda', 'Provolone Cheese', 'Asiago Cheese', 'Harvati Cheese', 'Gorgonzola Cheese'], 'fillings': ['Bacon', 'Diced Tomatoes', 'Shredded Lettuce', 'Sliced Ham', 'Sliced Turkey', 'Grilled Chicken', 'Jalapeños', 'Fajita Peppers', 'Pulled Pork', 'Sauteed Onions', 'Sliced Salami', 'Fried Egg', 'Philly Steak', 'Lobster Chunks', 'Corned Beef', 'Mushrooms', 'Deep-Fried Pickles', 'Sauerkraut', 'Olives', 'Ketchup', 'Mustard', 'Ranch', 'Buffalo Sauce', 'BBQ Sauce', 'Buffalo Sauce', 'Southwest Sauce', 'Wild Onion Sauce', 'Awesome Sauce', 'Honey Mustard', 'Balsamic Dressing'], 'timings': ['Lightly Done', 'Regularly Done', 'Well-Done'], 'fries': ['Curly Fries', 'French Fries', 'Waffle Fries', 'Sweet Potato Wedges', 'Crinkle Cut Fries'], 'fryToppings': ['Bacobites', 'Cheddar Topping', 'Ketchup', 'Ranch', 'BBQ Sauce', 'Jalapeños', "Rico's Chilli", 'Rosemary', 'Sour Cream', 'Awsome Sauce', 'Chives', 'Nacho Sauce', 'Fry Seasoning', 'Poutine']}, 'january': [{'name': 'New Year', 'breads': ['Cheddar Swirl Bread'], 'cheeses': ['Gruyere Cheese'], 'fillings': ["Mac n' Cheese", 'Parmesan Sauce'], 'fryToppings': ['Cheese Cubes', 'Parmesan Sauce']}], 'february': [{'name': "Valentine's Day", 'breads': ['Beetbread'], 'cheeses': ['Red Windsor Cheese'], 'fillings': ['Sun Dried Tomatoes', 'Strawberry Vinaigrette'], 'fryToppings': ['Salsa Criolla']}], 'march': [{'name': "St. Paddy's Day", 'breads': ['Barmbrack Bread'], 'cheeses': ['Sage Derby Cheese'], 'fillings': ['Corned Beef Hash', 'Irish Parsley Sauce'], 'fryToppings': []}, {'name': 'Holi', 'breads': ['Naan Bread'], 'cheeses': ['Paneer Cheese'], 'fillings': ['Pakoras', 'Bellulli Chutney'], 'fryToppings': ['Curry Powder', 'Bellulli Chutney']}], 'april': [{'name': 'Easter', 'breads': ['Paska Bread'], 'cheeses': ['Sirecz Cheese'], 'fillings': ['Pickled Eggs', 'Hollandaise Sauce'], 'fryToppings': ['Shredded Carrots', 'Hollandaise Sauce']}], 'may': [{'name': 'Cinco de Mayo', 'breads': ['Tortilla'], 'cheeses': ['Oaxaca Cheese'], 'fillings': ['Chorizo Sausage', 'Guacamole'], 'fryToppings': ['Black Beans', 'Guacamole']}], 'june': [{'name': 'Summer Luau', 'breads': ['Hawaiian Roll'], 'cheeses': ['Mango Cream Cheese'], 'fillings': ['Pineapple', 'Calypso Sauce'], 'fryToppings': ['Lemon Herb Seasoning']}], 'july': [{'name': 'Starlight BBQ', 'breads': ['Texas Toast'], 'cheeses': ['Smoked Cheddar'], 'fillings': ['Sliced Beef Brisket', 'Lone Star Pit Sauce'], 'fryToppings': ['Burnt Ends']}], 'august': [{'name': 'Portallini Fest', 'breads': ['Pepperoni Bread'], 'cheeses': ['Ricotta Cheese'], 'fillings': ['Meatballs', 'Marinara Sauce'], 'fryToppings': ['Sausage Crumbles', 'Marinara Sauce']}], 'september': [{'name': 'Maple Mornings', 'breads': ['Cinnamon Toast'], 'cheeses': ['Maple Jack Cheese'], 'fillings': ['Maple Mini Sausages', 'Maple Syrup'], 'fryToppings': []}, {'name': 'Pirate Bash', 'breads': ['Crossbone Bread'], 'cheeses': ['Calico Jack Cheese'], 'fillings': ['Anchovies', 'Blazeberry Sauce'], 'fryToppings': ['Caviar', 'Blazeberry Sauce']}], 'october': [{'name': 'Halloween', 'breads': ['Ecto Bread'], 'cheeses': ['Monster Muenster'], 'fillings': ['Spooky Slaw', 'Jackmomole'], 'fryToppings': ['Cauldron Powder', 'Jackmomole']}], 'november': [{'name': 'Thanksgiving', 'breads': ['Pumpkin Bread'], 'cheeses': ['Cheese Ball Spread'], 'fillings': ['Stuffing', 'Gravy'], 'fryToppings': ['Roasted Pumpkin Seeds', 'Gravy']}], 'december': [{'name': 'Christmas', 'breads': ['Fruitcake'], 'cheeses': ['Ginger Spice Cheese'], 'fillings': ['Roasted Goose', 'Cranberry Chutney'], 'fryToppings': ['Yule Spice', 'Cranberry Chutney']}]},
    'cluckeria': {'allTime': {'meats': ['Chicken Breast', 'Chicken', 'Veggie', 'Fish Fillet', 'Schnitzel', 'Pork Chop', 'Country Steak', 'Eggplant', 'Cod', 'Soft Shell Crab'], 'breadings': ['Beer Batter', "Papa's Original Breading", 'Spicy Cajun Batter', 'Pretzel Crust Breading', 'Cheez Puff Breading', 'Panko Breading', 'Tempura Batter', 'Sweet Belgian Batter'], 'buns': ['Classic', 'Croissant', 'Sesame', 'Buttermilk Biscuit', 'Multigrain', 'Kaiser Onion Roll', 'Bagel', 'Brioche'], 'toppings': ['Bacon', 'Cheddar Cheese', 'Creamy Coleslaw', 'Jalapeños', 'Onion', 'Onion Straws', 'Pickles', 'Provolone Cheese', 'Summer Crisp Lettuce', 'Tomato', 'Red Cabbage Slaw', 'Watercress', 'Banana Peppers', 'Fried Egg', 'Grilled Portobello Cap', 'Pickled Red Onions', 'Radish Sprouts', 'Sliced Avocado', 'Pineapple Ring', 'Pepperjack Cheese', 'BBQ Sauce', 'Blazeberry Sauce', 'Buffalo Sauce', 'Honey Mustard Sauce', 'Marinara Sauce', 'Mayo', 'Teriyaki Sauce', 'Tartar Sauce', 'Nashville Hot Sauce', 'Country Gravy', 'Peri Peri Sauce', 'Paprikash Sauce', 'Sticky Bourbon Sauce', 'Coronation Sauce'], 'slushSizes': ['Small', 'Medium', 'Large'], 'slushFlavours': ['Black Cherry', 'Blue Raspberry', 'Cream Soda', 'Lemonade', 'Sour Apple', 'Tangerine', 'Watermelon', 'Sweet Tea', 'Root Beer', 'Purple Burple', 'Pineapple', 'Dragonfruit', 'Bubblegum', 'Kiwi']}, 'january': [{'name': 'New Year', 'buns': ['Rainbow Rye'], 'toppings': ['Bolician Chiles', 'Wild Onion Sauce', 'Potato Chips', 'Midnight Marsala'], 'slushFlavours': ['Tutti Frutti']}], 'february': [{'name': "Valentine's Day", 'buns': ['Pink Poppyseed'], 'toppings': ['Radicchio', 'Heartbeet Arrabbiata', 'Prosciutto', 'Nogada Sauce'], 'slushFlavours': ['Hot Rods']}], 'march': [{'name': 'Lucky Lucky Matsuri', 'buns': ['Cheung Chau'], 'toppings': ['Lotus Root', 'Karashi Mayo', 'Kimchi', 'Gochujang Sauce'], 'slushFlavours': ['Iyokan']}], 'april': [{'name': 'Easter', 'buns': ['Pasqua'], 'toppings': ['Pickled Carrots', 'Wildflower Carbonara', 'Mixed Microgreens', 'Blackberry Remoulade'], 'slushFlavours': ['Cotton Candy']}], 'may': [{'name': 'Comet Con', 'buns': ['Lunar Loaf'], 'toppings': ['Starfruit', 'Astro Elixir', 'Space Ration ZX26', 'Hyper Green Sauce'], 'slushFlavours': ['Galaxy Grape']}], 'june': [{'name': 'Summer Luau', 'buns': ['Hawaiian'], 'toppings': ['Kalua Ham', 'Mango Chili Sauce', 'Grilled Plantains', 'Hula Hula Sauce'], 'slushFlavours': ['Luau Punch']}], 'july': [{'name': 'Starlight BBQ', 'buns': ['Smoked Cheddar'], 'toppings': ["Mac n' Cheese", 'Mambo Sauce', 'Baked Beans', 'Lone Star Pit Sauce'], 'slushFlavours': ['Powsicle']}], 'august': [{'name': 'BavariaFest', 'buns': ['Pretzel'], 'toppings': ['Sauerkraut', 'Bierkäse', 'Bratwurst', 'Marzen Mustard'], 'slushFlavours': ['Blockmalz']}], 'september': [{'name': 'Maple Mornings', 'buns': ['Waffle'], 'toppings': ['Hash Brown Patty', 'Maple Syrup', 'Sausage Party', 'Hollandaise Sauce'], 'slushFlavours': ['Cinnamon Swirl']}], 'october': [{'name': 'Day of the Dead', 'buns': ['Pan de Muerto'], 'toppings': ['Chicharrones', 'La Catrina Sauce', 'Tamalito', 'Mole Mística'], 'slushFlavours': ['Chamoyada']}], 'november': [{'name': 'Thanksgiving', 'buns': ['Frybread'], 'toppings': ['Mashed Potatoes', 'Gravy', 'Turducken', 'Wojapi Sauce'], 'slushFlavours': ['Pumpkin Spice']}], 'december': [{'name': 'Christmas', 'buns': ['Jack Frost'], 'toppings': ['Canned Cranberry', 'Creamy Pistachio Sauce', 'Arugula Wreaths', 'Krampus Sauce'], 'slushFlavours': ['Dr. Dasher']}]},
    'scooperia': {'allTime': {'doughs': ['Fudge', 'Traditional', 'Peanut Butter', 'Lemon Crinkle', 'Red Velvet', 'Oatmeal', 'Gingerbread', 'Snickerdoodle'], 'mixables': ['Chocolate Chips', 'Peanuts', 'White Chocolate Chips', "Yum n' Ms", 'Toffee Chunks', 'Pomegranate', 'Sugar Crystals', 'Dried Kiwi', 'Blackberry Bark', 'Coconut', 'Citrus Zest', 'Blueberries', 'Hot Rods', 'Butterzinger Bits', 'Raisins', 'Pretzel Bits', 'Mint Bar Chunks', 'Potato Chips'], 'iceCreams': ['Chocolate', 'Cookies and Cream', 'Strawberry', 'Vanilla', 'Mint Chocolate Chip', 'Purple Burple', 'Hokey Pokey', 'Spumoni', 'Raspberry Ripple', 'Pistachio', 'Blue Moon', 'Coco Coolada', 'Watermelon Chip', 'Cookie Dough', 'Tiger Tail', 'Rocky Road', 'Mocha Chocolate Chunk', 'Ambrosia', 'Moon Mist'], 'toppings': ['Whipped Cream', 'Chocolate Mousse', 'Chocolate Syrup', 'Strawberry Syrup', 'Butterscotch Syrup', 'Peanuts', 'Rainbow Sprinkles', 'Shaved Chocolate', 'Pistachios', 'Mini Mallows', 'Rock Candy', 'Cookie Dough Bits'], 'placeableToppings': ['Cherry', 'Waffle Cone', 'Salted Caramel', 'Chocolate Mint', 'Banana', 'Macaron', 'Sugarplum', 'Ladyfinger', 'Blueberry Swizzle']}, 'january': [{'name': 'New Year', 'mixables': ['Licorice Allsorts', 'Countdown Candies'], 'iceCreams': ['Tutti Frutti'], 'toppings': ['Licorice Allsorts', 'Flavour X Syrup'], 'placeableToppings': ['Rainbow Meringue']}], 'february': [{'name': "Valentine's Day", 'mixables': ['Candy Hearts', 'X and O Sprinkles'], 'iceCreams': ['Cherry Cordial'], 'toppings': ['Candy Hearts', 'Cherry Cheesecake Syrup'], 'placeableToppings': ['Chocolate Strawberry']}], 'march': [{'name': 'Holi', 'mixables': ['Holi Sugar', 'Dried Jackfruit'], 'iceCreams': ['Saffron Kulfi'], 'toppings': ['Holi Sugar', 'Kanji Syrup'], 'placeableToppings': ['Kaju Katli']}], 'april': [{'name': 'Cherry Blossom Festival', 'mixables': ['Konpeito', 'Cucumber Bubbles'], 'iceCreams': ['Hakuto'], 'toppings': ['Konpeito', 'Matcha Syrup'], 'placeableToppings': ['Sakuramochi']}, {'name': 'Easter', 'mixables': ['Jelly Beans', 'Spring Flowers'], 'iceCreams': ['Cremebury Egg'], 'toppings': ['Jelly Beans', 'Lavender Lemonade Syrup'], 'placeableToppings': ['Lavender Cheep']}], 'may': [{'name': 'OnionFest', 'mixables': ['Sourballs', 'Onion Zest'], 'iceCreams': ['Onion Overdrive'], 'toppings': ['Sourballs', 'Sugar Shallot Syrup'], 'placeableToppings': ['Gummy Onions']}, {'name': 'Cinco de Mayo', 'mixables': ['Cinco Swirls', 'Capirotada Blend'], 'iceCreams': ['Chamoyada'], 'toppings': ['Cinco Swirls', 'Champurrado Syrup'], 'placeableToppings': ['Churro']}], 'june': [{'name': 'Summer Luau', 'mixables': ['Tropical Charms', 'Splashberry Derps'], 'iceCreams': ['Passionfruit'], 'toppings': ['Tropical Charms', 'Luau Punch Syrup'], 'placeableToppings': ['Lemon Wedge']}], 'july': [{'name': 'Starlight Jubilee', 'mixables': ['Star Sprinkles', 'Crackle Crumbs'], 'iceCreams': ['Powsicle'], 'toppings': ['Star Sprinkles', 'Cherrybomb Syrup'], 'placeableToppings': ['Candy Rocket']}], 'august': [{'name': 'Baseball Season', 'mixables': ['Candy Jack', 'Sunflower Seeds'], 'iceCreams': ['Curveball Crunch'], 'toppings': ['Candy Jack', 'Peanut Butter Fluff'], 'placeableToppings': ['Candy Baseball']}], 'september': [{'name': 'Big Top Carnival', 'mixables': ['Chocolate Bacon', 'Lollipop Bits'], 'iceCreams': ['Caramel Apple'], 'toppings': ['Chocolate Bacon', 'Cotton Candy Syrup'], 'placeableToppings': ['Chocolate Banana']}], 'october': [{'name': 'Halloween', 'mixables': ['Shadowberry Derps', 'Scary Suga Eyes'], 'iceCreams': ['Cobweb Ripple'], 'toppings': ['Shadowberry Derps', "Witch's Brew Syrup"], 'placeableToppings': ['Gummy Spider']}], 'november': [{'name': 'Thanksgiving', 'mixables': ['Candy Corn', 'Pecans'], 'iceCreams': ['Pumpkin Pie'], 'toppings': ['Candy Corn', 'Crème Brulée Syrup'], 'placeableToppings': ['Buckeye']}], 'december': [{'name': 'Christmas', 'mixables': ["Holiday Yum n' Ms", 'Frostcaps'], 'iceCreams': ['Wintergreen Frost'], 'toppings': ["Holiday Yum n' Ms", "Santa's Cookie Syrup"], 'placeableToppings': ['Candy Cane']}]},
    'pancakeria': {'allTime': {'bases': ['Pancake', 'French Toast', 'Waffle'], 'mixables': ['Blueberry Mix', 'Chocolate Chip Mix', 'Pecan Mix', 'Bacon Mix'], 'toppings': ['Blueberries', 'Chocolate Chips', 'Raspberries', 'Cinnamon', 'Powdered Sugar', 'Blueberry Syrup', 'Maple Syrup', 'Whipped Cream', 'Honey', 'Strawberry Syrup'], 'placeableToppings': ['Butter', 'Banana', 'Srawberry'], 'drinkSizes': ['Small', 'Large'], 'drinks': ['Coffee', 'Decaf', 'Tea', 'Orange Juice', 'Milk'], 'drinkExtras': ['Cream', 'Sugar', 'Ice', 'Cocoa']}, 'january': [{'name': 'New Year', 'toppings': ['Flavour X Drizzle', 'Countdown Crunch'], 'placeableToppings': ['Confetti Pie-Tart'], 'drinks': ['Sparkling Grape Juice']}], 'february': [{'name': "Valentine's Day", 'toppings': ['Red Velvet Syrup', 'Cheesecake Crumbles'], 'placeableToppings': ['Candy Heart'], 'drinks': ['Cranberry Juice']}], 'march': [{'name': "St. Paddy's Day", 'toppings': ['Mint Cream', 'Pistachios'], 'placeableToppings': ['Mint Creameo Cookie'], 'drinks': ['Irish Cream Coffee']}], 'april': [{'name': 'Cherry Blossom Festival', 'toppings': ['Kuromitsu Drizzle', 'Oiri'], 'placeableToppings': ['Wasanbon Blossom'], 'drinks': ['Matcha Tea']}, {'name': 'Easter', 'toppings': ['Cotton Candy Drizzle', 'Jelly Beans'], 'placeableToppings': ['Cremebury Egg'], 'drinks': ['Wildberry Shake']}], 'may': [{'name': 'Cinco de Mayo', 'toppings': ['Cajeta Syrup', 'Cinco Swirls'], 'placeableToppings': ['Guava Roll'], 'drinks': ['Horchata']}], 'june': [{'name': 'Summer Luau', 'toppings': ['Passionfruit Drizzle', 'Toasted Coconut'], 'placeableToppings': ['Pineapple Slice'], 'drinks': ['Luau Punch']}], 'july': [{'name': 'Starlight Jubilee', 'toppings': ['Rocket Whip', 'Blue Star Sprinkles'], 'placeableToppings': ['Star Cookie'], 'drinks': ['Powsicle Punch']}], 'august': [{'name': 'BavariaFest', 'toppings': ['Buttermilk Syrup', 'Gebrannte Mandeln'], 'placeableToppings': ['Linzer Augen'], 'drinks': ['Eiskaffee']}, {'name': 'SugarPlex FilmFest', 'toppings': ['Butterzinger Syrup', 'Raisin Duds'], 'placeableToppings': ['Sweetish Fish'], 'drinks': ['Fizzo Gold']}], 'september': [{'name': 'Pirate Bash', 'toppings': ['Skallywag Syrup', 'Black Pearl Crisps'], 'placeableToppings': ['Gummy Kraken'], 'drinks': ['Sunken Treasure Tea']}, {'name': 'Groovstock', 'toppings': ['Salted Caramel Drizzle', 'Trail Mix'], 'placeableToppings': ['Misson Fig'], 'drinks': ['Chai Reverb Tea']}], 'october': [{'name': 'Halloween', 'toppings': ['Scream Cream', 'Shadowberry Derps'], 'placeableToppings': ['Candy Corn'], 'drinks': ["Witch's Brew"]}], 'november': [{'name': 'Thanksgiving', 'toppings': ['Pumpkin Pie Drizzle', 'Streusel'], 'placeableToppings': ['Pecan Praline'], 'drinks': ['Pumpkin Spice Coffee']}], 'december': [{'name': 'Christmas', 'toppings': ['Candy Cane Drizzle', "Holiday Yum n' Ms"], 'placeableToppings': ['Christmas Jelly Cookie'], 'drinks': ['Eggnog']}]},
    'cupcakeria': {'allTime': {'cakes': ['Chocolate', 'Vanilla', 'Blueberry', 'Strawberry', 'Carrot', 'Lemon', 'Red Velvet', 'Confetti', 'Zebra Stripe', 'Kiwi'], 'icings': ['Pink', 'White', 'Chocolate', 'Violet', 'Green', 'Teal', 'Dark Blue', 'Red', 'Black', 'Orange', 'Deep Purple', 'Mocha', 'Sunglow', 'Forest Green'], 'drizzles': ['Chocolate', 'Strawberry', 'Vanilla', 'Blue Moon', 'Apricot', 'Purple Burple'], 'shakers': ['Chocolate Chips', 'Rainbow Sprinkles', 'Shaved Coconut', 'Creameo Bits', 'Rock Candy', 'Lollipop Bits', 'Sourballs'], 'placeableToppings': ['Cherry', 'Marshmallow', 'Nutty Butter Cup', 'Cloudberry', 'Gummy Onion', 'Frosted Flower', 'Straberry Wafer', 'Salted Caramel']}, 'january': [{'name': 'New Year', 'cakes': [], 'drizzles': ['Flavor X'], 'shakers': ['Stache Sprinkles'], 'placeableToppings': ['New Year Topper', 'Streamer', 'Candle']}], 'february': [{'name': "Valentine's Day", 'cakes': ['Raspberry White Chocolate'], 'drizzles': ['Watermelon'], 'shakers': ['X and O Sprinkles'], 'placeableToppings': ['Chocolate Strawberry', 'Candy Heart', 'Frosted Rose']}], 'march': [{'name': "St. Paddy's Day", 'cakes': ['Green Emerald'], 'drizzles': ['Pistachio'], 'shakers': ['Mint Shavings'], 'placeableToppings': ['Mint Bar', 'Shamrock', 'Chocolate Coin']}], 'april': [{'name': 'Easter', 'cakes': ['Battenberg'], 'drizzles': ['Cotton Candy'], 'shakers': ['Jelly Beans'], 'placeableToppings': ['Bunny Ear Candy', 'Candy Egg', 'Tulip Cookie']}], 'may': [{'name': 'OnionFest', 'cakes': [], 'drizzles': [], 'shakers': [], 'placeableToppings': ['Sarge Gobstopper', 'Frosted Onion']}, {'name': 'Cinco de Mayo', 'cakes': ['Horchata'], 'drizzles': ['Cocoa Chipotle'], 'shakers': ['Cinco Swirls'], 'placeableToppings': ['Sombrero', 'Churro', 'Candy Cactus']}, {'name': 'Cherry Blossom Festival', 'cakes': ['Botamochi'], 'drizzles': ['Matcha'], 'shakers': ['Konpeito'], 'placeableToppings': ['Wasanbon Blossom', 'Uiro', 'Pogos']}], 'june': [{'name': 'Summer Luau', 'cakes': ['Seafoam'], 'drizzles': ['Honey'], 'shakers': ['Tropical Charms'], 'placeableToppings': ['Paper Umbrella', 'Gummy Pineapple', 'Bananas', 'Lemon Wedge']}], 'july': [{'name': 'Starlight Jubilee', 'cakes': ['Powsicle'], 'drizzles': ['Powsicle', 'Jubilee Jelly'], 'shakers': ['Silver Star Sprinkles'], 'placeableToppings': ['Candy Rocket', 'Festive Flag', 'White Chocolate Star']}], 'august': [{'name': 'Baseball Season', 'cakes': [], 'drizzles': ['Butterscotch'], 'shakers': ['Crushed Peanuts'], 'placeableToppings': ['Pretzel Bat', 'Candy Baseball', 'Popcorn']}, {'name': 'Big Top Carnival', 'cakes': ['Apple Crumb'], 'drizzles': ['Caramel Apple'], 'shakers': ['Popcorn'], 'placeableToppings': ['Cotton Candy', 'Saltwater Taffy', 'Chocolate Banana']}, {'name': 'SugarPlex FilmFest', 'cakes': ['Root Beer Float'], 'drizzles': ['Dr. Cherry'], 'shakers': ['Raisin Duds'], 'placeableToppings': ['Popcorn', 'Red Licorice', 'Blots']}], 'september': [{'name': 'Pirate Bash', 'cakes': [], 'drizzles': ['Blueberry Wave'], 'shakers': ['Canonball Gum'], 'placeableToppings': ['Anchor Cookie', 'Jolly Roger', 'Gummy Kraken']}, {'name': 'Comet Con', 'cakes': ['Cosmo'], 'drizzles': ['Hyper Green'], 'shakers': ['Asteriods'], 'placeableToppings': ['UFO Wafer', 'Astronaut Ice Cream', 'Bubble Planet']}, {'name': 'Maple Mornings', 'cakes': ['Cinnamon Roll'], 'drizzles': ['Maple Syrup'], 'shakers': ['Frosted Sugar Crunch'], 'placeableToppings': ['Mini Donut', 'Bacon', 'Waffle Stick']}], 'october': [{'name': 'Halloween', 'cakes': ['Tarantula'], 'drizzles': ['Licorice'], 'shakers': ['Spooky Sprinkles'], 'placeableToppings': ['Candy Jack-O-Lantern', 'Candy Corn', 'Sugar Skull']}], 'november': [{'name': 'Thanksgiving', 'cakes': ['Butter Pecan'], 'drizzles': ['Pumpkin Pie'], 'shakers': ['Autumn Leaves Sprinkles'], 'placeableToppings': ['Chocolate Acorn', 'Feather Cookie', 'Harvest Stripe Cookie']}], 'december': [{'name': 'Christmas', 'cakes': ['Holly Jolly'], 'drizzles': ['Santa Cookie', 'Candy Cane'], 'shakers': ['Crushed Candy Canes', 'Frostcaps'], 'placeableToppings': ['Candy Present', 'Gingerbread Man', 'Tree Cookie']}]},
    'bakeria': {'allTime': {'crusts': ['Chocolate', 'Graham Cracker', 'Traditional', 'Creameo', 'Ladyfingers', 'Red Velvet', 'Vanilla Crispies', 'Chocolate Chip', 'Peanut Butter Swirl', 'Gingersnap'], 'fillings': ['Apple', 'Cherry', 'Pecan', 'Fudge', 'Banana', 'Toffee', 'Cheesecake', 'Strawberry', 'Key Lime', 'Marshmallow', 'Lemon', 'Sugarplum', 'Dragonfruit', 'Pineapple', 'Peach', 'Blueberry', 'Kiwi', 'Rhubarb', 'Purple Yam', 'Peanut Butter'], 'tops': ['Lattice Top', 'Streusel Topping', 'Vented Crust', 'Meringue Topping', 'Polka Dot Crust', 'Chocolate Crumb Topping', 'Chocolate Meringue', 'Slit Top Crust'], 'toppings': ['Caramel Syrup', 'Cherry Syrup', 'Whipped Cream', 'White Chocolate Syrup', 'Chocolate Mousse', 'Chocolate Syrup', 'Huckleberry Syrup', 'Crushed Peanuts', 'Shaved Chocolate', 'Pistachios', 'Crushed Wafers', 'Toasted Coconuts', 'Blueberries', 'Blackberry Bark', 'Citrus Zest'], 'placeableToppings': ['Banana Slices', 'Cherries', 'Chocolate Mousse Dollops', 'Raspberries', 'Blueberry Pie-Tarts', 'Kumquats', 'Grape Jelly Cookies', 'Butterscotch Smooches', 'Kiwi Slices'], 'toppingPlacements': ['the Outer Third', 'the Middle Third', 'the Inner Third', 'the Hole Pie', 'the Inner 2 Thirds', 'the Outer 2 Thirds', 'the Inner Third and the Outer Third']}, 'january': [{'name': 'New Year', 'fillings': ['Tutti Frutti'], 'tops': ['Spiral Crust'], 'toppings': ['Flavour X Syrup'], 'placeableToppings': ["Yum n' M Cookies", 'Rainbow Meringue Dollops']}], 'february': [{'name': "Valentine's Day", 'fillings': ['Pomegranate'], 'tops': ['Heart Crust'], 'toppings': ['Lollipop Drizzle'], 'placeableToppings': ['Heart Cookies', 'Macarons']}], 'march': [{'name': "St. Paddy's Day", 'fillings': ['Choco Mint Custard'], 'tops': ['Celtic Knot Crust'], 'toppings': ['Mint Syrup'], 'placeableToppings': ['Clover Cookies', 'Chocolate Coins']}], 'april': [{'name': 'Easter', 'fillings': ['Jellybean Jam'], 'tops': ['Flower Bloom Crust'], 'toppings': ['Wildberry Whip'], 'placeableToppings': ['Cremebury Eggs', 'Lavender Cheeps']}], 'may': [{'name': 'Cherry Blossom Festival', 'fillings': ['Hakuto Jelly'], 'tops': ['Cherry Blossom Crust'], 'toppings': ['Matcha Syrup'], 'placeableToppings': ['Sakuramochi', 'Blossom Cookies']}, {'name': 'Big Top Carnival', 'fillings': ['Circus Peanut'], 'tops': ['Tent Top Crust'], 'toppings': ['Cotton Candy Syrup'], 'placeableToppings': ['Saltwater Taffies', 'Animal Crackers']}], 'june': [{'name': 'Summer Luau', 'fillings': ['Passionfruit'], 'tops': ['Sunburnt Crust'], 'toppings': ['Luau Punch Drizzle'], 'placeableToppings': ['Madeleines', 'Maui Meringue Dollops']}], 'july': [{'name': 'Starlight Jubilee', 'fillings': ['Mulberry Medley'], 'tops': ['Star Crust'], 'toppings': ['Rocket Whip'], 'placeableToppings': ['Dipped Strawberries', 'White Chocolate Star']}], 'august': [{'name': 'Comet Con', 'fillings': ['Starfruit'], 'tops': ['Crater Crust'], 'toppings': ['Hyper Green Syrup'], 'placeableToppings': ['Astronaut Ice Creams', 'Planet Cookies']}, {'name': 'SugarPlex FilmFest', 'fillings': ['Dual Licorice'], 'tops': ['Film Reel Crust'], 'toppings': ['Hot Rods Syrup'], 'placeableToppings': ['Popcorns', 'Sweetish Fish']}], 'september': [{'name': 'Groovstock', 'fillings': ['Misson Fig Jam'], 'tops': ['Lightning Crust'], 'toppings': ['Chai Reverb Drizzle'], 'placeableToppings': ['Music Notes', 'Marshmallow Drums']}], 'october': [{'name': 'Halloween', 'fillings': ['Shadowberry'], 'tops': ['Spiderweb Crust'], 'toppings': ['Scream Cream'], 'placeableToppings': ['Skull Cookies', 'Candy Corns']}], 'november': [{'name': 'Thanksgiving', 'fillings': ['Pumpkin'], 'tops': ['Autumn Leaves Crust'], 'toppings': ['Candy Corn Drizzle'], 'placeableToppings': ['Harvest Leaf Cookies', 'Chocolate Acorns']}], 'december': [{'name': 'Christmas', 'fillings': ['Peppermint Swirl Cream'], 'tops': ['Snowflake Crust'], 'toppings': ['Candy Cane Drizzle'], 'placeableToppings': ['Frosted Wreaths', 'Frosted Gifts']}]},
    'tacoMia': {'allTime': {'meats': ['Beef', 'Chicken', 'Pork', 'Steak'], 'shells': ['Hard Shell', 'Soft Shell', 'Pita Bread', 'Azul Ranch'], 'toppings': ['Cheese', 'Guacamole', 'Lettuce', 'Onions', 'Pinto Beans', 'Tomatoes', 'White Rice', 'Jalapeños', 'Peppers', 'Black Beans', 'Brown Rice', 'Refried Beans', 'Mild Sauce', 'Sour Cream', 'Hot Sauce', 'Nacho Cheese', 'Verde Sauce', 'Loco Mystery Sauce', 'Ancho Chile Sauce', 'Queso Blanco', 'Blazeberry Sauce'], 'chips': ['Chili Lime Tortillas', 'Traditional Chips', 'Blue Corn Chips', 'Multi-Grain Chips', 'Spicy Twists', 'Fiesta Chips', 'Nacho Cheese Chips', 'Pepperjack Rounds'], 'dips': ['Guacamole', 'Refried Beans', 'Nacho Cheese', 'Roasted Chili-Corn Salsa', 'Queso Blanco', 'Salsa Picante', 'Chile Serrano Salsa', 'Garlic Chipotle Dip', 'Pico de Gallo']}, 'january': [{'name': 'New Year', 'shells': ['Lava MunchMelt'], 'meats': ['Chorizo'], 'toppings': ['Fire Tortilla Strips', 'Diced Habaneros', 'Atomic Sauce']}], 'february': [{'name': "Valentine's Day", 'shells': ['Sundried Tomato Soft Shell'], 'meats': ['Anticucho'], 'toppings': ['Red Rice', 'Salsa Criolla', 'Nogada Sauce']}], 'march': [{'name': "St. Paddy's Day", 'shells': ['Cilantro Lime Soda Shell'], 'meats': ['Corned Beef Barbacoa'], 'toppings': ['Avocado', 'Diced Green Chiles', 'Creamy Tomatillo Sauce']}], 'april': [{'name': 'Easter', 'shells': ['Speckled'], 'meats': ['Battered Perch'], 'toppings': ['Spring Coleslaw', 'Blue Cheese Crumbles', 'Blackberry Remoulade']}], 'may': [{'name': 'Big Top Carnival', 'shells': ['Funnel Cake Shell'], 'meats': ['Corn Dog'], 'toppings': ['Chocolate Bacon', 'Cinnamon Swirl Popcorn', 'Caramel Apple Sauce']}, {'name': 'Cherry Blossom Festival', 'shells': ['Wonton Shell'], 'meats': ['Tofu'], 'toppings': ['Beni Shoga', 'Fried Crispy Noodles', 'Yum Yum Sauce']}], 'june': [{'name': 'Summer Luau', 'shells': ['Walking Taco Bag'], 'meats': ['Ahi Tuna'], 'toppings': ['Pineapple Salsa', 'Diced Kalua Ham', 'Mango Chilli Sauce']}], 'july': [{'name': 'Starlight BBQ', 'shells': ['Cornbread'], 'meats': ['Beef Brisket'], 'toppings': ['Fried Onion Rings', 'Baked Beans', 'Lone Star Pit Sauce']}], 'august': [{'name': 'BavariaFest', 'shells': ['Pretzel Crisp'], 'meats': ['Bratwurst'], 'toppings': ['Sauerkraut', 'Spätzle', 'Marzen Mustard']}, {'name': 'Portallini Feast', 'shells': ['Garlic and Olive Oil Piada'], 'meats': ['Gyro Meat'], 'toppings': ['Feta Cheese', 'Romaine Lettuce', 'Tzatziki']}], 'september': [{'name': 'Maple Mornings', 'shells': ['Waffle'], 'meats': ['Scrambled Eggs'], 'toppings': ['Hash Browns', 'Sausage Crumbles', 'Maple Syrup']}], 'october': [{'name': 'Halloween', 'shells': ['Midnight Crunch'], 'meats': ['Wild Boar'], 'toppings': ['Jack-o-Mole', 'Black Olives', 'La Catrina Sauce']}], 'november': [{'name': 'Thanksgiving', 'shells': ['Pumpkin Spice Tortilla'], 'meats': ['Turkey'], 'toppings': ['Southwest Stuffing', 'Diced Sweet Potatoes', 'Chichilo Mole']}], 'december': [{'name': 'Christmas', 'shells': ['Yule Spice Sizzler'], 'meats': ['Goose'], 'toppings': ['Cranberry Salsa', 'Pine Nuts', 'Chimichurri']}]},
    'wingeria': {'allTime': {'meats': ['Chicken Wings', 'Boneless Wings', 'Chicken Strips', 'Shrimp', 'Tofu Skewers', 'Hog Wings'], 'sauces': ['BBQ Sauce', 'Buffalo Sauce', 'Spicy Garlic Sauce', 'Calypso Sauce', 'Atomic Sauce', 'Honey Mustard Sauce', 'Teriyaki Sauce', 'Medium Sauce', 'Parmesan Sauce', 'Wild Onion Sauce', 'Wasabi Sauce', 'Smoky Bacon Sauce', 'Thai Chili Sauce', 'Blazeberry Sauce', 'Alabama BBQ Sauce', 'Nashville Hot Sauce', 'Peri Peri Sauce', 'Aji Amarillo Sauce', 'Carolina Sauce', 'Tikka Masala Sauce', 'Sriracha Sauce', 'Adobo Sauce'], 'sides': ['Carrots', 'Celery', 'Red Peppers', 'Green Peppers', 'French Fries', 'Cheese Cubes', 'Curly Fries', 'Potato Skins', 'Taquitos'], 'dips': ['Blue Cheese Dip', 'Ranch Dip', 'Awesome Sauce Dip', 'Kung Pao Dip', 'Zesty Pesto Dip', 'Lemon Butter', 'Southwest Dip', 'Hummus', 'Artichoke Dip', 'Guacamole', 'Blackberry Remoulade']}, 'january': [{'name': 'New Year', 'sauces': ['Rainbow-livian Sauce', 'Poutine Sauce'], 'sides': ['Pizza Poppers'], 'dips': ['Cheezy Whip']}], 'february': [{'name': 'Mardi Gras', 'sauces': ['Muffuletta Sauce', 'Vieux Carré Sauce'], 'sides': ['Crawdads'], 'dips': ['Creole Crab Dip']}], 'march': [{'name': 'Lucky Lucky Matsuri', 'sauces': ['Gochujang Sauce', 'Ginger Miso Sauce'], 'sides': ['Kobumaki'], 'dips': ['Karashi Mayo']}], 'april': [{'name': 'Big Top Carnival', 'sauces': ['Salted Caramel Sauce', 'Candy Apple Sauce'], 'sides': ['Corn Dogs'], 'dips': ['PB&J Dip']}], 'may': [{'name': 'OnionFest', 'sauces': ["Sarge's Revenge Sauce"], 'sides': ['Cocktail Onions'], 'dips': ['French Onion Dip']}], 'june': [{'name': 'Summer Luau', 'sauces': ['Kilauea Sauce', 'Hulu Hula Sauce'], 'sides': ['Luau Musubi'], 'dips': ['Mango-Chili Dip']}], 'july': [{'name': 'Starlight BBQ', 'sauces': ['Lone Star Pit Sauce', 'Mambo Sauce'], 'sides': ['BBQ Ribs'], 'dips': ['Coleslaw']}], 'august': [{'name': 'BavariaFest', 'sauces': ['Doppelbock Sauce', 'Würzig Sauce'], 'sides': ['Wiesswurst'], 'dips': ['Bierkäse Dip']}], 'september': [{'name': 'Maple Mornings', 'sauces': ['Maple Glaze', 'Sunrise Sauce'], 'sides': ['Bacon'], 'dips': ['Shirred Egg']}], 'october': [{'name': 'Halloween', 'sauces': ['La Catrina Sauce', 'Ecto Sauce'], 'sides': ['Mummy Dogs'], 'dips': ['Purple Pesto']}], 'november': [{'name': 'Thanksgiving', 'sauces': ['Peppered Pumpkin Sauce', 'Wojapi Sauce'], 'sides': ['Sweet Potato Wedges'], 'dips': ['Gravy']}], 'december': [{'name': 'Christmas', 'sauces': ['Cranberry Chili Sauce', 'Krampus Sauce'], 'sides': ['Roasted Asparagus'], 'dips': ['Risalamande']}]},
    'donuteria': {'allTime': {'doughs': ['Chocolate Cake', 'Regular', 'Pumpkin Cake', 'Red Velvet Cake', 'Blueberry Cake'], 'shapes': ['Ring', 'Round', 'Long John', 'French Cruller', 'Roll'], 'icings': ['Chocolate Icing', 'Clear Glaze', 'Powdered Sugar', 'Sky Blue Icing', 'Strawberry Icing', 'Vanilla Icing', 'Red Icing', 'Cinnamon Sugar', 'Orange Icing', 'Blue Nimbus Icing', 'Apricot Icing'], 'fillings': ['Bostom Cream', 'Strawberry Jam', 'Chocolate Mousse', 'Cookie Dough Cream', 'Whipped Cream', 'Blueberry Custard', 'Blackberry Jam', 'Lemon Chiffon'], 'sprinkles': ['Chocolate Chips', 'Cosmic Coconut', 'Rainbow Sprinkles', 'Mini-Mallows', 'Creameo Bits', 'Crushed Peanuts', 'Raspberry Bark', 'Rock Candy', 'Pistachios'], 'drizzles': ['Blue Moon', 'Strawerry', 'Vanilla', 'Chocolate', 'Dreamsicle', 'Caramel', 'Sugarplum', 'Banana', 'Neapolitan']}, 'january': [{'name': 'New Year', 'shapes': ['Infinity Loop'], 'icings': ['Midnight Powder'], 'fillings': ['Tutti Frutti Jam'], 'sprinkles': ['Countdown Crunch'], 'drizzles': ['Flavour X', 'Creameo']}], 'february': [{'name': "Valentine's Day", 'shapes': ['Heart'], 'icings': ['Valentine Powder'], 'fillings': ['Bubble Gum Cream'], 'sprinkles': ['Cupidberry Derps'], 'drizzles': ['Red Cinnamon']}, {'name': 'Mardi Gras', 'shapes': ['King Cake'], 'icings': ['Masquerade Powder'], 'fillings': ['Praline Sauce'], 'sprinkles': ['Fleur De Lis Sprinkles'], 'drizzles': ['Purple Burple', 'Doberge']}], 'march': [{'name': "St. Paddy's Day", 'shapes': ['Shamrock'], 'icings': ['Green Icing'], 'fillings': ['Mint Cream'], 'sprinkles': ['Lucky Sevens'], 'drizzles': ['Mint', 'Keylime']}], 'april': [{'name': 'Easter', 'shapes': ['Egg'], 'icings': ['Lavender Icing'], 'fillings': ['Marshmallow Cheeps Cream'], 'sprinkles': ['Jelly Beans'], 'drizzles': ['Wildberry Shake', 'Pink Lemonade']}], 'may': [{'name': 'Big Top Carnival', 'shapes': ['Bearclaw'], 'icings': ['Cotton Candy Icing'], 'fillings': ['Apple Pie Filling'], 'sprinkles': ['Candy Jack'], 'drizzles': ['Choco Banana', 'Caramel Apple']}, {'name': 'SugarPlex FilmFest', 'shapes': ['Letterbox'], 'icings': ['Golden Age Icing'], 'fillings': ['Root Beer Float Filling'], 'sprinkles': ['Baby Blots'], 'drizzles': ['Dual Licorice', 'Butterzinger']}], 'june': [{'name': 'Summer Luau', 'shapes': ['Seashell'], 'icings': ['Yellow Icing', 'Sunshine Icing'], 'fillings': ['Maui Meringue'], 'sprinkles': ['Tropical Charms'], 'drizzles': ['Mango', 'Luau Punch']}], 'july': [{'name': 'Starlight Jubilee', 'shapes': ['Star'], 'icings': ['Starlight Icing'], 'fillings': ['Jubilee Jam'], 'sprinkles': ['Blue Star Sprinkles'], 'drizzles': ['Powsicle', 'Cherrybomb']}], 'august': [{'name': 'Sky Ninja', 'shapes': ['Pon de Ring'], 'icings': ['Azuki Icing'], 'fillings': ['Hakuto Jam'], 'sprinkles': ['Boba Bubbles'], 'drizzles': ['Matcha', 'Cantaloupe']}], 'september': [{'name': 'Maple Mornings', 'shapes': ['Waffle'], 'icings': ['Maple Icing'], 'fillings': ['Mocha Cream'], 'sprinkles': ['Bacobites'], 'drizzles': ['Honey', 'Butterscotch']}], 'october': [{'name': 'Halloween', 'shapes': ['Skull'], 'icings': ['Full Moon Icing'], 'fillings': ['Brownie Batter'], 'sprinkles': ['Spooky Sprinkles'], 'drizzles': ['Peanut Butter', 'Licorice', 'Tiger Tail', "Witch's Brew"]}], 'november': [{'name': 'Thanksgiving', 'shapes': ['Acorn'], 'icings': ['Cocoa Powder'], 'fillings': ['Pumpkin Pie Filling'], 'sprinkles': ['Autumn Leaves Sprinkles'], 'drizzles': ['Candy Corn', 'Fudge Swirl']}], 'december': [{'name': 'Christmas', 'shapes': ['Tree'], 'icings': ['Festive Swirl Icing'], 'fillings': ['Cherry Cordial Cream'], 'sprinkles': ['Snowflake Sprinkles'], 'drizzles': ['Candy Cane', 'Santa Cookie']}]},
    'paleteria': {'allTime': {'shapes': ['Bar', 'Chuckle', 'Twin', 'Rocket', 'Wedge', 'Paddle'], 'fillings': ['Blueberry', 'Chocolate Chip', 'Kiwi', 'Pineapple', 'Pomegranate', 'Vanilla Wafer', 'Papaya', 'Tapioca Pearl', 'Nougat', 'Sourbatch Bear', 'Dragonfruit', 'Honeyocmb Crunch', 'Birthday Cake', 'Wildberry Derp', 'Banana Custard', 'Blueberry Yogurt', 'Chocolate Pudding', 'Strawberry Puree', 'Vanilla Custard', 'Orange Cream', 'Cajeta', 'Coconut Cream', 'Mamey Sorbet', 'Blackcurrent Puree', 'Taro Tapioca', 'Maple Creemee', 'Honeydew Gelato', 'Moon Mist Cream', 'Mango Puree'], 'dips': ['Chocolate', 'Cloudberry', 'White Chocolate', 'Blue Moon', 'Strawberry', 'Caramel', 'Key Lime'], 'toppings': ['Lemon Mist Drizzle', 'Marshmallow Drizzle', 'Watermelon Drizzle', 'Hazelnut Drizzle', 'Huckleberry Drizzle', 'Chamoy Drizzle', 'Grapefruit Drizzle', 'Peanuts', 'Toasted Coconut', 'Rainbow Sprinkles', 'Shortcake Crunch', 'Crushed Creameo', 'Chocolate Crumb', 'Streusel', 'Pistachios'], 'toppingPlacements': ['on the right Half', 'in the Top Right Corner', 'on the Top Half', 'in the Top Left Corner', 'on the Left Half']}, 'january': [{'name': 'New Year', 'shapes': ['Infinity'], 'fillings': ['Sesame Gelato', "Yum n' Ms"], 'dips': ['Flavour X'], 'toppings': ["Freezin' Flecks", 'Black Licorice Drizzle']}], 'february': [{'name': "Valentine's Day", 'shapes': ['Heart'], 'fillings': ['Red Velvet Custard', 'Candy Heart'], 'dips': ['Cherry Cheesecake'], 'toppings': ['Lollipop Crush', 'Hot Rod Drizzle']}], 'march': [{'name': 'Holi', 'shapes': ['Mandala'], 'fillings': ['Saffron Kulfi', 'Jalebi'], 'dips': ['Gulab Jamun'], 'toppings': ['Holi Sugar', 'Jackfruit Drizzle']}], 'april': [{'name': 'Easter', 'shapes': ['Bunny'], 'fillings': ['Wildberry Shake Cream', 'Jelly Bean'], 'dips': ['Lemon Chiffon'], 'toppings': ['Spring Flowers', 'Gooseberry Drizzle']}], 'may': [{'name': 'Cherry Blossom Festival', 'shapes': ['Blossom'], 'fillings': ['Pineberry Pudding', 'Azuki'], 'dips': ['Matcha'], 'toppings': ['Sugar Petals', 'Hakuto Drizzle']}], 'june': [{'name': 'Summer Luau', 'shapes': ['Pineapple'], 'fillings': ['Passionfruit Puree', 'Tropical Charms'], 'dips': ['Luau Punch'], 'toppings': ['Splashberry Derps', 'Piña Colada Drizzle']}], 'july': [{'name': 'Starlight Jubilee', 'shapes': ['Star'], 'fillings': ['Cherry Bomb Ripple', 'Gummy Star'], 'dips': ['Jubilee Jelly'], 'toppings': ['Crackle Crumbs', 'Powsicle Drizzle']}], 'august': [{'name': 'Big Top Carnival', 'shapes': ['Balloon'], 'fillings': ['Cotton Candy Yogurt', 'Candy Jack'], 'dips': ['Candy Apple'], 'toppings': ['Rock Candy', 'SuperFan Drizzle']}], 'september': [{'name': 'Pirate Bash', 'shapes': ['Anchor'], 'fillings': ['Sunken Treasure Custard', 'Black Pearl Crisp'], 'dips': ['Maelstrom Swirl'], 'toppings': ['Silver Doubloons', 'Scallywag Syrup Drizzle']}], 'october': [{'name': 'Halloween', 'shapes': ['Jack-o-Lantern'], 'fillings': ['Tiger Tail Cream', 'Dr. Bones'], 'dips': ['Ichabod Icing'], 'toppings': ['Spooky Sprinkles', 'Black Mist Drizzle']}], 'november': [{'name': 'Thanksgiving', 'shapes': ['Feather'], 'fillings': ['Buffaloberry Sxusem', 'Candy Corn'], 'dips': ['Pumpkin Spice'], 'toppings': ['Autumn Leaves', 'Nutty Butter Cup Drizzle']}], 'december': [{'name': 'Christmas', 'shapes': ['Tree'], 'fillings': ['Risalamande', 'Peppermint Bark'], 'dips': ['Eggnog Icing'], 'toppings': ['Frostcaps', 'Cherry Cordial Drizzle']}]},
    'sushiria': {'allTime': {'rices': ['Brown', 'White', 'Shiso', 'Black'], 'wraps': ['Nori', 'Momoiro Soy Paper', 'Ukoniro Soy Paper'], 'vinegars': ['Sushi Vinegar'], 'fillings': ['Avocado', 'Carrot', 'Crab Stick', 'Cream Cheese', 'Cucumber Slices', 'Salmon', 'Snow Peas', 'Tuna', 'Lobster', 'Tofu', 'Unagi', 'Jalapeños', 'Green Onions', 'Wagyu', 'Shiitake Mushrooms', 'Shrimp Tempura', 'Tamago', 'Octopus', 'Yellowtail', 'Radish Sprouts', 'Asparagus', 'Fried Calamari'], 'toppings': ['Avocado', 'Mango Slices', 'Prawn', 'Saba', 'Salmon', 'Tuna', 'Kiwi Slices', 'Wagyu', 'Yellowtail', 'Sayori', 'Tobiko', 'Bonito Flakes', 'Sesame Seeds', 'Tempura Crunch', 'Furikake', 'Duck Sauce', 'General Tso Sauce', 'Ginger Miso Sauce', 'Teriyaki Sauce', 'Wasabi Mayo', 'Yum Yum Sauce', 'Yuzu Kosho', 'Tonkatsu Sauce', 'Hibachi Sauce', 'Sriracha', 'Ponzu'], 'teas': ['Almond', 'Chai', 'Matcha', 'Mocha', 'Strawberry', 'Blueberry', 'Piña Colada', 'Tangerine', 'Taro', 'Honeydew', 'Chocolate'], 'bubbles': ['Butterscotch', 'Cucumber', 'Lychee', 'Mango', 'Tapioca Pearl', 'Watermelon', 'Cherry', 'Pawpaw', 'Sugarplum', 'Cotton Candy', 'Kiwi', 'Huckleberry']}, 'january': [{'name': 'New Year', 'wraps': ['Rainbow Soy Paper'], 'fillings': ['Rainbow Yokan', 'Eggplant'], 'toppings': ['Rainbow Yokan', 'Flavour X Sauce', 'Rainbow Peppercorn'], 'teas': ['Tutti Frutti']}], 'february': [{'name': "Valentine's Day", 'wraps': ['Akai Soy Paper'], 'fillings': ['Strawberry Slices', 'Hokkigai'], 'toppings': ['Strawberry Slices', 'Azuki Sauce', 'Pomegranate'], 'teas': ['Raspberry']}], 'march': [{'name': 'Lucky Lucky Matsuri', 'wraps': ['Lucky Soy Paper'], 'fillings': ['Datemaki', 'Kanpyo'], 'toppings': ['Datemaki', 'Kuri Kinton', 'Lucky Dust'], 'teas': ['Iyokan']}], 'april': [{'name': 'Cherry Blossom Festival', 'wraps': ['Shiroi Soy Paper'], 'fillings': ['Narutomaki', 'Kampachi'], 'toppings': ['Narutomaki', 'Sweet Sakura Sauce', 'Wakame'], 'teas': ['Hakuto']}], 'may': [{'name': 'Cinco de Mayo', 'wraps': ['Tortilla'], 'fillings': ['Chorizo', 'Chipotle Cheddar'], 'toppings': ['Chorizo', 'Nacho Cheese', 'Recado Rojo'], 'teas': ['Horchata']}], 'june': [{'name': 'Summer Luau', 'wraps': ['Mizuiro Soy Paper'], 'fillings': ['Pineapple', 'Canned Ham'], 'toppings': ['Pineapple', 'Calypso Sauce', 'Lemon Herb'], 'teas': ['Luau Punch']}], 'july': [{'name': 'Starlight BBQ', 'wraps': ['Deli Soy Paper'], 'fillings': ['Beef Brisket', 'Fried Onion Strings'], 'toppings': ['Beef Brisket', 'Lone Star Pit Sauce', 'BBQ Rub'], 'teas': ['Powsicle']}], 'august': [{'name': 'Bavariafest', 'wraps': ['Rautenflagge Soy Paper'], 'fillings': ['Brezn', 'Bratwurst'], 'toppings': ['Brezn', 'Marzen Mustard', 'Sauerkraut'], 'teas': ['Black Forest']}, {'name': 'Portallini Feast', 'wraps': ['Manicotti'], 'fillings': ['Capicola', 'Spinach Ricotta'], 'toppings': ['Capicola', 'Marinara Sauce', 'Parmesan Cheese'], 'teas': ['Spumoni']}], 'september': [{'name': 'Maple Mornings', 'wraps': ['Kiiroi Soy Paper'], 'fillings': ['Bacon', 'Hashbrown Patties'], 'toppings': ['Bacon', 'Maple Syrup', 'Cinnamon Sugar'], 'teas': ['English Breakfast']}, {'name': 'Comet Con', 'wraps': ['Meteor Blastor Soy Paper'], 'fillings': ['Starfruit', 'Lunar Jerky'], 'toppings': ['Starfruit', 'Pulsar Pesto Sauce', 'Cosmic Coconut'], 'teas': ['Galaxy Grape']}], 'october': [{'name': 'Halloween', 'wraps': ['Tarantula Soy Paper'], 'fillings': ['Uni', 'Torigai'], 'toppings': ['Uni', 'Squid Sauce', 'Ikrua'], 'teas': ["Witch's Brew"]}], 'november': [{'name': 'Thanksgiving', 'wraps': ['Chairo Soy Paper'], 'fillings': ['Sweet Potatoes', 'Roasted Turkey'], 'toppings': ['Sweet Potatoes', 'Gravy', 'Roasted Pumpkin Seeds'], 'teas': ['Pumpkin Spice']}], 'december': [{'name': 'Christmas', 'wraps': ['Elf Soy Paper'], 'fillings': ['Tai', 'Spruce Tips'], 'toppings': ['Tai', 'Cranberry Sauce', 'Merry Masago'], 'teas': ['Peppermint']}]},
    'pizzeria': {'allTime': {'crusts': ['Crispy Crust', 'Traditional Crust', 'Thick Crust', 'Garlic Knot Crust'], 'sauces': ['Classic Marinara', 'Rustic Romana', 'Creamy Garlic Sauce', 'Buffalo Sauce', 'BBQ Sauce', 'Olive Oil'], 'cheeses': ["Papa's Cheese Blend", 'Provolone Cheese', 'Smoked Cheddar Cheese', 'Grated Parmesan Cheese'], 'toppings': ['Pepperoni', 'Anchovies', 'Black Olives', 'Onions', 'Mushrooms', 'Green Peppers', 'Sausage', 'Bacon', 'Banana Peppers', 'Chicken', 'Tomatoes', 'Pepperjack Cheese', 'Spinach', 'Ground Beef', 'Ham', 'Red Peppers', 'Pineapple', 'Meatballs', 'Basil Leaves', 'Capicola', 'Jalapeños', 'Philly Steak', 'Asiago Cheese', 'Prosciutto', 'Fresh Garlic', 'Asiago Cheese', 'Pulled Pork', 'Gorgonzola', 'Cajun Shrimp', 'Pimento Olives', 'Salami', 'Artichoke Hearts', 'Smoked Salmon', 'Portobello Mushrooms', 'Broccoli'], 'bakes': ['Lightly-Done', 'Regular-Done', 'Well-Done'], 'cuts': ['4 slices', '6 slices', '8 slices', 'a grid']}, 'january': [{'name': 'New Year', 'crusts': ['Hot Dog Bites Crust'], 'sauces': ["PastariO's Sauce"], 'toppings': ['Cheez Puffs', 'Pizza Poppers']}], 'february': [{'name': "Valentine's Day", 'crusts': ['Tomato Basil Crust'], 'sauces': ['Heartbeet Arrabbiata'], 'toppings': ['Soppressata', 'Ricotta Balls']}], 'march': [{'name': 'Lucky Lucky Matsuri', 'crusts': ['Ramen Crust'], 'sauces': ['General Tso Sauce'], 'toppings': ['Kuri Kinton', 'Lotus Root']}], 'april': [{'name': 'Easter', 'crusts': ['Carrot Crust'], 'sauces': ['Wildflower Carbonara'], 'toppings': ['Carrot Sticks', 'Pickled Eggs']}], 'may': [{'name': 'Cinco de Mayo', 'crusts': ['Tostada'], 'sauces': ['Salda'], 'toppings': ['Chorizo', 'Avocado']}], 'june': [{'name': 'Summer Luau', 'crusts': ['Coconut Crust'], 'sauces': ['Calypso Sauce'], 'toppings': ['Ahi Tuna', 'Papaya']}], 'july': [{'name': 'Starlight BBQ', 'crusts': ['Cornbread Crust'], 'sauces': ['Smoky Bacon Sauce'], 'toppings': ['Onion Rings', 'Burnt Ends']}], 'august': [{'name': 'BavariaFest', 'crusts': ['Pretzel Crust'], 'sauces': ['Bierkäse Sauce'], 'toppings': ['Bratwurst', 'Schnitzel']}], 'september': [{'name': 'Maple Mornings', 'crusts': ['Buttermilk Biscuit'], 'sauces': ['Sausage Gracy'], 'toppings': ['Home Fries', 'Scrambled Eggs']}], 'october': [{'name': 'Halloween', 'crusts': ['Ecto Stuffed Crust'], 'sauces': ['Purple Pesto'], 'toppings': ['Smoked Oysters', 'Gouda Ghosts']}], 'november': [{'name': 'Thanksgiving', 'crusts': ['Pecan Crust'], 'sauces': ['Pumpkin Pomodoro'], 'toppings': ['Roasted Turkey', 'Sweet Potatoes']}], 'december': [{'name': 'Christmas', 'crusts': ['Red Pepper Crust'], 'sauces': ['Eggnog Alfredo'], 'toppings': ['Goose', 'Spruce Tips']}]}
}

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
            playerMinimumSpeeds[player] = prevPlayerMinimumSpeeds[-targetTime][player]
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
                    prevPlayerMinimumSpeeds[(-1)*i][player] = copy.deepcopy(prevPlayerMinimumSpeeds[(-1)*(i+1)][player])
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
    if quest['type'] == 'visitPapas':
        output = f'You must visit {PAPAS_WINGERIA_SPACE}papa\'s{CLEAR} {QUEST_SPACE}{quest["requirement"]}{CLEAR} times.'
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
        {"type": 'visitPapas', "requirement": (timesToVisit := random.randint(2, 5)), "reward": int(timesToVisit*4), "progress": 0, "timeLeft": int(timesToVisit*4)},
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
    global playerMinimumSpeeds
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
                                    if playerSpeeds[player] < playerMinimumSpeeds[player]:
                                        playerSpeeds[player] = playerMinimumSpeeds[player]
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
                                playerMinimumSpeeds = prevPlayerMinimumSpeeds[-1-NUM_PLAYERS+numEliminated]
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
                                    prevPlayerMinimumSpeeds.pop(-1)
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

def newline(multiline, indent):
    if multiline:
        return f'\n{" "*indent}'
    else:
        return ' '

def generatePizza(month, colouring, multiline, indent=0):
    definePapasColours(colouring)
    ingredients = ALL_PAPAS_INGREDIENTS['pizzeria']
    cost = 0
    
    holiday = random.choice(ingredients[month])
    crusts = ingredients['allTime']['crusts'] + holiday['crusts']
    sauces = ingredients['allTime']['sauces'] + holiday['sauces']
    cheeses = ingredients['allTime']['cheeses']
    toppings = ingredients['allTime']['toppings'] + holiday['toppings']
    bakes = ingredients['allTime']['bakes']
    cuts = ingredients['allTime']['cuts']
    
    output = f'{" "*indent}A {PAPAS_BLUE}{random.choice(bakes)}{PAPAS_CLEAR} {PAPAS_GREEN}Pizza{PAPAS_CLEAR} with{newline(multiline, indent+1)}{PAPAS_BROWN}{random.choice(crusts)}{PAPAS_CLEAR},{newline(multiline, indent+1)}{PAPAS_ORANGE}{random.choice(sauces)}{PAPAS_CLEAR} and{newline(multiline, indent+1)}{PAPAS_YELLOW}{random.choice(cheeses)}{PAPAS_CLEAR}'
    cost += 0.04
    numToppings = random.randint(0,4)
    if numToppings == 0:
        output = output.replace('Pizza', 'Margarita Pizza')
    else:
        output += f',{newline(multiline, indent)}topped with'
        for i in range(numToppings):
            topping = random.choice(toppings)
            toppings.remove(topping)
            qty = random.choice([4,6,8])
            cost += 0.0035*qty
            output += f'{newline(multiline, indent+1)}{PAPAS_TURQUOISE}{qty}{PAPAS_CLEAR} {PAPAS_RED}{topping}{PAPAS_CLEAR} {PAPAS_PURPLE}{random.choice(["on the left half", "on the right half", "on the top half", "on the bottom half", "all around"])}{PAPAS_CLEAR}{" and" if i == numToppings-2 else ","}'
    output += f'{newline(multiline, indent)}cut into {PAPAS_PINK}{random.choice(cuts)}{PAPAS_CLEAR}'

    output += f'{newline(multiline, indent)}{PAPAS_GRAY}[Pizzeria, {holiday["name"]}]{PAPAS_CLEAR}'
    return output, cost

def generateBurger(month, colouring, multiline, indent=0):
    definePapasColours(colouring)
    ingredients = ALL_PAPAS_INGREDIENTS['burgeria']
    cost = 0
    
    grills = ingredients['allTime']['grills']
    toppings = ingredients['allTime']['toppings']
    
    numToppings = random.randint(0,6)
    toppingsInBurger = []
    for _ in range(numToppings):
        toppingsInBurger.append(f'{PAPAS_RED}{random.choice(toppings)}{PAPAS_CLEAR}')
        cost += 0.0085
    pattyPos = random.randint(0,numToppings)
    toppingsInBurger.insert(pattyPos, f'A {PAPAS_BLUE}{random.choice(grills)}{PAPAS_CLEAR} {PAPAS_BROWN}Hamburger Patty{PAPAS_CLEAR}')
    cost += 0.045
    output = f'{" "*indent}A {PAPAS_GREEN}Burger{PAPAS_CLEAR} topped with {PAPAS_GRAY}(from bottom to top){PAPAS_CLEAR}'
    for n, topping in enumerate(toppingsInBurger):
        output += f'{newline(multiline, indent+1)}{topping}{" and" if n == numToppings-1 else "," if n != numToppings else ""}'
    
    output += f'{newline(multiline, indent)}{PAPAS_GRAY}[Burgeria]{PAPAS_CLEAR}'
    return output, cost

def generateTaco(month, colouring, multiline, indent=0):
    definePapasColours(colouring)
    ingredients = ALL_PAPAS_INGREDIENTS['tacoMia']
    cost = 0
    
    holiday = random.choice(ingredients[month])
    meats = ingredients['allTime']['meats'] + holiday['meats']
    shells = ingredients['allTime']['shells'] + holiday['shells']
    toppings = ingredients['allTime']['toppings'] + holiday['toppings']
    chips = ingredients['allTime']['chips']
    dips = ingredients['allTime']['dips']
    
    shell = random.choice(shells)
    meat = random.choice(meats)
    output = f'{" "*indent}A{"n" if meat[0] == "A" else ""} {PAPAS_BROWN}{meat}{PAPAS_CLEAR} {PAPAS_YELLOW}{shell}{PAPAS_GREEN}{"" if shell == "Walking Taco Bag" else " Taco"}{PAPAS_CLEAR} filled with {PAPAS_GRAY}(from bottom to top){PAPAS_CLEAR}'
    cost += 0.04
    numToppings = random.randint(1,5)
    for i in range(numToppings):
        output += f'{newline(multiline, indent+1)}{PAPAS_RED}{random.choice(toppings)}{PAPAS_CLEAR}{" and" if i == numToppings-2 else ","}'
        cost += 0.005
    output += f'{newline(multiline, indent)}with a side of {PAPAS_ORANGE}{random.choice(chips)}{PAPAS_CLEAR} with {PAPAS_CYAN}{random.choice(dips)}{PAPAS_CLEAR}'
    cost += 0.015
    
    output += f'{newline(multiline, indent)}{PAPAS_GRAY}[Taco Mia, {holiday["name"]}]{PAPAS_CLEAR}'
    return output, cost
    
def generateSundae(month, colouring, multiline, indent=0):
    definePapasColours(colouring)
    ingredients = ALL_PAPAS_INGREDIENTS['freezeria']
    cost = 0
    
    holiday = random.choice(ingredients[month])
    cups = ingredients['allTime']['cups']
    mixables = ingredients['allTime']['mixables'] + holiday['mixables']
    syrups = ingredients['allTime']['syrups'] + holiday['syrups']
    blends = ingredients['allTime']['blends']
    whippedCreams = ingredients['allTime']['whippedCreams'] + holiday['whippedCreams']
    sauceToppings = ingredients['allTime']['sauceToppings'] + holiday['sauceToppings']
    shakers = ingredients['allTime']['shakers'] + holiday['shakers']
    placeableToppings = ingredients['allTime']['placeableToppings'] + holiday['placeableToppings']
    
    size = random.choice(cups)
    output = f'{" "*indent}A {PAPAS_PINK}{size}{PAPAS_CLEAR} {PAPAS_BLUE}{random.choice(blends)}{PAPAS_CLEAR} {PAPAS_YELLOW}{random.choice(mixables)}{PAPAS_CLEAR} {PAPAS_GREEN}Freezer Sundae{PAPAS_CLEAR} mixed with {PAPAS_ORANGE}{random.choice(syrups)}{PAPAS_CLEAR}, topped with {PAPAS_GRAY}(from bottom to top){PAPAS_CLEAR}'
    cost += {"Small": 0.015, "Medium": 0.03, "Large": 0.045}[size]
    toppings = [f'{PAPAS_CYAN}{random.choice(whippedCreams)}{PAPAS_CLEAR}']
    slots = 4
    numPlaceables = random.randint(0,3)
    if numPlaceables != 0:
        slots -= 1
    if random.choice([True, False]):
        slots -= 1
        toppings.append(f'{PAPAS_CYAN}{random.choice(sauceToppings)} Sauce{PAPAS_CLEAR}')
    numShakers = random.randint(0,slots)
    for _ in range(numShakers):
        toppings.append(f'{PAPAS_CYAN}{random.choice(shakers)}{PAPAS_CLEAR}')
    if numPlaceables != 0:
        if numPlaceables != 3:
            oddPlaceable = random.randint(1,3)
        sides = ['on the left', 'in the middle', 'on the right']
        for i in range(3):
            if (numPlaceables == 3) or (numPlaceables == 2 and oddPlaceable != i+1) or (numPlaceables == 1 and oddPlaceable == i+1):
                placeable = random.choice(placeableToppings)
                toppings.append(f'a{"n" if placeable[0] == "A" else ""} {PAPAS_RED}{placeable}{PAPAS_CLEAR} {PAPAS_PURPLE}{sides[i]}{PAPAS_CLEAR}')
            else:
                toppings.append(f'nothing {PAPAS_PURPLE}{sides[i]}{PAPAS_CLEAR}')
    for n, topping in enumerate(toppings):
        output += f'{newline(multiline, indent+1)}{topping}{" and" if n == len(toppings)-2 else "," if n != len(toppings)-1 else ""}'
        cost += 0.0045

    output += f'{newline(multiline, indent)}{PAPAS_GRAY}[Freezeria, {holiday["name"]}]{PAPAS_CLEAR}'
    return output, cost

def generateWingPlatter(month, colouring, multiline, indent=0):
    definePapasColours(colouring)
    ingredients = ALL_PAPAS_INGREDIENTS['wingeria']
    cost = 0
    
    holiday = random.choice(ingredients[month])
    meats = ingredients['allTime']['meats']
    sauces = ingredients['allTime']['sauces'] + holiday['sauces']
    sides = ingredients['allTime']['sides'] + holiday['sides']
    dips = ingredients['allTime']['dips'] + holiday['dips']
    
    output = f'{" "*indent}A {PAPAS_GREEN}Wing Platter{PAPAS_CLEAR} with'
    slots = 7
    numMeats = random.randint(1,3)
    slots -= (2 * numMeats)
    items = []
    for _ in range(numMeats):
        qty = random.randint(1,12)
        meat = random.choice(meats)
        side = random.choice(['on the left', 'all round', 'on the right'])
        if qty == 1 and meat != 'Shrimp':
            meat = meat[:-1]
        items.append(f'{PAPAS_TURQUOISE}{qty}{PAPAS_CLEAR} {PAPAS_BROWN}{meat}{PAPAS_CLEAR} coated in {PAPAS_ORANGE}{random.choice(sauces)}{PAPAS_CLEAR} {PAPAS_PURPLE}{side}{PAPAS_CLEAR}')
        cost += 0.0035*qty
    numDips = random.randint(0,4)
    if numDips != 0:
        slots -= 1
    for _ in range(slots):
        side = random.choice(['on the left', 'all round', 'on the right'])
        qty = random.randint(2,12)
        items.append(f'{PAPAS_TURQUOISE}{qty}{PAPAS_CLEAR} {PAPAS_RED}{random.choice(sides)}{PAPAS_CLEAR} {PAPAS_PURPLE}{side}{PAPAS_CLEAR}')
        cost += 0.0005
    for _ in range(numDips):
        items.append(f'{PAPAS_CYAN}{random.choice(dips)}{PAPAS_CLEAR}')
        cost += 0.001*qty
    for n, item in enumerate(items):
        output += f'{newline(multiline, indent+1)}{item}{" and" if n == len(items)-2 else "," if n != len(items)-1 else ""}'
    
    output += f'{newline(multiline, indent)}{PAPAS_GRAY}[Wingeria, {holiday["name"]}]{PAPAS_CLEAR}'
    return output, cost

def generateHotDog(month, colouring, multiline, indent=0):
    definePapasColours(colouring)
    ingredients = ALL_PAPAS_INGREDIENTS['hotDoggeria']
    cost = 0
    
    holiday = random.choice(ingredients[month])
    sausages = ingredients['allTime']['sausages']
    buns = ingredients['allTime']['buns'] + holiday['buns']
    toppings = ingredients['allTime']['toppings'] + holiday['toppings']
    placeableToppings = ingredients['allTime']['placeableToppings']
    cups = ingredients['allTime']['cups']
    sodas = ingredients['allTime']['sodas'] + holiday['sodas']
    popcorn = ingredients['allTime']['popcorn'] + holiday['popcorn']
    
    sausage = random.choice(sausages)
    output = f'{" "*indent}A{"n" if sausage == "Italian Sausage" else ""} {PAPAS_BROWN}{sausage}{PAPAS_CLEAR} {PAPAS_GREEN}Hot Dog{PAPAS_CLEAR} in a {PAPAS_YELLOW}{random.choice(buns)}{PAPAS_CLEAR}, filled with {PAPAS_GRAY}(from bottom to top){PAPAS_CLEAR}'
    cost += 0.04
    slots = 6
    placeable = None
    toppingsToAdd = []
    if random.choice([True, False]):
        slots -= 1
        placeable = random.choice(placeableToppings)
    numToppings = random.randint(1,slots)
    for _ in range(numToppings):
        toppingsToAdd.append(f'{PAPAS_RED}{random.choice(toppings)}{PAPAS_CLEAR}')
    if placeable != None:
        toppingsToAdd.append(f'{PAPAS_RED}{placeable}{PAPAS_CLEAR}')
    for n, topping in enumerate(toppingsToAdd):
        output += f'{newline(multiline, indent+1)}{topping}{" and" if n == len(toppingsToAdd)-2 else ","}'
        cost += 0.005
    size = random.choice(cups)
    output += f'{newline(multiline, indent)}with a side of{newline(multiline, indent+1)}a {PAPAS_PINK}{random.choice(cups)}{PAPAS_CLEAR} {PAPAS_ORANGE}{random.choice(sodas)} Soda{PAPAS_CLEAR} and{newline(multiline, indent+1)}a {PAPAS_PINK}{size}{PAPAS_CLEAR} {PAPAS_CYAN}{random.choice(popcorn)}{PAPAS_CLEAR}'
    cost += {"Small": 0.01, "Medium": 0.02, "Large": 0.03}[size]
    
    output += f'{newline(multiline, indent)}{PAPAS_GRAY}[Hot Doggeria, {holiday["name"]}]{PAPAS_CLEAR}'
    return output, cost

def generateCupcake(month, colouring, multiline, indent=0):
    definePapasColours(colouring)
    ingredients = ALL_PAPAS_INGREDIENTS['cupcakeria']
    cost = 0
    
    holiday = random.choice(ingredients[month])
    cakes = ingredients['allTime']['cakes'] + holiday['cakes']
    icings = ingredients['allTime']['icings']
    drizzles = ingredients['allTime']['drizzles'] + holiday['drizzles']
    shakers = ingredients['allTime']['shakers'] + holiday['shakers']
    placeableToppings = ingredients['allTime']['placeableToppings'] + holiday['placeableToppings']
    
    output = f'{" "*indent}{PAPAS_TURQUOISE}2{PAPAS_CLEAR} {PAPAS_BROWN}{random.choice(cakes)}{PAPAS_CLEAR} {PAPAS_GREEN}Cupcakes{PAPAS_CLEAR}'
    cost += 0.04
    for i in range(2):
        if i == 0:
            output += f', one topped with {PAPAS_GRAY}(from bottom to top){PAPAS_CLEAR}{newline(multiline, indent+1)}{PAPAS_ORANGE}{random.choice(icings)} Icing{PAPAS_CLEAR}'
        else:
            output += f',{newline(multiline, indent)}and the other topped with {PAPAS_GRAY}(from bottom to top){PAPAS_CLEAR}{newline(multiline, indent+1)}{PAPAS_ORANGE}{random.choice(icings)} Icing{PAPAS_CLEAR}'
        slots = 4
        toppings = []
        if random.choice([True, False]):
            slots -= 1
            toppings.append(f'{PAPAS_CYAN}{random.choice(drizzles)} Drizzle{PAPAS_CLEAR}')
        numPlaceables = random.randint(0,2)
        if numPlaceables != 0:
            slots -= 1
        numShakers = random.randint(0,slots)
        for _ in range(numShakers):
            toppings.append(f'{PAPAS_CYAN}{random.choice(shakers)}{PAPAS_CLEAR}')
        if numPlaceables == 1:
            toppings.append(f'a {PAPAS_RED}{random.choice(placeableToppings)}{PAPAS_CLEAR}')
        if numPlaceables == 2:
            toppings.append(f'a {PAPAS_RED}{random.choice(placeableToppings)}{PAPAS_CLEAR} {PAPAS_PURPLE}on the left and right{PAPAS_CLEAR}')
            toppings.append(f'a {PAPAS_RED}{random.choice(placeableToppings)}{PAPAS_CLEAR} {PAPAS_PURPLE}in the middle{PAPAS_CLEAR}')
        if toppings != []:
            if len(toppings) == 1:
                output += ' and'
            else:
                output += ','
        for n, topping in enumerate(toppings):
            output += f'{newline(multiline, indent+1)}{topping}{" and" if n == len(toppings)-2 else "," if n != len(toppings)-1 else ""}'
            cost += 0.0035
    
    output += f'{newline(multiline, indent)}{PAPAS_GRAY}[Cupcakeria, {holiday["name"]}]{PAPAS_CLEAR}'
    return output, cost
    
def generateDonut(month, colouring, multiline, indent=0):
    definePapasColours(colouring)
    ingredients = ALL_PAPAS_INGREDIENTS['donuteria']
    cost = 0
    
    holiday = random.choice(ingredients[month])
    doughs = ingredients['allTime']['doughs']
    shapes = ingredients['allTime']['shapes'] + holiday['shapes']
    icings = ingredients['allTime']['icings'] + holiday['icings']
    fillings = ingredients['allTime']['fillings'] + holiday['fillings']
    sprinkles = ingredients['allTime']['sprinkles'] + holiday['sprinkles']
    drizzles = ingredients['allTime']['drizzles'] + holiday['drizzles']
    
    numDonuts = random.choice([1,3])
    output = f'{" "*indent}'
    for donut in range(numDonuts):
        slots = 3
        toppings = []
        if random.choice([True, False]):
            slots -= 1
            toppings.append(f'{PAPAS_RED}{random.choice(drizzles)} Drizzle{PAPAS_CLEAR}')
        numSprinkles = random.randint(0, slots)
        for _ in range(numSprinkles):
            slots -= 1
            toppings.append(f'{PAPAS_RED}{random.choice(sprinkles)}{PAPAS_CLEAR}')
        output += f'{newline(multiline, indent) if donut != 0 else ""}A {PAPAS_BROWN}{random.choice(doughs)}{PAPAS_CLEAR} {PAPAS_YELLOW}{random.choice(shapes)}-Shaped{PAPAS_CLEAR} {PAPAS_GREEN}Doughnut{PAPAS_CLEAR},{newline(multiline, indent+1)}coated with {PAPAS_ORANGE}{random.choice(icings)}{PAPAS_CLEAR}{" and" if len(toppings) == 0 else ","}{newline(multiline, indent+1)}filled with {PAPAS_CYAN}{random.choice(fillings)}{PAPAS_CLEAR}'
        cost += 0.04
        if len(toppings) != 0:
            output += f' and{newline(multiline, indent+1)}topped with {PAPAS_GRAY}(from bottom to top){PAPAS_CLEAR}'
            for n, topping in enumerate(toppings):
                output += f'{newline(multiline, indent+2)}{topping}{" and" if n == len(toppings)-2 else "," if n != len(toppings)-1 else ""}'
                cost += 0.0025
        output += f'{" and " if donut == numDonuts-2 else ", " if donut != numDonuts-1 else ""}'
    
    output += f'{newline(multiline, indent)}{PAPAS_GRAY}[Donuteria, {holiday["name"]}]{PAPAS_CLEAR}'
    return output, cost

def generateGrilledCheese(month, colouring, multiline, indent=0):
    definePapasColours(colouring)
    ingredients = ALL_PAPAS_INGREDIENTS['cheeseria']
    cost = 0
    
    holiday = random.choice(ingredients[month])
    breads = ingredients['allTime']['breads'] + holiday['breads']
    cheeses = ingredients['allTime']['cheeses'] + holiday['cheeses']
    fillings = ingredients['allTime']['fillings'] + holiday['fillings']
    timings = ingredients['allTime']['timings']
    fries = ingredients['allTime']['fries']
    fryToppings = ingredients['allTime']['fryToppings'] + holiday['fryToppings']
    
    cheese = random.choice(cheeses)
    output = f'{" "*indent}A{"n" if cheese[0] == "A" else ""} {PAPAS_YELLOW}{cheese}{PAPAS_CLEAR} {PAPAS_BLUE}{random.choice(timings)}{PAPAS_CLEAR} {PAPAS_BROWN}{random.choice(breads)}{PAPAS_CLEAR} {PAPAS_GREEN}Grilled Cheese Sandwich{PAPAS_CLEAR}'
    cost += 0.035
    toppings = []
    numToppings = random.randint(0,5)
    for _ in range(numToppings):
        toppings.append(f'{PAPAS_RED}{random.choice(fillings)}{PAPAS_CLEAR}')
    if numToppings != 0:
        output += f', filled with {PAPAS_GRAY}(from bottom to top){PAPAS_CLEAR}'
        for n, topping in enumerate(toppings):
            output += f'{newline(multiline, indent+1)}{topping}{" and" if n == len(toppings)-2 else "," if n != len(toppings)-1 else ""}'
            cost += 0.0035
    output += f',{newline(multiline, indent)}with a side of'
    sides = [f'{PAPAS_CYAN}{random.choice(fries)}{PAPAS_CLEAR}']
    numFryToppings = random.randint(0,2)
    for _ in range(numFryToppings):
        sides.append(f'{PAPAS_ORANGE}{random.choice(fryToppings)}{PAPAS_CLEAR}')
        cost += 0.0075
    for n, side in enumerate(sides):
        output += f'{newline(multiline, indent+1)}{side}{" and" if n == len(sides)-2 else "," if n != len(sides)-1 else ""}'
    
    output += f'{newline(multiline, indent)}{PAPAS_GRAY}[Cheeseria, {holiday["name"]}]{PAPAS_CLEAR}'
    return output, cost

def generatePie(month, colouring, multiline, indent=0):
    definePapasColours(colouring)
    ingredients = ALL_PAPAS_INGREDIENTS['bakeria']
    cost = 0
    
    holiday = random.choice(ingredients[month])
    crusts = ingredients['allTime']['crusts']
    fillings = ingredients['allTime']['fillings'] + holiday['fillings']
    tops = ingredients['allTime']['tops'] + holiday['tops']
    toppings = ingredients['allTime']['toppings'] + holiday['toppings']
    placeableToppings = ingredients['allTime']['placeableToppings'] + holiday['placeableToppings']
    toppingPlacements = ingredients['allTime']['toppingPlacements']
    
    output = f'{" "*indent}A {PAPAS_BROWN}{random.choice(crusts)} Crust{PAPAS_CLEAR} {PAPAS_GREEN}Baked Pie{PAPAS_CLEAR} with a {PAPAS_YELLOW}{random.choice(tops)}{PAPAS_CLEAR}, filled with {PAPAS_GRAY}(from bottom to top){PAPAS_CLEAR}'
    cost += 0.02
    usedFillings = []
    for _ in range(4):
        usedFillings.append(f'{PAPAS_ORANGE}{random.choice(fillings)}{PAPAS_CLEAR}')
    for n, filling in enumerate(usedFillings):
        output += f'{newline(multiline, indent+1)}{filling}{" and" if n == len(usedFillings)-2 else "," if n != len(usedFillings)-1 else ""}'
        cost += 0.005
    output += ' Fillings'
    numToppings = random.randint(0,3)
    usedToppings = []
    for _ in range(numToppings):
        topping = random.choice(toppings + placeableToppings)
        if topping in placeableToppings:
            usedToppings.append(f'{PAPAS_TURQUOISE}{random.randint(6,12)}{PAPAS_CLEAR} {PAPAS_RED}{topping}{PAPAS_CLEAR} on {PAPAS_PURPLE}{random.choice(toppingPlacements)}{PAPAS_CLEAR}')
        else:
            usedToppings.append(f'{PAPAS_RED}{topping}{PAPAS_CLEAR} on {PAPAS_PURPLE}{random.choice(toppingPlacements)}{PAPAS_CLEAR}')
    if numToppings != 0:
        output += f',{newline(multiline, indent)}and topped with {PAPAS_GRAY}(from bottom to top){PAPAS_CLEAR}'
        for n, topping in enumerate(usedToppings):
            output += f'{newline(multiline, indent+1)}{topping}{" and" if n == len(usedToppings)-2 else "," if n != len(usedToppings)-1 else ""}'
            cost += 0.0035
    
    output += f'{newline(multiline, indent)}{PAPAS_GRAY}[Bakeria, {holiday["name"]}]{PAPAS_CLEAR}'
    return output, cost

def generateSushi(month, colouring, multiline, indent=0):
    definePapasColours(colouring)
    ingredients = ALL_PAPAS_INGREDIENTS['sushiria']
    cost = 0
    
    holiday = random.choice(ingredients[month])
    rices = ingredients['allTime']['rices']
    wraps = ingredients['allTime']['wraps'] + holiday['wraps']
    vinegars = ingredients['allTime']['vinegars']
    fillings = ingredients['allTime']['fillings'] + holiday['fillings']
    toppings = ingredients['allTime']['toppings'] + holiday['toppings']
    teas = ingredients['allTime']['teas'] + holiday['teas']
    bubbles = ingredients['allTime']['bubbles']
    
    output = f'{" "*indent}A{f"n {PAPAS_PINK}Inverted{PAPAS_CLEAR}" if random.choice([True, False]) else ""} {PAPAS_YELLOW}{random.choice(rices)} Rice{PAPAS_CLEAR} and {PAPAS_DARK_GREEN}{random.choice(wraps)}{PAPAS_CLEAR} {PAPAS_GREEN}Sushi Roll{PAPAS_CLEAR}, with {PAPAS_BROWN}{random.choice(vinegars)}{PAPAS_CLEAR}, filled with {PAPAS_GRAY}(from bottom to top){PAPAS_CLEAR}'
    cost += 0.02
    numFillings = random.randint(1,3)
    usedFillings = []
    for _ in range(numFillings):
        usedFillings.append(f'{PAPAS_ORANGE}{random.choice(fillings)}{PAPAS_CLEAR}')
    for n, filling in enumerate(usedFillings):
        output += f'{newline(multiline, indent+1)}{filling}{" and" if n == len(usedFillings)-2 else "," if n != len(usedFillings)-1 else ""}'
        cost += 0.005
    numToppings = random.randint(0,3)
    usedToppings = []
    for _ in range(numToppings):
        usedToppings.append(f'{PAPAS_RED}{random.choice(toppings)}{PAPAS_CLEAR}')
    if numToppings != 0:
        output += f',{newline(multiline, indent)}and topped with {PAPAS_GRAY}(from bottom to top){PAPAS_CLEAR}'
        for n, topping in enumerate(usedToppings):
            output += f'{newline(multiline, indent+1)}{topping}{" and" if n == len(usedToppings)-2 else "," if n != len(usedToppings)-1 else ""}'
            cost += 0.0035
    output += f',{newline(multiline, indent)}with a side of {PAPAS_ORANGE_YELLOW}{random.choice(teas)} Tea{PAPAS_CLEAR} with {PAPAS_CYAN}{random.choice(bubbles)} Bubbles{PAPAS_CLEAR}'
    cost += 0.01
    
    output += f'{newline(multiline, indent)}{PAPAS_GRAY}[Sushiria, {holiday["name"]}]{PAPAS_CLEAR}'
    return output, cost

def generateIceCream(month, colouring, multiline, indent=0):
    definePapasColours(colouring)
    ingredients = ALL_PAPAS_INGREDIENTS['scooperia']
    cost = 0
    
    holiday = random.choice(ingredients[month])
    doughs = ingredients['allTime']['doughs']
    mixables = ingredients['allTime']['mixables'] + holiday['mixables']
    iceCreams = ingredients['allTime']['iceCreams'] + holiday['iceCreams']
    toppings = ingredients['allTime']['toppings'] + holiday['toppings']
    placeableToppings = ingredients['allTime']['placeableToppings'] + holiday['placeableToppings']
    
    numCookies = random.randint(1,3)
    output = f'{" "*indent}'
    for cookie in range(numCookies):
        dough = random.choice(doughs)
        output += f'A{"n" if dough[0] == "O" else ""} {PAPAS_BROWN}{dough}{PAPAS_CLEAR} {PAPAS_GREEN}Cookie{PAPAS_CLEAR}{newline(multiline, indent+1)}mixed with {PAPAS_ORANGE}{random.choice(mixables)}{PAPAS_CLEAR},{newline(multiline, indent+1)}with a scoop of {PAPAS_YELLOW}{random.choice(iceCreams)} Ice Cream{PAPAS_CLEAR} on top'
        output += f'{f" and{newline(multiline, indent)}" if cookie == numCookies-2 else f",{newline(multiline, indent)}" if cookie != numCookies-1 else ""}'
        cost += 0.02
    numToppings = random.randint(0,4)
    if numToppings != 0:
        output += f',{newline(multiline, indent)}{"all " if numCookies != 1 else ""}topped with {PAPAS_GRAY}(from bottom to top){PAPAS_CLEAR}'
        usedToppings = []
        for _ in range(numToppings):
            usedToppings.append(f'{PAPAS_RED}{random.choice(toppings)}{PAPAS_CLEAR}')
        for n, topping in enumerate(usedToppings):
            output += f'{newline(multiline, indent+1)}{topping}{" and" if n == len(usedToppings)-2 else "," if n != len(usedToppings)-1 else ""}'
            cost += 0.0035
    hasPlaceables = random.choice([True, False])
    if hasPlaceables:
        cost += 0.01*numCookies
        if numCookies == 1:
            output += f',{newline(multiline, indent)}and a {PAPAS_CYAN}{random.choice(placeableToppings)}{PAPAS_CLEAR} on top'
        elif numCookies == 2:
            output += f',{newline(multiline, indent)}the {PAPAS_PURPLE}left{PAPAS_CLEAR} ice cream with a {PAPAS_CYAN}{random.choice(placeableToppings)}{PAPAS_CLEAR} on top,{newline(multiline, indent)}and the {PAPAS_PURPLE}right{PAPAS_CLEAR} ice cream with a {PAPAS_CYAN}{random.choice(placeableToppings)}{PAPAS_CLEAR} on top'
        elif numCookies == 3:
            output += f',{newline(multiline, indent)}the {PAPAS_PURPLE}left and right{PAPAS_CLEAR} ice creams with a {PAPAS_CYAN}{random.choice(placeableToppings)}{PAPAS_CLEAR} on top,{newline(multiline, indent)}and the {PAPAS_PURPLE}middle{PAPAS_CLEAR} ice cream with a {PAPAS_CYAN}{random.choice(placeableToppings)}{PAPAS_CLEAR} on top'
    
    output += f'{newline(multiline, indent)}{PAPAS_GRAY}[Scooperia, {holiday["name"]}]{PAPAS_CLEAR}'
    return output, cost

def generatePancakes(month, colouring, multiline, indent=0):
    definePapasColours(colouring)
    ingredients = ALL_PAPAS_INGREDIENTS['pancakeria']
    cost = 0
    
    holiday = random.choice(ingredients[month])
    bases = ingredients['allTime']['bases']
    mixables = ingredients['allTime']['mixables']
    toppings = ingredients['allTime']['toppings'] + holiday['toppings']
    placeableToppings = ingredients['allTime']['placeableToppings'] + holiday['placeableToppings']
    drinkSizes = ingredients['allTime']['drinkSizes']
    drinks = ingredients['allTime']['drinks'] + holiday['drinks']
    drinkExtras = ingredients['allTime']['drinkExtras']
    
    output = f'{" "*indent}A {PAPAS_GREEN}stack of pancakes{PAPAS_CLEAR} containing {PAPAS_GRAY}(from bottom to top){PAPAS_CLEAR}'
    cost += 0.01
    stack = [f'A {PAPAS_YELLOW}{random.choice(bases)}{PAPAS_CLEAR} with {PAPAS_ORANGE}{random.choice(mixables)}{PAPAS_CLEAR}']
    additionalItems = random.randint(0,6)
    for _ in range(additionalItems):
        if random.choice([True, False]):
            stack.append(f'A {PAPAS_YELLOW}{random.choice(bases)}{PAPAS_CLEAR} with {PAPAS_ORANGE}{random.choice(mixables)}{PAPAS_CLEAR}')
            cost += 0.01
        else:
            chosenTopping = random.choice(toppings + placeableToppings)
            if chosenTopping in placeableToppings:
                qty = random.randint(1,6)
                stack.append(f'{PAPAS_TURQUOISE}{qty}{PAPAS_CLEAR} piece{"s" if qty != 1 else ""} of {PAPAS_RED}{chosenTopping}{PAPAS_CLEAR}')
            else:
                stack.append(f'{PAPAS_RED}{chosenTopping}{PAPAS_CLEAR}')
            cost += 0.0035
    for n, item in enumerate(stack):
        output += f'{newline(multiline, indent+1)}{item}{" and" if n == len(stack)-2 else "," if n != len(stack)-1 else ""}'
    size = random.choice(drinkSizes)
    output += f',{newline(multiline, indent)}with a side of a {PAPAS_PINK}{size}{PAPAS_CLEAR} {PAPAS_CYAN}{random.choice(drinks)}{PAPAS_CLEAR} with {PAPAS_BROWN}{random.choice(drinkExtras)}{PAPAS_CLEAR}'
    cost += {"Small": 0.005, "Medium": 0.01, "Large": 0.015}[size]
    
    output += f'{newline(multiline, indent)}{PAPAS_GRAY}[Pancakeria, {holiday["name"]}]{PAPAS_CLEAR}'
    return output, cost

def generatePasta(month, colouring, multiline, indent=0):
    definePapasColours(colouring)
    ingredients = ALL_PAPAS_INGREDIENTS['pastaria']
    cost = 0
    
    holiday = random.choice(ingredients[month])
    pastas = ingredients['allTime']['pastas'] + holiday['pastas']
    cooks = ingredients['allTime']['cooks']
    sauces = ingredients['allTime']['sauces'] + holiday['sauces']
    shakers = ingredients['allTime']['shakers'] + holiday['shakers']
    placeableToppings = ingredients['allTime']['placeableToppings'] + holiday['placeableToppings']
    breads = ingredients['allTime']['breads']
    
    output = f'{" "*indent}A bowl of {PAPAS_BLUE}{random.choice(cooks)}{PAPAS_CLEAR} {PAPAS_BROWN}{random.choice(pastas)}{PAPAS_CLEAR} {PAPAS_GREEN}Pasta{PAPAS_CLEAR}, topped with {PAPAS_GRAY}(from bottom to top){PAPAS_CLEAR}'
    cost += 0.025
    toppings = [f'{PAPAS_ORANGE}{random.choice(sauces)} Sauce{PAPAS_CLEAR}']
    numToppings = random.randint(0,4)
    for _ in range(numToppings):
        chosenTopping = random.choice(shakers + placeableToppings)
        if chosenTopping in placeableToppings:
            qty = random.randint(2,8)
            toppings.append(f'{PAPAS_TURQUOISE}{qty}{PAPAS_CLEAR} {PAPAS_RED}{chosenTopping}{PAPAS_CLEAR}')
        else:
            toppings.append(f'{PAPAS_CYAN}{chosenTopping}{PAPAS_CLEAR}')
    for n, topping in enumerate(toppings):
        output += f'{newline(multiline, indent+1)}{topping}{" and" if n == len(toppings)-2 else "," if n != len(toppings)-1 else ""}'
        cost += 0.0035
    output += f',{newline(multiline, indent)}with a side of {PAPAS_YELLOW}{random.choice(breads)}{PAPAS_CLEAR}'
    cost += 0.01
    
    output += f'{newline(multiline, indent)}{PAPAS_GRAY}[Pastaria, {holiday["name"]}]{PAPAS_CLEAR}'
    return output, cost

def generateLatte(month, colouring, multiline, indent=0):
    definePapasColours(colouring)
    ingredients = ALL_PAPAS_INGREDIENTS['mocharia']
    cost = 0
    
    holiday = random.choice(ingredients[month])
    milks = ingredients['allTime']['milks'] + holiday['milks']
    temperatures = ingredients['allTime']['temperatures']
    espressos = ingredients['allTime']['espressos']
    cups = ingredients['allTime']['cups']
    syrups = ingredients['allTime']['syrups'] + holiday['syrups']
    ices = ingredients['allTime']['ices']
    powders = ingredients['allTime']['powders'] + holiday['powders']
    creams = ingredients['allTime']['creams'] + holiday['creams']
    toppings = ingredients['allTime']['toppings'] + holiday['toppings']
    canoliShells = ingredients['allTime']['canoliShells'] + holiday['canoliShells']
    
    size = random.choice(cups)
    if size == 'Small':
        totalVolume = 4
    elif size == 'Medium':
        totalVolume = 5
    elif size == 'Large':
        totalVolume = 6
    volumeLeft = totalVolume
    output = f'{" "*indent}A {PAPAS_PINK}{size}{PAPAS_CLEAR} {PAPAS_GREEN}Latte{PAPAS_CLEAR} containing {PAPAS_GRAY}(from bottom to top){PAPAS_CLEAR}'
    latte = []
    somethingExtra = random.choice(['none', 'top', 'bottom'])
    if somethingExtra == 'none':
        extraItem = 'none'
    if somethingExtra == 'bottom':
        extraItem = f'{PAPAS_RED}{random.choice(syrups)} Syrup{PAPAS_CLEAR}'
        latte.append(extraItem)
        cost += 0.0035
    if somethingExtra == 'top':
        if random.choice([True, False]):
            extraItem = f'{PAPAS_CYAN}{random.choice(ices)}{PAPAS_CLEAR}'
            if extraItem == 'Ice Cubes' or extraItem == f'{PAPAS_CYAN}Ice Cubes{PAPAS_CLEAR}':
                volumeLeft -= 1
        else:
            extraItem = f'{PAPAS_RED}{random.choice(syrups)} Syrup{PAPAS_CLEAR}'
            cost += 0.0035
    mainOrder = ['milk', 'espresso']
    random.shuffle(mainOrder)
    for n, section in enumerate(mainOrder):
        if n == 0:
            volume = random.randint(1,volumeLeft-1)
        else:
            volume = volumeLeft
        volumeLeft -= volume
        if section == 'milk':
            latte.append(f'{PAPAS_TURQUOISE}{volume}/{totalVolume}{PAPAS_CLEAR} {PAPAS_ORANGE_YELLOW}{random.choice(temperatures)}{PAPAS_CLEAR} {PAPAS_ORANGE}{random.choice(milks)} Milk{PAPAS_CLEAR}')
            cost += 0.005*volume
        if section == 'espresso':
            latte.append(f'{PAPAS_TURQUOISE}{volume}/{totalVolume}{PAPAS_CLEAR} {PAPAS_BROWN}{random.choice(espressos)} Espresso{PAPAS_CLEAR}')
            cost += 0.0025*volume
        additionalItems = random.randint(0,2)
        for _ in range(additionalItems):
            item = random.choice(syrups + powders)
            latte.append(f'{PAPAS_RED}{item} {"Syrup" if item in syrups else "Powder"}{PAPAS_CLEAR}')
            cost += 0.0035
    if somethingExtra == 'top':
        if extraItem == 'Ice Cubes' or extraItem == f'{PAPAS_CYAN}Ice Cubes{PAPAS_CLEAR}':
            latte.append(f'{PAPAS_TURQUOISE}1/{totalVolume}{PAPAS_CLEAR} {extraItem}')
        else:
            latte.append(extraItem)
    for n, item in enumerate(latte):
        output += f'{newline(multiline, indent+1)}{item}{" and" if n == len(latte)-2 else "," if n != len(latte)-1 else ""}'
    usedToppings = []
    if random.choice([True, False]):
        usedToppings.append(f'{PAPAS_YELLOW}{random.choice(creams)} Cream{PAPAS_CLEAR}')
    if random.choice([True, False]):
        usedToppings.append(f'{PAPAS_RED}{random.choice(syrups)} Syrup{PAPAS_CLEAR}')
    if random.choice([True, False]):
        usedToppings.append(f'{PAPAS_DARK_GREEN}{random.choice(toppings)}{PAPAS_CLEAR}')
    if len(usedToppings) != 0:
        output += f',{newline(multiline, indent)}topped with {PAPAS_GRAY}(from bottom to top){PAPAS_CLEAR}'
        for n, topping in enumerate(usedToppings):
            output += f'{newline(multiline, indent+1)}{topping}{" and" if n == len(usedToppings)-2 else "," if n != len(usedToppings)-1 else ""}'
            cost += 0.0035
    output += f',{newline(multiline, indent)}with a side of a {PAPAS_MAROON}{random.choice(canoliShells)} Canoli{PAPAS_CLEAR},{newline(multiline, indent+1)}filled with {PAPAS_YELLOW}{random.choice(creams)} Cream{PAPAS_CLEAR} and{newline(multiline, indent+1)}{PAPAS_DARK_GREEN}{random.choice(toppings)}{PAPAS_CLEAR}'
    cost += 0.01
    
    output += f'{newline(multiline, indent)}{PAPAS_GRAY}[Mocharia, {holiday["name"]}]{PAPAS_CLEAR}'
    return output, cost

def generateChickenSandwich(month, colouring, multiline, indent=0):
    definePapasColours(colouring)
    ingredients = ALL_PAPAS_INGREDIENTS['cluckeria']
    cost = 0
    
    holiday = random.choice(ingredients[month])
    meats = ingredients['allTime']['meats']
    breadings = ingredients['allTime']['breadings']
    buns = ingredients['allTime']['buns'] + holiday['buns']
    toppings = ingredients['allTime']['toppings'] + holiday['toppings']
    slushSizes = ingredients['allTime']['slushSizes']
    slushFlavours = ingredients['allTime']['slushFlavours'] + holiday['slushFlavours']
    
    output = f'{" "*indent}A {PAPAS_GREEN}Chicken Sandwich{PAPAS_CLEAR} in a {PAPAS_YELLOW}{random.choice(buns)} Bun{PAPAS_CLEAR}, containing {PAPAS_GRAY}(from bottom to top){PAPAS_CLEAR}'
    cost += 0.04
    numToppings = random.randint(0,5)
    stack = []
    for _ in range(numToppings):
        stack.append(f'{PAPAS_RED}{random.choice(toppings)}{PAPAS_CLEAR}')
    pattyPos = random.randint(0,numToppings)
    stack.insert(pattyPos, f'A {PAPAS_BROWN}{random.choice(meats)} Patty{PAPAS_CLEAR} with {PAPAS_ORANGE}{random.choice(breadings)}{PAPAS_CLEAR}')
    for n, topping in enumerate(stack):
        output += f'{newline(multiline, indent+1)}{topping}{" and" if n == numToppings-1 else "," if n != numToppings else ""}'
        cost += 0.0035
    slushFlavour1 = random.choice(slushFlavours)
    slushFlavour2 = random.choice(slushFlavours)
    size = random.choice(slushSizes)
    if slushFlavour1 == slushFlavour2:
        output += f',{newline(multiline, indent)}with a side of a {PAPAS_PINK}{random.choice(slushSizes)}{PAPAS_CLEAR} {PAPAS_CYAN}{slushFlavour1}{PAPAS_CLEAR} Slushie'
    else:
        output += f',{newline(multiline, indent)}with a side of a {PAPAS_PINK}{random.choice(slushSizes)}{PAPAS_CLEAR} {PAPAS_CYAN}{slushFlavour1}{PAPAS_CLEAR} and {PAPAS_CYAN}{slushFlavour2}{PAPAS_CLEAR} Slushie'
    cost += {"Small": 0.005, "Medium": 0.01, "Large": 0.015}[size]
    
    output += f'{newline(multiline, indent)}{PAPAS_GRAY}[Cluckeria, {holiday["name"]}]{PAPAS_CLEAR}'
    return output, cost

def generateIceLolly(month, colouring, multiline, indent=0):
    definePapasColours(colouring)
    ingredients = ALL_PAPAS_INGREDIENTS['paleteria']
    cost = 0
    
    holiday = random.choice(ingredients[month])
    shapes = ingredients['allTime']['shapes'] + holiday['shapes']
    fillings = ingredients['allTime']['fillings'] + holiday['fillings']
    dips = ingredients['allTime']['dips'] + holiday['dips']
    toppings = ingredients['allTime']['toppings'] + holiday['toppings']
    toppingPlacements = ingredients['allTime']['toppingPlacements']
    
    shape = random.choice(shapes)
    output = f'{" "*indent}A{"n" if shape[0] in ["A","I"] else ""} {PAPAS_YELLOW}{shape}-Shaped{PAPAS_CLEAR} {PAPAS_GREEN}Ice Lolly{PAPAS_CLEAR}, flavoured with {PAPAS_GRAY}(in 3 horizontal stripes, from bottom to top){PAPAS_CLEAR}'
    cost += 0.02
    usedFillings = []
    for _ in range(3):
        usedFillings.append(f'{PAPAS_ORANGE}{random.choice(fillings)}{PAPAS_CLEAR}')
    for n, filling in enumerate(usedFillings):
        output += f'{newline(multiline, indent+1)}{filling}{" and" if n == len(usedFillings)-2 else "," if n != len(usedFillings)-1 else ""}'
    output += f',{newline(multiline, indent)}coated in {PAPAS_CYAN}{random.choice(dips)} Dip{PAPAS_CLEAR} {PAPAS_PURPLE}{random.choice(toppingPlacements)}{PAPAS_CLEAR}'
    numToppings = random.randint(0,3)
    usedToppings = []
    for _ in range(numToppings):
        usedToppings.append(f'{PAPAS_RED}{random.choice(toppings)}{PAPAS_CLEAR} {PAPAS_PURPLE}{random.choice(toppingPlacements)}{PAPAS_CLEAR}')
        cost += 0.0035
    if numToppings != 0:
        output += f',{newline(multiline, indent)}and topped with {PAPAS_GRAY}(from bottom to top){PAPAS_CLEAR}'
        for n, topping in enumerate(usedToppings):
            output += f'{newline(multiline, indent+1)}{topping}{" and" if n == len(usedToppings)-2 else "," if n != len(usedToppings)-1 else ""}'
    
    output += f'{newline(multiline, indent)}{PAPAS_GRAY}[Paleteria, {holiday["name"]}]{PAPAS_CLEAR}'
    return output, cost

def addToFoodInventory(numIngredients):
    month = datetime.datetime.today().strftime('%B').lower()
    for _ in range(numIngredients):
        ingredientType = random.choice(['meats', 'meats', 'sauces', 'sides', 'dips'])
        if ingredientType != 'meats':
            ingredient = random.choice(ALL_PAPAS_INGREDIENTS['wingeria']['allTime'][ingredientType] + random.choice(ALL_PAPAS_INGREDIENTS['wingeria'][month])[ingredientType])
        else:
            ingredient = random.choice(ALL_PAPAS_INGREDIENTS['wingeria']['allTime'][ingredientType])
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
    currentOrder.append(f'{GYM_SPACE}{qty}{CLEAR} {PAPAS_WINGERIA_SPACE}{meat}{CLEAR} coated in {ORANGE}{sauce}{CLEAR}')
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
            currentOrder.append(f'{GYM_SPACE}{qty}{CLEAR} {PAPAS_WINGERIA_SPACE}{meat}{CLEAR} coated in {ORANGE}{sauce}{CLEAR}')
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
            currentOrder.append(f'{GYM_SPACE}{qty}{CLEAR} {RED}{side}{CLEAR}')
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
    updateQuests('visitPapas', 1)
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
    games = ['Pizzeria', 'Burgeria', 'Taco Mia', 'Wingeria', 'Hot Doggeria', 'Cheeseria', 'Sushiria', 'Pastaria', 'Cluckeria', 'Freezeria', 'Cupcakeria', 'Donuteria', 'Bakeria', 'Scooperia', 'Pancakeria', 'Mocharia', 'Paleteria']
    game = random.choice(games)
    month = datetime.datetime.today().strftime('%B').lower()
    if game == 'Pizzeria':
        order, cost = generatePizza(month, colouring=True, multiline=True, indent=indent+1)
    elif game == 'Burgeria':
        order, cost = generateBurger(month, colouring=True, multiline=True, indent=indent+1)
    elif game == 'Taco Mia':
        order, cost = generateTaco(month, colouring=True, multiline=True, indent=indent+1)
    elif game == 'Freezeria':
        order, cost = generateSundae(month, colouring=True, multiline=True, indent=indent+1)
    elif game == 'Wingeria':
        order, cost = generateWingPlatter(month, colouring=True, multiline=True, indent=indent+1)
    elif game == 'Hot Doggeria':
        order, cost = generateHotDog(month, colouring=True, multiline=True, indent=indent+1)
    elif game == 'Cupcakeria':
        order, cost = generateCupcake(month, colouring=True, multiline=True, indent=indent+1)
    elif game == 'Donuteria':
        order, cost = generateDonut(month, colouring=True, multiline=True, indent=indent+1)
    elif game == 'Cheeseria':
        order, cost = generateGrilledCheese(month, colouring=True, multiline=True, indent=indent+1)
    elif game == 'Bakeria':
        order, cost = generatePie(month, colouring=True, multiline=True, indent=indent+1)
    elif game == 'Sushiria':
        order, cost = generateSushi(month, colouring=True, multiline=True, indent=indent+1)
    elif game == 'Scooperia':
        order, cost = generateIceCream(month, colouring=True, multiline=True, indent=indent+1)
    elif game == 'Pancakeria':
        order, cost = generatePancakes(month, colouring=True, multiline=True, indent=indent+1)
    elif game == 'Pastaria':
        order, cost = generatePasta(month, colouring=True, multiline=True, indent=indent+1)
    elif game == 'Mocharia':
        order, cost = generateLatte(month, colouring=True, multiline=True, indent=indent+1)
    elif game == 'Cluckeria':
        order, cost = generateChickenSandwich(month, colouring=True, multiline=True, indent=indent+1)
    elif game == 'Paleteria':
        order, cost = generateIceLolly(month, colouring=True, multiline=True, indent=indent+1)
    print(f'{" "*indent}You ordered\n{order}.')
    playerSpeeds[currentPlayer] -= cost
    playerSpeeds[currentPlayer] = round(playerSpeeds[currentPlayer], 4)
    if playerSpeeds[currentPlayer] < playerMinimumSpeeds[currentPlayer]:
        playerSpeeds[currentPlayer] = playerMinimumSpeeds[currentPlayer]
    print(f'{" "*indent}You {RED}gained some weight{CLEAR}, so your speed is now {GYM_SPACE}{playerSpeeds[currentPlayer]}{CLEAR}.')
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
                if playerSpeeds[player] < playerMinimumSpeeds[player]:
                    playerSpeeds[player] = playerMinimumSpeeds[player]
            indent += 1
            print(f'{" "*indent}{RED}Player {player}{CLEAR} now has {GYM_SPACE}{playerSpeeds[player]} speed{CLEAR}.')
            indent -= 1
    if playerGolds[currentPlayer] > 0:
        time.sleep(0.5)
        print(f'{" "*indent}Would you like to {YELLOW}invest{CLEAR} in {PAPAS_WINGERIA_SPACE}papa\'s{CLEAR}? (you have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR})')
        indent += 1
        print(f'{" "*indent}Once you invest {YELLOW}{WINGERIA_PROGRESS_REQUIRED} gold{CLEAR} you will recieve {YELLOW}1 gold{CLEAR} each time someone visits {PAPAS_WINGERIA_SPACE}papa\'s{CLEAR}!')
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
            indent += 1
            playerMinimumSpeeds[currentPlayer] = playerSpeeds[currentPlayer]
            playerSpeeds[currentPlayer] *= 2
            playerSpeeds[currentPlayer] = round(playerSpeeds[currentPlayer], 4)
            print(f'{" "*indent}Your speed is now {GYM_SPACE}{playerSpeeds[currentPlayer]}{CLEAR}.')
            playerGolds[currentPlayer] *= 2
            print(f'{" "*indent}You now have {YELLOW}{playerGolds[currentPlayer]} gold{CLEAR}.')
            indent -= 1
            print(f'{" "*indent}Due to your {GYM_SPACE}incredible new physique{CLEAR}, your minimum speed has increased!')
            indent += 1
            print(f'{" "*indent}You can now no longer go below {GREEN}{playerMinimumSpeeds[currentPlayer]}{CLEAR} {GYM_SPACE}speed{CLEAR}.')
            indent -= 1
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
                    print(f'{" "*indent}If you guess {GREEN}correctly{CLEAR}, you will be able to either {RED}murder{CLEAR} {YELLOW}that player{CLEAR}, or use {YELLOW}that player\'s{CLEAR} special ability.')
                    print(f'{" "*indent}If you guess {RED}incorrectly{CLEAR}, you will be {RED}murdered{CLEAR}.')
                    indent += 1
                    print(f'{" "*indent}For any {RED}murder{CLEAR}, it will look the same as if the {RED}Murderer{CLEAR} had {RED}murdered{CLEAR} that player.')
                    print(f'{" "*indent}They/you will be {RED}eliminated from the game{CLEAR} for {ORANGE}{VOTING_FREQUENCY//4} rounds{CLEAR}')
                    indent -= 2
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
                    playerSpecialAbilities[newStaller] = random.choice(STALLER_ABILITIES)
                    playerSpecialAbilities[oldStaller] = random.choice(FINDER_ABILITIES)
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
                        playerSpecialAbilities[newJester] = random.choice(JESTER_ABILITIES)
                        playerSpecialAbilities[oldJester] = random.choice(FINDER_ABILITIES)
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
            time.sleep(1)
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
            print(f'{" "*indent}That is {GREEN}correct{CLEAR}!')
            indent += 1
            if playerSpecialAbilities[chosenPlayer] == 'None' or (playerSpecialAbilities[chosenPlayer] == 'Medic' and 'Toxicologist' in playerSpecialAbilities):
                print(f'{" "*indent}{RED}Unfortunately,{CLEAR} this player does not have anything to do right now...')
                print(f'{" "*indent}Would you like to {RED}murder{CLEAR} this player instead?')
                indent += 1
                print(f'{" "*indent}0: No')
                print(f'{" "*indent}1: Yes')
                indent -= 1
                choice = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', 1))
                if choice == 1:
                    murderedPlayers.append(chosenPlayer)
            else:
                print(f'{" "*indent}Would you like to use the ability of the {grammatiseRole(playerSpecialAbilities[chosenPlayer])} or {RED}murder{CLEAR} this player?')
                indent += 1
                print(f'{" "*indent}0: Use {grammatiseRole(playerSpecialAbilities[chosenPlayer])} special ability')
                print(f'{" "*indent}1: {RED}Murder{CLEAR} player {chosenPlayer}')
                indent -= 1
                choice = int(askOptions(f'{" "*indent}{TURQUOISE}Enter your Choice:{CLEAR} ', 1))
                if choice == 0:
                    evalSpecialAbility(playerSpecialAbilities[chosenPlayer])
                if choice == 1:
                    murderedPlayers.append(chosenPlayer)
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
            if playerSpeeds[currentPlayer] < playerMinimumSpeeds[currentPlayer]:
                playerSpeeds[currentPlayer] = playerMinimumSpeeds[currentPlayer]
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
        return f'{"a " if article else ""}{PAPAS_WINGERIA_SPACE}{f"Papa{apostrophe}s" if title else f"papa{apostrophe}s"}{CLEAR} space{"!" if punctuation else ""}'
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
        "playerMinimumSpeeds": playerMinimumSpeeds,
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
        "prevPlayerMinimumSpeeds": prevPlayerMinimumSpeeds,
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
        "ingredient bundle": f'A collection of {ORANGE}{itemPrices["ingredient bundle"]*3} ingredients{CLEAR} to make a {PAPAS_WINGERIA_SPACE}wing platter{CLEAR} at {PAPAS_WINGERIA_SPACE}papa\'s{CLEAR}.',
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
playerMinimumSpeeds = [None]
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
    playerMinimumSpeeds.append(MINIMUM_SPEED)
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
prevPlayerMinimumSpeeds = [copy.deepcopy(playerMinimumSpeeds)]
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
                playerSpecialAbilities[player] = random.choice(STALLER_ABILITIES)
            elif role == 'Jester':
                playerSpecialAbilities[player] = random.choice(JESTER_ABILITIES)
            elif role == 'Finder':
                playerSpecialAbilities[player] = random.choice(FINDER_ABILITIES)
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
                playerMinimumSpeeds = data["playerMinimumSpeeds"]
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
                prevPlayerMinimumSpeeds = data["prevPlayerMinimumSpeeds"]
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
        prevPlayerMinimumSpeeds.append(copy.deepcopy(playerMinimumSpeeds))
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