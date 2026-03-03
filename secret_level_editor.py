import game
import sys
ACCEPTED_TILES = "abcdefghijklmnopqrstuvwxyz0123456789#_-+=^"
WALL_LETTERS = "abde"
ANIMATED = "f"
game.readAllJsonData()
commandList = ["[p]: Paint Tile", "[q]: Change Tile Brush", "[i]: Pick Tile", "[e]: exit"]
commandActivators = ["p", "q","e","i"]
brush = "a"
currentRoom = "test"
roomLayout = list(game.ROOMTILEDATA[currentRoom].values())[3:18]

def levelGet():
	for tile in roomLayout:
		print(tile)

def changeAt(coordinates = (0, 0), changeTo = "a"):
	#don't forget - coordinates are flipped
	rowConverted = list(roomLayout[coordinates[0]])
	rowConverted[coordinates[1]] = changeTo
	roomLayout[coordinates[0]] = "".join(map(str, rowConverted))

while True:
	levelGet()
	for command in commandList:
		print(command)
	command = input("> ")
	if (command in commandActivators):
		if (command == "p"):
			tileX = int(input("where x?> "))
			tileY = int(input("where y?> "))
			changeAt((tileY, tileX), brush)
		elif (command == "e"):
			sys.exit()
		elif (command == "q"):
			brush = input("brush type?> ")
			if (not (brush in ACCEPTED_TILES and (len(brush) < 2 and len(brush) > 0))):
				print("<qkuldo>that's not a tile!</qkuldo>")
				brush = "a"
		elif (command == "i"):
			tileX = int(input("where x?> "))
			tileY = int(input("where y?> "))
			brush = roomLayout[tileX][tileY]
	else:
		print(f"{command} is not a recognized command.")