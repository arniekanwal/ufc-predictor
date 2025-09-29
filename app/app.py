from flask import Flask, render_template, request, jsonify

import json

app = Flask(__name__)

def load_fighter_names():
    with open("data/fighters.json", "r") as file:
        data = json.load(file)
        return data["fighters"]


# Load all UFC fighter names in-memory on app startup
UFC_FIGHTERS = load_fighter_names()

def search_autocomplete(query, limit=10):
    """
    Search fighters with ranking:
    1. Exact matches first
    2. Starts with query
    3. Contains query
    """
    if not query:
        return []
    
    query_lower = query.lower()
    
    exact_matches = []
    starts_with = []
    contains = []
    
    for fighter in UFC_FIGHTERS:
        fighter_lower = fighter.lower()
        
        if fighter_lower == query_lower:
            exact_matches.append(fighter)
        elif fighter_lower.startswith(query_lower):
            starts_with.append(fighter)
        elif query_lower in fighter_lower:
            contains.append(fighter)
    
    # Combine results with priority order
    results = exact_matches + starts_with + contains
    return results[:limit]

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
    
    # Validate that both fighters exist in our database
    if fighter1 not in UFC_FIGHTERS or fighter2 not in UFC_FIGHTERS:
        return jsonify({'error': 'Invalid fighter selection'}), 400
    
    if fighter1 == fighter2:
        return jsonify({'error': 'Cannot select the same fighter twice'}), 400
    
    print(f"Processing prediction: {fighter1} vs {fighter2}")
    
    return jsonify({
        'message': f'Prediction submitted for {fighter1} vs {fighter2}',
        'status': 'success'
    })

if __name__ == '__main__':
    app.run(debug=True)