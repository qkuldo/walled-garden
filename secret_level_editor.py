import game
import sys
import pygame as pg
import modules
import json
ACCEPTED_TILES = "abcdefghijklmnopqrstuvwxyz0123456789#_-+=^"
WALL_LETTERS = "abde"
alphabet = "abcdefghijklmnopqrstuvwxyz"
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
	#Returns nothing if given command was executed, unless command changes brush, in which case it returns brush. Else, returns certain numbers based on issue
	tileX = givenX
	tileY = givenY
	if ((tileX > 26 or tileX < 0) or (tileY > 14 or tileY < 0) or (type(tileX) != int or type(tileY) != int)):
		return 0
	if (command in commandActivators):
		if (command == "p"):
			changeAt((tileY, tileX), brush)
		elif (command == "i"):
			brush = roomLayout[tileY][tileX]
			return brush
		elif (command == "r"):
			brush = tileOption
			return brush
		elif (command == "e"):
			changeAt((tileY, tileX), " ")
	else:
		return 1

def customRoomRenderer(tileLayer, roomLayout, frame):
	alphabet = "abcdefghijklmnopqrstuvwxyz"
	ANIMATED = "f"
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
					if (column in ANIMATED):
						tileLayer.blit(pg.transform.scale(extras.load_frame(alphabet.index(column), frame), (48,48)), (drawx, drawy))
					else:
						tileLayer.blit(pg.transform.scale(extras.load_frame(alphabet.index(column)), (48,48)), (drawx, drawy))
				else:
					tileLayer.blit(pg.transform.scale(game.MISSINGTEXTURE, (48,48)), (drawx, drawy))
			drawx += 48
		drawy += 48
		drawx = 0
	for item in range(0, len(game.ROOMTILEDATA[currentRoom]["items"])):
		itemID = game.ROOMTILEDATA[currentRoom]["items"][item]
		itemCoordinate = game.findTilePixelLocation(game.ROOMTILEDATA[currentRoom]["itemCoordinates"][item][0],game.ROOMTILEDATA[currentRoom]["itemCoordinates"][item][1])
		if (len(game.ITEMDATA["ITEM ASSETS"]) >= itemID):
			itemSurface = pg.transform.scale(pg.image.load(game.ITEMDATA["ITEM ASSETS"][itemID]), (48,48)).convert_alpha()
			tileLayer.blit(itemSurface, itemCoordinate)

def runEditor():
	global currentRoom
	global roomLayout
	global brush
	ROOMLAYER = game.initDrawLayer()
	EDITORHUDLAYER = game.initDrawLayer()
	ANIMATIONSWITCHEVENT = pg.event.custom_type()
	BUTTONPRESSCOOLDOWN = pg.event.custom_type()
	SAVECOOLDOWN = pg.event.custom_type()
	can_pressbutton = True
	display_saveText = False
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
	saveText, saveTextRect = game.createText((50, 20), 2, "saved!", game.BRIGHTYELLOW)
	currentBrushIndex = 0
	brush = ACCEPTED_TILES[currentBrushIndex]
	extras = pg.image.load("assets/extras.png").convert_alpha()
	extras = modules.sheets.Spritesheet(extras,16,16)
	wallSet = game.ROOMTILEDATA[currentRoom]["wall set"]
	propSet = game.ROOMTILEDATA[currentRoom]["prop set"]
	allroomData = game.readJsonFile("rooms.json")
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
			elif (event.type == SAVECOOLDOWN):
				display_saveText = False
				saveTextAlpha = 255
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
		elif (keys[pg.K_b] and can_pressbutton):
			current_tool = "p"
			can_pressbutton = False
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
			currentToolText, currentToolText_Rect = game.createText((game.SCREENWIDTH/4, 20), 2, ("using PAINT"), game.BLUE)
		elif (keys[pg.K_r] and can_pressbutton):
			current_tool = "r"
			can_pressbutton = False
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
			currentToolText, currentToolText_Rect = game.createText((game.SCREENWIDTH/4, 20), 2, ("using BRUSHCHANGE"), game.BLUE)
		elif (keys[pg.K_e] and can_pressbutton):
			current_tool = "e"
			can_pressbutton = False
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
			currentToolText, currentToolText_Rect = game.createText((game.SCREENWIDTH/4, 20), 2, ("using ERASE"), game.BLUE)
		elif (keys[pg.K_s] and can_pressbutton):
			for row in range(15):
				allroomData["rooms"][currentRoom][str(row)] = roomLayout[row]
			with open('rooms.json', 'w') as roomFile:
				json.dump(allroomData, roomFile, indent=2)
			saveText, saveTextRect = game.createText((1000, 20), 2, ("saved as "+currentRoom+"!"), game.BRIGHTYELLOW)
			can_pressbutton = False
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
			display_saveText = True
			pg.time.set_timer(SAVECOOLDOWN, 1000, 1)
			game.SFX["closeMenu"].play()
		if (keys[pg.K_UP] and can_pressbutton and current_tool == "r"):
			currentBrushIndex += 1
			if (currentBrushIndex > len(ACCEPTED_TILES)):
				currentBrushIndex = 0
			brush = ACCEPTED_TILES[currentBrushIndex]
			can_pressbutton = False
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
			currentToolText, currentToolText_Rect = game.createText((game.SCREENWIDTH/4, 20), 2, str(brush), game.BLUE)
		if (keys[pg.K_DOWN] and can_pressbutton and current_tool == "r"):
			currentBrushIndex -= 1
			if (currentBrushIndex < 0):
				currentBrushIndex = len(ACCEPTED_TILES)-1
			brush = ACCEPTED_TILES[currentBrushIndex]
			can_pressbutton = False
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
			currentToolText, currentToolText_Rect = game.createText((game.SCREENWIDTH/4, 20), 2, str(brush), game.BLUE)
		if (current_tool == "r" or current_tool == "p"):
			if (mouseRect.y > 48):
				tileshowing_pos = tileBoxList[mouseRect.collidelist(tileBoxList)].topleft
			else:
				tileshowing_pos = (tileBoxList[mouseRect.collidelist(tileBoxList)].x,0)
			if ((not brush == " ") and (not brush == "@")):
				if (brush.isdigit()):
					EDITORHUDLAYER.blit(pg.transform.scale(game.proptileSpritesheets[propSet].load_frame(int(brush)), (48,48)), tileshowing_pos)
				elif (brush == "#"):
					EDITORHUDLAYER.blit(pg.transform.scale(game.walltileSpritesheets[wallSet].load_frame(0), (48,48)), tileshowing_pos)
				elif (brush == "_"):
					EDITORHUDLAYER.blit(pg.transform.scale(game.walltileSpritesheets[wallSet].load_frame(1), (48,48)), tileshowing_pos)
				elif (brush == "-"):
					EDITORHUDLAYER.blit(pg.transform.scale(game.walltileSpritesheets[wallSet].load_frame(2), (48,48)), tileshowing_pos)
				elif (brush == "+"):
					EDITORHUDLAYER.blit(pg.transform.scale(game.walltileSpritesheets[wallSet].load_frame(3), (48,48)), tileshowing_pos)
				elif (brush == "="):
					EDITORHUDLAYER.blit(pg.transform.scale(game.walltileSpritesheets[wallSet].load_frame(4), (48,48)), tileshowing_pos)
				elif (brush == "^"):
					EDITORHUDLAYER.blit(pg.transform.scale(game.walltileSpritesheets[wallSet].load_frame(5), (48,48)), tileshowing_pos)
				elif (brush in alphabet):
					if (brush in ANIMATED):
						EDITORHUDLAYER.blit(pg.transform.scale(extras.load_frame(alphabet.index(brush), roomFrame), (48,48)), tileshowing_pos)
					else:
						EDITORHUDLAYER.blit(pg.transform.scale(extras.load_frame(alphabet.index(brush)), (48,48)), tileshowing_pos)
				else:
					EDITORHUDLAYER.blit(pg.transform.scale(game.MISSINGTEXTURE, (48,48)), tileshowing_pos)
		if (clicked):
			if (mouseRect.y > 48):
				if (current_tool == "i"):
					brush = recieveInput(current_tool, tileBoxList[mouseRect.collidelist(tileBoxList)].x//48, tileBoxList[mouseRect.collidelist(tileBoxList)].y//48, brush, currentBrushIndex)
					currentBrushIndex = ACCEPTED_TILES.index(brush)
					#print(currentBrushIndex)
				elif (current_tool == "p" or current_tool == "e"):
					recieveInput(current_tool, tileBoxList[mouseRect.collidelist(tileBoxList)].x//48, tileBoxList[mouseRect.collidelist(tileBoxList)].y//48, brush)
			else:
				if (current_tool == "i"):
					brush = recieveInput(current_tool, tileBoxList[mouseRect.collidelist(tileBoxList)].x//48, 0, brush)
				elif (current_tool == "p" or current_tool == "e"):
					recieveInput(current_tool, tileBoxList[mouseRect.collidelist(tileBoxList)].x//48, 0, brush)
		customRoomRenderer(ROOMLAYER, roomLayout, roomFrame)
		if (display_saveText):
			EDITORHUDLAYER.blit(saveText, saveTextRect)
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