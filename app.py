from flask import Flask, request, jsonify
from flask_cors import CORS
from main import run_research  # Import the function

app = Flask(__name__)
CORS(app)

@app.route('/research', methods=['GET', 'POST'])
def research():
    if request.method == 'POST':
        query = request.json.get('query')
        if not query:
            return jsonify({"error": "No query provided"}), 400
        result = run_research(query)
        return jsonify(result)
    else:
        return jsonify({"message": "Send a POST request with your query."})

if __name__ == '__main__':
    app.run(debug=True, port=5500)