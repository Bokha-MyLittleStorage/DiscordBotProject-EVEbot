encoding='euc-kr'
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import os
import openai

#.env에서 토큰 불러오기 (개발 환경에서만, 깃 업로드 시 주석처리하기)
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())  # 자동으로 .env 파일 경로를 찾고 로드
API_KEY = os.getenv("MY_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
# 여기까지

openai.api_key = API_KEY  # 발급받은 키 입력

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{datetime.utcnow()} - ✅ 로그인 완료: {bot.user}")

@bot.command()
async def newfleet(ctx, message): # 플릿 생성

    # 메시지 받아오기
    FleetLeader = ctx.author

    # 전처리
    response = openai.chat.completions.create(
    model="gpt-5", messages= [
    {"role": "system", "content": "You are a assistant."},
    {"role": "user", "content": f"다음 메시지의 내용에서 언급된 시간 정보를 추출해줘. 현재 시각은 {datetime.utcnow()+ timedelta(hours=9)}이고,  "} ], 
    temperature=1,
    max_tokens=500)


    guild = ctx.guild
    start_time = datetime.utcnow() + timedelta(minutes=10)
    end_time = start_time + timedelta(hours=1)

    event = await guild.create_scheduled_event(
        name="🎮 주말 게임 모임",
        start_time=start_time,
        end_time=end_time,
        privacy_level=discord.PrivacyLevel.guild_only,
        entity_type=discord.EntityType.voice,
        channel=ctx.author.voice.channel,  # 사용자의 현재 음성채널 기준
        description="다 같이 게임을 즐겨요!"
    )

    await ctx.send(f"이벤트가 생성되었습니다 👉 {event.name}")

bot.run(BOT_TOKEN)
