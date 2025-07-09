# 檔案位置: scripts/importer.py

import os
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, ProgrammingError

def main():
    """
    資料匯入腳本的主函式。
    """
    # 步驟 1: 載入環境變數
    # 從 .env 檔案中讀取我們設定的資料庫連線資訊
    load_dotenv()

    # 步驟 2: 建立資料庫連線
    # 從環境變數中取得資料庫連線資訊
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = "localhost"  # 因為我們的應用和資料庫都透過 Docker 在本機運行
    db_port = "5432"       # PostgreSQL 的預設 Port
    db_name = os.getenv("DB_NAME")

    if not all([db_user, db_password, db_name]):
        print("錯誤：資料庫連線資訊不完整，請檢查 .env 檔案。")
        return

    # 組裝成 SQLAlchemy 的資料庫連線 URL
    # 格式為: postgresql+psycopg2://使用者:密碼@主機:端口/資料庫名稱
    database_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    # 建立資料庫引擎 (Engine)，這是 SQLAlchemy 與資料庫溝通的核心
    try:
        engine = create_engine(database_url)
        # 測試連線
        with engine.connect() as connection:
            print("資料庫連線成功！")
    except Exception as e:
        print(f"資料庫連線失敗：{e}")
        return

    # 步驟 3: 讀取 JSON 檔案
    # 我們假設 recipe_data.json 檔案與 importer.py 在同一個目錄層級的根目錄下
    try:
        with open('recipes_data.json', 'r', encoding='utf-8') as f:
            recipes_data = json.load(f)
        print("成功讀取 recipe_data.json 檔案。")
    except FileNotFoundError:
        print("錯誤：找不到 recipe_data.json 檔案。請確保檔案存在於專案根目錄。")
        return # 找不到檔案就直接結束程式
    except json.JSONDecodeError:
        print("錯誤：recipe_data.json 檔案格式不正確，無法解析。")
        return # 找不到檔案就直接結束程式

    # 步驟 4: 將資料寫入資料庫
    # 我們將在這裡撰寫迴圈，以及執SQL INSERT 指令的邏輯
    print("準備開始將資料寫入資料庫...")

    # 從 engine 的連線池中借用一個連線來執行所有操作
    with engine.begin() as connection:
        # 為了避免重複寫入，我們先清空 recipes 表格
        print("清空舊資料...")
        connection.execute(text("TRUNCATE TABLE recipes RESTART IDENTITY CASCADE;"))
        
        # 準備我們的 SQL INSERT 語句
        # 我們使用 :key 的形式來代表參數，以防止 SQL 注入攻擊
        sql = text("""
            INSERT INTO recipes (
                name, image_url, core_ingredients, full_ingredient_list, steps,
                total_time, difficulty, cuisine_style, servings, key_equipment,
                tips, nutrition_info
            ) VALUES (
                :name, :image_url, :core_ingredients, :full_ingredient_list, :steps,
                :total_time, :difficulty, :cuisine_style, :servings, :key_equipment,
                :tips, :nutrition_info
            )
        """)

        success_count = 0
        fail_count = 0

        # 迭代每一筆從 JSON 讀取到的食譜資料
        for recipe in recipes_data:
            try:
                # 這裡就是我們之前討論的「守門人」邏輯
                # 檢查必要欄位是否存在，如果不存在，我們就跳過這筆資料
                if not all([recipe.get('name'), recipe.get('image_url'), recipe.get('steps')]):
                    print(f"警告：跳過一筆資料，因為缺少必要欄位 (名稱、圖片或步驟)。")
                    fail_count += 1
                    continue

                # 將 None 或空字串的欄位轉換為資料庫能接受的 NULL
                # 這是為了應對 JSON 中可能存在的空值
                params = {
                    "name": recipe.get('name'),
                    "image_url": recipe.get('image_url'),
                    "core_ingredients": recipe.get('core_ingredients'),
                    "full_ingredient_list": json.dumps(recipe.get('full_ingredient_list')), # JSON 欄位需要轉換成字串
                    "steps": recipe.get('steps'),
                    "total_time": recipe.get('total_time') if recipe.get('total_time') is not None else 0,
                    "difficulty": recipe.get('difficulty') if recipe.get('difficulty') is not None else 0,
                    "cuisine_style": recipe.get('cuisine_style'),
                    "servings": recipe.get('servings'),
                    "key_equipment": recipe.get('key_equipment'),
                    "tips": recipe.get('tips'),
                    "nutrition_info": json.dumps(recipe.get('nutrition_info')) # JSON 欄位需要轉換成字串
                }
                
                # 執行 SQL 指令，並將 recipe 字典作為參數傳入
                connection.execute(sql, params)
                success_count += 1

            except (IntegrityError, ProgrammingError) as e:
                # 捕捉可能的資料庫錯誤，例如違反 NOT NULL 限制
                print(f"錯誤：寫入食譜 '{recipe.get('name')}' 時發生資料庫錯誤: {e}")
                fail_count += 1
            except Exception as e:
                # 捕捉其他未知錯誤
                print(f"錯誤：處理食譜 '{recipe.get('name')}' 時發生未知錯誤: {e}")
                fail_count += 1

    print("-" * 20)
    print("資料匯入完成！")
    print(f"成功寫入 {success_count} 筆。")
    print(f"失敗或跳過 {fail_count} 筆。")


if __name__ == "__main__":
    # 當我們直接執行這個 python 檔案時，就呼叫 main() 函式
    main()