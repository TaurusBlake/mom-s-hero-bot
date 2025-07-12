import os
import time
import json
from dotenv import load_dotenv
import psycopg2
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# 載入 .env 檔案
load_dotenv()

# 取得資料庫連線字串，與專案 session.py 一致
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = "localhost"
    db_port = "5432"
    db_name = os.getenv("DB_NAME")
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
elif DATABASE_URL.startswith("postgresql+psycopg2://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://", 1)

# 初始化 Gemini Embedding
API_KEY = os.getenv("GOOGLE_API_KEY")
emb = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",  # 官方建議的 embedding 模型
    google_api_key=API_KEY
)

# 讀取 JSON 檔案
with open('recipes_data.json', 'r', encoding='utf-8') as f:
    recipes = json.load(f)

# 連線資料庫
with psycopg2.connect(DATABASE_URL) as conn, conn.cursor() as cur:
    for idx, r in enumerate(recipes[2001:]):
        name = r.get('name') or ''
        core = '；'.join(r.get('core_ingredients') or [])
        full = []
        for section in (r.get('full_ingredient_list') or {}).values():
            for ing, amt in section.items():
                full.append(f"{ing}{amt or ''}")
        full = '，'.join(full)
        steps = '；'.join(r.get('steps') or [])
        vector_text = '。'.join([p for p in [name, core, full, steps] if p])

        vec = emb.embed_query(vector_text)

        # 以 name 為條件更新
        cur.execute(
            "UPDATE recipes SET embedding = %s WHERE name = %s",
            (list(vec), name)
        )
        conn.commit()

        # 控制 API 頻率（建議每 4 秒 1 筆，避免超過免費額度）
        time.sleep(0.3)
        print(f"已處理第 {idx+1} 筆")

print("前 500 筆食譜向量化完成。")
