 # tarkov_bot_full.py
# Escape from Tarkov Discord BOT（シンプル動作版）
# - 先頭が "!" のメッセージをアイテム検索として扱う
# - Tarkov-Market API から価格情報を取得
# - 日本語＆略称は簡易エイリアス + Fuzzy で解決
# - Wikiリンク / 画像 / Twitch 宣伝付き Embed

import os
import requests
import discord
from rapidfuzz import process, fuzz

# =========================
# 環境変数
# =========================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
TARKOV_MARKET_API_KEY = os.getenv("TARKOV_MARKET_API_KEY", "").strip()
TWITCH_URL = os.getenv("TWITCH_URL", "https://m.twitch.tv/jagami_orochi/home").strip()
FUZZY_THRESHOLD = int(os.getenv("FUZZY_THRESHOLD", "70"))

if not DISCORD_TOKEN:
    raise SystemExit("❌ DISCORD_TOKEN が設定されていません")

if not TARKOV_MARKET_API_KEY:
    raise SystemExit("❌ TARKOV_MARKET_API_KEY が設定されていません")

# =========================
# エイリアス辞書
# （好きなだけ増やしてOK）
# =========================
ALIASES = {
    # --- 高額ルート ---
    "ledx": "ledx",
    "れどっくす": "ledx",
    "レドックス": "ledx",
    "レドックス 静脈": "ledx",
    "レドエックス": "ledx",

    "グラボ": "graphics card",
    "ぐらぼ": "graphics card",
    "gpu": "graphics card",

    "ビットコイン": "btc",
    "びっとこいん": "btc",
    "bitcoin": "btc",
    "btc": "btc",

    # 例：医療系
    "サレワ": "salewa",
    "されわ": "salewa",
    "salewa": "salewa",

    "グリズリー": "grizzly",
    "ぐりずりー": "grizzly",
    "grizzly": "grizzly",

    # 例：キー類
    "フラッシュドライブ": "secure flash drive",
    "フラドリ": "secure flash drive",
    "flash drive": "secure flash drive",
}

# =========================
# Discord client
# =========================
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# =========================
# エイリアス + Fuzzy 解決
# =========================
def resolve_query(user_text: str):
    """
    1) ALIASES に完全一致
    2) ALIASES キーに fuzzy
    3) 何もなければそのまま返す
    """
    raw = user_text.strip()
    key = raw.lower()

    # 1) 完全一致
    if key in ALIASES:
        return ALIASES[key], f"alias:{key}"

    # 2) fuzzy エイリアス
    if ALIASES:
        best = process.extractOne(key, list(ALIASES.keys()), scorer=fuzz.WRatio)
        if best and best[1] >= FUZZY_THRESHOLD:
            alias_key = best[0]
            return ALIASES[alias_key], f"alias-fuzzy:{alias_key}({best[1]})"

    # 3) そのまま
    return raw, "raw"


# =========================
# Tarkov-Market から価格取得
#   ※ 正式なエンドポイント:
#   https://api.tarkov-market.app/api/v1/item
# =========================
def fetch_price_from_tarkov_market(query: str):
    base_url = "https://api.tarkov-market.app/api/v1/item"
    headers = {"x-api-key": TARKOV_MARKET_API_KEY}
    params = {"q": query}

    try:
        resp = requests.get(base_url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            print(f"[TarkovMarket] 空レスポンス q={query}")
            return None
        return data[0]  # 先頭の候補を採用
    except Exception as e:
        print(f"[TarkovMarket] エラー q={query} -> {e}")
        return None


# =========================
# Discord イベント
# =========================
@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user} (ID: {client.user.id})")


@client.event
async def on_message(message: discord.Message):
    # 自分 & 他 BOT は無視
    if message.author.bot:
        return

    content = message.content.strip()

    # ヘルプ
    if content.lower() == "!help":
        await message.channel.send(
            "使い方：`!アイテム名`\n"
            "例：`!ledx`, `!レドックス`, `!グラボ`, `!bitcoin` など"
        )
        return

    # 先頭が "!" でなければ無視
    if not content.startswith("!"):
        return

    # "! xxx" → 検索ワード
    raw_query = content[1:].strip()
    if not raw_query:
        return

    # エイリアス + fuzzy
    resolved_query, how = resolve_query(raw_query)
    print(f"[Query] '{raw_query}' -> '{resolved_query}' via {how}")

    # Tarkov-Market から取得
    item = fetch_price_from_tarkov_market(resolved_query)
    if not item:
        await message.channel.send(f"❌ 価格情報が取得できませんでした。（検索ワード: `{raw_query}`）")
        return

    name = item.get("name", resolved_query)
    short_name = item.get("shortName")
    flea = item.get("avg24hPrice")
    trader_name = item.get("traderName")
    trader_price = item.get("traderPrice")
    icon = item.get("icon") or item.get("img")
    wiki = item.get("wikiLink")
    link = item.get("link") or wiki

    # 数値フォーマット
    def fmt(v):
        try:
            return f"{int(v):,}₽"
        except Exception:
            return "----"

    flea_s = fmt(flea)
    trader_price_s = fmt(trader_price)

    # 差額
    profit_s = "----"
    try:
        if isinstance(flea, (int, float)) and isinstance(trader_price, (int, float)):
            profit = int(flea) - int(trader_price)
            profit_s = f"{profit:+,}₽"
    except Exception:
        pass

    # =========================
    # Embed 作成
    # =========================
    embed = discord.Embed(
        title=name,
        url=link if link else discord.Embed.Empty,
        color=0x00AAFF,
    )

    # サムネ
    if icon:
        embed.set_thumbnail(url=icon)

    # 説明
    desc_lines = [
        f"🔍 **検索ワード：** `{raw_query}`",
        f"🎯 **実クエリ：** `{resolved_query}`",
    ]
    if short_name and short_name.lower() not in name.lower():
        desc_lines.append(f"🧾 **略称：** `{short_name}`")

    embed.description = "\n".join(desc_lines)

    # 価格フィールド
    price_lines = [
        f"フリマ平均：**{flea_s}**",
        f"トレーダー最高買取価格：**{trader_name or '----'}（{trader_price_s}）**",
        f"差額：**{profit_s}**",
    ]
    embed.add_field(
        name="💰 価格情報",
        value="\n".join(price_lines),
        inline=False,
    )

    # フッター（Twitch 宣伝）
    footer = "Prices via Tarkov-Market"
    if TWITCH_URL:
        footer += f" | Twitch: {TWITCH_URL}"
    embed.set_footer(text=footer)

    await message.channel.send(embed=embed)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
