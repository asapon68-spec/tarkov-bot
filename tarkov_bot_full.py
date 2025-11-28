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
    print("警告: TARKOV_MARKET_API_KEY が設定されていません。価格データは取得不可になります")

# =========================
# API ENDPOINTS
# =========================
TARKOV_DEV_ITEMS_URL = "https://api.tarkov.dev/graphql"
TARKOV_MARKET_DETAILS_URL = "https://api.tarkov-market.app/api/v1/item/details/{}?x-api-key={}"

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

# =========================
# 日本語 → 英語 エイリアス
# =========================
ALIASES = {
    "レドックス": "LEDX Skin Transilluminator",
    "レドックススキン": "LEDX Skin Transilluminator",
    "グラボ": "Graphics card",
    "サレワ": "Salewa first aid kit",
    "グリズリー": "Grizzly first aid kit",
    "ガスアナ": "Gas analyzer",
    "ミリタリーフラッシュドライブ": "Secure Flash drive",
}

# =========================
# 全アイテム名をロード（tarkov.dev）
# =========================
def load_all_items():
    global ITEM_NAMES, ITEM_NAME_TO_ID

    query = """
    {
      items {
        id
        name
      }
    }
    """

    try:
        print("tarkov.dev から全アイテム取得中...")
        r = requests.post(TARKOV_DEV_ITEMS_URL, json={"query": query}, timeout=25)
        r.raise_for_status()

        data = r.json().get("data", {}).get("items", [])
        ITEM_NAMES = [item["name"] for item in data]
        ITEM_NAME_TO_ID = {item["name"]: item["id"] for item in data}

        print(f"ロード完了: {len(ITEM_NAMES)} アイテム")

    except Exception as e:
        print("全アイテム取得エラー:", e)
        ITEM_NAMES = []
        ITEM_NAME_TO_ID = {}


# =========================
# Fuzzy Match
# =========================
def fuzzy_match(user_input: str):
    ui = user_input.strip()

    # 日本語エイリアス優先
    if ui in ALIASES:
        return ALIASES[ui], 100

    if not ITEM_NAMES:
        return None, 0

    result = process.extractOne(ui, ITEM_NAMES, scorer=fuzz.WRatio)
    if result:
        name, score, _ = result
        return name, int(score)

    return None, 0


# =========================
# Tarkov Market 詳細API
# =========================
def get_item_details(item_id: str):
    if not TARKOV_MARKET_API_KEY:
        return None
    try:
        url = TARKOV_MARKET_DETAILS_URL.format(item_id, TARKOV_MARKET_API_KEY)
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("Tarkov-Market 詳細APIエラー:", e)
        return None


# =========================
# Discord BOT
# =========================
@client.event
async def on_ready():
    print(f"Bot 起動: {client.user}")
    load_all_items()


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    content = message.content.strip()

    # Help
    if content.lower() == "!help":
        await message.channel.send(
            "使い方：`!アイテム名`\n例：`!ledx`, `!グラボ`, `!サレワ`"
        )
        return

    # コマンドは "!" から始まる
    if not content.startswith("!"):
        return

    # 検索ワード抽出
    query = content[1:].strip()
    if not query:
        await message.channel.send("例：`!ledx` のように入力してください。")
        return

    # Fuzzy検索
    name, score = fuzzy_match(query)
    if not name:
        await message.channel.send("一致するアイテムが見つかりませんでした。")
        return

    if score < FUZZY_THRESHOLD:
        await message.channel.send(
            f"もしかして **{name}** (score {score})\n"
            "もっと近い名前で入力してみてください。"
        )
        return

    # ID取得
    item_id = ITEM_NAME_TO_ID.get(name)
    if not item_id:
        await message.channel.send("アイテムID取得に失敗しました。")
        return

    # 詳細取得
    data = get_item_details(item_id)
    if not data:
        await message.channel.send("詳細データ取得エラー。")
        return

    # ======== 価格情報 ========
    avg = data.get("avg24hPrice")
    trader = data.get("traderName") or "----"
    trader_price = data.get("traderPrice")

    def fmt(v):
        try:
            return f"{int(v):,}₽"
        except:
            return "----"

    avg_s = fmt(avg)
    trader_price_s = fmt(trader_price)

    # Profit
    try:
        if avg and trader_price:
            profit = avg - trader_price
            profit_s = f"{profit:+,}₽"
        else:
            profit_s = "----"
    except:
        profit_s = "----"

    # ======== Wiki URL ========
    wiki_url = data.get("wikiLink", None)

    # ======== EMBED ========
    embed = discord.Embed(
        title=name,
        url=wiki_url if wiki_url else discord.Embed.Empty,
        description=f"検索ワード: `{query}` / マッチ: `{name}` (score {score})",
        color=0x00AAFF
    )

    # アイテム画像
    icon = data.get("icon")
    if icon:
        embed.set_thumbnail(url=icon)

    # 価格情報
    embed.add_field(
        name="価格情報",
        value=(
            f"Flea Avg: {avg_s}\n"
            f"Trader: {trader}（{trader_price_s}）\n"
            f"Profit: {profit_s}"
        ),
        inline=False
    )

    # Footer
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
