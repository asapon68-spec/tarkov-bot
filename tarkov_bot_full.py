import os
import json
import discord
import requests
from rapidfuzz import process, fuzz
from discord.ui import View, Button

# =========================
# 設定
# =========================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
TWITCH_URL = os.getenv("TWITCH_URL", "https://www.twitch.tv/jagami_orochi")

ALIAS_FUZZY_THRESHOLD = 35   # alias fuzzy 甘め
ITEM_FUZZY_THRESHOLD  = 65   # item fuzzy 少し厳しめ
FUZZY_LIMIT = 10             # 最大10件

# ▼▼ GitHub キャッシュ破壊用 v= を付けて強制最新読込 ▼▼
ITEM_JSON_URL = "https://raw.githubusercontent.com/asapon68-spec/tarkov-bot/main/items.json?v=20251201a"
ALIAS_JSON_URL = "https://raw.githubusercontent.com/asapon68-spec/tarkov-bot/main/alias.json?v=20251201a"

if not DISCORD_TOKEN:
    raise SystemExit("❌ DISCORD_TOKEN が設定されていません")


# =========================
# GitHub JSON Loader
# =========================
def load_json(url):
    try:
        print(f"📥 Fetching JSON from: {url}")
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("❌ JSON読み込みエラー:", e)
        return {}


ITEM_DB = load_json(ITEM_JSON_URL)
ALIAS_DB = load_json(ALIAS_JSON_URL)

ITEM_NAMES = list(ITEM_DB.keys())

print("===== DEBUG: JSON LOAD CHECK =====")
print("Loaded alias count:", len(ALIAS_DB))
print("Loaded items count:", len(ITEM_DB))
print("Sample alias keys:", list(ALIAS_DB.keys())[:10])
print("===================================")


# =========================
# 正規化（ハイフン除去 + スペース除去 + 小文字）
# =========================
def normalize(text: str) -> str:
    return text.replace("-", "").replace(" ", "").lower()


# =========================
# alias → item_name の逆引き辞書生成
# =========================
def build_alias_reverse_map():
    amap = {}

    for real_name, aliases in ALIAS_DB.items():
        for a in aliases:
            na = normalize(a)
            if na not in amap:
                amap[na] = []
            amap[na].append(real_name)

    return amap


ALIAS_REVERSE = build_alias_reverse_map()


# =========================
# 検索フロー（alias → items）
# =========================
def find_candidates(query: str):
    q_norm = normalize(query)
    candidates = []

    # ---- 1) alias fuzzy ----
    alias_keys = list(ALIAS_REVERSE.keys())

    alias_results = process.extract(
        q_norm,
        alias_keys,
        scorer=fuzz.WRatio,
        limit=20
    )

    for alias_key, score, _ in alias_results:
        if score >= ALIAS_FUZZY_THRESHOLD:
            for real in ALIAS_REVERSE.get(alias_key, []):
                candidates.append(real)

    # ---- 2) items fuzzy ----
    item_results = process.extract(
        q_norm,
        ITEM_NAMES,
        scorer=fuzz.WRatio,
        processor=normalize,
        limit=FUZZY_LIMIT
    )

    for name, score, _ in item_results:
        if score >= ITEM_FUZZY_THRESHOLD:
            candidates.append(name)

    # ---- 重複排除（順序保持）----
    return list(dict.fromkeys(candidates))


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
# アイテム埋め込み生成
# =========================
async def send_item_embed(message, item_name: str, query: str):
    item = ITEM_DB.get(item_name)
    if not item:
        await message.channel.send(f"❌ `{item_name}` のデータが見つかりませんでした。")
        return

    embed = discord.Embed(
        title=item_name,
        description=f"🔍 検索： `{query}`\n🎯 実クエリ： `{item_name}`",
        color=0x00AAFF,
    )

    trader_info = item.get("trader_price")
    trader_text = "----"

    if isinstance(trader_info, dict) and trader_info:
        tn = list(trader_info.keys())[0]
        tp = trader_info[tn]
        trader_text = f"{tn}: {tp:,}₽"

    embed.add_field(
        name="💰 買取価格",
        value=trader_text,
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

    await message.channel.send(embed=embed)


# =========================
# ボタン生成
# =========================
class ItemSelectView(View):
    def __init__(self, message, query, user_id, candidates):
        super().__init__(timeout=30)
        self.message = message
        self.query = query
        self.user_id = user_id

        for name in candidates:
            self.add_item(ItemButton(label=name, item_name=name))


class ItemButton(Button):
    def __init__(self, label, item_name):
        super().__init__(label=label[:80], style=discord.ButtonStyle.primary)
        self.item_name = item_name

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message(
                "❌ この選択肢はあなたの入力ではありません。",
                ephemeral=True
            )
            return

        await interaction.response.defer()
        await send_item_embed(self.view.message, self.item_name, self.view.query)
        self.view.stop()


# =========================
# メッセージイベント
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

    candidates = find_candidates(query)

    # 0件
    if len(candidates) == 0:
        await message.channel.send(f"❌ `{query}` に一致するアイテムがありませんでした。")
        return

    # 1件
    if len(candidates) == 1:
        await send_item_embed(message, candidates[0], query)
        return

    # 2件以上
    view = ItemSelectView(message, query, message.author.id, candidates)
    await message.channel.send("🔍 複数候補があります👇\n押して選んでください！", view=view)


# =========================
# 起動
# =========================
client.run(DISCORD_TOKEN)