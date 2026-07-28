#FROM python:3.11-slim
#WORKDIR /app
#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
#COPY . .
#CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]







#FROM python:3.11-slim
#WORKDIR /app
#COPY requirements.txt .
#RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
#COPY . .
#CMD ["sh", "-c", "python -c \"from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-MiniLM-L3-v2')\" && uvicorn main:app --host 0.0.0.0 --port 8000"]




FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
# 所有 pip install 都加上 --root-user-action=ignore
RUN pip install --root-user-action=ignore --upgrade pip setuptools wheel packaging
RUN pip install --root-user-action=ignore -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# 预下载模型（保持不变）
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-MiniLM-L3-v2')"
COPY . .
# 启动 Streamlit（注意使用 $PORT 环境变量）
CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8000", "--server.address", "0.0.0.0"]