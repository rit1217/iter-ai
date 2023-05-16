import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from math import sqrt

from .config import DATA_FILEPATHS
from components.utils import process_strings


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
    
    def recommend_attraction(self, features, activities, destination, top_n=15):
        # df = pd.read_csv(DATA_FILEPATHS['place_with_type'])
        candidates_count = len(features)
        candidates_id = []
        features = process_strings(features)
        activities = process_strings(activities)

        connection_url = f"postgresql://data:data@dev.se.kmitl.ac.th:54330/data"
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
            result = connection.execute(query)

        attractions = pd.DataFrame(result.fetchall(), columns=result.keys())
        attractions = attractions[attractions.destination == destination]
        columns = ['place_id', 'place_name', 'attraction_types', 'category_code', 'latitude', 'longitude', 'opening_hours', 'popularity']
        place_ids = attractions.place_id.tolist()


        return df_candidates[columns[:len(columns)-1]][:top_n]

    def recommend_restaurant(self, cuisine_types, destination, top_n):
        num_dist = top_n // len(cuisine_types)
        candidates_id = []
        columns = ['place_id', 'place_name', 'cuisine_types', 'category_code', 'latitude', 'longitude', 'opening_hours', 'popularity']

        df_place = pd.read_csv(DATA_FILEPATHS['place'])
        df_ophr = pd.read_csv(DATA_FILEPATHS['opening_hour'])
        df_place_pop = pd.read_csv(DATA_FILEPATHS['place_popularity'])
        df_cuisine_types = pd.read_csv(DATA_FILEPATHS['cuisine_type'])
        
        df_place = df_place[df_place.category_code == "RESTAURANT"]
        df_cuisine_types = df_cuisine_types.groupby(['place_id']).agg({'description': list}).reset_index()
        grouped = df_ophr.groupby(['place_id']).apply(lambda x: x[['day', 'opening_time', 'closing_time']].apply(row_to_dict, axis=1).tolist()).reset_index(name='opening_hours')

        df_merged = pd.merge(df_place, df_cuisine_types, how="left", on="place_id")
        df_merged = pd.merge(df_merged, grouped, on='place_id', how='left')
        df_merged = pd.merge(df_merged, df_place_pop, how="left", on=["place_id", "place_name", "destination"])
        df_merged.rename(columns={'description': 'cuisine_types'}, inplace=True)

        for cuisine in cuisine_types:
            mask = (df_merged[~df_merged.cuisine_types.isna()].
                    cuisine_types.apply(lambda row: cuisine in row))
            temp_df = df_merged[~df_merged.cuisine_types.isna()]
            candidates_id.append(self._roulette_selector(temp_df[mask].copy(), size=num_dist))
            
        candidates_id = np.concatenate(candidates_id)

        if len(candidates_id) < top_n:
            candidates_id = np.concatenate((candidates_id, self._roulette_selector(df_merged[~df_merged.cuisine_types.isna()].copy(), size=top_n-len(candidates_id))))

        df_candidates = df_merged[df_merged.place_id.isin(candidates_id)]
        return df_candidates[columns[:len(columns)-1]][:top_n]
            