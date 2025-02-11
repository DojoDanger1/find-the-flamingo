# Find the Flamingo
A game about spatial awareness, logic, memory, lying, and absolute nonsense.

# Changelog

## v2.5.9
### Bug Fixes
- Ensured that finders play flamingo games at `STALLER_WIN` only if `ROLES_ENABLED`

## v2.5.8 - 11/02/2025
### Bug Fixes
- Save file no longer becomes hundreds of megabytes due to `prevPlayerSmasheds` and `prevPlayerHipnosisRounds`

## v2.5.7 - 10/02/2025
### Features
- Added option `FLAMINGO-GAME` to enable/disable playing the flamingo game to win
### Bug Fixes
- Ensured lovers can't generate after the final vote

## v2.5.6 - 09/02/2025
### Features
- Now allowing for settings to be altered from the command line
### Adjustments
- Adjusted assertions to allow for games of size 2 for high dimensions
### Bug Fixes
- Ensured that when executioner/shifter shifts, executioner isn't targeting themselves
- Ensured that `LYING_GAME_DIFFICULTY` is at least 1

## v2.5.5 - 06/02/2025
### Adjustments
- Added coimplies and conimplies gates to logic game

## v2.5.4 - 05/02/2025
### Adjustments
- Changed number of questions on board quiz from between 5 and 10 to between 3 and 5
- Changed number of questions on lying game from between 4 and 9 to between 4 and 7
- Changed `LYING_GAME_DIFFICULTY` from 4 to 5
- In the logic game, the colour of `True`s and `False`s is now random
- Added implies and nimplies gates to logic game
- Answers may be swapped in logic game

## v2.5.3 - 05/02/2025
### Features
- Now giving the option to explain roles and special abilities or not

## v2.5.2 - 04/02/2025
### Bug Fixes
- Fixed Crashes on Python 3.11.0

## v2.5.1 - 29/01/2025
### Bug Fixes
- Fix time machine not decreasing the round number

## v2.5.0 - 28/01/2025
### Features
- Map
  - A data store that stores the route to the flamingo space
  - Players can add to their map with a new option on the information space
- Cartographer Special Ability (Finder)
  - Adds to their map

## v2.4.0 - 26/01/2025
### Features
- Jester Variant: Executioner
  - Instead of trying to get voted out, the executioner has a target. If the target is voted out, the executioner will play a flamingo game.
  - If the executioner is voted out, or fails the flamingo game, the role of executioner will be removed, and a finder will be picked to become either a jester or executioner
- Hypnotist Special Ability (Jester/Executioner)
  - Chooses a player to hypnotise. On a chosen round, that player will appear to land on the flamingo space, but at the end it will be revealed that they have hallucinated it.
- Smasher Special Ability (Staller)
  - Chooses a player to violently smash. Smashed players will break their legs.
  - Players with broken legs have a 50% chance of being able to move at any opportunity.
  - The legs will heal at the next vote
  - If there is a medic, they can choose a player to shield from being smashed
- Option for players to skip the vote
  - Final vote cannot be skipped
- Players who are eliminated for any reason will loose half for their belongings
### Adjustments
- Changed `CHANCE_OF_LOVERS` from 0.35 to 0.3
- Changed `CHANCE_OF_3_WAY` from 0.15 to 0.1
### Bug Fixes
- Fixed Toxicologist timing being off

## v2.3.1 - 20/11/2024
### Adjustments
- Print new roles when new lovers are added

## v2.3.0 - 19/11/2024
### Features
- Shifter Special Ability (Jester)
  - Allows the player to choose a player to swap roles and special abilities with
- Lovers modifier
  - 35% chance that there exists lovers. If one player is voted out/murdered/poisoned, so will the other
  - 15% chance that the lovers are in the throuple, If one player is voted out/murdered/poisoned, so will the other 2
### Adjustments
- Seer is now a Finder Special Ability

## v2.2.5 - 19/09/2024
### Bug Fixes
- Fix crash on loading wingeria quest

## v2.2.4 - 17/09/2024
### Features
- Papa's Wingeria renamed to Papa's
  - Papa's sells everything from all of the papa's games

## v2.2.3 - 08/09/2024
### Adjustments
- Guesser can choose to murder correctly guessed player or use the special ability

## v2.2.2 - 23/08/2024
### Features
- Secret Feature that mewing increases minimum speed to previous speed
### Bug Fixes
- Grammatical Errors

## v2.2.1 - 22/08/2024
### Features
- Green Potion Buff
  - Completing the Bicep Curls workout at the gym will increase the duration of the green potion
- Fat People squish people on spaces they move to
- Can't move onto a space if there is not enough room (due to collective fat)
### Adjustments
- Decreased chance of finder with no special ability
### Bug Fixes
- Swapper can now choose themselves to swap

## v2.2.0 - 20/08/2024
### Features
- Special Abilities
  - All players are given a special ability on top of their role.
  - Each special ability allows the player to do something in secret during the vote
  - Staller Abilities:
    - Murderer: Choose a player to murder, they are eliminated for 7 rounds
    - Toxicologist: Choose a player to poison, they will feel symptoms for the middle 2/3 of the voting period, and are eliminated for the last 1/6 of the voting period
  - Jester Abilities:
    - Guesser: Choose a player to guess the special ability of, if the guess is correct the guesser can use that special ability. If the guess is incorrect, the guesser will be murdered.
    - Seer: Choose a player to see the role and special ability of
  - Finder Abilities:
    - Medic: If the current staller is a Murderer, then the medic can shield a player from murder. If the current staller is a toxicologist, the medic can heal poisoned players by occupying the same space as them on the map
    - Cleaner: Removes half of the quantum entanglements
    - Mewer: Increases the chance of a successful mew by 1%
    - Swapper: Swap the votes that any 2 players recieve
    - None: This finder has no special ability
### Adjustments
- Changed `STALLER_WIN` from 250 to 150
- Changed `VOTING_FREQUENCY` from 50 to 30

## v2.1.1 - 08/07/2024
### Adjustments
- Improved map rendering for higher dimensions
- Jester can now find the flamingo space after the final vote
### Bug Fixes
- Role can't change upon timewarp

## v2.1.0 - 06/07/2024
### Features
- Added support for a general number of dimensions (instead of just 2)

## v2.0.2 - 01/07/2024
### Features
- Added option for stallers and jesters to be able to land on the flamingo space
### Bug Fixes
- Grammatical Errors

## v2.0.1 - 30/06/2024
### Adjustments
- Added extra sentence to finder instructions to not give away information based on reading time

## v2.0.0 - 28/06/2024
### Features
- Roles
  - Each player is now given a role. This functionality can be enabled for games with at least 4 players
  - Finder: Same goal as before
  - Staller: Remain undetected, and reach round 250. At this time, you will play a flamingo game every 5 rounds until you win, or one of the finders finds the flamingo space before you
  - Jester: Act Suspicious. The jester will play a flamingo game if they are voted out at one of the votes.
- Voting
  - Every 50 rounds, a vote will be held, to attempt to vote out the staller.
  - The player who is voted out (if they are not the jester) will be eliminated from the game for 12 rounds
  - If the voted player is the staller, the role of staller will be passed onto another player
  - If the voted player is the jester, they will play a flamingo game to win the game
  - If they fail the game, the role of jester will be passed onto another player
- Final Voting
  - On round 250, the final vote will be held.
  - If the staller is voted out, they will be eliminated permanently, and the finders will take turns playing the flamingo game.
  - If they fail, they will be eliminated permanently. The jester will be picked last to play the flamingo game
  - If the staller is not voted out, they will play a flamingo game every 5 rounds until they win, or a finder finds the flamingo space.
### Adjustments
- Changed the default number of players from 3 to 5
### Bug Fixes
- Fixed some crashing in generating the map
### Removals
- Removed the emergency quick save
- Removed `traceback` as a dependancy

## v1.6.1 - 15/06/2024
### Bug Fixes
- Grammatical on Wingeria Platter

## v1.6.0 - 10/06/2024
### Features
- Black hole is generated on entanglement space after 25 entanglements are generated.
  - Warning messages are shown every 5 entanglements
  - Players encapsulated by black holes are eliminated from the game
  - Black hole has a 1/3 chance of expanding on any given turn, after it has been generated
- Now supports 1 player games
### Adjustments
- Players must confirm if they want to stay on the current space

## v1.5.3 - 09/06/2024
### Adjustments
- Changed price of quantum notification from 5 gold for 1 to 3 gold for 2

## v1.5.2 - 07/05/2024
### Bug Fixes
- Reworked Wingeria Quest to work with new rules

## v1.5.1 - 04/06/2024
### Bug Fixes
- Ensure game ends if player has more moves after they win

## v1.5.0 - 03/06/2024
### Features
- Flamingo Game: Lying Game
  - The player is given a scenario in which $n$ people make statements such as "Person $k$ is [lying/telling the truth]"
  - Players must determine how many of the above people are lying
- Flamingo Fame: Mixed Game
  - Players must answer 1 question from each of the other flamingo games, in a random order.
  - At the end, they will play the number game to a smaller count

## v1.4.0 - 29/05/2024
### Features
- Replaced Information Item with Information Space
  - When landing on the information space, players will recieve a random piece of information about the board, and in particular the location of the flamingo space and how to get to it.
  - Information space can also show information about quantum entanglements

## v1.3.0 - 29/05/2024
### Features
- Feeding Other Players
  - Players can build their own wing platters and feed them to other players
  - Players can buy ingredient bundles from the shop, and use them on the papa's wingeria space
  - Players can construct platters with $n+7$ slots, where $n$ is the number of investments they have made
  - Chicken must have sauce and that together takes up 2 slots
  - Sides each take up 1 slot
  - Platters can have up to 4 dips, which collectively take up 1 slot
  - Speed is lost in the same manner as when landing on the wingeria
- Speed lost due to wingeria now includes sides and dips
### Adjustments
- Nerfed fat injection to remove 0.1 speed instead of 0.15
- Wing platters at papa's wingeria now reflect the real month as opposed to a random one
### Bug Fixes
- Consistent Punctiation on Inputs
- Indentation errors
- Grammatical Errors

## v1.2.1 - 25/05/2024
### Features
- Gold is now printed at the start of a player's turn
### Bug Fixes
- Ensure `MINIMUM_SPEED` setting is non negative

## v1.2.0 - 24/05/2024
### Features
- Entangled Spaces
  - If a player is on a quantum-entangled space at the beginning of their turn, there is a 50% chance they are teleported to the other one
- Entanglement Space
  - Landing on this space creates a quantum entanglement between 2 spaces
  - Players can pay 5 gold to be notified when they next get quantum-teleported

## v1.1.1 - 24/05/2024
### Features
- Quests now have an associated time limit
  - If the quest is not completed within the time limit, it is deleted
### Bug Fixes
- Update shop quest only if the user has bought something

## v1.1.0 - 23/05/2024
### Features
- Gym Exercise: Mewing
  - 1% chance to double speed and gold

## v1.0.6 - 21/05/2024
### Adjustments
- Can no longer use the same item in the same instance
### Bug Fixes
- F3 menu was 0-indexed where the rest of the game wasn't
- Number game not doing letters correctly

## v1.0.5 - 18/05/2024
### Adjustments
- Made Number Game Hader
  - Can no longer get $n=2$
  - Extra rule: digits cannot sum to $n$
- Can no longer buy portable shops from portable shops
### Bug Fixes
- Incorrect message in number game faliure
- Removed redundant line in shop code

## v1.0.4 - 16/05/2024
### Features
- Added quest to shoot people with 1 bullet
### Adjustments
- Nerfed fat injection to remove 0.15 speed instead of 0.2
### Bug Fixes
- Fix item metadata in giving away item
- Fix date game not working in December

## v1.0.3 - 15/05/2024
### Bug Fixes
- Indentation error in wingeria
- Floating point error in fat injection

## v1.0.2 - 12/05/2024
### Adjustments
- Ensured that there is no backtracking in board quiz
### Bug Fixes
- 90 has 2 syllables not 3
- Indexed time machines to avoid travelling back in time to a point where you had the time machine


## v1.0.1 - 11/05/2024
### Features
- Indented all print messages, to show hierarchical structure and processes
### Adjustments
- Changed `MINIMUM_SPEED` from 0 to 0.25
### Bug Fixes
- Can no longer move due to speed in shadow realm
- Reworked Clearing Lines

## v1.0.0 - 09/05/2024
### Features
- The Endgame
  - When players land on the flamingo space, they must now play a "flamingo game" to win the game
  - If the player looses, they are sent back to the home space
- Flamingo Game: Number Game
  - Player must count to a certain number, excluding numbers that are divisible by $n$, contain $n$, have $n$ digits, have $n$ letters in English and have $n$ syllables in English
  - If they say ain incorrect number, or skip over a number, they loose
- Flamingo Game: Board Quiz
  - Player is asked a number of questions about the board
  - On question $n$, they are asked what space they will land on if they move $n$ specific moves from the home space.
- Flamingo Game: Logic Game
  - Player is asked to simplify 5 logic expressions
- Flamingo Game: Date Quiz
  - Player is asked to determine the day of the week of 5 dates.
  - The first will be in the current month, the second will be in the current year, the third will be in the current decade, the fourth will be in the current century, and the fifth will be in the current century, or the 2 centuries either side (so 1800 to 2299 at the time of writing).
### Bug Fixes
- Printing error message in emergency save
- Grammatical Errors

## v0.7.2 - 07/05/2024
### Features
- Automatic saving after each turn
### Adjustments
- Added emergency quick save
- Changed gym progress required from 3 to 2

## v0.7.1 - 05/05/2024
### Features
- Padlock Item
  - Can be placed on a certain path, players must enter a 4 digit code to get through
### Adjustments
- Added `assert` statements to ensure rules on settings

## v0.7.0 - 30/04/2024
### Features
- Quests
  - Players are rewarded for completing certain tasks around the map
  - Rewards are proportional to the requirement
- Quest Space
  - Gives the player a random quest

### Bug Fixes
- Ensured speed can't be negative on fat injection
- Grammatical Errors

## v0.6.0 - 29/04/2024
### Features
- Gym Workouts
  - Players have the choice between the workouts when they land on the gym space
  - Squats: Previous Gym Functionality
  - Bicep Curls: Once this workout has been completed 3 times, they will steal one more gold from knife and gun uses
- Papa's Wingeria Investments
  - After eating chicken, players can invest in the wingeria
  - For each 4 gold they invest, they will steal 1 gold each time another player lands on papa's wingeria
- Dumbell Item
  - Increases the player's speed by 0.1
- Fat Injection Item
  - Decreases another player's speed by 0.2 if they share a space with the item's user
- Freeze Ray Item
  - Chosen player cannot move on their next turn
### Adjustments
- Re-organised shop, items are now in categories
- Print Timing on Wingeira slightly adjusted
### Bug Fixes
- Ensured there are no spaces such that there is a limited number of spaces that you can get to, which does not include all spaces ("purgatories")
- Ensured speed can't be negative
- Time machine crash, not rewinding player frozens

## v0.5.0 - 28/04/2024
### Features
- Speed
  - Speed is a measure of the average number of moves a player can make in their turn
  - A player is guaranteed $\text{floor}\left(\text{speed}\right)$ moves, and may get $\text{ceil}\left(\text{speed}\right)$ moves with a random chance of $\text{speed}-\text{floor}\left(\text{speed}\right)$
- Gym Space
  - Players can work out for a random number from 1 to 24 of hours
  - Their speed will increase by $0.0035\times\text{Workout Hours}$
- Papa's Wingeria Space
  - Players order chicken wings and get fat
  - Their speed will increase by $0.0035$ for each meat item they order
### Adjustments
- Renamed `STARTING_HAND` setting to `STARTING_INVENTORY`
### Bug Fixes
- Incorrect Indentation on Item Use
- Grammatical Errors

## v0.4.4 - 26/04/2024
### Features
- Multiply gold by -1 in bad wheel
### Bug fixes
- Generalised Time Machine Length
- Allowed the player to randomly teleport themselves

## v0.4.3 - 25/04/2024
### Features
- Can now gamble items instead of gold in blackjack
### Bug Fixes
- Fixed trap not being deleted after use
- Fixed give away item in bad wheel

## v0.4.2 - 24/04/2024
### Features
- Item rewards now scale with the price of an item
### Adjustments
- Added `SHOP_PURCHACE_LIMIT` setting

## v0.4.1 - 24/04/2024
### Features
- Gun Item
  - Shoot in a particular direction to steal gold
- Good wheel option for gambling
  - Players can choose whether to gamble themselves or make another player gamble half of their gold
### Adjustments
- Knife item now steals more gold
### Bug Fixes
- Goblins that flee to the shadow realm now die
- Fixed bug on creating a small map

## v0.4.0 - 23/04/2024
### Features
- Games can now be saved to and loaded from `.json` files
  - When prompting to continue to the next player, a game can be saved by writing `SAVE`, or loaded by writing `LOAD`

## v0.3.1 - 21/04/2024
### Features
- Information on Good Wheel Spin
- F3 Menu Item
  - Tells the player their current coordinates
- Super Inflation
  - 5% chance for the price of an item to double instead of +1
### Adjustments
- Goblins now get lost in the shadow realm and die
- Compass now also tells the player about their current space
### Bug Fixes
- Replace instances of `copy.copy()` with `copy.deepcopy()`
- Navigation items in the shadow realm no longer work
- Added debug print statements to boad generation
- Ensured there are no isolated spaces.

## v0.3.0 - 20/04/2024
### Features
- Information Item
  - Tells the player a row in which the flamingo space **isn't**
- Portable Shop Item
  - Allows the player to visit the shop from anywhere in the map
- Flamingo Item
  - Moves towards the flamingo space each round
  - Player is notified when they land on a space with their flamingo
  - Flamingo is despawned when it reaches the flamingo space
### Adjustments
- Increased chance of escaping from the shadow realm
- Ensure it is possible to reach the flamingo space from the home space
- Added `BIAS` setting for map generation
### Bug Fixes
- Increased Length of clear line in good & shadow wheel spins
- Users can now use more than 1 item per turn

## v0.2.3 - 12/04/2024
### Features
- Visit Shop Good Wheel Option
### Adjustments
- Added one-way labelling to the maps

## v0.2.2 - 11/04/2024
### Features
- Green Potion Item
  - Tells the player how many moves away from the flamingo space they are
- Random Change Bad Wheel Option
  - Makes a random change to the board
### Adjustments
- Added `STARTING_HAND` setting
### Bug Fixes
- Increased Length of clear line in bad wheel spin
- Time Machine now reverts the board

## v0.2.1 - 11/04/2024
### Features
- Safeword Item
  - Returns the player to the Home space
### Adjustments
- Changed prices of items in the shop
- Changed `PERCENTAGE_PATHS` default setting from `0.8` to `0.5`
### Bug Fixes
- Reworked generating the board

## v0.2.0 - 10/04/2024
### Features
- Timewarp Space
  - Player can choose a player to get sent back in time
  - Chosen player will be sent back in time by 3 rounds
- Time Machine Item
  - Rewinds the entire game by 1 round
### Adjustments
- Added `BLACKJACK_DEALER_CAUTION` setting
### Bug Fixes
- Added gold amount to "give away all gold" bad wheel spin
- Added missing bad wheel functionality, to swap places with another player
- Now clearing screen at the start of the game
- Grammatical Errors

## v0.1.0 - 10/04/2024
### Features
- Gambling Space
  - Players can play blackjack on the gambling space
  - They can gamble any amount of gold
### Bug Fixes
- Grammatical Errors

## v0.0.1 - 10/04/2024
### Adjustments
- Reduce the number of highways

## v0.0.0 - 09/04/2024
### Features
Base game, as shown in Magic the Noah's Video
- Spaces
  - Home - The space the players start on. They recieve 1 gold each time they land here again
  - Flamingo - The space the players are aiming to get to. Landing on this space wins the game
  - Empty - Nothing happens
  - Good - Spin the good wheel, to get rewards
  - Bad - Spin the bad wheel, to get punishments
  - Shop - Buy up to 3 items with gold
  - Shadow Realm - Players are stuck here until they escape. Each round, they must spin the shadow wheel, which can have good or bad effects. One option is to return home.
  - Teleport - Choose a player to teleport to a random space
- Items
  - Compass - Tells the player information about all adjacent spaces and who is on them.
  - Swap - Swap the positions of any 2 players
  - Trap - Place it on the current space, any player who lands on it pays you 3 gold
  - Gold Potion - Places 2 gold on the current space
  - Knife - Stab a player on the same space as you, you will steal 3 of their gold
  - Red Potion - Tells you which direction to go to get closer to the flamingo space
  - Goblin - Roams around the map and steals 1 gold from players it hits
  - Wand - Make a player spin the bad wheel