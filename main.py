from data_retrieval import get_data
from data_transformation import transform_data
from database import store_structure, store_articles
from flask import Flask, request, jsonify
from model import prepare_model, make_recommendation
from db_utility import get_db_engine

#items = get_data()

#transformed_data = transform_data(items)

#store_structure()

#store_articles()

#print (len(transformed_data))

#recommender
app = Flask(__name__)

engine = get_db_engine()

# Initialize the model
prepare_model(engine)

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.json
        ordered_items = data.get('ordered', [])
        viewed_items = data.get('viewed', [])
        
        all_items = ordered_items + viewed_items
        recommendations = make_recommendation(all_items)

        return jsonify(recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/', methods=['GET'])
def greet():
    return 'Recommender here!';
    
if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)

