# ============================================
#   Escape from Tarkov 豪華版 Discord BOT
#   画像つき / 絵文字つき / 緑ライン / Twitch宣伝
#   完全版フルセット（Render向け）
# ============================================

import os
import discord
import requests
from rapidfuzz import process, fuzz

# ==========
# ENV 読込
# ==========
TOKEN = os.getenv("DISCORD_TOKEN")
TARKOV_API_KEY = os.getenv("TARKOV_MARKET_API_KEY")
TWITCH_URL = os.getenv("TWITCH_URL", "https://www.twitch.tv/jagamiorochi")
FUZZY_THRESHOLD = int(os.getenv("FUZZY_THRESHOLD", "60"))

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# ==========
# 辞書
# ==========
ITEM_DICT = {
    "ledx": "LEDX Skin Transilluminator",
    "レドックス": "LEDX Skin Transilluminator",
    "ledx 光る": "LEDX Skin Transilluminator",
    "gpu": "Graphics card",
    "グラボ": "Graphics card",
    "bitcoin": "Physical Bitcoin",
    "ビットコイン": "Physical Bitcoin",
}


# ==========
# Tarkov Market API
# ==========
def get_market_item(name):
    url = "https://api.tarkov-market.app/api/v1/item"
    headers = {"x-api-key": TARKOV_API_KEY}

    try:
        r = requests.get(url, params={"q": name}, headers=headers)
        data = r.json()

        if isinstance(data, list) and len(data) > 0:
            return data[0]
        return None
    except:
        return None


# ==========
# Discord メッセージ
# ==========
@client.event
async def on_message(message):
    if message.author.bot:
        return

    msg = message.content.strip().lower()

    if not msg.startswith("!"):
        return

    query = msg[1:].strip()

    # ファジー一致
    match = process.extractOne(query, ITEM_DICT.keys(), scorer=fuzz.token_sort_ratio)

    if match and match[1] >= FUZZY_THRESHOLD:
        item_name = ITEM_DICT[match[0]]
    else:
        item_name = query

    # API取得
    item = get_market_item(item_name)

    if not item:
        await message.channel.send(f"❌ 該当アイテムが見つかりませんでした…")
        return

    # ==========
    # EMBED 豪華版
    # ==========
    embed = discord.Embed(
        title=item["name"],
        description=f"🎯 **検索ワード:** `{query}`\n🟢 **マッチ:** {item['name']}",
        color=0x00ff99,
    )

    # 画像
    if "img" in item:
        embed.set_thumbnail(url=item["img"])

    # フリマ平均
    embed.add_field(
        name="💰 フリマ平均",
        value=f"{item['avg24hPrice']:,}₽",
        inline=False,
    )

    # トレーダー価格
    trader_text = ""
    if "traderName" in item and item["traderName"]:
        trader_text += f"🔸 **{item['traderName']}**：{item['traderPrice']:,}₽\n"

    if trader_text == "":
        trader_text = "データなし"

    embed.add_field(name="🏪 トレーダー最高買取", value=trader_text, inline=False)

    # 差額
    if item["traderPrice"] > 0:
        diff = item["avg24hPrice"] - item["traderPrice"]
        embed.add_field(
            name="📈 差額",
            value=f"{diff:+,}₽",
            inline=False
        )

    # Wiki
    if "wikiLink" in item:
        embed.add_field(
            name="📘 Wiki",
            value=f"[開く]({item['wikiLink']})",
            inline=False
        )

    # Twitch
    embed.add_field(
        name="✨ Twitch",
        value=f"[{TWITCH_URL}]({TWITCH_URL})",
        inline=False
    )

    await message.channel.send(embed=embed)


# ==========
# BOT 起動
# ==========
client.run(TOKEN)
