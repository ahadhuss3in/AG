from services.Rag.agent.StateGraph.RagState import AgentState
from app.config import config
from langchain_groq import ChatGroq
import logfire


llm = ChatGroq(api_key=config.GROQ_API_KEY, model=config.MODEL_REASONING)

def planned_node(state: AgentState):
    """
    The planned is set to decide if a search is needed based on the conversation
    """
    ## import the history of messages 
    history = ""
    for msg in state["messages"][:-1]:
        ## determine what is the type of the  message to check if its user or Assistan
        role  = "User" if msg["role"] == "user" else "Assistant"
        history += f"{role}:{msg['content']}\n"
    
    user_message = state["messages"][-1]["content"] if state["messages"] else ""
    
    prompt = f"""
    You are an intelligent Assistant Planner. 
    Analyze the conversation history and the latest user message.
    
    CONVERSATION HISTORY:
    {history}
    
    LATEST MESSAGE:
    "{user_message}"
    
    Task:
    1. If the latest message is a greeting (hi, hello) or a question that can be answered using ONLY the conversation history above (e.g., "what is my name" or details mentioned in the history), respond with 'CONVERSATIONAL'.
    2. If it is a technical question about Kubernetes, Intel, or Networking that requires fresh documentation, output a refined search query.
    
    Output ONLY 'CONVERSATIONAL' or the search query.
    """
    with logfire.span("Planning Decision"):
        decision=llm.invoke(prompt).content.strip()
        logfire.info(f"Intent Identified : {decision}")


    ## just for Logs in logfire
    if decision == "CONVERSATIONAL":
        return {
            "query":"CONVERSATIONAL",
            "status":"Handling conversationally (using memory)...",
            "plan":["Intent:Conersational", "Retrieval:Skipped"]
        }
    return {
         "query":decision,
         "status":f"Technical research needed. Searching for :{decision}",
         "plan":["Intent:Technical", f"Search Term:{decision}"]
    }