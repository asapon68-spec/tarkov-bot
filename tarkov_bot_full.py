import os
import json
import discord
import requests
from rapidfuzz import process, fuzz

# ================================
# 設定
# ================================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
TWITCH_URL = os.getenv("TWITCH_URL", "https://www.twitch.tv/jagami_orochi")
ITEM_JSON_URL = os.getenv(
    "ITEM_JSON_URL",
    "https://raw.githubusercontent.com/asapon68-spec/tarkov-bot/main/items.json"
)

ALIAS_JSON_URL = "https://raw.githubusercontent.com/asapon68-spec/tarkov-bot/main/alias.json"

FUZZY_THRESHOLD = 25  # 曖昧検索の許容値（低いほど拾いやすい）

if not DISCORD_TOKEN:
    raise SystemExit("❌ DISCORD_TOKEN が設定されていません")


# ================================
# JSON ロード
# ================================
def load_items():
    try:
        print("📦 GitHubから items.json 読み込み中...")
        r = requests.get(ITEM_JSON_URL, timeout=10)
        r.raise_for_status()
        print("✅ items.json 読み込み成功")
        return r.json()
    except Exception as e:
        print("❌ items.json読み込みエラー:", e)
        return {}


def load_alias():
    try:
        print("📦 GitHubから alias.json 読み込み中...")
        r = requests.get(ALIAS_JSON_URL, timeout=10)
        r.raise_for_status()
        print("👍 alias.json 読み込み成功")
        return r.json()
    except Exception as e:
        print("⚠ alias.json読み込みエラー:", e)
        return {}


ITEM_DB = load_items()
ITEM_NAMES = list(ITEM_DB.keys())
ALIAS = load_alias()


# ================================
# Fuzzy検索
# ================================
def fuzzy_match(query):
    result = process.extract(query, ITEM_NAMES, scorer=fuzz.WRatio, limit=5)
    return [(name, score) for name, score, _ in result if score >= FUZZY_THRESHOLD]


# ================================
# Discord クライアント
# ================================
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

    query = content[1:].strip().lower()

    # ================================
    # alias置換処理
    # ================================
    for official_name, aliases in ALIAS.items():
        if query in [a.lower() for a in aliases]:
            print(f"🔁 Alias変換: {query} -> {official_name}")
            query = official_name.lower()
            break

    # ================================
    # fuzzy検索
    # ================================
    matches = fuzzy_match(query)

    if not matches:
        # 候補提示
        suggestions = process.extract(query, ITEM_NAMES, scorer=fuzz.WRatio, limit=3)
        text = "\n".join([f"{i+1}. {s[0]}" for i, s in enumerate(suggestions)])
        await message.channel.send(
            f"❓ `{query}` に完全一致はありませんでした。\n\n"
            f"📌 もしかして？\n{text}"
        )
        return

    best_name, score = matches[0]
    item = ITEM_DB[best_name]

    # ================================
    # trader price表示
    # ================================
    trader_text = "----"
    if isinstance(item.get("trader_price"), dict):
        trader_text = "\n".join(
            f"{name}: {int(price):,}₽" for name, price in item["trader_price"].items()
        )

    # ================================
    # Embed生成
    # ================================
    embed = discord.Embed(
        title=best_name,
        url=item.get("wiki", ""),
        description=f"🔍 検索： `{content[1:]}`\n🎯 実クエリ： `{best_name}`",
        color=0x00AAFF,
    )

    if item.get("icon"):
        embed.set_thumbnail(url=item["icon"])

    embed.add_field(name="💰 買取価格", value=trader_text, inline=False)
    embed.add_field(
        name="📌 その他",
        value=(
            f"タスク必要： **{item.get('task', '❌')}**\n"
            f"ハイドアウト必要： **{item.get('hideout', '❌')}**"
        ),
        inline=False,
    )

    embed.add_field(
        name="🔗 Twitch",
        value=f"[CLICK HERE]({TWITCH_URL})",
        inline=False,
    )

    embed.set_footer(text="✨ FOLLOW ME ON TWITCH ✨")

    await message.channel.send(embed=embed)


# ================================
# RUN
# ================================
client.run(DISCORD_TOKEN)
