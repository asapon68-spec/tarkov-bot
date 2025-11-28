# ==============================
#  Escape from Tarkov Discord Bot
#  アイテム検索 + Wikiリンク + Twitch宣伝
#  完全版 / 重複表示なし / Embedのみ
# ==============================

import discord
import requests
from rapidfuzz import process, fuzz

# ---------------------------------------
# 1. Discord BOT 設定
# ---------------------------------------

TOKEN = "YOUR_DISCORD_BOT_TOKEN"
CHANNEL_ID = 000000000000  # 任意のチャンネルID（制限しないなら削除可）

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# ---------------------------------------
# 2. タルコフ アイテム辞書 (必要に応じて追加)
# ---------------------------------------

item_dict = {
    "ledx skin transilluminator": {
        "jp": "LEDX 静脈可視化装置",
        "aka": ["LEDX", "ledx", "LEDX Skin"],
        "wiki": "https://escapefromtarkov.fandom.com/wiki/LEDX_Skin_Transilluminator"
    },
    "graphics card": {
        "jp": "グラフィックボード",
        "aka": ["GPU", "gpu", "グラボ"],
        "wiki": "https://escapefromtarkov.fandom.com/wiki/Graphics_card"
    },
    "physical bitcoin": {
        "jp": "ビットコインの金貨",
        "aka": ["BTC", "bitcoin", "0.2BTC", "ビットコイン"],
        "wiki": "https://escapefromtarkov.fandom.com/wiki/Physical_Bitcoin"
    },
    # ← ここにあとで大量追加することも可能（Bot側は自動処理）
}


# ---------------------------------------
# 3. API（Tarkov Market）
# ---------------------------------------

def fetch_item(name: str):
    """Tarkov Market APIでアイテム検索"""
    try:
        url = f"https://api.tarkov-market.app/api/v2/search?query={name}"
        headers = {"accept": "application/json"}
        res = requests.get(url, headers=headers, timeout=5)
        data = res.json()
        if data and "items" in data and len(data["items"]) > 0:
            return data["items"][0]  # 最も一致したアイテム
    except:
        return None
    return None


# ---------------------------------------
# 4. 最適一致（正式名・略称・日本語・曖昧）
# ---------------------------------------

def search_best_match(user_text):
    """辞書 + ユーザー入力のベストマッチを返す"""

    # 辞書キーリスト
    all_keys = []
    for key, info in item_dict.items():
        all_keys.append(key)
        all_keys.extend(info["aka"])
        all_keys.append(info["jp"])

    # RapidFuzz で曖昧マッチ
    match, score, _ = process.extractOne(
        user_text,
        all_keys,
        scorer=fuzz.WRatio
    )

    if score < 60:  # 閾値（必要なら調整）
        return None, None

    # 抽出されたキーが辞書のどのアイテムに属するか検索
    for key, info in item_dict.items():
        if match.lower() == key.lower():
            return key, info

        if match in info.get("aka", []):
            return key, info

        if match == info.get("jp"):
            return key, info

    return None, None


# ---------------------------------------
# 5. Discord BOT メイン処理
# ---------------------------------------

@client.event
async def on_ready():
    print(f"Bot logged in as {client.user}")


@client.event
async def on_message(message):

    if message.author.bot:
        return

    user_query = message.content.strip()
    if len(user_query) < 1:
        return

    # ベストマッチ辞書検索
    item_key, info = search_best_match(user_query)

    # まず辞書でヒットしない場合 API 検索
    api_item = fetch_item(user_query)

    if not info and not api_item:
        await message.channel.send(f"❌ 該当アイテムが見つかりませんでした：**{user_query}**")
        return

    # Embed 作成
    embed = discord.Embed(
        title=api_item["name"] if api_item else info["jp"],
        description=f"🔍 検索ワード: **{user_query}**",
        color=0x00ffbf
    )

    # 画像
    if api_item and "img" in api_item:
        embed.set_thumbnail(url=api_item["img"])

    # API 情報
    if api_item:
        price = api_item.get("avg24hPrice", 0)
        trader = api_item.get("traderName", "?")
        trader_price = api_item.get("traderPrice", 0)
        diff = price - trader_price

        embed.add_field(
            name="💰 価格情報",
            value=f"""
・フリマ平均：**{price:,}₽**
・トレーダー最高買取：**{trader}（{trader_price:,}₽）**
・差額：**{diff:,}₽**
""",
            inline=False
        )

    # Wiki リンク（辞書にあれば）
    if info and "wiki" in info:
        embed.add_field(
            name="📘 Wiki",
            value=info["wiki"],
            inline=False
        )

    # Twitch リンク（最下部）
    embed.add_field(
        name="✨ Follow my Twitch!",
        value="https://m.twitch.tv/jagami_orochi/home",
        inline=False
    )

    await message.channel.send(embed=embed)


# ---------------------------------------
# 6. BOT 実行
# ---------------------------------------

client.run(TOKEN)
