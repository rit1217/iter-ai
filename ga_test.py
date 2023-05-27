import random

class Node:
    def __init__(self, index, x, y, time_window=None):
        self.index = index
        self.x = x
        self.y = y
        self.time_window = time_window

class GeneticAlgorithmVRPTW:
    def __init__(self, distance_matrix, nodes, population_size, mutation_rate, max_iterations):
        self.distance_matrix = distance_matrix
        self.nodes = nodes
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.max_iterations = max_iterations

    def initialize_population(self):
        population = []
        for _ in range(self.population_size):
            # Generate a random permutation of nodes excluding the depot
            chromosome = random.sample(self.nodes[1:], len(self.nodes)-1)
            population.append(chromosome)
        return population

    def calculate_fitness(self, chromosome):
        fitness = 0
        current_time = 0
        for i in range(len(chromosome)):
            current_node = chromosome[i]
            next_node = chromosome[(i+1) % len(chromosome)]  # Consider circular routes
            distance = self.distance_matrix[current_node.index][next_node.index]
            travel_time = distance  # Assuming unit travel time per unit distance
            waiting_time = max(0, current_node.time_window[0] - current_time)
            current_time = max(current_node.time_window[0], current_time) + travel_time + waiting_time
            if current_time > current_node.time_window[1]:
                fitness += current_time - current_node.time_window[1]  # Penalize violations
        return fitness

    def crossover(self, parent1, parent2):
        # Perform ordered crossover (OX) operator
        start_index = random.randint(0, len(parent1) - 1)
        end_index = random.randint(start_index + 1, len(parent1))
        offspring = [None] * len(parent1)
        offspring[start_index:end_index] = parent1[start_index:end_index]
        j = end_index
        for i in range(len(parent2)):
            if parent2[i] not in offspring:
                offspring[j % len(parent2)] = parent2[i]
                j += 1
        return offspring

    def mutate(self, chromosome):
        # Perform swap mutation
        for i in range(len(chromosome)):
            if random.random() < self.mutation_rate:
                j = random.randint(0, len(chromosome) - 1)
                chromosome[i], chromosome[j] = chromosome[j], chromosome[i]
        return chromosome

    def select_parents(self, population):
        # Tournament selection with tournament size of 2
        parents = []
        for _ in range(len(population)):
            tournament = random.sample(population, 2)
            fitnesses = [self.calculate_fitness(chromosome) for chromosome in tournament]
            selected_parent = tournament[fitnesses.index(min(fitnesses))]
            parents.append(selected_parent)
        return parents

    def run(self):
        population = self.initialize_population()
        best_fitness = float('inf')
        best_solution = None

        for iteration in range(self.max_iterations):
            parents = self.select_parents(population)
            offspring = []

            while len(offspring) < self.population_size:
                parent1, parent2 = random.sample(parents, 2)
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                offspring.append(child)

            population = offspring

            # Evaluate fitness of new population
            for chromosome in population:
                fitness = self.calculate_fitness(chromosome)
                if fitness < best_fitness:
                    best_fitness = fitness
                    best_solution = chromosome

        return best_solution

# Example usage
distance_matrix = [
    [0, 10, 20, 30],
    [10, 0, 15, 25],
    [20, 15, 0, 10],
    [30, 25, 10, 0]
]

nodes = [
    Node(0, 0, 0),  # Depot
    Node(1, 5, 15, time_window=(0, 20)),
    Node(2, 10, 20, time_window=(5, 30)),
    Node(3, 10, 25, time_window=(10, 40)),
    Node(0, 0, 0, time_window=(0, 100)),  # Depot
    Node(0, 0, 0,time_window=(0, 100)) # Depot
]

ga_vrptw = GeneticAlgorithmVRPTW(distance_matrix, nodes, population_size=10, mutation_rate=0.1, max_iterations=100)
best_solution = ga_vrptw.run()

# print('\n---',best_solution, nodes)

route_nodes = [nodes.index(node_index) for node_index in best_solution]
print("Route:", route_nodes)
# print("Best solution:", best_solution)
