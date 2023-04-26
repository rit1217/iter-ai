import pandas as pd
import numpy as np
from sqlalchemy import create_engine

from .config import DATA_FILEPATHS
from components.utils import row_to_dict


class PlaceRecommender:

    def _jaccard_simmilarity(self, A, B):
        nominator = set(A).intersection(B)
        denominator = set(A).union(B)
        similarity = len(nominator)/len(denominator)
        
        return similarity
    
    def _calc_feature_sim(self, features, item_feature, items_list):
        items_list['similarity_score'] = items_list.apply(lambda x: self._jaccard_simmilarity(features, x[item_feature]), axis=1)
        
        return items_list[['place_id', 'similarity_score']].sort_values('similarity_score', ascending=False)
    
    def _roulette_selector(self, places):
        pop_fitness = places['popularity'].sum()
        places['probability'] = places.popularity / pop_fitness

        return np.random.choice(places['place_id'], p=places['probability'])
    
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
