import random

# constants for the maze
ROWS, COLS = 6, 6
TOTAL_NODES = ROWS * COLS


# Helper function 
def get_coordinates(node_id):
    """Return (x, y) coordinates given a node ID."""
    return (node_id % COLS, node_id // COLS)

def get_node_id(x, y):
    """Return node ID given (x, y) coordinates."""
    return y * COLS + x

#Create the maze generator
def generate_maze():
    all_nodes = list(range(TOTAL_NODES))

    # choose start from 0-11
    start_candidates = range(0, 12)
    start = random.choice(start_candidates)

    #choose goal from 24-35
    goal_candidates = range(24, 36)
    goal = random.choice(goal_candidates)

    # Exclude start and goal from the list of all nodes
    remaining_nodes = [node for node in all_nodes if node != start and node != goal]

    # choose 4 uniques barriers 
    barriers = random.sample(remaining_nodes, 4)

    return{
        'start': start,
        'goal': goal,
        'barriers': barriers
    }

# Maze visualizer (optional)
def print_maze(start, goal, barriers):
    print("\nMaze Layout (6x6):\n")
    for y in range(ROWS):
        row = ""
        for x in range(COLS):
            node_id = get_node_id(x, y)
            if node_id == start:
                row += "[S] "
            elif node_id == goal:
                row += "[G] "
            elif node_id in barriers:
                row += "[X] "
            else:
                row += f"[{node_id:2}] "
        print(row)

if __name__ == "__main__":
    maze = generate_maze()

    start_node = maze["start"]
    goal_node = maze["goal"]
    barrier_nodes = maze["barriers"]

    print(f"Start Node: {start_node} at {get_coordinates(start_node)}")
    print(f"Goal Node: {goal_node} at {get_coordinates(goal_node)}")
    print(f"Barrier Nodes: {barrier_nodes}")
    
    print_maze(start_node, goal_node, barrier_nodes)