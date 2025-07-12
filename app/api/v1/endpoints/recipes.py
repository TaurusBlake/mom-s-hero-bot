# 檔案位置: app/api/v1/endpoints/recipes.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

# 這就是我們之前建立的「依賴項」和「資料庫模型」
import os, json
from sqlalchemy import text
from app.api import deps
from app.db import models
from app.schemas import recipe as recipe_schema
from app.schemas.recipe import RecipeSearchResult
from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# 建立一個專屬於食譜的 APIRouter
router = APIRouter()

# -------------------------------------------------------------------
# 這就是我們第一個真正的 API 端點 (Endpoint)
# -------------------------------------------------------------------
@router.get(
    "/{recipe_id}", 
    response_model=recipe_schema.Recipe  # 指定回應的資料格式
)
def read_recipe_by_id(
    recipe_id: int,
    # =================================================================
    # ==  這就是魔法發生的地方！我們「注入」了 get_db 這個依賴項  ==
    # =================================================================
    db: Session = Depends(deps.get_db)
):
    """
    根據食譜 ID，從資料庫中讀取一筆食譜資料。
    """
    # 使用被注入的 db session 物件，來查詢資料庫
    # 這行程式碼會去 `recipes` 表格中，尋找 id 等於我們傳入的 recipe_id 的那一筆資料
    found_recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

    # 如果找不到對應的食譜，就回傳一個 404 Not Found 錯誤
    if not found_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
        
    # 如果找到了，就直接回傳這個從資料庫拿到的物件
    # FastAPI 會很聰明地根據我們在 response_model 中指定的格式，將它轉換成 JSON
    return found_recipe

@router.post(
    "/search",
    response_model=List[RecipeSearchResult],
    summary="語意搜尋食譜",
)
def search_recipes(
    query: str = Query(..., description="搜尋文字"),
    limit: int = Query(5, ge=1, le=20, description="回傳筆數，預設 5"),
    db: Session = Depends(deps.get_db)
    ):
    # 1. 產生查詢向量
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(500, "GOOGLE_API_KEY 未設定")
    emb = GoogleGenerativeAIEmbeddings(model="models/embedding-001",
                                       google_api_key=api_key)
    try:
        q_vec = emb.embed_query(query)
    except Exception as e:
        raise HTTPException(500, f"Embedding 失敗: {e}")

    # 2. 向量檢索
    stmt = text("""
        SELECT id, name, image_url,
               embedding <#> CAST(:q_vec AS vector) AS distance
        FROM recipes
        WHERE embedding IS NOT NULL
        ORDER BY distance
        LIMIT :limit
    """)
    rows = db.execute(stmt, {"q_vec": q_vec, "limit": limit}).fetchall()

    if not rows:
        raise HTTPException(404, f"找不到符合「{query}」的食譜")

    # 3. 回傳結果
    return [
        RecipeSearchResult(
            id=r.id,
            name=r.name,
            image_url=r.image_url,
            distance=r.distance
        )
        for r in rows
    ]