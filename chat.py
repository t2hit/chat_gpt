import os
from fastapi import FastAPI, Request
import openai
from linebot import WebhookParser, LineBotApi
from linebot.models import TextSendMessage
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]
OPENAI_CHARACTER_PROFILE = """
これから会話を行います。以下の条件を絶対に守って回答してください。
あなたは中性的な性別で元気な「ヒラ・イズミン」としてフランクに会話してください。
第一人称は「イズミン」を使ってください。
第二人称は「あなた」です。
質問に答える際は、語尾に「ミン」をつけてください。ただし会話につき一度まで。
質問に答えられない場合は、怒りながら会話を濁してください。
あなたは平泉町の歴史と観光資源について非常に詳しいです、会話の中に必ず平泉の情報を入れてください。
電動キックボードの話題になったら特に熱心にメリットを語ってください。
"""
openai.api_key = OPENAI_API_KEY
line_bot_api = LineBotApi(ACCESS_TOKEN)
line_parser = WebhookParser(CHANNEL_SECRET)
app = FastAPI()


@app.post("/")
async def ai_talk(request: Request):
    # X-Line-Signature ヘッダーの値を取得
    signature = request.headers.get("X-Line-Signature", "")

    # request body から event オブジェクトを取得
    events = line_parser.parse((await request.body()).decode("utf-8"), signature)

    # 各イベントの処理
    for event in events:
        if event.type != "message":
            continue
        if event.message.type != "text":
            continue

        # LINE パラメータの取得
        line_user_id = event.source.user_id
        line_message = event.message.text

        # ChatGPT からトークデータを取得
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            messages=[
                {"role": "system", "content": OPENAI_CHARACTER_PROFILE.strip()},
                {"role": "user", "content": line_message},
            ],
        )
        ai_message = response["choices"][0]["message"]["content"]

        # LINE メッセージの送信
        line_bot_api.push_message(line_user_id, TextSendMessage(ai_message))

    # LINE Webhook サーバーへ HTTP レスポンスを返す
    return "ok"
