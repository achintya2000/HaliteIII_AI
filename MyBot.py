#!/usr/bin/env python3
# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants
from hlt.positionals import Position
from hlt.positionals import Direction

import random
import logging
import numpy
import math

# This game object contains the initial game state.
game = hlt.Game()
# Respond with your name.
game.ready("MyPythonBot")
shipsToReturn = []
threshold = 1000
# vary this threshold with regard to halite available on map
shiptargets = {}
nextmap = []
shipsOrdered = []
shipsToStay = []
shipsToCrash = []
nw = []
ne = []
sw = []
se = []

shipcounter = 0
shipspawned = False
turnamount = {64: 501, 56: 476, 48: 451, 40: 426, 32: 401}
shipthreshold = {64: 40, 56: 36, 48: 32, 40: 28, 32: 24}
remainingTurns = turnamount[game.game_map.width]
shipsmade = 0

halitethreshold = 100


for i in range(0, game.game_map.height):

    nextmap.append([])

    for j in range(0, game.game_map.width):

        nextmap[i].append(-1)


# id for my ship

# -1 if empty

# -2 for anyone else's ship

def updateNextMap():

    for i in range(0, game.game_map.height):

        for j in range(0, game.game_map.width):

            if game.game_map[Position(i, j)].is_occupied:

                if game.game_map[Position(i, j)].ship.owner == game.me.id:

                    nextmap[i][j] = game.game_map[Position(i, j)].ship.id

                else:

                    nextmap[i][j] = -2

            else:

                nextmap[i][j] = -1


def check(sect):

    if sect == 0:

        scanx0 = me.shipyard.position.x - int(game_map.width/2)

        scanx = me.shipyard.position.x

        scany0 = me.shipyard.position.y - int(game_map.height/2)

        scany = me.shipyard.position.y

    elif sect == 1:

        scanx0 = me.shipyard.position.x - int(game_map.width/2)

        scanx = me.shipyard.position.x

        scany0 = me.shipyard.position.y

        scany = me.shipyard.position.y + int(game_map.height/2)

    elif sect == 2:

        scanx0 = me.shipyard.position.x

        scanx = me.shipyard.position.x + int(game_map.width/2)

        scany0 = me.shipyard.position.y - int(game_map.height/2)

        scany = me.shipyard.position.y

    elif sect == 3:

        scanx0 = me.shipyard.position.x

        scanx = me.shipyard.position.x + int(game_map.width/2)

        scany0 = me.shipyard.position.y

        scany = me.shipyard.position.y + int(game_map.height/2)

    for i in range(scanx0, scanx):

        for j in range(scany0, scany):

            if game_map[game_map.normalize(Position(i, j))].halite_amount >= halitethreshold:

                return True

    return False

# takes in a ship and a location, returns way to get to location through local minima if returning, maxima if leaving


def getBack(ship, drop):

    possPos = []

    returning = 1

    mustGetBack = False

    same = False

    for dir in game_map.get_unsafe_moves(ship.position, drop):

        possPos.append(ship.position.directional_offset(dir))

    if ship.position.x == drop.x and ship.position.y == drop.y:

        possPos.append(ship.position)

        same = True

    if ship.id not in shipsToReturn:

        returning = -1

    if returning == 1 and remainingTurns - game_map.calculate_distance(ship.position, me.shipyard.position) <= 10:

        mustGetBack = True

    min = possPos[0]

    for pos in possPos:

        if (game_map[pos].halite_amount < returning * game_map[min].halite_amount):

            min = pos

    moves = game_map.get_unsafe_moves(ship.position, min)

    min = game_map.normalize(min)

    if not same:

        # Move if my ship isnt in the way

        if nextmap[min.x][min.y] < 0:

                command_queue.append(ship.move(Direction.convert(moves[0])))

                shipsOrdered.append(ship.id)

                nextmap[min.x][min.y] = ship.id

                nextmap[ship.position.x][ship.position.y] = -1

        elif mustGetBack and min.x == drop.x and min.y == drop.y:

                command_queue.append(ship.move(Direction.convert(moves[0])))

                shipsOrdered.append(ship.id)

                nextmap[min.x][min.y] = ship.id

                nextmap[ship.position.x][ship.position.y] = -1

        # When you don't want to swap since it would make the other ship further from goal

        elif ship.id not in shipsToReturn and game_map.calculate_distance(ship.position, shiptargets[nextmap[min.x][min.y]]) > game_map.calculate_distance(min, shiptargets[nextmap[min.x][min.y]]):

                if game_map[ship.position].halite_amount < halitethreshold and ship.id not in shipsToCrash:

                    # something I put in for testing purposes, get rid of it if it's bad

                    # Don't just sit there if there's someone ahead and the cell is almost empty, move to nearest highest halite location

                    max = game_map[ship.position].halite_amount

                    maxpos = ship.position

                    for pos in ship.position.get_surrounding_cardinals():

                        pos = game_map.normalize(pos)

                        if nextmap[pos.x][pos.y] < 0 and game_map[pos].halite_amount > max:

                            max = game_map[pos].halite_amount

                            maxpos = pos

                    if max > game_map[ship.position].halite_amount and max >= halitethreshold:

                        command_queue.append(
                            ship.move(game_map.get_unsafe_moves(ship.position, maxpos)[0]))

                        shipsOrdered.append(ship.id)

                        nextmap[maxpos.x][maxpos.y] = ship.id

                        nextmap[ship.position.x][ship.position.y] = -1

                elif ship.position != me.shipyard.position:

                    command_queue.append(ship.stay_still())

                    shipsOrdered.append(ship.id)

                    shipsToStay.append(ship.id)

        # Swap positions of ships if first one is higher in priority

        elif nextmap[min.x][min.y] >= 0 and nextmap[min.x][min.y] not in shipsToStay and nextmap[min.x][min.y] not in shipsToReturn and nextmap[min.x][min.y] not in shipsOrdered:

                command_queue.append(ship.move(Direction.convert(moves[0])))

                command_queue.append(game.game_map[min].ship.move(
                    Direction.invert(moves[0])))

                shipsOrdered.append(ship.id)

                shipsOrdered.append(game.game_map[min].ship.id)

                nextmap[ship.position.x][ship.position.y] = game.game_map[min].ship.id

                nextmap[min.x][min.y] = ship.id

    else:

        # if the destination is reached and it has less than 10 halite, go to the nearest highest halite square

        if game_map[drop].halite_amount < 10:

            max = game_map[drop].halite_amount

            maxpos = ship.position

            for pos in ship.position.get_surrounding_cardinals():

                pos = game_map.normalize(pos)

                if nextmap[pos.x][pos.y] < 0 and game_map[pos].halite_amount > game_map[ship.position].halite_amount and game_map[pos].halite_amount > max:

                    max = game_map[pos].halite_amount

                    maxpos = pos

            if max > game_map[drop].halite_amount:

                command_queue.append(ship.move(game_map.get_unsafe_moves(ship.position, maxpos)[0]))

                shipsOrdered.append(ship.id)

                nextmap[maxpos.x][maxpos.y] = ship.id

                nextmap[ship.position.x][ship.position.y] = -1

        else:

            command_queue.append(ship.stay_still())

            shipsOrdered.append(ship.id)

            shipsToStay.append(ship.id)

       

def locateClosestDense(ship, blacklist):

    haliteamount = []

    position = []

    max = [0]

    scanx0 = 0

    scanx = 0

    scany = 0

    scany0 = 0

    if ship.id in nw:

        scanx0 = me.shipyard.position.x - int(game_map.width/2)

        scanx = me.shipyard.position.x

        scany0 = me.shipyard.position.y - int(game_map.height/2)

        scany = me.shipyard.position.y

    elif ship.id in sw:

        scanx0 = me.shipyard.position.x - int(game_map.width/2)

        scanx = me.shipyard.position.x

        scany0 = me.shipyard.position.y

        scany = me.shipyard.position.y + int(game_map.height/2)

    elif ship.id in ne:

        scanx0 = me.shipyard.position.x

        scanx = me.shipyard.position.x + int(game_map.width/2)

        scany0 = me.shipyard.position.y - int(game_map.height/2)

        scany = me.shipyard.position.y

    elif ship.id in se:

        scanx0 = me.shipyard.position.x

        scanx = me.shipyard.position.x + int(game_map.width/2)

        scany0 = me.shipyard.position.y

        scany = me.shipyard.position.y + int(game_map.height/2)

    else:

        scanx0 = ship.position.x - 20

        scanx = ship.position.x + 20

        scany0 = ship.position.y - 20

        scany = ship.position.y + 20

    if ship.id in shiptargets:

        blacklist.remove(shiptargets[ship.id])

    # If another ship has that location as a target, don't go there

    for i in range(scanx0, scanx):

        for j in range (scany0, scany):

            temp = game_map.normalize(Position(i, j))

            if temp not in blacklist:

                areasum = 0

                for h in temp.get_surrounding_cardinals():

                    areasum += game_map[h].halite_amount

                # vary this the denominator with ML

                haliteamount.append( (areasum + 4 * game_map[temp].halite_amount) / (10 + game_map.calculate_distance(ship.position, temp)))

                position.append(temp)

    for i in range(0, len(haliteamount)):

        if haliteamount[max[0]] < haliteamount[i]:

            max = [i]

        elif haliteamount[max[0]] == haliteamount[i]:

            max.append(i)

    positions = []

    temp = []

    for i in range(0, len(max)):

        temp.append(game_map.calculate_distance(ship.position, position[max[i]]))

        positions.append(position[max[i]])

    return positions[temp.index(min(temp))]

 

# Order the ship order based on distance

def sortShips(ships):

    temp = []

    for ship in ships:

        temp.append(ship)

    result = []

    for ship in temp:

        if ship.id in shipsToReturn:

            temp.remove(ship)

            result.append(ship)

    result = sorted(result, key = distance)

    if game_map[me.shipyard.position].is_occupied and game_map[me.shipyard.position].ship.owner == me.id:

        result.insert(0, game_map[me.shipyard.position].ship)

    for ship in sorted(temp, key = distance):

        result.append(ship)

    return result

   

def distance(ship):

    return game_map.calculate_distance(ship.position, shiptargets[ship.id])           

 

def rival():

    result = -1

    haliteamount = -1

    for player in game.players:

        if player != game.me.id and game.players[player].halite_amount > haliteamount:

            result = player

            haliteamount = game.players[player].halite_amount

    return result

   

def updateShipTargets():

    toremove = []

    for id in shiptargets:

        if id not in list(map(lambda x: x.id, me.get_ships())):

            toremove.append(id)

    for id in toremove:

        shiptargets.pop(id)

while True:

    # Get the latest game state.

    game.update_frame()

    # You extract player metadata and the updated map metadata here for convenience.

    remainingTurns-=1

    me = game.me

    game_map = game.game_map

    updateNextMap()

    updateShipTargets()

    # A command queue holds all the commands you will run this turn.

    command_queue = []

    shipsOrdered = []

    shipsToStay = []

    # Assign ships to their sectors

    if shipspawned and game_map[me.shipyard.position].is_occupied and game.turn_number < turnamount[game.game_map.width]/2:

        if shipcounter == 0 and check(0):

            nw.append(game_map[me.shipyard.position].ship.id)

        elif shipcounter == 2 and check(2):

            ne.append(game_map[me.shipyard.position].ship.id)

        elif shipcounter == 3 and check(3):

            se.append(game_map[me.shipyard.position].ship.id)

        elif shipcounter == 1 and check(1):

            sw.append(game_map[me.shipyard.position].ship.id)

        shipcounter+=1

        shipcounter = shipcounter % 5

    # Get rid of sectors if they don't have halite

    reducehalthresh = 0

    if len(nw)!=0 and not check(0):

        nw = []

        reducehalthresh += 1

    if len(sw)!=0 and not check(1):

        sw = []

        reducehalthresh += 1

    if len(ne)!=0 and not check(2):

        ne = []

        reducehalthresh += 1

    if len(se)!=0 and not check(3):

        se = []

        reducehalthresh += 1

    # When all sectors don't have halite reduce the staying threshold by 25

    if reducehalthresh == 4:

        halitethreshold -= 25

    for ship in me.get_ships():

        # Set destinations for all ships

        if ship.halite_amount >= threshold and ship.id not in shipsToReturn:

            shipsToReturn.append(ship.id)

        if ship.halite_amount < 100 and ship.id in shipsToReturn:

            shipsToReturn.remove(ship.id)

        # Get back if you don't have time

        if ship.id not in shipsToReturn and remainingTurns - game_map.calculate_distance(ship.position, me.shipyard.position) <= 10 and remainingTurns - game_map.calculate_distance(ship.position, me.shipyard.position) > 0 and ship.halite_amount > 50:

            shipsToReturn.append(ship.id)

        # If the ship doesn't have a lot of halite, crash it into adjacent squares from the leading player's shipyard

        elif remainingTurns - game_map.calculate_distance(ship.position, game.players[rival()].shipyard.position) <= 15:

            shipsToCrash.append(ship.id)

            shiptargets[ship.id] = game.players[rival()].shipyard.position

        elif ship.id not in shipsToReturn and ship.id not in shipsToCrash:

            shiptargets[ship.id] = locateClosestDense(ship, list(shiptargets.values()))

        if ship.id in shipsToReturn:

            shiptargets[ship.id] = me.shipyard.position

    # Check which ships should stay

    for ship in me.get_ships():

        if ship.id not in shipsToReturn:

            if game_map[ship.position].halite_amount >= halitethreshold or ship.halite_amount < round(game_map[ship.position].halite_amount/10):

                shipsToStay.append(ship.id)

                command_queue.append(ship.stay_still())

                shipsOrdered.append(ship.id)

        if game_map[ship.position].has_structure and game_map[ship.position].structure.owner == me.id and remainingTurns <= 10:

                shipsToStay.append(ship.id)

                command_queue.append(ship.stay_still())

                shipsOrdered.append(ship.id)

        if ship.id not in shipsOrdered and ship.id in shipsToCrash and game_map.calculate_distance(ship.position, game.players[rival()].shipyard.position) == 1:

                shipsToStay.append(ship.id)

                command_queue.append(ship.stay_still())

                shipsOrdered.append(ship.id)

    # Act to reach destinations if ships should move

    shipList = sortShips(me.get_ships())

    for i in range (0, len(shipList)):

        if shipList[i].id not in shipsOrdered and shipList[i].id not in shipsToStay:

            getBack(shipList[i], shiptargets[shipList[i].id])

    # Increment halite threshold by 100 every 10 turns

    if game.turn_number % 10 == 0 and threshold < 1000 :

        threshold += 100

    # If you have spawned less ships than the threshold and have enough halite, spawn a ship.

    # Don't spawn a ship if you will have a ship at port, though.

    shipspawned = False

    if shipsmade <= shipthreshold[game_map.width] and me.halite_amount >= constants.SHIP_COST and nextmap[me.shipyard.position.x][me.shipyard.position.y] < 0:

        command_queue.append(game.me.shipyard.spawn())

        shipsmade+=1

        shipspawned = True

    # Note to self: play around with these numbers

    # Spawn ships if you have at least halite and less than half of threshold ships on the board

    elif halitethreshold == 100 and game.turn_number <= turnamount[game.game_map.width]- 56 and len(me.get_ships()) < shipthreshold[game_map.width]/2 and me.halite_amount >= 1000 and nextmap[me.shipyard.position.x][me.shipyard.position.y] < 0:

        command_queue.append(game.me.shipyard.spawn())

        shipspawned = True
    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
