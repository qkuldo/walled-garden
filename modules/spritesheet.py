import pygame as pg
class Spritesheet:
	"""Class for extracting individual frames from spritesheets."""
	def __init__(self,sheet,width,height):
		self.sheet = sheet
		self.width = width
		self.height = height
	def load_frame(self,frame):
		# Load and return a specific frame from the spritesheet.
		image = pg.Surface((self.width,self.height)).convert()
		image.blit(self.sheet,(0,0),((frame*self.width),0,self.width,self.height))
		image.set_colorkey((0,0,0))
		return image