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
FUZZY_THRESHOLD = 60          # あいまい検索のしきい値
FUZZY_LIMIT = 10              # fuzzy候補最大件数

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
# 文字列正規化（ハイフン無視＋小文字）
# =========================
def normalize(text: str) -> str:
    return text.replace("-", "").replace(" ", "").lower()


# =========================
# alias検索＋曖昧一致
# =========================
def find_candidates(query: str):
    """
    - まず alias.json を優先して検索
    - 次に items.json に対して fuzzy 検索
    - ハイフン有り/無しは同じ扱い
    - 最大 FUZZY_LIMIT 件まで候補を返す
    """
    q_raw = query.strip()
    q_norm = normalize(q_raw)

    candidates = []

    # ---- 1) alias 検索 ----
    for real_name, aliases in ALIAS_DB.items():
        # alias も正規化して比較（ハイフン無視・小文字化）
        if any(q_norm == normalize(a) for a in aliases):
            candidates.append(real_name)

    # ---- 2) fuzzy 検索 ----
    # choices 側だけ normalize してスコア計算
    fuzzy_results = process.extract(
        q_norm,
        ITEM_NAMES,
        scorer=fuzz.WRatio,
        processor=normalize,   # ITEM_NAME を normalize してから比較
        limit=FUZZY_LIMIT
    )

    for name, score, _ in fuzzy_results:
        if score >= FUZZY_THRESHOLD:
            candidates.append(name)

    # ---- 3) 重複排除（順番は維持）----
    unique = list(dict.fromkeys(candidates))
    return unique


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
# アイテム表示関数
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
# ボタン選択ビュー
# =========================
class ItemSelectView(View):
    def __init__(self, message, query, user_id, candidates):
        super().__init__(timeout=30)
        self.message = message
        self.query = query
        self.user_id = user_id

        # 候補ごとにボタン追加（最大10件想定）
        for name in candidates:
            self.add_item(ItemButton(label=name, item_name=name))


class ItemButton(Button):
    def __init__(self, label, item_name):
        # ラベルは長すぎると切れるので 80 文字で丸め
        super().__init__(label=label[:80], style=discord.ButtonStyle.primary)
        self.item_name = item_name

    async def callback(self, interaction: discord.Interaction):
        # 他人のボタン禁止
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message(
                "❌ この選択肢はあなたの入力に対するものではありません。",
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

    # 1件 → そのまま表示
    if len(candidates) == 1:
        await send_item_embed(message, candidates[0], query)
        return

    # 2件以上 → ボタン選択
    view = ItemSelectView(message, query, message.author.id, candidates)
    txt = "🔍 複数候補があります👇　押して選んでください！"
    await message.channel.send(txt, view=view)


# =========================
# RUN
# =========================
client.run(DISCORD_TOKEN)
