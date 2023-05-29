import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from math import sqrt
import os

from .config import DATA_FILEPATHS
from components.utils import *


class PlaceRecommender:
    
    def _calc_dist(self, user_vec, place_vec):
        distances = place_vec.loc[:, place_vec.columns != 'place_id'].apply(lambda row: self._dist(row, user_vec.values.flatten()), axis=1)
        df = place_vec.copy()
        df['score'] = distances
        return df

    def _dist(self, vec_a, vec_b):
        return sqrt(sum((e1-e2)**2 for e1, e2 in zip(vec_a, vec_b)))
    
    def _roulette_selector(self, places, size=15):
        pop_fitness = places['popularity'].sum()
        places['probability'] = places.popularity / pop_fitness
        # print(places.probability)
        return np.random.choice(places['place_id'], size=size, p=places['probability'], replace=False)
    
    def recommend_attraction(self, attraction_types, activities, destination, top_n=15):
        attraction_types = process_strings(attraction_types)
        activities = process_strings(activities)
        destination = destination.upper()

        connection_url = os.getenv('DB_URL')
        engine = create_engine(connection_url)

        with engine.connect() as connection:
            query = text(
                "SELECT p.place_id, p.place_name, p.latitude, p.longitude, p.category_code, p.destination, \
                    a_t.attraction_types, \
                    a.activities, \
                    po.popularity, \
                    json_agg(json_build_object('day', oh.day, 'opening_time', oh.opening_time, 'closing_time', oh.closing_time) \
                        ORDER BY CASE oh.day WHEN 'Sunday' THEN 1 WHEN 'Monday' THEN 2 WHEN 'Tuesday' THEN 3 WHEN 'Wednesday' THEN 4 \
                        WHEN 'Thursday' THEN 5 WHEN 'Friday' THEN 6 WHEN 'Saturday' THEN 7 ELSE 8 END) \
                    AS opening_hours \
                FROM ( \
                    SELECT place_id, place_name, latitude, longitude, category_code, destination \
                    FROM place \
                    WHERE category_code = 'ATTRACTION' \
                ) p \
                LEFT JOIN ( \
                    SELECT place_id, ARRAY_AGG(description) AS attraction_types \
                    FROM attraction_type \
                    GROUP BY place_id \
                ) a_t ON p.place_id = a_t.place_id \
                LEFT JOIN ( \
                    SELECT place_id, ARRAY_AGG(description) AS activities \
                    FROM activity \
                    GROUP BY place_id \
                ) a ON p.place_id = a.place_id \
                LEFT JOIN opening_hour oh ON p.place_id = oh.place_id \
                LEFT JOIN popularity po ON p.place_id = po.place_id AND p.place_name = po.place_name AND p.destination = po.destination \
                GROUP BY p.place_id, p.place_name, p.latitude, p.longitude, p.category_code, p.destination, a_t.attraction_types, a.activities, po.popularity;"
            )
            result_attractions = connection.execute(query)
            result_rank_vect = connection.execute(text("SELECT * FROM attraction_rank_vector;"))

        attractions = pd.DataFrame(result_attractions.fetchall(), columns=result_attractions.keys())
        attractions = attractions[attractions.destination == destination]

        attractions['activities_process'] = attractions.activities.apply(lambda x: process_strings(x) if isinstance(x, list) else [])
        attractions['attraction_types_process'] = attractions.attraction_types.apply(lambda x: process_strings(x) if isinstance(x, list) else [])

        columns = ['place_id', 'place_name', 'attraction_types', 'category_code', 'latitude', 'longitude', 'opening_hours', 'popularity']
        place_ids = attractions.place_id.tolist()

        attraction_types_unique = attractions.attraction_types_process.explode().unique().tolist()
        attraction_types = [type for type in attraction_types if type in attraction_types_unique]

        activities_unique = attractions.activities_process.explode().unique().tolist()
        activities = [activity for activity in activities if activity in activities_unique]

        attractions_vec = pd.DataFrame(result_rank_vect.fetchall(), columns=result_rank_vect.keys())
        attractions_vec = attractions_vec[attractions_vec.place_id.isin(place_ids)]
        features_set = attraction_types + activities

        #initialize variables
        candidates = []
        repeat_len_count = 0
        prev_candidates_len = 0
        
        while top_n > 0:
            if len(features_set) == 0:
                features_set = attraction_types + activities

            # select feature from set of features
            feature = features_set[0]
            
            # get pool of attractions if it contain the chosen feature
            selection_pool = attractions_vec.loc[attractions_vec[feature] > 0, :].sort_values(feature, ascending=False)
            
            # create user vector from feature set
            user_vec = pd.DataFrame(np.zeros((1, len(attractions_vec.columns[1:]))), columns=attractions_vec.columns[1:])
            user_vec.loc[:, features_set] = 1

            # calculate distance between user vector and attractions from selection pool
            result = self._calc_dist(user_vec, selection_pool).sort_values('score').reset_index(drop=True)

            # find top place that is not in the candidate list
            result_index = 0
            complete_iteration = True
            for index, row in result.iterrows():
                if row.place_id not in candidates:
                    result_index = index
                    complete_iteration = False
                    break
            
            if not complete_iteration:
                # print(result.loc[result_index, ['place_id', 'score']])
                # print(features_set)
                # retrieve feature of selected candidates
                result_feature = result.columns[result.iloc[result_index].ne(0)]
                result_feature = result_feature[1: -1]

                # remove feature from feature pool
                features_set = [item for item in features_set if item not in result_feature]
                
                # add place id to candidate list
                candidates.append(result.loc[result_index, 'place_id'])
                attractions_vec = attractions_vec.drop(attractions_vec[attractions_vec.place_id.isin(candidates)].index)
                
                top_n -= 1

            # print(len(candidates))
            # Check if candidates list length is repeating
            if len(candidates) == prev_candidates_len:
                repeat_len_count += 1
                if repeat_len_count >= 3:
                    break
            else:
                repeat_len_count = 0
                prev_candidates_len = len(candidates)
        
        attractions_rm_selected = attractions.drop(attractions[attractions.place_id.isin(candidates)].index)

        # Convert attractions DataFrame to list of dictionaries
        attractions_list = attractions_rm_selected.to_dict('records')

        # Fill remaining candidates using n_nearest_place function
        remaining_candidates = n_nearest_place(attractions[attractions.place_id.isin(candidates)].to_dict('records'), attractions_list, top_n)
        candidates.extend([place['place_id'] for place in remaining_candidates])

        # print(top_n)
        # print(features_set)
        # print(len(candidates))
        # print(candidates)
        # print(attractions)

        output = attractions[attractions.place_id.isin(candidates)].reset_index()

        return output[columns[:len(columns)-1]]

    def recommend_restaurant(self, cuisine_types, destination, top_n):
        num_dist = top_n // len(cuisine_types)
        candidates_id = []
        columns = ['place_id', 'place_name', 'cuisine_types', 'category_code', 'latitude', 'longitude', 'opening_hours', 'popularity']

        connection_url = os.getenv('DB_URL')
        engine = create_engine(connection_url)

        with engine.connect() as connection:
            query = text(
                "SELECT p.place_id, p.place_name, p.latitude, p.longitude, p.category_code, p.destination, \
                    c_t.cuisine_types, \
                    po.popularity, \
                    json_agg(json_build_object('day', oh.day, 'opening_time', oh.opening_time, 'closing_time', oh.closing_time) \
                        ORDER BY CASE oh.day WHEN 'Sunday' THEN 1 WHEN 'Monday' THEN 2 WHEN 'Tuesday' THEN 3 WHEN 'Wednesday' THEN 4 \
                        WHEN 'Thursday' THEN 5 WHEN 'Friday' THEN 6 WHEN 'Saturday' THEN 7 ELSE 8 END) \
                    AS opening_hours \
                FROM ( \
                    SELECT place_id, place_name, latitude, longitude, category_code, destination \
                    FROM place \
                    WHERE category_code = 'RESTAURANT' \
                ) p \
                LEFT JOIN ( \
                    SELECT place_id, ARRAY_AGG(description) AS cuisine_types\
                    FROM cuisine_type \
                    GROUP BY place_id \
                ) c_t ON p.place_id = c_t.place_id \
                LEFT JOIN opening_hour oh ON p.place_id = oh.place_id \
                LEFT JOIN popularity po ON p.place_id = po.place_id AND p.place_name = po.place_name AND p.destination = po.destination \
                GROUP BY p.place_id, p.place_name, p.latitude, p.longitude, p.category_code, p.destination, c_t.cuisine_types, po.popularity;"
            )
            result = connection.execute(query)

        restaurants = pd.DataFrame(result.fetchall(), columns=result.keys())
        restaurants = restaurants[restaurants.destination == destination]
        
        if len(restaurants[restaurants.destination == destination].cuisine_types.tolist()) == 0:
            candidates_id = np.random.choice(restaurants[restaurants.destination == destination].copy(), size=top_n, replace=False)
        else:
            selection_pool = restaurants[~restaurants.cuisine_types.isna()]
            for cuisine in cuisine_types:
                mask = selection_pool.cuisine_types.apply(lambda row: cuisine in row)
                selection = self._roulette_selector(selection_pool[mask].copy(), size=min(num_dist, len(selection_pool[mask])))
                candidates_id.extend(selection)

            if len(candidates_id) < top_n:
                remaining_candidates = self._roulette_selector(selection_pool[~selection_pool.place_id.isin(candidates_id)].copy(),
                                                            size=top_n - len(candidates_id))
                candidates_id.extend(remaining_candidates)

        df_candidates = restaurants[restaurants.place_id.isin(candidates_id)]
        print(len(df_candidates))
        return df_candidates[columns[:len(columns)-1]][:top_n]
    
    def recommend_accommodation(self, other_places):
        columns = ['place_id', 'place_name', 'category_code', 'latitude', 'longitude', 'opening_hours', 'popularity']

        connection_url = os.getenv('DB_URL')
        engine = create_engine(connection_url)

        with engine.connect() as connection:
            query = text(
                "SELECT p.place_id, p.place_name, p.latitude, p.longitude, p.category_code, p.destination, \
                    po.popularity, \
                    json_agg(json_build_object('day', oh.day, 'opening_time', oh.opening_time, 'closing_time', oh.closing_time) \
                        ORDER BY CASE oh.day WHEN 'Sunday' THEN 1 WHEN 'Monday' THEN 2 WHEN 'Tuesday' THEN 3 WHEN 'Wednesday' THEN 4 \
                        WHEN 'Thursday' THEN 5 WHEN 'Friday' THEN 6 WHEN 'Saturday' THEN 7 ELSE 8 END) \
                    AS opening_hours \
                FROM ( \
                    SELECT place_id, place_name, latitude, longitude, category_code, destination \
                    FROM place \
                    WHERE category_code = 'ACCOMMODATION' \
                ) p \
                LEFT JOIN opening_hour oh ON p.place_id = oh.place_id \
                LEFT JOIN popularity po ON p.place_id = po.place_id AND p.place_name = po.place_name AND p.destination = po.destination \
                GROUP BY p.place_id, p.place_name, p.latitude, p.longitude, p.category_code, p.destination, po.popularity;"
            )
            result = connection.execute(query)

        accom_list = pd.DataFrame(result.fetchall(), columns=result.keys())
        accom_list = accom_list[columns]

        return nearest_place(other_places, accom_list.to_dict('records'))