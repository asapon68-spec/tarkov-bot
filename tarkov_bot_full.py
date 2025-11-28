# ============================================
#  Escape from Tarkov Discord BOT
#  ・辞書なし
#  ・APIのアイテム名リストから曖昧マッチ
#  ・Tarkov-Market API対応
#  ・画像 / Wiki / Twitch付き
# ============================================

import os
import discord
import requests
from rapidfuzz import process, fuzz

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TARKOV_MARKET_API_KEY = os.getenv("TARKOV_MARKET_API_KEY")
TWITCH_URL = os.getenv("TWITCH_URL", "https://www.twitch.tv/jagamiorochi")

FUZZY_THRESHOLD = int(os.getenv("FUZZY_THRESHOLD", "60"))

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# ============================================
#  Tarkov-Market から全アイテム名リスト取得
# ============================================

ALL_ITEM_NAMES = []

def load_all_item_names():
    global ALL_ITEM_NAMES
    url = "https://tarkov-market.com/api/v1/items/all"
    headers = {"x-api-key": TARKOV_MARKET_API_KEY}

    try:
        print("Fetching item list...")
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        ALL_ITEM_NAMES = [item["name"] for item in data if "name" in item]

        print(f"Loaded {len(ALL_ITEM_NAMES)} item names.")
    except Exception as e:
        print("Error loading item list:", e)
        ALL_ITEM_NAMES = []


# ============================================
#  単語 → もっとも近いアイテム名を探す
# ============================================

def resolve_query(query: str) -> str:
    if not ALL_ITEM_NAMES:
        return query

    best = process.extractOne(
        query,
        ALL_ITEM_NAMES,
        scorer=fuzz.token_sort_ratio
    )

    if best and best[1] >= FUZZY_THRESHOLD:
        return best[0]

    return query


# ============================================
#  Tarkov-Market からアイテムデータ取得
# ============================================

def fetch_item(name: str):
    url = "https://tarkov-market.com/api/v1/item"
    headers = {"x-api-key": TARKOV_MARKET_API_KEY}
    params = {"q": name}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return None
        return data[0]  # 最もスコアが高いアイテム
    except Exception:
        return None


# ============================================
#  Discord メッセージ
# ============================================

@client.event
async def on_message(message: discord.Message):

    if message.author.bot:
        return

    content = message.content.strip()

    # 「!」だけ反応
    if not content.startswith("!"):
        return

    query = content[1:].strip()
    if not query:
        return

    # 曖昧検索
    resolved = resolve_query(query)

    # API検索
    data = fetch_item(resolved)

    if not data:
        await message.channel.send(f"❌ `{query}` のアイテムが見つかりませんでした…")
        return

    # ==== Embed 作成 ====
    embed = discord.Embed(
        title=data["name"],
        url=data.get("wikiLink"),
        color=0x00FF99
    )

    # 画像
    if data.get("img"):
        embed.set_thumbnail(url=data["img"])

    # 説明
    embed.description = f"""
🔍 **検索ワード：** `{query}`
🎯 **マッチ：** {resolved}
"""

    # 価格情報
    flea = data.get("avg24hPrice")
    trader_name = data.get("traderName")
    trader_price = data.get("traderPrice")

    price_text = ""

    if flea:
        price_text += f"フリマ平均：**{flea:,}₽**\n"

    if trader_name and trader_price:
        price_text += f"{trader_name}：**{trader_price:,}₽**\n"

    # 差額
    if flea and trader_price:
        diff = flea - trader_price
        sign = "+" if diff >= 0 else "-"
        price_text += f"差額：**{sign}{abs(diff):,}₽**"

    embed.add_field(name="💰 価格情報", value=price_text, inline=False)

    # フッター（Twitch）
    embed.set_footer(text=f"Twitch → {TWITCH_URL}")

    await message.channel.send(embed=embed)


# ============================================
#  起動
# ============================================

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN が設定されていません。")

    load_all_item_names()  # 起動時にアイテム名を取得
    client.run(DISCORD_TOKEN)
