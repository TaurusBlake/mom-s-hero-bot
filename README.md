# Mom's Hero - AI 智能食譜推薦 LineBot

本專案旨在開發一個為忙碌媽媽設計的 AI 智能食譜推薦 LineBot，解決「今晚吃什麼」的決策疲勞，並有效利用家中剩餘食材。

## 技術棧 (Tech Stack)
- **語言/框架**: Python 3.10+, FastAPI
- **AI 核心**: LangChain, GraphRAG, Gemini API
- **資料庫**: PostgreSQL with pgvector, Apache AGE, and JSONB extensions
- **快取**: Redis
- **前端介面**: LINE Messaging API
- **開發環境**: VS Code / Cursor in WSL2 (Ubuntu 24.04 LTS)
- **部署與維運**: Docker, GitHub Actions (CI/CD)

## 開發環境設定 (WSL2)
本專案在 WSL2 (Windows Subsystem for Linux) 環境中進行開發。

1.  **安裝核心工具**:
    * 在 Windows 中，透過 Microsoft Store 安裝 **Ubuntu 24.04 LTS**。
    * 從[官網](https://code.visualstudio.com/)下載並安裝 **Visual Studio Code**，安裝時務必勾選 `新增至 PATH` 的選項。

2.  **初始化 Ubuntu & VS Code 連線**:
    * 從 Windows「開始」選單啟動 `Ubuntu 24.04 LTS`。
    * 完成初次的 Linux 使用者名稱與密碼設定（建議使用全英文小寫）。
    * 在 Ubuntu 終端機中，執行 `code .`，VS Code 將會自動安裝遠端伺服器並連接。成功後，編輯器左下角會顯示 `WSL: Ubuntu`。

3.  **安裝 Python 擴充套件**:
    * 在 VS Code 左側的擴充套件市場 🧩，搜尋 `Python` (from Microsoft)。
    * 點擊「Install in WSL: Ubuntu」，將其安裝在 WSL 環境中。若遇到問題，可嘗試離線安裝 `.vsix` 檔案。

4.  **設定 Git 身分 (僅需一次)**:
    * 在 WSL 終端機中，設定您的 Git 使用者名稱和 Email：
    ```bash
    git config --global user.name "Your Name"
    git config --global user.email "your.email@example.com"
    ```

## 如何運行
1.  **複製專案 (僅新電腦需一次)**:
    ```bash
    # 在您選擇的工作目錄下 (e.g., ~/projects)
    git clone <您的專案網址>
    cd mom-s-hero-bot
    ```

2.  **建立並啟用虛擬環境**:
    ```bash
    # 僅需在第一次設定
    python3 -m venv venv
    
    # 每次開啟新終端機時執行
    source venv/bin/activate
    ```

3.  **安裝依賴套件**:
    ```bash
    # 僅需在第一次或 requirements.txt 更新時執行
    pip install -r requirements.txt
    ```

4.  **啟動開發伺服器**:
    ```bash
    uvicorn app.main:app --reload
    ```
5.  伺服器將運行在 `http://127.0.0.1:8000`。