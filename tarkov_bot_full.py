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

ITEM_JSON_URL = "https://raw.githubusercontent.com/asapon68-spec/tarkov-bot/main/items.json"
ALIAS_JSON_URL = "https://raw.githubusercontent.com/asapon68-spec/tarkov-bot/main/alias.json"

FUZZY_THRESHOLD = 60
MAX_RESULTS = 10  # ← 最大10件候補表示

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
# 数字2桁以下は無視（仕様）
# =========================
def is_too_short_numeric(query):
    return query.isdigit() and len(query) <= 2


# =========================
# アイテム検索（複数候補）
# =========================
def search_items(query):
    q = query.lower()
    results = []

    # --- 数字1〜2桁はヒットなし ---
    if is_too_short_numeric(q):
        return []

    # --- 1) alias 完全一致ヒット ---
    alias_hits = []
    for real_name, aliases in ALIAS_DB.items():
        if q in [a.lower() for a in aliases]:
            alias_hits.append(real_name)

    if alias_hits:
        return alias_hits[:MAX_RESULTS]

    # --- 2) items.json 内の部分一致 ---
    partial = [name for name in ITEM_NAMES if q in name.lower()]
    if partial:
        return partial[:MAX_RESULTS]

    # --- 3) fuzzy search fallback（複数candidate） ---
    fuzzy = process.extract(q, ITEM_NAMES, scorer=fuzz.WRatio, limit=MAX_RESULTS)
    fuzzy_hits = [name for name, score, _ in fuzzy if score >= FUZZY_THRESHOLD]

    return fuzzy_hits


# =========================
# Discord BOT
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

    # ------------------------
    # 検索
    # ------------------------
    hits = search_items(query)

    if not hits:
        await message.channel.send(f"❌ `{query}` に一致するアイテムがありませんでした。")
        return

    # ------------------------
    # 候補が複数の場合
    # ------------------------
    if len(hits) > 1:
        text = "🔍 **複数候補が見つかりました**\n"
        for i, name in enumerate(hits, 1):
            text += f"**{i}.** {name}\n"
        text += "\n👉 **もっと絞って入力してね！**"
        await message.channel.send(text)
        return

    # ------------------------
    # 1件だけ
    # ------------------------
    item_name = hits[0]
    item = ITEM_DB[item_name]

    embed = discord.Embed(
        title=item_name,
        description=f"🔍 検索： `{query}`\n🎯 実クエリ： `{item_name}`",
        color=0x00AAFF,
    )

    trader_info = item.get("trader_price")
    trader_text = "----"

    if isinstance(trader_info, dict) and trader_info:
        tn = list(trader_info.keys())[0]
        tp = trader_info[tn]
        trader_text = f"{tn}: {tp:,}₽"

    embed.add_field(name="💰 買取価格", value=trader_text, inline=False)

    embed.add_field(
        name="📌 その他",
        value=f"タスク必要： {item.get('task')}\nハイドアウト必要： {item.get('hideout')}",
        inline=False,
    )

    embed.add_field(
        name="",
        value=f"[✨ FOLLOW 蛇神オロチ ON TWITCH ✨]({TWITCH_URL})",
        inline=False,
    )

    await message.channel.send(embed=embed)


# =========================
# RUN
# =========================
client.run(DISCORD_TOKEN)
