import bottle
import os
import random

previousMove = 'none'

'''
0 nothing
1 wall
2 snake
3 head
4 anything
'''

scenarios = [
	{'scene':	[[0,0,0,0,0,0,0],
	 			 [0,0,0,0,0,0,0],
	 			 [0,0,0,0,0,0,0],
	 			 [0,0,0,0,0,0,0],
	 			 [0,0,0,0,0,0,0],
	 			 [0,0,0,0,0,0,0]], 'move': 'left'}
]

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
		'taunt': 'Wake up Blake, you\'re a snake',
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
	#food = [x,y for x, y in zip(you['food']['data']['x'], you['food']['data']['x'])]
	
	add_walls(walls, head)
	moves = get_restrictions(head, walls, None)
	print 'moves: ', moves
	if(previousMove in moves):
		move = previousMove
	else:
		move = random.choice(moves)
	previousMove = move
	print 'move: ' + move
	
	return {
		'move': move,
		'taunt': 'It\'s Blake the Snake!'
	}


def get_restrictions(head, walls, snakes):

	directions = {'up':1, 'down':1, 'left':1, 'right':1}
	
	print "previousMove: " + previousMove
	
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
	
	moves = [k for k in directions.keys() if directions[k] is 1]
	
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
