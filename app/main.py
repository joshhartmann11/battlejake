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
	
	print '*******************************************************************\n\
			*******************************************************************'
	
	return {
		'color': '#99FFFF',
		'taunt': 'Wake up Blake, you\'re a snake',
		'head_url': headUrl
	}
	

@bottle.post('/move')
def move():
	taunt = 'Jake the Snake!'
	t1 = time.clock()
	
	data = bottle.request.json
	
	you = data.get('you')
	health = you["health"]
	mySize = you['length']
	body = you['body']['data']
	head = (body[0]['x'], body[0]['y'])
	walls = (data.get('width'), data.get('height'))
	snakes = data['snakes']['data']
	size = []
	for s in snakes:
		size.append(s['length'])
	snakes = [s['body']['data'] for s in snakes]
	snakes2 = []
	heads = []
	for s1 in snakes:
		heads.append((s1[0]['x'], s1[0]['x']))
		for s2 in s1:
			snakes2.append((s2['x'], s2['y']))
	snakes = snakes2
	food = data.get('food')['data']
	food = [(f['x'], f['y']) for f in food]
	pm = get_previous_move(head, (body[1]['x'], body[1]['y']))
	
	print "Head: ", head, "Second: ", (body[1]['x'], body[1]['y'])
	print "Size: ", size
	
	# Moving restrictions
	moves = get_restrictions(head, mySize, walls, snakes, heads, size)
	
	print 'moves: ', moves
	
	move = None
	if(health < 25):
			move = starving(moves, head, food)
			taunt = 'ST, Mvs: ' + str(move)
	if(move == None):
		move = kill_others(head, mySize, heads, size, moves)
		
	if(move == None):
		if(health < 50):
			move = get_food(moves, head, food)
			taunt = 'GF, Mvs: ' + str(move)
		
	if(move == None):
		move = flee_wall(moves, walls, head)
		taunt = 'FW, Mvs: ' + str(move)
		
	if(move == None):
		if(pm in moves or moves == []):
			move = pm
		else:
			move = random.choice(moves)
		taunt = 'Mvs: ' + str(moves)
	
	# Find the next position of the head given the move
	nextHead = get_future_head(head, move)
	
	# If that move results in no more options for the next turn, chose another
	# If you get a value error here it doesn't matter anyways
	# 					head, 	walls, 	snakes, heads, size, pm
	if(get_restrictions(nextHead, mySize, walls, snakes, heads, size, op=False) == []):
		if(moves != []):
			moves.remove(move)
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

def flee_wall(moves, walls, head):
	if(head[0] == walls[0]-1 and 'left' in moves):
		return 'left'
	elif(head[0] == 0 and 'right' in moves):
		return 'right'
	if(head[1] == 0 and 'down' in moves):
		return 'down'
	elif(head[1] == walls[1]-1 and 'up' in moves):
		return up


def kill_others(head, mySize, heads, size, moves):

	# If you're bigger than other, kill them
	for i, h in enumerate(heads):
		if(size[i] < mySize):
			xdist = h[0]-head[0]
			ydist = h[1]-head[1]
			if(abs(xdist) == 1 and abs(ydist) == 1):
				# Which move would put you further from his head?
				if(xdist > 0 and 'right' in moves):
					return 'right'
				elif(xdist < 0 and 'left' in moves):
					return 'left'
				if(ydist > 0 and 'down' in moves):
					return 'down'
				elif(ydist < 0 and 'up' in moves):
					return 'up'
				else:
					return None
					
			elif((abs(xdist) == 2 and ydist == 0) ^ (abs(ydist) == 2 and xdist == 0)):
				if(xdist == 2 and 'right' in moves):
					return 'right'
				elif(xdist == -2 and 'left' in moves):
					return 'left'
				elif(ydist == 2 and 'down' in moves):
					return 'down'
				elif('up' in moves):
					return 'up'
				else:
					return None


def starving(moves, head, food):
	val = None
	for f in food:
		xdist = f[0]-head[0]
		ydist = f[1]-head[1]
		if((abs(xdist) == 2 and ydist == 0) ^ (abs(ydist) == 2 and xdist == 0)):
			if(xdist == 2 and 'right' in moves):
				return 'right'
			elif(xdist == -2 and 'left' in moves):
				return'left'
			elif(ydist == 2 and 'down' in moves):
				return 'down'
			elif(ydist == -2 and 'up' in moves):
				return 'up'
	return None


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
				

def get_restrictions(head, mySize, walls, snakes, heads, size, op=True):

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
	
	# Be scared of the heads of others if they're scary
	for i, h in enumerate(heads):
		if( not (size[i] < mySize)):
			xdist = h[0]-head[0]
			ydist = h[1]-head[1]
			if(abs(xdist) == 1 and abs(ydist) == 1):
				print "1,1 battle scenario"
				if(xdist > 0):
					directions['right'] = 0
					print 'Not right'
				elif(xdist < 0):
					directions['left'] = 0
					print 'Not left'
				if(ydist > 0):
					directions['down'] = 0
					print 'Not down'
				elif(ydist < 0):
					directions['up'] = 0
					print 'Not up'
					
			elif((abs(xdist) == 2 and ydist == 0) ^ (abs(ydist) == 2 and xdist == 0)):
				print "2,0 battle scenario"
				if(xdist == 2):
					directions['right'] = 0
					print 'Not right'
				elif(xdist == -2):
					directions['left'] = 0
					print 'Not left'
				elif(ydist == 2):
					directions['down'] = 0
					print 'Not down'
				else:
					directions['up'] = 0
					print 'Not up'
	
	if(1 not in directions.values() and op):
		directions = directions2
	if not op:
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
