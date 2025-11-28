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
TWITCH_URL = os.getenv("TWITCH_URL", "").strip()
FUZZY_THRESHOLD = int(os.getenv("FUZZY_THRESHOLD", "60"))

# =========================
# Tarkov APIエンドポイント
# =========================
TARKOV_DEV_ITEMS_URL = "https://api.tarkov.dev/graphql"
TARKOV_MARKET_ITEM_URL = "https://api.tarkov-market.app/api/v1/item?q={}&x-api-key={}"

# =========================
# Discord 設定
# =========================
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# =========================
# キャッシュ
# =========================
ITEM_NAMES = []
ITEM_NAME_TO_ID = {}

# 日本語→英語のエイリアス（必要に応じて後から追加）
ALIASES = {
    "レドックス": "LEDX Skin Transilluminator",
    "グラボ": "Graphics card",
    "グリズリー": "Grizzly first aid kit",
    "サレワ": "Salewa first aid kit",
    "ガスアナ": "Gas analyzer",
    "ミリタリーフラッシュドライブ": "Secure Flash drive",
}

# =========================
# 全アイテムをtarkov.devから取得
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
        r = requests.post(TARKOV_DEV_ITEMS_URL, json={"query": query}, timeout=20)
        r.raise_for_status()
        data = r.json()
        items = data.get("data", {}).get("items", [])

        ITEM_NAMES = [item["name"] for item in items]
        ITEM_NAME_TO_ID = {item["name"]: item["id"] for item in items}

        print(f"全アイテム読み込み完了: {len(ITEM_NAMES)} items")

    except Exception as e:
        print("アイテム一覧取得エラー:", e)
        ITEM_NAMES = []
        ITEM_NAME_TO_ID = {}


# =========================
# あいまい検索（日本語エイリアス→英語、なければ英語fuzzy）
# =========================
def fuzzy_match(user_input: str):
    ui = user_input.strip()

    # 日本語 alias 優先
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
# Tarkov-Market価格取得
# =========================
def get_price_from_tarkov_market(query_name: str):
    if not TARKOV_MARKET_API_KEY:
        return None
    try:
        url = TARKOV_MARKET_ITEM_URL.format(
            requests.utils.quote(query_name),
            TARKOV_MARKET_API_KEY
        )
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        return data[0]
    except:
        return None


# =========================
# Discord Events
# =========================
@client.event
async def on_ready():
    print(f"Bot 起動: {client.user}")
    load_all_items()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.strip()

    if content.lower().startswith("!price"):
        query = content[6:].strip()
        if not query:
            await message.channel.send("例：`!price ledx`")
            return

        # fuzzy match
        name, score = fuzzy_match(query)
        if not name:
            await message.channel.send("アイテム候補なし。")
            return

        if score < FUZZY_THRESHOLD:
            await message.channel.send(
                f"もしかして: **{name}** (類似度 {score})\n"
                "もう少し近い名前で入力してください。"
            )
            return

        # 価格
        price_data = get_price_from_tarkov_market(name)

        if price_data:
            avg = price_data.get("avg24hPrice") or price_data.get("price") or 0
            trader = price_data.get("traderName") or "----"
            trader_price = price_data.get("traderPrice") or 0
        else:
            avg = "取得不可"
            trader = "----"
            trader_price = "取得不可"

        # Embed
        embed = discord.Embed(
            title=name,
            description=f"検索ワード: `{query}` / マッチ: `{name}` (score {score})",
            color=0x00FFAA,
        )

        embed.add_field(
            name="価格情報",
            value=f"フリマ平均: {avg:,}₽\n{trader} 買取: {trader_price:,}₽",
            inline=False,
        )

        # ✨ フッター（Tarkov-Market + Twitch）
        footer_text = "Prices from Tarkov-Market (https://tarkov-market.com)"
        if TWITCH_URL:
            footer_text += f" | ✨ Follow my Twitch! → {TWITCH_URL} ✨"

        embed.set_footer(text=footer_text)

        await message.channel.send(embed=embed)


# =========================
# 実行
# =========================
if __name__ == "__main__":
    load_all_items()  # 念のため
    client.run(DISCORD_TOKEN)
