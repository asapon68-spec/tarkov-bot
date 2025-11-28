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

# ★ 修正：正しい Twitch URL に変更
TWITCH_URL = os.getenv("TWITCH_URL", "https://www.twitch.tv/jagami_orochi").strip()

FUZZY_THRESHOLD = int(os.getenv("FUZZY_THRESHOLD", "60"))

if not DISCORD_TOKEN:
    raise SystemExit("❌ DISCORD_TOKEN が設定されていません")

# =========================
# API ENDPOINTS
# =========================
TARKOV_DEV_URL = "https://api.tarkov.dev/graphql"
TARKOV_MARKET_SEARCH_URL = "https://api.tarkov-market.app/api/v1/item?q={}&x-api-key={}"

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
# 日本語・略称エイリアス
# =========================
ALIASES = {
    "レドックス": "LEDX Skin Transilluminator",
    "れどっくす": "LEDX Skin Transilluminator",
    "ledx": "LEDX Skin Transilluminator",
    "グラボ": "Graphics card",
    "gpu": "Graphics card",
    "ぐらぼ": "Graphics card",
    "salewa": "Salewa first aid kit",
    "サレワ": "Salewa first aid kit",
    "されわ": "Salewa first aid kit",
}

# =========================
# tarkov.dev から全アイテム取得
# =========================
def load_all_items():
    global ITEM_NAMES, ITEM_NAME_TO_WIKI

    query = """
    {
      items {
        name
        wikiLink
      }
    }
    """

    try:
        print("📦 tarkov.dev アイテム一覧取得中...")
        r = requests.post(TARKOV_DEV_URL, json={"query": query}, timeout=20)
        r.raise_for_status()

        items = r.json()["data"]["items"]
        ITEM_NAMES = [item["name"] for item in items]
        ITEM_NAME_TO_WIKI = {item["name"]: item["wikiLink"] for item in items}

        print(f"✅ {len(ITEM_NAMES)} アイテムロード完了")

    except Exception as e:
        print("❌ アイテム一覧取得エラー:", e)
        ITEM_NAMES = []
        ITEM_NAME_TO_WIKI = {}

# =========================
# Fuzzy + Alias マッチ
# =========================
def fuzzy_match(query: str):
    q = query.strip().lower()
    results = []

    # 1) 完全エイリアス一致
    if q in ALIASES:
        return [(ALIASES[q], 100)]

    # 2) エイリアス fuzzy
    alias_keys = list(ALIASES.keys())
    for a, score, _ in process.extract(q, alias_keys, scorer=fuzz.WRatio, limit=3):
        if score >= 85:
            results.append((ALIASES[a], int(score)))

    # 3) 英語正式名 fuzzy
    if ITEM_NAMES:
        for name, score, _ in process.extract(query, ITEM_NAMES, scorer=fuzz.WRatio, limit=5):
            results.append((name, int(score)))

    # 重複除去 & スコア順
    uniq = {}
    for name, score in results:
        if name not in uniq or score > uniq[name]:
            uniq[name] = score

    sorted_results = sorted(uniq.items(), key=lambda x: x[1], reverse=True)
    return [(name, s) for name, s in sorted_results if s >= FUZZY_THRESHOLD]

# =========================
# Tarkov-Market：価格取得
# =========================
def get_price_data(name):
    try:
        url = TARKOV_MARKET_SEARCH_URL.format(requests.utils.quote(name), TARKOV_MARKET_API_KEY)
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        return data[0] if data else None
    except Exception as e:
        print("❌ Tarkov-Market API エラー:", e)
        return None

# =========================
# Discord BOT
# =========================
@client.event
async def on_ready():
    print(f"🚀 BOT起動: {client.user}")
    load_all_items()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.strip()

    if not content.startswith("!"):
        return

    query = content[1:].strip()
    if not query:
        return

    matches = fuzzy_match(query)
    if not matches:
        await message.channel.send(f"❌ `{query}` に一致なし")
        return

    name, score = matches[0]
    price = get_price_data(name)

    if not price:
        await message.channel.send("❌ 価格情報が取得できませんでした")
        return

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

    profit = "----"
    try:
        profit = f"{avg - trader_price:+,}₽"
    except:
        pass

    embed = discord.Embed(
        title=name,
        url=wiki if wiki else discord.Embed.Empty,
        description=f"🔍 検索：`{query}`\n🎯 マッチ：`{name}`",
        color=0x00AAFF,
    )

    if icon:
        embed.set_thumbnail(url=icon)

    embed.add_field(
        name="💰 価格情報",
        value=(
            f"フリマ平均：**{fmt(avg)}**\n"
            f"トレーダー最高買取：**{trader}（{fmt(trader_price)}）**\n"
            f"差額：**{profit}**"
        ),
        inline=False,
    )

    embed.set_footer(text="Prices from Tarkov-Market")

    # Twitchボタン
    view = discord.ui.View()
    follow_button = discord.ui.Button(
        label="✨ FOLLOW 蛇神オロチ ON TWITCH ✨",
        url=TWITCH_URL,
        style=discord.ButtonStyle.url
    )
    view.add_item(follow_button)

    await message.channel.send(embed=embed, view=view)

# =========================
# RUN
# =========================
if __name__ == "__main__":
    load_all_items()
    client.run(DISCORD_TOKEN)
