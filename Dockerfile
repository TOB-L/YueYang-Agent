# 使用官方轻量级 Python 3.10 镜像作为基础
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量，防止 python 缓冲 stdout 和 stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_ENDPOINT=https://hf-mirror.com

# 安装系统依赖 (如有需要，例如编译 C 扩展)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 先复制依赖文件并安装，利用 Docker 缓存层机制加速后续构建
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制项目所有文件到工作目录
COPY . .

# 暴露 Streamlit 默认端口
EXPOSE 8501

# 启动 Streamlit 服务
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]