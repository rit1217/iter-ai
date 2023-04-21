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
    
    def recommend(self, features, top_n=10, threshold=0.5):
        df = pd.read_csv(DATA_FILEPATHS['place_with_type'])
        candidates = self._calc_feature_sim(features, df)
        df_candidates = pd.DataFrame(candidates, columns=['place_id', 'items_feature', 'sim_score'])
        recommended_df = df_candidates[df_candidates.sim_score >= threshold].sort_values('sim_score', ascending=False)

        return recommended_df['place_id'][:top_n]
    