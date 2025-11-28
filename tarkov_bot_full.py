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

if not DISCORD_TOKEN:
    raise SystemExit("DISCORD_TOKEN が設定されていません")

# =========================
# APIエンドポイント
# =========================
# 軽量で安定。全アイテムの "name" と "id" を取得できる。
TARKOV_DEV_ITEMS_URL = "https://api.tarkov.dev/graphql"

TARKOV_MARKET_ITEM_URL = "https://api.tarkov-market.app/api/v1/item?q={}&x-api-key={}"

# Discord Intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 全アイテムキャッシュ
ITEM_NAMES = []
ITEM_NAME_TO_ID = {}


# =========================
# 全アイテム取得（安定版）
# =========================
def load_all_items():
    """
    tarkov.dev から全アイテム名とIDを取得する（軽いクエリ）
    """
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
# あいまい検索
# =========================
def fuzzy_match(user_input: str):
    if not ITEM_NAMES:
        return None, 0
    result = process.extractOne(user_input, ITEM_NAMES, scorer=fuzz.WRatio)
    if result:
        name, score, _ = result
        return name, int(score)
    return None, 0


# =========================
# 価格取得（Tarkov Market）
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
        j = r.json()
        if not j:
            return None
        return j[0]
    except:
        return None


# =========================
# Discord イベント
# =========================
@client.event
async def on_ready():
    print(f"Bot 起動: {client.user}")
    load_all_items()  # ⚡ 全アイテム自動読み込み


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.strip()

    if content.lower().startswith("!price"):
        query = content[6:].strip()
        if not query:
            await message.channel.send("例：`!price LEDX`")
            return

        # 1) fuzzy match
        name, score = fuzzy_match(query)
        if not name:
            await message.channel.send("アイテム候補が見つかりませんでした。")
            return

        if score < FUZZY_THRESHOLD:
            await message.channel.send(
                f"もしかして: **{name}** (類似度 {score})\nもう少し正確に入力してください。"
            )
            return

        # 2) 価格取得
        price_data = get_price_from_tarkov_market(name)

        if price_data:
            avg = price_data.get("avg24hPrice") or price_data.get("price") or 0
            trader = price_data.get("traderName") or "----"
            trader_price = price_data.get("traderPrice") or 0
        else:
            avg = "取得不可"
            trader = "----"
            trader_price = "取得不可"

        # 3) Embed出力
        embed = discord.Embed(
            title=name,
            description=f"検索ワード: `{query}` / マッチ: `{name}` (score {score})",
            color=0x00FF00,
        )
        embed.add_field(
            name="価格情報",
            value=f"フリマ平均: {avg:,}₽\n{trader} 買取: {trader_price:,}₽",
            inline=False,
        )

        # Footer with Tarkov-Market attribution + Twitch follow request (sparkle version)
footer_text = "Prices from Tarkov-Market (https://tarkov-market.com)"
if TWITCH_URL:
    footer_text += f" | ✨ Follow my Twitch! → {TWITCH_URL} ✨"

embed.set_footer(text=footer_text)

        await message.channel.send(embed=embed)


# =========================
# 実行
# =========================
if __name__ == "__main__":
    load_all_items()  # ←念のため実行（on_readyが動かない環境でも安全）
    client.run(DISCORD_TOKEN)
