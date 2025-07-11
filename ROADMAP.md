# Mom's Hero 專案開發路線圖 (ROADMAP)

最後更新：2025-07-01

## 階段一：環境設定與基礎建設 (已完成)
- [x] 完成 WSL2 + Ubuntu 的安裝與重設
- [x] 解決環境、網路與擴充套件安裝問題
- [x] 完成 VS Code 與 WSL 的無縫整合
- [x] 完成 Git 本地與 GitHub 遠端的身分設定與授權
- [x] 完成 Python 虛擬環境建立
- [x] 完成 FastAPI 與 Uvicorn 安裝並成功運行 Hello World API
- [x] 完成專案文件系統初始化 (本文件)

## 階段二：核心功能開發 (進行中)
- [x] **(當前任務)** Lesson 4: 定義 API 與資料庫模型 (Pydantic & SQLAlchemy)
- [X] Lesson 5: 撰寫爬蟲腳本 (`scripts/crawler.py`)
- [X] Lesson 6: 建立與連接 PostgreSQL 資料庫
- [x] Lesson 7: 完成食譜資料的寫入與讀取
- [ ] Lesson 8: 整合 Line Messaging API

## 階段三：AI 智能核心 (規劃中)
- [X] Lesson 9: 整合 LangChain 與 Gemini API
- [ ] Lesson 10: 建立 GraphRAG 所需的知識圖譜
- [ ] Lesson 11: 實現智能食譜推薦邏輯

## 階段四：部署與上線 (規劃中)
- [ ] Lesson 12: 使用 Docker 進行容器化打包
- [ ] Lesson 13: 設定 GitHub Actions (CI/CD) 自動化部署
- [ ] Lesson 14: MVP 正式上線