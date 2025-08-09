import os
import json
from typing import TypedDict

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Load text file content
with open('knowledge.txt', 'r', encoding='utf-8') as f:
    file_content = f.read()

# Load JSON object
with open('data.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)


class AgentState(TypedDict):
    messages: list[HumanMessage | AIMessage]
    knowledge: str
    json_data: dict
    currQuestion: str
    currAnswer: str
    cookie: list
    llm: ChatGoogleGenerativeAI


def create_agent_state() -> AgentState:
    """Initialize the agent's state with empty messages and loaded knowledge/JSON data."""
    return AgentState(
        messages=[],
        knowledge=file_content,
        json_data=json_data,
        currQuestion="",
        currAnswer="",
        cookie=[]
    )



def create_llm() -> ChatGoogleGenerativeAI:
    """Create and return a Google Generative AI model instance."""
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        max_output_tokens=1024,
        temperature=0.2,
        top_p=0.95,
        top_k=40,
        api_key="AIzaSyDNEAhvr11GQV0I13UeI0-Poqsyd1xpNQ4"
    )

    return model


def ask_question(state: AgentState) -> AgentState:
    """
    state: {
        'cookie': [{'user': '...', 'bot': '...'}, ...],  # conversation history
        'currQuestion': '...',
        'messages': [],  # persists between turns
        'llm': <Gemini or other LLM instance>
    }
    """

    SYSTEM_PROMPT = f"""
        You are YCTBot, the official AI assistant for Yaba College of Technology students.
        Your purpose is to answer questions based on the given Knowledge Base only.
        If the answer is not in the KB, say: "I don't have that information."
        Avoid unnecessary greetings and small talk unless the user greets you first.
        Do NOT repeat your role unless asked.
        knowledge: {state['knowledge']}
        json_data: {json.dumps(state['json_data'])}
    """

    if not state.get('messages'):
        state['messages'] = [HumanMessage(content=SYSTEM_PROMPT)]

    for turn in state.get('cookie', []):
        state['messages'].append(HumanMessage(content=turn['user']))
        if 'bot' in turn and turn['bot']:
            state['messages'].append(AIMessage(content=turn['bot']))


    state['messages'].append(HumanMessage(content=state['currQuestion']))

    response = state['llm'].invoke(state['messages'])

    bot_reply = response.content.strip()
    state['currAnswer'] = bot_reply
    state['messages'].append(AIMessage(content=bot_reply))
    state['cookie'][-1]['bot'] = bot_reply

    return state


def make_graph_and_compile(cookie:list):
    """Create nodes, add edges, compile the StateGraph, and run the flow."""
    graph = StateGraph(AgentState)
    graph.add_node("ask_question", ask_question)
    graph.add_edge("ask_question", END)
    graph.set_entry_point("ask_question")

    compiled_graph = graph.compile()

    state = create_agent_state()
    state["cookie"] = cookie
    state["llm"] = create_llm()

    state = compiled_graph.invoke(state)
    print(state["currAnswer"])
    return {
        'response' : state["currAnswer"],
        "cookie" : state["cookie"]
    }
