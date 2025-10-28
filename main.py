encoding='euc-kr'
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import os
import openai
import threading
from flask import Flask

'''
#.env에서 토큰 불러오기 (개발 환경에서만, 깃 업로드 시 주석처리하기)
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())  # 자동으로 .env 파일 경로를 찾고 로드
API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
# 여기까지
'''
API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 타임스탬프
# print(f"[{discord.utils.utcnow()}] ")

openai.api_key = API_KEY  # 발급받은 키 입력

intents = discord.Intents.default()
intents.message_content = True  # 👈 메시지 내용 읽기 허용
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"[{discord.utils.utcnow()}] ✅ 로그인 완료: {bot.user}")
    
# zz 이거 켜면 명령어가 작동 안한대
'''
@bot.event
async def on_message(ctx):
    print(f"[{discord.utils.utcnow()}] Message detected:", str(ctx.content))
    '''

@bot.command()
async def hello(ctx):
    print(f"[{discord.utils.utcnow()}] hello, working now.")
    await ctx.send(f"[{discord.utils.utcnow()}] hello, working now.")

@bot.command()
async def newfleet(ctx, *, message_raw): # 플릿 생성

    # 메시지 받아오기
    message = message_raw[:500]
    fleet_leader = ctx.author.display_name
    print(f"[{discord.utils.utcnow()}] 메시지 수신: " + message)
    print(f"[{discord.utils.utcnow()}] 메시지 작성자: " + fleet_leader)
    message_link = f"https://discord.com/channels/{ctx.message.guild.id}/{ctx.message.channel.id}/{ctx.message.id}"
    
    # 전처리
    response = openai.responses.create(
    model="gpt-5-mini", input= [
    {"role": "system", "content": "You are a assistant."},
    {"role": "user", "content": f"""현재 시각 정보를 기반으로 다음 메시지의 내용에서 언급된 시각을 구하고,
    해당 시각까지 남은 시간을 초 단위로 변환해서 출력해줘.
    현재 시각은 {discord.utils.utcnow()+ timedelta(hours=9)}이야.
    출력할 때는 출력값을 바로 코드에 집어넣을 수 있도록 문자 없이 정수 형태로 대답해 줘."""
     + " 메시지: " + message} ],
    #reasoning={"effort": "minimal"}, # 켜면 자원을 덜 먹지만 망가지더라
    #text={"verbosity": "low"}
    )
    timeleft = int(response.output_text)

    guild = ctx.guild
    start_time = discord.utils.utcnow() + timedelta(seconds=timeleft)
    end_time = start_time + timedelta(hours=1)

    event = await guild.create_scheduled_event(
        name=("New Fleet by "+ fleet_leader),
        start_time=start_time,
        end_time=end_time,
        privacy_level=discord.PrivacyLevel.guild_only,
        entity_type=discord.EntityType.external,
        #channel=ctx.author.voice.channel,  # 사용자의 현재 음성채널 기준
        location= message_link, # 메시지 링크
        description= message
    )

    await ctx.send(f"이벤트가 생성되었습니다 👉 {event.name}")
    
def run_discord_bot():
    API_KEY = os.getenv("API_KEY")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    openai.api_key = API_KEY  # 발급받은 키 입력
    intents = discord.Intents.default()
    intents.message_content = True  # 👈 메시지 내용 읽기 허용
    intents.messages = True
    intents.guilds = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    bot.run(BOT_TOKEN)

# ----------------- 2. Render용 HTTP 서버 추가 -----------------

# Render가 요구하는 PORT 환경 변수를 가져옵니다. 기본값은 10000입니다.
PORT = int(os.environ.get("PORT", 10000)) 

app = Flask(__name__)

# Render는 이 엔드포인트에 주기적으로 요청을 보내 서비스 상태를 확인합니다.
@app.route('/')
def home():
    return "Discord Bot is Running!", 200

def run_flask_server():
    # 0.0.0.0 호스트와 Render가 요구하는 PORT에 바인딩합니다.
    app.run(host='0.0.0.0', port=PORT)

# ----------------- 3. 메인 실행 -----------------

if __name__ == '__main__':
    # 봇을 별도의 스레드로 실행하여 봇과 서버가 동시에 돌아가도록 합니다.
    # Flask 서버는 메인 스레드에서 실행됩니다.
    bot_thread = threading.Thread(target=run_discord_bot)
    bot_thread.start()

    # Flask 서버 (HTTP 서버)를 시작하여 Render의 포트 바인딩 요구 사항을 충족합니다.
    run_flask_server()