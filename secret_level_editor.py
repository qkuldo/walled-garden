import game
import sys
import pygame as pg
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

def recieveInput(command, givenX = 0, givenY = 0, brush = "a", tileOption = "b"):
	#Returns True if given command was executed. Else, returns certain numbers based on issue
	tileX = givenX
	tileY = givenY
	if ((tileX > 26 or tileX < 0) or (tileY > 14 or tileY < 0) or (type(tileX) != int or type(tileY) != int)):
		return 0
	if (command in commandActivators):
		if (command == "p"):
			changeAt((tileY, tileX), brush)
		elif (command == "q"):
			if (tileOption in ACCEPTED_TILES and (len(tileOption) < 2 and len(tileOption) > 0)):
				brush = tileOption
			else:
				return 2
		elif (command == "i"):
			brush = roomLayout[tileX][tileY]
		return True
	else:
		return 1

def runEditor():
	ROOMLAYER = game.initDrawLayer()
	EDITORHUDLAYER = game.initDrawLayer()
	ANIMATIONSWITCHEVENT = pg.event.custom_type()
	pg.time.set_timer(ANIMATIONSWITCHEVENT, 360)
	roomFrame = 0
	currentRoom = "test"
	clicked = False
	while True:
		mouseRect = pg.Rect(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1], 48, 48)
		game.clearLayer(ROOMLAYER)
		game.clearLayer(EDITORHUDLAYER)
		game.clearLayer(game.screen)
		switchFrame = False
		for event in pg.event.get():
			if (event.type == pg.QUIT):
				game.terminate()
			elif (event.type == ANIMATIONSWITCHEVENT):
				switchFrame = True
				if (roomFrame == 0):
					roomFrame = 1
				else:
					roomFrame = 0
			elif (event.type == pg.MOUSEBUTTONDOWN):
				clicked = True
			elif (event.type == pg.MOUSEBUTTONUP):
				clicked = False
		game.loadRoom(currentRoom, ROOMLAYER, game.ITEMDATA["ITEM ASSETS"], False, roomFrame)
		game.screen.blit(ROOMLAYER, (0, 0))
		game.screen.blit(EDITORHUDLAYER, (0, 0))
		if (not clicked):
			game.screen.blit(game.CURSOR, pg.mouse.get_pos())
		else:
			game.screen.blit(game.CURSORCLICKED, pg.mouse.get_pos())
		pg.display.flip()
		game.clock.tick(game.FPS)

if (__name__ == "__main__"):
	game.setup()
	game.loadTileSpritesheets()
	runEditor()