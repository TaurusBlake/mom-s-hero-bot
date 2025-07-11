# scripts/graph_builder.py

import os
import sys
from dotenv import load_dotenv
import psycopg2

# 輔助函式，用來處理字串中的單引號，防止 Cypher 語法錯誤
def escape_cypher_string(s):
    if s is None:
        return ""
    # 將一個單引號替換成兩個單引號，這是 SQL/Cypher 中跳脫單引號的標準做法
    return s.replace("'", "''")

def main():
    load_dotenv()
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    db_host = "localhost"
    db_port = "5432"

    conn = None
    try:
        conn_str = f"dbname='{db_name}' user='{db_user}' host='{db_host}' port='{db_port}' password='{db_password}'"
        print("正在連線到 PostgreSQL...")
        conn = psycopg2.connect(conn_str)
        cursor = conn.cursor()
        print("連線成功！")

        cursor.execute("SET search_path = ag_catalog, '$user', public;")
        
        print("正在讀取食譜資料...")
        cursor.execute("SELECT id, name, core_ingredients, cuisine_style, key_equipment FROM recipes;")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        recipes = [dict(zip(columns, row)) for row in rows]
        print(f"成功讀取 {len(recipes)} 筆食譜資料。")

        print("正在重建 'moms_hero_graph' 以清空舊資料...")
        cursor.execute("SELECT drop_graph('moms_hero_graph', true);")
        cursor.execute("SELECT create_graph('moms_hero_graph');")
        print("圖譜已成功重建。")

        print("準備開始建立知識圖譜... 這個過程可能需要幾分鐘，請耐心等候。")
        
        for i, recipe in enumerate(recipes):
            recipe_id = recipe['id']
            recipe_name = escape_cypher_string(recipe['name'])

            cypher_query = f"MERGE (r:Recipe {{recipe_id: {recipe_id}, name: '{recipe_name}'}})"

            if recipe.get('core_ingredients'):
                for ingredient in recipe['core_ingredients']:
                    safe_ing = escape_cypher_string(ingredient)
                    # 建立一個在 Cypher 中合法的變數名 (移除空格、特殊符號)
                    ing_variable = ''.join(filter(str.isalnum, safe_ing))
                    cypher_query += f" MERGE (i_{ing_variable}_{i}:Ingredient {{name: '{safe_ing}'}}) MERGE (r)-[:HAS_INGREDIENT]->(i_{ing_variable}_{i})"
            
            if recipe.get('cuisine_style'):
                cuisine = escape_cypher_string(recipe['cuisine_style'])
                cuisine_variable = ''.join(filter(str.isalnum, cuisine))
                cypher_query += f" MERGE (c_{cuisine_variable}:Cuisine {{name: '{cuisine}'}}) MERGE (r)-[:BELONGS_TO_CUISINE]->(c_{cuisine_variable})"

            if recipe.get('key_equipment'):
                for equipment in recipe['key_equipment']:
                    safe_eq = escape_cypher_string(equipment)
                    eq_variable = ''.join(filter(str.isalnum, safe_eq))
                    cypher_query += f" MERGE (e_{eq_variable}_{i}:Equipment {{name: '{safe_eq}'}}) MERGE (r)-[:REQUIRES_EQUIPMENT]->(e_{eq_variable}_{i})"
            
            # --- 最終修正點：在 Python 中手動建立包含 $$ 的完整 SQL 指令 ---
            final_sql_command = f"SELECT * FROM cypher('moms_hero_graph', $${cypher_query}$$) as (v agtype);"
            
            # 直接執行這個完整的指令，不再使用參數替換
            cursor.execute(final_sql_command)

            if (i + 1) % 100 == 0:
                print(f"已處理 {i + 1} / {len(recipes)} 筆食譜...")

        conn.commit()
        print("知識圖譜建立完成！")
        cursor.close()

    except Exception as e:
        print(f"發生錯誤：{e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("資料庫連線已關閉。")

if __name__ == "__main__":
    main()