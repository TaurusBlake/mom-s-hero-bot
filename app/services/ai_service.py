# app/services/ai_service.py

import os
import sys
from dotenv import load_dotenv
import psycopg2
from typing import Any, Dict, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import GraphCypherQAChain
# 步驟 1: 匯入 LangChain 要求我們繼承的 GraphStore 基底類別
from langchain_community.graphs.graph_store import GraphStore

# --- 我們自訂的 Graph 連接器 ---
# 步驟 2: 讓我們的 CustomAgeGraph 繼承自 GraphStore
class CustomAgeGraph(GraphStore):
    """
    一個自訂的 LangChain Graph 類別，繼承自 GraphStore，
    用於教 LangChain 如何與我們的 PostgreSQL + Apache AGE 資料庫溝通。
    """
    def __init__(self, connection_details: Dict[str, Any], graph_name: str):
        self._connection_details = connection_details
        self.graph_name = graph_name
        self.refresh_schema()

    def query(self, cypher_query: str) -> List[Dict[str, Any]]:
        """執行一個 Cypher 查詢並回傳結果。"""
        conn = None
        try:
            conn = psycopg2.connect(**self._connection_details)
            cursor = conn.cursor()
            cursor.execute("SET search_path = ag_catalog, '$user', public;")
            cursor.execute(f"SELECT * FROM cypher('{self.graph_name}', $${cypher_query}$$) as (v agtype);")
            results = cursor.fetchall()
            cursor.close()
            return [row[0] for row in results]
        except Exception as e:
            print(f"Cypher 查詢錯誤: {e}")
            return []
        finally:
            if conn:
                conn.close()

    @property
    def get_structured_schema(self) -> Dict[str, Any]:
        """將這個方法變成一個屬性，以符合 LangChain 的要求。"""
        return self._structured_schema

    def refresh_schema(self) -> None:
        """
        重新整理並儲存圖譜的綱要資訊。
        """
        self._structured_schema = {
            "node_labels": ["Recipe", "Ingredient", "Cuisine", "Equipment"],
            "node_properties": [
                {"label": "Recipe", "properties": [("recipe_id", "INTEGER"), ("name", "STRING")]},
                {"label": "Ingredient", "properties": [("name", "STRING")]},
                {"label": "Cuisine", "properties": [("name", "STRING")]},
                {"label": "Equipment", "properties": [("name", "STRING")]},
            ],
            "relationships": [
                {"start": "Recipe", "type": "HAS_INGREDIENT", "end": "Ingredient"},
                {"start": "Recipe", "type": "BELONGS_TO_CUISINE", "end": "Cuisine"},
                {"start": "Recipe", "type": "REQUIRES_EQUIPMENT", "end": "Equipment"},
            ],
            "relationship_properties": [], 
        }

# --- 主要服務 ---

load_dotenv()

class AIService:
    def __init__(self):
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("請設定 GOOGLE_API_KEY 環境變數")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            temperature=0.2,
        )
        print("AI Service: Gemini LLM 已成功初始化。")

        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME")
        db_host = "localhost"
        db_port = "5432"
        graph_name = "moms_hero_graph"
        
        connection_details = {
            "dbname": db_name,
            "user": db_user,
            "password": db_password,
            "host": db_host,
            "port": db_port,
        }

        self.graph = CustomAgeGraph(connection_details, graph_name)
        print(f"AI Service: 已成功連線至 '{graph_name}' 圖譜，並載入綱要。")
        
        self.qa_chain = GraphCypherQAChain.from_llm(
            graph=self.graph,
            llm=self.llm,
            allow_dangerous_requests=True
        )
        print("AI Service: GraphCypherQAChain 已成功建立。")

    def query_graph(self, user_question: str) -> str:
        try:
            result = self.qa_chain.invoke({"query": user_question})
            return result.get("result", "抱歉，我無法根據您的問題找到對應的答案。")
        except Exception as e:
            print(f"AI Service: 執行圖譜查詢時發生錯誤: {e}")
            return "抱歉，我的大腦好像有點短路了，請稍後再試一次。"

# ... (主程式進入點部分維持不變) ...
ai_service = AIService()

if __name__ == '__main__':
    print("="*30)
    print("AI 服務已啟動，現在可以開始提問關於食譜的問題。")
    print("例如：'有哪些食譜用到牛肉？' 或 '列出三個中式料理'")
    print("輸入 'exit' 或 'quit' 來離開。")
    print("="*30)
    
    while True:
        user_text = input("你: ")
        if user_text.lower() in ["exit", "quit", "掰掰"]:
            print("AI: 掰掰！")
            break
        
        ai_response = ai_service.query_graph(user_text)
        print(f"AI: {ai_response}")