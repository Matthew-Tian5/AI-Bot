from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor

from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS

# --- Tool Definitions ---
def save_to_txt(data: str, filename: str = "research_output.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"--- Research Output ---\nTimestamp: {timestamp}\n\n{data}\n\n"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)
    return f"Data successfully saved to {filename}"

save_tool = Tool(
    name="save_text_to_file",
    func=save_to_txt,
    description="Saves structured research data to a text file.",
)

search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="search",
    func=search.run,
    description="Search the web for information",
)

api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=100)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

# --- LangChain Setup ---
load_dotenv()

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")  # Ensure your Anthropic API key is in .env
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         """
You are a research assistant that will help generate a research paper.
Answer the user query and use neccessary tools.
Wrap the output in this format and provide no other text
{format_instructions}
"""),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}")
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [search_tool, wiki_tool, save_tool]

agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def run_research(query: str) -> dict:
    try:
        raw_response = agent_executor.invoke({"query": query})
        # DEBUG: print(raw_response) to console to inspect the output structure
        # You may need to adjust this parsing line based on actual output
        output_text = raw_response.get("output", [{}])[0].get("text", "")
        if not output_text:
            output_text = str(raw_response)
        structured_response = parser.parse(output_text)
        return structured_response.dict()
    except Exception as e:
        return {
            "topic": query,
            "summary": f"Error parsing response: {e}",
            "sources": [],
            "tools_used": []
        }

# --- Flask App ---
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


'''
This is for if you want to set up aws lambda 
'''
import json
from main import run_research

def lambda_handler(event, context):
    try:
        # Check HTTP method
        method = event.get("httpMethod", "GET")
        
        if method == 'POST':
            # Parse request body, which is a string
            body = event.get('body')
            if body:
                body_json = json.loads(body)
                query = body_json.get('query')
            else:
                query = None

            if not query:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "No query provided"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            result = run_research(query)
            return {
                "statusCode": 200,
                "body": json.dumps(result),
                "headers": {"Content-Type": "application/json"}
            }
        else:
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Send a POST request with your query."}),
                "headers": {"Content-Type": "application/json"}
            }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {"Content-Type": "application/json"}
        }