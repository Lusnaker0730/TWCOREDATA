@echo off
REM 台灣FHIR生成器 - Docker安全掃描腳本 (Windows版本)
REM Taiwan FHIR Generator - Docker Security Scan Script (Windows Version)

echo 🔍 開始Docker安全掃描 / Starting Docker Security Scan
echo ==================================================

REM 檢查Docker是否安裝
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker未安裝 / Docker is not installed
    exit /b 1
)

REM 映像名稱
set IMAGE_NAME=taiwan-fhir-generator
set SECURE_IMAGE_NAME=taiwan-fhir-generator-secure
set ULTRA_SECURE_IMAGE_NAME=taiwan-fhir-generator-ultra-secure
set DISTROLESS_IMAGE_NAME=taiwan-fhir-generator-distroless

echo 📦 建構Docker映像 / Building Docker images

REM 建構原始映像
echo 建構原始映像 / Building original image...
docker build -t %IMAGE_NAME%:latest .
if %errorlevel% neq 0 (
    echo ❌ 原始映像建構失敗
    exit /b 1
)

REM 建構安全映像
echo 建構安全映像 / Building secure image...
docker build -f Dockerfile.secure -t %SECURE_IMAGE_NAME%:latest .
if %errorlevel% neq 0 (
    echo ❌ 安全映像建構失敗
    exit /b 1
)

REM 建構超安全映像 (Alpine)
echo 建構超安全映像 / Building ultra-secure image...
docker build -f Dockerfile.ultra-secure -t %ULTRA_SECURE_IMAGE_NAME%:latest .
if %errorlevel% neq 0 (
    echo ❌ 超安全映像建構失敗
    exit /b 1
)

REM 建構Distroless映像
echo 建構Distroless映像 / Building distroless image...
docker build -f Dockerfile.distroless -t %DISTROLESS_IMAGE_NAME%:latest .
if %errorlevel% neq 0 (
    echo ❌ Distroless映像建構失敗
    exit /b 1
)

echo 🔍 執行安全掃描 / Running security scans

REM 檢查是否安裝了Trivy
trivy --version >nul 2>&1
if %errorlevel% equ 0 (
    echo 使用Trivy進行漏洞掃描...
    
    echo 掃描原始映像...
    trivy image --format table --output scan-original.txt %IMAGE_NAME%:latest
    
    echo 掃描安全映像...
    trivy image --format table --output scan-secure.txt %SECURE_IMAGE_NAME%:latest
    
    echo 掃描超安全映像...
    trivy image --format table --output scan-ultra-secure.txt %ULTRA_SECURE_IMAGE_NAME%:latest
    
    echo 掃描Distroless映像...
    trivy image --format table --output scan-distroless.txt %DISTROLESS_IMAGE_NAME%:latest
    
    echo ✅ Trivy掃描完成
) else (
    echo ⚠️  Trivy未安裝，跳過漏洞掃描
    echo 安裝Trivy: https://aquasecurity.github.io/trivy/
)

REM 映像大小比較
echo 📊 映像大小比較 / Image size comparison
for /f "tokens=*" %%i in ('docker images %IMAGE_NAME%:latest --format "{{.Size}}"') do set ORIGINAL_SIZE=%%i
for /f "tokens=*" %%i in ('docker images %SECURE_IMAGE_NAME%:latest --format "{{.Size}}"') do set SECURE_SIZE=%%i
for /f "tokens=*" %%i in ('docker images %ULTRA_SECURE_IMAGE_NAME%:latest --format "{{.Size}}"') do set ULTRA_SECURE_SIZE=%%i
for /f "tokens=*" %%i in ('docker images %DISTROLESS_IMAGE_NAME%:latest --format "{{.Size}}"') do set DISTROLESS_SIZE=%%i

echo 原始映像大小 / Original image size: %ORIGINAL_SIZE%
echo 安全映像大小 / Secure image size: %SECURE_SIZE%
echo 超安全映像大小 / Ultra-secure image size: %ULTRA_SECURE_SIZE%
echo Distroless映像大小 / Distroless image size: %DISTROLESS_SIZE%

REM 運行時測試
echo 🧪 運行時測試 / Runtime testing
echo 測試安全映像...

REM 啟動測試容器
docker run -d --name test-secure -p 5001:5000 %SECURE_IMAGE_NAME%:latest
if %errorlevel% neq 0 (
    echo ❌ 容器啟動失敗
    goto cleanup
)

REM 等待啟動
echo 等待容器啟動...
timeout /t 15 /nobreak >nul

REM 健康檢查
curl -f http://localhost:5001/api/info >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 容器健康檢查通過
) else (
    echo ❌ 容器健康檢查失敗
    docker logs test-secure
)

REM 檢查用戶
for /f "tokens=*" %%i in ('docker exec test-secure whoami 2^>nul') do set USER_INFO=%%i
if not "%USER_INFO%"=="root" (
    echo ✅ 運行在非root用戶: %USER_INFO%
) else (
    echo ❌ 運行在root用戶
)

:cleanup
REM 清理測試容器
docker stop test-secure >nul 2>&1
docker rm test-secure >nul 2>&1

echo.
echo 🎉 安全掃描完成 / Security scan completed
echo ==================================================
echo 掃描報告已保存到:
if exist scan-original.txt echo - scan-original.txt (原始映像掃描結果)
if exist scan-secure.txt echo - scan-secure.txt (安全映像掃描結果)
echo.
echo 建議使用最安全的映像進行部署:
echo.
echo 1. Distroless映像 (最安全):
echo docker run -d -p 5000:5000 %DISTROLESS_IMAGE_NAME%:latest
echo.
echo 2. 超安全Alpine映像:
echo docker run -d -p 5000:5000 %ULTRA_SECURE_IMAGE_NAME%:latest
echo.
echo 3. 標準安全映像:
echo docker run -d -p 5000:5000 %SECURE_IMAGE_NAME%:latest

pause
