import numpy as np

# Define the problem parameters
num_robots = 3
num_endpoints = 3
grid_size = (10, 10)  # Example grid size
num_iterations = 100
num_particles = 30
inertia_weight = 0.5
c1 = 2.0
c2 = 2.0

# Initialize particles with random positions and velocities
particles_position = np.random.rand(num_particles, num_robots * 2) * grid_size[0]
particles_velocity = np.random.rand(num_particles, num_robots * 2) * 2 - 1  # Random values between -1 and 1


# Function to calculate fitness based on the total  path length
# Assuming you have a function 'calculate_path_length' that takes a robot's path as an argument and returns its length
def calculate_path_length(path):
    # Your implementation of path length calculation (e.g., A* algorithm)
    pass


def fitness(solution):
    total_path_length = 0
    for robot_index in range(num_robots):
        # Extract the assigned endpoint and path for the current robot
        endpoint = solution[robot_index][:2]
        path = solution[robot_index][2:]

        # Calculate the path length for the current robot
        path_length = calculate_path_length(path)
        total_path_length += path_length

        # Penalize solutions where a robot doesn't reach its assigned endpoint
        if not np.array_equal(path[-1], endpoint):
            total_path_length += grid_size[0] * grid_size[1]  # Add a penalty for not reaching the endpoint

    # Minimize the total path length while considering endpoint assignments
    return total_path_length


def PSO():
    # PSO optimization loop
    for iteration in range(num_iterations):
        for i in range(num_particles):
            # Evaluate fitness for each particle
            fitness_val = fitness(particles_position[i])

            # Update personal best position and fitness
            if iteration == 0 or fitness_val < fitness(particles_position[i]):
                particles_position[i] = np.clip(particles_position[i], 0, grid_size[0])
                particles_velocity[i] = np.clip(particles_velocity[i], -1, 1)

                personal_best_position = particles_position[i].copy()
                personal_best_fitness = fitness_val

        # Update global best position and fitness
        global_best_index = np.argmin([fitness(p) for p in particles_position])
        global_best_position = particles_position[global_best_index].copy()
        global_best_fitness = fitness(global_best_position)

        # Update particle velocities and positions
        for i in range(num_particles):
            r1, r2 = np.random.rand(), np.random.rand()

            # Update velocity
            particles_velocity[i] = (inertia_weight * particles_velocity[i] +
                                     c1 * r1 * (personal_best_position - particles_position[i]) +
                                     c2 * r2 * (global_best_position - particles_position[i]))

            # Update position
            particles_position[i] += particles_velocity[i]

    # Extract the best solution
    best_solution = global_best_position.reshape((num_robots, 2))

    print("Optimal Solution:")
    print(best_solution)
