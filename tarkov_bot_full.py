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
# APIエンドポイント
# =========================
TARKOV_DEV_ITEMS_URL = "https://api.tarkov.dev/graphql"
TARKOV_MARKET_DETAILS_URL = "https://api.tarkov-market.app/api/v1/item/details/{}?x-api-key={}"

# Discord intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# キャッシュ
ITEM_NAMES = []
ITEM_NAME_TO_ID = {}

# 日本語→英語のエイリアス（後から増やせる）
ALIASES = {
    "レドックス": "LEDX Skin Transilluminator",
    "グラボ": "Graphics card",
    "グリズリー": "Grizzly first aid kit",
    "サレワ": "Salewa first aid kit",
    "ガスアナ": "Gas analyzer",
    "ミリタリーフラッシュドライブ": "Secure Flash drive",
}


# =========================
# 全アイテム一覧（tarkov.dev）から取得
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

        print(f"全アイテムロード完了: {len(ITEM_NAMES)} 件")

    except Exception as e:
        print("アイテム一覧取得エラー:", e)
        ITEM_NAMES = []
        ITEM_NAME_TO_ID = {}


# =========================
# あいまい検索
# =========================
def fuzzy_match(user_input: str):
    ui = user_input.strip()

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
# Tarkov-Market 詳細APIで情報取得
# =========================
def get_item_details(item_id: str):
    try:
        url = TARKOV_MARKET_DETAILS_URL.format(item_id, TARKOV_MARKET_API_KEY)
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return r.json()
    except:
        return None


# =========================
# Discord Event
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

    if not content.startswith("!price"):
        return

    query = content[6:].strip()
    if not query:
        await message.channel.send("例：`!price ledx`")
        return

    # Fuzzy
    name, score = fuzzy_match(query)
    if not name:
        await message.channel.send("一致するアイテムが見つかりません。")
        return

    if score < FUZZY_THRESHOLD:
        await message.channel.send(
            f"もしかして: **{name}** (score {score})\nより正確に入力してください。"
        )
        return

    # ID取得
    item_id = ITEM_NAME_TO_ID.get(name)
    if not item_id:
        await message.channel.send("アイテムIDが取得できません。")
        return

    # 詳細データ取得
    data = get_item_details(item_id)
    if not data:
        await message.channel.send("詳細データ取得エラー。")
        return

    # --- 価格情報 ---
    avg = data.get("avg24hPrice", "取得不可")
    trader = data.get("traderName", "----")
    trader_price = data.get("traderPrice", "取得不可")

    # Profit自動計算
    try:
        profit = avg - trader_price
        profit_s = f"{profit:,}₽"
        if profit > 0:
            profit_s = f"+{profit_s}"
    except:
        profit_s = "----"

    # --- タスク/ハイドアウト ---
    quest_flag = "✅" if data.get("needForQuest") else "❌"
    hideout_flag = "✅" if data.get("needForHideout") else "❌"
    fir_flag = "❌"
    if "requireFIR" in data:
        fir_flag = "✅" if data["requireFIR"] else "❌"

    # --- Embed生成 ---
    embed = discord.Embed(
        title=name,
        description=f"検索ワード: `{query}` / マッチ: `{name}` (score {score})",
        color=0x00AAFF,
    )

    # アイテム画像
    if data.get("icon"):
        embed.set_thumbnail(url=data["icon"])

    # 価格情報
    embed.add_field(
        name="価格情報",
        value=(
            f"Flea Avg: {avg:,}₽\n"
            f"Trader: {trader}（{trader_price:,}₽）\n"
            f"Profit: {profit_s}"
        ),
        inline=False,
    )

    # Requirement
    embed.add_field(
        name="Requirement",
        value=(
            f"Quest: {quest_flag}\n"
            f"Hideout: {hideout_flag}\n"
            f"Find in Raid: {fir_flag}"
        ),
        inline=False,
    )

    # フッター（Tarkov-Market + Twitch誘導）
    footer_text = "Prices from Tarkov-Market (https://tarkov-market.com)"
    if TWITCH_URL:
        footer_text += f" | ✨ Follow my Twitch! → {TWITCH_URL} ✨"

    embed.set_footer(text=footer_text)

    await message.channel.send(embed=embed)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    load_all_items()
    client.run(DISCORD_TOKEN)
