
import random
import typing
import sys
import copy


# called when you create your Battlesnake on play.battlesnake.com
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "Jrochelle",
        "color": "#5D1725",  
        "head": "default",  
        "tail": "default",  
    }


# called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")
    boardHeight = game_state['board']['height']
    boardWidth = game_state['board']['width']
    timeout = game_state['game']['timeout']
    print('Starting game with %dx%d board and %dms timeout' % (boardHeight, boardWidth, timeout))


# called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


def evaluation_function(game_state):
    your_snake = game_state['you']
    food = game_state['board']['food']
    head = your_snake['head']

    closest_food_distance = min(abs(head['x'] - f['x']) + abs(head['y'] - f['y']) for f in food) if food else float('inf')

    score = your_snake['health'] - closest_food_distance
    return score

# simulates what the next state will be after a given move
def get_next_state(game_state, move, is_maximizing_player):
    next_game_state = copy.deepcopy(game_state)
    your_snake_index = 0 if game_state['board']['snakes'][0]['id'] == game_state['you']['id'] else 1
    opponent_snake_index = 1 - your_snake_index

    snake = next_game_state['board']['snakes'][your_snake_index] if is_maximizing_player \
            else next_game_state['board']['snakes'][opponent_snake_index]
    new_head = copy.deepcopy(game_state['you']['body'][0])
    if move == "up":
        new_head["y"] += 1
    elif move == "down":
        new_head["y"] -= 1
    elif move == "left":
        new_head["x"] -= 1
    elif move == "right":
        new_head["x"] += 1
    
    snake['health'] -= 1
    snake['head'] = new_head
    snake['body'].insert(0, new_head)
    snake['body'].pop()

    if is_maximizing_player:
        next_game_state['you']['health'] -= 1
        next_game_state['you']['head'] = new_head
        next_game_state['you']['body'].insert(0, new_head)
        next_game_state['you']['body'].pop()

    for food in next_game_state['board']['food']:
        if food == new_head:
            next_game_state['board']['food'].remove(food)
            snake['health'] = 100
            snake['body'].append(snake['body'][-1])
            snake['length'] += 1
            if is_maximizing_player:
                next_game_state['you']['health'] = 100
                next_game_state['you']['body'].append(snake['body'][-1])
                next_game_state['you']['length'] += 1
            break

    return next_game_state



def minimax(game_state, depth, is_maximizing_player):
    if depth == 0:
        return evaluation_function(game_state)

    moves = ["up", "down", "left", "right"]
    if is_maximizing_player:
        max_eval = float('-inf')
        for move in moves:
            next_state = get_next_state(game_state, move, True)
            eval = minimax(next_state, depth - 1, False)
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for move in moves:
            next_state = get_next_state(game_state, move, False)
            eval = minimax(next_state, depth - 1, True)
            min_eval = min(min_eval, eval)
        return min_eval  


# move is called on every turn and returns your next move
def move(game_state: typing.Dict) -> typing.Dict:

    is_move_safe = {"up": True, "down": True, "left": True, "right": True}

    my_head = game_state["you"]["body"][0]  # Coordinates of your head
    my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"

    if my_neck["x"] < my_head["x"]:  
        is_move_safe["left"] = False

    elif my_neck["x"] > my_head["x"]:  
        is_move_safe["right"] = False

    elif my_neck["y"] < my_head["y"]:  
        is_move_safe["down"] = False

    elif my_neck["y"] > my_head["y"]:  
        is_move_safe["up"] = False

    # Prevents your Battlesnake from moving out of bounds
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]

    if my_head["x"] == 0:
        is_move_safe["left"] = False
    if my_head["x"] == board_width - 1:
        is_move_safe["right"] = False
    if my_head["y"] == 0:
        is_move_safe["down"] = False
    if my_head["y"] == board_height - 1:
        is_move_safe["up"] = False

    # Prevents your Battlesnake from colliding with itself
    my_body = game_state["you"]["body"]
    
    for segment in my_body[1:]:
        if segment["x"] == my_head["x"] - 1 and segment["y"] == my_head["y"]:
            is_move_safe["left"] = False
        if segment["x"] == my_head["x"] + 1 and segment["y"] == my_head["y"]:
            is_move_safe["right"] = False
        if segment["y"] == my_head["y"] - 1 and segment["x"] == my_head["x"]:
            is_move_safe["down"] = False
        if segment["y"] == my_head["y"] + 1 and segment["x"] == my_head["x"]:
            is_move_safe["up"] = False

    # Prevents your Battlesnake from colliding with other Battlesnakes
    opponents = game_state["board"]["snakes"]

    for snake in opponents:
        for segment in snake["body"]:
            if segment["x"] == my_head["x"] - 1 and segment["y"] == my_head["y"]:
                is_move_safe["left"] = False
            if segment["x"] == my_head["x"] + 1 and segment["y"] == my_head["y"]:
                is_move_safe["right"] = False
            if segment["y"] == my_head["y"] - 1 and segment["x"] == my_head["x"]:
                is_move_safe["down"] = False
            if segment["y"] == my_head["y"] + 1 and segment["x"] == my_head["x"]:
                is_move_safe["up"] = False


    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)

    if len(safe_moves) == 0:
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}


    best_move = None
    best_score = float('-inf')

    for move in is_move_safe:
        if is_move_safe[move]:
            next_state = get_next_state(game_state, move, True)
            score = minimax(next_state, depth=3, is_maximizing_player=False)
            if score > best_score:
                best_score = score
                best_move = move
    
    next_move = best_move if best_move else random.choice(safe_moves)


    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}


if __name__ == "__main__":
    from server import run_server
    port = "8000"
    for i in range(len(sys.argv) - 1):
        if sys.argv[i] == '--port':
            port = sys.argv[i+1]

    run_server({"info": info, "start": start, "move": move, "end": end, "port": port})
