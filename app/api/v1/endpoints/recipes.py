# 檔案位置: app/api/v1/endpoints/recipes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# 這就是我們之前建立的「依賴項」和「資料庫模型」
from app.api import deps
from app.db import models
from app.schemas import recipe as recipe_schema

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