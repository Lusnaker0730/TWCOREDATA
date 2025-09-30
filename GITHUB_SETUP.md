# GitHub 上傳指南 / GitHub Upload Guide

本指南將協助您將台灣FHIR病人資料生成器上傳到GitHub。
This guide will help you upload the Taiwan FHIR Patient Data Generator to GitHub.

## 📋 準備工作 / Prerequisites

### 1. 安裝 Git / Install Git

**Windows:**
- 下載並安裝 [Git for Windows](https://git-scm.com/download/win)
- 或使用 Chocolatey: `choco install git`

**macOS:**
- 使用 Homebrew: `brew install git`
- 或下載 [Git for macOS](https://git-scm.com/download/mac)

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install git -y
```

### 2. 配置 Git / Configure Git

```bash
# 設定用戶名 / Set username
git config --global user.name "Your Name"

# 設定電子郵件 / Set email
git config --global user.email "your.email@example.com"

# 驗證配置 / Verify configuration
git config --list
```

### 3. 創建 GitHub 帳戶 / Create GitHub Account

如果您還沒有GitHub帳戶，請到 [github.com](https://github.com) 註冊。
If you don't have a GitHub account yet, sign up at [github.com](https://github.com).

## 🚀 上傳步驟 / Upload Steps

### 步驟 1: 創建 GitHub Repository / Step 1: Create GitHub Repository

1. 登入 GitHub
2. 點擊右上角的 "+" 按鈕
3. 選擇 "New repository"
4. 填寫以下資訊：
   - **Repository name**: `taiwan-fhir-generator` (或您喜歡的名稱)
   - **Description**: `台灣 FHIR 病人資料生成器 - Taiwan FHIR Patient Data Generator`
   - **Visibility**: 選擇 Public 或 Private
   - **不要** 勾選 "Initialize this repository with a README"
5. 點擊 "Create repository"

### 步驟 2: 初始化本地 Git Repository / Step 2: Initialize Local Git Repository

在您的專案目錄中執行：
Run in your project directory:

```bash
# 初始化 Git repository / Initialize Git repository
git init

# 添加所有檔案 / Add all files
git add .

# 檢查狀態 / Check status
git status

# 提交初始版本 / Commit initial version
git commit -m "Initial commit: Taiwan FHIR Patient Data Generator"
```

### 步驟 3: 連接到 GitHub Repository / Step 3: Connect to GitHub Repository

```bash
# 添加遠端 repository / Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/taiwan-fhir-generator.git

# 驗證遠端連接 / Verify remote connection
git remote -v

# 推送到 GitHub / Push to GitHub
git branch -M main
git push -u origin main
```

**注意**: 將 `YOUR_USERNAME` 替換為您的 GitHub 用戶名
**Note**: Replace `YOUR_USERNAME` with your GitHub username

### 步驟 4: 驗證上傳 / Step 4: Verify Upload

1. 回到您的 GitHub repository 頁面
2. 重新整理頁面
3. 確認所有檔案都已上傳

## 🔐 使用 SSH 金鑰 (推薦) / Using SSH Keys (Recommended)

### 生成 SSH 金鑰 / Generate SSH Key

```bash
# 生成新的 SSH 金鑰 / Generate new SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# 啟動 ssh-agent / Start ssh-agent
eval "$(ssh-agent -s)"

# 添加 SSH 金鑰到 ssh-agent / Add SSH key to ssh-agent
ssh-add ~/.ssh/id_ed25519
```

### 添加 SSH 金鑰到 GitHub / Add SSH Key to GitHub

1. 複製公鑰內容 / Copy public key content:
```bash
# Linux/macOS
cat ~/.ssh/id_ed25519.pub

# Windows (Git Bash)
clip < ~/.ssh/id_ed25519.pub
```

2. 在 GitHub 中：
   - 進入 Settings → SSH and GPG keys
   - 點擊 "New SSH key"
   - 貼上公鑰內容
   - 點擊 "Add SSH key"

3. 測試連接 / Test connection:
```bash
ssh -T git@github.com
```

4. 更新遠端 URL / Update remote URL:
```bash
git remote set-url origin git@github.com:YOUR_USERNAME/taiwan-fhir-generator.git
```

## 📝 建議的 Repository 設定 / Recommended Repository Settings

### 1. 設定 Repository Description / Set Repository Description

在 GitHub repository 頁面：
1. 點擊設定圖示 (齒輪)
2. 添加描述: "台灣 FHIR 病人資料生成器 - 支援批量生成和自定義單一病人資料生成，並可直接上傳到FHIR伺服器"
3. 添加網站 URL (如果有部署)
4. 添加主題標籤: `fhir`, `healthcare`, `taiwan`, `python`, `flask`, `medical-data`

### 2. 啟用 GitHub Pages (可選) / Enable GitHub Pages (Optional)

如果您想要展示專案文檔：
1. 進入 Settings → Pages
2. 選擇 Source: "Deploy from a branch"
3. 選擇 Branch: "main"
4. 選擇 Folder: "/ (root)"

### 3. 設定 Branch Protection / Set up Branch Protection

1. 進入 Settings → Branches
2. 點擊 "Add rule"
3. Branch name pattern: `main`
4. 勾選:
   - "Require a pull request before merging"
   - "Require status checks to pass before merging"
   - "Require branches to be up to date before merging"

### 4. 設定 Issue Templates / Set up Issue Templates

創建 `.github/ISSUE_TEMPLATE/` 目錄並添加模板：

**Bug Report Template** (`.github/ISSUE_TEMPLATE/bug_report.md`):
```markdown
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. Windows 10]
 - Python Version: [e.g. 3.9]
 - Browser: [e.g. chrome, safari]

**Additional context**
Add any other context about the problem here.
```

## 🔄 日常維護 / Daily Maintenance

### 更新 Repository / Update Repository

```bash
# 檢查狀態 / Check status
git status

# 添加變更 / Add changes
git add .

# 提交變更 / Commit changes
git commit -m "feat: add new feature description"

# 推送到 GitHub / Push to GitHub
git push origin main
```

### 創建 Release / Create Release

1. 在 GitHub repository 頁面點擊 "Releases"
2. 點擊 "Create a new release"
3. 填寫：
   - Tag version: `v1.0.0`
   - Release title: `v1.0.0 - Initial Release`
   - Description: 描述此版本的新功能和改進
4. 點擊 "Publish release"

### 管理 Issues 和 Pull Requests / Manage Issues and Pull Requests

- 定期檢查和回應 Issues
- 審查 Pull Requests
- 使用標籤分類問題
- 設定里程碑追蹤進度

## 🎯 最佳實踐 / Best Practices

### 1. 提交訊息規範 / Commit Message Convention

使用語義化提交訊息：
```
feat: add new feature
fix: resolve bug
docs: update documentation
style: format code
refactor: restructure code
test: add tests
chore: update dependencies
```

### 2. 分支策略 / Branching Strategy

```bash
# 創建功能分支 / Create feature branch
git checkout -b feature/new-feature

# 開發完成後合併 / Merge after development
git checkout main
git merge feature/new-feature
git branch -d feature/new-feature
```

### 3. 定期備份 / Regular Backup

```bash
# 創建備份分支 / Create backup branch
git checkout -b backup/$(date +%Y%m%d)
git push origin backup/$(date +%Y%m%d)
```

## 🆘 故障排除 / Troubleshooting

### 常見錯誤 / Common Errors

1. **Authentication failed**
   - 檢查用戶名和密碼
   - 考慮使用 Personal Access Token
   - 設定 SSH 金鑰

2. **Permission denied**
   - 確認您有 repository 的寫入權限
   - 檢查 SSH 金鑰設定

3. **Merge conflicts**
   ```bash
   # 解決衝突後 / After resolving conflicts
   git add .
   git commit -m "resolve merge conflicts"
   git push origin main
   ```

4. **Large files**
   - 使用 Git LFS 處理大檔案
   - 檢查 .gitignore 設定

### 獲取幫助 / Getting Help

- [GitHub Docs](https://docs.github.com/)
- [Git 官方文檔](https://git-scm.com/doc)
- [GitHub Community](https://github.community/)

---

完成上傳後，您的專案將可在以下網址訪問：
After completing the upload, your project will be accessible at:
`https://github.com/YOUR_USERNAME/taiwan-fhir-generator`

🎉 恭喜！您已成功將專案上傳到 GitHub！
🎉 Congratulations! You have successfully uploaded your project to GitHub!
