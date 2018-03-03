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
	move = get_move(health, walls, head)
	previousMove = move
	print (move, previousMove)
	
	return {
		'move': move,
		'taunt': 'It\'s Blake the Snake!'
	}


def get_move(health, walls, head):
	directions = ['up', 'down', 'left', 'right']
	up = 0
	down = 1
	left = 2
	right = 3
	remove = [0,0,0,0]
	
	if(previousMove is 'up'):
		remove[down] = 1
	elif(previousMove is 'down'):
		remove[up] = 1
	elif(previousMove is 'left'):
		remove[right] = 1
	elif(previousMove is 'right'):
		remove[left] = 1
		
	if(head[1] <= 1):
		remove[down] = 1
	elif(head[1] >= (walls[1]-1)):
		remove[up] = 1
		
	if(head[0] <= 1):
		remove[left] = 1
	elif(head[0] >= (walls[0]-1)):
		remove[right] = 1
	
	directions = [d for i, d in enumerate(directions) if remove[i] is 1]
	
	if(previousMove in directions):
		return previousMove
	else:
		return random.choice(directions)
	
	
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
