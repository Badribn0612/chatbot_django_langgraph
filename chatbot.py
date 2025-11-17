from typing import Annotated
from langchain_core.messages import SystemMessage
from typing_extensions import TypedDict

from langchain.chat_models import init_chat_model
# from langchain_tavily import TavilySearch

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.tools import tool

from dotenv import load_dotenv

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

vector_store = Chroma(
    collection_name="rag_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",
)

retriever = vector_store.as_retriever(
    search_type="mmr", search_kwargs={"k": 2, "fetch_k": 10}
)

def _format_document(document) -> str:
    title = document.metadata.get("title")
    url = document.metadata.get("url")
    metadata_summary = (
        f"Title: {title}" if title else f"Metadata: {document.metadata}"
    )
    if url:
        metadata_summary = f"{metadata_summary}\nURL: {url}"

    return f"{metadata_summary}\nContent:\n{document.page_content}"


@tool
def retrieve_relevant_documents(query: str) -> list:
    "This tool will retrieve relevant document based on the query, this tool will give you all the available context"
    results = retriever.invoke(query)
    formatted_results = [_format_document(doc) for doc in results]
    return formatted_results

class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

# tool = TavilySearch(max_results=2)
# tools = [tool]
tools = [retrieve_relevant_documents]
llm_with_fallbacks = init_chat_model("google_genai:gemini-2.0-flash").with_fallbacks(
    [init_chat_model("groq:llama-3.3-70b-versatile")]
)
llm_with_tools = llm_with_fallbacks.bind_tools(tools)


def chatbot(state: State):
    SYSTEM_PROMPT = (
        "Use only the following pieces of context to answer the question at the end.\n"
        "If you don't know the answer, just say that you don't know, don’t try to make up an answer.\n"
        "Always use the tool to retrieve relevant content before answering"
        "Keep the answer as concise as possible."
    )

    system_message = SystemMessage(content=SYSTEM_PROMPT)

    return {
        "messages": [
            llm_with_tools.invoke([system_message] + state["messages"]),
        ]
    }


graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=[retrieve_relevant_documents])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile()

def get_chatbot_response(messages: list):
    print(f"Input messages to graph: {messages}")
    result = graph.invoke({"messages": messages})
    print(f"Graph result: {result}")
    return result