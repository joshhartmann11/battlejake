import bottle
import os
import random

grid = [[0]*5]*5

previousMove = 'none'

@bottle.route('/')
def static():
	return "the server is running"


@bottle.route('/static/<path:path>')
def static(path):
	return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
	
	headUrl = '%s://%s/static/head.png' % (
		bottle.request.urlparts.scheme,
		bottle.request.urlparts.netloc
	)
	
	return {
		'color': '#00FF00',
		'taunt': '{} ({}x{})',
		'head_url': headUrl
	}


@bottle.post('/move')
def move():

	global previousMove
	
	data = bottle.request.json
	
	you = data.get('you')
	health = you["health"]
	body = you['body']['data']
	head = (body[0]['x'], body[0]['y'])
	walls = (data.get('width'), data.get('height'))
	
	add_walls(walls, head)
	moves = get_restrictions(head, walls, None)
	print 'moves: ', moves
	if(previousMove in moves):
		move = previousMoves
	else:
		move = random.choice(moves)
	previousMove = move
	print 'move' + move
	
	return {
		'move': move,
		'taunt': 'It\'s Blake the Snake!'
	}


def get_restrictions(head, walls, snakes):
	directions = {'up':1, 'down':1, 'left':1, 'right':1}
	
	print 'previousMove: ' + previousMove 
	
	# Don't go back on it's self
	if(previousMove is 'up'):
		directions['down'] = 0
	elif(previousMove is 'down'):
		directions['up'] = 0
	elif(previousMove is 'left'):
		directions['right'] = 0
	elif(previousMove is 'right'):
		directions['left'] = 0
	
	# Don't run into a wall
	if(head[1] <= 0):
		directions['down'] = 0
	elif(head[1] >= walls[1]):
		directions['up'] = 0
	if(head[0] <= 0):
		directions['left'] = 0
	elif(head[0] >= walls[0]):
		directions['right'] = 0
	
	# Don't hit other snakes
	
	
	moves = [d for k in enumerate(directions.keys()) if directions[k] is 0]
	
	return moves
	
	
def add_walls(walls, head):
	print head
	

def add_myself(myself, head):
	pass


def add_snakes(snakes, head):
	pass

def add_food(food, head):
	pass


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug = True)
