# 使用 Python 3.11.9 官方镜像
FROM python:3.11.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 暴露端口（Railway 会通过 $PORT 环境变量覆盖）
EXPOSE 8000

# 启动命令（使用环境变量 $PORT 或默认 8000）
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]