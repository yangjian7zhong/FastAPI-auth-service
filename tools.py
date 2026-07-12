from langchain.tools import tool
import httpx
from bs4 import BeautifulSoup
from app.core.config import settings

@tool
def tavily_search(query: str) -> str:
    """使用Tavily API进行网络搜索，获取最新实时信息"""
    if not settings.TAVILY_API_KEY:
        return "搜索功能未配置"
    try:
        import tavily
        client = tavily.TavilyClient(api_key=settings.TAVILY_API_KEY)
        result = client.search(query, max_results=3)
        return "\n".join([f"- {r['content']}" for r in result.get('results', [])])
    except Exception as e:
        return f"搜索失败: {e}"

@tool
def rag_retrieve(query: str) -> str:
    """从内部知识库检索文档片段（RAG）"""
    # 这里替换为你实际使用的 Chroma 或 Pgvector 检索代码
    # 现在演示用模拟数据
    return f"根据知识库检索，关于 '{query}' 的相关信息：\n- FastAPI 是一个现代 Web 框架...\n- RAG 可以显著提升回答质量..."

@tool
def execute_python(code: str) -> str:
    """安全执行 Python 代码（限时1秒，仅返回输出）"""
    import subprocess, tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
        f.write(code.encode())
        fname = f.name
    try:
        result = subprocess.run(["python", fname], capture_output=True, text=True, timeout=1)
        return result.stdout or result.stderr
    except subprocess.TimeoutExpired:
        return "代码执行超时"
    finally:
        os.unlink(fname)

@tool
def calculator(expression: str) -> str:
    """计算数学表达式（仅允许基础运算）"""
    try:
        allowed = {"+", "-", "*", "/", "(", ")", ".", " "}
        if not all(c in allowed or c.isdigit() for c in expression):
            return "表达式包含非法字符"
        return f"计算结果: {eval(expression)}"
    except Exception as e:
        return f"计算错误: {e}"