import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
import httpx
from app.core.config import settings  # 确保能从 .env 读取 SILICONFLOW_API_KEY

# 1. 自定义嵌入函数类（SiliconFlow 专用）
class SiliconFlowEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key: str, model_name: str = "BAAI/bge-large-zh-v1.5"):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = "https://api.siliconflow.cn/v1/embeddings"

    def __call__(self, input: Documents) -> Embeddings:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "input": list(input)
        }
        with httpx.Client() as client:
            response = client.post(self.base_url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]

# 2. 初始化 ChromaDB（使用自定义嵌入函数）
siliconflow_ef = SiliconFlowEmbeddingFunction(api_key=settings.SILICONFLOW_API_KEY)

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="knowledge_base",
    embedding_function=siliconflow_ef
)

# 3. 工具函数
def add_documents(ids: list, documents: list, metadatas: list = None):
    """添加文档到向量库"""
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas or [{}] * len(documents)
    )

def query_documents(query: str, n_results: int = 3) -> list:
    """检索最相似的文档"""
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results["documents"][0] if results["documents"] else []