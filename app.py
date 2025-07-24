from flask import Flask, request, jsonify
from your_agent_module import agent_executor, parser  # Adjust import paths as needed

app = Flask(__name__)

@app.route('/research', methods=['POST'])
def research():
    query = request.json.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    try:
        raw_response = agent_executor.invoke({"query": query})
        # Debug: print raw_response to console
        print("Raw response:", raw_response)
        structured_response = parser.parse(raw_response.get("output")[0]["text"])
        return jsonify(structured_response.dict())
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)