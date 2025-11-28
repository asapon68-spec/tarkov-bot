# ==========================================================
# Escape from Tarkov Discord BOT（最新版）
# ・日本語／略称／ミススペル → 辞書 & 曖昧検索で補正
# ・Tarkov-Market API で価格取得
# ・Wikiリンク / サムネ / アイコン付き Embed
# ・Twitch 宣伝つき
# ==========================================================

import os
import discord
import requests
from rapidfuzz import process, fuzz
from item_dictionary import ITEM_ALIASES

# ========= 環境変数 =========
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TARKOV_MARKET_API_KEY = os.getenv("TARKOV_MARKET_API_KEY")
TWITCH_URL = os.getenv("TWITCH_URL", "https://www.twitch.tv/jagamiorochi")
FUZZY_THRESHOLD = int(os.getenv("FUZZY_THRESHOLD", "70"))  # 75くらいがベスト
CHANNEL_ID = None

# ========= Discord Client =========
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# ========= Wiki URL生成 =========
def build_wiki_url(name: str) -> str:
    base = "https://escapefromtarkov.fandom.com/wiki/"
    return base + name.replace(" ", "_")


# ========= Tarkov-Market API =========
def fetch_from_tarkov_market(name: str):
    if not TARKOV_MARKET_API_KEY:
        return None

    try:
        url = "https://tarkov-market.com/api/v1/item"
        headers = {"x-api-key": TARKOV_MARKET_API_KEY}
        params = {"q": name}

        res = requests.get(url, headers=headers, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
        if not data:
            return None

        return data[0]  # 一番近いやつ
    except:
        return None


# ========= 日本語・略称 → 英語名（辞書 + 曖昧） =========
def resolve_query(query: str) -> str:
    key = query.lower().strip()

    # ① 完全一致（alias → 正式名）
    if key in ITEM_ALIASES:
        return ITEM_ALIASES[key]

    # ② RapidFuzz の曖昧一致
    best = process.extractOne(key, ITEM_ALIASES.keys(), scorer=fuzz.WRatio)
    if best and best[1] >= FUZZY_THRESHOLD:
        alias = best[0]
        return ITEM_ALIASES[alias]

    # ③ どうしても辞書に無い → そのまま API 検索
    return query


# ========= メッセージイベント =========
@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    content = message.content.strip()

    # 「!」コマンドだけ反応
    if not content.startswith("!"):
        return

    raw_query = content[1:].strip()
    if not raw_query:
        return

    # 🔥 日本語・略称 → 正式英語名（辞書＋曖昧検索）
    resolved_name = resolve_query(raw_query)

    # 🔥 API検索
    item = fetch_from_tarkov_market(resolved_name)
    if not item:
        await message.channel.send(f"❌  `{raw_query}` のアイテムが見つかりません…")
        return

    # データ取得
    name = item.get("name", resolved_name)
    short_name = item.get("shortName", "")
    flea = item.get("avg24hPrice")
    trader_name = item.get("traderName")
    trader_price = item.get("traderPrice")
    img = item.get("img") or item.get("icon")
    wiki_url = item.get("wikiLink") or build_wiki_url(name)

    # 差額計算
    if flea and trader_price:
        profit = flea - trader_price
        profit_text = f"{profit:+,}₽"
    else:
        profit_text = "不明"

    # ========= Embed生成 =========
    embed = discord.Embed(
        title=f"🔫 {name}",
        url=wiki_url,
        color=0x00FFAA
    )

    if img:
        embed.set_thumbnail(url=img)

    embed.description = (
        f"🔍 **検索ワード**： `{raw_query}`\n"
        f"🎯 **一致したアイテム**： `{resolved_name}`\n"
    )

    price_text = []
    if flea:
        price_text.append(f"🛒 **フリマ平均**：{flea:,}₽")
    if trader_name:
        price_text.append(f"🏪 **{trader_name} 買取**：{trader_price:,}₽")
    price_text.append(f"💹 **差額**：{profit_text}")

    embed.add_field(name="💰 価格情報", value="\n".join(price_text), inline=False)

    embed.set_footer(
        text=f"Prices via Tarkov-Market ｜ Twitch → {TWITCH_URL}"
    )

    await message.channel.send(embed=embed)


# ========= BOT起動 =========
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN が設定されていません!")
    client.run(DISCORD_TOKEN)
