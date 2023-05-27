import random
from .vrptw_base import VrptwGraph, Node
from datetime import timedelta
from components.constants import *
from components.utils import *
import numpy as np


class Node:
    def __init__(self, index, time_window_start, time_window_end):
        self.index = index
        self.time_window_start = time_window_start
        self.time_window_end = time_window_end

class GeneticAlgorithmVRPTW:
    def __init__(self, graph: VrptwGraph, start_time, num_day, population_size=10, mutation_rate=0.05, max_iterations=1000):
        self.graph = graph
        for node in self.graph.nodes:
            if node.is_depot:
                self.depot = node
                for i in range(num_day):
                    self.graph.nodes.append(node)
                break
        self.num_day = num_day
        print([node.id for node in self.graph.nodes])
        self.meal_time = {}
        for k, v in MEAL_TIME.items():
            meal_start = max(0, to_minute(str_to_time(v[0])) - to_minute(start_time))
            meal_end = min(to_minute(str_to_time(v[1])) - to_minute(start_time), self.graph.end_time - 150)
    
            if meal_start <= meal_end:
                self.meal_time[k] = [meal_start, meal_end]

        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.max_iterations = max_iterations

    def initialize_population(self):
        population = []
        # print('\n\n--------NODES', self.graph.nodes)
        for _ in range(self.population_size):
            # Generate a random permutation of nodes excluding the depot
            chromosome = random.sample(self.graph.nodes[1:], len(self.graph.nodes)-1)
            chromosome.insert(0, self.depot)
            # print('chromosome', [node.id for node in chromosome])
            population.append(chromosome)
        return population

    def calculate_fitness(self, chromosome):
        # print('\nCHROMOSOME', chromosome)
        fitness = 0
        current_time = 0
        day = self.graph.start_date - timedelta(days=1)
        weekday = DAY_OF_WEEK[day.weekday()]
        # temp = chromosome[:]
        # temp.reverse()
        # last_depot_ind = temp.index(self.depot)
        # chromosome = chromosome[:len(temp) - last_depot_ind]
        # print('\nCHROMOSOME AFTER', chromosome)
        for i in range(len(chromosome)):
            current_node = chromosome[i]
            if current_node.is_depot:
                current_time = 0
                day += timedelta(days=1)
                weekday = DAY_OF_WEEK[day.weekday()]
            next_node = chromosome[(i+1) % len(chromosome)]  # Consider circular routes
            distance = self.graph.node_dist_mat[current_node.id][next_node.id]
            travel_time = distance  # Assuming unit travel time per unit distance
            waiting_time = max(0, current_node.ready_time[weekday] - current_time)
            current_time = max(current_node.ready_time[weekday], current_time) + travel_time + waiting_time + current_node.service_time
            # current_time += travel_time + waiting_time
            if current_time > current_node.due_time[weekday]:
                fitness += current_time - current_node.due_time[weekday]  # Penalize violations
            elif current_time > self.graph.end_time:
                fitness += current_time - self.graph.end_time
            elif current_node.place.category == "RESTAURANT":
                for meal in self.meal_time.keys():
                    if self.meal_time[meal][0] > current_time:
                        fitness += self.meal_time[meal][0] - current_time
                        break
                
        return fitness
    
    def crossover(self, parent1, parent2):
        # Select a random crossover point
        crossover_point = random.randint(1, len(parent1) - 1)

        # Create two offspring by combining the parents' genes
        offspring1 = parent1[:crossover_point] + parent2[crossover_point:]
        offspring2 = parent2[:crossover_point] + parent1[crossover_point:]
        # print('crossovered', [node.id for node in offspring1],[node.id for node in offspring2] )
        return random.choice([offspring1, offspring2])

    # def crossover(self, parent1, parent2):
    #     offspring = [None] * len(parent1)

    #     # Choose a random sub-route from parent1
    #     start_index = random.randint(0, len(parent1) - 1)
    #     end_index = random.randint(start_index + 1, len(parent1))
    #     sub_route = parent1[start_index:end_index]

    #     # Insert the sub-route into offspring
    #     offspring[start_index:end_index] = sub_route
    #     print(len(parent2), len(sub_route))

    #     # Fill in the remaining nodes from parent2
    #     parent2_index = 0

    #     for i in range(len(offspring)):
    #         if offspring[i] is None:
    #             while parent2[parent2_index % len(parent2)] in sub_route:
    #                 parent2_index += 1
    #             offspring[i] = parent2[parent2_index % len(parent2)]
    #             parent2_index += 1

    #     print('\n\n-----AFTER CROSSOVER', offspring)

    #     return offspring

    def mutate(self, chromosome):
        # Perform swap mutation
        for i in range(1, len(chromosome)):
            # print([node.id for node in chromosome])

            if random.random() < self.mutation_rate:
                j = random.randint(1, len(chromosome) - 1)
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
                # print('crossovered', [node.id for node in child])

                child = self.mutate(child)
                # print('mutated', [node.id for node in child])

                offspring.append(child)

            population = offspring

            # Evaluate fitness of new population
            for chromosome in population:
                fitness = self.calculate_fitness(chromosome)
                if fitness < best_fitness and [node.id for node in chromosome].count(0) == self.num_day + 1:
                    print([node.id for node in chromosome], [node.id for node in chromosome].count(0))

                    best_fitness = fitness
                    best_solution = chromosome

        temp = [node.id for node in best_solution]
        # print('BEFORE', temp)
        # temp.reverse()
        # print('REVERSED', temp)

        # last_depot_ind = temp.index(0)
        # best_solution = best_solution[:len(temp) - last_depot_ind]
        # best_path = [node.id for node in best_solution]
        best_path = self.limit_result(temp, self.num_day)
        print(best_path, self.cal_score(best_path))
        # print('\nCHROMOSOME AFTER', chromosome)
        return best_path
    

    def place_visit_objective(self, travel_path):
        # ant.travel_path is list of index of nodes in a graph that visited by the ant
        path = [ind for ind in travel_path if ind != 0] #travel path excluding hotel

        # ant.travel_time is list of travel_time + wait_time between places
        # e.g. [0, 39, 18, 0, 17, 6]
        # noted that 0 in ant.travel_time is the start of each day in the trip

        # avg_travel_time = sum(ant.travel_time) / (len(ant.travel_time) - ant.travel_time.count(0))

        num_place = len(set(path))
        num_type = {}
        cuisine_type = {}
        num_shop = 0
        score = 0
        for ind in path:
            place = self.graph.nodes[ind].place
            if place.category == 'RESTAURANT':
                for type in place.types:
                    if type not in cuisine_type.keys():
                        cuisine_type[type] = 0
                    score += (((num_place - cuisine_type[type])/num_place)) \
                        / len(place.types) # place.types in this case is cuisine_types for restaurant
                    cuisine_type[type] += 1

            elif place.category == 'ATTRACTION':
                # place.types is variable stored types of place, i.e.,attraction_types,
                #  cuisine_types, etc.
                for type in place.types:
                    if type not in num_type.keys():
                        num_type[type] = 0
                    score += ( ((num_place - num_type[type])/num_place))/len(place.types)
                    num_type[type] += 1

            elif place.category == 'SHOP':
                score += ((num_place - num_shop)/num_place)
                num_shop += 1
        
        return -(score*num_place)

    def cal_score(self, travel_path):
        place_visit_score = self.place_visit_objective(travel_path)
        distance_score = self.cal_travel_dist(travel_path)
        score = {'VISIT': place_visit_score, 'DISTANCE': distance_score, 
                'TOTAL' :(place_visit_score )+ distance_score}
        
        return score

    def limit_result(self, travel_path, num_day):
        cur_ind = travel_path[0]
        new_path = [cur_ind]
        cur_time = 0
        day = self.graph.start_date
        flag = False
        for next_ind in travel_path[1:]:
            print('\n', next_ind, new_path)
            if next_ind == 0:
                num_day -= 1
                day += timedelta(days=1)
                if num_day == 0:
                    new_path.append(0)
                    break
            if flag:
                if cur_ind == 0:
                    flag = False
                    cur_time = 0
                    new_path.append(0)
                else:
                    cur_ind = next_ind
                    continue


            dist = self.cal_temp_dist_mat(cur_time, day)[cur_ind][next_ind]
            cur_time += dist + self.graph.nodes[next_ind].service_time
            # print(cur_time)
            print(cur_ind, next_ind, num_day, cur_time, self.graph.nodes[next_ind].due_time[DAY_OF_WEEK[day.weekday()]],self.graph.end_time )

            if cur_time > self.graph.nodes[next_ind].due_time[DAY_OF_WEEK[day.weekday()]] or cur_time > self.graph.end_time:
                cur_time -= dist + self.graph.nodes[next_ind].service_time
                flag = True
            else:
                new_path.append(next_ind)
            cur_ind = next_ind
    
        return new_path

    def cal_travel_dist(self, travel_path):
        cur_ind = travel_path[0]
        travel_time = 0
        cur_time = 0
        day = self.graph.start_date
        for next_ind in travel_path[1:]:
            dist = self.cal_temp_dist_mat(cur_time, day)[cur_ind][next_ind]
            travel_time += dist
            cur_time += dist + self.graph.nodes[next_ind].service_time
            cur_ind = next_ind
            if cur_ind == 0:
                cur_time = 0
                day += timedelta(days=1)
        return travel_time


    def cal_temp_dist_mat(self, vehicle_travel_time, day):
        distance_mat = np.copy(self.graph.node_dist_mat)
        for index in range(1, self.graph.node_num):
            ready_time = self.graph.nodes[index].ready_time[DAY_OF_WEEK[day.weekday()]]
            if ready_time > vehicle_travel_time:
                wait_time = ready_time - vehicle_travel_time
                for i in range(self.graph.node_num):
                    if i != index:
                        distance_mat[i][index] += wait_time

        return distance_mat