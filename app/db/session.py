# 檔案位置: app/db/session.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 載入 .env 檔案中的環境變數
load_dotenv()

# 從環境變數中取得資料庫連線 URL
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    # 為了讓它在之前的 importer.py 也能運作，我們保留這種組裝方式作為備用
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = "db"
    db_port = "5432"
    db_name = os.getenv("DB_NAME")
    DATABASE_URL = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# 建立 SQLAlchemy 引擎
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 建立一個 SessionLocal class
# 這個 class 的每一個實例，都將會是一個獨立的資料庫 session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)