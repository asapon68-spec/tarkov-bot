import os
import json
import discord
import requests
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
# GitHub JSON Loader
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
# アイテム検索処理（alias → item名 → fuzzy）
# =========================
def find_candidates(query):
    q = query.lower()

    # 🔒 1桁の数字 → 強制ノーヒット
    if q.isdigit() and len(q) == 1:
        return []

    candidates = set()

    # 1) alias 完全一致
    for real_name, aliases in ALIAS_DB.items():
        for a in aliases:
            if q == a.lower():
            # 完全一致 alias は即リターン（唯一解扱い）
                return [real_name]

    # 2) item.json の部分一致
    for name in ITEM_NAMES:
        if q in name.lower():
            candidates.add(name)

    # 3) fuzzy 検索（2件以上候補がある場合のみ追加）
    fuzzy_hits = process.extract(q, ITEM_NAMES, scorer=fuzz.WRatio, limit=10)
    for name, score, _ in fuzzy_hits:
        if score >= FUZZY_THRESHOLD:
            candidates.add(name)

    return list(candidates)


# =========================
# Discord UI (選択ボタン)
# =========================

class ItemSelectView(discord.ui.View):
    def __init__(self, items, query):
        super().__init__(timeout=20)
        self.query = query

        # ボタンを自動生成（最大10件）
        for name in items[:10]:
            self.add_item(ItemButton(name))

class ItemButton(discord.ui.Button):
    def __init__(self, item_name):
        super().__init__(label=item_name, style=discord.ButtonStyle.primary)
        self.item_name = item_name

    async def callback(self, interaction: discord.Interaction):
        await show_item_detail(interaction, self.item_name, interaction.data["custom_id"])


# =========================
# アイテム詳細 Embed
# =========================
async def show_item_detail(interaction_or_channel, item_name, query):
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

    embed.add_field(
        name="💰 買取価格",
        value=f"{trader_text}",
        inline=False,
    )

    embed.add_field(
        name="📌 その他",
        value=(
            f"タスク必要： {item.get('task')}\n"
            f"ハイドアウト必要： {item.get('hideout')}"
        ),
        inline=False,
    )

    embed.add_field(
        name="",
        value=f"[✨ FOLLOW 蛇神オロチ ON TWITCH ✨]({TWITCH_URL})",
        inline=False
    )

    # interaction か channel のどちらかに対応
    if isinstance(interaction_or_channel, discord.Interaction):
        await interaction_or_channel.response.edit_message(embed=embed, view=None)
    else:
        await interaction_or_channel.send(embed=embed)


# =========================
# Discord BOT設定
# =========================
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"🚀 BOT起動: {client.user}")


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

    candidates = find_candidates(query)

    # ヒットなし
    if not candidates:
        await message.channel.send(f"❌ `{query}` に一致するアイテムがありませんでした。")
        return

    # 1件だけ → 即表示
    if len(candidates) == 1:
        await show_item_detail(message.channel, candidates[0], query)
        return

    # 複数件 → 選択ボタン
    view = ItemSelectView(candidates, query)
    await message.channel.send(
        f"🔍 **複数候補が見つかりました**\n押して選んでください👇",
        view=view
    )


# =========================
# RUN
# =========================
client.run(DISCORD_TOKEN)
