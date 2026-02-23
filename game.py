import random, sys, json, os, time, math
import pygame as pg
import modules
FPS = 30
SCREENWIDTH = 1280
SCREENHEIGHT = 720
#26.666666... x 15 tiles can be shown onscreen
#400 tile area btw
BGCOLOR = "black"
WHITE = (255,255,255)
BRIGHTYELLOW = (255,228,3)
BLUE = (7,5,129)
DARKBLUE = (7,5,35)
ORANGE = (255,126,71)
BASEIMGPATH = "assets/"
TILESIZE = 48
#from bottom
HUDMARGIN = 440
menuPressCooldown = 0
MENUPRESSTIME = 10
ITEMIDS = [
	"unknown item",
	"Ceremonial Sword",
	"Berry"
]
ITEMWEAPONS = {
	"sword":[1],
	"shield":[],
	"bow":[]
}
ITEMTYPEIDS = ["trinket", "weapon", "consumable","armor"]
DEBUGTEXT = "<qkuldo>you're not supposed to see this!</qkuldo>"
DIRECTION_IDS = {
"left":0,
"right":1,
"up":2,
"down":3
}

def loadImages(path):
	images = []
	aseExtension = ".ase"
	fullpath = BASEIMGPATH + path
	imageNames = []
	for img_name in os.listdir(fullpath):
		#code until continue block is for checking and ignoring .ase files from libresprite
		root, extension = os.path.splitext(fullpath + img_name)
		if (extension == aseExtension):
			continue
		images.append(pg.image.load(fullpath + img_name).convert_alpha())
		imageNames.append(img_name)
		#print(img_name + " loaded in")
	assert len(images) == len(imageNames), f"there are not enough names for images or there are not enough images for names. why? find out urself. also {len(images)} images {len(imageNames)} names.  </qkuldo>"
	return images, imageNames

def loadTileSpritesheets():
	global walltileSpritesheets, proptileSpritesheets
	tileImages,tileNames = loadImages("tiles/")
	walltileSpritesheets = []
	proptileSpritesheets = []
	wallbunchID, propbunchID = "walltile", "proptile"
	for tilebunch in tileImages:
		if (wallbunchID in tileNames[tileImages.index(tilebunch)]):
			walltileSpritesheets.append(modules.sheets.Spritesheet(tilebunch,16,16))
		elif (propbunchID in tileNames[tileImages.index(tilebunch)]):
			proptileSpritesheets.append(modules.sheets.Spritesheet(tilebunch,16,16))
		else:
			raise Exception("you BUFFOON!!!!! one of the tile bunches is named IMPROPERLY!!!!!! you have done a SLOPPY JOB!!!!! you *****************!!!!!!!!<qkuldo> sorry for its harsh language, the code's just letting you know that one of the tile sheets is not properly named. pls use walltile prefix for walls and proptile prefix for props. goodbye! </qkuldo>")
	#print("tile spritesheets successfully loaded")

def readJsonFile(path):
	#loads path file with json.load
	with open(path, "r") as file:
		#more rhyme!
		data = json.load(file)
		file.close()
	return data

def readAllJsonData():
	global DIALOGDATA, ITEMDATA, ROOMTILEDATA
	ROOMTILEDATA = readJsonFile("rooms.json")["rooms"]
	DIALOGDATA = readJsonFile("dialog.json")
	ITEMDATA = readJsonFile("itemData.json")
	assert len(ITEMDATA["ITEM TYPES"]) == len(ITEMDATA["ITEM ASSETS"]), "<qkuldo>there's an inequality in the itemData.json file between the item types and item assets.</qkuldo>"

def addItem(itemList, itemID, coordinates, assets):
	"""Appends item sprites to a list
	itemList - list sprite is appended to
	itemID - the index in ITEMIDS
	coordinates - where the coordinate attribute of the sprite will be
	assets - the list of all item assets
	"""
	itemList.append(modules.interactables.Sprite(assets[itemID], coordinates, 0, spriteScale=[TILESIZE,TILESIZE], hitboxScale=[TILESIZE,TILESIZE], customAttributes = {
					"itemID":itemID,
					"fromGroundOffset":0,
					"oscillate":0,
					"active":True
				}))

def goto_angle(velocity,angle):
	# Calculates a directional vector based on velocity and angle.`
	direction = pg.Vector2(0, velocity).rotate(-angle)
	return direction

def loadRoom(roomname,tileLayer,itemAssets, loadAll=True, frame=0):
	#loadRoom function needs only to be used when loading a new room
	alphabet = "abcdefghijklmnopqrstuvwxyz"
	wallLetters = "abde"
	animatedTiles = "f"
	extras = pg.image.load("assets/extras.png").convert_alpha()
	#all letters up until h are walls
	extras = modules.sheets.Spritesheet(extras,16,16)
	roomToLoad = roomname
	assert roomToLoad in ROOMTILEDATA, "<qkuldo>searching for a room that doesn't exist </qkuldo>"
	#iykyk
	valid_tiles = "#_-+=^@ "
	assert type(ROOMTILEDATA[roomToLoad]["wall set"]) == int, "<qkuldo> only integers can be used to assign wall tilesets </qkuldo>"
	assert type(ROOMTILEDATA[roomToLoad]["prop set"]) == int, "<qkuldo> only integers can be used to assign prop tilesets </qkuldo>"
	wallSet = ROOMTILEDATA[roomToLoad]["wall set"]
	propSet = ROOMTILEDATA[roomToLoad]["prop set"]
	hudTheme = tuple(ROOMTILEDATA[roomToLoad]["theme"])
	roomLayout = list(ROOMTILEDATA[roomToLoad].values())[3:18]
	#print(roomLayout)
	drawx, drawy = 0, 0
	playerSpawn = [0,0]
	collisionBoxes = []
	items = []
	for row in roomLayout:
		for column in row:
			if ((not column == " ") and (not column == "@")):
				if (column.isdigit()):
					tileLayer.blit(pg.transform.scale(proptileSpritesheets[propSet].load_frame(int(column)), (TILESIZE,TILESIZE)), (drawx, drawy))
				elif (column == "#"):
					tileLayer.blit(pg.transform.scale(walltileSpritesheets[wallSet].load_frame(0), (TILESIZE,TILESIZE)), (drawx, drawy))
					collisionBoxes.append(pg.Rect((drawx,drawy),(TILESIZE,TILESIZE)))
				elif (column == "_"):
					tileLayer.blit(pg.transform.scale(walltileSpritesheets[wallSet].load_frame(1), (TILESIZE,TILESIZE)), (drawx, drawy))
					collisionBoxes.append(pg.Rect((drawx,drawy),(TILESIZE,TILESIZE)))
				elif (column == "-"):
					tileLayer.blit(pg.transform.scale(walltileSpritesheets[wallSet].load_frame(2), (TILESIZE,TILESIZE)), (drawx, drawy))
					collisionBoxes.append(pg.Rect((drawx,drawy),(TILESIZE,TILESIZE)))
				elif (column == "+"):
					tileLayer.blit(pg.transform.scale(walltileSpritesheets[wallSet].load_frame(3), (TILESIZE,TILESIZE)), (drawx, drawy))
					collisionBoxes.append(pg.Rect((drawx,drawy),(TILESIZE,TILESIZE)))
				elif (column == "="):
					tileLayer.blit(pg.transform.scale(walltileSpritesheets[wallSet].load_frame(4), (TILESIZE,TILESIZE)), (drawx, drawy))
					collisionBoxes.append(pg.Rect((drawx,drawy),(TILESIZE,TILESIZE)))
				elif (column == "^"):
					tileLayer.blit(pg.transform.scale(walltileSpritesheets[wallSet].load_frame(5), (TILESIZE,TILESIZE)), (drawx, drawy))
					collisionBoxes.append(pg.Rect((drawx,drawy),(TILESIZE,TILESIZE)))
				elif (column in alphabet):
					if (column in animatedTiles):
						tileLayer.blit(pg.transform.scale(extras.load_frame(alphabet.index(column), frame), (TILESIZE,TILESIZE)), (drawx, drawy))
					else:
						tileLayer.blit(pg.transform.scale(extras.load_frame(alphabet.index(column)), (TILESIZE,TILESIZE)), (drawx, drawy))
					if (column in wallLetters):
						collisionBoxes.append(pg.Rect((drawx,drawy),(TILESIZE,TILESIZE)))
				else:
					tileLayer.blit(pg.transform.scale(MISSINGTEXTURE, (TILESIZE,TILESIZE)), (drawx, drawy))
			if (column == "@"):
				playerSpawn = [drawx,drawy]
			drawx += TILESIZE
		drawy += TILESIZE
		drawx = 0
	if (loadAll):
		for item in range(0, len(ROOMTILEDATA[roomToLoad]["items"])):
			itemID = ROOMTILEDATA[roomToLoad]["items"][item]
			itemCoordinate = findTilePixelLocation(ROOMTILEDATA[roomToLoad]["itemCoordinates"][item][0],ROOMTILEDATA[roomToLoad]["itemCoordinates"][item][1])
			if (len(itemAssets) >= item):
				addItem(items, itemID, itemCoordinate, itemAssets)
		currentRoomData = {
			"wall set index":wallSet,
			"prop set index":propSet,
			"hud theme":hudTheme,
			"playerSpawn":playerSpawn,
			"roomLayout":roomLayout,
			"collisionBoxes":collisionBoxes,
			"items":items,
		}
		return currentRoomData

def findTilePixelLocation(tileRow, tileColumn):
	#converts tile coordinates to pixel coordinates
	#tile = roomLayout[str(tileRow)][tileColumn]
	tileX = tileRow*TILESIZE
	tileY = tileColumn*TILESIZE
	return (tileX,tileY)

def findPixelTileLocation(x, y):
	#converts pixel coordinates to tile coordinates
	pixelX = int(x//TILESIZE)
	pixelY = int(y//TILESIZE)
	return (pixelX,pixelY)

def terminate():
	pg.quit()
	sys.exit()

def setup():
	global screen,clock,MISSINGTEXTURE,SFX,BIGDISPLAYFONT,CURSOR, CURSORCLICKED, SMALLDISPLAYFONT, ICONS, EQUIPPED_SELECTOR, TARGET, TARGETRECT, LOCKEDTARGET, MEDIUMDISPLAYFONT, HPBARDESIGN
	pg.init()
	pg.mixer.init()
	clock = pg.time.Clock()
	screen = pg.display.set_mode((SCREENWIDTH,SCREENHEIGHT))
	MISSINGTEXTURE = pg.image.load("assets/missing.png").convert_alpha()
	EQUIPPED_SELECTOR = pg.image.load("assets/equippedSelector.png").convert_alpha()
	SFX = {}
	SFX_PATH = "sounds/sfx/"
	for SFX_name in os.listdir(SFX_PATH):
		SFX[os.path.splitext(SFX_name)[0]] = pg.mixer.Sound(SFX_PATH + SFX_name)
		SFX[os.path.splitext(SFX_name)[0]].set_volume(0.3)
	BIGDISPLAYFONT = pg.font.Font("font/PixelifySans-Bold.ttf", 30)
	SMALLDISPLAYFONT = pg.font.Font("font/PixelifySans-Bold.ttf", 15)
	MEDIUMDISPLAYFONT = pg.font.Font("font/PixelifySans-Bold.ttf", 25)
	CURSOR = pg.image.load("assets/cursor.png").convert_alpha()
	CURSORCLICKED = pg.image.load("assets/cursorClicked.png").convert_alpha()
	CURSOR = pg.transform.scale(CURSOR, (TILESIZE,TILESIZE))
	CURSORCLICKED = pg.transform.scale(CURSORCLICKED, (TILESIZE,TILESIZE))
	ICONS = pg.image.load("assets/icons.png").convert_alpha()
	ICONS = modules.sheets.Spritesheet(ICONS, 16, 16)
	TARGET = pg.image.load("assets/target.png").convert_alpha()
	TARGET = pg.transform.scale(TARGET, (TILESIZE,TILESIZE))
	LOCKEDTARGET = pg.image.load("assets/locked_target.png").convert_alpha()
	LOCKEDTARGET = pg.transform.scale(LOCKEDTARGET, (TILESIZE,TILESIZE))
	HPBARDESIGN = pg.image.load("assets/healthbarDesign.png")
	HPBARDESIGN = pg.transform.scale(HPBARDESIGN, (TILESIZE*2, TILESIZE*2))
	TARGETRECT = TARGET.get_rect()
	pg.mouse.set_visible(False)

def initDrawLayer():
	layer = pg.Surface((SCREENWIDTH,SCREENHEIGHT),pg.SRCALPHA).convert_alpha()
	return layer

def clearLayer(layer):
	#use this for tilelayer before loading a new room after exiting a previous room
	layer.fill((0,0,0,0))

def showInventory(HUDLAYER, Player, itemAssets, loadAll = True, mouse_collide_index = -1):
	drawx, drawy = 500, 450
	ITEMTILESIZE = 48
	ITEMHITBOXES = []
	INVENTORYITEMIDS = []
	ITEM_AMOUNT_TEXT, ITEM_AMOUNT_TEXT_RECT = createText((0,0), text = DEBUGTEXT)
	weaponSlots = Player.customAttributes["stats"]["equipment"]["WEAPONS"]
	for item in Player.customAttributes["inventory"]:
		itemAmount = Player.customAttributes["inventory"][item]
		itemIndex = list(Player.customAttributes["inventory"].keys()).index(item)
		if (0 <= item < len(ITEMIDS)):
			if (mouse_collide_index == itemIndex):
				HUDLAYER.blit(pg.transform.scale(itemAssets[item], (ITEMTILESIZE*1.5,ITEMTILESIZE*1.5)), (drawx-ITEMTILESIZE/2,drawy))
			else:
				HUDLAYER.blit(pg.transform.scale(itemAssets[item], (ITEMTILESIZE,ITEMTILESIZE)), (drawx,drawy))
			INVENTORYITEMIDS.append(ITEMIDS[item])
		else:
			if (mouse_collide_index == itemIndex):
				HUDLAYER.blit(pg.transform.scale(itemAssets[0], (ITEMTILESIZE*1.5,ITEMTILESIZE*1.5)), (drawx-ITEMTILESIZE/2,drawy))
			else:
				HUDLAYER.blit(pg.transform.scale(itemAssets[0], (ITEMTILESIZE,ITEMTILESIZE)), (drawx,drawy))
			INVENTORYITEMIDS.append(ITEMIDS[0])
		if (item in weaponSlots.values()):
			if (mouse_collide_index == itemIndex):
				HUDLAYER.blit(pg.transform.scale(EQUIPPED_SELECTOR, (ITEMTILESIZE*1.5,ITEMTILESIZE*1.5)), (drawx-ITEMTILESIZE/2,drawy))
			else:
				HUDLAYER.blit(pg.transform.scale(EQUIPPED_SELECTOR, (ITEMTILESIZE,ITEMTILESIZE)), (drawx,drawy))
		if (itemAmount > 1):
			if (mouse_collide_index == itemIndex):
				ITEM_AMOUNT_TEXT, ITEM_AMOUNT_TEXT_RECT = createText((drawx+ITEMTILESIZE/2+10,drawy+ITEMTILESIZE+10), text = f"{itemAmount}", font=0)
				HUDLAYER.blit(ITEM_AMOUNT_TEXT, ITEM_AMOUNT_TEXT_RECT)
			else:
				ITEM_AMOUNT_TEXT, ITEM_AMOUNT_TEXT_RECT = createText((drawx+ITEMTILESIZE-10,drawy+ITEMTILESIZE-10), text = f"{itemAmount}", font=0)
				HUDLAYER.blit(ITEM_AMOUNT_TEXT, ITEM_AMOUNT_TEXT_RECT)
		if (loadAll):
			ITEMHITBOXES.append(pg.Rect(drawx,drawy, ITEMTILESIZE, ITEMTILESIZE))
		if (drawx < 788):
			drawx += ITEMTILESIZE
		else:
			drawx = 500
			drawy += ITEMTILESIZE
	if (loadAll):
		return ITEMHITBOXES, INVENTORYITEMIDS

def loadHudLayer(HUDLAYER,blackHudArea,currentRoomData,playerPortrait):
	HUDLAYER.fill((0,0,0,0))
	pg.draw.rect(HUDLAYER,(0,0,0),blackHudArea)
	pg.draw.line(HUDLAYER,currentRoomData["hud theme"],(0,HUDMARGIN),(SCREENWIDTH,HUDMARGIN),5)
	HUDLAYER.blit(playerPortrait, (10,480))

def hitboxInbound(rect):
	"""checks if given rect is outside of the screen borders
	returns False if not out of bounds, returns True otherwise
	"""
	if (rect.midbottom[1] < SCREENHEIGHT and rect.midtop[1] > 0 and rect.midleft[0] > 0 and rect.midright[0] < SCREENWIDTH):
		return True
	else:
		return False

def complexMove(Sprite, movement_line,operation,currentRoomData):
	collideChecker = Sprite.siMove(movement_line,operation)
	if (collideChecker.collidelist(currentRoomData["collisionBoxes"]) == -1 and hitboxInbound(collideChecker)):
		Sprite.move(movement_line,operation)

def animateLoop(Sprite, startFrame, endFrame):
	#loops animation on certain start and end frames
	if (Sprite.customAttributes["currentFrame"] > endFrame or Sprite.customAttributes["currentFrame"] < startFrame):
		Sprite.customAttributes["currentFrame"] = startFrame
	if (Sprite.customAttributes["currentFrame"] < endFrame):
		Sprite.customAttributes["currentFrame"] += 1
	else:
		Sprite.customAttributes["currentFrame"] = startFrame

def createText(center, font = 0, text = "hello there", color=(255,255,255)):
	if (font == 0):
		textSurface = BIGDISPLAYFONT.render(text, False, color)
	elif (font == 1):
		textSurface = SMALLDISPLAYFONT.render(text, False, color)
	elif (font == 2):
		textSurface = MEDIUMDISPLAYFONT.render(text, False, color)
	textRect = textSurface.get_rect()
	textRect.center = center
	return (textSurface, textRect)

def face_target(person_pos,targetpos,face=True):
	out_dir = (targetpos[0]-person_pos[0],targetpos[1]-person_pos[1])
	length = math.hypot(*out_dir)
	if (length == 0.0):
		out_dir = (0,1)
	else:
		out_dir = (out_dir[0]/length, out_dir[1]/length)
	if (face):
		angle = math.degrees(math.atan2(-out_dir[0],-out_dir[1]))
	else:
		angle = math.degrees(math.atan2(out_dir[0],out_dir[1]))
	return angle

def goto_angleAndSetDir(Sprite, speed_multiplier=3, angle=0, targetPos=(SCREENWIDTH/2, SCREENHEIGHT/2)):
	#goto_angle that also sets the "facingDirection" custom attribute of sprite
	#returns the initial goto_angle call
	directional_vector = -goto_angle(Sprite.speed*speed_multiplier, angle)
	distance_fromTarget = (Sprite.coordinates[0]-targetPos[0], Sprite.coordinates[1]-targetPos[1])
	assert "facingDirection" in Sprite.customAttributes.keys(), "<qkuldo>Sprite incompatible with function due to the lack of the facingDirection custom attribute. Use goto_angle instead if this is intended.</qkuldo>"
	if (abs(distance_fromTarget[0]) > abs(distance_fromTarget[1])):
		if (abs(distance_fromTarget[0]) == distance_fromTarget[0]):
			Sprite.customAttributes["facingDirection"] = DIRECTION_IDS["left"]
		elif (abs(distance_fromTarget[0]) != distance_fromTarget[0]):
			Sprite.customAttributes["facingDirection"] = DIRECTION_IDS["right"]
	else:
		if (abs(distance_fromTarget[1]) == distance_fromTarget[1]):
			Sprite.customAttributes["facingDirection"] = DIRECTION_IDS["up"]
		elif (abs(distance_fromTarget[1]) != distance_fromTarget[1]):
			Sprite.customAttributes["facingDirection"] = DIRECTION_IDS["down"]
	return directional_vector

def game():
	#find and make assets
	itemAssets = ITEMDATA["ITEM ASSETS"]
	for assetPath in itemAssets:
		itemAssets[itemAssets.index(assetPath)] = pg.image.load(assetPath).convert_alpha()
	playerAsset = pg.image.load("assets/player.png").convert_alpha()
	playerAsset = modules.sheets.Spritesheet(playerAsset, 16, 16)
	playerPortrait = pg.image.load("assets/playerPortrait.png").convert()
	playerPortrait = pg.transform.scale(playerPortrait,(128,128))
	hand = pg.transform.scale(pg.image.load("assets/hand.png"), (8, 8)).convert()
	specialItem = pg.Surface((TILESIZE,TILESIZE)).convert_alpha()
	specialItemRect = specialItem.get_rect()
	#define screen layers
	TILELAYER = initDrawLayer()
	HUDLAYER = initDrawLayer()
	SPRITELAYER = initDrawLayer()
	INFOLAYER = initDrawLayer()
	BASELAYER = initDrawLayer()
	CAMERALAYER = initDrawLayer()
	INVENTORY_DESCLAYER = initDrawLayer()
	DEBUGLAYER = initDrawLayer()
	clearLayer(TILELAYER)
	current_room = "spawnSpot"
	currentRoomData = loadRoom(current_room,TILELAYER,itemAssets)
	#directionalFrames custom attribute is written as a list for compatibility with DIRECTION_IDS constant dict
	Player = modules.interactables.Sprite(playerAsset,currentRoomData["playerSpawn"],5,spriteScale = (TILESIZE,TILESIZE), hitboxScale = (TILESIZE-24,TILESIZE-18), hitboxLocation = (currentRoomData["playerSpawn"][0]+6,currentRoomData["playerSpawn"][1]+18),customAttributes = {
			"currentFrame":0,
			"frameRow":0,
			"facingDirection":DIRECTION_IDS["left"],
			"directionalFrames":[{"startFrame":0, "endFrame":2}, {"startFrame":3, "endFrame":5}, {"startFrame":6, "endFrame":8}, {"startFrame":9, "endFrame":11}],
			"inventory":{},
			"target pos":[SCREENWIDTH/2, SCREENHEIGHT/2],
			"stats":{
				"health":20,
				"max health":20,
				"defense":3,
				"equipment":{
					"WEAPONS":{
						"sword":None,
						"shield":None,
						"bow":None
					},
					"OTHER EQUIPMENT":[]
				}
			},
			"visible":True,
			"got hit":False
		})
	playerSword = modules.interactables.Sprite(pg.transform.rotate(pg.transform.scale(itemAssets[1], (TILESIZE*2,TILESIZE*2)), 45), Player.hitbox.center, 0, spriteScale = (TILESIZE, TILESIZE), hitboxScale = (TILESIZE, TILESIZE), hitboxLocation = Player.hitbox.center, customAttributes = {"visible":False, "moving":False})
	blackHudArea = pg.Rect((0,HUDMARGIN),(SCREENWIDTH,HUDMARGIN))
	drawHud = False
	menuPressCooldown = 0
	running = True
	#define custom events
	ANIMATIONSWITCHEVENT = pg.event.custom_type()
	SPECIALPICKUPSTAY = pg.event.custom_type()
	START_FADEOUT = pg.event.custom_type()
	ENDSWORD_VISIBILITY = pg.event.custom_type()
	ENDSWORD_PLAYERMOVEMENT = pg.event.custom_type()
	#player attack variables
	ATTACK_QTE_END = pg.event.custom_type()
	ATTACK_QTE_START = pg.event.custom_type()
	attack_qte_active = False
	attack_qte_success = None
	attack_qte_ongoing_attack = False
	ATTACK_BUTTON_COOLDOWN = pg.event.custom_type()
	on_attack_button_cooldown = False
	PLAYER_HITSTOP = pg.event.custom_type()
	#------------------------------
	pg.time.set_timer(ANIMATIONSWITCHEVENT,180)
	#define other variables
	debugMode = 0
	specialPickupVisible = False
	specialPickupAlpha = 255
	specialPickupFade = False
	timedRect_fillRate = 1
	timedRect_fill = False
	ZOOM_LEVEL = 2
	SIMOVE_SUB = -1
	SIMOVE_ADD = 1
	SIMOVE_Y = 1
	SIMOVE_X = 0
	clicked = False
	INVENTORYBUTTONS = []
	INVENTORY_ITEMS = []
	SPECIAL_ITEMGET_FLY = 3
	special_itemGet_addY = 0
	ITEMTYPE_XMARGIN = 25
	ITEMTYPE_YMARGIN = 10
	HEALTHBAR_COORDINATES = (85,55)
	target_angle = 0
	roomFrame = 0
	roomAccumulateFrames = 0
	#rect creation
	timedRect = pg.Rect(0, 0, 0, TILESIZE//5)
	timedRectBG = pg.Rect(0, 0, 30*timedRect_fillRate, TILESIZE//5)
	playerHealthRect = pg.Rect(30, 20, 10*Player.customAttributes["stats"]["health"], TILESIZE//2)
	playerMaxHealthRect = pg.Rect(30, 20, 10*Player.customAttributes["stats"]["max health"], TILESIZE//2)
	#make text
	#testText, textTestRect = createText((SCREENWIDTH/2,SCREENHEIGHT/2))
	specialPickupText, specialPickupTextRect = createText((0,0), text = DEBUGTEXT)
	INVENTORY_ITEM_TEXT, INVENTORY_ITEM_TEXT_RECT = createText((520,500), text = DEBUGTEXT)
	WEAPON_EQUIPPED_TEXT, WEAPON_EQUIPPED_TEXT_RECT = createText((300, 650), text = "EQUIPPED IN WEAPON SLOT", color=BRIGHTYELLOW, font = 1)
	test_text, test_text_rect = createText((50, 20), text = str(debugMode), color=BRIGHTYELLOW)
	while running:
		playerHealthRect = pg.Rect(HEALTHBAR_COORDINATES, (10*Player.customAttributes["stats"]["health"], TILESIZE//2))
		playerMaxHealthRect = pg.Rect(HEALTHBAR_COORDINATES, (10*Player.customAttributes["stats"]["health"], TILESIZE//2))
		healthString = str(Player.customAttributes["stats"]["health"])+"/"+str(Player.customAttributes["stats"]["max health"])
		healthText, healthTextRect = createText((playerHealthRect.midleft[0]+45, playerHealthRect.midleft[1]), text = healthString, color = BRIGHTYELLOW, font = 2)
		#below line is pretty trippy ngl
		#Player.angle = face_target(Player.coordinates, (SCREENWIDTH/2,SCREENHEIGHT/2))
		if (debugMode == 1):
			test_text, test_text_rect = createText((200, 20), text = current_room + " MODE " + str(debugMode), color=BRIGHTYELLOW)
		else:
			test_text, test_text_rect = createText((100, 20), text = "MODE "+str(debugMode), color=BRIGHTYELLOW)
		timedRect.bottomleft = Player.hitbox.topright
		timedRectBG.bottomleft = Player.hitbox.topright
		mouseRect = pg.Rect(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1], TILESIZE, TILESIZE)
		switchFrame = False
		current_time = pg.time.get_ticks()
		BASELAYER.fill(BGCOLOR)
		screen.fill(BGCOLOR)
		clearLayer(SPRITELAYER)
		clearLayer(CAMERALAYER)
		clearLayer(HUDLAYER)
		clearLayer(INVENTORY_DESCLAYER)
		clearLayer(INFOLAYER)
		clearLayer(TILELAYER)
		clearLayer(DEBUGLAYER)
		keys = pg.key.get_pressed()
		for event in pg.event.get():
			if (event.type == pg.QUIT):
				terminate()
			elif (event.type == ANIMATIONSWITCHEVENT):
				switchFrame = True
			elif (event.type == SPECIALPICKUPSTAY):
				specialPickupVisible = not specialPickupVisible
				pg.time.set_timer(SPECIALPICKUPSTAY, 0)
				specialPickupAlpha = 255
				specialPickupText, specialPickupTextRect = createText((0,0), text = "<qkuldo>you're not supposed to see this!</qkuldo>")
				specialPickupFade = False
				special_itemGet_addY = 0
			elif (event.type == START_FADEOUT):
				pg.time.set_timer(START_FADEOUT, 0)
				specialPickupFade = True
				SFX["itemCollect"].play()
			elif (event.type == pg.MOUSEBUTTONDOWN):
				clicked = True
			elif (event.type == pg.MOUSEBUTTONUP):
				clicked = False
			elif (event.type == ATTACK_BUTTON_COOLDOWN):
				on_attack_button_cooldown = False
			elif (event.type == ATTACK_QTE_START):
				#print(timedRect.width)
				timedRect = pg.Rect(0, 0, 0, TILESIZE//5)
				timedRect_fill = False
				if (debugMode == 1):
					test_text, test_text_rect = createText((100, 20), text = "click", color=BRIGHTYELLOW)
				attack_qte_active = True
				pg.time.set_timer(ATTACK_QTE_END, 1000, 1)
			elif (event.type == ATTACK_QTE_END):
				if (attack_qte_success):
					if (debugMode == 2):
						test_text, test_text_rect = createText((100, 20), text = "success", color=BRIGHTYELLOW)
					#print("success")
					SFX["slash"].play()
					pg.time.set_timer(ENDSWORD_VISIBILITY, 500, 1)
					pg.time.set_timer(ENDSWORD_PLAYERMOVEMENT, 100, 1)
					playerSword.customAttributes["visible"] = True
					playerSword.customAttributes["moving"] = True
				else:
					#print("fail")
					if (debugMode == 2):
						test_text, test_text_rect = createText((100, 20), text = "fail", color=BRIGHTYELLOW)
				attack_qte_success = False
				attack_qte_ongoing_attack = False
				attack_qte_active = False
			elif (event.type == ENDSWORD_VISIBILITY):
				playerSword.customAttributes["visible"] = False
			elif (event.type == ENDSWORD_PLAYERMOVEMENT):
				playerSword.customAttributes["moving"] = False
			elif (event.type == PLAYER_HITSTOP):
				Player.customAttributes["got hit"] = False
		if (keys[pg.K_ESCAPE] and menuPressCooldown <= 0 and (not specialPickupVisible) and (not attack_qte_ongoing_attack) and (not playerSword.customAttributes["visible"])):
			drawHud = not drawHud
			menuPressCooldown = MENUPRESSTIME
			#it is intentional that the "menu close" sound plays when opening the menu, and vice versa
			if (drawHud):
				SFX["closeMenu"].play()
				INVENTORYBUTTONS, INVENTORY_ITEMS = showInventory(HUDLAYER,Player, itemAssets, loadAll=True)
			else:
				SFX["openMenu"].play()
		if (drawHud):
			MOUSE_HOVER_INVENTORY_INDEX = mouseRect.collidelist(INVENTORYBUTTONS)
			loadHudLayer(HUDLAYER,blackHudArea,currentRoomData, playerPortrait)
			showInventory(HUDLAYER,Player, itemAssets, loadAll=False, mouse_collide_index=MOUSE_HOVER_INVENTORY_INDEX)
		for item in currentRoomData["items"]:
			if (item.customAttributes["active"]):
				item.update()
				if (switchFrame and item.customAttributes["oscillate"] == 0):
					item.customAttributes["fromGroundOffset"] -= 2
					if (abs(item.customAttributes["fromGroundOffset"]) >= 10):
						item.customAttributes["oscillate"] = 1
				elif (switchFrame and item.customAttributes["oscillate"] == 1):
					item.customAttributes["fromGroundOffset"] += 2
					if (item.customAttributes["fromGroundOffset"] >= 0):
						item.customAttributes["oscillate"] = 0
				item.draw(0, SPRITELAYER, (0,item.customAttributes["fromGroundOffset"]))
				if (item.hitbox.colliderect(Player.hitbox)):
					item.customAttributes["active"] = False
					if (item.customAttributes["itemID"] in Player.customAttributes["inventory"]):
						Player.customAttributes["inventory"][item.customAttributes["itemID"]] += 1
					else:
						Player.customAttributes["inventory"][item.customAttributes["itemID"]] = 1
					if (ITEMTYPEIDS[item.customAttributes["itemID"]] in ("weapon", "armor")):
						SFX["special_ItemCollect"].play()
						itemText = ITEMIDS[item.customAttributes["itemID"]]
						specialPickupText, specialPickupTextRect = createText((0,0), text = f"You got a {itemText}!", color=BRIGHTYELLOW)
						specialPickupVisible = True
						pg.time.set_timer(SPECIALPICKUPSTAY, 2700)
						pg.time.set_timer(START_FADEOUT,1890)
						specialItem.fill((0,0,0,0))
						specialItem = pg.transform.scale(item.asset, (TILESIZE, TILESIZE))
					else:
						SFX["itemCollect"].play()
		if (keys[pg.K_p] and menuPressCooldown <= 0):
			#pepug menu
			debugMode += 1
			if (debugMode > 3):
				debugMode = 0
			menuPressCooldown = MENUPRESSTIME
		if ((not drawHud) and (not specialPickupVisible) and (not playerSword.customAttributes["visible"])):
			if (not attack_qte_ongoing_attack):
				if (keys[pg.K_w] or keys[pg.K_UP]):
					complexMove(Player,SIMOVE_Y,SIMOVE_SUB,currentRoomData)
					Player.customAttributes["facingDirection"] = DIRECTION_IDS["up"]
				elif (keys[pg.K_s] or keys[pg.K_DOWN]):
					complexMove(Player,SIMOVE_Y,SIMOVE_ADD,currentRoomData)
					Player.customAttributes["facingDirection"] = DIRECTION_IDS["down"]
				if (keys[pg.K_a] or keys[pg.K_LEFT]):
					complexMove(Player,SIMOVE_X,SIMOVE_SUB,currentRoomData)
					Player.customAttributes["facingDirection"] = DIRECTION_IDS["left"]
				elif (keys[pg.K_d] or keys[pg.K_RIGHT]):
					complexMove(Player,SIMOVE_X,SIMOVE_ADD,currentRoomData)
					Player.customAttributes["facingDirection"] = DIRECTION_IDS["right"]
				if (keys[pg.K_LSHIFT]):
					goto_angleAndSetDir(Player, angle=playerSword.angle, targetPos = Player.customAttributes["target pos"])
					target_angle += 4
					TARGETRECT = pg.transform.rotate(TARGET, target_angle).get_rect()
					TARGETRECT.center = Player.customAttributes["target pos"]
					INFOLAYER.blit(pg.transform.rotate(TARGET, target_angle), TARGETRECT)
			if (keys[pg.K_LSHIFT] and keys[pg.K_z] and (not attack_qte_ongoing_attack) and Player.customAttributes["stats"]["equipment"]["WEAPONS"]["sword"] != None):
				attack_qte_ongoing_attack = True
				attack_qte_success = False
				timedRect_fill = True
				pg.time.set_timer(ATTACK_QTE_START, 1000, 1)
			if (keys[pg.K_x] and attack_qte_ongoing_attack and attack_qte_active):
				attack_qte_success = True
				on_attack_button_cooldown = True
				pg.time.set_timer(ATTACK_QTE_START, 0)
				pg.time.set_timer(ATTACK_QTE_END, 1, 1)
				pg.time.set_timer(ATTACK_BUTTON_COOLDOWN, 800, 1)
				playerSword.angle = face_target(Player.hitbox.center, Player.customAttributes["target pos"])
			elif (keys[pg.K_x] and attack_qte_ongoing_attack and not attack_qte_active):
				attack_qte_success = False
				on_attack_button_cooldown = True
				timedRect_fill = False
				timedRect = pg.Rect(0, 0, 0, TILESIZE//5)
				pg.time.set_timer(ATTACK_QTE_START, 0)
				pg.time.set_timer(ATTACK_QTE_END, 1, 1)
				pg.time.set_timer(ATTACK_BUTTON_COOLDOWN, 800, 1)
		playerSword.hitbox.center = Player.hitbox.center
		playerSword.coordinates = (playerSword.hitbox.x-goto_angle(50,playerSword.angle)[0], playerSword.hitbox.y-goto_angle(50,playerSword.angle)[1])
		if (switchFrame and (not specialPickupVisible)):
			if (Player.customAttributes["got hit"]):
				Player.customAttributes["visible"] = not Player.customAttributes["visible"]
				Player.customAttributes["currentFrame"] = 1
				Player.customAttributes["frameRow"] = 1
			else:
				Player.customAttributes["visible"] = True
				animateLoop(Player, Player.customAttributes["directionalFrames"][Player.customAttributes["facingDirection"]]["startFrame"], Player.customAttributes["directionalFrames"][Player.customAttributes["facingDirection"]]["endFrame"])
				Player.customAttributes["frameRow"] = 0
			roomAccumulateFrames += 1
			if (roomAccumulateFrames == 2):
				if (roomFrame == 0):
					roomFrame = 1
				else:
					roomFrame = 0
				roomAccumulateFrames = 0
		elif (specialPickupVisible):
			Player.customAttributes["currentFrame"] = 0
			Player.customAttributes["frameRow"] = 1
		loadRoom(current_room,TILELAYER,itemAssets,False,roomFrame)
		if (specialPickupVisible and specialPickupFade):
			specialPickupAlpha -= 15
			specialPickupText.set_alpha(specialPickupAlpha)
			specialItem.set_alpha(specialPickupAlpha)
		if (not specialPickupFade):
			specialItemRect.midbottom = [Player.hitbox.midtop[0], Player.hitbox.midtop[1]-25]
			specialPickupTextRect.midbottom = [Player.hitbox.midtop[0], Player.hitbox.midtop[1]-70]
		else:
			special_itemGet_addY += SPECIAL_ITEMGET_FLY
			specialItemRect.midbottom = [Player.hitbox.midtop[0], Player.hitbox.midtop[1]-25-special_itemGet_addY]
			specialPickupTextRect.midbottom = [Player.hitbox.midtop[0], Player.hitbox.midtop[1]-70-special_itemGet_addY]
		Player.update(rectOperation = (Player.coordinates[0]+12,Player.coordinates[1]+18))
		if (Player.customAttributes["visible"]):
			if (not specialPickupVisible):
				if ((not Player.customAttributes["got hit"]) or (Player.customAttributes["got hit"] and Player.customAttributes["facingDirection"] == DIRECTION_IDS["right"])):
					Player.draw(Player.customAttributes["currentFrame"], SPRITELAYER, frameRow = Player.customAttributes["frameRow"])
				else:
					Player.draw(Player.customAttributes["currentFrame"], SPRITELAYER, frameRow = Player.customAttributes["frameRow"], flipX=True)
				#if (playerSword.customAttributes["visible"]):
				#	Player.draw(Player.customAttributes["currentFrame"], SPRITELAYER, offset = (-goto_angle(50, playerSword.angle)[0],-goto_angle(50, playerSword.angle)[1]))
				#else:
				#	Player.draw(Player.customAttributes["currentFrame"], SPRITELAYER)
			else:
				Player.draw(Player.customAttributes["currentFrame"], SPRITELAYER, offset = (-20, -10), frameRow = Player.customAttributes["frameRow"])
		if (playerSword.customAttributes["visible"]):
			if (playerSword.customAttributes["moving"]):
				directional_vector = goto_angleAndSetDir(Player, angle=playerSword.angle, targetPos = Player.customAttributes["target pos"])
				collisionTestDummy = Player.createDummy()
				collisionTestDummy.x += directional_vector[0]
				collisionTestDummy.y += directional_vector[1]
				if (collisionTestDummy.collidelist(currentRoomData["collisionBoxes"]) == -1 and hitboxInbound(collisionTestDummy)):
					Player.coordinates[0] += directional_vector[0]
					Player.coordinates[1] += directional_vector[1]
			playerSword.draw(0, SPRITELAYER)
			SPRITELAYER.blit(pg.transform.rotate(hand, playerSword.angle), (Player.hitbox.center[0]-goto_angle(40,playerSword.angle)[0], Player.hitbox.center[1]-goto_angle(40,playerSword.angle)[1]))
		if (attack_qte_ongoing_attack or playerSword.customAttributes["visible"]):
			target_angle += 2
			TARGETRECT = pg.transform.rotate(TARGET, target_angle).get_rect()
			TARGETRECT.center = Player.customAttributes["target pos"]
			INFOLAYER.blit(pg.transform.rotate(LOCKEDTARGET, target_angle), TARGETRECT)
		if (specialPickupVisible):
			SPRITELAYER.blit(specialPickupText, specialPickupTextRect)
			SPRITELAYER.blit(specialItem, specialItemRect)
		if (not debugMode):
			pg.draw.rect(INFOLAYER, DARKBLUE, playerMaxHealthRect)
			pg.draw.rect(INFOLAYER, BLUE, playerHealthRect)
			pg.draw.rect(INFOLAYER, DARKBLUE, playerMaxHealthRect.inflate(5,5),5)
			INFOLAYER.blit(healthText, healthTextRect)
			INFOLAYER.blit(HPBARDESIGN, (0,20))
		#SPRITELAYER.blit(testText, textTestRect)
		if ((not specialPickupVisible) and drawHud and len(Player.customAttributes["inventory"]) > 0):
			#loops through INVENTORYBUTTONS for a rect that passes colliderect check with mouse position
			MOUSE_HOVER_ID = ITEMIDS.index(INVENTORY_ITEMS[mouseRect.collidelist(INVENTORYBUTTONS)])
			if (MOUSE_HOVER_INVENTORY_INDEX != -1):
				#creates item header text
				if (ITEMTYPEIDS[ITEMDATA["ITEM TYPES"][ITEMIDS[MOUSE_HOVER_ID]]] in ("weapon", "armor")):
					INVENTORY_ITEM_TEXT, INVENTORY_ITEM_TEXT_RECT = createText((300,480), text = INVENTORY_ITEMS[MOUSE_HOVER_INVENTORY_INDEX], color=BRIGHTYELLOW)
				else:
					INVENTORY_ITEM_TEXT, INVENTORY_ITEM_TEXT_RECT = createText((300,480), text = INVENTORY_ITEMS[MOUSE_HOVER_INVENTORY_INDEX], color=WHITE)
				itemType = ITEMTYPEIDS.index(ITEMTYPEIDS[ITEMDATA["ITEM TYPES"][INVENTORY_ITEMS[MOUSE_HOVER_INVENTORY_INDEX]]])
				#blit type icon and item name
				HUDLAYER.blit(pg.transform.scale(ICONS.load_frame(itemType), (TILESIZE/2, TILESIZE/2)), (INVENTORY_ITEM_TEXT_RECT.topleft[0]-ITEMTYPE_XMARGIN, INVENTORY_ITEM_TEXT_RECT.midleft[1]-ITEMTYPE_YMARGIN))
				HUDLAYER.blit(INVENTORY_ITEM_TEXT, INVENTORY_ITEM_TEXT_RECT)
				#display description
				if (type(DIALOGDATA["ITEM DESCRIPTIONS"][MOUSE_HOVER_ID]) != list):
					INVENTORY_ITEM_DESCRIPTION, INVENTORY_ITEM_DESC_RECT = createText((300,520), font=1, text = DIALOGDATA["ITEM DESCRIPTIONS"][ITEMIDS.index(INVENTORY_ITEMS[MOUSE_HOVER_INVENTORY_INDEX])])
					INVENTORY_DESCLAYER.blit(INVENTORY_ITEM_DESCRIPTION, INVENTORY_ITEM_DESC_RECT)
				else:
					starty = 520
					for line in DIALOGDATA["ITEM DESCRIPTIONS"][MOUSE_HOVER_ID]:
						INVENTORY_ITEM_DESCRIPTION, INVENTORY_ITEM_DESC_RECT = createText((300,starty), font=1, text = line)
						INVENTORY_DESCLAYER.blit(INVENTORY_ITEM_DESCRIPTION, INVENTORY_ITEM_DESC_RECT)
						starty += 15
				#display equipped text if item is equipped
				if (MOUSE_HOVER_ID in Player.customAttributes["stats"]["equipment"]["WEAPONS"].values()):
					HUDLAYER.blit(WEAPON_EQUIPPED_TEXT, WEAPON_EQUIPPED_TEXT_RECT)
				#equip weapon
				if (ITEMTYPEIDS[itemType] == "weapon" and clicked and not MOUSE_HOVER_ID in Player.customAttributes["stats"]["equipment"]["WEAPONS"].values()):
					if (MOUSE_HOVER_ID in ITEMWEAPONS["sword"]):
						Player.customAttributes["stats"]["equipment"]["WEAPONS"]["sword"] = MOUSE_HOVER_ID
					elif (MOUSE_HOVER_ID in ITEMWEAPONS["shield"]):
						Player.customAttributes["stats"]["equipment"]["WEAPONS"]["shield"] = MOUSE_HOVER_ID
					elif (MOUSE_HOVER_ID in ITEMWEAPONS["bow"]):
						Player.customAttributes["stats"]["equipment"]["WEAPONS"]["bow"] = MOUSE_HOVER_ID
					else:
						raise Exception("<qkuldo>the item is classified as a weapon but is not in the list of weapons</qkuldo>")
					SFX["equipItem"].play()
			HUDLAYER.blit(INVENTORY_DESCLAYER, (0, 0))
		else:
			INVENTORY_ITEM_TEXT, INVENTORY_ITEM_TEXT_RECT = createText((500,520), text = DEBUGTEXT)
		if (timedRect_fill):
			timedRect.width += timedRect_fillRate
			pg.draw.rect(INFOLAYER, DARKBLUE, timedRectBG)
			pg.draw.rect(INFOLAYER, BLUE, timedRectBG,3)
		#draw circle function below is for testing purposes
		pg.draw.rect(INFOLAYER, BRIGHTYELLOW, timedRect)
		if (debugMode > 0):
			DEBUGLAYER.blit(test_text, test_text_rect)
			if (debugMode == 2):
				pg.draw.circle(DEBUGLAYER, BRIGHTYELLOW, (SCREENWIDTH/2,SCREENHEIGHT/2), 5)
				pg.draw.rect(DEBUGLAYER,WHITE,Player.hitbox)
			elif (debugMode == 3):
				if (keys[pg.K_f]):
					Player.customAttributes["stats"]["health"] -= 1
				if (keys[pg.K_g]):
					Player.customAttributes["stats"]["health"] += 1
				if (keys[pg.K_h] and menuPressCooldown <= 0):
					menuPressCooldown = MENUPRESSTIME
					Player.customAttributes["got hit"] = True
					pg.time.set_timer(PLAYER_HITSTOP, 1000)
		if (((not drawHud) or (drawHud and Player.hitbox.center[1] < 420))):
			BASELAYER.blit(TILELAYER,(0,0))
			BASELAYER.blit(SPRITELAYER, (0,0))
			BASELAYER.blit(INFOLAYER, (0,0))
		elif (drawHud and Player.hitbox.center[1] > 420):
			BASELAYER.blit(TILELAYER,(0,(420-Player.coordinates[1])-30))
			BASELAYER.blit(SPRITELAYER, (0,(420-Player.coordinates[1])-30))
		if (drawHud):
			BASELAYER.blit(HUDLAYER,(0,0))
		BASELAYER.blit(DEBUGLAYER, (0,0))
		if ((not specialPickupVisible)):
			screen.blit(BASELAYER, (0,0))
		else:
			CAMERALAYER.blit(pg.transform.scale(BASELAYER, (SCREENWIDTH, SCREENHEIGHT)), (SCREENWIDTH//2 - Player.hitbox.center[0], SCREENHEIGHT//2 - Player.hitbox.center[1]))
			CAMERA_ZOOMED_RECT = pg.transform.scale(CAMERALAYER, (SCREENWIDTH*ZOOM_LEVEL, SCREENHEIGHT*ZOOM_LEVEL)).get_rect()
			CAMERA_ZOOMED_RECT.center = (SCREENWIDTH/2,SCREENHEIGHT/2)
			screen.blit(pg.transform.scale(CAMERALAYER, (SCREENWIDTH*ZOOM_LEVEL, SCREENHEIGHT*ZOOM_LEVEL)), CAMERA_ZOOMED_RECT)
		if ((not specialPickupVisible) and (not clicked)):
			screen.blit(CURSOR, pg.mouse.get_pos())
		elif ((not specialPickupVisible) and clicked):
			screen.blit(CURSORCLICKED, pg.mouse.get_pos())
		if (menuPressCooldown > 0):
			menuPressCooldown -= 1
		pg.display.flip()
		clock.tick(FPS)
		Player.moved = False

if (__name__ == "__main__"):
	readAllJsonData()
	setup()
	loadTileSpritesheets()
	game()