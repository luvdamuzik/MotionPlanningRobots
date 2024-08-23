import numpy as np
import random


class BatAlgorithmClustering:
    def __init__(self, coordinates, n_clusters, n_bats=20, n_iterations=100, f_min=0, f_max=2):
        self.coordinates = coordinates
        self.n_clusters = n_clusters
        self.n_bats = n_bats
        self.n_iterations = n_iterations
        self.f_min = f_min
        self.f_max = f_max
        self.bats = self._initialize_bats()
        self.best_bat = min(self.bats, key=self._evaluate_fitness)

    def _euclidean_distance(self, point1, point2):
        return np.sqrt(np.sum((point1 - point2) ** 2))

    def _evaluate_fitness(self, bat):
        clusters = self._assign_clusters(bat['position'])
        return sum(self._euclidean_distance(coord, bat['position'][i])
                   for i, cluster in enumerate(clusters) for coord in cluster)

    def _assign_clusters(self, centroids):
        clusters = [[] for _ in range(centroids.shape[0])]
        for coord in self.coordinates:
            closest_centroid_idx = np.argmin([self._euclidean_distance(coord, centroid) for centroid in centroids])
            clusters[closest_centroid_idx].append(coord)
        return clusters

    def _initialize_bats(self):
        n_dim = self.coordinates.shape[1]
        bats = []
        for _ in range(self.n_bats):
            centroids = self.coordinates[np.random.choice(self.coordinates.shape[0], self.n_clusters, replace=False)]
            bats.append({
                "velocity": np.zeros((self.n_clusters, n_dim)),
                "position": centroids,
                "frequency": 0,
                "pulse_rate": random.random(),
                "loudness": random.random(),
            })
        return bats

    def _update_bats(self):
        for bat in self.bats:
            bat['frequency'] = self.f_min + (self.f_max - self.f_min) * random.random()
            bat['velocity'] += (bat['position'] - self.best_bat['position']) * bat['frequency']
            candidate_position = bat['position'] + bat['velocity']

            # Local search with random walk
            if random.random() > bat['pulse_rate']:
                candidate_position += 0.01 * np.random.randn(*bat['position'].shape)

            # Apply boundary constraints
            candidate_position = np.clip(candidate_position, self.coordinates.min(axis=0), self.coordinates.max(axis=0))

            # Evaluate new solution
            candidate_fitness = self._evaluate_fitness({"position": candidate_position})
            if candidate_fitness < self._evaluate_fitness(bat) and random.random() < bat['loudness']:
                bat['position'] = candidate_position
                bat['loudness'] *= 0.9  # Decrease loudness
                bat['pulse_rate'] = bat['pulse_rate'] * (1 - np.exp(-0.1))  # Increase pulse rate

    def run(self):
        for _ in range(self.n_iterations):
            self._update_bats()
            current_best_bat = min(self.bats, key=self._evaluate_fitness)
            if self._evaluate_fitness(current_best_bat) < self._evaluate_fitness(self.best_bat):
                self.best_bat = current_best_bat

        # Get the final clusters based on the best bat's centroids
        final_clusters = self._assign_clusters(self.best_bat['position'])
        return self.best_bat['position'], final_clusters


coordinates = np.array([
    [1, 2], [2, 3], [3, 4], [8, 8], [9, 9], [10, 10],
    [50, 50], [51, 51], [52, 52], [100, 100], [101, 101], [102, 102]
])
n_clusters = 3

# Create an instance of the BatAlgorithmClustering class
bat_clustering = BatAlgorithmClustering(coordinates, n_clusters)

# Run the algorithm to find the optimal centroids and the clusters
centroids, clusters = bat_clustering.run()
print("Centroids:", centroids)
for i, cluster in enumerate(clusters):
    print(f"Cluster {i + 1}: {cluster}")
