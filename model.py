from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd
from joblib import dump, load
from collections import defaultdict

from concurrent.futures import ThreadPoolExecutor
import numpy as np

tfidf_vectorizer = None #tfidf=term frequency inverse document frequency
tfidf_matrix = None
df_articles = None  #df=document frequency

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

def process_item(i, cosine_sim_query, data_ids, single_gender, score_accumulator):
    score = cosine_sim_query[i]
    if df_articles.iloc[i]['id'] in data_ids:
        return
    if single_gender is not None and df_articles.iloc[i]['gender_id'] != single_gender:
        return
    score_accumulator[i] += score

def make_recommendation(data):
    global df_articles, tfidf_matrix, tfidf_vectorizer

    # Precompute IDs and gender IDs for faster lookup
    article_ids = df_articles['id'].values
    article_genders = df_articles['gender_id'].values

    # Create a set to store the IDs of the articles that are in the data
    data_ids = set(item['id'] for item in data)
    
    # Check if all articles have the same gender_id
    unique_gender_ids = set(item['gender_id'] for item in data)
    single_gender = unique_gender_ids.pop() if len(unique_gender_ids) == 1 else None
    
    # Initialize a defaultdict to accumulate scores
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

        # Use Numpy's where method to filter relevant indices
        # Assuming that 'continue' cases are rarer than the opposite
        relevant_indices = np.where(
            (article_ids != item['id']) & 
            ((article_genders == single_gender) | (single_gender is None))
        )[0]

        # Update score accumulator based on relevant indices
        for i in relevant_indices:
            score_accumulator[i] += cosine_sim_query[i]
            
    # Sort items by the accumulated score
    sorted_indices = sorted(score_accumulator, key=score_accumulator.get, reverse=True)[:10]

    # Get only the 'id' of the recommended articles
    recommended_ids = article_ids[sorted_indices].tolist()

    return recommended_ids
    