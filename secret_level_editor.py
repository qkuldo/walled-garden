import game
import sys
import pygame as pg
import modules
ACCEPTED_TILES = "abcdefghijklmnopqrstuvwxyz0123456789#_-+=^"
WALL_LETTERS = "abde"
ANIMATED = "f"
game.readAllJsonData()
allrooms = game.readJsonFile("rooms.json")["roomList"]
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
	#Returns given brush parameter if given command was executed. Else, returns certain numbers based on issue
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
			brush = roomLayout[tileY][tileX]
		return brush
	else:
		return 1

def customRoomRenderer(tileLayer, roomLayout, frame):
	alphabet = "abcdefghijklmnopqrstuvwxyz"
	animatedTiles = "f"
	wallSet = game.ROOMTILEDATA[currentRoom]["wall set"]
	propSet = game.ROOMTILEDATA[currentRoom]["prop set"]
	drawx, drawy = (0, 0)
	extras = pg.image.load("assets/extras.png").convert_alpha()
	extras = modules.sheets.Spritesheet(extras,16,16)
	for row in roomLayout:
		for column in row:
			if ((not column == " ") and (not column == "@")):
				if (column.isdigit()):
					tileLayer.blit(pg.transform.scale(game.proptileSpritesheets[propSet].load_frame(int(column)), (48,48)), (drawx, drawy))
				elif (column == "#"):
					tileLayer.blit(pg.transform.scale(game.walltileSpritesheets[wallSet].load_frame(0), (48,48)), (drawx, drawy))
				elif (column == "_"):
					tileLayer.blit(pg.transform.scale(game.walltileSpritesheets[wallSet].load_frame(1), (48,48)), (drawx, drawy))
				elif (column == "-"):
					tileLayer.blit(pg.transform.scale(game.walltileSpritesheets[wallSet].load_frame(2), (48,48)), (drawx, drawy))
				elif (column == "+"):
					tileLayer.blit(pg.transform.scale(game.walltileSpritesheets[wallSet].load_frame(3), (48,48)), (drawx, drawy))
				elif (column == "="):
					tileLayer.blit(pg.transform.scale(game.walltileSpritesheets[wallSet].load_frame(4), (48,48)), (drawx, drawy))
				elif (column == "^"):
					tileLayer.blit(pg.transform.scale(game.walltileSpritesheets[wallSet].load_frame(5), (48,48)), (drawx, drawy))
				elif (column in alphabet):
					if (column in animatedTiles):
						tileLayer.blit(pg.transform.scale(extras.load_frame(alphabet.index(column), frame), (48,48)), (drawx, drawy))
					else:
						tileLayer.blit(pg.transform.scale(extras.load_frame(alphabet.index(column)), (48,48)), (drawx, drawy))
				else:
					tileLayer.blit(pg.transform.scale(MISSINGTEXTURE, (48,48)), (drawx, drawy))
			drawx += 48
		drawy += 48
		drawx = 0

def runEditor():
	global currentRoom
	global roomLayout
	global brush
	ROOMLAYER = game.initDrawLayer()
	EDITORHUDLAYER = game.initDrawLayer()
	ANIMATIONSWITCHEVENT = pg.event.custom_type()
	BUTTONPRESSCOOLDOWN = pg.event.custom_type()
	can_pressbutton = True
	pg.time.set_timer(ANIMATIONSWITCHEVENT, 360)
	roomFrame = 0
	currentRoom = allrooms[0]
	clicked = False
	tileCoordinatesX = list(range(0, 28))
	tileCoordinatesY = list(range(0, 15))
	findoutX = 0
	findoutY = 0
	tileBoxList = []
	roomIndex = 0
	currentRoomText, currentRoomText_Rect = game.createText((game.SCREENWIDTH/2, 20), 2, currentRoom, game.ORANGE)
	for row in roomLayout:
		findoutX = 0
		findoutY += 48
		for column in row:
			tileBoxList.append(pg.Rect(findoutX, findoutY, 48, 48))
			findoutX += 48
	current_tool = "p"
	currentToolText, currentToolText_Rect = game.createText((game.SCREENWIDTH/4, 20), 2, ("using PAINT"), game.BLUE)
	while True:
		mouseRect = pg.Rect(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1], 48, 48)
		game.clearLayer(ROOMLAYER)
		game.clearLayer(EDITORHUDLAYER)
		game.clearLayer(game.screen)
		switchFrame = False
		tileOption = "a"
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
			elif (event.type == BUTTONPRESSCOOLDOWN):
				can_pressbutton = True
		keys = pg.key.get_pressed()
		if (keys[pg.K_l] and can_pressbutton):
			roomIndex += 1
			if (roomIndex > len(allrooms)-1):
				roomIndex = 0
			currentRoom = allrooms[roomIndex]
			roomLayout = list(game.ROOMTILEDATA[currentRoom].values())[3:18]
			can_pressbutton = False
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
			currentRoomText, currentRoomText_Rect = game.createText((game.SCREENWIDTH/2, 20), 2, currentRoom, game.ORANGE)
		elif (keys[pg.K_i] and can_pressbutton):
			current_tool = "i"
			can_pressbutton = False
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
			currentToolText, currentToolText_Rect = game.createText((game.SCREENWIDTH/4, 20), 2, ("using COLORPICKER}"), game.BLUE)
		elif (keys[pg.K_p] and can_pressbutton):
			current_tool = "p"
			can_pressbutton = False
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
			currentToolText, currentToolText_Rect = game.createText((game.SCREENWIDTH/4, 20), 2, ("using PAINT"), game.BLUE)
		if (clicked):
			brush = recieveInput(current_tool, tileBoxList[mouseRect.collidelist(tileBoxList)].x//48, tileBoxList[mouseRect.collidelist(tileBoxList)].y//48, brush)
		customRoomRenderer(ROOMLAYER, roomLayout, roomFrame)
		EDITORHUDLAYER.blit(currentRoomText, currentRoomText_Rect)
		EDITORHUDLAYER.blit(currentToolText, currentToolText_Rect)
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