import pygame as pg
import json, sys, os, math, random, copy
import modules.sprite as sprite
import modules.spritesheet as sheets
SCREENWIDTH = 1280
SCREENHEIGHT = 720
BASEIMGPATH = "assets/"
TILESIZE = 48
pg.font.init()
BIGDISPLAYFONT_BOLD = pg.font.Font("font/PixelifySans-Bold.ttf", 30)
SMALLDISPLAYFONT_BOLD = pg.font.Font("font/PixelifySans-Bold.ttf", 15)
MEDIUMDISPLAYFONT_BOLD = pg.font.Font("font/PixelifySans-Bold.ttf", 25)
DIRECTION_IDS = {
"left":0,
"right":1,
"up":2,
"down":3
}
screen = pg.Surface((1,1))
clock = pg.time.Clock()
FPS = 30
namecharacters = "abcdefghijklmnopqrstuvwxyz"
#enemy finite state machine states
IDLE = 0
PURSUING = 1
WINDUP = 2
ATTACK = 3
RECOVERY = 4
HITSTUN = 5
#the direction order the enemy looks in during idle state
LOOKSEQUENCE = (3,0,2,1)
DIRECTION_ANGLES = (90,270,0,180)

def generateName(length=1):
	return "".join(random.choices(namecharacters, k=length))

def setVeryImportants(surface, clockObject):
	"""sets the main blitting surface and the clock"""
	global screen, clock
	screen = surface
	clock = clockObject
def measureDistance(pos1,pos2):
	"""measures euclidian distance between 2 points"""
	output = [(pos1[0]-pos2[0]) ** 2,(pos1[1]-pos2[1]) ** 2]
	#square roots values
	output = (output[0]+output[1])**0.5
	return output
def loadImages(path):
	"""returns a list of pygame surfaces of .png images within the folder corresponding to the path parameter and a list of all .png filenames without the file extension"""
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
def loadTileSpritesheets(walltileSpritesheets, proptileSpritesheets):
	tileImages,tileNames = loadImages("tiles/")
	wallbunchID, propbunchID = "walltile", "proptile"
	for tilebunch in tileImages:
		if (wallbunchID in tileNames[tileImages.index(tilebunch)]):
			walltileSpritesheets.append(sheets.Spritesheet(tilebunch,16,16))
		elif (propbunchID in tileNames[tileImages.index(tilebunch)]):
			proptileSpritesheets.append(sheets.Spritesheet(tilebunch,16,16))
		else:
			raise Exception("<qkuldo> one of the tile sheets is not properly named. pls use walltile prefix for walls and proptile prefix for props. goodbye! </qkuldo>")
	#print("tile spritesheets successfully loaded")
def readJsonFile(path):
	#loads path file with json.load
	with open(path, "r") as file:
		#more rhyme!
		data = json.load(file)
		file.close()
	return data
def addItem(itemList, itemID, coordinates, assets):
	"""Appends item sprites to a list
	itemList - list sprite is appended to
	itemID - the index in ITEMIDS
	coordinates - where the coordinate attribute of the sprite will be
	assets - the list of all item assets
	"""
	itemList.append(sprite.Sprite(assets[itemID], coordinates, 0, spriteScale=[TILESIZE,TILESIZE], hitboxScale=[TILESIZE,TILESIZE], customAttributes = {
					"itemID":itemID,
					"fromGroundOffset":0,
					"oscillate":0,
					"active":True
				}))
def timerFinishCheck(currentTime, startTime, duration):
	return currentTime - startTime >= duration
def moveEnemy(enemy, data, currentRoomData, Player, currentTime, isHit=False, slowdown=False, deltaTime=0):
	movement_vector = (0, 0)
	checkCollisionList = copy.deepcopy(currentRoomData["collisionBoxes"])
	checkCollisionList.append(Player.hitbox)
	distance_fromPlayer = measureDistance(Player.hitbox.center, enemy.hitbox.center)
	if (not slowdown):
		durationMultiplier = 1
	else:
		durationMultiplier = 2
	if (data["FLAGS"][2] in enemy.customAttributes["flags"]):
		longHitstunMultiplier = 1
		if (enemy.customAttributes["strong attack"] == True):
			longHitstun = 2
		if (enemy.customAttributes["state"] == 1):
			if (distance_fromPlayer < 500 and distance_fromPlayer > enemy.customAttributes["pursue distance"]):
				enemy.customAttributes["state"] = PURSUING
			elif (distance_fromPlayer <= enemy.customAttributes["pursue distance"]):
				enemy.customAttributes["state"] = WINDUP
				enemy.customAttributes["state timer start"] = currentTime
				enemy.customAttributes["target angle"] = face_target(enemy.hitbox.center, Player.hitbox.center)
		if (enemy.customAttributes["state"] == WINDUP):
			if (timerFinishCheck(currentTime, enemy.customAttributes["state timer start"], enemy.customAttributes["windup duration"]*durationMultiplier)):
				enemy.customAttributes["state timer start"] = currentTime
				enemy.customAttributes["state"] = ATTACK
		if (enemy.customAttributes["state"] == ATTACK):
			if (timerFinishCheck(currentTime, enemy.customAttributes["state timer start"], enemy.customAttributes["attack duration"]*durationMultiplier)):
				enemy.customAttributes["state timer start"] = currentTime
				enemy.customAttributes["state"] = RECOVERY
				enemy.customAttributes["random steer"] = random.randint(-enemy.customAttributes["steer offset"],enemy.customAttributes["steer offset"])
		if (enemy.customAttributes["state"] == RECOVERY):
			if (timerFinishCheck(currentTime, enemy.customAttributes["state timer start"], enemy.customAttributes["recovery duration"]*durationMultiplier)):
				enemy.customAttributes["state timer start"] = currentTime
				enemy.customAttributes["state"] = PURSUING
		if (enemy.customAttributes["state"] == HITSTUN):
			if (timerFinishCheck(currentTime, enemy.customAttributes["state timer start"], enemy.customAttributes["hitstun duration"]*durationMultiplier)):
				enemy.customAttributes["state timer start"] = currentTime
				enemy.customAttributes["strong attack"] = False
				enemy.customAttributes["random steer"] = random.randint(-enemy.customAttributes["steer offset"],enemy.customAttributes["steer offset"])
				if (distance_fromPlayer <= enemy.customAttributes["pursue distance"]):
					enemy.customAttributes["state"] = WINDUP
				else:
					enemy.customAttributes["state"] = PURSUING
		if (enemy.customAttributes["state"] == IDLE):
			enemy.customAttributes["debug"] = basicIdle(enemy, durationMultiplier, currentTime, Player, deltaTime)
		if (enemy.customAttributes["state"] == PURSUING):
			movement_vector = goto_angleComplex(enemy, speed_multiplier=1, angle=face_target(enemy.hitbox.center, Player.hitbox.center)+enemy.customAttributes["random steer"], targetPos=Player.hitbox.center, checkCollision=True, collisionList=checkCollisionList, setDir = True) 
		elif (enemy.customAttributes["state"] == ATTACK):
			movement_vector = goto_angleComplex(enemy, speed_multiplier=2, angle=enemy.customAttributes["target angle"], targetPos=Player.hitbox.center, checkCollision=True, collisionList=currentRoomData["collisionBoxes"], setDir = True)
		if (not slowdown):
			enemy.coordinates[0] += movement_vector[0]
			enemy.coordinates[1] += movement_vector[1]
		else:
			enemy.coordinates[0] += movement_vector[0]/2
			enemy.coordinates[1] += movement_vector[1]/2
	if (data["FLAGS"][3] in enemy.customAttributes["flags"]):
		if (enemy.customAttributes["state"] == IDLE):
			enemy.customAttributes["debug"] = basicIdle(enemy, durationMultiplier, currentTime, Player, deltaTime)
def basicIdle(enemy,durationMultiplier, currentTime, Player, deltaTime):
	#base idle function for enemies
	if (timerFinishCheck(currentTime, enemy.customAttributes["look timer start"], enemy.customAttributes["look duration"]*durationMultiplier) and enemy.customAttributes["player see timer"] == 0):
		enemy.customAttributes["look timer start"] = currentTime
		lookSequence_index = LOOKSEQUENCE.index(copy.deepcopy(enemy.customAttributes["facingDirection"]))+1
		if (lookSequence_index > len(LOOKSEQUENCE)-1):
			lookSequence_index = 0
		enemy.customAttributes["facingDirection"] = LOOKSEQUENCE[lookSequence_index]
		enemy.customAttributes["target angle"] = DIRECTION_ANGLES[enemy.customAttributes["facingDirection"]]
	#reverse up & down angles because it's simpler than fixing the bug fully
	#if (enemy.customAttributes["target angle"] == 180):
	#	useAngle = 0
	#elif (enemy.customAttributes["target angle"] == 0):
	#	useAngle = 180
	#else:
	useAngle = enemy.customAttributes["target angle"]
	targetAngleOffsets = (useAngle-enemy.customAttributes["looking offset"],useAngle+enemy.customAttributes["looking offset"])
	playerFindAngle = face_target(enemy.hitbox.center, Player.hitbox.center)
	if (betweenAngles(targetAngleOffsets[0], targetAngleOffsets[1], playerFindAngle)):
		enemy.customAttributes["player see timer"] += deltaTime
		enemy.customAttributes["look timer start"] = copy.deepcopy(currentTime)
		if (enemy.customAttributes["player see timer"] >= enemy.customAttributes["aggression time"]):
			enemy.customAttributes["state"] = PURSUING
			enemy.customAttributes["random steer"] = random.randint(-enemy.customAttributes["steer offset"],enemy.customAttributes["steer offset"])
	else:
		enemy.customAttributes["player see timer"] = 0
	return betweenAngles(targetAngleOffsets[0], targetAngleOffsets[1], playerFindAngle, True)

def betweenAngles(lower, upper, angle, debug=False):
    lower %= 360
    upper %= 360
    angle %= 360
    if (not debug):
    	if (lower > upper):
       	 	return angle >= lower or angle <= upper
    	return angle > lower and angle < upper
    else:
    	return (lower, upper)

def lerp(start, end, percent):
	return start+(end-start)*percent
def makeEnemy(data, type, coordinates, assetData, facingDirection):
	enemyFlags = data["FLAGS"]
	BASE_ATTRIBUTES = copy.deepcopy(data["BASE ATTRIBUTES"][type])
	CUSTOM_ATTRIBUTES = copy.deepcopy(data["CUSTOM ATTRIBUTES"][type])
	CUSTOM_ATTRIBUTES["name"] = CUSTOM_ATTRIBUTES["nameAdder"] + generateName(random.randint(5,10))
	CUSTOM_ATTRIBUTES["facingDirection"] = facingDirection
	for flag in CUSTOM_ATTRIBUTES["flags"]:
		if (not flag in enemyFlags):
			raise Exception("<qkuldo> flag " + flag + " does not exist. </qkuldo>")
		CUSTOM_ATTRIBUTES["flags"][CUSTOM_ATTRIBUTES["flags"].index(flag)] = enemyFlags[enemyFlags.index(flag)]
	CUSTOM_ATTRIBUTES["flags"] = set(CUSTOM_ATTRIBUTES["flags"])
	CUSTOM_ATTRIBUTES["facingDirection"] = 3
	CUSTOM_ATTRIBUTES["combo knockback duration"] = CUSTOM_ATTRIBUTES["knockback duration"]/2
	enemy = sprite.Sprite(assetData[type], coordinates, BASE_ATTRIBUTES["speed"], BASE_ATTRIBUTES["scale"], BASE_ATTRIBUTES["hitboxScale"], customAttributes=CUSTOM_ATTRIBUTES)
	enemy.update(CUSTOM_ATTRIBUTES["rectOperation"])
	return enemy
def goto_angle(velocity,angle):
	# Calculates a directional vector based on velocity and angle.`
	direction = pg.Vector2(0, velocity).rotate(-angle)
	return direction
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
def initDrawLayer():
	layer = pg.Surface((SCREENWIDTH,SCREENHEIGHT),pg.SRCALPHA).convert_alpha()
	return layer
def clearLayer(layer):
	#use this for tilelayer before loading a new room after exiting a previous room
	layer.fill((0,0,0,0))
def hitboxInbound(rect):
	"""checks if given rect is outside of the screen borders
	returns False if not out of bounds, returns True otherwise
	"""
	if (rect.midbottom[1] < SCREENHEIGHT and rect.midtop[1] > 0 and rect.midleft[0] > 0 and rect.midright[0] < SCREENWIDTH):
		return True
	else:
		return False
def complexMove(Sprite, movement_line,operation,currentRoomData, divider=1):
	collideChecker = Sprite.siMove(movement_line,operation, divider)
	if (collideChecker.collidelist(currentRoomData["collisionBoxes"]) == -1 and hitboxInbound(collideChecker)):
		Sprite.move(movement_line,operation,divider)
		return True
	return False
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
		textSurface = BIGDISPLAYFONT_BOLD.render(text, False, color)
	elif (font == 1):
		textSurface = SMALLDISPLAYFONT_BOLD.render(text, False, color)
	elif (font == 2):
		textSurface = MEDIUMDISPLAYFONT_BOLD.render(text, False, color)
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
def goto_angleComplex(Sprite, speed_multiplier=3, angle=0, targetPos=(SCREENWIDTH/2, SCREENHEIGHT/2), checkCollision=False, collisionList=(), setDir = True, speedDivider=1, speedOverride=None):
	#goto_angle that also sets the "facingDirection" custom attribute of sprite if setDir is True
	#returns the initial goto_angle call if checkCollision is False, else returns (0,0) if collision checks with any rect in collisionList parameter fail
	if (speedOverride == None):
		directional_vector = -goto_angle(Sprite.speed*speed_multiplier/speedDivider, angle)
	else:
		directional_vector = -goto_angle(speedOverride*speed_multiplier/speedDivider, angle)
	if (setDir):
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
	if (checkCollision):
		spriteDummy = Sprite.createDummy()
		spriteDummy.x += directional_vector[0]
		spriteDummy.y += directional_vector[1]
		if (spriteDummy.collidelist(collisionList) == -1 and hitboxInbound(spriteDummy)):
			return directional_vector
		else:
			spriteDummy = Sprite.createDummy()
			spriteDummy.x += directional_vector[0]
			if (spriteDummy.collidelist(collisionList) == -1 and hitboxInbound(spriteDummy)):
				return (directional_vector[0],0)
			spriteDummy = Sprite.createDummy()
			spriteDummy.y += directional_vector[1]
			if (spriteDummy.collidelist(collisionList) == -1 and hitboxInbound(spriteDummy)):
				return (0,directional_vector[1])
			return (0, 0)
	else:
		return directional_vector
def unpack_nestedDict(inputArray, key, returnSet = True):
	"""returns a set(if returnSet is true, otherwise it returns a list) with all the values with parameter 'key' in a nested array 'inputDict'"""
	if (returnSet):
		output = set()
	else:
		output = []
	for nestedDict in inputArray:
		if (returnSet):
			output.add(nestedDict[key])
		else:
			output.append(nestedDict[key])
	return output
def roomTransition(background, duration=1000, center=(SCREENWIDTH//2,SCREENHEIGHT//2), mode=0, circleRadius=600, radiusChange=10):
	"""if mode is 0, this function causes a tunnel transition animation with the circle getting smaller, if mode is 1 the circle gets bigger"""
	mask = initDrawLayer().convert_alpha()
	END_TRANSITION = pg.event.custom_type()
	pg.time.set_timer(END_TRANSITION, duration)
	break_signal = False
	if (mode == 1):
		maxCircleRadius = circleRadius
		circleRadius = 0
	else:
		maxCircleRadius = 0
	while True:
		for event in pg.event.get():
			if (event.type == pg.QUIT):
				terminate()
			elif (event.type == END_TRANSITION):
				break_signal = True
		screen.fill("black")
		mask.fill("black")
		if (mode == 1 and circleRadius < maxCircleRadius):
			masked = background.copy().convert_alpha()
			circleRadius += radiusChange
			pg.draw.circle(mask, (0,0,0,0), center, circleRadius)
			masked.blit(mask)
		elif (mode == 0):
			masked = background.copy().convert_alpha()
			circleRadius -= radiusChange
			pg.draw.circle(mask, (0,0,0,0), center, circleRadius)
			masked.blit(mask)
		screen.blit(masked)
		pg.draw.circle(screen, (7,5,35), center, circleRadius+5, width=10)

		pg.display.flip()
		clock.tick(FPS)
		if (break_signal):
			break
#quit that font thing