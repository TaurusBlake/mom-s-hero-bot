-- DDL for creating the recipes table
-- Final Version: Precisely aligned with the app/db/models.py SQLAlchemy model

-- 先刪除可能已存在的舊表格，方便我們重新開始
DROP TABLE IF EXISTS recipes;

-- 建立 recipes 表格
CREATE TABLE recipes (
    -- 對應 id = Column(Integer, primary_key=True, index=True)
    id SERIAL PRIMARY KEY,

    -- 對應 name = Column(String, index=True, nullable=False)
    name TEXT NOT NULL,

    -- 對應 image_url = Column(String, nullable=False)
    image_url TEXT NOT NULL,

    -- 對應 core_ingredients = Column(ARRAY(String), nullable=False)
    core_ingredients TEXT[] NOT NULL,

    -- 對應 full_ingredient_list = Column(JSON, nullable=False)
    full_ingredient_list JSONB NOT NULL,

    -- 對應 steps = Column(ARRAY(Text), nullable=False)
    steps TEXT[] NOT NULL,

    -- 對應 total_time = Column(Integer, nullable=False)
    total_time INTEGER NOT NULL,

    -- 對應 difficulty = Column(Integer, nullable=False)
    difficulty INTEGER NOT NULL,

    -- 對應 cuisine_style = Column(String, nullable=True)
    cuisine_style VARCHAR(50),

    -- 對應 servings = Column(String, nullable=True)
    servings VARCHAR(50),

    -- 對應 key_equipment = Column(ARRAY(String), nullable=True)
    key_equipment TEXT[],

    -- 對應 tips = Column(ARRAY(Text), nullable=True)
    tips TEXT[],

    -- 對應 nutrition_info = Column(JSON, nullable=True)
    nutrition_info JSONB,

    -- 雖然 models.py 中沒有，但保留時間戳記是極佳的實踐
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 根據 models.py 中的 index=True，為 name 欄位建立索引
CREATE INDEX idx_recipes_name ON recipes (name);