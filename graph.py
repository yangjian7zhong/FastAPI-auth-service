from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import supervisor_agent, rag_agent, search_agent, code_agent, final_answer_node, tool_node

builder = StateGraph(AgentState)

# 添加节点
builder.add_node("supervisor", supervisor_agent)
builder.add_node("rag_agent", rag_agent)
builder.add_node("search_agent", search_agent)
builder.add_node("code_agent", code_agent)
builder.add_node("final_answer", final_answer_node)

# 设置入口
builder.set_entry_point("supervisor")

# 条件路由：根据 supervisor 的决策分配
def route_after_supervisor(state):
    next_agent = state["next_agent"]
    if "RAG" in next_agent:
        return "rag_agent"
    elif "搜索" in next_agent:
        return "search_agent"
    elif "代码" in next_agent:
        return "code_agent"
    else:
        return "final_answer"

builder.add_conditional_edges("supervisor", route_after_supervisor, {
    "rag_agent": "rag_agent",
    "search_agent": "search_agent",
    "code_agent": "code_agent",
    "final_answer": "final_answer"
})

# 所有专家节点执行后回到 supervisor 或进入 final_answer
builder.add_edge("rag_agent", "supervisor")
builder.add_edge("search_agent", "supervisor")
builder.add_edge("code_agent", "supervisor")
builder.add_edge("final_answer", END)

# 编译
graph = builder.compile()