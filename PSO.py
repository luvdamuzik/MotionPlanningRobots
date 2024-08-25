from tkinter import messagebox
import tkinter as tk


import numpy as np


def is_adjacent(p1, p2):
    return np.all(np.abs(p1 - p2) == [1, 0]) or np.all(np.abs(p1 - p2) == [0, 1])


class Particle:
    def __init__(self, start, targets, obstacles, grid_width, grid_height, num_waypoints):
        self.targets = targets
        self.start = np.array(start[0])
        self.obstacles = obstacles
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.num_waypoints = num_waypoints
        self.position = self.initialize_path()
        self.velocity = np.random.uniform(-1, 1, (num_waypoints + 1, 2))
        self.best_position = self.position.copy()
        self.best_fitness = float('inf')
        self.c1 = 2.0
        self.c2 = 2.0
        self.w = 0.5

    def initialize_path(self):
        path = [self.start]
        for _ in range(self.num_waypoints):
            last_position = path[-1]
            while True:
                move = np.random.choice(['up', 'down', 'left', 'right'])
                if move == 'up' and last_position[1] < self.grid_height - 1:
                    next_position = last_position + [0, 1]
                elif move == 'down' and last_position[1] > 0:
                    next_position = last_position + [0, -1]
                elif move == 'left' and last_position[0] > 0:
                    next_position = last_position + [-1, 0]
                elif move == 'right' and last_position[0] < self.grid_width - 1:
                    next_position = last_position + [1, 0]
                else:
                    continue
                if tuple(next_position) not in self.obstacles:
                    path.append(next_position)
                    break
        return np.array(path, dtype=np.int32)

    def fitness(self):
        path = np.vstack([np.round(self.position).astype(int)])

        # Penalty for paths that intersect obstacles
        obstacle_penalty = sum(
            [float('inf') if tuple(coord) in self.obstacles or tuple(coord) in self.targets else 0 for coord in path])

        unvisited_targets = set()
        for i in range(len(path)):
            for target in self.targets:
                for direction in ((-1, 0), (1, 0), (0, 1), (0, -1)):
                    if [target[1] + direction[1], target[0] + direction[0]] not in self.obstacles and not \
                            (path[i] == [target[1] + direction[1], target[0] + direction[0]]).all():
                        unvisited_targets.add(tuple(target))

        distance_cost = np.sum([np.linalg.norm(path - target, axis=1).min() for target in unvisited_targets])

        # Penalty for revisiting nodes
        # unnecessary_node_penalty = 0
        # visited_nodes = {}
        # for coord in path:
        #     coord_tuple = tuple(coord)
        #     if coord_tuple in visited_nodes:
        #         visited_nodes[coord_tuple] += 1
        #
        #         # Check if this revisit is necessary (adjacent to any target)
        #         necessary_backtrack = any(is_adjacent(coord, target) for target in self.targets)
        #
        #         # Apply penalty if revisiting a node unnecessarily
        #         if not necessary_backtrack:
        #             unnecessary_node_penalty += 10000  # Penalize unnecessary revisits
        #     else:
        #         visited_nodes[coord_tuple] = 1

        # Penalty for revisiting waypoints or circular paths
        # visited_segments = set()
        # circular_penalty = 0
        # for i in range(len(path) - 1):
        #     segment = tuple(sorted([tuple(path[i]), tuple(path[i + 1])]))
        #     if segment in visited_segments:
        #         circular_penalty += 3000  # Large penalty for revisiting segments
        #     visited_segments.add(segment)

        # Penalty for not visiting all targets
        # target_penalty = 0
        # visited_targets = set()
        # for i in range(len(path)):
        #     for target in self.targets:
        #         if np.array_equal(path[i], target):
        #             visited_targets.add(tuple(target))
        # if len(visited_targets) < len(self.targets):
        #     target_penalty += 1e6  # Large penalty for missing targets\

        # unvisited_target_penalty = 0
        # for i in range(len(path)):
        #     # Unvisited target penalty (sum of Manhattan distances to unvisited targets)
        #     last_node = path[-1]
        #     unvisited_targets = [target for target in self.targets if tuple(target) not in visited_targets]
        #     for target in unvisited_targets:
        #         manhattan_distance = np.abs(last_node[0] - target[0]) + np.abs(last_node[1] - target[1])
        #         unvisited_target_penalty += manhattan_distance * 1000  # Add a significant penalty based on distance

        # early_target_reward = 0
        # for i in range(len(path)):
        #     if tuple(path[i]) in [tuple(target) for target in self.targets]:
        #         early_target_reward += 2000 / (self.num_waypoints - i + 1)
        #     else:
        #         early_target_reward += 2000

        # Penalty for path length
        # path_length = len(path) - 1  # Total path length in steps
        # path_length_penalty = path_length * 10  # Adjust the penalty scale as needed

        # Penalty for path smoothness (large changes in direction)
        # smoothness_penalty = 0
        # for i in range(2, len(path)):
        #     prev_direction = path[i - 1] - path[i - 2]
        #     current_direction = path[i] - path[i - 1]
        #     angle_diff = np.arccos(np.clip(np.dot(prev_direction, current_direction) /
        #                                    (np.linalg.norm(prev_direction) * np.linalg.norm(current_direction)), -1.0,
        #                                    1.0))
        #     smoothness_penalty += angle_diff * 1000  # Larger penalty for sharp turns

        # Deviation penalty (minimize distance from targets)
        # deviation_penalty = np.sum([np.linalg.norm(path - target, axis=1).min() for target in self.targets]) * 500

        # Penalty for direction deviation
        # direction_penalty = 0
        # for i in range(1, len(path)):
        #     prev_node = path[i - 1]
        #     curr_node = path[i]
        #     movement_vector = curr_node - prev_node
        #
        #     # Calculate direction to each target
        #     target_directions = [target - curr_node for target in self.targets]
        #     movement_angle_cost = float('inf')
        #
        #     for direction in target_directions:
        #         direction_norm = np.linalg.norm(direction)
        #         if direction_norm == 0:
        #             continue
        #         movement_norm = np.linalg.norm(movement_vector)
        #         if movement_norm == 0:
        #             continue
        #
        #         # Normalize the vectors
        #         direction = direction / direction_norm
        #         movement_vector = movement_vector / movement_norm
        #
        #         # Compute the angle between the movement direction and the target direction
        #         angle = np.arccos(np.clip(np.dot(direction, movement_vector), -1.0, 1.0))
        #         angle_cost = np.sin(angle) * 1000  # Penalty proportional to the angle deviation
        #
        #         movement_angle_cost = min(movement_angle_cost, angle_cost)
        #
        #     direction_penalty += movement_angle_cost

        # Deviation from centroid penalty
        # centroid = np.mean(self.targets, axis=0)
        # centroid_penalty = 0
        # distance_from_targets_penalty = 0
        # for i in range(1, len(path)):
        #     current_node = path[i]
        #     previous_node = path[i - 1]
        #
        #     # Calculate distance from previous node to centroid
        #     dist_to_centroid_prev = np.linalg.norm(previous_node - centroid)
        #     dist_to_centroid_curr = np.linalg.norm(current_node - centroid)
        #
        #     # Penalize if moving away from centroid
        #     if dist_to_centroid_curr > dist_to_centroid_prev:
        #         centroid_penalty += (dist_to_centroid_curr - dist_to_centroid_prev) * 500
        #
        #     # Find the closest target for the previous and current nodes
        #     dist_to_nearest_target_prev = min(np.linalg.norm(previous_node - target) for target in self.targets)
        #     dist_to_nearest_target_curr = min(np.linalg.norm(current_node - target) for target in self.targets)
        #
        #     # Penalize if moving away from the closest target
        #     if dist_to_nearest_target_curr > dist_to_nearest_target_prev:
        #         distance_from_targets_penalty += (dist_to_nearest_target_curr - dist_to_nearest_target_prev) * 500

        # return obstacle_penalty + target_penalty + unnecessary_node_penalty + deviation_penalty \
        #     + unvisited_target_penalty + circular_penalty + early_target_reward + direction_penalty + centroid_penalty \
        #     + distance_from_targets_penalty
        return distance_cost + obstacle_penalty - 100 * (len(self.targets) - len(unvisited_targets))

    def update(self, global_best_position):
        r1, r2 = np.random.rand(), np.random.rand()
        self.velocity = (self.w * self.velocity +
                         self.c1 * r1 * (self.best_position - self.position) +
                         self.c2 * r2 * (global_best_position - self.position))
        self.position = np.round(self.position + self.velocity).astype(int)

        self.position[1:] = np.clip(self.position[1:], 0, [self.grid_width - 1, self.grid_height - 1])
        self.position[0] = self.start

        self.enforce_adjacency()

        fitness = self.fitness()
        if fitness < self.best_fitness:
            self.best_fitness = fitness
            self.best_position = self.position.copy()

    def enforce_adjacency(self):
        for i in range(1, len(self.position)):
            if not is_adjacent(self.position[i], self.position[i - 1]):
                current_position = self.position[i]
                previous_position = self.position[i - 1]

                possible_moves = [
                    previous_position + [0, 1],
                    previous_position + [0, -1],
                    previous_position + [1, 0],
                    previous_position + [-1, 0]
                ]

                possible_moves = [move for move in possible_moves
                                  if tuple(move) not in self.obstacles and
                                  0 <= move[0] < self.grid_width and 0 <= move[1] < self.grid_height]

                if possible_moves:
                    distances = [np.linalg.norm(np.array(move) - np.array(current_position)) for move in possible_moves]
                    min_distance_index = np.argmin(distances)
                    self.position[i] = possible_moves[min_distance_index]


def find_obstacles(grid, targets):
    obstacles = []
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == 0 and (i, j) not in targets:
                obstacles.append((j, i))
    return obstacles, len(grid), len(grid[0])


def find_path_pso(grid, start, targets, initial_max_waypoints=2, max_waypoints=5, max_iterations=100):
    try:
        obstacles, grid_height, grid_width = find_obstacles(grid, targets)
        num_waypoints = initial_max_waypoints
        found_path = False
        targets = [(y, x) for x, y in targets]

        while not found_path and num_waypoints <= max_waypoints:
            print(f"Searching with {num_waypoints} waypoints...")

            particles = []
            while len(particles) < 50 * num_waypoints:
                a = Particle(start, targets, obstacles, grid_width, grid_height, num_waypoints)
                if a not in particles:
                    particles.append(a)

            global_best_position = np.zeros_like(particles[0].position, dtype=np.int32)
            global_best_fitness = float('inf')

            # PSO main loop
            for _ in range(max_iterations):
                for particle in particles:
                    particle.update(global_best_position)

                    if particle.best_fitness < global_best_fitness:
                        global_best_fitness = particle.best_fitness
                        global_best_position = particle.best_position.copy()

            best_path = np.vstack([np.round(global_best_position).astype(int)])
            best_path_coordinates = [(int(x), int(y)) for x, y in best_path]
            print("Best path (x, y) coordinates:")
            print("Fitness:", global_best_fitness)
            for coord in best_path_coordinates:
                print(coord)
            visited_targets = set(tuple(target) for target in targets)
            helper = {}
            for target in targets:
                for direction in ((-1, 0), (1, 0), (0, 1), (0, -1)):
                    new_coord = (target[0] + direction[0], target[1] + direction[1])
                    if new_coord not in obstacles:
                        if target not in helper:
                            helper[target] = []

                        helper[target].append([target[0] + direction[0], target[1] + direction[1]])
            for coord in best_path:
                for key, value_list in helper.items():
                    if [coord[0], coord[1]] in value_list:
                        visited_targets.discard(key)
                        break
            if not visited_targets:
                found_path = True

            if not found_path:
                num_waypoints += 1

        if found_path:
            best_path = np.vstack([np.round(global_best_position).astype(int)])
            best_path_coordinates = [(int(x), int(y)) for x, y in best_path]
            print("Best path (x, y) coordinates:")
            for coord in best_path_coordinates:
                print(coord)

            surrounding_indices = []

            for target in targets:
                for direction in ((-1, 0), (1, 0), (0, 1), (0, -1)):
                    new_coord = (target[0] + direction[0], target[1] + direction[1])
                    if new_coord in best_path_coordinates and new_coord not in obstacles:
                        surrounding_indices.append(best_path_coordinates.index(new_coord))

            if surrounding_indices:
                last_target_index = max(surrounding_indices)
            else:
                last_target_index = None

            best_path = best_path[:last_target_index + 1]

            return best_path
        else:
            raise ValueError("No path found with the given waypoints limit.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", str(e))
        return None
