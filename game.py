import random, os, time, math, copy
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
PALEBLUE = (24, 23, 87)
DARKBLUE = (7,5,35)
DARKESTBLUE = (0,0,15)
ORANGE = (255,126,71)
GREEN = (88, 130, 112)
PALEGREEN = (138, 158, 149)
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
DIRECTION_ANGLES = (90,-90,0,180)
walltileSpritesheets = []
proptileSpritesheets = []
SCROLLWHEEL_UP = 1
SCROLLWHEEL_DOWN = -1
MIN_KNOCKBACK = 3.52

def readAllJsonData():
	global DIALOGDATA, ITEMDATA, ROOMTILEDATA, EXITDATA, ENEMYDATA
	ROOMTILEDATA = modules.helper.readJsonFile("rooms.json")["rooms"]
	EXITDATA = modules.helper.readJsonFile("rooms.json")["exitData"]
	DIALOGDATA = modules.helper.readJsonFile("dialog.json")
	ITEMDATA = modules.helper.readJsonFile("itemData.json")
	ENEMYDATA = modules.helper.readJsonFile("enemy.json")
	assert len(ITEMDATA["ITEM TYPES"]) == len(ITEMDATA["ITEM ASSETS"]), "<qkuldo>there's an inequality in the itemData.json file between the item types and item assets.</qkuldo>"

def loadRoom(roomname,tileLayer,itemAssets, loadAll=True, frame=0, inactiveItems=[]):
	#loadRoom function needs only to be used when loading a new room
	oneWayExits = []
	for exit in EXITDATA:
		if (roomname in exit["involved rooms"]):
			if (not EXITDATA.index(exit) in ROOMTILEDATA[roomname]["exits"]):
				oneWayExits.append(EXITDATA.index(exit))
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
	exits = []
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
		exitReturns = []
		inExit = []
		toCoordinates = []
		exitIDs = []
		for item in range(0, len(ROOMTILEDATA[roomToLoad]["items"])):
			if (not item in inactiveItems):
				itemID = ROOMTILEDATA[roomToLoad]["items"][item]
				itemCoordinate = modules.helper.findTilePixelLocation(ROOMTILEDATA[roomToLoad]["itemCoordinates"][item][0],ROOMTILEDATA[roomToLoad]["itemCoordinates"][item][1])
				if (len(itemAssets) >= itemID):
					modules.helper.addItem(items, itemID, itemCoordinate, itemAssets)
		for exitID in ROOMTILEDATA[roomToLoad]["exits"]:
			assert exitID <= len(EXITDATA)-1, f"<qkuldo>searching for an exit({exitID}) that doesn't exist</qkuldo>"
			assert roomToLoad in EXITDATA[exitID].keys(), f"<qkuldo>this exit({exitID}) is not related to this room({roomToLoad})</qkuldo>"
			exitCoordinate = modules.helper.findTilePixelLocation(EXITDATA[exitID][roomToLoad][0],EXITDATA[exitID][roomToLoad][1])
			exitTo = list(EXITDATA[exitID]["involved rooms"]).index(roomToLoad)
			#below code switches exitTo from the index of the current room to the index of the next room
			if (exitTo > 0):
				exitTo = 0
			else:
				exitTo = 1
			exitTo = EXITDATA[exitID]["involved rooms"][exitTo]
			toCoordinates.append(EXITDATA[exitID][roomToLoad])
			exitReturns.append(exitTo)
			inExit.append(False)
			exitBox = pg.Rect(exitCoordinate,(TILESIZE,TILESIZE))
			exitBox = pg.Rect(exitBox.center, (TILESIZE//10, TILESIZE//10))
			exits.append(exitBox)
			exitIDs.append(exitID)
		for exitID in oneWayExits:
			assert exitID <= len(EXITDATA)-1, f"<qkuldo>searching for an exit({exitID}) that doesn't exist</qkuldo>"
			assert roomToLoad in EXITDATA[exitID].keys(), f"<qkuldo>this exit({exitID}) is not related to this room({roomToLoad})</qkuldo>"
			exitTo = list(EXITDATA[exitID]["involved rooms"]).index(roomToLoad)
			if (exitTo > 0):
				exitTo = 0
			else:
				exitTo = 1
			exitTo = EXITDATA[exitID]["involved rooms"][exitTo]
			exitCoordinate = modules.helper.findTilePixelLocation(EXITDATA[exitID][exitTo][0],EXITDATA[exitID][exitTo][1])
			toCoordinates.append(EXITDATA[exitID][roomToLoad])
			exitReturns.append(exitTo)
			exitIDs.append(exitID)
		currentRoomData = {
			"wall set index":wallSet,
			"prop set index":propSet,
			"hud theme":hudTheme,
			"playerSpawn":playerSpawn,
			"roomLayout":roomLayout,
			"collisionBoxes":collisionBoxes,
			"items":items,
			"exits":exits,
			"exit returns":exitReturns,
			"contained exits":inExit,
			"exit tp coordinates":toCoordinates,
			"exit IDs":exitIDs
		}
		return currentRoomData

def setup():
	global screen,clock,MISSINGTEXTURE,SFX,CURSOR, CURSORCLICKED, ICONS, EQUIPPED_SELECTOR, TARGET, TARGETRECT, LOCKEDTARGET, HPBARDESIGN, LOCKEDUNTARGET, AVAILABLETARGET
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
	AVAILABLETARGET = pg.image.load("assets/available_target.png").convert_alpha()
	AVAILABLETARGET = pg.transform.scale(AVAILABLETARGET, (TILESIZE,TILESIZE))
	LOCKEDUNTARGET = pg.image.load("assets/locked_untarget.png").convert_alpha()
	LOCKEDUNTARGET = pg.transform.scale(LOCKEDUNTARGET, (TILESIZE//1.5,TILESIZE//1.5))
	HPBARDESIGN = pg.image.load("assets/healthbarDesign.png")
	HPBARDESIGN = pg.transform.scale(HPBARDESIGN, (TILESIZE*2, TILESIZE*2))
	TARGETRECT = TARGET.get_rect()
	pg.mouse.set_visible(False)
	modules.helper.setVeryImportants(screen, clock)

def showInventory(HUDLAYER, Player, itemAssets, loadAll = True, mouse_collide_index = -1):
	drawx, drawy = 500, 450
	ITEMTILESIZE = 48
	ITEMHITBOXES = []
	INVENTORYITEMIDS = []
	ITEM_AMOUNT_TEXT, ITEM_AMOUNT_TEXT_RECT = modules.helper.createText((0,0), text = DEBUGTEXT)
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
				ITEM_AMOUNT_TEXT, ITEM_AMOUNT_TEXT_RECT = modules.helper.createText((drawx+ITEMTILESIZE/2+10,drawy+ITEMTILESIZE+10), text = f"{itemAmount}", font=0)
				HUDLAYER.blit(ITEM_AMOUNT_TEXT, ITEM_AMOUNT_TEXT_RECT)
			else:
				ITEM_AMOUNT_TEXT, ITEM_AMOUNT_TEXT_RECT = modules.helper.createText((drawx+ITEMTILESIZE-10,drawy+ITEMTILESIZE-10), text = f"{itemAmount}", font=0)
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

def game():
	#find and make assets
	itemAssets = ITEMDATA["ITEM ASSETS"]
	weaponAssets = ITEMDATA["WEAPON USE"]
	enemyAssets = ENEMYDATA["ASSETS"]
	for assetPath in itemAssets:
		itemAssets[itemAssets.index(assetPath)] = pg.image.load(assetPath).convert_alpha()
	for assetPath in weaponAssets:
		weaponAssets[weaponAssets.index(assetPath)] = pg.image.load(assetPath).convert_alpha()
	for assetPath in enemyAssets:
		enemyAssets[enemyAssets.index(assetPath)] = pg.image.load(assetPath).convert_alpha()
	playerAsset = pg.image.load("assets/player.png").convert_alpha()
	playerAsset = modules.sheets.Spritesheet(playerAsset, 16, 16)
	playerPortrait = pg.image.load("assets/playerPortrait.png").convert()
	playerPortrait = pg.transform.scale(playerPortrait,(128,128))
	hand = pg.transform.scale(pg.image.load("assets/hand.png"), (8, 8)).convert()
	specialItem = pg.Surface((TILESIZE,TILESIZE)).convert_alpha()
	specialItemRect = specialItem.get_rect()
	#define screen layers
	TILELAYER = modules.helper.initDrawLayer()
	HUDLAYER = modules.helper.initDrawLayer()
	SPRITELAYER = modules.helper.initDrawLayer()
	INFOLAYER = modules.helper.initDrawLayer()
	AFFECTED_INFOLAYER = modules.helper.initDrawLayer()
	BASELAYER = modules.helper.initDrawLayer()
	CAMERALAYER = modules.helper.initDrawLayer()
	INVENTORY_DESCLAYER = modules.helper.initDrawLayer()
	DEBUGLAYER = modules.helper.initDrawLayer()
	blackHudArea = pg.Rect((0,HUDMARGIN),(SCREENWIDTH,HUDMARGIN))
	#define custom events
	ANIMATIONSWITCHEVENT = pg.event.custom_type()
	SPECIALPICKUPSTAY = pg.event.custom_type()
	START_FADEOUT = pg.event.custom_type()
	ENDSWORD_VISIBILITY = pg.event.custom_type()
	ENDSWORD_PLAYERMOVEMENT = pg.event.custom_type()
	PLAYER_HITSTART = pg.event.custom_type()
	PLAYER_HITSTOP = pg.event.custom_type()
	SCROLLWHEEL_COOLDOWN = pg.event.custom_type()

	#player attack variables
	ATTACK_QTE_END = pg.event.custom_type()
	ATTACK_QTE_START = pg.event.custom_type()
	attack_qte_active = False
	attack_qte_success = None
	attack_qte_ongoing_attack = False
	ATTACK_BUTTON_COOLDOWN = pg.event.custom_type()
	CLICKCOOLDOWNFINISH = pg.event.custom_type()
	on_attack_button_cooldown = False
	#define other variables
	drawHud = False
	menuPressCooldown = 0
	running = True
	debugMode = 0
	specialPickupVisible = False
	specialPickupAlpha = 255
	specialPickupFade = False
	timedRect_fillRate = 1
	timedRect_fill = False
	zoom_level = 1
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
	ACTIONBAR_COORDINATES = (45,130)
	target_angle = 0
	screenCoordinates = (0, 0)
	roomFrame = 0
	roomAccumulateFrames = 0
	current_room = "spawnSpot"
	clickInCooldown = False
	debugSecMode = 0
	distanceList = []
	canScroll = True
	attack_qte_power = 0
	actionTimer_baseChange = 1
	actionTimer_recoveryChange = 0.5
	actionTimer_max = 100
	actionTimerFailingMark = False
	comboSlowdown = False
	swingWithoutTarget_setting = False
	start_zoomLevel = 1
	slowedDownAnimations = False
	was_comboSlowdown = False
	zoomStep = 0
	#minimum topleft position of camera to reveal out of bounds
	outOfBoundsRevealBaseline = (4.3, 2.42)
	#cache stores data that should be saved
	cache = {
		"item inactivators":{}
	}
	#temp cache stores data only needed for the current session
	temp_cache = {
		"item timers":{},
		"hit cooldowns":{},
		"combolist":set()
	}
	if (not current_room in list(cache["item inactivators"].keys())):
		cache["item inactivators"][current_room] = set()
	if (not current_room in list(temp_cache["item timers"].keys())):
		temp_cache["item timers"][current_room] = []
	currentRoomData = loadRoom(current_room,TILELAYER,itemAssets,inactiveItems=cache["item inactivators"][current_room] | modules.helper.unpack_nestedDict(temp_cache["item timers"][current_room], "item index"))
	#define sprites
	#directionalFrames custom attribute is written as a list for compatibility with DIRECTION_IDS constant dict
	Player = modules.interactables.Sprite(playerAsset,copy.copy(currentRoomData["playerSpawn"]),5,spriteScale = (TILESIZE,TILESIZE), hitboxScale = (TILESIZE-24,TILESIZE-18), hitboxLocation = (currentRoomData["playerSpawn"][0]+6,currentRoomData["playerSpawn"][1]+18),customAttributes = {
			"currentFrame":0,
			"frameRow":0,
			"facingDirection":DIRECTION_IDS["left"],
			"directionalFrames":[{"startFrame":0, "endFrame":2}, {"startFrame":3, "endFrame":5}, {"startFrame":6, "endFrame":8}, {"startFrame":9, "endFrame":11}],
			"inventory":{},
			"target pos":None,
			"targeting":False,
			"target name":"",
			"stats":{
				"health":20,
				"max health":20,
				"defense":3,
				"weight":1,
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
			"hit animation":False,
			"apply knockback":False,
			"reverse knockback":False,
			"attempted qte":False,
			"speed divider":1,
			"hit angle":0,
			"attack power":0,
			"action timer":100,
			"action state":1,
			"recovery timer":0
		})
	playerSword = modules.interactables.Sprite(weaponAssets[1], Player.hitbox.center, 0, spriteScale = (TILESIZE, TILESIZE), hitboxScale = (TILESIZE, TILESIZE), hitboxLocation = Player.hitbox.center, customAttributes = {"visible":False, "moving":False, "offset":0, "negativeSUB":False})
	test_enemy = modules.helper.makeEnemy(ENEMYDATA, 0, [currentRoomData["playerSpawn"][0] + 48, currentRoomData["playerSpawn"][1] + 48], enemyAssets, DIRECTION_IDS["left"])
	enemyList = [test_enemy]
	#rect creation
	playerActionCostRect = pg.Rect((0, 0), (0, TILESIZE//2))
	timedRect = pg.Rect(0, 0, 0, TILESIZE//5)
	timedRectBG = pg.Rect(0, 0, 30*timedRect_fillRate, TILESIZE//5)
	playerHealthRect = pg.Rect(30, 20, 10*Player.customAttributes["stats"]["health"], TILESIZE//2)
	playerMaxHealthRect = pg.Rect(30, 20, 10*Player.customAttributes["stats"]["max health"], TILESIZE//2)
	attackHitbox = pg.Rect(0, 0, TILESIZE//2, TILESIZE//2)
	#make text
	#testText, textTestRect = modules.helper.createText((SCREENWIDTH/2,SCREENHEIGHT/2))
	specialPickupText, specialPickupTextRect = modules.helper.createText((0,0), text = DEBUGTEXT)
	INVENTORY_ITEM_TEXT, INVENTORY_ITEM_TEXT_RECT = modules.helper.createText((520,500), text = DEBUGTEXT)
	WEAPON_EQUIPPED_TEXT, WEAPON_EQUIPPED_TEXT_RECT = modules.helper.createText((300, 650), text = "LEFT CLICK TO EQUIP WEAPON", color=BRIGHTYELLOW, font = 1)
	test_text, test_text_rect = modules.helper.createText((50, 20), text = str(debugMode), color=BRIGHTYELLOW)
	PLACEHOLDERTARGETLOCK = [SCREENWIDTH/2, SCREENHEIGHT/2]
	#set timers
	pg.time.set_timer(ANIMATIONSWITCHEVENT,180)
	while running:
		#playerSword.angle += 5
		#cleanup

		screen.fill(BGCOLOR)
		modules.helper.clearLayer(SPRITELAYER)
		modules.helper.clearLayer(CAMERALAYER)
		modules.helper.clearLayer(HUDLAYER)
		modules.helper.clearLayer(INVENTORY_DESCLAYER)
		modules.helper.clearLayer(INFOLAYER)
		modules.helper.clearLayer(AFFECTED_INFOLAYER)
		modules.helper.clearLayer(DEBUGLAYER)
		#set stuff
		scrollWheel_direction = 0
		if (not (specialPickupVisible or drawHud)):
			current_time = pg.time.get_ticks()
		timedRect.bottomleft = Player.hitbox.topright
		timedRectBG.bottomleft = Player.hitbox.topright
		mouseRect = pg.Rect(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1], TILESIZE, TILESIZE)
		playerActionRect = pg.Rect(ACTIONBAR_COORDINATES, (Player.customAttributes["action timer"]*2, TILESIZE//2))
		playerRecoveryRect = pg.Rect((ACTIONBAR_COORDINATES[0],ACTIONBAR_COORDINATES[1]+30), (Player.customAttributes["recovery timer"], TILESIZE//5))
		playerMaxActionRect = pg.Rect(ACTIONBAR_COORDINATES, (actionTimer_max*2, TILESIZE//2))
		playerHealthRect = pg.Rect(HEALTHBAR_COORDINATES, (10*Player.customAttributes["stats"]["health"], TILESIZE//2))
		playerMaxHealthRect = pg.Rect(HEALTHBAR_COORDINATES, (10*Player.customAttributes["stats"]["max health"], TILESIZE//2))
		healthString = str(Player.customAttributes["stats"]["health"])+"/"+str(Player.customAttributes["stats"]["max health"])
		healthText, healthTextRect = modules.helper.createText((playerHealthRect.midleft[0]+45, playerHealthRect.midleft[1]), text = healthString, color = BRIGHTYELLOW, font = 2)
		player_CenterOffset = [SCREENWIDTH//2 - Player.hitbox.center[0], SCREENHEIGHT//2 - Player.hitbox.center[1]]
		zoom_reveal_outOfBounds = [outOfBoundsRevealBaseline[0]*((zoom_level-1)*100),outOfBoundsRevealBaseline[1]*((zoom_level-1)*100)]
		playerSword.hitbox.center = Player.hitbox.center
		#below line is pretty trippy ngl
		#Player.angle = modules.helper.face_target(Player.coordinates, (SCREENWIDTH/2,SCREENHEIGHT/2))

		if (debugMode == 1):
			test_text, test_text_rect = modules.helper.createText((200, 20), text = current_room + " MODE " + str(debugMode), color=BRIGHTYELLOW)
		elif (debugMode == 3):
			test_text, test_text_rect = modules.helper.createText((200, 20), text = str(Player.customAttributes["action timer"]) + " , " + str(Player.customAttributes["action state"]) + " MODE 3", color=BRIGHTYELLOW)
		else:
			test_text, test_text_rect = modules.helper.createText((100, 20), text = "MODE "+str(debugMode), color=BRIGHTYELLOW)
		clock_text, clock_text_rect = modules.helper.createText((100, 50), text = str(current_time), color=BRIGHTYELLOW)
		distanceList = []
		switchFrame = False
		#cache important data
		cache["player"] = Player.customAttributes
		#handle events
		for event in pg.event.get():
			if (event.type == pg.QUIT):
				modules.helper.terminate()
			elif (event.type == ANIMATIONSWITCHEVENT):
				switchFrame = True
			elif (event.type == SPECIALPICKUPSTAY):
				specialPickupVisible = not specialPickupVisible
				pg.time.set_timer(SPECIALPICKUPSTAY, 0)
				specialPickupAlpha = 255
				specialPickupText, specialPickupTextRect = modules.helper.createText((0,0), text = "<qkuldo>you're not supposed to see this!</qkuldo>")
				specialPickupFade = False
				special_itemGet_addY = 0
				comboSlowdown = False
			elif (event.type == START_FADEOUT):
				pg.time.set_timer(START_FADEOUT, 0)
				specialPickupFade = True
				start_zoomLevel = copy.deepcopy(zoom_level)
				zoomStep = 0.001
				SFX["itemCollect"].play()
			elif (event.type == pg.MOUSEBUTTONDOWN):
				clicked = True
			elif (event.type == pg.MOUSEBUTTONUP):
				clicked = False
			elif (event.type == ATTACK_BUTTON_COOLDOWN):
				on_attack_button_cooldown = False
			elif (event.type == ATTACK_QTE_END):
				attack_qte_power = 0
				Player.customAttributes["speed divider"] = 1
				if (attack_qte_success):
					if (debugMode == 2):
						test_text, test_text_rect = modules.helper.createText((100, 20), text = "success", color=BRIGHTYELLOW)
					#print("success")
					SFX["slash"].set_volume(0.4)
					SFX["slash"].play()
					pg.time.set_timer(ENDSWORD_VISIBILITY, 500, 1)
					pg.time.set_timer(ENDSWORD_PLAYERMOVEMENT, 100, 1)
					playerSword.customAttributes["visible"] = True
					playerSword.customAttributes["moving"] = True
				elif (Player.customAttributes["attempted qte"] and not attack_qte_success):
					#print("fail")
					SFX["failedSlash"].play()
					Player.customAttributes["apply knockback"] = True
					pg.time.set_timer(PLAYER_HITSTART, 200, 1)
					pg.time.set_timer(PLAYER_HITSTOP, 1000, 1)
					if (debugMode == 2):
						test_text, test_text_rect = modules.helper.createText((100, 20), text = "fail", color=BRIGHTYELLOW)
				attack_qte_success = False
				attack_qte_ongoing_attack = False
				attack_qte_active = False
				Player.customAttributes["attempted qte"] = False
			elif (event.type == ENDSWORD_VISIBILITY):
				playerSword.customAttributes["visible"] = False
			elif (event.type == ENDSWORD_PLAYERMOVEMENT):
				playerSword.customAttributes["moving"] = False
			elif (event.type == PLAYER_HITSTOP):
				Player.customAttributes["hit animation"] = False
				Player.customAttributes["apply knockback"] = False
				Player.customAttributes["reverse knockback"] = False
			elif (event.type == PLAYER_HITSTART):
				Player.customAttributes["hit animation"] = True
			if (event.type == CLICKCOOLDOWNFINISH):
				clickInCooldown = False
			if (event.type == pg.MOUSEWHEEL):
				#if (event.y == SCROLLWHEEL_UP):
				#	print("up")
				#elif (event.y == SCROLLWHEEL_DOWN):
				#	print("down")
				scrollWheel_direction = copy.copy(event.y)
			if (event.type == SCROLLWHEEL_COOLDOWN):
				canScroll = True
		#detect key presses
		keys = pg.key.get_pressed()
		if (drawHud):
			MOUSE_HOVER_INVENTORY_INDEX = mouseRect.collidelist(INVENTORYBUTTONS)
			loadHudLayer(HUDLAYER,blackHudArea,currentRoomData, playerPortrait)
			showInventory(HUDLAYER,Player, itemAssets, loadAll=False, mouse_collide_index=MOUSE_HOVER_INVENTORY_INDEX)
		else:
			MOUSE_HOVER_INVENTORY_INDEX = -1
		if (keys[pg.K_ESCAPE] and menuPressCooldown <= 0 and (not specialPickupVisible) and (not attack_qte_ongoing_attack) and (not playerSword.customAttributes["visible"])):
			drawHud = not drawHud
			menuPressCooldown = MENUPRESSTIME
			#it is intentional that the "menu close" sound plays when opening the menu, and vice versa
			if (drawHud):
				SFX["closeMenu"].play()
				INVENTORYBUTTONS, INVENTORY_ITEMS = showInventory(HUDLAYER,Player, itemAssets, loadAll=True)
			else:
				SFX["openMenu"].play()
		if (keys[pg.K_p] and menuPressCooldown <= 0):
			#pepug menu
			debugMode += 1
			if (debugMode > 3):
				debugMode = 0
			menuPressCooldown = MENUPRESSTIME
		if (playerSword.customAttributes["visible"]):
			attackHitbox.center = (Player.hitbox.center[0]-modules.helper.goto_angle(50,playerSword.angle+playerSword.customAttributes["offset"])[0], Player.hitbox.center[1]-modules.helper.goto_angle(50,playerSword.angle+playerSword.customAttributes["offset"])[1])
		for enemy in enemyList:
			if (enemy.hitbox.colliderect(attackHitbox) and playerSword.customAttributes["visible"] and not enemy.customAttributes["name"] in temp_cache["hit cooldowns"].keys()):
				if (Player.customAttributes["attack power"] == 1):
					damage = ITEMDATA["WEAPON STATS"][Player.customAttributes["stats"]["equipment"]["WEAPONS"]["sword"]]
					enemy.customAttributes["hit power"] = 1
				else:
					enemy.customAttributes["hit power"] = 0
					damage = ITEMDATA["WEAPON STATS"][Player.customAttributes["stats"]["equipment"]["WEAPONS"]["sword"]]*0.5
				#deals damage if enemy has no "invincible" flag
				if (not ENEMYDATA["FLAGS"][1] in enemy.customAttributes["flags"]):
					enemy.customAttributes["stats"]["health"] -= damage
				#name is for identification in case of index change
				temp_cache["hit cooldowns"][enemy.customAttributes["name"]] = {
					"start time":pg.time.get_ticks(),
					"duration":500
				}
				enemy.customAttributes["hit angle"] = copy.copy(playerSword.angle)
				SFX["damage"].set_volume(random.uniform(0.2,0.5))
				SFX["slash"].set_volume(0.2)
				SFX["damage"].play()
				if (not comboSlowdown):
					enemy.customAttributes["stored momentum"] = MIN_KNOCKBACK
				else:
					enemy.customAttributes["stored momentum"] += MIN_KNOCKBACK
					temp_cache["combolist"].add(enemy.customAttributes["name"])
			if (was_comboSlowdown and enemy.customAttributes["name"] in temp_cache["combolist"]):
				temp_cache["hit cooldowns"][enemy.customAttributes["name"]] = {
					"start time":pg.time.get_ticks(),
					"duration":500
				}
				SFX["damage"].set_volume(random.uniform(0.2,0.5))
				SFX["damage"].play()
				enemy.customAttributes["stored momentum"] = 0
				temp_cache["combolist"].remove(enemy.customAttributes["name"])
			if (enemy.customAttributes["name"] in temp_cache["hit cooldowns"].keys() and not (specialPickupVisible or drawHud)):
				enemy.customAttributes["visible"] = not enemy.customAttributes["visible"]
				if (not ENEMYDATA["FLAGS"][0] in enemy.customAttributes["flags"]):
					speedResistanceCalculation = enemy.customAttributes["stats"]["weight"]
					if (enemy.customAttributes["hit power"] == 0):
						speedResistanceCalculation = speedResistanceCalculation*1.5
					if (not comboSlowdown):
						directional_vector = modules.helper.goto_angleComplex(enemy, angle=enemy.customAttributes["hit angle"], checkCollision=True, collisionList=currentRoomData["collisionBoxes"], setDir = False, speedDivider=speedResistanceCalculation, speedOverride=enemy.customAttributes["stored momentum"])
					if (not comboSlowdown):
						enemy.coordinates[0] += directional_vector[0]
						enemy.coordinates[1] += directional_vector[1]
				enemy.customAttributes["got hit"] = True
			else:
				if (enemy.customAttributes["stats"]["health"] <= 0):
					enemyList.remove(enemy)
				enemy.customAttributes["visible"] = True
				if (not (specialPickupVisible or drawHud)):
					modules.helper.moveEnemy(enemy, ENEMYDATA, currentRoomData, Player, current_time, enemy.customAttributes["got hit"], comboSlowdown)
					enemy.customAttributes["got hit"] = False
			enemy.update(rectOperation = (enemy.coordinates[0]+enemy.customAttributes["rectOperation"][0],enemy.coordinates[1]+enemy.customAttributes["rectOperation"][1]))
			if (enemy.customAttributes["name"] == Player.customAttributes["target name"]):
				Player.customAttributes["target pos"] = copy.deepcopy(enemy.hitbox.center)
			if (enemy.customAttributes["visible"]):
				enemy.draw(0, SPRITELAYER)
			if (enemy.hitbox.colliderect(Player.hitbox) and enemy.customAttributes["state"] == modules.helper.ATTACK and not (Player.customAttributes["apply knockback"] or specialPickupVisible)):
				Player.customAttributes["apply knockback"] = True
				Player.customAttributes["stats"]["health"] -= enemy.customAttributes["stats"]["attack"]
				Player.customAttributes["hit angle"] = modules.helper.face_target(Player.hitbox.center, enemy.hitbox.center, False)
				pg.time.set_timer(PLAYER_HITSTART, 200, 1)
				pg.time.set_timer(PLAYER_HITSTOP, 1000, 1)
				SFX["damage"].set_volume(random.uniform(0.2,0.5))
				SFX["slash"].set_volume(0.2)
				SFX["damage"].play()
			if (debugMode == 2):
				#debug shenanigans
				if (debugSecMode == 0):
					dataDisplayText, dataDisplayRect = modules.helper.createText((enemy.hitbox.midtop[0],enemy.hitbox.midtop[1]-10),2,str(enemy.customAttributes["type"]),ORANGE)
					DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
					dataDisplayText, dataDisplayRect = modules.helper.createText((enemy.hitbox.midtop[0],enemy.hitbox.midtop[1]-30),2,enemy.customAttributes["name"],ORANGE)
					DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
					dataDisplayText, dataDisplayRect = modules.helper.createText((enemy.hitbox.midtop[0],enemy.hitbox.midtop[1]-50),2,f"{enemy.coordinates[0]:.2f},{enemy.coordinates[1]:.2f}",ORANGE)
					DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
				elif (debugSecMode == 1):
					healthFormatting = str(enemy.customAttributes["stats"]["health"]) + "/" + str(enemy.customAttributes["stats"]["max health"])
					dataDisplayText, dataDisplayRect = modules.helper.createText((enemy.hitbox.midtop[0],enemy.hitbox.midtop[1]-10),2,healthFormatting,BRIGHTYELLOW)
					DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
					dataDisplayText, dataDisplayRect = modules.helper.createText((enemy.hitbox.midtop[0],enemy.hitbox.midtop[1]-30),2,str(enemy.customAttributes["stats"]["defense"]),BRIGHTYELLOW)
					DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
					dataDisplayText, dataDisplayRect = modules.helper.createText((enemy.hitbox.midtop[0],enemy.hitbox.midtop[1]-50),2,str(enemy.customAttributes["stats"]["weight"]),BRIGHTYELLOW)
					DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
					dataDisplayText, dataDisplayRect = modules.helper.createText((enemy.hitbox.midtop[0],enemy.hitbox.midtop[1]-70),2,str(enemy.customAttributes["stats"]["attack"]),BRIGHTYELLOW)
					DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
				else:
					directionFormatting = list(DIRECTION_IDS.keys())[list(DIRECTION_IDS.values()).index(enemy.customAttributes["facingDirection"])]
					dataDisplayText, dataDisplayRect = modules.helper.createText((enemy.hitbox.midtop[0],enemy.hitbox.midtop[1]-10),2,directionFormatting,BLUE)
					DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
					dataDisplayText, dataDisplayRect = modules.helper.createText((enemy.hitbox.midtop[0],enemy.hitbox.midtop[1]-30),2,str(enemy.customAttributes["visible"]),BLUE)
					DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
					dataDisplayText, dataDisplayRect = modules.helper.createText((enemy.hitbox.midtop[0],enemy.hitbox.midtop[1]-50),2,f"{enemy.customAttributes["hit angle"]:.2f}",BLUE)
					DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
					if (enemy.customAttributes["state"] == modules.helper.IDLE):
						dataDisplayText, dataDisplayRect = modules.helper.createText((enemy.hitbox.midtop[0],enemy.hitbox.midtop[1]-70),2,"IDLE",BLUE)
					if (enemy.customAttributes["state"] == modules.helper.PURSUING):
						dataDisplayText, dataDisplayRect = modules.helper.createText((enemy.hitbox.midtop[0],enemy.hitbox.midtop[1]-70),2,"PURSING",BLUE)
					if (enemy.customAttributes["state"] == modules.helper.WINDUP):
						dataDisplayText, dataDisplayRect = modules.helper.createText((enemy.hitbox.midtop[0],enemy.hitbox.midtop[1]-70),2,"WINDUP",BLUE)
					if (enemy.customAttributes["state"] == modules.helper.ATTACK):
						dataDisplayText, dataDisplayRect = modules.helper.createText((enemy.hitbox.midtop[0],enemy.hitbox.midtop[1]-70),2,"ATTACK",BLUE)
					if (enemy.customAttributes["state"] == modules.helper.RECOVERY):
						dataDisplayText, dataDisplayRect = modules.helper.createText((enemy.hitbox.midtop[0],enemy.hitbox.midtop[1]-70),2,"RECOVERY",BLUE)
					if (enemy.customAttributes["state"] == modules.helper.HITSTUN):
						dataDisplayText, dataDisplayRect = modules.helper.createText((enemy.hitbox.midtop[0],enemy.hitbox.midtop[1]-70),2,"HITSTUN",BLUE)
					DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
					dataDisplayText, dataDisplayRect = modules.helper.createText((enemy.hitbox.midtop[0],enemy.hitbox.midtop[1]-90),2,str(enemy.customAttributes["state timer start"]),BLUE)
					DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
			distanceList.append({"distance":modules.helper.measureDistance(enemy.hitbox.center,Player.hitbox.center),"position":enemy.hitbox.center,"name":enemy.customAttributes["name"]})
		was_comboSlowdown = False
		if (len(enemyList) > 0):
			distances = modules.helper.unpack_nestedDict(distanceList, "distance", returnSet = False)
			zipped_distData = zip(distances, distanceList)
			zipped_distData_sorted = sorted(zipped_distData, key = lambda x:x[0])
			distances_sorted, distanceList_sorted = zip(*zipped_distData_sorted)
			distances, distanceList = list(distances_sorted), list(distanceList_sorted)
		if (timedRect_fill):
			if (15 <= attack_qte_power < 30):
				#print(timedRect.width)
				if (debugMode == 1):
					test_text, test_text_rect = modules.helper.createText((100, 20), text = "click", color=BRIGHTYELLOW)
				attack_qte_active = True
			if (attack_qte_power >= 30 or playerSword.customAttributes["visible"]):
				timedRect = pg.Rect(0, 0, 0, TILESIZE//5)
				timedRect_fill = False
				pg.time.set_timer(ATTACK_QTE_END, 500, 1)
		if (keys[pg.K_SPACE] and menuPressCooldown <= 0):
			#debug controller
			debugSecMode += 1
			if (debugSecMode > 2):
				debugSecMode = 0
			if (debugMode == 3):
				enemyList.append(modules.helper.makeEnemy(ENEMYDATA, 0, [Player.coordinates[0] + 48, Player.coordinates[1] + 48], enemyAssets, DIRECTION_IDS["left"]))
			menuPressCooldown = MENUPRESSTIME
		if ((not drawHud) and (not specialPickupVisible) and (not playerSword.customAttributes["visible"]) and (not Player.customAttributes["hit animation"])):
			if (keys[pg.K_w] or keys[pg.K_UP]):
				modules.helper.complexMove(Player,SIMOVE_Y,SIMOVE_SUB,currentRoomData,Player.customAttributes["speed divider"])
				Player.customAttributes["facingDirection"] = DIRECTION_IDS["up"]
				#Player.angle = DIRECTION_ANGLES["up"]
			elif (keys[pg.K_s] or keys[pg.K_DOWN]):
				modules.helper.complexMove(Player,SIMOVE_Y,SIMOVE_ADD,currentRoomData,Player.customAttributes["speed divider"])
				Player.customAttributes["facingDirection"] = DIRECTION_IDS["down"]
				#Player.angle = DIRECTION_ANGLES["down"]
			if (keys[pg.K_a] or keys[pg.K_LEFT]):
				modules.helper.complexMove(Player,SIMOVE_X,SIMOVE_SUB,currentRoomData,Player.customAttributes["speed divider"])
				Player.customAttributes["facingDirection"] = DIRECTION_IDS["left"]
				#Player.angle = DIRECTION_ANGLES["left"]
			elif (keys[pg.K_d] or keys[pg.K_RIGHT]):
				modules.helper.complexMove(Player,SIMOVE_X,SIMOVE_ADD,currentRoomData,Player.customAttributes["speed divider"])
				Player.customAttributes["facingDirection"] = DIRECTION_IDS["right"]
				#Player.angle = DIRECTION_ANGLES["right"]
			if (scrollWheel_direction == SCROLLWHEEL_UP and Player.customAttributes["targeting"] and canScroll and not (attack_qte_ongoing_attack or playerSword.customAttributes["visible"] or len(enemyList) == 0)):
				targetNames = modules.helper.unpack_nestedDict(distanceList, "name", False)
				targetIndex = targetNames.index(Player.customAttributes["target name"])
				if (targetIndex+1 < len(distanceList)):
					targetIndex += 1
				else:
					targetIndex = 0
				Player.customAttributes["target pos"] = copy.deepcopy(distanceList[targetIndex]["position"])
				Player.customAttributes["target name"] = copy.copy(distanceList[targetIndex]["name"])
				modules.helper.goto_angleComplex(Player, angle=playerSword.angle, targetPos = Player.customAttributes["target pos"])
				canScroll = False
				pg.time.set_timer(SCROLLWHEEL_COOLDOWN, 300, 1)
			if (scrollWheel_direction == SCROLLWHEEL_DOWN and Player.customAttributes["targeting"] and canScroll and not (attack_qte_ongoing_attack or playerSword.customAttributes["visible"] or len(enemyList) == 0)):
				targetNames = modules.helper.unpack_nestedDict(distanceList, "name", False)
				targetIndex = targetNames.index(Player.customAttributes["target name"])
				if (targetIndex-1 >= 0):
					targetIndex -= 1
				else:
					targetIndex = len(distanceList)-1
				Player.customAttributes["target pos"] = copy.deepcopy(distanceList[targetIndex]["position"])
				Player.customAttributes["target name"] = copy.copy(distanceList[targetIndex]["name"])
				modules.helper.goto_angleComplex(Player, angle=playerSword.angle, targetPos = Player.customAttributes["target pos"])
				canScroll = False
				pg.time.set_timer(SCROLLWHEEL_COOLDOWN, 300, 1)
			if (keys[pg.K_LSHIFT] and not (attack_qte_ongoing_attack or playerSword.customAttributes["visible"] or len(enemyList) == 0)):
				start_zoomLevel = copy.deepcopy(zoom_level)
				zoomStep = 0.001
				if (not Player.customAttributes["targeting"]):
					Player.customAttributes["target pos"] = copy.deepcopy(distanceList[0]["position"])
					Player.customAttributes["targeting"] = True
					Player.customAttributes["target name"] = copy.copy(distanceList[0]["name"])
				modules.helper.goto_angleComplex(Player, angle=playerSword.angle, targetPos = Player.customAttributes["target pos"])
				target_angle += 4
				TARGETRECT = pg.transform.rotate(TARGET, target_angle).get_rect()
				TARGETRECT.center = Player.customAttributes["target pos"]
				if (modules.helper.measureDistance(Player.hitbox.center, Player.customAttributes["target pos"]) > 120):
					AFFECTED_INFOLAYER.blit(pg.transform.rotate(TARGET, target_angle), TARGETRECT)
				else:
					AFFECTED_INFOLAYER.blit(pg.transform.rotate(AVAILABLETARGET, target_angle), TARGETRECT)
			elif (not (attack_qte_ongoing_attack or playerSword.customAttributes["visible"])):
				Player.customAttributes["targeting"] = False
				Player.customAttributes["target pos"] = None
				Player.customAttributes["target name"] = ""
			if (keys[pg.K_z] and Player.customAttributes["action state"] == 1 and (not attack_qte_ongoing_attack) and Player.customAttributes["stats"]["equipment"]["WEAPONS"]["sword"] != None and (not Player.customAttributes["apply knockback"])):
				Player.customAttributes["recovery timer"] = 0
				if (swingWithoutTarget_setting and not Player.customAttributes["targeting"]):
					Player.customAttributes["target pos"] = copy.copy(mouseRect.center)
					attack_qte_ongoing_attack = True
					attack_qte_success = False
					timedRect_fill = True
					Player.customAttributes["attack power"] = 0
					Player.customAttributes["speed divider"] = 3
				elif (Player.customAttributes["targeting"] and modules.helper.measureDistance(Player.hitbox.center, Player.customAttributes["target pos"]) < 120):
					attack_qte_ongoing_attack = True
					attack_qte_success = False
					timedRect_fill = True
					Player.customAttributes["attack power"] = 0
					Player.customAttributes["speed divider"] = 3
			if (keys[pg.K_x] and attack_qte_ongoing_attack and attack_qte_active):
				if (attack_qte_power > 27):
					Player.customAttributes["attack power"] = 1
					Player.customAttributes["action timer"] -= 40
					playerSword.customAttributes["offset"] = random.choice((-100,100))
				else:
					Player.customAttributes["action timer"] -= 20
					playerSword.customAttributes["offset"] = random.choice((-40,40))
				if (Player.customAttributes["action timer"] >= 0):
					attack_qte_success = True
				else:
					attack_qte_success = False
				on_attack_button_cooldown = True
				timedRect_fill = False
				timedRect = pg.Rect(0, 0, 0, TILESIZE//5)
				pg.time.set_timer(ATTACK_QTE_END, 1, 1)
				pg.time.set_timer(ATTACK_BUTTON_COOLDOWN, 800, 1)
				Player.customAttributes["attempted qte"] = True
				if (playerSword.customAttributes["offset"] > 0):
					playerSword.customAttributes["negativeSUB"] = True
				else:
					playerSword.customAttributes["negativeSUB"] = False
				playerSword.angle = modules.helper.face_target(Player.hitbox.center, Player.customAttributes["target pos"])
			elif (keys[pg.K_x] and attack_qte_ongoing_attack and not attack_qte_active):
				Player.customAttributes["action timer"] -= 25
				attack_qte_success = False
				Player.customAttributes["hit angle"] = modules.helper.face_target(Player.hitbox.center, Player.customAttributes["target pos"])
				on_attack_button_cooldown = True
				timedRect_fill = False
				Player.customAttributes["attempted qte"] = True
				timedRect = pg.Rect(0, 0, 0, TILESIZE//5)
				pg.time.set_timer(ATTACK_QTE_END, 1, 1)
				pg.time.set_timer(ATTACK_BUTTON_COOLDOWN, 800, 1)
		#update stuff
		if (attack_qte_ongoing_attack):
			actionTimerFailingMark = False
			if (attack_qte_power > 27):
				if (Player.customAttributes["action timer"] >= 40):
					playerActionCostRect.width = 80
				else:
					playerActionCostRect.width = playerActionRect.width
					actionTimerFailingMark = True
			else:
				if (Player.customAttributes["action timer"] >= 20):
					playerActionCostRect.width = 40
				else:
					actionTimerFailingMark = True
					playerActionCostRect.width = playerActionRect.width
			playerActionCostRect.topright = playerActionRect.topright
		else:
			playerActionCostRect.width = 0
		if (attack_qte_ongoing_attack or playerSword.customAttributes["visible"]):
			modules.helper.goto_angleComplex(Player, angle=playerSword.angle, targetPos = Player.customAttributes["target pos"])
		if (switchFrame and (not specialPickupVisible)):
			if (comboSlowdown and not slowedDownAnimations):
				slowedDownAnimations = True
				pg.time.set_timer(ANIMATIONSWITCHEVENT, 360)
			elif (slowedDownAnimations and not comboSlowdown):
				slowedDownAnimations = False
				pg.time.set_timer(ANIMATIONSWITCHEVENT, 180)
			if (Player.customAttributes["hit animation"]):
				Player.customAttributes["visible"] = not Player.customAttributes["visible"]
				if (Player.customAttributes["facingDirection"] == DIRECTION_IDS["left"]):
					Player.customAttributes["currentFrame"] = 4
				elif (Player.customAttributes["facingDirection"] == DIRECTION_IDS["right"]):
					Player.customAttributes["currentFrame"] = 1
				elif (Player.customAttributes["facingDirection"] == DIRECTION_IDS["up"]):
					Player.customAttributes["currentFrame"] = 2
				elif (Player.customAttributes["facingDirection"] == DIRECTION_IDS["down"]):
					Player.customAttributes["currentFrame"] = 3
				Player.customAttributes["frameRow"] = 1
			elif (not Player.customAttributes["apply knockback"]):
				Player.customAttributes["visible"] = True
				modules.helper.animateLoop(Player, Player.customAttributes["directionalFrames"][Player.customAttributes["facingDirection"]]["startFrame"], Player.customAttributes["directionalFrames"][Player.customAttributes["facingDirection"]]["endFrame"])
				Player.customAttributes["frameRow"] = 0
			roomAccumulateFrames += 1
			if (roomAccumulateFrames == 2):
				if (roomFrame == 0):
					roomFrame = 1
				else:
					roomFrame = 0
				roomAccumulateFrames = 0
			modules.helper.clearLayer(TILELAYER)
			TILELAYER.fill(DARKESTBLUE)
			loadRoom(current_room,TILELAYER,itemAssets,False,roomFrame)
		elif (specialPickupVisible):
			Player.customAttributes["currentFrame"] = 0
			Player.customAttributes["frameRow"] = 1

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
		if (playerSword.customAttributes["visible"]):
			if (playerSword.customAttributes["negativeSUB"] == True):
				if (playerSword.customAttributes["offset"] > 0):
					if (Player.customAttributes["attack power"] == 0):
						playerSword.customAttributes["offset"] -= 6
					else:
						playerSword.customAttributes["offset"] -= 10
			else:
				if (playerSword.customAttributes["offset"] < 0):
					if (Player.customAttributes["attack power"] == 0):
						playerSword.customAttributes["offset"] += 6
					else:
						playerSword.customAttributes["offset"] += 8
			if (playerSword.customAttributes["moving"]):
				if (Player.customAttributes["attack power"] == 0):
					directional_vector = modules.helper.goto_angleComplex(Player, angle=playerSword.angle, targetPos = Player.customAttributes["target pos"], checkCollision=True, collisionList=currentRoomData["collisionBoxes"], speed_multiplier=2)
				else:
					directional_vector = modules.helper.goto_angleComplex(Player, angle=playerSword.angle, targetPos = Player.customAttributes["target pos"], checkCollision=True, collisionList=currentRoomData["collisionBoxes"], speed_multiplier=0.6)
				Player.coordinates[0] += directional_vector[0]
				Player.coordinates[1] += directional_vector[1]

		if (Player.customAttributes["apply knockback"] and not Player.customAttributes["hit animation"]):
			directional_vector = modules.helper.goto_angleComplex(Player, speed_multiplier=1, angle=Player.customAttributes["hit angle"], checkCollision=True, collisionList=currentRoomData["collisionBoxes"], setDir = False, speedDivider=Player.customAttributes["stats"]["weight"], speedOverride=MIN_KNOCKBACK)
			if (Player.customAttributes["reverse knockback"]):
				Player.coordinates[0] -= directional_vector[0]
				Player.coordinates[1] -= directional_vector[1]
			else:
				Player.coordinates[0] += directional_vector[0]
				Player.coordinates[1] += directional_vector[1]
			if (not modules.helper.hitboxInbound(Player.hitbox)):
				raise Exception("<qkuldo>u were right, there was an exception</qkuldo>")

		#SPRITELAYER.blit(testText, textTestRect)
		if ((not specialPickupVisible) and drawHud and len(Player.customAttributes["inventory"]) > 0):
			#loops through INVENTORYBUTTONS for a rect that passes colliderect check with mouse position
			MOUSE_HOVER_ID = ITEMIDS.index(INVENTORY_ITEMS[mouseRect.collidelist(INVENTORYBUTTONS)])
			if (MOUSE_HOVER_INVENTORY_INDEX != -1):
				#creates item header text
				if (ITEMTYPEIDS[ITEMDATA["ITEM TYPES"][ITEMIDS[MOUSE_HOVER_ID]]] in ("weapon", "armor")):
					INVENTORY_ITEM_TEXT, INVENTORY_ITEM_TEXT_RECT = modules.helper.createText((300,480), text = INVENTORY_ITEMS[MOUSE_HOVER_INVENTORY_INDEX], color=BRIGHTYELLOW)
				else:
					INVENTORY_ITEM_TEXT, INVENTORY_ITEM_TEXT_RECT = modules.helper.createText((300,480), text = INVENTORY_ITEMS[MOUSE_HOVER_INVENTORY_INDEX], color=WHITE)
				itemType = ITEMTYPEIDS.index(ITEMTYPEIDS[ITEMDATA["ITEM TYPES"][INVENTORY_ITEMS[MOUSE_HOVER_INVENTORY_INDEX]]])
				#blit type icon and item name
				HUDLAYER.blit(pg.transform.scale(ICONS.load_frame(itemType), (TILESIZE/2, TILESIZE/2)), (INVENTORY_ITEM_TEXT_RECT.topleft[0]-ITEMTYPE_XMARGIN, INVENTORY_ITEM_TEXT_RECT.midleft[1]-ITEMTYPE_YMARGIN))
				HUDLAYER.blit(INVENTORY_ITEM_TEXT, INVENTORY_ITEM_TEXT_RECT)
				#display description
				if (type(DIALOGDATA["ITEM DESCRIPTIONS"][MOUSE_HOVER_ID]) != list):
					INVENTORY_ITEM_DESCRIPTION, INVENTORY_ITEM_DESC_RECT = modules.helper.createText((300,520), font=1, text = DIALOGDATA["ITEM DESCRIPTIONS"][ITEMIDS.index(INVENTORY_ITEMS[MOUSE_HOVER_INVENTORY_INDEX])])
					INVENTORY_DESCLAYER.blit(INVENTORY_ITEM_DESCRIPTION, INVENTORY_ITEM_DESC_RECT)
				else:
					starty = 520
					for line in DIALOGDATA["ITEM DESCRIPTIONS"][MOUSE_HOVER_ID]:
						INVENTORY_ITEM_DESCRIPTION, INVENTORY_ITEM_DESC_RECT = modules.helper.createText((300,starty), font=1, text = line)
						INVENTORY_DESCLAYER.blit(INVENTORY_ITEM_DESCRIPTION, INVENTORY_ITEM_DESC_RECT)
						starty += 15
				isWeapon = ITEMTYPEIDS[itemType] == "weapon"
				isEquipped = MOUSE_HOVER_ID in Player.customAttributes["stats"]["equipment"]["WEAPONS"].values()
				if (isWeapon and not isEquipped):
					WEAPON_EQUIPPED_TEXT, WEAPON_EQUIPPED_TEXT_RECT = modules.helper.createText((300, 650), text = "LEFT CLICK TO EQUIP WEAPON", color=BRIGHTYELLOW, font = 1)
				elif (isWeapon and isEquipped):
					WEAPON_EQUIPPED_TEXT, WEAPON_EQUIPPED_TEXT_RECT = modules.helper.createText((300, 650), text = "EQUIPPED IN WEAPON SLOT", color=BRIGHTYELLOW, font = 1)
				if (ITEMTYPEIDS[itemType] == "weapon"):
					HUDLAYER.blit(WEAPON_EQUIPPED_TEXT, WEAPON_EQUIPPED_TEXT_RECT)
				#equip weapon
				if (clicked and not clickInCooldown):
					clickInCooldown = True
					pg.time.set_timer(CLICKCOOLDOWNFINISH, 500, 1)
					if (isWeapon and not isEquipped):
						if (MOUSE_HOVER_ID in ITEMWEAPONS["sword"]):
							Player.customAttributes["stats"]["equipment"]["WEAPONS"]["sword"] = MOUSE_HOVER_ID
						elif (MOUSE_HOVER_ID in ITEMWEAPONS["shield"]):
							Player.customAttributes["stats"]["equipment"]["WEAPONS"]["shield"] = MOUSE_HOVER_ID
						elif (MOUSE_HOVER_ID in ITEMWEAPONS["bow"]):
							Player.customAttributes["stats"]["equipment"]["WEAPONS"]["bow"] = MOUSE_HOVER_ID
						else:
							raise Exception("<qkuldo>the item is classified as a weapon but is not in the list of weapons</qkuldo>")
						SFX["equipItem"].play()
						playerSword.asset = pg.transform.scale(weaponAssets[MOUSE_HOVER_ID], (TILESIZE,TILESIZE))
					elif (isWeapon and isEquipped):
						if (MOUSE_HOVER_ID in ITEMWEAPONS["sword"]):
							Player.customAttributes["stats"]["equipment"]["WEAPONS"]["sword"] = None
						elif (MOUSE_HOVER_ID in ITEMWEAPONS["shield"]):
							Player.customAttributes["stats"]["equipment"]["WEAPONS"]["shield"] = None
						elif (MOUSE_HOVER_ID in ITEMWEAPONS["bow"]):
							Player.customAttributes["stats"]["equipment"]["WEAPONS"]["bow"] = None
						else:
							raise Exception("<qkuldo>the item is classified as a weapon but is not in the list of weapons</qkuldo>")
						playerSword.asset = pg.transform.scale(weaponAssets[0], (TILESIZE,TILESIZE))
			HUDLAYER.blit(INVENTORY_DESCLAYER, (0, 0))
		else:
			INVENTORY_ITEM_TEXT, INVENTORY_ITEM_TEXT_RECT = modules.helper.createText((500,520), text = DEBUGTEXT)

		if (Player.customAttributes["action state"] == 0):
			Player.customAttributes["action timer"] += actionTimer_baseChange
		if (Player.customAttributes["action timer"] >= actionTimer_max):
			Player.customAttributes["action state"] = 1
		if (Player.customAttributes["action timer"] <= 0 and Player.customAttributes["action state"] == 1):
			Player.customAttributes["action state"] = 0
		if (Player.customAttributes["action state"] == 1 and Player.customAttributes["action timer"] < actionTimer_max and not (attack_qte_ongoing_attack or playerSword.customAttributes["visible"])):
			if (not comboSlowdown):
				Player.customAttributes["recovery timer"] += actionTimer_recoveryChange
			else:
				Player.customAttributes["recovery timer"] += actionTimer_recoveryChange/2
			if (Player.customAttributes["recovery timer"] >= 50):
				Player.customAttributes["action timer"] += 16
				Player.customAttributes["recovery timer"] = 0
				if (Player.customAttributes["action timer"] > 100):
					Player.customAttributes["action timer"] = 100
		elif (Player.customAttributes["action state"] == 0):
			Player.customAttributes["recovery timer"] = 0
		if (debugMode > 0):
			DEBUGLAYER.blit(test_text, test_text_rect)
			DEBUGLAYER.blit(clock_text, clock_text_rect)
			if (debugMode == 2):
				pg.draw.circle(DEBUGLAYER, BRIGHTYELLOW, (SCREENWIDTH/2,SCREENHEIGHT/2), 5)
				for enemy in enemyList:
					pg.draw.rect(DEBUGLAYER,ORANGE,enemy.hitbox)
					extended_endpoint = modules.helper.goto_angle(3000, enemy.customAttributes["target angle"])
					pg.draw.line(DEBUGLAYER,GREEN,enemy.hitbox.center,(enemy.hitbox.center[0]-extended_endpoint[0], enemy.hitbox.center[1]-extended_endpoint[1]), 2)
				for dataIndex in range(0, len(distanceList)):
					data = distanceList[dataIndex]
					distance = distances[dataIndex]
					if (distance == distances[0]):
						pg.draw.line(DEBUGLAYER, WHITE, data["position"], Player.hitbox.center, 2)
					elif (distance == distances[-1]):
						pg.draw.line(DEBUGLAYER, ORANGE, data["position"], Player.hitbox.center, 2)
					else:
						pg.draw.line(DEBUGLAYER, PALEBLUE, data["position"], Player.hitbox.center, 2)
				pg.draw.rect(DEBUGLAYER,WHITE,Player.hitbox)
				pg.draw.rect(DEBUGLAYER,BRIGHTYELLOW,attackHitbox)
				if (Player.customAttributes["target pos"] != None):
					pg.draw.circle(DEBUGLAYER, BRIGHTYELLOW, Player.customAttributes["target pos"], 5)
				if (keys[pg.K_n] and menuPressCooldown <= 0):	
					comboSlowdown = not comboSlowdown
					if (not comboSlowdown):
						was_comboSlowdown = True
					start_zoomLevel = copy.deepcopy(zoom_level)
					zoomStep = 0.001
					menuPressCooldown = MENUPRESSTIME
			elif (debugMode == 3):
				if (keys[pg.K_f]):
					Player.customAttributes["stats"]["health"] -= 1
				if (keys[pg.K_g]):
					Player.customAttributes["stats"]["health"] += 1
				if (keys[pg.K_h] and menuPressCooldown <= 0):
					menuPressCooldown = MENUPRESSTIME
					Player.customAttributes["apply knockback"] = True
					Player.customAttributes["hit angle"] = DIRECTION_ANGLES[list(DIRECTION_IDS.values()).index(Player.customAttributes["facingDirection"])]
					pg.time.set_timer(PLAYER_HITSTART, 200, 1)
					pg.time.set_timer(PLAYER_HITSTOP, 1000, 1)

		for itemIndex in range(0, len(currentRoomData["items"])):
			item = currentRoomData["items"][itemIndex]
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
					if (ITEMDATA["RESPAWN RATES"][item.customAttributes["itemID"]] != -1):
						temp_cache["item timers"][current_room].append({
								"item index":itemIndex,
								"time":ITEMDATA["RESPAWN RATES"][item.customAttributes["itemID"]],
								"start time":pg.time.get_ticks()
							})
					else:
						cache["item inactivators"][current_room].add(itemIndex)
					if (item.customAttributes["itemID"] in Player.customAttributes["inventory"]):
						Player.customAttributes["inventory"][item.customAttributes["itemID"]] += 1
					else:
						Player.customAttributes["inventory"][item.customAttributes["itemID"]] = 1
					if (ITEMTYPEIDS[item.customAttributes["itemID"]] in ("weapon", "armor")):
						SFX["special_ItemCollect"].play()
						itemText = ITEMIDS[item.customAttributes["itemID"]]
						specialPickupText, specialPickupTextRect = modules.helper.createText((0,0), text = f"You got a {itemText}!", color=BRIGHTYELLOW)
						specialPickupVisible = True
						start_zoomLevel = copy.deepcopy(zoom_level)
						zoomStep = 0.001
						comboSlowdown = True
						zoom_level = 1
						pg.time.set_timer(SPECIALPICKUPSTAY, 2700)
						pg.time.set_timer(START_FADEOUT,1890)
						specialItem.fill((0,0,0,0))
						specialItem = pg.transform.scale(item.asset, (TILESIZE, TILESIZE))
					else:
						SFX["itemCollect"].play()
		if (not (specialPickupVisible or drawHud)):
			for timerKey in list(temp_cache["hit cooldowns"]):
				timer = temp_cache["hit cooldowns"][timerKey]
				if (modules.helper.timerFinishCheck(current_time, timer["start time"], timer["duration"])):
					del temp_cache["hit cooldowns"][timerKey]
		if (Player.customAttributes["visible"]):
			Player.draw(Player.customAttributes["currentFrame"], SPRITELAYER, frameRow = Player.customAttributes["frameRow"])
			#if (playerSword.customAttributes["visible"]):
			#	Player.draw(Player.customAttributes["currentFrame"], SPRITELAYER, offset = (-modules.helper.goto_angle(50, playerSword.angle)[0],-modules.helper.goto_angle(50, playerSword.angle)[1]))
			#else:
			#	Player.draw(Player.customAttributes["currentFrame"], SPRITELAYER)
		if (debugMode == 2):
			#debug shenanigans part 2: electric boogaloo
			if (debugSecMode == 0):
				dataDisplayText, dataDisplayRect = modules.helper.createText((Player.hitbox.midtop[0],Player.hitbox.midtop[1]-10),2,f"{Player.coordinates[0]:.2f},{Player.coordinates[1]:.2f}",ORANGE)
				DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
				if (Player.customAttributes["target pos"] != None):
					dataDisplayText, dataDisplayRect = modules.helper.createText((Player.hitbox.midtop[0],Player.hitbox.midtop[1]-30),2,f"{Player.customAttributes["target pos"][0]:.2f},{Player.customAttributes["target pos"][1]:.2f}",ORANGE)
				else:
					dataDisplayText, dataDisplayRect = modules.helper.createText((Player.hitbox.midtop[0],Player.hitbox.midtop[1]-30),2,"what target?",ORANGE)
				DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
			elif (debugSecMode == 1):
				healthFormatting = str(Player.customAttributes["stats"]["health"]) + "/" + str(Player.customAttributes["stats"]["max health"])
				dataDisplayText, dataDisplayRect = modules.helper.createText((Player.hitbox.midtop[0],Player.hitbox.midtop[1]-10),2,healthFormatting,BRIGHTYELLOW)
				DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
				dataDisplayText, dataDisplayRect = modules.helper.createText((Player.hitbox.midtop[0],Player.hitbox.midtop[1]-30),2,str(Player.customAttributes["stats"]["defense"]),BRIGHTYELLOW)
				DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
				dataDisplayText, dataDisplayRect = modules.helper.createText((Player.hitbox.midtop[0],Player.hitbox.midtop[1]-50),2,str(Player.customAttributes["stats"]["weight"]),BRIGHTYELLOW)
				DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
				weaponFormatting = str(Player.customAttributes["stats"]["equipment"]["WEAPONS"]["sword"]) + "," + str(Player.customAttributes["stats"]["equipment"]["WEAPONS"]["shield"]) + "," + str(Player.customAttributes["stats"]["equipment"]["WEAPONS"]["bow"])
				dataDisplayText, dataDisplayRect = modules.helper.createText((Player.hitbox.midtop[0],Player.hitbox.midtop[1]-70),2,weaponFormatting,BRIGHTYELLOW)
				DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
			else:
				directionFormatting = list(DIRECTION_IDS.keys())[list(DIRECTION_IDS.values()).index(Player.customAttributes["facingDirection"])]
				dataDisplayText, dataDisplayRect = modules.helper.createText((Player.hitbox.midtop[0],Player.hitbox.midtop[1]-10),2,directionFormatting,BLUE)
				DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
				dataDisplayText, dataDisplayRect = modules.helper.createText((Player.hitbox.midtop[0],Player.hitbox.midtop[1]-30),2,str(Player.customAttributes["visible"]),BLUE)
				DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
				dataDisplayText, dataDisplayRect = modules.helper.createText((Player.hitbox.midtop[0],Player.hitbox.midtop[1]-50),2,str(Player.customAttributes["currentFrame"]) + "," + str(Player.customAttributes["frameRow"]),BLUE)
				DEBUGLAYER.blit(dataDisplayText, dataDisplayRect)
		if ((not (Player.customAttributes["targeting"] or comboSlowdown or specialPickupVisible) and zoomStep > 0) and zoom_level > 1):
			start_zoomLevel = copy.deepcopy(zoom_level)
			zoomStep = 0.001
		if ((Player.customAttributes["targeting"] or comboSlowdown or specialPickupVisible) and zoomStep < 1):
			if (not specialPickupVisible):
				zoomStep += 0.1
			else:
				zoomStep += 0.05
		if (specialPickupFade):
			zoom_level = modules.helper.lerp(start_zoomLevel, 1, zoomStep)
		elif (specialPickupVisible):
			zoom_level = modules.helper.lerp(start_zoomLevel, 1.5, zoomStep)
		elif (comboSlowdown):
			zoom_level = modules.helper.lerp(start_zoomLevel, 1.5, zoomStep)
		elif (Player.customAttributes["targeting"]):
			zoom_level = modules.helper.lerp(start_zoomLevel, 1.25, zoomStep)
		else:
			if (zoomStep < 1):
				zoomStep += 0.1
			zoom_level = modules.helper.lerp(start_zoomLevel, 1, zoomStep)
		if (not specialPickupVisible):
			for exit in currentRoomData["exits"]:
				if (exit.colliderect(Player.hitbox) and not currentRoomData["contained exits"][currentRoomData["exits"].index(exit)]):
					exitID = currentRoomData["exit IDs"][currentRoomData["exits"].index(exit)]
					PREVCOMBINELAYER = TILELAYER.copy()
					PREVCOMBINELAYER.blit(SPRITELAYER, (0,0))
					current_room = currentRoomData["exit returns"][currentRoomData["exits"].index(exit)]
					givenExitData = currentRoomData["exits"][:]
					if (not current_room in list(cache["item inactivators"].keys())):
						cache["item inactivators"][current_room] = set()
					if (not current_room in list(temp_cache["item timers"].keys())):
						temp_cache["item timers"][current_room] = []
					modules.helper.roomTransition(PREVCOMBINELAYER, center=Player.hitbox.center, duration=2500, circleRadius=600, radiusChange=15)
					currentRoomData = loadRoom(current_room,TILELAYER,itemAssets,inactiveItems=cache["item inactivators"][current_room] | modules.helper.unpack_nestedDict(temp_cache["item timers"][current_room], "item index"))
					Player.coordinates = list(modules.helper.findTilePixelLocation(currentRoomData["exit tp coordinates"][currentRoomData["exit IDs"].index(exitID)][0],currentRoomData["exit tp coordinates"][currentRoomData["exit IDs"].index(exitID)][1]))
					Player.update(rectOperation = (Player.coordinates[0]+12,Player.coordinates[1]+18))
					for exitIndex in range(0, len(currentRoomData["exits"])):
						if (currentRoomData["exits"][exitIndex].colliderect(Player.hitbox)):
							currentRoomData["contained exits"][exitIndex] = True
					CURRENTCOMBINELAYER = modules.helper.initDrawLayer().convert_alpha()
					CURRENTCOMBINELAYER.fill((0,0,15))
					loadRoom(current_room,CURRENTCOMBINELAYER,itemAssets,False,roomFrame)
					Player.draw(Player.customAttributes["currentFrame"], SPRITELAYER, frameRow = Player.customAttributes["frameRow"])
					CURRENTCOMBINELAYER.blit(SPRITELAYER, (0,0))
					modules.helper.roomTransition(CURRENTCOMBINELAYER, center=Player.hitbox.center, duration=1000, circleRadius=300, radiusChange=15, mode=1)
					modules.helper.clearLayer(TILELAYER)
					modules.helper.clearLayer(SPRITELAYER)
					playerSword.customAttributes["moving"] = False
					playerSword.customAttributes["visible"] = False
					Player.customAttributes["speed divider"] = 1
					playerSword.customAttributes["offset"] = 0
					attack_qte_success = True
					on_attack_button_cooldown = False
					timedRect_fill = False
					attack_qte_ongoing_attack = False
					Player.customAttributes["attempted qte"] = True
					timedRect = pg.Rect(0, 0, 0, TILESIZE//5)
					pg.time.set_timer(ATTACK_QTE_END, 0)
					pg.time.set_timer(ATTACK_BUTTON_COOLDOWN, 0)
					break
				elif (currentRoomData["contained exits"][currentRoomData["exits"].index(exit)] and not exit.colliderect(Player.hitbox)):
					currentRoomData["contained exits"][currentRoomData["exits"].index(exit)] = False

		for timer in temp_cache["item timers"][current_room]:
			if (current_time-timer["start time"] >= timer["time"]):
				temp_cache["item timers"][current_room].remove(timer)
			continue

		if ((attack_qte_ongoing_attack or playerSword.customAttributes["visible"]) and Player.customAttributes["targeting"]):
			posMatch = next((enemy for enemy in enemyList if (enemy.customAttributes["name"] == Player.customAttributes["target name"])), None)
			if (posMatch != None):
				Player.customAttributes["target pos"] = posMatch.hitbox.center
			target_angle += 2
			TARGETRECT = pg.transform.rotate(TARGET, target_angle).get_rect()
			TARGETRECT.center = Player.customAttributes["target pos"]
			AFFECTED_INFOLAYER.blit(pg.transform.rotate(LOCKEDTARGET, target_angle), TARGETRECT)
		elif (attack_qte_ongoing_attack and not playerSword.customAttributes["visible"]):
			faceAngle = modules.helper.face_target(Player.hitbox.center, copy.copy(Player.customAttributes["target pos"]))
			UNTARGETRECT = pg.transform.rotate(LOCKEDUNTARGET, faceAngle).get_rect()
			UNTARGETRECT.center = (Player.hitbox.center[0]-modules.helper.goto_angle(30,faceAngle)[0],Player.hitbox.center[1]-modules.helper.goto_angle(30,faceAngle)[1])
			AFFECTED_INFOLAYER.blit(pg.transform.rotate(LOCKEDUNTARGET, faceAngle), UNTARGETRECT)
		if (timedRect_fill):
			attack_qte_power += timedRect_fillRate
			timedRect.width = attack_qte_power
			pg.draw.rect(AFFECTED_INFOLAYER, DARKBLUE, timedRectBG)
			pg.draw.rect(AFFECTED_INFOLAYER, BLUE, timedRectBG,3)
		#draw circle function below is for testing purposes
		pg.draw.rect(AFFECTED_INFOLAYER, BRIGHTYELLOW, timedRect)

		if (playerSword.customAttributes["visible"]):
			playerSword.coordinates = (playerSword.hitbox.x-modules.helper.goto_angle(50,playerSword.angle+playerSword.customAttributes["offset"])[0], playerSword.hitbox.y-modules.helper.goto_angle(50,playerSword.angle+playerSword.customAttributes["offset"])[1])
			playerSword.draw(0, SPRITELAYER, angleOffset=playerSword.customAttributes["offset"])
			SPRITELAYER.blit(pg.transform.rotate(hand, playerSword.angle+playerSword.customAttributes["offset"]), (Player.hitbox.center[0]-modules.helper.goto_angle(35,playerSword.angle+playerSword.customAttributes["offset"])[0], Player.hitbox.center[1]-modules.helper.goto_angle(35,playerSword.angle+playerSword.customAttributes["offset"])[1]))

		if (specialPickupVisible):
			SPRITELAYER.blit(specialPickupText, specialPickupTextRect)
			SPRITELAYER.blit(specialItem, specialItemRect)

		if (not debugMode):
			pg.draw.rect(INFOLAYER, PALEBLUE, playerMaxHealthRect)
			pg.draw.rect(INFOLAYER, BLUE, playerHealthRect)
			pg.draw.rect(INFOLAYER, DARKBLUE, playerMaxHealthRect.inflate(5,5),5)
			pg.draw.rect(INFOLAYER, DARKBLUE, playerMaxActionRect)
			if (Player.customAttributes["action state"] == 0):
				pg.draw.rect(INFOLAYER, BLUE, playerActionRect)
			else:
				pg.draw.rect(INFOLAYER, GREEN, playerActionRect)
			if (Player.customAttributes["action state"] == 1):
				if (actionTimerFailingMark):
					pg.draw.rect(INFOLAYER, ORANGE, playerActionCostRect)
				else:
					pg.draw.rect(INFOLAYER, PALEGREEN, playerActionCostRect)
			pg.draw.rect(INFOLAYER, BRIGHTYELLOW, playerRecoveryRect)
			INFOLAYER.blit(healthText, healthTextRect)
			INFOLAYER.blit(HPBARDESIGN, (0,20))
			INFOLAYER.blit(pg.transform.scale(ICONS.load_frame(4), (32,32)), (ACTIONBAR_COORDINATES[0]-32, ACTIONBAR_COORDINATES[1]-3))
		BASELAYER.fill(BGCOLOR)
		if (((not drawHud) or (drawHud and Player.hitbox.center[1] < 420))):
			BASELAYER.blit(TILELAYER,(0,0))
			BASELAYER.blit(SPRITELAYER, (0,0))
			BASELAYER.blit(AFFECTED_INFOLAYER, (0,0))
			screen.blit(INFOLAYER, (0,0))
		elif (drawHud and Player.hitbox.center[1] > 420):
			BASELAYER.blit(TILELAYER,(0,(420-Player.coordinates[1])-30))
			BASELAYER.blit(SPRITELAYER, (0,(420-Player.coordinates[1])-30))
		BASELAYER.blit(DEBUGLAYER, (0,0))
		if (player_CenterOffset[0] > zoom_reveal_outOfBounds[0]):
			player_CenterOffset[0] = zoom_reveal_outOfBounds[0]
		elif (player_CenterOffset[0] < -zoom_reveal_outOfBounds[0]):
			player_CenterOffset[0] = -zoom_reveal_outOfBounds[0]
		if (player_CenterOffset[1] > zoom_reveal_outOfBounds[1]):
			player_CenterOffset[1] = zoom_reveal_outOfBounds[1]
		elif (player_CenterOffset[1] < -zoom_reveal_outOfBounds[1]):
			player_CenterOffset[1] = -zoom_reveal_outOfBounds[1]
		if (zoom_level > 1):
			CAMERALAYER.blit(BASELAYER, player_CenterOffset)
		else:
			CAMERALAYER.blit(BASELAYER)
		CAMERA_ZOOMED_RECT = pg.transform.scale(CAMERALAYER, (SCREENWIDTH*zoom_level, SCREENHEIGHT*zoom_level)).get_rect()
		CAMERA_ZOOMED_RECT.center = (SCREENWIDTH/2,SCREENHEIGHT/2)
		screen.blit(pg.transform.scale(CAMERALAYER, (SCREENWIDTH*zoom_level, SCREENHEIGHT*zoom_level)), CAMERA_ZOOMED_RECT)
		if (((not drawHud) or (drawHud and Player.hitbox.center[1] < 420)) and (not specialPickupVisible)):
			screen.blit(INFOLAYER, (0,0))
		if (drawHud):
			screen.blit(HUDLAYER,(0,0))
		if (keys[pg.K_o] and debugMode == 3):
			modules.helper.roomTransition(BASELAYER, center=Player.hitbox.center, duration=1500, circleRadius=600, radiusChange=15)
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
	modules.helper.loadTileSpritesheets(walltileSpritesheets, proptileSpritesheets)
	game()