# ==============================
#  Escape from Tarkov Discord Bot
#  アイテム検索 + Wikiリンク + Twitch宣伝
#  A版（import os 対応）
#  完全復元版
# ==============================

import os
import discord
import requests
from rapidfuzz import process, fuzz

# ---------------------------------------
# 1. Discord BOT 設定
# ---------------------------------------

TOKEN = os.getenv("DISCORD_TOKEN")  # ← OSから読み取るバージョン
CHANNEL_ID = None  # 特定チャンネルに制限しないなら None

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# ---------------------------------------
# 2. タルコフ辞書（略称・日本語OK）
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
    "ledx 光るやつ": "LEDX Skin Transilluminator",
    "ガラナ": "Sodium bicarbonate",
}

# ---------------------------------------
# 3. Wiki URL 自動生成
# ---------------------------------------

def generate_wiki_url(item_name):
    base = "https://escapefromtarkov.fandom.com/wiki/"
    return base + item_name.replace(" ", "_")

# ---------------------------------------
# 4. Tarkov.dev API 取得
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
          trader {
            name
          }
        }
      }
    }
    """
    try:
        r = requests.post(url, json={"query": query, "variables": {"name": item_name}})
        data = r.json()
        return data["data"]["items"]
    except:
        return None

# ---------------------------------------
# 5. メッセージイベント
# ---------------------------------------

@client.event
async def on_message(message):
    if message.author.bot:
        return
    if CHANNEL_ID and message.channel.id != CHANNEL_ID:
        return

    user_query = message.content.strip()

    if len(user_query) < 2:
        return

    # --- ① 辞書で判定 ---
    match = process.extractOne(user_query, ITEM_DICT.keys(), scorer=fuzz.token_sort_ratio)

    if match and match[1] > 75:
        fixed_name = ITEM_DICT[match[0]]
    else:
        fixed_name = user_query  # 辞書がはずれたらそのまま検索

    # --- ② API検索 ---
    results = get_api_data(fixed_name)

    if not results:
        await message.channel.send("❌ 該当アイテムが見つかりませんでした…")
        return

    item = results[0]

    # --- ③ Embed 生成 ---
    embed = discord.Embed(
        title=item["name"],
        description=f"**検索ワード：** {user_query}",
        color=0x2ecc71
    )

    embed.add_field(name="Wiki", value=f"[開く]({item['wikiLink']})", inline=False)
    embed.add_field(name="24h平均価格", value=f"{item['avg24hPrice']}₽", inline=True)

    trader_text = ""
    for tp in item["traderPrices"]:
        trader_text += f"**{tp['trader']['name']}**：{tp['price']}₽\n"
    if trader_text == "":
        trader_text = "データなし"

    embed.add_field(name="トレーダー買取", value=trader_text, inline=False)

    embed.set_footer(text="Twitch: https://www.twitch.tv/jagamiorochi")

    await message.channel.send(embed=embed)

# ---------------------------------------
# 6. BOT 起動
# ---------------------------------------

client.run(TOKEN)
