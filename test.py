import random
import time

def getColour(r, g, b, background=False):
  return f'\033[{48 if background else 38};2;{r};{g};{b}m'

White = '\033[0m'
Red = getColour(255, 43, 89)
Green = getColour(0, 255, 0)
Orange = getColour(255, 123, 8)
Yellow = getColour(255, 210, 8)
Cyan = getColour(0, 217, 255)
Turquoise = getColour(0, 255, 183)

TARGET = 31

def game():
    money = 50
    
    def getCardColour(card):
        if 'Hearts' in card or 'Diamonds' in card:
            return f'{getColour(219, 72, 72)}{card}\033[0m'
        else:
            return f'{getColour(148, 148, 148)}{card}\033[0m'

    def getHandValueColour(value):
        if value < TARGET-6:
            return f' {Green}{value}\033[0m'
        elif value < TARGET-1:
            return f' {Yellow}{value}\033[0m'
        elif value < TARGET+1:
            return f' {Orange}{value}\033[0m'
        else:
            return f' {Red}{value}\033[0m'
    
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
            print(f'{Cyan}The Dealer\'s hand is:{White}')
            for card in dealerhand:
                print(getCardColour(card))
            print(f'Dealer hand value is{getHandValueColour(dealerhandValue)}\n')
        if person == 'player':
            print(f'{Cyan}Your hand is:{White}')
            for card in hand:
                print(getCardColour(card))
            print(f'Your hand value is{getHandValueColour(handValue)}\n')

    yesTypes = ['yes', 'y']
    noTypes = ['no', 'n']
    suits = ['Hearts', 'Diamonds', 'Spades', 'Clubs']
    cards = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']

    bet = None
    while bet == None:
        bet = int(input(f'{White}\nWhat would you like to bet? (put 0 if you don\'t want to bet)\n'+Turquoise+'> '))
        if bet > money:
            print(f'{Red}You don\'t have that much money!{White}')
            bet = None

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
    if handValue == TARGET+1:
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
    if dealerhandValue == TARGET+1:
        dealerhandValue -= 10
        dealeracesInHand -= 1

    #let dealer simulate game
    dealerdoneDrawing = False
    while dealerdoneDrawing == False:
        if dealerhandValue <= TARGET-5:
            dealercardAmount += 1
            globals()[f'dealercard{dealercardAmount}'] = f'{random.choice(cards)} of {random.choice(suits)}'
            if 'Ace' in globals()[f'dealercard{dealercardAmount}']:
                dealeracesInHand += 1
            globals()[f'dealercard{dealercardAmount}Value'] = findValue(globals()[f'dealercard{dealercardAmount}'])
            dealerhand.append(globals()[f'dealercard{dealercardAmount}'])
            dealerhandValue += globals()[f'dealercard{dealercardAmount}Value']
            if dealerhandValue > TARGET-5:
                if dealerhandValue > TARGET:
                    if dealeracesInHand != 0:
                        dealerhandValue -= 10
                        dealeracesInHand -= 1
                    else:
                        dealerdoneDrawing = True
                        dealerBusted = True
                elif dealerhandValue <= TARGET:
                    dealerdoneDrawing = True
                    dealerBusted = False
        else:
            dealerdoneDrawing = True
            dealerBusted = False
    dealerShownCard = random.choice(dealerhand)
    print(f'{Orange}The dealer has {dealercardAmount} cards{White}')
    print(f'One of the dealer\'s cards is: {getCardColour(dealerShownCard)}{White}\n')
    
    doneDrawing = False
    while doneDrawing == False:
        sayHand()
        draw = ''
        if handValue == TARGET:
            doneDrawing = True
            youBusted = False
            print(f'{Green}You scored Blackjack!{White}')
            input('Press Enter to see the results')
        else:
            while draw not in yesTypes and draw not in noTypes:
                draw = input(f'Would you like to draw?\n{Turquoise}> ').lower()
                if draw in yesTypes:
                    #draw
                    cardAmount += 1
                    globals()[f'card{cardAmount}'] = f'{random.choice(cards)} of {random.choice(suits)}'
                    if 'Ace' in globals()[f'card{cardAmount}']:
                        acesInHand += 1
                    globals()[f'card{cardAmount}Value'] = findValue(globals()[f'card{cardAmount}'])
                    hand.append(globals()[f'card{cardAmount}'])
                    handValue += globals()[f'card{cardAmount}Value']
                    print('')
                    if handValue > TARGET:
                        if acesInHand != 0:
                            handValue -= 10
                            acesInHand -= 1
                        else:
                            doneDrawing = True
                            youBusted = True
                            sayHand()
                            print(f'{Orange}You busted!{White}')
                            input('Press Enter to see the results')
                    elif handValue == TARGET:
                        doneDrawing = True
                        youBusted = False
                        sayHand()
                        print(f'{Green}You scored Blackjack!{White}')
                        input('Press Enter to see the results')
                elif draw in noTypes:
                    doneDrawing = True
                    if handValue <= TARGET:
                        youBusted = False
                else:
                    print(f'{Red}That is not an option! Pleae try again{White}')
    
    print(f'{White}\n---RESULTS---\n')
    sayHand()
    sayHand('dealer')
    time.sleep(0.25)

    if youBusted == True and dealerBusted == True:
        print(f'{Yellow}Both of you busted, so no one wins!{White}')
        winner = 'one'
    elif youBusted == True and dealerBusted == False:
        print(f'{Red}You busted! That means the dealer wins!{White}')
        money -= bet
        winner = 'dealer'
    elif youBusted == False and dealerBusted == True:
        print(f'{Green}The dealer busted! That means you win!{White}')
        money += bet
        winner = 'player'
    elif youBusted == False and dealerBusted == False:
        print('No one busted, so the person with the highest number wins...')
        if handValue > dealerhandValue:
            print(f'{Green}You win!{White}')
            money += bet
            winner = 'player'
        else:
            print(f'{Red}Dealer wins!{White}')
            money -= bet
            winner = 'dealer'
    
    return winner

game()