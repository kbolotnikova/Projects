import random
import typing


# info called when you create your Battlesnake on play.battlesnake.com
# controls Battlesnake's appearance
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "Torezion",
        "color": "#66c9c1",
        "head": "all-seeing",
        "tail": "mlh-gene",
    }

# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("FIGHT!")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER :(\n")


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    board = game_state["board"]
    you = game_state["you"]
    my_body = you["body"]
    my_head = my_body[0]

    # Coordinates your head would move to in each direction.
    next_positions = {
        "up": {
            "x": my_head["x"],
            "y": my_head["y"] + 1
        },
        "down": {
            "x": my_head["x"],
            "y": my_head["y"] - 1
        },
        "left": {
            "x": my_head["x"] - 1,
            "y": my_head["y"]
        },
        "right": {
            "x": my_head["x"] + 1,
            "y": my_head["y"]
        },
    }

    is_move_safe = {direction: True for direction in next_positions}

    # Prevent moving backwards.
    if len(my_body) > 1:
        my_neck = my_body[1]

        for direction, position in next_positions.items():
            if position == my_neck:
                is_move_safe[direction] = False

    # Step 1: Prevent moving outside the board.
    for direction, position in next_positions.items():
        if not (0 <= position["x"] < board["width"]
                and 0 <= position["y"] < board["height"]):
            is_move_safe[direction] = False

    # Step 2: Prevent colliding with your own body.
    # Conservatively treat every current body segment as occupied.
    for direction, position in next_positions.items():
        if position in my_body:
            is_move_safe[direction] = False

    # Step 3: Prevent colliding with other snakes.
    opponents = [
        snake for snake in board["snakes"] if snake["id"] != you["id"]
    ]

    for opponent in opponents:
        for direction, position in next_positions.items():
            if position in opponent["body"]:
                is_move_safe[direction] = False

    safe_moves = [
        direction for direction, safe in is_move_safe.items() if safe
    ]

    if not safe_moves:
        # No move avoids the walls and current bodies.
        # Still return a valid direction.
        print(f"MOVE {game_state['turn']}: No safe moves detected!")
        return {"move": "down"}

    # Bonus: Avoid squares a larger or equal-length opponent
    # could move its head into on this turn.
    preferred_moves = []

    for direction in safe_moves:
        position = next_positions[direction]
        head_collision_risk = False

        for opponent in opponents:
            opponent_head = opponent["body"][0]

            distance = (abs(position["x"] - opponent_head["x"]) +
                        abs(position["y"] - opponent_head["y"]))

            # Account for possible growth when comparing lengths.
            my_length = len(my_body) + int(position in board["food"])
            opponent_length = (len(opponent["body"]) +
                               int(position in board["food"]))

            if distance == 1 and opponent_length >= my_length:
                head_collision_risk = True
                break

        if not head_collision_risk:
            preferred_moves.append(direction)

    # If every safe move has head-to-head risk, keep those options.
    candidates = preferred_moves or safe_moves

    # Step 4: Prefer safe moves closer to food.
    food = board["food"]

    if food:
        distances = {}

        for direction in candidates:
            position = next_positions[direction]

            distances[direction] = min(
                abs(position["x"] - item["x"]) + abs(position["y"] - item["y"])
                for item in food)

        closest_distance = min(distances.values())

        best_moves = [
            direction for direction in candidates
            if distances[direction] == closest_distance
        ]

        next_move = random.choice(best_moves)
    else:
        next_move = random.choice(candidates)

    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
