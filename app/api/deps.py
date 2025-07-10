# 檔案位置: app/api/deps.py
from app.db.session import SessionLocal

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