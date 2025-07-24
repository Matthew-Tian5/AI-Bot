from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_tool


load_dotenv()

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]
    

llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a research assistant that will help generate a research paper.
            Answer the user query and use neccessary tools. 
            Wrap the output in this format and provide no other text\n{format_instructions}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [search_tool, wiki_tool, save_tool]
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
query = input("What can i help you research? ")
raw_response = agent_executor.invoke({"query": query})

try:
    structured_response = parser.parse(raw_response.get("output")[0]["text"])
    print(structured_response)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(f"""
    <html>
    <head>
        <title>Research Output</title>
    </head>
    <body>
        <h1>Topic: {structured_response.topic}</h1>
        <h2>Summary</h2>
        <p>{structured_response.summary}</p>
        <h3>Sources</h3>
        <ul>
            {''.join(f'<li>{src}</li>' for src in structured_response.sources)}
        </ul>
        <h3>Tools Used</h3>
        <ul>
            {''.join(f'<li>{tool}</li>' for tool in structured_response.tools_used)}
        </ul>
    </body>
    </html>
    """)

except Exception as e:
    print("Error parsing response", e, "Raw Response - ", raw_response)