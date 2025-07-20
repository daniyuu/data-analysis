# 1. 使用官方精简版 Python 镜像
FROM python:3.11.9-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 安装系统依赖（如有 C 扩展编译需求）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. 拷贝 requirements.txt 和本地已下载的 wheels
COPY requirements.txt .
COPY wheels/ ./wheels/

# 5. 从本地安装 Python 依赖，避免 PyPI 网络问题
RUN pip install --no-cache-dir --find-links=./wheels -r requirements.txt

# 6. 拷贝剩余代码
COPY . .

# 7. 暴露服务端口
EXPOSE 8000

# 8. 启动命令
CMD ["python", "server.py"]
