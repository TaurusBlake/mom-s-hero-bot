# 檔案位置: app/api/deps.py
from app.db.session import SessionLocal
from fastapi import Header, HTTPException
import os

def get_db():
    """
    一個 FastAPI 的依賴項 (Dependency)。
    在處理請求的過程中，它會建立並提供一個資料庫 session，
    並在請求結束後，確保 session 被關閉。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 新增：管理者權限驗證依賴
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "changeme")

def admin_auth(x_admin_token: str = Header(...)):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="管理者權限驗證失敗")