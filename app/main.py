# app/main.py
from fastapi import FastAPI
# 匯入 line_bot router
from app.api.v1.endpoints import line_bot , recipes

# 建立一個 FastAPI 應用實例
app = FastAPI(title="Mom's Hero API")

# 定義一個根路由 (endpoint)
@app.get("/")
def read_root():
    return {"message": "Welcome to Mom's Hero API!"}

# 建立一個健康檢查的路由
@app.get("/health")
def health_check():
    return {"status": "ok"}

# 將 line_bot router 掛載到主應用程式上
# 這樣所有到 /api/v1/line 的請求，都會被轉交給 line_bot.py 處理
app.include_router(line_bot.router, prefix="/api/v1/line", tags=["linebot"])

# 將 recipes router 也掛載到主應用程式上
# 我們給它一個 /api/v1/recipes 的分機號
app.include_router(recipes.router, prefix="/api/v1/recipes", tags=["recipes"])