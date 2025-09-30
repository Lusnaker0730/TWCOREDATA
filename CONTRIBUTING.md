# 貢獻指南 / Contributing Guide

感謝您對台灣FHIR病人資料生成器的興趣！我們歡迎各種形式的貢獻。

Thank you for your interest in the Taiwan FHIR Patient Data Generator! We welcome contributions of all kinds.

## 🤝 如何貢獻 / How to Contribute

### 🐛 回報問題 / Reporting Issues

如果您發現了bug或有功能建議，請：
If you find a bug or have a feature suggestion, please:

1. 檢查[現有的Issues](https://github.com/your-username/taiwan-fhir-generator/issues)確認問題尚未被回報
   Check [existing issues](https://github.com/your-username/taiwan-fhir-generator/issues) to ensure the issue hasn't been reported

2. 創建新的Issue，包含：
   Create a new issue with:
   - 清楚的標題和描述 / Clear title and description
   - 重現步驟 / Steps to reproduce
   - 預期行為 / Expected behavior
   - 實際行為 / Actual behavior
   - 螢幕截圖（如適用）/ Screenshots (if applicable)
   - 環境資訊（作業系統、Python版本等）/ Environment info (OS, Python version, etc.)

### 💻 程式碼貢獻 / Code Contributions

#### 設置開發環境 / Setting up Development Environment

1. **Fork並克隆專案 / Fork and clone the repository**
```bash
git clone https://github.com/your-username/taiwan-fhir-generator.git
cd taiwan-fhir-generator
```

2. **創建虛擬環境 / Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 / or
venv\Scripts\activate     # Windows
```

3. **安裝依賴 / Install dependencies**
```bash
pip install -r requirements.txt
```

4. **創建功能分支 / Create feature branch**
```bash
git checkout -b feature/your-feature-name
```

#### 開發指南 / Development Guidelines

##### 📝 程式碼風格 / Code Style

- 使用Python PEP 8風格指南
  Follow Python PEP 8 style guide
- 函數和變數使用snake_case
  Use snake_case for functions and variables
- 類別使用PascalCase
  Use PascalCase for classes
- 常數使用UPPER_CASE
  Use UPPER_CASE for constants

##### 📋 程式碼結構 / Code Structure

- 保持函數簡潔，單一職責
  Keep functions concise with single responsibility
- 添加適當的註釋和文檔字串
  Add appropriate comments and docstrings
- 使用有意義的變數名稱
  Use meaningful variable names

##### 🧪 測試 / Testing

- 為新功能添加測試
  Add tests for new features
- 確保所有測試通過
  Ensure all tests pass
- 測試覆蓋率應保持在80%以上
  Test coverage should be above 80%

```bash
# 運行測試 / Run tests
python -m pytest

# 檢查覆蓋率 / Check coverage
python -m pytest --cov=.
```

#### 提交變更 / Submitting Changes

1. **確保程式碼品質 / Ensure code quality**
```bash
# 檢查語法 / Check syntax
python -m flake8 .

# 格式化程式碼 / Format code
python -m black .
```

2. **提交變更 / Commit changes**
```bash
git add .
git commit -m "feat: add new feature description"
```

3. **推送到您的Fork / Push to your fork**
```bash
git push origin feature/your-feature-name
```

4. **創建Pull Request / Create Pull Request**
   - 提供清楚的標題和描述
     Provide clear title and description
   - 說明變更的原因和影響
     Explain the reason and impact of changes
   - 連結相關的Issues
     Link related issues

### 📚 文檔貢獻 / Documentation Contributions

我們也歡迎文檔改進：
We also welcome documentation improvements:

- 修正錯字或語法錯誤
  Fix typos or grammar errors
- 改善說明的清晰度
  Improve clarity of explanations
- 添加範例或教學
  Add examples or tutorials
- 翻譯文檔
  Translate documentation

### 🔧 配置檔案貢獻 / Configuration File Contributions

如果您想添加新的醫療代碼或改善現有配置：
If you want to add new medical codes or improve existing configurations:

#### 疾病配置 / Condition Configuration
```json
{
  "code": "SNOMED_CT_CODE",
  "display": "疾病名稱",
  "system": "http://snomed.info/sct",
  "category": "疾病類別"
}
```

#### 觀察項目配置 / Observation Configuration
```json
{
  "code": "LOINC_CODE",
  "display": "觀察項目名稱",
  "unit": "單位",
  "ucum_code": "UCUM代碼",
  "min_val": 最小值,
  "max_val": 最大值,
  "category": "觀察類別"
}
```

#### 藥物配置 / Medication Configuration
```json
{
  "code": "RXNORM_CODE",
  "display": "藥物名稱",
  "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
  "atc": "ATC代碼",
  "category": "藥物類別",
  "dosage_form": "劑型",
  "strength": "劑量"
}
```

## 📋 提交訊息格式 / Commit Message Format

使用以下格式：
Use the following format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### 類型 / Types:
- `feat`: 新功能 / New feature
- `fix`: 錯誤修復 / Bug fix
- `docs`: 文檔變更 / Documentation changes
- `style`: 格式變更 / Formatting changes
- `refactor`: 重構 / Code refactoring
- `test`: 測試相關 / Test related
- `chore`: 維護任務 / Maintenance tasks

### 範例 / Examples:
```
feat(ui): add custom patient generation interface
fix(generator): resolve duplicate condition generation
docs(readme): update installation instructions
```

## 🎯 開發優先順序 / Development Priorities

目前我們特別歡迎以下類型的貢獻：
We especially welcome contributions in the following areas:

1. **🏥 醫療代碼擴充 / Medical Code Expansion**
   - 添加更多SNOMED CT疾病代碼
   - 擴充LOINC觀察項目
   - 增加RxNorm藥物代碼

2. **🌐 國際化 / Internationalization**
   - 英文界面翻譯
   - 多語言支援

3. **🧪 測試覆蓋 / Test Coverage**
   - 單元測試
   - 整合測試
   - 端到端測試

4. **📊 資料驗證 / Data Validation**
   - FHIR資源驗證
   - 醫療代碼驗證

5. **🚀 效能優化 / Performance Optimization**
   - 大量資料生成優化
   - 記憶體使用優化

## 📞 聯絡方式 / Contact

如有任何問題，請透過以下方式聯絡：
If you have any questions, please contact us via:

- 📧 Email: your-email@example.com
- 💬 [GitHub Discussions](https://github.com/your-username/taiwan-fhir-generator/discussions)
- 🐛 [GitHub Issues](https://github.com/your-username/taiwan-fhir-generator/issues)

## 📜 行為準則 / Code of Conduct

請遵守我們的[行為準則](CODE_OF_CONDUCT.md)，確保友善和包容的社群環境。
Please follow our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a friendly and inclusive community environment.

---

再次感謝您的貢獻！🙏
Thank you again for your contributions! 🙏
