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
    
    def _calc_feature_sim(self, features, items_list):
        similarities = []
        items_list = items_list.values.tolist()

        for item in items_list:
            sim = self._jaccard_simmilarity(features, eval(item[2]))
            similarities.append([item[1], item[2], sim])
        
        return similarities
    
    def recommend(self, features, top_n=10, threshold=0.5):
        df = pd.read_csv(DATA_FILEPATHS['place_with_type'])
        candidates = self._calc_feature_sim(features, df)
        df_candidates = pd.DataFrame(candidates, columns=['place_id', 'items_feature', 'sim_score'])
        recommended_df = df_candidates[df_candidates.sim_score >= threshold].sort_values('sim_score', ascending=False)

        return recommended_df['place_id'][:top_n]
    