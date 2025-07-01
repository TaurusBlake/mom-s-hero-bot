# 檔案位置: app/schemas/recipe.py

from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class RecipeBase(BaseModel):
    """
    食譜資料的基礎模型，定義了所有食譜都會有的共同欄位。
    """
    name: str   # 食譜名稱
    image_url: HttpUrl  # 食譜圖片網址
    core_ingredients: List[str]  # 核心食材
    full_ingredient_list: dict  # 完整食材清單
    steps: List[str]  # 步驟
    total_time: int  # 總時間
    difficulty: int  # 難度
    cuisine_style: Optional[str] = None  # 菜系
    servings: Optional[str] = None  # 份量
    key_equipment: Optional[List[str]] = None  # 關鍵設備
    tips: Optional[List[str]] = None  # 小技巧
    nutrition_info: Optional[dict] = None  # 營養資訊

class RecipeCreate(RecipeBase):
    """ 用於創建新食譜的模型。 """
    pass

class Recipe(RecipeBase):
    """ 用於從 API 讀取食譜資料的模型。 """
    id: int

    class Config:
        orm_mode = True