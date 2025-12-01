import os
import json
import discord
import requests
import re
from rapidfuzz import process, fuzz

# =========================
# 設定
# =========================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
TWITCH_URL = os.getenv("TWITCH_URL", "https://www.twitch.tv/jagami_orochi")
FUZZY_THRESHOLD = 60

ITEM_JSON_URL = "https://raw.githubusercontent.com/asapon68-spec/tarkov-bot/main/items.json"
ALIAS_JSON_URL = "https://raw.githubusercontent.com/asapon68-spec/tarkov-bot/main/alias.json"

if not DISCORD_TOKEN:
    raise SystemExit("❌ DISCORD_TOKEN が設定されていません")


# =========================
# JSON Loader
# =========================
def load_json(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("❌ JSON読み込みエラー:", e)
        return {}


ITEM_DB = load_json(ITEM_JSON_URL)
ALIAS_DB = load_json(ALIAS_JSON_URL)
ITEM_NAMES = list(ITEM_DB.keys())


# =========================
# 🔍 複数候補検索ロジック（v1.5.1）
# =========================
def fuzzy_search_candidates(query):
    q = query.lower()

    # --- 数字抽出（例: d314 → 314） ---
    numbers = re.findall(r"\d+", q)

    # AP-20 / M855A1 / 556mdr など → 弾・武器なので数字抽出しない
    is_ammo_like = (
        "-" in q or 
        re.match(r"^[a-z]+\d+[a-z0-9]*$", q)
    )

    if numbers and not is_ammo_like:
        num = numbers[0]

        # 1〜2桁の数字は検索しない
        if len(num) <= 2:
            return []

        # 数字3桁以上 → 名前に数字を含むアイテム
        return [name for name in ITEM_NAMES if num in name.lower()]

    # --- 通常 fuzzy search ---
    results = process.extract(q, ITEM_NAMES, scorer=fuzz.WRatio, limit=20)
    return [name for name, score, _ in results if score >= FUZZY_THRESHOLD]


# =========================
# エイリアス優先検索
# =========================
def find_item_exact(query):
    q = query.lower()

    # alias から検索
    for real, alias_list in ALIAS_DB.items():
        if q in [a.lower() for a in alias_list]:
            return real

    return None


# =========================
# Discord BOT
# =========================
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"🚀 BOT起動: {client.user}")


# =========================
# ボタンUIクラス
# =========================
class CandidateView(discord.ui.View):
    def __init__(self, query, candidates):
        super().__init__(timeout=20)
        self.query = query
        self.candidates = candidates

        for name in candidates[:10]:  # 最大10件
            self.add_item(CandidateButton(label=name, item_name=name))


class CandidateButton(discord.ui.Button):
    def __init__(self, label, item_name):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.item_name = item_name

    async def callback(self, interaction: discord.Interaction):
        item = ITEM_DB[self.item_name]

        embed = discord.Embed(
            title=self.item_name,
            description=f"🔍 選択： `{self.label}`\n🎯 実クエリ： `{self.item_name}`",
            color=0x00AAFF,
        )

        trader_info = item.get("trader_price")
        trader_text = "----"

        if isinstance(trader_info, dict):
            tn = list(trader_info.keys())[0]
            tp = trader_info[tn]
            trader_text = f"{tn}: {tp:,}₽"

        embed.add_field(name="💰 買取価格", value=trader_text, inline=False)
        embed.add_field(
            name="📌 その他",
            value=f"タスク必要： {item.get('task')}\nハイドアウト必要： {item.get('hideout')}",
            inline=False
        )
        embed.add_field(
            name="",
            value=f"[✨ FOLLOW 蛇神オロチ ON TWITCH ✨]({TWITCH_URL})",
            inline=False
        )

        await interaction.response.send_message(embed=embed)


# =========================
# メッセージ処理
# =========================
@client.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip()
    if not content.startswith("!"):
        return

    query = content[1:].strip()
    if not query:
        return

    # alias → 即決ヒット
    item_name = find_item_exact(query)
    if item_name:
        candidates = [item_name]
    else:
        candidates = fuzzy_search_candidates(query)

    # No hit
    if not candidates:
        await message.channel.send(f"❌ `{query}` に一致するアイテムが見つかりませんでした")
        return

    # Multiple hit → ボタン
    if len(candidates) > 1:
        await message.channel.send(
            f"🔍 複数候補があります👇\n押して選んでください！",
            view=CandidateView(query, candidates)
        )
        return

    # Single hit → 即表示
    item_name = candidates[0]
    item = ITEM_DB[item_name]

    embed = discord.Embed(
        title=item_name,
        description=f"🔍 検索： `{query}`\n🎯 実クエリ： `{item_name}`",
        color=0x00AAFF,
    )

    trader_info = item.get("trader_price")
    trader_text = "----"

    if isinstance(trader_info, dict):
        tn = list(trader_info.keys())[0]
        tp = trader_info[tn]
        trader_text = f"{tn}: {tp:,}₽"

    embed.add_field(name="💰 買取価格", value=trader_text, inline=False)
    embed.add_field(
        name="📌 その他",
        value=f"タスク必要： {item.get('task')}\nハイドアウト必要： {item.get('hideout')}",
        inline=False
    )
    embed.add_field(
        name="",
        value=f"[✨ FOLLOW 蛇神オロチ ON TWITCH ✨]({TWITCH_URL})",
        inline=False
    )

    await message.channel.send(embed=embed)


# =========================
# RUN
# =========================
client.run(DISCORD_TOKEN)
