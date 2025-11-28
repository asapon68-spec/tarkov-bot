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
    raise SystemExit("❌ DISCORD_TOKEN が設定されていません")

if not TARKOV_MARKET_API_KEY:
    print("⚠️ TARKOV_MARKET_API_KEY がありません → 価格データ取得不可になります")

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
ITEM_NAMES = []               # 英語正式名のリスト
ITEM_NAME_TO_ID = {}          # 拡張用
ITEM_NAME_TO_WIKI = {}        # Wikiリンク


# =========================
#  日本語・略称エイリアス辞書
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
#  tarkov.dev：全アイテムロード
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
        print("📦 tarkov.dev アイテム一覧取得中...")
        r = requests.post(TARKOV_DEV_URL, json={"query": query}, timeout=25)
        r.raise_for_status()

        items = r.json().get("data", {}).get("items", [])

        ITEM_NAMES = [item["name"] for item in items]
        ITEM_NAME_TO_ID = {item["name"]: item["id"] for item in items}
        ITEM_NAME_TO_WIKI = {item["name"]: item.get("wikiLink") for item in items}

        print(f"✅ ロード成功: {len(ITEM_NAMES)} アイテム")

    except Exception as e:
        print("❌ アイテム一覧取得エラー:", e)
        ITEM_NAMES = []
        ITEM_NAME_TO_ID = {}
        ITEM_NAME_TO_WIKI = {}


# =========================
#  Fuzzy + Alias マッチ
# =========================
def fuzzy_match(user_input: str):
    ui_raw = user_input.strip()
    if not ui_raw:
        return []

    ui = ui_raw.lower()
    matches = []

    # 1) 完全エイリアス一致
    if ui in ALIASES:
        # 完全一致が最優先なので、それをリストに入れて即座に返します
        return [(ALIASES[ui], 100)] 

    # 2) エイリアスの fuzzy (スコア85以上)
    alias_keys = list(ALIASES.keys())
    alias_matches = process.extract(ui, alias_keys, scorer=fuzz.WRatio, limit=3)
    for alias_key, alias_score, _ in alias_matches:
        if alias_score >= 85:
            # 既にリストに含まれていないか確認してから追加
            official_name = ALIASES[alias_key]
            if official_name not in [m[0] for m in matches]:
                matches.append((official_name, int(alias_score)))
    
    # 3) 英語正式名に fuzzy (常に実行し、上位の結果を取得)
    if ITEM_NAMES:
        # 英語正式名から上位5つを取得
        official_matches = process.extract(ui_raw, ITEM_NAMES, scorer=fuzz.WRatio, limit=5)
        for name, score, _ in official_matches:
             # 既にリストに含まれていないか確認してから追加
             if name not in [m[0] for m in matches]:
                matches.append((name, int(score)))

    # スコアで降順ソート
    matches.sort(key=lambda x: x[1], reverse=True)
    
    # スコア60未満の結果は除外
    return [m for m in matches if m[1] >= FUZZY_THRESHOLD]


# =========================
#  Tarkov-Market：価格取得
# =========================
def get_price_data(name: str):
    if not TARKOV_MARKET_API_KEY:
        return None

    try:
        url = TARKOV_MARKET_SEARCH_URL.format(
            requests.utils.quote(name), TARKOV_MARKET_API_KEY
        )
        r = requests.get(url, timeout=20)
        r.raise_for_status()

        data = r.json()
        if not data:
            return None

        return data[0]

    except Exception as e:
        print("❌ TarkovMarket API エラー:", e)
        return None


# =========================
# Discord BOT
# =========================
@client.event
async def on_ready():
    print(f"🚀 BOT起動: {client.user}")
    load_all_items()


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    content = message.content.strip()

    # help
    if content.lower() == "!help":
        await message.channel.send(
            "使い方：`!アイテム名`\n"
            "例：`!ledx`, `!グラボ`, `!m4`, `!フラッシュドライブ`"
        )
        return

    # コマンド判定
    if not content.startswith("!"):
        return

    query = content[1:].strip()
    if not query:
        await message.channel.send("例：`!ledx` のように入力してください。")
        return

    # Fuzzy + Alias検索
    # NOTE: 
    matches = fuzzy_match(query)
    
    if not matches:
        await message.channel.send(f"❌ `{query}` に一致するアイテムがありませんでした。")
        return

    # 最もスコアの高いアイテムを取得
    best_match_name, best_match_score = matches[0]

    # スコアがしきい値未満の場合、候補一覧を返す
    if best_match_score < FUZZY_THRESHOLD:
        
        # 上位5つを表示
        top_matches = matches[:5]
        
        candidates = "\n".join(
            [f"・**{name}** (スコア: {score})" for name, score in top_matches]
        )
        
        await message.channel.send(
            f"⚠️ **`{query}`** の類似度が低いです。(ベストマッチのスコア: {best_match_score})\n"
            f"もしかして、以下のアイテムではありませんか？\n\n"
            f"{candidates}\n\n"
            "正確なアイテム名を再検索するか、エイリアスが未登録の場合は開発者にご連絡ください。"
        )
        return

    # スコアが高く、ベストマッチが決まった場合、処理を続行
    name = best_match_name

    # Tarkov-Market API
    price = get_price_data(name)
    if not price:
        await message.channel.send("❌ 価格情報が取得できませんでした。")
        return

    # 価格情報整理
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

    profit_s = "----"
    try:
        if isinstance(avg, (int, float)) and isinstance(trader_price, (int, float)):
            profit = avg - trader_price
            profit_s = f"{profit:+,}₽"
    except:
        pass

    wiki = ITEM_NAME_TO_WIKI.get(name)

    # =========================
    #  Embed 生成
    # =========================
    embed = discord.Embed(
        title=name,
        url=wiki if wiki else discord.Embed.Empty,
        description=f"🔍 検索ワード： `{query}`\n🎯 実クエリ： `{name.lower()}`",
        color=0x00AAFF,
    )

    # サムネ
    if icon:
        embed.set_thumbnail(url=icon)

    # 価格情報
    embed.add_field(
        name="💰 価格情報",
        value=(
            f"フリマ平均： **{avg_s}**\n"
            f"トレーダー最高買取： **{trader}（{trader_price_s}）**\n"
            f"差額： **{profit_s}**"
        ),
        inline=False,
    )

    # =========================
    #  ⭐ Twitch を超強調したフッター
    # =========================
    twitch_footer = (
        "Prices via Tarkov-Market\n"
        f"✨ FOLLOW ME ON TWITCH ✨ → {TWITCH_URL}"
    )

    embed.set_footer(text=twitch_footer)

    await message.channel.send(embed=embed)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    load_all_items()
    client.run(DISCORD_TOKEN)
