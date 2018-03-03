import bottle
import os
import random
import time

'''
TODO:
Take preference away from the walls
Change the collision work
Got Time? Implement future move validation, make sure the second move has at least one option
'''

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
		'color': '#99FFFF',
		'taunt': 'Wake up Blake, you\'re a snake',
		'head_url': headUrl
	}
	

@bottle.post('/move')
def move():
	
	t1 = time.clock()
	
	data = bottle.request.json
	
	you = data.get('you')
	health = you["health"]
	body = you['body']['data']
	head = (body[0]['x'], body[0]['y'])
	walls = (data.get('width'), data.get('height'))
	snakes = data['snakes']['data']
	snakes = [s['body']['data'] for s in snakes]
	snakes2 = []
	heads = []
	size = []
	for s1 in snakes:
		heads.append((s1[0]['x'], s1[0]['x']))
		size.append(s1['length'])
		for s2 in s1:
			snakes2.append((s2['x'], s2['y']))
	snakes = snakes2
	food = data.get('food')['data']
	food = [(f['x'], f['y']) for f in food]
	
	print "Head: ", head, "Second: ", (body[1]['x'], body[1]['y'])
	print "Size: ", size
	
	pm = get_previous_move(head, (body[1]['x'], body[1]['y']))
	moves = get_restrictions(head, walls, snakes, heads, size, pm)
	move = get_food(moves, head, food)
	print "previousMove: " + pm
	print 'moves: ', moves
	
	# Check to see if the snake has a preferred move
	if(move == None):
		if(pm in moves or moves == []):
			move = pm
		else:
			move = random.choice(moves)
		taunt = 'Mvs: ' + str(moves)
	else:
		print 'Food Found!'
		taunt = 'FF, Mvs: ' + str(moves)
	
	# Find the next position of the head given the move
	nextHead = get_future_head(head, move)
	
	# If that move results in no more options for the next turn, chose another
	# If you get a value error here it doesn't matter anyways
	if(get_restrictions(nextHead, walls, snakes, size, size, move, op=False) == []):
		moves.remove('move')
		if(moves != []):
			move = random.choice(moves)
		taunt = 'Fnd Trp! Mvs: ' + str(moves)
		
		
	print 'move: ', move
	print 'time: ', time.clock()-t1
	print '------------------------------------------------------'
	
	return {
		'move': move,
		'taunt': taunt
	}

def get_future_head(head, move):
	if(move == 'left'):
		return (head[0] - 1, head[1])
	elif(move == 'right'):
		return (head[0] + 1, head[1])
	elif(move == 'up'):
		return (head[0], head[1] - 1)
	else:
		return (head[0], head[1] + 1)


def get_previous_move(head, second):
	if(head[0] == second[0]):
		if(head[1] > second[1]):
			return 'down'
		else:
			return 'up'
	else:
		if(head[0] > second[0]):
			return 'right'
		else:
			return 'left'


def get_food(moves, head, food):
	val = None
	for f in food:
		xdist = f[0]-head[0]
		ydist = f[1]-head[1]
		if((abs(xdist) == 1 and ydist == 0) ^ (abs(ydist) == 1 and xdist == 0)):
			if(xdist == 1 and 'right' in moves):
				return 'right'
			elif(xdist == -1 and 'left' in moves):
				return'left'
			elif(ydist == 1 and 'down' in moves):
				return 'down'
			elif(ydist == -1 and 'up' in moves):
				return 'up'
	return None
				

def get_restrictions(head, walls, snakes, heads, size, pm, op=True):

	directions = {'up':1, 'down':1, 'left':1, 'right':1}
	
	# Don't hit a wall
	if(head[0] == walls[0]-1):
		directions['right'] = 0
	elif(head[0] == 0):
		directions['left'] = 0
	if(head[1] == 0):
		directions['up'] = 0
	elif(head[1] == walls[1]-1):
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
	for s in snakes:
		xdist = abs(s[0]-head[0])
		ydist = abs(s[1]-head[1])
		if(xdist + ydist == 1):
			if(xdist == 1):
				if(s[0] > head[0]):
					directions['right'] = 0
				else:
					directions['left'] = 0
			else:
				if(s[1] > head[1]):
					directions['down'] = 0
				else:
					directions['up'] = 0
	
	directions2 = directions
	
	# OPTIONAL: Be scared of the heads of others
	for h in heads:
		xdist = h[0]-head[0]
		ydist = h[1]-head[1]
		if(abs(xdist) == 1 and abs(ydist) == 1):
			# Which move would put you further from his head?
			if(xdist > 0):
				directions['left'] = 0
			elif(xdist < 0):
				directions['right'] = 0
			if(ydist > 0):
				directions['up'] = 0
			elif(ydist < 0):
				directions['down'] = 0
		elif((abs(xdist) == 2 and ydist == 0) ^ (abs(ydist) == 2 and xdist == 0)):
			if(xdist == 2):
				directions['left'] = 0
			elif(xdist == -2):
				directions['right'] = 0
			elif(ydist == 2):
				directions['up'] = 0
			else:
				directions['down'] = 0
	
	if(1 not in directions.values() and op):
		directions = directions2
	
	moves = [k for k in directions.keys() if directions[k] is 1]
	
	return moves


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug = True)
