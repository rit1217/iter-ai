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
        columns = ['place_id', 'place_name', 'attraction_types', 'category_code', 'latitude', 'longitude', 'opening_hours', 'popularity']
        
        df_place = pd.read_csv(DATA_FILEPATHS['place'])
        df_activity = pd.read_csv(DATA_FILEPATHS['activity'])
        df_atr_type = pd.read_csv(DATA_FILEPATHS['attraction_type'])
        df_place_pop = pd.read_csv(DATA_FILEPATHS['place_popularity'])
        df_ophr = pd.read_csv(DATA_FILEPATHS['opening_hour'])

        df_place = df_place[df_place.category_code == "ATTRACTION"]
        df_atr_type = df_atr_type.groupby(['place_id']).agg({'description': list}).reset_index()
        df_activity = df_activity.groupby(['place_id']).agg({'description': list}).reset_index()

        df_merged = pd.merge(df_place, df_atr_type, how="left", on="place_id")
        df_merged = pd.merge(df_merged, df_activity, how="left", on="place_id")
        df_merged = pd.merge(df_merged, df_place_pop, how="left", on=["place_id", "place_name", "destination"])
        df_merged.rename(columns={'description_x': 'attraction_types', 'description_y': 'activities'}, inplace=True)
        
        grouped = df_ophr.groupby(['place_id']).apply(lambda x: x[['day', 'opening_time', 'closing_time']].apply(row_to_dict, axis=1).tolist()).reset_index(name='opening_hours')
        df_merged = pd.merge(df_merged, grouped, on='place_id', how='left')

        df_merged.attraction_types = df_merged.attraction_types.apply(lambda x: x if isinstance(x, list) else [])
        df_merged = df_merged[columns]

        for feature in features:
            mask = (df_merged[~df_merged.attraction_types.isna()].
                    attraction_types.apply(lambda row: feature in row))
            candidates_id.append(self._roulette_selector(df_merged[mask].copy()))

        candidates = self._calc_feature_sim(features, 'attraction_types', df_merged)
        candidates_id += candidates['place_id'].values.tolist()[:top_n-candidates_count]
        df_candidates = df_merged[df_merged.place_id.isin(candidates_id)]

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
            