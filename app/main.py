import bottle
import os
import random

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
	
	data = bottle.request.json
	
	you = data.get('you')
	health = you["health"]
	body = you['body']['data']
	head = (body[0]['x'], body[0]['y'])
	walls = (data.get('width'), data.get('height'))
	#food = [(x,y) for x, y in zip([f['x'] for f in data['food']['data']], [f['y'] for f in data['food']['data']['x']])]
	
	pm = get_previous_move(head, (body[1]['x'], body[1]['y']))
	moves = get_restrictions(head, walls, None, pm)
	print 'moves: ', moves
	
	move = solve_4x4_moves()
	
	if(move is None):
		if(pm in moves):
			move = pm
		else:
			move = random.choice(moves)
	
	return {
		'move': move,
		'taunt': 'It\'s Jake the Snake!'
	}


def get_previous_move(head, second):
	if(head[0] == second[0]):
		if(head[0] > second[0]):
			return 'right'
		else:
			return 'left'
	else:
		if(head[1] > second[1]):
			return 'up'
		else:
			return 'down'


def get_restrictions(head, walls, snakes, pm):

	directions = {'up':1, 'down':1, 'left':1, 'right':1}
	
	print "previousMove: " + pm
	
	# Don't hit a wall
	if(head[0] == walls[0]):
		directions['right'] = 0
	elif(head[0] == 0):
		directions['left'] = 0
	if(head[1] == 0):
		directions['up'] = 0
	elif(head[1] == walls[1]):
		directions['down'] = 0
	
	# Don't go back on yourself
	if(pm == 'right'):
		directions['left'] = 0
	elif(pm == 'left'):
		directions['right'] = 0
	elif(pm == 'up'):
		directions['down'] = 0
	elif(pm == 'down'):
		directions['up'] = 0
	
	# Don't hit other snakes
	
	
	# Be scared of the heads of others
	
	
	moves = [k for k in directions.keys() if directions[k] is 1]
	
	return moves
	
	
def solve_6x6_moves():
	pass


def solve_4x4_moves():
	pass


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug = True)
