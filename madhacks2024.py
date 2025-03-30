from flask import Flask, jsonify, request
import os
import json
from combination_logic import start_get_combinations

app = Flask(__name__)
DATA_DIR = "data"  # Base directory containing subdirectories like "soe" and "sohe"

# Helper function to load JSON files from subdirectories
def load_json_files():
    programs = []
    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith(".json"):
                filepath = os.path.join(root, file)
                with open(filepath) as f:
                    data = json.load(f)
                    programs.append({"title": data["title"], "total_min_credits": data["total_min_credits"]})
    return programs

# Endpoint to list all programs
@app.route('/programs', methods=['GET'])
def get_all_programs():
    programs = load_json_files()
    return jsonify(programs)

# Endpoint to fetch details of a specific program by title
@app.route('/program/<title>', methods=['GET'])
def get_program(title):
    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith(".json") and file == f"{title.replace(' ', '_')}.json":
                filepath = os.path.join(root, file)
                with open(filepath) as f:
                    return jsonify(json.load(f))
    return jsonify({'error': 'Program not found'}), 404


# Endpoint to suggest degree combinations
@app.route('/suggest-combinations', methods=['POST'])
def suggest_combinations():

    data = request.json
    completed_courses = data.get("completed_courses", [])
    ongoing_degrees = data.get("ongoing_degrees", [])
    primary_college = data.get("primary_college", "")
    remaining_semesters = data.get("remaining_semesters", 0)
    credits_per_semester = data.get("credits_per_semester", 0)
    
    combinations = start_get_combinations(completed_courses, ongoing_degrees, primary_college, remaining_semesters, credits_per_semester, DATA_DIR)

    return jsonify({'message': 'Combination suggestion logic not implemented yet'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

