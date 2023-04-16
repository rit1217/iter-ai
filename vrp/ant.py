import numpy as np
import copy
from threading import Event

from .vrptw_base import VrptwGraph


class Ant:
    def __init__(self, graph: VrptwGraph, start_index=0):
        self.graph = graph
        self.current_index = start_index
        self.vehicle_travel_time = 0
        self.start_index = start_index
        self.travel_path = [start_index]
        self.travel_time = []
        self.wait_time = []
        self.day_meals = list(graph.meal_time.keys())

        self.index_to_visit = list(range(graph.node_num))
        self.index_to_visit.remove(start_index)

        self.available_index = self.index_to_visit[:]
        self.total_travel_distance = 0

    def clear(self):
        self.travel_path.clear()
        self.index_to_visit.clear()
    
    def cal_temp_dist_mat(self, vehicle_travel_time):
        distance_mat = np.copy(self.graph.node_dist_mat)
        for index in range(1, self.graph.node_num):
            if self.graph.nodes[index].ready_time > vehicle_travel_time:
                wait_time = self.graph.nodes[index].ready_time - vehicle_travel_time
                for i in range(self.graph.node_num):
                    if i != index:
                        distance_mat[i][index] += wait_time

        return distance_mat

    def move_to_next_index(self, next_index):
        self.graph.temp_dist_mat = self.cal_temp_dist_mat(self.vehicle_travel_time)
        self.travel_path.append(next_index)
        self.total_travel_distance += self.graph.temp_dist_mat[self.current_index][next_index]
        self.travel_time.append(self.graph.temp_dist_mat[self.current_index][next_index])
        self.wait_time.append(self.graph.temp_dist_mat[self.current_index][next_index] - \
                        self.graph.node_dist_mat[self.current_index][next_index])
        
        next_node = self.graph.nodes[next_index]

        dist = self.graph.temp_dist_mat[self.current_index][next_index]

        if next_node.is_depot:
            self.vehicle_travel_time = 0

        else:            
            self.vehicle_travel_time += dist + next_node.service_time
            self.index_to_visit.remove(next_index)
            self.available_index = self.index_to_visit[:]

        if next_node.place.category == 'RESTAURANT':
            if len(self.day_meals) > 1:
                self.day_meals.pop(0)
            else:
                self.day_meals = list(self.graph.meal_time.keys())


        self.current_index = next_index

    def index_to_visit_empty(self):
        return len(self.index_to_visit) == 0

    def get_active_vehicles_num(self):
        return self.travel_path.count(0)-1
    
    def check_empty_fleet(self):
        for i in range(len(self.travel_path[:-1])):
            if self.travel_path[i] == 0 and self.travel_path[i+1] == 0:
                return True
        
        return False

    def check_condition(self, next_index) -> bool:
        next_node = self.graph.nodes[next_index]

        dist = self.graph.node_dist_mat[self.current_index][next_index]
        wait_time = max(next_node.ready_time - self.vehicle_travel_time - dist, 0)

        service_time = next_node.service_time
        arrive_time = self.vehicle_travel_time + dist


        if  arrive_time + service_time > self.graph.nodes[0].due_time:
            return False

        if arrive_time < next_node.ready_time or \
            arrive_time + service_time > next_node.due_time:
            return False
        
        if arrive_time >= self.graph.meal_time[self.day_meals[0]][0] and \
            arrive_time <= self.graph.meal_time[self.day_meals[0]][1] and \
            next_node.place.category != 'RESTAURANT':
            return False
        
        if (arrive_time < self.graph.meal_time[self.day_meals[0]][0] or \
            arrive_time > self.graph.meal_time[self.day_meals[0]][1]) and \
            next_node.place.category == 'RESTAURANT':
            return False

        return True

    def cal_next_index_meet_constrains(self):
        next_index_meet_constrains = []
        for next_ind in self.index_to_visit:
            if self.check_condition(next_ind):
                next_index_meet_constrains.append(next_ind)
        return next_index_meet_constrains

    def cal_nearest_next_index(self, next_index_list):
        current_ind = self.current_index

        nearest_ind = next_index_list[0]
        min_dist = self.graph.node_dist_mat[current_ind][next_index_list[0]]

        for next_ind in next_index_list[1:]:
            dist = self.graph.node_dist_mat[current_ind][next_ind]
            if dist < min_dist:
                min_dist = dist
                nearest_ind = next_ind

        return nearest_ind

    def cal_path_travel_dist(self, path):
        travel_dist = 0
        temp_vehicle_travel_time = 0
        temp_wait_time = []

        for ind in range(len(path[:-1])):
            cur_ind = path[ind]
            next_ind = path[ind+1]

            temp_dist_mat = self.cal_temp_dist_mat(temp_vehicle_travel_time)
            dist = temp_dist_mat[cur_ind][next_ind]
            travel_dist += dist
            temp_wait_time.append(temp_dist_mat[cur_ind][next_ind] - \
                        self.graph.node_dist_mat[cur_ind][next_ind])

            if self.graph.nodes[next_ind].is_depot:
                temp_vehicle_travel_time = 0
            else:
                temp_vehicle_travel_time += dist + self.graph.nodes[next_ind].service_time

        temp_wait_time.append(0)

        return travel_dist, temp_wait_time

    @staticmethod
    def cal_total_travel_distance(graph: VrptwGraph, travel_path):
        distance = 0
        current_ind = travel_path[0]

        for next_ind in travel_path[1:]:
            distance += graph.node_dist_mat[current_ind][next_ind]
            current_ind = next_ind

        return distance

    def try_insert_on_path(self, node_id, stop_event: Event):
        best_insert_index = None
        best_distance = None

        for insert_index in range(len(self.travel_path)):

            if stop_event.is_set():
                return

            if self.graph.nodes[self.travel_path[insert_index]].is_depot:
                continue

            front_depot_index = insert_index
            while front_depot_index >= 0 and not self.graph.nodes[self.travel_path[front_depot_index]].is_depot:
                front_depot_index -= 1
            front_depot_index = max(front_depot_index, 0)

            check_ant = Ant(self.graph, self.travel_path[front_depot_index])

            for i in range(front_depot_index+1, insert_index):
                check_ant.move_to_next_index(self.travel_path[i])

            if check_ant.check_condition(node_id):
                check_ant.move_to_next_index(node_id)
            else:
                continue

            for next_ind in self.travel_path[insert_index:]:

                if stop_event.is_set():
                    return

                if check_ant.check_condition(next_ind):
                    check_ant.move_to_next_index(next_ind)

                    if self.graph.nodes[next_ind].is_depot:
                        temp_travel_path = self.travel_path[:]

                        temp_travel_path.insert(insert_index, node_id)
                        check_ant_distance, _ = self.cal_path_travel_dist(temp_travel_path)
                        if best_distance is None or check_ant_distance < best_distance:
                            best_distance = check_ant_distance
                            best_insert_index = insert_index
                        break

                else:
                    break

        return best_insert_index

    def insertion_procedure(self, stop_even: Event):

        if self.index_to_visit_empty():
            return

        success_to_insert = True

        while success_to_insert:

            success_to_insert = False

            ind_to_visit = np.array(copy.deepcopy(self.index_to_visit))

            for node_id in ind_to_visit:

                best_insert_index = self.try_insert_on_path(node_id, stop_even)
                if best_insert_index is not None:
                    self.travel_path.insert(best_insert_index, node_id)
                    self.total_travel_distance, self.wait_time = self.cal_path_travel_dist(self.travel_path)
                        
                    self.index_to_visit.remove(node_id)
                    self.available_index = self.index_to_visit[:]

                    success_to_insert = True

            del ind_to_visit
        # if self.index_to_visit_empty():
            # print('[insertion_procedure]: success in insertion')

    @staticmethod
    def local_search_once(graph: VrptwGraph, travel_path: list, travel_distance: float, i_start, stop_event: Event):

        depot_ind = []
        for ind in range(len(travel_path)):
            if graph.nodes[travel_path[ind]].is_depot:
                depot_ind.append(ind)

        for i in range(i_start, len(depot_ind)):
            for j in range(i + 1, len(depot_ind)):

                if stop_event.is_set():
                    return None, None, None

                for start_a in range(depot_ind[i - 1] + 1, depot_ind[i]):
                    for end_a in range(start_a, min(depot_ind[i], start_a + 6)):
                        for start_b in range(depot_ind[j - 1] + 1, depot_ind[j]):
                            for end_b in range(start_b, min(depot_ind[j], start_b + 6)):
                                if start_a == end_a and start_b == end_b:
                                    continue
                                new_path = []
                                new_path.extend(travel_path[:start_a])
                                new_path.extend(travel_path[start_b:end_b + 1])
                                new_path.extend(travel_path[end_a:start_b])
                                new_path.extend(travel_path[start_a:end_a])
                                new_path.extend(travel_path[end_b + 1:])

                                depot_before_start_a = depot_ind[i - 1]

                                depot_before_start_b = depot_ind[j - 1] + (end_b - start_b) - (end_a - start_a) + 1
                                if not graph.nodes[new_path[depot_before_start_b]].is_depot:
                                    raise RuntimeError('error')

                                success_route_a = False
                                check_ant = Ant(graph, new_path[depot_before_start_a])
                                for ind in new_path[depot_before_start_a + 1:]:
                                    if check_ant.check_condition(ind):
                                        check_ant.move_to_next_index(ind)
                                        if graph.nodes[ind].is_depot:
                                            success_route_a = True
                                            break
                                    else:
                                        break

                                check_ant.clear()
                                del check_ant

                                success_route_b = False
                                check_ant = Ant(graph, new_path[depot_before_start_b])
                                for ind in new_path[depot_before_start_b + 1:]:
                                    if check_ant.check_condition(ind):
                                        check_ant.move_to_next_index(ind)
                                        if graph.nodes[ind].is_depot:
                                            success_route_b = True
                                            break
                                    else:
                                        break
                                check_ant.clear()
                                del check_ant

                                if success_route_a and success_route_b:
                                    new_path_distance = Ant.cal_total_travel_distance(graph, new_path)
                                    if new_path_distance < travel_distance:
                                        
                                        for temp_ind in range(1, len(new_path)):
                                            if graph.nodes[new_path[temp_ind]].is_depot and graph.nodes[new_path[temp_ind - 1]].is_depot:
                                                new_path.pop(temp_ind)
                                                break
                                        return new_path, new_path_distance, i
                                else:
                                    new_path.clear()

        return None, None, None

    def local_search_procedure(self, stop_event: Event):
        
        new_path = copy.deepcopy(self.travel_path)
        new_path_distance = self.total_travel_distance
        times = 100
        count = 0
        i_start = 1
        while count < times:
            temp_path, temp_distance, temp_i = Ant.local_search_once(self.graph, new_path, new_path_distance, i_start, stop_event)
            if temp_path is not None:
                count += 1

                del new_path, new_path_distance
                new_path = temp_path
                new_path_distance = temp_distance

                i_start = (i_start + 1) % (new_path.count(0)-1)
                i_start = max(i_start, 1)
            else:
                break

        self.travel_path = new_path
        self.total_travel_distance = new_path_distance
        print('[local_search_procedure]: local search finished')