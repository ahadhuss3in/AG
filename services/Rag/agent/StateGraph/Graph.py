### Making the State Graph and Initializing it.


## connecting akk the components
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from services.Rag.agent.StateGraph.RagState import AgentState
from services.Rag.agent.nodes.planner import planned_node
from services.Rag.agent.nodes.responder import generate_node
from services.Rag.agent.nodes.retriever import retrieve_node

## Initialize the graph
graph = StateGraph(AgentState)


## define what are the nodes of the graph
graph.add_node("planner",planned_node)
graph.add_node("retriver", retrieve_node)
graph.add_node("generate_res", generate_node)