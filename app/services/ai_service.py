# 檔案位置: app/services/ai_service.py

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 載入環境變數
load_dotenv()

class AIService:
    """
    提供所有與 AI (Gemini, LangChain) 相關的服務。
    """
    def __init__(self):
        """
        初始化 AI 服務，並設定 Gemini 模型。
        """
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("請設定 GOOGLE_API_KEY 環境變數")

        # 初始化 Gemini 1.5 Flash 模型
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
        )
        print("AI Service 初始化完成，已連線至 Gemini 1.5 Flash。")

    def chat(self, user_input: str) -> str:
        """
        一個簡單的對話函式，接收使用者輸入並回傳模型的生成結果。
        """
        try:
            response = self.llm.invoke(user_input)
            return response.content
        except Exception as e:
            print(f"呼叫 Gemini API 時發生錯誤: {e}")
            return "抱歉，系統似乎有些問題，請稍後再試。"

# 建立一個全域共享的 AIService 實例
ai_service = AIService()

# 主程式進入點，方便獨立測試
if __name__ == '__main__':
    print("正在測試 AIService...")
    while True:
        user_text = input("你: ")
        if user_text.lower() in ["exit", "quit", "掰掰"]:
            print("AI: 掰掰！")
            break
        
        ai_response = ai_service.chat(user_text)
        print(f"AI: {ai_response}")