import bottle
import os
import random

grid = [[0]*5]*5
previousMove = 'up'

@bottle.route('/')
def static():
    return "the server is running"


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    gameId = data.get('game_id')
    boardWidth = data.get('width')
    boardHeight = data.get('height')

    headUrl = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    return {
        'color': '#00FF00',
        'taunt': '{} ({}x{})'.format(gameId, boardWidth, boardHeight),
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
    add_walls(walls, head)
    move = get_move(health, head)
    print move
    return {
        'move': move
    }
    
	
def get_move(health, head):
	directions = ['up', 'down', 'left', 'right']
	
	if(head[1] <= 1):
		directions.remove('up')
	elif(head[1] >= walls[1]):
		directions.remove('down')
	
	if(head[0] <= 1):
		directions.remove('left')
	elif(head[0] >= walls[0]):
		directions.remove('right')
		
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
