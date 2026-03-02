import game
game.readAllJsonData()

def levelGet(currentRoom):
	roomLayout = list(game.ROOMTILEDATA[currentRoom].values())[3:18]
	for tile in roomLayout:
		print(tile)
levelGet("test")