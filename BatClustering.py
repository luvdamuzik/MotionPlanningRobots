import numpy as np
import random


class BatAlgorithmClustering:
    def __init__(self, coordinates, n_clusters, n_bats=20, n_iterations=100, f_min=0, f_max=2):
        self.coordinates = np.array(coordinates)
        self.n_clusters = n_clusters
        self.n_bats = n_bats
        self.n_iterations = n_iterations
        self.f_min = f_min
        self.f_max = f_max
        self.bats = self.initialize_bats()
        self.best_bat = min(self.bats, key=self.evaluate_fitness)

    def euclidean_distance(self, point1, point2):
        return np.sqrt(np.sum((point1 - point2) ** 2))

    def evaluate_fitness(self, bat):
        clusters = self.assign_clusters(bat['position'])
        return sum(self.euclidean_distance(coord, bat['position'][i])
                   for i, cluster in enumerate(clusters) for coord in cluster)

    def assign_clusters(self, centroids):
        clusters = [[] for _ in range(centroids.shape[0])]
        for coord in self.coordinates:
            closest_centroid_idx = np.argmin([self.euclidean_distance(coord, centroid) for centroid in centroids])
            clusters[closest_centroid_idx].append(coord)
        return clusters

    def initialize_bats(self):
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

    def update_bats(self):
        for bat in self.bats:
            bat['frequency'] = self.f_min + (self.f_max - self.f_min) * random.random()
            bat['velocity'] += (bat['position'] - self.best_bat['position']) * bat['frequency']
            candidate_position = bat['position'] + bat['velocity']

            if random.random() > bat['pulse_rate']:
                candidate_position += 0.01 * np.random.randn(*bat['position'].shape)

            candidate_position = np.clip(candidate_position, self.coordinates.min(axis=0), self.coordinates.max(axis=0))

            candidate_fitness = self.evaluate_fitness({"position": candidate_position})
            if candidate_fitness < self.evaluate_fitness(bat) and random.random() < bat['loudness']:
                bat['position'] = candidate_position
                bat['loudness'] *= 0.9
                bat['pulse_rate'] = bat['pulse_rate'] * (1 - np.exp(-0.1))

    def run(self):
        for _ in range(self.n_iterations):
            self.update_bats()
            current_best_bat = min(self.bats, key=self.evaluate_fitness)
            if self.evaluate_fitness(current_best_bat) < self.evaluate_fitness(self.best_bat):
                self.best_bat = current_best_bat

        # Get the final clusters based on the best bat's centroids
        final_clusters = self.assign_clusters(self.best_bat['position'])
        return self.best_bat['position'], final_clusters
