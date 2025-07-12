# app/services/ai_service.py
# app/services/ai_service.py

import os
from typing import Any, Dict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import GraphCypherQAChain
from langchain_community.graphs.graph_store import GraphStore
from dotenv import load_dotenv
 
class CustomAgeGraph(GraphStore):
    def __init__(self, connection_details: Dict[str, Any], graph_name: str):
        self.connection_details = connection_details
        self.graph_name = graph_name
        self._structured_schema: Dict[str, Any] = {}
        self.refresh_schema()

    @property
    def get_structured_schema(self) -> Dict[str, Any]:
        return self._structured_schema
 
    def refresh_schema(self) -> None:
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

class AIService:
    """
    封裝 AI 後端，使用 ChatGoogleGenerativeAI + GraphCypherQAChain
    """
    def __init__(self):
        # 載入環境變數
        load_dotenv()
        # 準備資料庫連線資訊
        self.conn_details = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
        }
        # 初始化 CustomAgeGraph
        self.graph = CustomAgeGraph(self.conn_details, graph_name=os.getenv("GRAPH_NAME", "moms_hero"))
        # 初始化 LLM
        self.llm = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"),
                                          model="gemini-1.5-flash"  # 或您要的其他 Gemini 模型
                                          )
        # 建立 Graph QA Chain
        self.chain = GraphCypherQAChain.from_llm(llm=self.llm,
                                                 graph=self.graph,
                                                 allow_dangerous_requests=True)

    def query_graph(self, question: str) -> Any:
        """
        接收使用者問題，執行 GraphCypherQAChain 並回傳結果
        """
        try:
            return self.chain.run(question)
        except Exception as e:
            # 記錄錯誤並回傳可讀訊息
            print(f"[AIService] 查詢發生錯誤：{e}")
            return "抱歉，查詢時發生錯誤，請稍後再試。"

__all__ = ["CustomAgeGraph", "AIService"]

# 原有主程式入口
if __name__ == '__main__':
    print("="*30)
    print("AI 服務已啟動，現在可以開始提問關於食譜的問題。")
    print("例如：'有哪些食譜用到牛肉？' 或 '列出三個中式料理'")
    print("輸入 'exit' 或 'quit' 來離開。")
    print("="*30)
    ai_service = AIService()
    while True:
        user_text = input("你: ")
        if user_text.lower() in ["exit", "quit", "掰掰"]:
            print("AI: 掰掰！")
            break
        ai_response = ai_service.query_graph(user_text)
        print(f"AI: {ai_response}")