import os
import requests
from dotenv import load_dotenv
from rapidfuzz import process, fuzz
import discord

# =========================
# 環境変数読み込み
# =========================
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
TARKOV_MARKET_API_KEY = os.getenv("TARKOV_MARKET_API_KEY", "").strip()
TWITCH_URL = os.getenv("TWITCH_URL", "https://www.twitch.tv/jagamiorochi").strip()
FUZZY_THRESHOLD = int(os.getenv("FUZZY_THRESHOLD", "60"))  # 類似度しきい値

if not DISCORD_TOKEN:
    raise SystemExit("DISCORD_TOKEN が設定されていません（Render環境変数を確認）")

if not TARKOV_MARKET_API_KEY:
    print("警告: TARKOV_MARKET_API_KEY が設定されていません → 価格データ取得不可")

# =========================
# API ENDPOINTS（正しい本家API）
# =========================
TARKOV_DEV_URL = "https://api.tarkov.dev/graphql"
TARKOV_MARKET_URL = "https://tarkov-market.com/api/v1/item"

# =========================
# Discord Settings
# =========================
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# =========================
# Cache
# =========================
ITEM_NAMES = []
ITEM_NAME_TO_WIKI = {}

# =========================
# 日本語・略称 → 英語名 辞書
# =========================
ALIASES = {
    "レドックス": "LEDX Skin Transilluminator",
    "れどっくす": "LEDX Skin Transilluminator",
    "ledx": "LEDX Skin Transilluminator",

    "グラボ": "Graphics card",
    "ぐらぼ": "Graphics card",
    "gpu": "Graphics card",

    "フラッシュドライブ": "Secure Flash drive",
    "flash drive": "Secure Flash drive",

    "ガスアナ": "Gas analyzer",
    "がすあな": "Gas analyzer",

    "マークドキー": "Marked key",
    "marked key": "Marked key",

    "m4": "Colt M4A1 5.56x45 assault rifle",
    "m4a1": "Colt M4A1 5.56x45 assault rifle",

    "mp7": "HK MP7A2 4.6x30 submachine gun",
    "mp7a2": "HK MP7A2 4.6x30 submachine gun",

    "m995": "5.56x45 mm M995",
    "7n39": "5.45x39 mm 7N39 Igolnik",
}

# =========================
# tarkov.dev から全アイテム一覧取得
# =========================
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
        print("tarkov.dev アイテム一覧取得中...")
        r = requests.post(TARKOV_DEV_URL, json={"query": query}, timeout=25)
        r.raise_for_status()

        items = r.json().get("data", {}).get("items", [])

        ITEM_NAMES = [item["name"] for item in items]
        ITEM_NAME_TO_WIKI = {item["name"]: item["wikiLink"] for item in items}

        print(f"ロード成功: {len(ITEM_NAMES)} アイテム取得")

    except Exception as e:
        print("tarkov.dev アイテム取得エラー:", e)
        ITEM_NAMES = []
        ITEM_NAME_TO_WIKI = {}


# =========================
# Fuzzy match + alias
# =========================
def fuzzy_match(user_input: str):
    raw = user_input.strip()
    if not raw:
        return None, 0

    lowered = raw.lower()

    # 1) エイリアス完全一致
    if lowered in ALIASES:
        return ALIASES[lowered], 100

    # 2) エイリアス fuzzy
    alias_keys = list(ALIASES.keys())
    alias_match = process.extractOne(lowered, alias_keys, scorer=fuzz.WRatio)
    if alias_match:
        alias_key, alias_score, _ = alias_match
        if alias_score >= 80:
            return ALIASES[alias_key], alias_score

    # 3) 英語正式名 fuzzy
    if ITEM_NAMES:
        match = process.extractOne(raw, ITEM_NAMES, scorer=fuzz.WRatio)
        if match:
            name, score, _ = match
            return name, score

    return None, 0


# =========================
# Tarkov-Market 本家 API で価格取得（完全版）
# =========================
def get_price_data(name: str):
    if not TARKOV_MARKET_API_KEY:
        return None
    try:
        headers = {"x-api-key": TARKOV_MARKET_API_KEY}
        params = {"q": name}

        r = requests.get(TARKOV_MARKET_URL, headers=headers, params=params, timeout=20)
        r.raise_for_status()

        data = r.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0]

        return None

    except Exception as e:
        print("Tarkov-Market API エラー:", e)
        return None


# =========================
# Discord BOT
# =========================
@client.event
async def on_ready():
    print(f"Bot起動: {client.user}")
    load_all_items()


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    content = message.content.strip()

    # help
    if content.lower() == "!help":
        await message.channel.send(
            "使い方：`!アイテム名`\n例：`!ledx`, `!グラボ`, `!flash drive`, `!m4a1`"
        )
        return

    # "!" 以外無視
    if not content.startswith("!"):
        return

    query = content[1:].strip()
    if not query:
        await message.channel.send("例：`!ledx` のように入力してください。")
        return

    # fuzzy + alias
    name, score = fuzzy_match(query)

    if not name:
        await message.channel.send(f"❌ `{query}`に一致するアイテムがありません。")
        return

    if score < FUZZY_THRESHOLD:
        await message.channel.send(f"🤔 もしかして **{name}**？ (score {score})")
        return

    # 価格情報取得
    price = get_price_data(name)
    if not price:
        await message.channel.send("❌ 価格情報が取得できませんでした。")
        return

    # Tarkov-Market フィールド
    avg = price.get("avg24hPrice")
    trader = price.get("traderName")
    trader_price = price.get("traderPrice")
    icon = price.get("icon")

    def fmt(v):
        try:
            return f"{int(v):,}₽"
        except:
            return "----"

    avg_s = fmt(avg)
    trader_price_s = fmt(trader_price)

    # 差額
    profit_s = "----"
    try:
        if isinstance(avg, (int, float)) and isinstance(trader_price, (int, float)):
            p = avg - trader_price
            profit_s = f"{p:+,}₽"
    except:
        pass

    wiki = ITEM_NAME_TO_WIKI.get(name)

    # =========================
    # Embed
    # =========================
    embed = discord.Embed(
        title=name,
        url=wiki if wiki else discord.Embed.Empty,
        description=f"🔍検索: `{query}`\n🎯マッチ: **{name}** (score {score})",
        color=0x00AAFF,
    )

    if icon:
        embed.set_thumbnail(url=icon)

    embed.add_field(
        name="💰 価格情報",
        value=(
            f"フリマ平均: **{avg_s}**\n"
            f"トレーダー: **{trader}（{trader_price_s}）**\n"
            f"差額: **{profit_s}**"
        ),
        inline=False,
    )

    footer = "Prices from Tarkov-Market"
    if TWITCH_URL:
        footer += f" | ✨ Twitch → {TWITCH_URL}"
    embed.set_footer(text=footer)

    await message.channel.send(embed=embed)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    load_all_items()
    client.run(DISCORD_TOKEN)
