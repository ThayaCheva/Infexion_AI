# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part A: Single Player Infexion

from .utils import render_board

dir = [[0, 1], [-1, 1], [-1, 0], [0, -1], [1, -1], [1, 0]]

# Function used to wrap the cell around the board
def wrap_cell(next_x: int, next_y: int) :
    if (next_y == 7) :
        next_y = 0

    if (next_y < 0) :
        next_y = 6
    
    if (next_x == 7) :
        next_x = 0

    if (next_x < 0) :
        next_x = 6

    return next_x, next_y

# Function that takes the state of the board and determines it desirability (total power)
def eval_func(board: dict[tuple,tuple], curr_cell: tuple, direction: tuple, current : dict[tuple,tuple]):
    #Determine the remaining blue power on the board
    b_power= calc_power(board)[0]
    #Evaluate the cell which we are spreading and the direction
    move_eval = eval_direction(curr_cell, direction, current)

    #if a move results in a win we do not need to determine the desirability of the direction and cell we are spreading
    if (b_power == 0) :
        return b_power
    # Check if the move will result in Red losing
    if(calc_power(board)[1] == 0 and calc_power(board)[0]>0):
        return 49
    #Determine if the move results in a decrease in red's power 
    if(calc_power(board)[1] < calc_power(current)[1]):
        if(calc_power(board)[1]==0 and calc_power(board)[0]==0):
            return b_power
        else:
            return b_power + move_eval + (calc_power(current)[1] - calc_power(board)[1])
    
    return b_power + move_eval

# Helper function for eval_direction
def search_cells(cur_power: int, x: int, y: int, next_x: int, next_y: int, 
        found_b: int, neighbor_power: int, current: dict[tuple, tuple], steps: int) :
    
    for _ in range(cur_power):
        next_x, next_y = wrap_cell(next_x, next_y)

        # Check all the neighbours of the cell
        for d in dir :
            neighbor_x = next_x + d[0]
            neighbor_y = next_y + d[1]
            neighbor_x, neighbor_y = wrap_cell(neighbor_x, neighbor_y)

            # Check if neighbour cell exists and if it's is blue
            if((neighbor_x, neighbor_y) in current):
                neighbor_color = current[(neighbor_x, neighbor_y)][0]

                if(neighbor_color =="b"):
                    found_b = 1
                    neighbor_power += current[(neighbor_x, neighbor_y)][1]

        # if a blue cell is found stop search, otherwise keep searching
        if (found_b == 1):
            break
        else:
            if (cur_power == 49) :
                steps += 1
            next_x += x
            next_y += y

    return x, y, next_x, next_y, found_b, neighbor_power, steps

# Evaluation function to find the best possible direction
def eval_direction(curr_cell: tuple, direction: tuple, current: dict[tuple,tuple]):
    x = direction[0]
    y = direction[1]

    next_x = curr_cell[0]
    next_y = curr_cell[1]

    steps, found_b, neighbor_power = 0, 0, 0

    curr_power = current[curr_cell][1]

    # Search all neighboring cells
    x, y, next_x, next_y, found_b, neighbor_power, steps = search_cells(curr_power, x, y,
        next_x, next_y, found_b, neighbor_power, current, steps)

    if (found_b != 1):
        # If a blue cell is never found, loop through the entire board
        x, y, next_x, next_y, found_b, neighbor_power, steps = search_cells(49, x, y, 
        next_x, next_y, found_b, neighbor_power, current, steps)
    #Determine if the power of the neighbors is higher than our current power 
    if(neighbor_power > curr_power):
        #Value moves that allow us to reduce enemy power but increase our own 
        return steps + 0
    
    return steps + 1

# Determine how much power each color has remaining on the board in the current game state
def calc_power(board: dict[tuple, tuple]) :
    blue_power = 0
    red_power = 0
    for cell in board:
        cell_info = board[cell] # e.g. ('r', 2)
        cell_col = cell_info[0]

        if(cell_col == 'b'):
            blue_power += cell_info[1]

        if(cell_col == 'r'):
            red_power += cell_info[1]
       
    return [blue_power, red_power] 

# Determine if blue has any power remaining 
def is_terminal_state(state: dict[tuple,tuple]):
    remainingPower = calc_power(state)[0]

    if (remainingPower == 0):
        return True

    else:
        return False

# Function that applys the specified spread move to a state of the game 
def apply_move(next_moves: tuple, board: dict[tuple,tuple]):
    temp_board = board.copy()

    # Current x and y coords 
    x = next_moves[1]
    y = next_moves[2] 

    next_x = next_moves[0][0] + x
    next_y = next_moves[0][1] + y
    
    power = temp_board[next_moves[0]][1]

    # Loop through the amount of power the node has, in order to spread
    for _ in range(power) :
        next_x, next_y = wrap_cell(next_x, next_y)

        next_pos = (next_x, next_y)

        # Check if there is a cell on the position, if not then add it otherwise add to power
        if (next_pos not in temp_board) :
            temp_board[next_pos] = ("r", 1)   

        else :
            next_power = temp_board[next_pos][1] + 1
            temp_board[next_pos] = ('r', next_power)

            if (next_power == 7) :
                del temp_board[next_pos]

        next_x += x
        next_y += y

    # After all power is used up, remove from the board    
    del temp_board[next_moves[0]]

    return temp_board


# Function that generates all possible moves that a player can make on a specific game state
def generate_next_moves(game_state: dict[tuple,tuple]):
    next_moves = []
    # Loop through all cells on the board
    for cell in game_state :
        cell_color = game_state[cell][0]
        if (cell_color == 'r') :
            # Each cell can move in 6 possible directions
            for i in range (len(dir)) :
                x_dir = dir[i][0]
                y_dir = dir[i][1]
                next_moves.append([cell, x_dir, y_dir])

    return next_moves

        
# Returns the item in the list of game states with the highest desirability 
def priority_pop(states: list):

    return states[0][1], states[0][2], states[0][3]


# Implementation of Best first search adopted from https://www.geeksforgeeks.org/best-first-search-informed-search/ (game_state = csv file)
def best_first_search(game_state: dict[tuple,tuple]):
    states = []
    moves = []
    NotInitial = False

    # Input the initial state of game into priority queue and assign cell and direction values to None as no move was made
    states.append([calc_power(game_state)[0], (None, None), (None, None), game_state])

    while states:
        moveCell, moveDir, game_state = priority_pop(states)

        if (NotInitial) :
            moves.append((moveCell[0], moveCell[1], moveDir[0], moveDir[1]))
        # Once the information has been accesssed about the state remove it
        states = []
        
        if (is_terminal_state(game_state) == True):
             return moves

        # Generate the next possible moves that the player can make from the current state
        possible_moves = generate_next_moves(game_state)

        # For each possible move that can be made apply the move and determine its desirability
        for next_moves in possible_moves :
            temp_state = apply_move(next_moves, game_state)
            evaluation = eval_func(temp_state, next_moves[0], (next_moves[1], next_moves[2]), game_state)

            states.append([evaluation, next_moves[0], (next_moves[1], next_moves[2]), temp_state])
            states.sort()
        NotInitial=True



def search(input: dict[tuple, tuple]) -> list[tuple]:
    """
    This is the entry point for your submission. The input is a dictionary
    of board cell states, where the keys are tuples of (r, q) coordinates, and
    the values are tuples of (p, k) cell states. The output should be a list of 
    actions, where each action is a tuple of (r, q, dr, dq) coordinates.

    See the specification document for more details.
    """
    moves = best_first_search(input)

    # The render_board function is useful for debugging -- it will print out a 
    # board state in a human-readable format. Try changing the ansi argument 
    # to True to see a colour-coded version (if your terminal supports it).
    print(render_board(input, ansi=True))

    
    return moves
