# ==============================
#  Escape from Tarkov Discord Bot
#  A版（Render / os.getenv 対応 完全版）
# ==============================

import os
import discord
import requests
from rapidfuzz import process, fuzz

# ---------------------------------------
# 1. Discord BOT 設定（Render用）
# ---------------------------------------

TOKEN = os.getenv("DISCORD_TOKEN")   # Render の環境変数から取る
CHANNEL_ID = None  # 制限しない場合 None

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# ---------------------------------------
# 2. アイテム辞書（略称 / 日英 / 日本語OK）
# ---------------------------------------

ITEM_DICT = {
    "GPU": "Graphics card",
    "グラボ": "Graphics card",
    "ビットコイン": "Physical Bitcoin",
    "bitcoin": "Physical Bitcoin",
    "レッドレベル": "Red Rebel ice pick",
    "red rebel": "Red Rebel ice pick",
    "prokill": "Chain with Prokill medallion",
    "goldchain": "Golden neck chain",
    "ライオン": "Bronze lion figurine",
    "lion": "Bronze lion figurine",
    "ledx": "LEDX Skin Transilluminator",
    "ガラナ": "Sodium bicarbonate",
}


# ---------------------------------------
# 3. Tarkov.dev API
# ---------------------------------------

def get_api_data(item_name):
    url = "https://api.tarkov.dev/graphql"
    query = """
    query($name:String!) {
      items(name:$name) {
        name
        shortName
        wikiLink
        avg24hPrice
        traderPrices {
          price
          trader { name }
        }
      }
    }
    """

    try:
        r = requests.post(url, json={"query": query, "variables": {"name": item_name}})
        data = r.json()
        return data["data"]["items"]
    except Exception:
        return None


# ---------------------------------------
# 4. メッセージイベント
# ---------------------------------------

@client.event
async def on_ready():
    print("Bot is online!")

@client.event
async def on_message(message):

    if message.author.bot:
        return

    if CHANNEL_ID and message.channel.id != CHANNEL_ID:
        return

    user_query = message.content.strip()
    if len(user_query) < 2:
        return

    # --- ① 辞書の曖昧検索 ---
    match = process.extractOne(user_query, ITEM_DICT.keys(), scorer=fuzz.token_sort_ratio)

    if match and match[1] > 75:
        fixed_name = ITEM_DICT[match[0]]
    else:
        fixed_name = user_query

    # --- ② API ---
    results = get_api_data(fixed_name)

    if not results:
        await message.channel.send("❌ アイテムが見つかりませんでした")
        return

    item = results[0]

    # --- ③ Embed ---
    embed = discord.Embed(
        title=item["name"],
        description=f"**検索ワード：** {user_query}",
        color=0x00ff9d
    )

    embed.add_field(name="Wiki", value=f"[開く]({item['wikiLink']})", inline=False)
    embed.add_field(name="フリマ平均", value=f"{item['avg24hPrice']}₽", inline=True)

    trader_text = ""
    for t in item["traderPrices"]:
        trader_text += f"**{t['trader']['name']}**：{t['price']}₽\n"
    if trader_text == "":
        trader_text = "データなし"

    embed.add_field(name="トレーダー最高買取価格", value=trader_text, inline=False)

    embed.set_footer(text="Twitch: https://www.twitch.tv/jagamiorochi")

    await message.channel.send(embed=embed)


# ---------------------------------------
# 5. BOT起動
# ---------------------------------------

client.run(TOKEN)
