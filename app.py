from flask import Flask, request, jsonify
from your_agent_module import agent_executor, parser  # Import your agent and parser

app = Flask(__name__)

@app.route('/research', methods=['POST'])
def research():
    query = request.json.get('query')
    raw_response = agent_executor.invoke({"query": query})
    try:
        structured_response = parser.parse(raw_response.get("output")[0]["text"])
        return jsonify(structured_response.dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)