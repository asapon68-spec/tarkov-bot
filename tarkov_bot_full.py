import os
import json
import discord
import requests
from rapidfuzz import process, fuzz

# =========================
# 設定
# =========================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
TWITCH_URL = os.getenv("TWITCH_URL", "https://www.twitch.tv/jagami_orochi")
FUZZY_THRESHOLD = 60

ITEM_JSON_URL = "https://raw.githubusercontent.com/asapon68-spec/tarkov-bot/main/items.json"
ALIAS_JSON_URL = "https://raw.githubusercontent.com/asapon68-spec/tarkov-bot/main/alias.json"

if not DISCORD_TOKEN:
    raise SystemExit("❌ DISCORD_TOKEN が設定されていません")


# =========================
# GitHub JSON Loader
# =========================
def load_json(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("❌ JSON読み込みエラー:", e)
        return {}


ITEM_DB = load_json(ITEM_JSON_URL)
ALIAS_DB = load_json(ALIAS_JSON_URL)

ITEM_NAMES = list(ITEM_DB.keys())


# =========================
# アイテム検索処理（alias優先）
# =========================
def find_item(query):
    q = query.lower()

    # 1) alias search first
    for real_name, aliases in ALIAS_DB.items():
        if q in [a.lower() for a in aliases]:
            return real_name

    # 2) fuzzy search fallback
    result = process.extract(q, ITEM_NAMES, scorer=fuzz.WRatio, limit=1)
    best_name, score, _ = result[0]
    if score >= FUZZY_THRESHOLD:
        return best_name

    return None


# =========================
# Discord BOT設定
# =========================
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"🚀 BOT起動: {client.user}")


@client.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip()
    if not content.startswith("!"):
        return

    query = content[1:].strip()
    if not query:
        return

    item_name = find_item(query)
    if not item_name:
        await message.channel.send(f"❌ `{query}` に一致するアイテムがありませんでした。")
        return

    item = ITEM_DB[item_name]

    embed = discord.Embed(
        title=item_name,
        description=f"🔍 検索： `{query}`\n🎯 実クエリ： `{item_name}`",
        color=0x00AAFF,
    )

    trader_info = item.get("trader_price")
    trader_text = "----"

    if isinstance(trader_info, dict):
        tn = list(trader_info.keys())[0]
        tp = trader_info[tn]
        trader_text = f"{tn}: {tp:,}₽"

    embed.add_field(
        name="💰 買取価格",
        value=f"{trader_text}",
        inline=False,
    )

    embed.add_field(
        name="📌 その他",
        value=(
            f"タスク必要： {item.get('task')}\n"
            f"ハイドアウト必要： {item.get('hideout')}"
        ),
        inline=False,
    )

    embed.add_field(
        name="🔗 Twitch",
        value=f"[CLICK HERE]({TWITCH_URL})",
        inline=False
    )

    await message.channel.send(embed=embed)


# =========================
# RUN
# =========================
client.run(DISCORD_TOKEN)
