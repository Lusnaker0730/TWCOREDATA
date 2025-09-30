# 使用官方Python運行時作為基礎映像
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 設定環境變數
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安裝系統依賴
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 複製requirements文件並安裝Python依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案文件
COPY . .

# 創建輸出目錄
RUN mkdir -p output/complete_patients_fixed output/custom_patients

# 暴露埠號
EXPOSE 5000

# 設定健康檢查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# 啟動應用程式
CMD ["python", "run.py", "--host", "0.0.0.0", "--port", "5000"]
