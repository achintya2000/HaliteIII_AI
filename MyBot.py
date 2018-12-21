#!/usr/bin/env python3

# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants
from hlt.positionals import Position

import random
import logging


# This game object contains the initial game state.
game = hlt.Game()
# Respond with your name.
game.ready("MyPythonBot")
shipsToReturn = []
threshold = 200

# takes in a ship and a location, returns way to get to location through local minima


def getBack(ship, drop):
    possPos = []
    if ship.position.x < drop.x:
        possPos.append(ship.position.directional_offset((1, 0)))
    if ship.position.x > drop.x:
        possPos.append(ship.position.directional_offset((-1, 0)))
    if ship.position.y < drop.y:
        possPos.append(ship.position.directional_offset((0, 1)))
    if ship.position.y > drop.y:
        possPos.append(ship.position.directional_offset((0, -1)))
    min = possPos[0]
    for pos in possPos:
        if (game_map[pos].halite_amount < game_map[min].halite_amount):
            min = pos
    if min.x < ship.position.x:
        command_queue.append(ship.move("w"))
    elif min.x > ship.position.x:
        command_queue.append(ship.move("e"))
    elif min.y < ship.position.y:
        command_queue.append(ship.move("n"))
    elif min.y > ship.position.y:
        command_queue.append(ship.move("s"))


def locateClosestDense(ship):
    haliteamount = []
    position = []
    max = [0]
    for i in range(0, game_map.height):
        for j in range(0, game_map.width):
            temp = Position(i, j)
            areasum = 0
            for h in temp.get_surrounding_cardinals():
                areasum += game_map[h].halite_amount
            haliteamount.append(areasum + game_map[temp].halite_amount)
            position.append(temp)
    for i in range(0, len(haliteamount)):
        if haliteamount[max[0]] < haliteamount[i]:
            max = [i]
        elif haliteamount[max[0]] == haliteamount[i]:
            max.append(i)
    positions = []
    temp = []
    for i in range(0, len(max)):
        temp.append(game_map.calculate_distance(
            ship.position, position[max[i]]))
        positions.append(position[max[i]])
    return positions[temp.index(min(temp))]


while True:
    # Get the latest game state.
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn.
    command_queue = []
    for ship in me.get_ships():
        # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
        #   Else, collect halite.
        if ship.halite_amount >= threshold and ship.id not in shipsToReturn:
            shipsToReturn.append(ship.id)
        if ship.halite_amount == 0 and ship.id in shipsToReturn:
            shipsToReturn.remove(ship.id)
        if ship.id not in shipsToReturn:
            if game_map[ship.position].halite_amount < 100:
                getBack(ship, locateClosestDense(ship))
            else:
                command_queue.append(ship.stay_still())
        if ship.id in shipsToReturn:
            getBack(ship, me.shipyard.position)
    # increment threshold by 100 every 10 turns
    if game.turn_number % 10 == 0 and threshold < 900:
        threshold += 100
    # If you're on the first turn and have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though.
    if game.turn_number <= 1 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(game.me.shipyard.spawn())
    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
