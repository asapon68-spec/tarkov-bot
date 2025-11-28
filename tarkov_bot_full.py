# =============================
# Escape from Tarkov Discord BOT
# 価格: Tarkov-Market API
# アイテム名: tarkov.dev + Fuzzy Search
# 日本語 & 略称対応
# =============================

import os
import requests
from dotenv import load_dotenv
from rapidfuzz import process, fuzz
import discord

# =============================
# 環境変数
# =============================
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
TARKOV_MARKET_API_KEY = os.getenv("TARKOV_MARKET_API_KEY", "").strip()
TWITCH_URL = os.getenv("TWITCH_URL", "https://www.twitch.tv/jagamiorochi").strip()
FUZZY_THRESHOLD = int(os.getenv("FUZZY_THRESHOLD", "60"))

if not DISCORD_TOKEN:
    raise SystemExit("❌ DISCORD_TOKEN が設定されていません")

# =============================
# APIエンドポイント（重要）
# =============================
TARKOV_DEV_URL = "https://api.tarkov.dev/graphql"
TARKOV_MARKET_URL = "https://tarkov-market.com/api/v1/item"  # ←これが正しい

# =============================
# Discord設定
# =============================
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# =============================
# キャッシュ
# =============================
ITEM_NAMES = []
ITEM_NAME_TO_WIKI = {}

# =============================
# 日本語・略称エイリアス
# =============================
ALIASES = {
    "ledx": "LEDX Skin Transilluminator",
    "レドックス": "LEDX Skin Transilluminator",
    "れどっくす": "LEDX Skin Transilluminator",

    "グラボ": "Graphics card",
    "gpu": "Graphics card",
    "ぐらぼ": "Graphics card",

    "ガスアナ": "Gas analyzer",
    "gas analyzer": "Gas analyzer",

    "サレワ": "Salewa first aid kit",
    "grizzly": "Grizzly medical kit",
    "フラッシュドライブ": "Secure Flash drive",
}

# =============================
# tarkov.dev から全アイテム読み込み
# =============================
def load_all_items():
    global ITEM_NAMES, ITEM_NAME_TO_WIKI

    query = """
    {
      items {
        id
        name
        wikiLink
      }
    }
    """
    try:
        print("tarkov.dev → アイテム一覧取得中…")
        r = requests.post(TARKOV_DEV_URL, json={"query": query}, timeout=20)
        r.raise_for_status()

        items = r.json()["data"]["items"]
        ITEM_NAMES = [i["name"] for i in items]
        ITEM_NAME_TO_WIKI = {i["name"]: i["wikiLink"] for i in items}

        print(f"ロード完了: {len(ITEM_NAMES)} items")

    except Exception as e:
        print("❌ tarkov.dev エラー:", e)


# =============================
# Fuzzy検索
# =============================
def fuzzy_match(user_input: str):
    s = user_input.lower().strip()
    if not s:
        return None, 0

    # ① エイリアス完全一致
    if s in ALIASES:
        return ALIASES[s], 100

    # ② エイリアスにFuzzy
    alias_keys = list(ALIASES.keys())
    alias_match = process.extractOne(s, alias_keys, scorer=fuzz.WRatio)
    if alias_match and alias_match[1] >= 85:
        return ALIASES[alias_match[0]], alias_match[1]

    # ③ 英語正式名にFuzzy
    match = process.extractOne(user_input, ITEM_NAMES, scorer=fuzz.WRatio)
    if match:
        return match[0], match[1]

    return None, 0


# =============================
# Tarkov Market 価格API
# =============================
def get_price_data(name: str):
    if not TARKOV_MARKET_API_KEY:
        return None

    try:
        headers = {"x-api-key": TARKOV_MARKET_API_KEY}
        params = {"q": name}

        r = requests.get(TARKOV_MARKET_URL, headers=headers, params=params, timeout=15)
        r.raise_for_status()

        data = r.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0]

        return None

    except Exception as e:
        print("❌ Tarkov-Market API エラー:", e)
        return None


# =============================
# Discord BOT イベント
# =============================
@client.event
async def on_ready():
    print(f"BOT起動: {client.user}")
    load_all_items()


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

    # Fuzzy検索
    name, score = fuzzy_match(query)
    if not name:
        await message.channel.send(f"❌ `{query}` のアイテムが見つかりませんでした…")
        return

    # しきい値チェック
    if score < FUZZY_THRESHOLD:
        await message.channel.send(
            f"❓ もしかして **{name}** ? (score {score})"
        )
        return

    # 価格情報取得
    price = get_price_data(name)
    if not price:
        await message.channel.send("❌ 価格情報が取得できませんでした。")
        return

    # --- 表示整形 ---
    avg = price.get("avg24hPrice")
    trader = price.get("traderName") or "----"
    trader_price = price.get("traderPrice")
    icon = price.get("icon")

    wiki = ITEM_NAME_TO_WIKI.get(name)

    def fmt(v):
        try:
            return f"{int(v):,}₽"
        except:
            return "----"

    # 差額
    try:
        if avg and trader_price:
            diff = int(avg) - int(trader_price)
            diff_s = f"{diff:+,}₽"
        else:
            diff_s = "----"
    except:
        diff_s = "----"

    # Embed
    embed = discord.Embed(
        title=name,
        url=wiki if wiki else discord.Embed.Empty,
        description=f"🔍 検索: `{query}`\n🎯 マッチ: `{name}` (score {score})",
        color=0x00AAFF,
    )

    if icon:
        embed.set_thumbnail(url=icon)

    embed.add_field(
        name="💰 価格情報",
        value=(
            f"フリマ平均: **{fmt(avg)}**\n"
            f"トレーダー最高買取: **{trader}（{fmt(trader_price)}）**\n"
            f"差額: **{diff_s}**"
        ),
        inline=False,
    )

    embed.set_footer(
        text=f"Prices via Tarkov-Market | Twitch → {TWITCH_URL}"
    )

    await message.channel.send(embed=embed)


# =============================
# 起動
# =============================
if __name__ == "__main__":
    load_all_items()
    client.run(DISCORD_TOKEN)
