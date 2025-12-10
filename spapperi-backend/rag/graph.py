from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import node_manager, node_analyst

# Workflow Definition
workflow = StateGraph(AgentState)

# Nodes
workflow.add_node("analyst", node_analyst)
workflow.add_node("manager", node_manager)

# Edges
workflow.set_entry_point("analyst")
workflow.add_edge("analyst", "manager")
workflow.add_edge("manager", END)

app = workflow.compile()
