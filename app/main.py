# app/main.py
from fastapi import FastAPI

# 建立一個 FastAPI 應用實例
app = FastAPI(title="Mom's Hero Recipe Bot API")

# 定義一個根路由 (endpoint)
@app.get("/")
def read_root():
    return {"message": "Mom's Hero Recipe Bot is running!"}

# 建立一個健康檢查的路由
@app.get("/health")
def health_check():
    return {"status": "ok"}