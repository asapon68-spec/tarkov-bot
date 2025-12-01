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
# アイテム検索処理
# =========================
def fuzzy_search_candidates(query):
    """
    曖昧検索で候補を返す。
    数字のみ → 1〜2桁は無視 / 3桁以上は部分一致
    文字 → Fuzzy
    """
    q = query.lower()

    # --- 数字のみの入力 ---
    if q.isdigit():
        # 1〜2桁はノーヒット扱い
        if len(q) <= 2:
            return []
        # 3桁以上は名前の部分一致
        return [name for name in ITEM_NAMES if q in name.lower()]

    # --- それ以外は fuzzy search ---
    results = process.extract(q, ITEM_NAMES, scorer=fuzz.WRatio, limit=20)
    return [name for name, score, _ in results if score >= FUZZY_THRESHOLD]


def find_alias_hit(query):
    q = query.lower()
    for real_name, aliases in ALIAS_DB.items():
        if q in [a.lower() for a in aliases]:
            return real_name
    return None


# =========================
# Discord BOT設定
# =========================
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# ----- embed 作る -----
def make_embed(item_name, query):
    item = ITEM_DB[item_name]

    embed = discord.Embed(
        title=item_name,
        description=f"🔍 検索： `{query}`\n🎯 実クエリ： `{item_name}`",
        color=0x00AAFF,
    )

    # trader price
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
        inline=False,
    )

    return embed


# ----- ボタン作る -----
class ItemSelectView(discord.ui.View):
    def __init__(self, query, candidates):
        super().__init__(timeout=20)
        self.query = query
        for name in candidates:
            self.add_item(ItemSelectButton(label=name))


class ItemSelectButton(discord.ui.Button):
    def __init__(self, label):
        super().__init__(label=label, style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        item_name = self.label
        embed = make_embed(item_name, item_name)
        await interaction.response.edit_message(content="", embed=embed, view=None)


@client.event
async def on_ready():
    print(f"🚀 BOT起動: {client.user}")


@client.event
async def on_message(message):
    if message.author.bot:
        return

    if not message.content.startswith("!"):
        return

    query = message.content[1:].strip()
    if not query:
        return

    # --- alias 先にチェック ---
    alias_hit = find_alias_hit(query)
    if alias_hit:
        embed = make_embed(alias_hit, query)
        await message.channel.send(embed=embed)
        return

    # --- fuzzy検索 ---
    candidates = fuzzy_search_candidates(query)

    # 0件
    if len(candidates) == 0:
        await message.channel.send(f"❌ `{query}` に一致するアイテムがありませんでした。")
        return

    # 1件 → 即表示
    if len(candidates) == 1:
        embed = make_embed(candidates[0], query)
        await message.channel.send(embed=embed)
        return

    # 10件超え → 候補出さずメッセージのみ
    if len(candidates) > 10:
        await message.channel.send("🔎 **複数候補が多すぎます！もっと絞って入力してね！**")
        return

    # 2〜10件 → ボタン表示
    view = ItemSelectView(query, candidates)
    await message.channel.send("🔎 **複数候補があります👇 どれを表示する？**", view=view)


# =========================
# RUN
# =========================
client.run(DISCORD_TOKEN)
