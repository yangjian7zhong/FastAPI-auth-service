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

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/huggingface

COPY requirements.txt .

RUN pip install --root-user-action=ignore --upgrade pip setuptools wheel packaging

# Railway 没有 GPU：强制安装 CPU 版 PyTorch，避免下载 nvidia_* CUDA 依赖。
RUN pip install --root-user-action=ignore \
    --index-url https://download.pytorch.org/whl/cpu \
    torch==2.2.2+cpu

RUN pip install --root-user-action=ignore \
    -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 在构建期下载模型，避免每次容器启动时重新下载。
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-MiniLM-L3-v2')"

COPY . .

# 必须通过 sh -c 展开 Railway 自动注入的 PORT。
CMD ["sh", "-c", "streamlit run streamlit_app.py --server.port ${PORT:-8501} --server.address 0.0.0.0"]
