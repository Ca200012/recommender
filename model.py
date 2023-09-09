from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd
from joblib import dump
from collections import defaultdict

import numpy as np

tfidf_vectorizer = None 
tfidf_matrix = None
df_articles = None  

def prepare_model(engine):
    global df_articles, tfidf_matrix, tfidf_vectorizer

    df_articles = pd.read_sql("SELECT id, display_name, brand_name, colour, season, pattern, `usage`, gender_id, category_id, subcategory_id, articletype_id FROM articles", engine)

    df_articles['features'] = df_articles.apply(lambda row: ' '.join([
        str(row['display_name']),
        str(row['brand_name']),
        str(row['colour']),
        str(row['season']),
        str(row['usage']),
        str(row['gender_id']),
        str(row['category_id']),
        str(row['subcategory_id']),
        str(row['articletype_id'])]), axis=1)
    
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(df_articles['features'])

    dump(tfidf_vectorizer, 'tfidf_vectorizer.joblib')

def make_recommendation(data):
    global df_articles, tfidf_matrix, tfidf_vectorizer

    article_ids = df_articles['id'].values
    article_genders = df_articles['gender_id'].values
    
    unique_gender_ids = set(item['gender_id'] for item in data)
    single_gender = unique_gender_ids.pop() if len(unique_gender_ids) == 1 else None
    
    score_accumulator = defaultdict(float)
    
    for item in data:
        query_features = ' '.join([
            str(item[k]) for k in [
                'display_name', 'brand_name', 'colour', 'season', 'usage',
                'gender_id', 'category_id', 'subcategory_id', 'articletype_id'
            ]
        ])
        
        query_vector = tfidf_vectorizer.transform([query_features])
        cosine_sim_query = linear_kernel(query_vector, tfidf_matrix).flatten()

        relevant_indices = np.where(
            (article_ids != item['id']) & 
            ((article_genders == single_gender) | (single_gender is None))
        )[0]

        for i in relevant_indices:
            score_accumulator[i] += cosine_sim_query[i]
            
    sorted_indices = sorted(score_accumulator, key=score_accumulator.get, reverse=True)[:10]

    recommended_ids = article_ids[sorted_indices].tolist()

    return recommended_ids
    