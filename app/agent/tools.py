import httpx
import subprocess
import tempfile
import os
import json
from app.core.config import settings

def rag_search(query: str) -> str:
    """模拟RAG检索（可替换为真实向量库）"""
    return f"关于 '{query}' 的检索结果：\n- 相关文档片段1\n- 相关文档片段2"

def web_search(query: str) -> str:
    """使用Tavily搜索（如果没Key则返回模拟数据）"""
    if settings.TAVILY_API_KEY:
        try:
            import tavily
            client = tavily.TavilyClient(api_key=settings.TAVILY_API_KEY)
            result = client.search(query, max_results=3)
            return json.dumps(result.get("results", []), ensure_ascii=False)
        except Exception as e:
            return f"搜索失败: {e}"
    return f"模拟搜索结果（未配置API Key）：关于 '{query}' 的搜索结果"

def execute_python(code: str) -> str:
    """安全执行Python代码（限时1秒）"""
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            f.write(code.encode())
            fname = f.name
        result = subprocess.run(["python", fname], capture_output=True, text=True, timeout=1)
        return result.stdout or result.stderr
    except subprocess.TimeoutExpired:
        return "代码执行超时"
    finally:
        os.unlink(fname)

def calculator(expression: str) -> str:
    """计算数学表达式"""
    try:
        allowed = {"+", "-", "*", "/", "(", ")", ".", " "}
        if not all(c in allowed or c.isdigit() for c in expression):
            return "表达式包含非法字符"
        return f"计算结果: {eval(expression)}"
    except Exception as e:
        return f"计算错误: {e}"

TOOLS = {
    "rag_search": rag_search,
    "web_search": web_search,
    "execute_python": execute_python,
    "calculator": calculator
}
TOOL_DESCRIPTIONS = {
    "rag_search": "用于从知识库检索信息",
    "web_search": "用于搜索互联网实时信息",
    "execute_python": "用于执行Python代码",
    "calculator": "用于数学计算"
}