import pygame as pg
import modules.spritesheet as sheets

class Sprite:
	"""handles interactable/controllable/moving objects"""
	def __init__(self, asset, coordinates, speed, spriteScale=(0,0), hitboxScale=(16,16), hitboxLocation=(0,0), angle=0 ,customAttributes={}):
		#if spriteScale = (0,0), no scaling function will be used when drawing sprite. Else, scaling function will use spriteScale attribute for scaling
		self.asset = asset
		self.coordinates = coordinates
		self.speed = speed
		self.customAttributes = customAttributes
		self.spriteScale = spriteScale
		self.hitbox = pg.Rect(hitboxLocation,hitboxScale)
		self.moved = False
		self.angle = angle
	def siMove(self,movement_line,operation):
		#to check for collisions
		dummy = self.createDummy()
		if (operation == 1):
			if (movement_line == 1):
				dummy.y += self.speed
			elif (movement_line == 0):
				dummy.x += self.speed
		elif (operation == -1):
			if (movement_line == 1):
				dummy.y -= self.speed
			elif (movement_line == 0):
				dummy.x -= self.speed
		return dummy
	def createDummy(self):
		#to check for collisions for non-default movement
		dummy = self.hitbox.copy()
		return dummy
	def move(self, movement_line, operation):
		#movement_line is 0 for x, 1 for y, operation is 1 for positive, -1 for negative
		if (operation == 1):
			self.coordinates[movement_line] += self.speed
		elif (operation == -1):
			self.coordinates[movement_line] -= self.speed
		self.moved = True
	def draw(self, frame, layer, offset = (0,0)):
		drawCoordinates = (self.coordinates[0]+offset[0],self.coordinates[1]+offset[1])
		drawSurf = None
		if (type(self.asset) == sheets.Spritesheet):
			if (self.spriteScale != (0,0)):
				drawSurf = pg.transform.scale(self.asset.load_frame(frame),self.spriteScale)
			else:
				drawSurf = self.asset.load_frame(frame)
		elif (type(self.asset) == pg.Surface):
			if (self.spriteScale != (0,0)):
				drawSurf = pg.transform.scale(self.asset,self.spriteScale)
			else:
				drawSurf = self.asset
		drawSurf = pg.transform.rotate(drawSurf, self.angle)
		layer.blit(drawSurf, drawCoordinates)
	def update(self, rectOperation=None):
		#if rectOperation = None, hitbox topleft will default to player coordinates\
		if (rectOperation != None):
			self.hitbox.topleft = rectOperation
		else:
			self.hitbox.topleft = self.coordinates
