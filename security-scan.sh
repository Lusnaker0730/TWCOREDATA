#!/bin/bash

# 台灣FHIR生成器 - Docker安全掃描腳本
# Taiwan FHIR Generator - Docker Security Scan Script

set -e

echo "🔍 開始Docker安全掃描 / Starting Docker Security Scan"
echo "=================================================="

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 檢查Docker是否安裝
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker未安裝 / Docker is not installed${NC}"
    exit 1
fi

# 映像名稱
IMAGE_NAME="taiwan-fhir-generator"
SECURE_IMAGE_NAME="taiwan-fhir-generator-secure"

echo -e "${BLUE}📦 建構Docker映像 / Building Docker images${NC}"

# 建構原始映像
echo "建構原始映像 / Building original image..."
docker build -t $IMAGE_NAME:latest .

# 建構安全映像
echo "建構安全映像 / Building secure image..."
docker build -f Dockerfile.secure -t $SECURE_IMAGE_NAME:latest .

echo -e "${BLUE}🔍 執行安全掃描 / Running security scans${NC}"

# 函數：執行Trivy掃描
run_trivy_scan() {
    local image=$1
    local output_file=$2
    
    echo "掃描映像: $image"
    
    if command -v trivy &> /dev/null; then
        echo "使用Trivy進行漏洞掃描..."
        trivy image --format table --output $output_file $image
        
        # 檢查高風險漏洞
        HIGH_VULNS=$(trivy image --format json $image | jq '.Results[]?.Vulnerabilities[]? | select(.Severity=="HIGH") | .VulnerabilityID' | wc -l)
        CRITICAL_VULNS=$(trivy image --format json $image | jq '.Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL") | .VulnerabilityID' | wc -l)
        
        echo "高風險漏洞數量: $HIGH_VULNS"
        echo "嚴重漏洞數量: $CRITICAL_VULNS"
        
        if [ $CRITICAL_VULNS -gt 0 ]; then
            echo -e "${RED}⚠️  發現 $CRITICAL_VULNS 個嚴重漏洞${NC}"
        elif [ $HIGH_VULNS -gt 0 ]; then
            echo -e "${YELLOW}⚠️  發現 $HIGH_VULNS 個高風險漏洞${NC}"
        else
            echo -e "${GREEN}✅ 未發現高風險或嚴重漏洞${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Trivy未安裝，跳過漏洞掃描${NC}"
        echo "安裝Trivy: https://aquasecurity.github.io/trivy/"
    fi
}

# 函數：檢查Docker最佳實踐
check_docker_best_practices() {
    local dockerfile=$1
    echo "檢查Docker最佳實踐: $dockerfile"
    
    # 檢查是否使用非root用戶
    if grep -q "USER " $dockerfile; then
        echo -e "${GREEN}✅ 使用非root用戶${NC}"
    else
        echo -e "${RED}❌ 未使用非root用戶${NC}"
    fi
    
    # 檢查是否清理apt快取
    if grep -q "rm -rf /var/lib/apt/lists" $dockerfile; then
        echo -e "${GREEN}✅ 清理apt快取${NC}"
    else
        echo -e "${YELLOW}⚠️  未清理apt快取${NC}"
    fi
    
    # 檢查是否使用特定版本標籤
    if grep -q "FROM.*:.*-" $dockerfile; then
        echo -e "${GREEN}✅ 使用特定版本標籤${NC}"
    else
        echo -e "${YELLOW}⚠️  建議使用特定版本標籤${NC}"
    fi
}

# 掃描原始映像
echo -e "${BLUE}掃描原始映像 / Scanning original image${NC}"
run_trivy_scan $IMAGE_NAME:latest "scan-original.txt"
check_docker_best_practices "Dockerfile"

echo ""

# 掃描安全映像
echo -e "${BLUE}掃描安全映像 / Scanning secure image${NC}"
run_trivy_scan $SECURE_IMAGE_NAME:latest "scan-secure.txt"
check_docker_best_practices "Dockerfile.secure"

echo ""

# 映像大小比較
echo -e "${BLUE}📊 映像大小比較 / Image size comparison${NC}"
ORIGINAL_SIZE=$(docker images $IMAGE_NAME:latest --format "table {{.Size}}" | tail -n 1)
SECURE_SIZE=$(docker images $SECURE_IMAGE_NAME:latest --format "table {{.Size}}" | tail -n 1)

echo "原始映像大小 / Original image size: $ORIGINAL_SIZE"
echo "安全映像大小 / Secure image size: $SECURE_SIZE"

# 運行時測試
echo -e "${BLUE}🧪 運行時測試 / Runtime testing${NC}"

test_container() {
    local image=$1
    local container_name=$2
    
    echo "測試映像: $image"
    
    # 啟動容器
    docker run -d --name $container_name -p 5001:5000 $image
    
    # 等待啟動
    sleep 10
    
    # 健康檢查
    if curl -f http://localhost:5001/api/info > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 容器健康檢查通過${NC}"
    else
        echo -e "${RED}❌ 容器健康檢查失敗${NC}"
        docker logs $container_name
    fi
    
    # 檢查用戶
    USER_INFO=$(docker exec $container_name whoami 2>/dev/null || echo "unknown")
    if [ "$USER_INFO" != "root" ]; then
        echo -e "${GREEN}✅ 運行在非root用戶: $USER_INFO${NC}"
    else
        echo -e "${RED}❌ 運行在root用戶${NC}"
    fi
    
    # 清理
    docker stop $container_name > /dev/null 2>&1
    docker rm $container_name > /dev/null 2>&1
}

# 測試安全映像
test_container $SECURE_IMAGE_NAME:latest "test-secure"

echo ""
echo -e "${GREEN}🎉 安全掃描完成 / Security scan completed${NC}"
echo "=================================================="
echo "掃描報告已保存到:"
echo "- scan-original.txt (原始映像掃描結果)"
echo "- scan-secure.txt (安全映像掃描結果)"
echo ""
echo "建議使用安全映像進行部署:"
echo "docker run -d -p 5000:5000 $SECURE_IMAGE_NAME:latest"
