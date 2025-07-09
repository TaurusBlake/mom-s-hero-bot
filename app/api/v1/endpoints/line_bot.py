# 檔案位置: app/api/v1/endpoints/line_bot.py

import os
from dotenv import load_dotenv
from fastapi import APIRouter, Request, HTTPException

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent

# 建立一個 APIRouter，之後可以被主應用程式 main.py 引用
router = APIRouter()

# 從 .env 檔案載入環境變數
load_dotenv()

# 從環境變數取得我們的 channel secret 和 access token
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

# 確認環境變數是否設定
if channel_secret is None or channel_access_token is None:
    print("錯誤：LINE_CHANNEL_SECRET 或 LINE_CHANNEL_ACCESS_TOKEN 未設定。")
    # 在真實應用中，你可能會希望程式在此處停止或拋出更明確的錯誤
    
# 設定 Line Bot 的配置
configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)

# 建立一個異步的 API 客戶端
# 在 FastAPI 這種異步框架中，使用異步的函式庫是最佳實踐
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)

@router.post("/callback")
async def callback(request: Request):
    """
    Line Bot 的 Webhook 端點。
    所有來自 Line Platform 的事件都會被送到這裡。
    """
    # 取得請求頭中的 X-Line-Signature，用於驗證請求是否來自 Line
    signature = request.headers['X-Line-Signature']

    # 將請求的內容（body）以文字形式讀取
    body = await request.body()
    body = body.decode()

    try:
        # 使用 handler 來處理 webhook 事件
        handler.handle(body, signature)
    except InvalidSignatureError:
        # 如果簽名驗證失敗，回傳 400 錯誤
        raise HTTPException(status_code=400, detail="Invalid signature. Please check your channel secret.")

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    """
    處理文字訊息事件。
    這是一個「迴聲機器人 (Echo Bot)」的簡單實現。
    """
    # 取得使用者傳來的文字
    user_text = event.message.text
    
    # 準備回覆同樣的文字
    reply_message = TextMessage(text=f"你說了：「{user_text}」")

    # 使用 line_bot_api 的 reply_message 方法回覆訊息
    # 注意：我們需要 event.reply_token 來知道要回覆給誰
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[reply_message]
        )
    )