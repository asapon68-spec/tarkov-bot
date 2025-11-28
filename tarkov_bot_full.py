# tarkov_bot_full.py
# Escape from Tarkov Discord BOT
# ・! から始まるメッセージをアイテム検索として扱う
# ・日本語＆略称を item_dictionary.ITEM_ALIASES で解決
# ・Tarkov-Market の価格を表示
# ・Wiki リンク & Twitch 宣伝付き Embed

import os
import discord
import requests
from rapidfuzz import process, fuzz

from item_dictionary import ITEM_ALIASES

# --------- 環境変数 ---------
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TARKOV_MARKET_API_KEY = os.getenv("TARKOV_MARKET_API_KEY")
TWITCH_URL = os.getenv("TWITCH_URL", "https://www.twitch.tv/jagamiorochi")
FUZZY_THRESHOLD = int(os.getenv("FUZZY_THRESHOLD", "65"))

CHANNEL_ID = None  # 特定チャンネルだけに制限したい場合はIDを入れる

# --------- Discord クライアント ---------
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# --------- Wiki URL 自動生成 ---------
def build_wiki_url(english_name: str) -> str:
    base = "https://escapefromtarkov.fandom.com/wiki/"
    return base + english_name.replace(" ", "_")


# --------- Tarkov-Market から価格取得 ---------
def fetch_from_tarkov_market(name: str):
    """Tarkov-Market から item 情報を1件取ってくる"""
    if not TARKOV_MARKET_API_KEY:
        return None

    url = "https://tarkov-market.com/api/v1/item"
    headers = {"x-api-key": TARKOV_MARKET_API_KEY}
    params = {"q": name}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return None
        # 一番スコアが高い/先頭のものを採用
        return data[0]
    except Exception:
        return None


# --------- 日本語＆略称 → 英語正式名 変換 ---------
def resolve_query_to_name(query: str) -> str:
    """
    1. 完全一致（辞書キー）
    2. RapidFuzz で曖昧マッチ
    3. どれもダメならそのまま返す（英語で直接API検索）
    """
    key = query.lower().strip()

    # 1) 完全一致
    if key in ITEM_ALIASES:
        return ITEM_ALIASES[key]

    # 2) 曖昧一致
    if ITEM_ALIASES:
        best = process.extractOne(
            key, ITEM_ALIASES.keys(), scorer=fuzz.token_sort_ratio
        )
        if best and best[1] >= FUZZY_THRESHOLD:
            alias = best[0]
            return ITEM_ALIASES[alias]

    # 3) そのまま
    return query


# --------- メッセージイベント ---------
@client.event
async def on_message(message: discord.Message):
    # BOT 自身は無視
    if message.author.bot:
        return

    # チャンネル制限したい場合
    if CHANNEL_ID and message.channel.id != CHANNEL_ID:
        return

    content = message.content.strip()
    # 「!」から始まるものだけコマンドとして扱う
    if not content.startswith("!"):
        return

    # 先頭の「!」を外してクエリにする
    raw_query = content[1:].strip()
    if not raw_query:
        return

    # 日本語 / 略称 → 英語正式名
    resolved_name = resolve_query_to_name(raw_query)

    # Tarkov-Market から情報取得
    item_data = fetch_from_tarkov_market(resolved_name)

    if not item_data:
        await message.channel.send(f"❌ 該当アイテムが見つかりませんでした…（`{raw_query}`）")
        return

    # Tarkov-Market のフィールド名に合わせて取得
    name = item_data.get("name", resolved_name)
    short_name = item_data.get("shortName", "")
    flea = item_data.get("avg24hPrice") or item_data.get("avg24hPrice") or 0
    trader_name = item_data.get("traderName")
    trader_price = item_data.get("traderPrice")
    img = item_data.get("img") or item_data.get("icon") or None

    # 差額
    profit_text = "不明"
    if flea and trader_price:
        profit = int(flea) - int(trader_price)
        sign = "+" if profit >= 0 else "-"
        profit_text = f"{sign}{abs(profit):,}₽"

    # Wikiリンクは自前生成（名前ベース）
    wiki_url = item_data.get("wikiLink") or build_wiki_url(name)

    # --------- Embed 生成 ---------
    embed = discord.Embed(
        title=name,
        url=wiki_url,  # タイトルをクリックするとWikiへ
        color=0x00FF99,
    )

    # サムネ画像
    if img:
        embed.set_thumbnail(url=img)

    # 上部説明
    desc_lines = [
        f"🔍 **検索ワード：** `{raw_query}`",
        f"🎯 **マッチ：** {resolved_name}",
    ]
    if short_name and short_name.lower() not in name.lower():
        desc_lines.append(f"🧾 **略称：** {short_name}")
    embed.description = "\n".join(desc_lines)

    # 価格情報フィールド
    price_lines = []
    if flea:
        price_lines.append(f"フリマ平均：**{int(flea):,}₽**")
    if trader_name and trader_price:
        price_lines.append(
            f"トレーダー最高買取価格：**{trader_name}（{int(trader_price):,}₽）**"
        )
    price_lines.append(f"差額：**{profit_text}**")

    embed.add_field(name="💰 価格情報", value="\n".join(price_lines), inline=False)

    # フッター（Twitch 宣伝 + クレジット）
    embed.set_footer(
        text=f"Prices via Tarkov-Market | ✨ Follow my Twitch! → {TWITCH_URL}"
    )

    await message.channel.send(embed=embed)


# --------- 起動 ---------
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN が設定されていません。Render の環境変数を確認してね。")
    client.run(DISCORD_TOKEN)
