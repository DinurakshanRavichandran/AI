import random
import heapq
import math
import statistics

# Maze generator for a 6x6 grid with barriers
ROWS, COLS = 6, 6
TOTAL_NODES = ROWS * COLS

# Helper functions
def get_coordinates(node_id):
    return (node_id % COLS, node_id // COLS)

def get_node_id(x, y):
    return y * COLS + x

def generate_maze():
    all_nodes = list(range(TOTAL_NODES))
    start_candidates = range(0, 12)
    goal_candidates = range(24, 36)
    start = random.choice(start_candidates)
    goal = random.choice(goal_candidates)

    remaining_nodes = [node for node in all_nodes if node != start and node != goal]
    barriers = random.sample(remaining_nodes, 4)

    return {'start': start, 'goal': goal, 'barriers': barriers}

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

# Search helpers
def get_neighbors(node, barriers):
    x, y = get_coordinates(node)
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),         (0, 1),
                  (1, -1), (1, 0), (1, 1)]
    
    neighbors = []
    for dx, dy in directions:
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < COLS and 0 <= new_y < ROWS:
            neighbor_id = get_node_id(new_x, new_y)
            if neighbor_id not in barriers:
                neighbors.append(neighbor_id)
    return sorted(neighbors)

def edge_cost(node1, node2):
    x1, y1 = get_coordinates(node1)
    x2, y2 = get_coordinates(node2)
    return math.hypot(x2 - x1, y2 - y1)

def chebyshev_distance(node1, node2):
    x1, y1 = get_coordinates(node1)
    x2, y2 = get_coordinates(node2)
    return max(abs(x2 - x1), abs(y2 - y1))

# Uniform Cost Search (UCS)
def uniform_cost_search(start, goal, barriers):
    visited = set()
    came_from = {}
    cost_so_far = {start: 0}
    queue = [(0, start)]
    visited_order = []

    while queue:
        current_cost, current_node = heapq.heappop(queue)

        if current_node in visited:
            continue

        visited.add(current_node)
        visited_order.append(current_node)

        if current_node == goal:
            break

        for neighbor in get_neighbors(current_node, barriers):
            new_cost = cost_so_far[current_node] + edge_cost(current_node, neighbor)
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                heapq.heappush(queue, (new_cost, neighbor))
                came_from[neighbor] = current_node

    # Reconstruct path
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from.get(current)
        if current is None:
            return visited_order, len(visited_order) / 60, []  # No path found
    path.append(start)
    path.reverse()

    return visited_order, len(visited_order) / 60, path

# A* Search
def a_star_search(start, goal, barriers):
    visited = set()
    came_from = {}
    cost_so_far = {start: 0}
    queue = [(chebyshev_distance(start, goal), start)]
    visited_order = []

    while queue:
        current_priority, current_node = heapq.heappop(queue)

        if current_node in visited:
            continue

        visited.add(current_node)
        visited_order.append(current_node)

        if current_node == goal:
            break

        for neighbor in get_neighbors(current_node, barriers):
            new_cost = cost_so_far[current_node] + edge_cost(current_node, neighbor)
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + chebyshev_distance(neighbor, goal)
                heapq.heappush(queue, (priority, neighbor))
                came_from[neighbor] = current_node

    # Reconstruct path
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from.get(current)
        if current is None:
            return visited_order, len(visited_order) / 60, []  # No path found
    path.append(start)
    path.reverse()

    return visited_order, len(visited_order) / 60, path

# Main Execution
if __name__ == "__main__":
    ucs_times = []
    ucs_path_lengths = []
    astar_times = []
    astar_path_lengths = []

    for i in range(4):  # 4 mazes (original + 3 randoms)
        print(f"\n\n=== Maze {i+1} ===")
        maze = generate_maze()
        start_node = maze["start"]
        goal_node = maze["goal"]
        barrier_nodes = maze["barriers"]

        print(f"Start Node: {start_node} at {get_coordinates(start_node)}")
        print(f"Goal Node: {goal_node} at {get_coordinates(goal_node)}")
        print(f"Barrier Nodes: {barrier_nodes}")
        print_maze(start_node, goal_node, barrier_nodes)

        # UCS
        visited_nodes, time_taken, final_path = uniform_cost_search(start_node, goal_node, barrier_nodes)
        ucs_times.append(time_taken)
        ucs_path_lengths.append(len(final_path))

        print("\n--- Uniform Cost Search Results ---")
        print(f"Visited Nodes: {visited_nodes}")
        print(f"Time to Find Goal: {time_taken:.2f} minutes")
        print(f"Final Path: {final_path}")

        # A* Search
        visited_nodes_a_star, time_taken_a_star, final_path_a_star = a_star_search(start_node, goal_node, barrier_nodes)
        astar_times.append(time_taken_a_star)
        astar_path_lengths.append(len(final_path_a_star))

        print("\n--- A* Search Results ---")
        print(f"Visited Nodes: {visited_nodes_a_star}")
        print(f"Time to Find Goal: {time_taken_a_star:.2f} minutes")
        print(f"Final Path: {final_path_a_star}")

    # After all mazes
    print("\n\n=== Summary Statistics ===")
    print("\n--- Uniform Cost Search (UCS) ---")
    print(f"Mean Solution Time: {statistics.mean(ucs_times):.4f} minutes")
    print(f"Variance of Solution Time: {statistics.variance(ucs_times):.6f}")
    print(f"Mean Path Length: {statistics.mean(ucs_path_lengths):.2f} nodes")
    print(f"Variance of Path Length: {statistics.variance(ucs_path_lengths):.2f}")

    print("\n--- A* Search ---")
    print(f"Mean Solution Time: {statistics.mean(astar_times):.4f} minutes")
    print(f"Variance of Solution Time: {statistics.variance(astar_times):.6f}")
    print(f"Mean Path Length: {statistics.mean(astar_path_lengths):.2f} nodes")
    print(f"Variance of Path Length: {statistics.variance(astar_path_lengths):.2f}")
