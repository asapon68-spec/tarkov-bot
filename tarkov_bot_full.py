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
TWITCH_URL = os.getenv("TWITCH_URL", "").strip()
FUZZY_THRESHOLD = int(os.getenv("FUZZY_THRESHOLD", "60"))

if not DISCORD_TOKEN:
    raise SystemExit("DISCORD_TOKEN が設定されていません")

# =========================
# 定数
# =========================
TARKOV_MARKET_ITEM_URL = "https://api.tarkov-market.app/api/v1/item?q={}&x-api-key={}"

# Discord Intents
intents = discord.Intents.default()
intents.message_content = True  # メッセージ内容を読むのに必須
client = discord.Client(intents=intents)

# キャッシュ（簡易版：名前リストだけ）
ITEM_NAMES = []

# タスク必要アイテム（ここを自分好みに増やせる）
TASK_ITEMS = {
    "LEDX Skin Transilluminator": False,
    "Salewa first aid kit": True,
    "Gas analyzer": True,
}

# ハイドアウト使用アイテム（ここも自分好みに増やせる）
HIDEOUT_ITEMS = {
    "LEDX Skin Transilluminator": True,
    "Military power filter": True,
    "Electric drill": True,
}

# =========================
# アイテム候補（あいまい検索用）
# 本当はtarkov.devから全部取ってくるけど、
# まずは動かすこと優先で、よく使うもの中心に置いておく
# =========================
BASE_ITEMS = [
    "LEDX Skin Transilluminator",
    "Salewa first aid kit",
    "Gas analyzer",
    "Graphics card",
    "Secure Flash drive",
    "Tetriz portable game console",
    "Military power filter",
    "Electric drill",
]


def init_items():
    """
    起動時にあいまい検索用のアイテム名リストを用意する。
    （とりあえず手動リスト。あとから増やせる）
    """
    global ITEM_NAMES
    ITEM_NAMES = BASE_ITEMS[:]
    print(f"アイテム候補数: {len(ITEM_NAMES)}")


# =========================
# あいまい検索
# =========================
def fuzzy_match(user_input: str):
    """
    ユーザー入力 (誤字・略称) から最も近いアイテム名を取得。
    """
    if not ITEM_NAMES:
        return None, 0
    match = process.extractOne(user_input, ITEM_NAMES, scorer=fuzz.WRatio)
    if match:
        name, score, _ = match
        return name, int(score)
    return None, 0


# =========================
# 「詳細取得」ダミー（tarkov.dev問い合わせは一旦やめる）
# =========================
def get_item_detail_stub(name: str):
    """
    本当はtarkov.devから詳細を取るが、
    いったん確実に動くようにダミーで返す。
    """
    return {
        "name": name,
        "usedInTasks": []  # 自動タスク判定は使わず、手動テーブルだけ利用
    }


# =========================
# Tarkov Market 価格取得
# =========================
def get_price_from_tarkov_market(query_name: str):
    """
    Tarkov Market API から価格情報を取得。
    APIキーが設定されていない場合は None を返す。
    """
    if not TARKOV_MARKET_API_KEY:
        return None

    try:
        url = TARKOV_MARKET_ITEM_URL.format(
            requests.utils.quote(query_name),
            TARKOV_MARKET_API_KEY
        )
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        return data[0]
    except Exception as e:
        print("Tarkov Market API エラー:", e)
        return None


# =========================
# Discord イベント
# =========================
@client.event
async def on_ready():
    print(f"Bot 起動: {client.user} (id: {client.user.id})")
    init_items()


@client.event
async def on_message(message: discord.Message):
    # 自分自身のメッセージは無視
    if message.author == client.user:
        return

    content = message.content.strip()

    # ヘルプ
    if content.lower().startswith("!help"):
        txt = (
            "Tarkov item BOT 使い方\n"
            "`!price <アイテム名>` でフリマ価格とタスク/ハイドアウト情報を表示します。\n"
            "例: `!price LEDX` `!price salewa`\n"
        )
        await message.channel.send(txt)
        return

    if not content.lower().startswith("!price"):
        return

    query_text = content[6:].strip()
    if not query_text:
        await message.channel.send("使い方：`!price <アイテム名>` の形式で入力してください。\n例：`!price LEDX`")
        return

    # 1) あいまい検索で正式名称を推定
    matched_name, score = fuzzy_match(query_text)
    if not matched_name:
        await message.channel.send("アイテム候補が見つかりませんでした。リストにないアイテムかもしれません。")
        return

    if score < FUZZY_THRESHOLD:
        await message.channel.send(f"もしかして: **{matched_name}** (類似度 {score})\nもう少し正確な名前を入力してみてください。")
        return

    # 2) 詳細情報（ダミー）
    detail = get_item_detail_stub(matched_name)
    official_name = detail.get("name", matched_name)

    # 3) タスク判定（手動テーブルのみ）
    is_task_required = TASK_ITEMS.get(official_name, False)
    task_text = "タスク必要: ✅" if is_task_required else "タスク必要: ❌"

    # 4) ハイドアウト判定
    is_hideout_item = HIDEOUT_ITEMS.get(official_name, False)
    hideout_text = "ハイドアウト使用: ✅" if is_hideout_item else "ハイドアウト使用: ❌"

    # 5) 価格情報
    price_data = get_price_from_tarkov_market(official_name)
    if price_data:
        avg = price_data.get("avg24hPrice") or price_data.get("price") or 0
        trader_name = price_data.get("traderName") or price_data.get("trader") or "----"
        trader_price = price_data.get("traderPrice") or price_data.get("trader_price") or 0

        try:
            avg_s = f"{int(avg):,}₽" if avg else "取得不可"
        except Exception:
            avg_s = str(avg)

        try:
            trader_price_s = f"{int(trader_price):,}₽" if trader_price else "取得不可"
        except Exception:
            trader_price_s = str(trader_price)

        price_text = (
            f"フリマ平均: {avg_s}\n"
            f"{trader_name} 買取: {trader_price_s}"
        )
    else:
        price_text = "価格情報: 取得不可（Tarkov Market APIキー未設定か、アイテム未対応）"

    # 6) Embed で表示
    embed = discord.Embed(
        title=official_name,
        description=f"検索ワード: `{query_text}` / マッチ: `{matched_name}` (score {score})",
        color=0x00FF00
    )
    embed.add_field(name="タスク / ハイドアウト", value=f"{task_text}\n{hideout_text}", inline=False)
    embed.add_field(name="価格情報", value=price_text, inline=False)

    if TWITCH_URL:
        embed.set_footer(text=f"Powered by {TWITCH_URL}")

    await message.channel.send(embed=embed)


# =========================
# 実行
# =========================
if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
