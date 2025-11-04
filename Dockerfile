# 台灣 FHIR 病人資料生成器 - 標準 Docker 映像
# Taiwan FHIR Patient Data Generator - Standard Docker Image

FROM python:3.11-slim-bookworm

# 設定標籤
LABEL maintainer="Taiwan FHIR Generator Team" \
      version="2.2.0" \
      description="Taiwan FHIR Patient Data Generator"

# 設定環境變數
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random

# 安裝系統依賴
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 複製requirements並安裝Python依賴
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# 複製應用程式文件
COPY app.py generate_TW_patients.py config_loader.py run.py ./
COPY config/ ./config/
COPY templates/ ./templates/

# 創建輸出目錄
RUN mkdir -p /app/output/complete_patients_fixed \
             /app/output/custom_patients \
             /app/logs

# 創建非root用戶
RUN useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /app

# 切換到非root用戶
USER appuser

# 暴露埠號
EXPOSE 5000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# 啟動應用程式
CMD ["python", "run.py", "--host", "0.0.0.0", "--port", "5000"]

