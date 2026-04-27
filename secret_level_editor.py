import game
import sys
import pygame as pg
import modules
import random
import json
import copy
ACCEPTED_TILES = "abcdefghijklmnopqrstuvwxyz0123456789#_-+=^@"
WALL_LETTERS = "abde"
alphabet = "abcdefghijklmnopqrstuvwxyz"
ANIMATED = "f"
game.readAllJsonData()
commandActivators = ["p", "q","e","i"]
brush = "a"
currentRoom = "test"
allroomData = game.readJsonFile("rooms.json")
roomLayout = list(allroomData["rooms"][currentRoom].values())[3:18]
roomItems = allroomData["rooms"][currentRoom]["items"]
roomExits = allroomData["rooms"][currentRoom]["exits"]
allExits = allroomData["exitData"]
roomItemCoordinates = allroomData["rooms"][currentRoom]["itemCoordinates"]
alphabet = "abcdefghijklmnopqrstuvwxyz"

def levelGet():
	for tile in roomLayout:
		print(tile)

def changeAt(coordinates = (0, 0), changeTo = "a"):
	#don't forget - coordinates are flipped
	rowConverted = list(roomLayout[coordinates[0]])
	rowConverted[coordinates[1]] = changeTo
	roomLayout[coordinates[0]] = "".join(map(str, rowConverted))

def recieveInput(command, givenX = 0, givenY = 0, brush = "a", tileOption = "b", itembrush=0, itemVersion=False):
	global roomItems
	global roomItemCoordinates
	#Returns nothing if given command was executed, unless command changes brush, in which case it returns brush. Else, returns certain numbers based on issue
	tileX = givenX
	tileY = givenY
	if ((tileX > 26 or tileX < 0) or (tileY > 14 or tileY < 0) or (type(tileX) != int or type(tileY) != int)):
		return 0
	if (command in commandActivators):
		if (command == "p"):
			if (not itemVersion):
				changeAt((tileY, tileX), brush)
			else:
				if (not [givenX, givenY] in roomItemCoordinates):
					roomItems.append(itembrush)
					roomItemCoordinates.append([givenX, givenY])
		elif (command == "i"):
			brush = roomLayout[tileY][tileX]
			return brush
		elif (command == "r"):
			if (not itemVersion):
				brush = tileOption
				return brush
		elif (command == "e"):
			if (not itemVersion):
				changeAt((tileY, tileX), " ")
			else:
				if ([givenX, givenY] in roomItemCoordinates):
					roomItems.pop(roomItemCoordinates.index([givenX, givenY]))
					roomItemCoordinates.pop(roomItemCoordinates.index([givenX, givenY]))
	else:
		return 1

def customRoomRenderer(tileLayer, roomLayout, frame, extraView=1):
	global allroomData
	"""extraView parameter controls what extra information can be displayed with tiles
	extraView = 0 means that all tiles will be displayed except for the @ tile(just like normal gameplay)
	extraView = 1 means that @ tile will be displayed along with all tiles
	extraView = 2 means that @ tile will be displayed, wall indicators
	"""
	wallLetters = "abde"
	ANIMATED = "f"
	disabledExits = []
	oneWayExits = []
	roomExits_noOneWay = copy.deepcopy(roomExits)
	for exit in allroomData["exitData"]:
		if (currentRoom in exit["involved rooms"] and not allExits.index(exit) in roomExits):
			disabledExits.append(allExits.index(exit))
		elif (currentRoom in exit["involved rooms"]):
			otherRoom = copy.deepcopy(exit["involved rooms"])
			otherRoom.remove(currentRoom)
			if (not allExits.index(exit) in allroomData["rooms"][otherRoom[0]]["exits"]):
				oneWayExits.append(allExits.index(exit))
				roomExits_noOneWay.remove(allExits.index(exit))
	wallSet = allroomData["rooms"][currentRoom]["wall set"]
	propSet = allroomData["rooms"][currentRoom]["prop set"]
	drawx, drawy = (0, 0)
	extras = pg.image.load("assets/extras.png").convert_alpha()
	extras = modules.sheets.Spritesheet(extras,16,16)
	wallDisplay = pg.Surface((48,48))
	wallDisplay.fill(game.ORANGE)
	wallDisplay.set_alpha(100)
	exitDisplay = pg.Surface((4,4))
	exitDisplay.fill((7,240,5))
	exitDisplay.set_alpha(100)
	exitDisplay_fake = pg.Surface((24,24))
	exitDisplay_fake.fill(game.BLUE)
	exitDisplay_fake.set_alpha(100)
	disabled_exitDisplay_fake = pg.Surface((24,24))
	disabled_exitDisplay_fake.fill((25,25,25))
	disabled_exitDisplay_fake.set_alpha(100)
	oneWay_exitDisplay_fake = pg.Surface((24,24))
	oneWay_exitDisplay_fake.fill((150,50,50))
	oneWay_exitDisplay_fake.set_alpha(100)
	exitSelectors = []
	for row in roomLayout:
		for column in row:
			if ((not column == " ")):
				if (column.isdigit()):
					tileLayer.blit(pg.transform.scale(game.proptileSpritesheets[propSet].load_frame(int(column)), (48,48)), (drawx, drawy))
				elif (column == "#"):
					tileLayer.blit(pg.transform.scale(game.walltileSpritesheets[wallSet].load_frame(0), (48,48)), (drawx, drawy))
					if (extraView == 2 or extraView == 3):
						tileLayer.blit(wallDisplay, (drawx, drawy))
				elif (column == "_"):
					tileLayer.blit(pg.transform.scale(game.walltileSpritesheets[wallSet].load_frame(1), (48,48)), (drawx, drawy))
					if (extraView == 2 or extraView == 3):
						tileLayer.blit(wallDisplay, (drawx, drawy))
				elif (column == "-"):
					tileLayer.blit(pg.transform.scale(game.walltileSpritesheets[wallSet].load_frame(2), (48,48)), (drawx, drawy))
					if (extraView == 2 or extraView == 3):
						tileLayer.blit(wallDisplay, (drawx, drawy))
				elif (column == "+"):
					tileLayer.blit(pg.transform.scale(game.walltileSpritesheets[wallSet].load_frame(3), (48,48)), (drawx, drawy))
					if (extraView == 2 or extraView == 3):
						tileLayer.blit(wallDisplay, (drawx, drawy))
				elif (column == "="):
					tileLayer.blit(pg.transform.scale(game.walltileSpritesheets[wallSet].load_frame(4), (48,48)), (drawx, drawy))
					if (extraView == 2 or extraView == 3):
						tileLayer.blit(wallDisplay, (drawx, drawy))
				elif (column == "^"):
					tileLayer.blit(pg.transform.scale(game.walltileSpritesheets[wallSet].load_frame(5), (48,48)), (drawx, drawy))
					if (extraView == 2 or extraView == 3):
						tileLayer.blit(wallDisplay, (drawx, drawy))
				elif (column == "@"):
					if (extraView > 0):
						tileLayer.blit(pg.transform.scale(playerAsset.load_frame(0), (48,48)), (drawx, drawy))
				elif (column in alphabet):
					if (column in ANIMATED):
						tileLayer.blit(pg.transform.scale(extras.load_frame(alphabet.index(column), frame), (48,48)), (drawx, drawy))
					else:
						tileLayer.blit(pg.transform.scale(extras.load_frame(alphabet.index(column)), (48,48)), (drawx, drawy))
					if (column in wallLetters and (extraView == 2 or extraView == 3)):
						tileLayer.blit(wallDisplay, (drawx, drawy))
				else:
					tileLayer.blit(pg.transform.scale(game.MISSINGTEXTURE, (48,48)), (drawx, drawy))
			drawx += 48
		drawy += 48
		drawx = 0
	for item in range(0, len(roomItems)):
		itemID = roomItems[item]
		itemCoordinate = game.findTilePixelLocation(roomItemCoordinates[item][0],roomItemCoordinates[item][1])
		if (len(game.ITEMDATA["ITEM ASSETS"]) >= itemID):
			itemSurface = pg.transform.scale(pg.image.load(game.ITEMDATA["ITEM ASSETS"][itemID]), (48,48)).convert_alpha()
			tileLayer.blit(itemSurface, itemCoordinate)
	if (extraView > 0):
		displayRect = pg.Rect(0,0, 4, 4)
		fakeDisplayRect = pg.Rect(0,0, 24, 24)
		for exit in roomExits_noOneWay + disabledExits + oneWayExits:
			exitCoordinate = game.findTilePixelLocation(allExits[exit][currentRoom][0],allExits[exit][currentRoom][1])
			posRect = pg.Rect(exitCoordinate, (48, 48))
			exitSelectors.append(posRect)
			displayRect.center = posRect.center
			fakeDisplayRect.center = posRect.center
			IDtext, IDtext_rect = game.createText(posRect.center, text=str(exit))
			IDtext.set_alpha(50)
			tileLayer.blit(IDtext, IDtext_rect)
			if (exit in disabledExits):
				tileLayer.blit(disabled_exitDisplay_fake, fakeDisplayRect)
			elif (exit in oneWayExits):
				tileLayer.blit(oneWay_exitDisplay_fake, fakeDisplayRect)
			else:
				tileLayer.blit(exitDisplay_fake, fakeDisplayRect)
			tileLayer.blit(exitDisplay, displayRect)
	return exitSelectors, roomExits_noOneWay + disabledExits + oneWayExits #check for selecting exits to edit

def makeExitLoop(toggleEvent, togglekey=pg.K_ESCAPE, roomLayout=pg.Surface((game.SCREENWIDTH, game.SCREENHEIGHT)),fromRoomIndex=0, data=[]):
	#data parameter is for editing premade exits, and is just the exit data.
	allowLoopTerminate = False
	clicked = False
	blueBoxRect = pg.Rect(0,0, game.SCREENWIDTH, game.SCREENHEIGHT//3+(48*2))
	titleText, titleTextRect = game.createText((game.SCREENWIDTH//2, 20), text="qkuldo's very high-tech Exit Editor", color=game.BRIGHTYELLOW)
	toText, toRect = game.createText((game.SCREENWIDTH//2, 180), font=2, text="to", color=game.BRIGHTYELLOW)
	lilGuyDecorator = pg.transform.scale(playerAsset.load_frame(0), (48,48))
	can_pressbutton = True
	selection = 0
	#selection table:
	# value | button
	# -1    | none
	#  0    | left room slot
	#  1    | right room slot
	if (len(data) == 0):
		toRoomIndex = 0
		leftSlotSwitch, rightSlotSwitch = True, True
	else:
		involvedRooms = data["involved rooms"].copy()
		involvedRooms.remove(allroomData["roomList"][fromRoomIndex])
		toRoomIndex = allroomData["roomList"].index(involvedRooms[0])
		leftSlotSwitch, rightSlotSwitch = False, False
		if (allExits.index(data) in allroomData["rooms"][allroomData["roomList"][fromRoomIndex]]["exits"]):
			leftSlotSwitch = True
		if (allExits.index(data) in allroomData["rooms"][allroomData["roomList"][toRoomIndex]]["exits"]):
			rightSlotSwitch = True
	BUTTONPRESSCOOLDOWN = pg.event.custom_type()
	leftSlotSwitchText, leftSlotSwitchRect = game.createText((game.SCREENWIDTH//3, 250), text="X", color=game.BRIGHTYELLOW)
	rightSlotSwitchText, rightSlotSwitchRect = game.createText((game.SCREENWIDTH//2+game.SCREENWIDTH//3-200, 250), text="X", color=game.BRIGHTYELLOW)
	while True:
		if (leftSlotSwitch):
			leftSlotSwitchText, leftSlotSwitchRect = game.createText((game.SCREENWIDTH//3, 250), text="X", color=game.BRIGHTYELLOW)
		else:
			leftSlotSwitchText, leftSlotSwitchRect = game.createText((game.SCREENWIDTH//3, 250), text="[]", color=game.BRIGHTYELLOW)
		if (rightSlotSwitch):
			rightSlotSwitchText, rightSlotSwitchRect = game.createText((game.SCREENWIDTH//2+game.SCREENWIDTH//3-200, 250), text="X", color=game.BRIGHTYELLOW)
		else:
			rightSlotSwitchText, rightSlotSwitchRect = game.createText((game.SCREENWIDTH//2+game.SCREENWIDTH//3-200, 250), text="[]", color=game.BRIGHTYELLOW)
		mouseRect = pg.Rect(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1], 48, 48)
		roomSlotLeft = allroomData["roomList"][fromRoomIndex]
		roomSlotRight = allroomData["roomList"][toRoomIndex]
		leftSlotText, leftSlotRect = game.createText((game.SCREENWIDTH//3, 180), text=roomSlotLeft, color=game.BRIGHTYELLOW)
		rightSlotText, rightSlotRect = game.createText((game.SCREENWIDTH//2+game.SCREENWIDTH//3-200, 180), text=roomSlotRight, color=game.BRIGHTYELLOW)
		if (selection == 0):
			leftSlotText, leftSlotRect = game.createText((game.SCREENWIDTH//3, 180), text=roomSlotLeft, color=game.ORANGE)
		elif (selection == 1):
			rightSlotText, rightSlotRect = game.createText((game.SCREENWIDTH//2+game.SCREENWIDTH//3-200, 180), text=roomSlotRight, color=game.ORANGE)
		for event in pg.event.get():
			if (event.type == pg.QUIT):
				game.terminate()
			elif (event.type == toggleEvent):
				allowLoopTerminate = True
			elif (event.type == pg.MOUSEBUTTONDOWN):
				clicked = True
			elif (event.type == pg.MOUSEBUTTONUP):
				clicked = False
			elif (event.type == BUTTONPRESSCOOLDOWN):
				can_pressbutton = True
		keys = pg.key.get_pressed()
		if (keys[togglekey] and allowLoopTerminate):
			break
		if (keys[pg.K_l] and can_pressbutton):
			if (selection == 0):
				fromRoomIndex += 1
				if (fromRoomIndex > len(allroomData["roomList"])-1):
					fromRoomIndex = 0
				game.SFX["equipItem"].play()
			elif (selection == 1):
				toRoomIndex += 1
				if (toRoomIndex > len(allroomData["roomList"])-1):
					toRoomIndex = 0
				game.SFX["equipItem"].play()
			can_pressbutton = False
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
		if (clicked):
			selection = -1
			if (mouseRect.colliderect(leftSlotRect)):
				selection = 0
			elif (mouseRect.colliderect(rightSlotRect)):
				selection = 1
			elif (mouseRect.colliderect(leftSlotSwitchRect) and can_pressbutton):
				game.SFX["equipItem"].play()
				leftSlotSwitch = not leftSlotSwitch
				can_pressbutton = False
				pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
			elif (mouseRect.colliderect(rightSlotSwitchRect) and can_pressbutton):
				game.SFX["equipItem"].play()
				rightSlotSwitch = not rightSlotSwitch
				can_pressbutton = False
				pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
		game.screen.blit(roomLayout, (0,0))
		pg.draw.rect(game.screen, game.BLUE, blueBoxRect)
		game.screen.blit(titleText, titleTextRect)
		game.screen.blit(toText, toRect)
		game.screen.blit(leftSlotText, leftSlotRect)
		game.screen.blit(rightSlotText, rightSlotRect)
		game.screen.blit(leftSlotSwitchText, leftSlotSwitchRect)
		game.screen.blit(rightSlotSwitchText, rightSlotSwitchRect)
		game.screen.blit(lilGuyDecorator, (titleTextRect.topleft[0]-48,titleTextRect.topleft[1]))
		game.screen.blit(lilGuyDecorator, titleTextRect.topright)
		if (not clicked):
			game.screen.blit(game.CURSOR, pg.mouse.get_pos())
		else:
			game.screen.blit(game.CURSORCLICKED, pg.mouse.get_pos())
		pg.display.flip()
		game.clock.tick(game.FPS)
	pg.time.set_timer(toggleEvent, 500, 1)
	return False #will be used for main button check flag


def runEditor():
	global currentRoom
	global roomLayout
	global brush
	global roomItems
	global roomItemCoordinates
	global roomExits
	global BUTTONPRESSCOOLDOWN
	commandList = ["qkuldo's very futuristic modern ","high-tech room editor","[b]: Paint Tile", "[q]: Change Tile Brush", "[i]: Tilepicker",  "[l]: Switch room","[x]: Switch to Item Mode","[e]: Erase Tile","[r]: Change Tile with up/down arrow keys","[s]: Save Room","[v]: Change Helper View","[n]: New Room","[d]: Delete Current Room","[t]: Exit Select","[left shift]: Edit Exits","[h]: Toggle this Help Menu"]
	ROOMLAYER = game.initDrawLayer()
	EDITORHUDLAYER = game.initDrawLayer()
	ANIMATIONSWITCHEVENT = pg.event.custom_type()
	BUTTONPRESSCOOLDOWN = pg.event.custom_type()
	SAVECOOLDOWN = pg.event.custom_type()
	EXITEDITORCOOLDOWN = pg.event.custom_type()
	can_pressbutton = True
	display_saveText = False
	pg.time.set_timer(ANIMATIONSWITCHEVENT, 360)
	roomFrame = 0
	currentRoom = allroomData["roomList"][0]
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
	currentModeText, currentModeText_Rect = game.createText((100, 20), 2, ("TILE MODE"), game.BRIGHTYELLOW)
	saveText, saveTextRect = game.createText((50, 20), 2, "saved!", game.BRIGHTYELLOW)
	helpText, helpText_Rect = game.createText((1100, 20), 2, ("[c]:aaaaaaaaa"), game.ORANGE)
	currentBrushIndex = 0
	brush = ACCEPTED_TILES[currentBrushIndex]
	extras = pg.image.load("assets/extras.png").convert_alpha()
	extras = modules.sheets.Spritesheet(extras,16,16)
	wallSet = allroomData["rooms"][currentRoom]["wall set"]
	propSet = allroomData["rooms"][currentRoom]["prop set"]
	exits = allroomData["rooms"][currentRoom]["exits"]
	itembrush = 2
	itemVer = False
	helpMenu = True
	hudView = 1
	exitHover = pg.Rect(0,0, 24, 24)
	while True:
		helpMenu_index = 0
		helpMenu_drawy = 20
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
			game.SFX["equipItem"].play()
			roomIndex += 1
			if (roomIndex > len(allroomData["roomList"])-1):
				roomIndex = 0
			currentRoom = allroomData["roomList"][roomIndex]
			roomLayout = list(allroomData["rooms"][currentRoom].values())[3:18]
			roomItems = allroomData["rooms"][currentRoom]["items"]
			roomItemCoordinates = allroomData["rooms"][currentRoom]["itemCoordinates"]
			roomExits = allroomData["rooms"][currentRoom]["exits"]
			can_pressbutton = False
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
			currentRoomText, currentRoomText_Rect = game.createText((game.SCREENWIDTH/2, 20), 2, currentRoom, game.ORANGE)
		elif (keys[pg.K_h] and can_pressbutton and hudView):
			game.SFX["equipItem"].play()
			helpMenu = not helpMenu
			can_pressbutton = False
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
		elif (keys[pg.K_n] and can_pressbutton):
			game.SFX["equipItem"].play()
			can_pressbutton = False
			roomLayout = []
			for row in range(15):
				roomLayout.append("                           ")
			roomItems = []
			roomExits = []
			roomItemCoordinates = []
			currentRoom = "".join(random.choices(alphabet, k=10))
			allroomData["rooms"][currentRoom] = {}
			allroomData["rooms"][currentRoom]["wall set"] = 0
			allroomData["rooms"][currentRoom]["prop set"] = 0
			allroomData["rooms"][currentRoom]["theme"] = game.DARKBLUE
			for row in range(15):
				allroomData["rooms"][currentRoom][str(row)] = roomLayout[row]
			allroomData["rooms"][currentRoom]["items"] = roomItems
			allroomData["rooms"][currentRoom]["itemCoordinates"] = roomItemCoordinates
			allroomData["rooms"][currentRoom]["exits"] = []
			allroomData["roomList"].append(currentRoom)
			currentRoomText, currentRoomText_Rect = game.createText((game.SCREENWIDTH/2, 20), 2, currentRoom, game.ORANGE)
			roomIndex = allroomData["roomList"].index(currentRoom)
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
		elif (keys[pg.K_d] and can_pressbutton):
			game.SFX["equipItem"].play()
			if (len(allroomData["rooms"]) > 1):
				allroomData["rooms"].pop(currentRoom)
				allroomData["roomList"].remove(currentRoom)
				roomIndex -= 1
				currentRoom = allroomData["roomList"][roomIndex]
				currentRoomText, currentRoomText_Rect = game.createText((game.SCREENWIDTH/2, 20), 2, currentRoom, game.ORANGE)
				roomLayout = list(allroomData["rooms"][currentRoom].values())[3:18]
			else:
				game.SFX["openMenu"].play()
			can_pressbutton = False
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
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
		elif (keys[pg.K_x] and can_pressbutton):
			game.SFX["equipItem"].play()
			itemVer = not itemVer
			if (itemVer):
				currentModeText, currentModeText_Rect = game.createText((100, 20), 2, ("ITEM MODE"), game.BRIGHTYELLOW)
				commandList = ["[b]: Paint Item", "[q]: Change Item Brush", "[i]: Itempicker",  "[l]: Switch room","[x]: Switch to Tile Mode","[e]: Erase Item","[r]: Change Item with up/down arrow keys","[s]: Save Room","[v]: Change Helper View","[n]: New Room","[d]: Delete Current Room","[t]: Exit Select","[left shift]: Edit Exits","[h]: Toggle this Help Menu"]
			else:
				currentModeText, currentModeText_Rect = game.createText((100, 20), 2, ("TILE MODE"), game.BRIGHTYELLOW)
				commandList = ["[b]: Paint Tile", "[q]: Change Tile Brush", "[i]: Tilepicker",  "[l]: Switch room","[x]: Switch to Item Mode","[e]: Erase Tile","[r]: Change Tile with up/down arrow keys","[s]: Save Room","[v]: Change Helper View","[n]: New Room","[d]: Delete Current Room","[t]: Exit Select","[left shift]: Edit Exits","[h]: Toggle this Help Menu"]
			can_pressbutton = False
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
		elif (keys[pg.K_v] and can_pressbutton):
			hudView += 1
			if (hudView > 3):
				hudView = 0
			can_pressbutton = False
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
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
			allroomData["rooms"][currentRoom]["items"] = roomItems
			allroomData["rooms"][currentRoom]["exits"] = roomExits
			allroomData["rooms"][currentRoom]["itemCoordinates"] = roomItemCoordinates
			with open('rooms.json', 'w') as roomFile:
				json.dump(allroomData, roomFile, indent=2)
			saveText, saveTextRect = game.createText((1000, 20), 2, ("saved as "+currentRoom+"!"), game.BRIGHTYELLOW)
			can_pressbutton = False
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
			display_saveText = True
			pg.time.set_timer(SAVECOOLDOWN, 1000, 1)
			game.SFX["closeMenu"].play()
		elif (keys[pg.K_t] and can_pressbutton):
			current_tool = "t"
			can_pressbutton = False
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
			currentToolText, currentToolText_Rect = game.createText((game.SCREENWIDTH/4, 20), 2, ("using EXIT SELECT"), game.BLUE)
		if (keys[pg.K_UP] and can_pressbutton and current_tool == "r"):
			if (not itemVer):
				currentBrushIndex += 1
				if (currentBrushIndex > len(ACCEPTED_TILES)-1):
					currentBrushIndex = 0
				brush = ACCEPTED_TILES[currentBrushIndex]
			else:
				itembrush += 1
				if (itembrush > len(game.ITEMDATA["ITEM TYPES"])-1):
					itembrush = 0
			can_pressbutton = False
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
			currentToolText, currentToolText_Rect = game.createText((game.SCREENWIDTH/4, 20), 2, str(brush), game.BLUE)
		if (keys[pg.K_DOWN] and can_pressbutton and current_tool == "r"):
			if (not itemVer):
				currentBrushIndex -= 1
				if (currentBrushIndex < 0):
					currentBrushIndex = len(ACCEPTED_TILES) - 1
				brush = ACCEPTED_TILES[currentBrushIndex]
			else:
				itembrush -= 1
				if (itembrush < 0):
					itembrush = len(game.ITEMDATA["ITEM TYPES"]) - 1
			can_pressbutton = False
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
			currentToolText, currentToolText_Rect = game.createText((game.SCREENWIDTH/4, 20), 2, str(brush), game.BLUE)
		if (keys[pg.K_LSHIFT] and can_pressbutton):
			ROOMLAYER.fill((0,0,15))
			customRoomRenderer(ROOMLAYER, roomLayout, roomFrame, hudView)
			pg.time.set_timer(BUTTONPRESSCOOLDOWN, 500, 1)
			exitID = 0
			if (current_tool == "t"):
				for exitSelector in exitSelectors:
					if (exitSelector.colliderect(mouseRect)):
						exitID = knownExits[exitSelectors.index(exitSelector)]
						can_pressbutton = makeExitLoop(BUTTONPRESSCOOLDOWN, pg.K_LSHIFT, ROOMLAYER, roomIndex, allExits[exitID])
						break
				if (can_pressbutton):
					can_pressbutton = makeExitLoop(BUTTONPRESSCOOLDOWN, pg.K_LSHIFT, ROOMLAYER, roomIndex)
			else:
				can_pressbutton = makeExitLoop(BUTTONPRESSCOOLDOWN, pg.K_LSHIFT, ROOMLAYER, roomIndex)
		if (mouseRect.y > 48):
			tileshowing_pos = tileBoxList[mouseRect.collidelist(tileBoxList)].topleft
		else:
			tileshowing_pos = (tileBoxList[mouseRect.collidelist(tileBoxList)].x,0)
		if ((current_tool == "r" or current_tool == "p") and not itemVer):
			if ((not brush == " ")):
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
				elif (brush == "@"):
					EDITORHUDLAYER.blit(pg.transform.scale(playerAsset.load_frame(0), (48,48)), tileshowing_pos)
				elif (brush in alphabet):
					if (brush in ANIMATED):
						EDITORHUDLAYER.blit(pg.transform.scale(extras.load_frame(alphabet.index(brush), roomFrame), (48,48)), tileshowing_pos)
					else:
						EDITORHUDLAYER.blit(pg.transform.scale(extras.load_frame(alphabet.index(brush)), (48,48)), tileshowing_pos)
				else:
					EDITORHUDLAYER.blit(pg.transform.scale(game.MISSINGTEXTURE, (48,48)), tileshowing_pos)
		elif (itemVer and (current_tool == "r" or current_tool == "p")):
			itemSurface = pg.transform.scale(pg.image.load(game.ITEMDATA["ITEM ASSETS"][itembrush]), (48,48)).convert_alpha()
			EDITORHUDLAYER.blit(itemSurface, tileshowing_pos)
		if (current_tool == "t"):
			for exitSelector in exitSelectors:
				if (exitSelector.colliderect(mouseRect)):
					tempAlphaChange = game.initDrawLayer()
					exitHover.center = exitSelector.center
					pg.draw.rect(tempAlphaChange, game.ORANGE, exitHover)
					tempAlphaChange.set_alpha(150)
					EDITORHUDLAYER.blit(tempAlphaChange)
					break
		ROOMLAYER.fill((0,0,15))
		exitSelectors, knownExits = customRoomRenderer(ROOMLAYER, roomLayout, roomFrame, hudView)
		if (clicked):
			if (mouseRect.y > 48):
				if (current_tool == "i"):
					brush = recieveInput(current_tool, tileBoxList[mouseRect.collidelist(tileBoxList)].x//48, tileBoxList[mouseRect.collidelist(tileBoxList)].y//48, brush, itembrush=itembrush, itemVersion=itemVer)
					currentBrushIndex = ACCEPTED_TILES.index(brush)
					#print(currentBrushIndex)
				elif (current_tool == "p" or current_tool == "e" or current_tool == "g"):
					recieveInput(current_tool, tileBoxList[mouseRect.collidelist(tileBoxList)].x//48, tileBoxList[mouseRect.collidelist(tileBoxList)].y//48, brush, itembrush=itembrush, itemVersion=itemVer)
			else:
				if (current_tool == "i"):
					brush = recieveInput(current_tool, tileBoxList[mouseRect.collidelist(tileBoxList)].x//48, 0, brush, itembrush=itembrush, itemVersion=itemVer)
				elif (current_tool == "p" or current_tool == "e" or current_tool == "g"):
					recieveInput(current_tool, tileBoxList[mouseRect.collidelist(tileBoxList)].x//48, 0, brush, itembrush=itembrush, itemVersion=itemVer)
		if (hudView != 3):
			EDITORHUDLAYER.blit(currentToolText, currentToolText_Rect)
			if (display_saveText):
				EDITORHUDLAYER.blit(saveText, saveTextRect)
			EDITORHUDLAYER.blit(currentModeText, currentModeText_Rect)
			EDITORHUDLAYER.blit(currentRoomText, currentRoomText_Rect)
		if (helpMenu and hudView != 3):
			for text in commandList:
				helpText, helpText_Rect = game.createText((1100, helpMenu_drawy), 2, text, game.ORANGE)
				helpMenu_index += 1
				helpMenu_drawy += 20
				helpText_Rect.midright = (game.SCREENWIDTH,helpText_Rect.midright[1])
				EDITORHUDLAYER.blit(helpText, helpText_Rect)
		elif (hudView != 3):
			#helpText text is now equal to the "toggle this help menu" element in commandList
			helpText, helpText_Rect = game.createText((1100, helpMenu_drawy), 2, commandList[-1], game.ORANGE)
			helpText_Rect.midright = (game.SCREENWIDTH,helpText_Rect.midright[1])
			EDITORHUDLAYER.blit(helpText, helpText_Rect)
		game.screen.blit(ROOMLAYER, (0, 0))
		if (hudView):
			game.screen.blit(EDITORHUDLAYER, (0, 0))
		if (not clicked):
			game.screen.blit(game.CURSOR, pg.mouse.get_pos())
		else:
			game.screen.blit(game.CURSORCLICKED, pg.mouse.get_pos())
		pg.display.flip()
		game.clock.tick(game.FPS)

if (__name__ == "__main__"):
	game.setup()
	playerAsset = pg.image.load("assets/player.png").convert_alpha()
	playerAsset = modules.sheets.Spritesheet(playerAsset, 16, 16)
	game.loadTileSpritesheets()
	runEditor()