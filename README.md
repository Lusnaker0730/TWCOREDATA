# 台灣 FHIR 病人資料生成器

一個功能完整的台灣FHIR (Fast Healthcare Interoperability Resources) 病人資料生成器，支援批量生成和自定義單一病人資料生成，並可直接上傳到FHIR伺服器。

## 🌟 主要功能

### 📊 批量生成模式
- 批量生成多個病人的完整醫療資料
- 支援自定義每個病人的疾病、觀察項目和藥物數量
- 可設定數量為0以跳過特定類型的資料生成
- 即時進度顯示和統計資訊

### 🎯 自定義單一病人生成模式
- 精確選擇特定的疾病、觀察項目和藥物
- 支援三種選擇方式：
  - 瀏覽並選擇特定項目
  - 搜尋並選擇項目  
  - 使用代碼直接指定
- 統一的項目總結區域，用顏色區分不同類型
- 結果即時顯示在頁面頂部

### 🏥 FHIR 資源支援
- **Patient** - 病人基本資料（台灣身分證、健保卡號）
- **Condition** - 疾病診斷（使用SNOMED CT代碼）
- **Observation** - 觀察項目（使用LOINC代碼）
- **Medication** - 藥物資訊（使用RxNorm代碼）
- **MedicationRequest** - 處方資訊

### 🚀 伺服器上傳
- 支援台灣TWCORE伺服器
- 支援國際HAPI FHIR伺服器
- 支援自訂FHIR伺服器
- 上傳結果即時回饋

## 🛠️ 技術特色

### 📋 配置檔案管理
- 疾病、觀察項目、藥物資料分離至獨立JSON配置檔案
- 易於維護和更新醫療代碼
- 支援類別分類和搜尋功能

### 🎨 現代化Web UI
- 響應式設計，支援各種螢幕尺寸
- 美觀的漸變色彩和動畫效果
- 直觀的選項卡式界面
- 即時搜尋和篩選功能

### ⚡ 非同步處理
- 背景執行緒處理資料生成，避免網頁超時
- 即時進度更新和狀態顯示
- 優雅的錯誤處理和使用者回饋

## 📦 安裝與使用

### 環境需求
- Python 3.7+
- Flask 2.0+
- requests
- pathlib

### 安裝步驟

1. **克隆專案**
```bash
git clone https://github.com/your-username/taiwan-fhir-generator.git
cd taiwan-fhir-generator
```

2. **安裝依賴**
```bash
pip install -r requirements.txt
```

3. **啟動應用程式**
```bash
python app.py
```

4. **開啟瀏覽器**
```
http://localhost:5000
```

### 命令列使用

也可以直接使用命令列模式：

```bash
python generate_TW_patients.py
```

## 📁 專案結構

```
taiwan-fhir-generator/
├── app.py                          # Flask Web應用程式
├── generate_TW_patients.py         # 核心FHIR資料生成器
├── config_loader.py                # 配置檔案載入器
├── requirements.txt                # Python依賴套件
├── README.md                       # 專案說明文件
├── config/                         # 配置檔案目錄
│   ├── conditions.json             # 疾病診斷配置
│   ├── observations.json           # 觀察項目配置
│   └── medications.json            # 藥物配置
├── templates/                      # HTML模板
│   ├── index.html                  # 批量生成頁面
│   └── custom.html                 # 自定義生成頁面
├── output/                         # 輸出檔案目錄
│   ├── complete_patients_fixed/    # 批量生成結果
│   └── custom_patients/            # 自定義生成結果
└── static/                         # 靜態資源（如有需要）
```

## 🎯 使用指南

### 批量生成模式

1. 在首頁選擇要生成的病人數量
2. 設定每個病人的疾病、觀察項目、藥物數量
3. 選擇是否上傳到FHIR伺服器
4. 點擊"開始生成"按鈕
5. 查看生成進度和結果統計

### 自定義生成模式

1. 點擊"自定義單一病人生成"按鈕
2. 在不同選項卡中選擇所需的項目：
   - **疾病診斷**：選擇特定疾病
   - **觀察項目**：選擇檢驗項目
   - **藥物處方**：選擇藥物
3. 在頂部總結區域查看已選擇的項目
4. 設定上傳選項（可選）
5. 點擊"生成病人資料"按鈕
6. 在頂部查看生成結果

## 📊 支援的醫療代碼標準

- **SNOMED CT** - 疾病診斷分類
- **LOINC** - 實驗室和臨床觀察
- **RxNorm** - 藥物標準化命名
- **UCUM** - 測量單位統一代碼
- **ATC** - 解剖學治療學化學分類系統

## 🔧 配置檔案說明

### 疾病配置 (config/conditions.json)
```json
[
  {
    "code": "38341003",
    "display": "高血壓",
    "system": "http://snomed.info/sct",
    "category": "心血管疾病"
  }
]
```

### 觀察項目配置 (config/observations.json)
```json
[
  {
    "code": "8480-6",
    "display": "收縮壓",
    "unit": "mmHg",
    "ucum_code": "mm[Hg]",
    "min_val": 90,
    "max_val": 180,
    "category": "生命徵象"
  }
]
```

### 藥物配置 (config/medications.json)
```json
[
  {
    "code": "316049",
    "display": "Lisinopril",
    "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
    "atc": "C09AA03",
    "category": "心血管用藥",
    "dosage_form": "tablet",
    "strength": "10mg"
  }
]
```

## 🚀 部署說明

### 本地部署
```bash
python app.py
```

### Docker部署
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

### 雲端部署
支援部署到各大雲端平台：
- Heroku
- AWS EC2
- Google Cloud Platform
- Azure App Service

## 🤝 貢獻指南

歡迎提交Issue和Pull Request！

1. Fork此專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟Pull Request

## 📝 更新日誌

### v2.0.0 (最新版本)
- ✨ 新增自定義單一病人生成功能
- 🎨 全新的Web UI設計
- 📋 配置檔案模組化
- 🚀 結果即時顯示在頁面頂部
- 🔍 支援搜尋和篩選功能

### v1.0.0
- 🎉 初始版本發布
- 📊 批量生成FHIR資料
- 🏥 支援多種FHIR伺服器上傳
- 🌐 Web UI界面

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 📞 聯絡資訊

如有問題或建議，請透過以下方式聯絡：

- 📧 Email: your-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/taiwan-fhir-generator/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-username/taiwan-fhir-generator/discussions)

## 🙏 致謝

感謝以下專案和組織的支持：
- [FHIR Taiwan](https://twcore.hapi.fhir.tw/) - 台灣FHIR標準推廣
- [HL7 FHIR](https://www.hl7.org/fhir/) - FHIR標準制定
- [SNOMED International](https://www.snomed.org/) - SNOMED CT代碼系統
- [Regenstrief Institute](https://loinc.org/) - LOINC代碼系統

---

⭐ 如果這個專案對您有幫助，請給我們一個星星！