import os
import requests
from dotenv import load_dotenv
from rapidfuzz import process, fuzz
import discord

# =========================
# Load ENV
# =========================
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
TARKOV_MARKET_API_KEY = os.getenv("TARKOV_MARKET_API_KEY", "").strip()
TWITCH_URL = os.getenv("TWITCH_URL", "").strip()
FUZZY_THRESHOLD = int(os.getenv("FUZZY_THRESHOLD", "60"))

if not DISCORD_TOKEN:
    raise SystemExit("DISCORD_TOKEN が設定されていません")

if not TARKOV_MARKET_API_KEY:
    print("警告: TARKOV_MARKET_API_KEY がありません → 価格データ取得不可")

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
ITEM_NAME_TO_ID = {}
ITEM_NAME_TO_WIKI = {}

# =========================
# 日本語エイリアス
# =========================
ALIASES = {
    "グラボ": "Graphics card",
    "レドックス": "LEDX Skin Transilluminator",
    "サレワ": "Salewa first aid kit",
    "グリズリー": "Grizzly first aid kit",
    "ガスアナ": "Gas analyzer",
    "ミリタリーフラッシュドライブ": "Secure Flash drive",
}

# =========================
# tarkov.dev から全アイテム + Wikiリンク取得
# =========================
def load_all_items():
    global ITEM_NAMES, ITEM_NAME_TO_ID, ITEM_NAME_TO_WIKI

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
        ITEM_NAME_TO_ID = {item["name"]: item["id"] for item in items}
        ITEM_NAME_TO_WIKI = {item["name"]: item.get("wikiLink") for item in items}

        print(f"ロード成功: {len(ITEM_NAMES)} アイテム")

    except Exception as e:
        print("アイテム一覧取得エラー:", e)
        ITEM_NAMES = []
        ITEM_NAME_TO_ID = {}
        ITEM_NAME_TO_WIKI = {}

# =========================
# Fuzzy Match
# =========================
def fuzzy_match(text: str):
    t = text.strip()

    # 日本語エイリアス優先
    if t in ALIASES:
        return ALIASES[t], 100

    if not ITEM_NAMES:
        return None, 0

    match = process.extractOne(t, ITEM_NAMES, scorer=fuzz.WRatio)
    if match:
        name, score, _ = match
        return name, int(score)

    return None, 0

# =========================
# Tarkov Market (通常API)
# =========================
def get_price_data(name: str):
    try:
        url = TARKOV_MARKET_SEARCH_URL.format(requests.utils.quote(name), TARKOV_MARKET_API_KEY)
        r = requests.get(url, timeout=20)
        r.raise_for_status()

        data = r.json()
        if not data:
            return None

        return data[0]

    except Exception as e:
        print("TarkovMarket 通常APIエラー:", e)
        return None

# =========================
# BOT動作
# =========================
@client.event
async def on_ready():
    print(f"Bot起動: {client.user}")
    load_all_items()

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    content = message.content.strip()

    # help
    if content.lower() == "!help":
        await message.channel.send(
            "使い方：`!アイテム名`\n例：`!ledx`, `!グラボ`, `!サレワ`"
        )
        return

    # commands
    if not content.startswith("!"):
        return

    query = content[1:].strip()
    if not query:
        await message.channel.send("例：`!ledx` のように入力してください")
        return

    # fuzzy match
    name, score = fuzzy_match(query)
    if not name:
        await message.channel.send("一致するアイテムが見つかりません")
        return

    if score < FUZZY_THRESHOLD:
        await message.channel.send(
            f"もしかして **{name}** ？ (score {score})\nもっと近い名前で再入力してください。"
        )
        return

    # price data
    price = get_price_data(name)
    if not price:
        await message.channel.send("価格情報が取得できませんでした。")
        return

    # price fields
    avg = price.get("avg24hPrice")
    trader = price.get("traderName") or "----"
    trader_price = price.get("traderPrice")
    icon = price.get("icon")

    def fmt(v):
        try:
            return f"{int(v):,}₽"
        except:
            return "----"

    avg_s = fmt(avg)
    trader_price_s = fmt(trader_price)

    # profit
    try:
        if avg and trader_price:
            profit = avg - trader_price
            profit_s = f"{profit:+,}₽"
        else:
            profit_s = "----"
    except:
        profit_s = "----"

    # wiki url from tarkov.dev
    wiki = ITEM_NAME_TO_WIKI.get(name)

    # embed
    embed = discord.Embed(
        title=name,
        url=wiki if wiki else discord.Embed.Empty,
        description=f"検索: `{query}` / マッチ: `{name}` (score {score})",
        color=0x00AAFF
    )

    # item icon
    if icon:
        embed.set_thumbnail(url=icon)

    embed.add_field(
        name="価格情報",
        value=(
            f"Flea Avg: {avg_s}\n"
            f"Trader: {trader}（{trader_price_s}）\n"
            f"Profit: {profit_s}"
        ),
        inline=False
    )

    # footer
    footer = "Prices from Tarkov-Market (https://tarkov-market.com)"
    if TWITCH_URL:
        footer += f" | ✨ Follow my Twitch! → {TWITCH_URL} ✨"
    embed.set_footer(text=footer)

    await message.channel.send(embed=embed)

# =========================
# RUN
# =========================
if __name__ == "__main__":
    load_all_items()
    client.run(DISCORD_TOKEN)
