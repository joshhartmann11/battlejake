import bottle
import os
import random
import numpy as np
import astar

grid = numpy.zeros(5, 5)

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

    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    return {
        'color': '#00FF00',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url
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

    
    directions = ['up', 'down', 'left', 'right']
    direction = random.choice(directions)
    return {
        'move': 'up',
    }
    
	
def get_move():
	pass
	
	
def add_walls(walls, head):
	print walls
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
