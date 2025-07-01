# 檔案位置: app/db/models.py

from sqlalchemy import Column, Integer, String, Text, ARRAY, JSON
from sqlalchemy.orm import declarative_base

# 建立一個所有模型都會繼承的 Base class
Base = declarative_base()

class Recipe(Base):
    """
    對應資料庫中 "recipes" 表格的 SQLAlchemy ORM 模型。
    """
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)  # 食譜編號
    name = Column(String, index=True, nullable=False)  # 食譜名稱
    image_url = Column(String, nullable=False)  # 食譜圖片網址
    core_ingredients = Column(ARRAY(String), nullable=False)  # 核心食材
    full_ingredient_list = Column(JSON, nullable=False)  # 完整食材清單
    steps = Column(ARRAY(Text), nullable=False)  # 步驟
    total_time = Column(Integer, nullable=False)  # 總時間
    difficulty = Column(Integer, nullable=False)  # 難度
    cuisine_style = Column(String, nullable=True)  # 菜系
    servings = Column(String, nullable=True)  # 份量
    key_equipment = Column(ARRAY(String), nullable=True)  # 關鍵設備
    tips = Column(ARRAY(Text), nullable=True)  # 小技巧
    nutrition_info = Column(JSON, nullable=True)  # 營養資訊