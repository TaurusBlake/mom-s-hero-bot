#!/usr/bin/env python3
# scripts/graph_builder.py

import os
import sys
import psycopg2
from dotenv import load_dotenv

def escape_cypher_string(s):
    """跳脫 Cypher 字串中的單引號"""
    if s is None:
        return ""
    return s.replace("'", "''")

def main():
    load_dotenv()
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    graph_name = os.getenv("GRAPH_NAME", "moms_hero_graph")

    try:
        conn_str = (
            f"dbname='{db_name}' user='{db_user}' "
            f"host='{db_host}' port='{db_port}' password='{db_password}'"
        )
        print("正在連線到 PostgreSQL...")
        conn = psycopg2.connect(conn_str)
        cursor = conn.cursor()
        print("連線成功！")

        # 安裝並載入 Apache AGE、設定 search_path
        cursor.execute("CREATE EXTENSION IF NOT EXISTS age;")
        cursor.execute("LOAD 'age';")
        cursor.execute("SET search_path = ag_catalog, \"$user\", public;")

        # 刪除並重建圖，並立即提交
        cursor.execute(
            "SELECT * FROM ag_catalog.drop_graph(%s::text, %s);",
            (graph_name, True)
        )
        cursor.execute(
            "SELECT * FROM ag_catalog.create_graph(%s::text);",
            (graph_name,)
        )
        conn.commit()
        print(f"圖譜 '{graph_name}' 已重建並提交。")

        # 讀取食譜主表資料
        print("正在讀取食譜資料...")
        cursor.execute(
            "SELECT id, name, core_ingredients, cuisine_style, key_equipment FROM recipes;"
        )
        cols = [d[0] for d in cursor.description]
        recipes = [dict(zip(cols, row)) for row in cursor.fetchall()]
        print(f"成功讀取 {len(recipes)} 筆食譜資料。")

        # 逐筆建立節點與關係
        for i, recipe in enumerate(recipes, start=1):
            rid = recipe['id']
            rname = escape_cypher_string(recipe['name'])
            # MERGE 食譜節點
            cypher = f"MERGE (r:Recipe {{id: {rid}, name: '{rname}'}})"

            # 核心食材關係
            for ing in recipe.get('core_ingredients') or []:
                ing_safe = escape_cypher_string(ing)
                var_ing = ''.join(filter(str.isalnum, ing_safe))
                cypher += (
                    f" MERGE (i_{var_ing}_{i}:Ingredient {{name: '{ing_safe}'}})"
                    f" MERGE (r)-[:HAS_INGREDIENT]->(i_{var_ing}_{i})"
                )

            # 料理類型關係
            if recipe.get('cuisine_style'):
                cuisine = escape_cypher_string(recipe['cuisine_style'])
                var_cu = ''.join(filter(str.isalnum, cuisine))
                cypher += (
                    f" MERGE (c_{var_cu}:Cuisine {{name: '{cuisine}'}})"
                    f" MERGE (r)-[:BELONGS_TO_CUISINE]->(c_{var_cu})"
                )

            # 所需設備關係
            for eq in recipe.get('key_equipment') or []:
                eq_safe = escape_cypher_string(eq)
                var_eq = ''.join(filter(str.isalnum, eq_safe))
                cypher += (
                    f" MERGE (e_{var_eq}_{i}:Equipment {{name: '{eq_safe}'}})"
                    f" MERGE (r)-[:REQUIRES_EQUIPMENT]->(e_{var_eq}_{i})"
                )

            # 執行 Cypher
            final_sql = (
                f"SELECT * FROM ag_catalog.cypher('{graph_name}', $$"
                f"{cypher}"
                "$$) AS (v agtype);"
            )
            try:
                cursor.execute(final_sql)
            except Exception as e:
                print(f"[ERROR] 第 {i} 筆處理失敗：{e}", file=sys.stderr)
                conn.rollback()
                sys.exit(1)

            # 每 100 筆 Commit
            if i % 100 == 0 or i == len(recipes):
                conn.commit()
                print(f"已處理 {i}/{len(recipes)} 筆")

        print("知識圖譜建構完成！")

    except Exception as ex:
        print(f"[ERROR] 建圖失敗：{ex}", file=sys.stderr)
        sys.exit(1)

    finally:
        try:
            cursor.close()
            conn.close()
            print("資料庫連線已關閉。")
        except:
            pass

if __name__ == "__main__":
    main()
