from flask import Flask, render_template, request, jsonify

from rapidfuzz import fuzz, process
import json
import requests

app = Flask(__name__)

def load_fighter_names():
    with open("data/fighters.json", "r") as file:
        data = json.load(file)
        return data["fighters"]


# Load all UFC fighter names in-memory on app startup
UFC_FIGHTERS = load_fighter_names()

def search_autocomplete(query, limit=10):
    if not query:
        return []
    
    res = process.extract(
        query,
        UFC_FIGHTERS,
        scorer=fuzz.WRatio,
        limit=limit
    )
    
    # res --> [(str, weight, index), ...]
    return [r[0] for r in res if r[1] > 60]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_fighters')
def api_search_fighters():
    query = request.args.get('q', '')
    results = search_autocomplete(query)
    return jsonify(results)

# TODO: needs to make request to ml-api service
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    fighter1 = data.get('fighter1')
    fighter2 = data.get('fighter2')
    
    if fighter1 == fighter2:
        return jsonify({'error': 'Cannot select the same fighter twice'}), 400
    
    resp = requests.post(
        "http://ml-api:4000/predict",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    if resp.status_code != 200:
        return jsonify({"error": "Prediction failed..."}), 500
    
    return jsonify(resp.json())

if __name__ == '__main__':
    app.run(debug=True)