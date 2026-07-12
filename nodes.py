from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from app.core.config import settings
from app.agent.tools import tavily_search, rag_retrieve, execute_python, calculator
from app.agent.state import AgentState

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=settings.DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1",
    temperature=0
)

# 工具集合
tools = [tavily_search, rag_retrieve, execute_python, calculator]
tool_node = ToolNode(tools)


# 主 Agent 路由函数
def supervisor_agent(state: AgentState):
    system_prompt = """你是AI任务主管。根据用户问题类型，将任务分配给对应专家：
    - 如果问题涉及文档、知识库或技术概念，分配给 "RAG专家"
    - 如果问题需要实时信息、新闻、股票，分配给 "搜索专家"
    - 如果问题需要编程、数据分析，分配给 "代码专家"
    - 对于数学计算，直接使用计算器工具
    回答必须简洁，只输出分配结果。"""

    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": state["messages"][-1]["content"]}
    ])
    next_agent = response.content.strip()
    return {"next_agent": next_agent, "iteration": state.get("iteration", 0) + 1}


def rag_agent(state: AgentState):
    """RAG 专家节点"""
    query = state["messages"][-1]["content"]
    result = rag_retrieve.invoke({"query": query})
    return {
        "tool_results": [{"tool": "rag", "result": result}],
        "messages": [{"role": "assistant", "content": f"RAG检索结果: {result}"}]
    }


def search_agent(state: AgentState):
    """搜索专家节点"""
    query = state["messages"][-1]["content"]
    result = tavily_search.invoke({"query": query})
    return {
        "tool_results": [{"tool": "search", "result": result}],
        "messages": [{"role": "assistant", "content": f"搜索结果: {result}"}]
    }


def code_agent(state: AgentState):
    """代码专家节点"""
    query = state["messages"][-1]["content"]
    result = execute_python.invoke({"query": query})
    return {
        "tool_results": [{"tool": "code", "result": result}],
        "messages": [{"role": "assistant", "content": f"代码执行结果: {result}"}]
    }


def final_answer_node(state: AgentState):
    """汇总所有结果，生成最终答案"""
    context = "\n".join([r["result"] for r in state.get("tool_results", [])])
    prompt = f"""基于以下信息回答用户问题：
用户问题：{state['messages'][0]['content']}
工具结果：{context}
请给出简洁、准确的最终答案。"""
    response = llm.invoke(prompt)
    return {"final_answer": response.content}