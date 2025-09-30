# 部署指南 / Deployment Guide

本文檔說明如何在不同環境中部署台灣FHIR病人資料生成器。
This document explains how to deploy the Taiwan FHIR Patient Data Generator in different environments.

## 🚀 快速開始 / Quick Start

### 本地開發 / Local Development

```bash
# 克隆專案 / Clone repository
git clone https://github.com/your-username/taiwan-fhir-generator.git
cd taiwan-fhir-generator

# 安裝依賴 / Install dependencies
pip install -r requirements.txt

# 啟動應用程式 / Start application
python run.py
```

訪問 http://localhost:5000

## 🐳 Docker 部署 / Docker Deployment

### 使用 Docker / Using Docker

```bash
# 建構映像 / Build image
docker build -t taiwan-fhir-generator .

# 運行容器 / Run container
docker run -d \
  --name taiwan-fhir-generator \
  -p 5000:5000 \
  -v $(pwd)/output:/app/output \
  taiwan-fhir-generator
```

### 使用 Docker Compose / Using Docker Compose

```bash
# 啟動服務 / Start services
docker-compose up -d

# 查看日誌 / View logs
docker-compose logs -f

# 停止服務 / Stop services
docker-compose down
```

## ☁️ 雲端部署 / Cloud Deployment

### Heroku

1. **準備 Heroku 應用程式 / Prepare Heroku App**
```bash
# 安裝 Heroku CLI
# Install Heroku CLI

# 登入 Heroku / Login to Heroku
heroku login

# 創建應用程式 / Create app
heroku create your-app-name
```

2. **創建 Procfile**
```bash
echo "web: python run.py --host 0.0.0.0 --port \$PORT" > Procfile
```

3. **部署 / Deploy**
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### AWS EC2

1. **啟動 EC2 實例 / Launch EC2 Instance**
   - 選擇 Ubuntu 20.04 LTS
   - 配置安全群組開放 80, 443, 5000 埠

2. **安裝依賴 / Install Dependencies**
```bash
# 更新系統 / Update system
sudo apt update && sudo apt upgrade -y

# 安裝 Python 和 pip / Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# 安裝 Git / Install Git
sudo apt install git -y

# 安裝 Nginx (可選) / Install Nginx (optional)
sudo apt install nginx -y
```

3. **部署應用程式 / Deploy Application**
```bash
# 克隆專案 / Clone project
git clone https://github.com/your-username/taiwan-fhir-generator.git
cd taiwan-fhir-generator

# 創建虛擬環境 / Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 安裝依賴 / Install dependencies
pip install -r requirements.txt

# 使用 systemd 管理服務 / Manage service with systemd
sudo cp deployment/taiwan-fhir.service /etc/systemd/system/
sudo systemctl enable taiwan-fhir
sudo systemctl start taiwan-fhir
```

### Google Cloud Platform (GCP)

1. **使用 App Engine / Using App Engine**

創建 `app.yaml`:
```yaml
runtime: python39

env_variables:
  FLASK_ENV: production

automatic_scaling:
  min_instances: 1
  max_instances: 10
```

部署 / Deploy:
```bash
gcloud app deploy
```

2. **使用 Cloud Run / Using Cloud Run**
```bash
# 建構並推送映像 / Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/taiwan-fhir-generator

# 部署到 Cloud Run / Deploy to Cloud Run
gcloud run deploy --image gcr.io/PROJECT_ID/taiwan-fhir-generator --platform managed
```

### Azure App Service

1. **創建 Web App / Create Web App**
```bash
# 創建資源群組 / Create resource group
az group create --name taiwan-fhir-rg --location eastus

# 創建 App Service 計劃 / Create App Service plan
az appservice plan create --name taiwan-fhir-plan --resource-group taiwan-fhir-rg --sku B1 --is-linux

# 創建 Web App / Create Web App
az webapp create --resource-group taiwan-fhir-rg --plan taiwan-fhir-plan --name your-app-name --runtime "PYTHON|3.9"
```

2. **部署程式碼 / Deploy Code**
```bash
# 配置部署 / Configure deployment
az webapp deployment source config --name your-app-name --resource-group taiwan-fhir-rg --repo-url https://github.com/your-username/taiwan-fhir-generator --branch main --manual-integration
```

## 🔧 環境配置 / Environment Configuration

### 環境變數 / Environment Variables

```bash
# Flask 配置 / Flask Configuration
export FLASK_ENV=production
export FLASK_DEBUG=False

# 應用程式配置 / Application Configuration
export HOST=0.0.0.0
export PORT=5000

# 資料庫配置 (如果使用) / Database Configuration (if used)
export DATABASE_URL=your_database_url

# 安全配置 / Security Configuration
export SECRET_KEY=your_secret_key
```

### Nginx 配置 / Nginx Configuration

創建 `/etc/nginx/sites-available/taiwan-fhir`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 靜態檔案 / Static files
    location /static {
        alias /path/to/taiwan-fhir-generator/static;
        expires 30d;
    }
}
```

啟用站點 / Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/taiwan-fhir /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL 配置 / SSL Configuration

使用 Let's Encrypt:
```bash
# 安裝 Certbot / Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# 獲取 SSL 證書 / Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# 自動續期 / Auto renewal
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 監控和日誌 / Monitoring and Logging

### 系統監控 / System Monitoring

1. **使用 systemd 日誌 / Using systemd logs**
```bash
# 查看服務狀態 / Check service status
sudo systemctl status taiwan-fhir

# 查看日誌 / View logs
sudo journalctl -u taiwan-fhir -f
```

2. **使用 htop 監控資源 / Monitor resources with htop**
```bash
sudo apt install htop -y
htop
```

### 應用程式監控 / Application Monitoring

1. **健康檢查端點 / Health check endpoint**
```bash
curl http://your-domain.com/health
```

2. **日誌配置 / Logging configuration**

在 `app.py` 中添加:
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/taiwan-fhir.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

## 🔒 安全性考量 / Security Considerations

### 基本安全措施 / Basic Security Measures

1. **更新系統 / Update System**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **配置防火牆 / Configure Firewall**
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
```

3. **限制檔案權限 / Restrict File Permissions**
```bash
chmod 600 config/*.json
chmod 755 *.py
```

4. **使用環境變數存儲敏感資訊 / Use Environment Variables for Sensitive Data**
```bash
# 不要在程式碼中硬編碼敏感資訊
# Don't hardcode sensitive information in code
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex())')
```

## 🚨 故障排除 / Troubleshooting

### 常見問題 / Common Issues

1. **埠號衝突 / Port Conflict**
```bash
# 檢查埠號使用情況 / Check port usage
sudo netstat -tlnp | grep :5000

# 終止程序 / Kill process
sudo kill -9 PID
```

2. **權限問題 / Permission Issues**
```bash
# 檢查檔案權限 / Check file permissions
ls -la

# 修改權限 / Change permissions
chmod +x run.py
```

3. **依賴問題 / Dependency Issues**
```bash
# 重新安裝依賴 / Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

4. **記憶體不足 / Out of Memory**
```bash
# 檢查記憶體使用 / Check memory usage
free -h

# 增加 swap 空間 / Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📈 效能優化 / Performance Optimization

### 應用程式層級 / Application Level

1. **使用 Gunicorn / Using Gunicorn**
```bash
pip install gunicorn
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

2. **啟用快取 / Enable Caching**
```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
```

### 系統層級 / System Level

1. **調整系統參數 / Tune System Parameters**
```bash
# 增加檔案描述符限制 / Increase file descriptor limit
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf
```

2. **使用 Redis 快取 / Use Redis Cache**
```bash
sudo apt install redis-server -y
pip install redis flask-caching
```

---

如有部署相關問題，請參考 [故障排除指南](TROUBLESHOOTING.md) 或提交 [Issue](https://github.com/your-username/taiwan-fhir-generator/issues)。

For deployment-related issues, please refer to the [Troubleshooting Guide](TROUBLESHOOTING.md) or submit an [Issue](https://github.com/your-username/taiwan-fhir-generator/issues).
