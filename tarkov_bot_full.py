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
    raise SystemExit("DISCORD_TOKEN が設定されていません (.env か Render の環境変数を確認してください)")

# =========================
# 定数
# =========================
TARKOV_DEV_GQL = "https://api.tarkov.dev/graphql"
TARKOV_MARKET_ITEM_URL = "https://api.tarkov-market.app/api/v1/item?q={}&x-api-key={}"

# Discord Intents
intents = discord.Intents.default()
intents.message_content = True  # メッセージ内容を読むのに必須
client = discord.Client(intents=intents)

# キャッシュ
ITEM_NAMES = []        # アイテム名一覧（あいまい検索用）
ITEM_NAME_TO_ID = {}   # アイテム名 → ID の対応

# タスク必要アイテム（とりあえず例。必要に応じて増やす）
TASK_ITEMS = {
    "LEDX Skin Transilluminator": False,   # 実際はタスクでは使わない例
    "Salewa first aid kit": True,
    "Gas analyzer": True,
}

# ハイドアウト使用アイテム（例）
HIDEOUT_ITEMS = {
    "LEDX Skin Transilluminator": True,
    "Military power filter": True,
    "Electric drill": True,
}


# =========================
# tarkov.dev から全アイテム取得
# =========================
def fetch_items():
    """
    起動時に一括で Tarkov.dev からアイテム一覧を取得してキャッシュ。
    """
    global ITEM_NAMES, ITEM_NAME_TO_ID

    query = """
    query {
      items {
        id
        name
        shortName
        normalizedName
      }
    }
    """
    try:
        print("tarkov.dev からアイテム一覧を取得中…")
        r = requests.post(TARKOV_DEV_GQL, json={"query": query}, timeout=60)
        r.raise_for_status()
        data = r.json()
        items = data.get("data", {}).get("items", [])
        names = []
        mapping = {}

        for it in items:
            _id = it.get("id")
            # 表示名は name（なければ shortName や normalizedName）
            name = it.get("name") or it.get("shortName") or it.get("normalizedName")
            if not _id or not name:
                continue
            names.append(name)
            mapping[name] = _id

        ITEM_NAMES = names
        ITEM_NAME_TO_ID = mapping
        print(f"アイテム取得完了: {len(ITEM_NAMES)} 件")
    except Exception as e:
        print("アイテム一覧取得に失敗しました:", e)


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
# アイテム詳細取得 (IDベース)
# =========================
def get_item_detail_by_id(item_id: str):
    """
    Tarkov.dev から item ID を使って詳細を取得。
    """
    query = """
    query($id: ID!) {
      items(id: $id) {
        id
        name
        usedInTasks {
          id
          name
          count
        }
      }
    }
    """
    try:
        r = requests.post(
            TARKOV_DEV_GQL,
            json={"query": query, "variables": {"id": item_id}},
            timeout=30,
        )
        r.raise_for_status()
        j = r.json()
        items = j.get("data", {}).get("items", [])
        if items:
            return items[0]
    except Exception as e:
        print("get_item_detail_by_id エラー:", e)
    return None


def get_item_detail_by_name(name: str):
    """
    万が一 ID が取れなかった場合用のフォールバック (nameベース)。
    """
    query = """
    query($name: String!) {
      items(name: $name) {
        id
        name
        usedInTasks {
          id
          name
          count
        }
      }
    }
    """
    try:
        r = requests.post(
            TARKOV_DEV_GQL,
            json={"query": query, "variables": {"name": name}},
            timeout=30,
        )
        r.raise_for_status()
        j = r.json()
        items = j.get("data", {}).get("items", [])
        if items:
            return items[0]
    except Exception as e:
        print("get_item_detail_by_name エラー:", e)
    return None


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
    fetch_items()


@client.event
async def on_message(message: discord.Message):
    # 自分自身のメッセージは無視
    if message.author == client.user:
        return

    content = message.content.strip()

    # 簡易ヘルプ
    if content.lower().startswith("!help") or content.lower().startswith("!tarkov"):
        txt = (
            "Tarkov item BOT 使い方\n"
            "`!price <アイテム名>` でフリマ価格とタスク/ハイドアウト情報を表示します。\n"
            "例: `!price LEDX` `!price salewa`\n"
        )
        await message.channel.send(txt)
        return

    # price コマンド以外はスルー
    if not content.lower().startswith("!price"):
        return

    query_text = content[6:].strip()  # "!price" の後ろ
    if not query_text:
        await message.channel.send("使い方：`!price <アイテム名>` の形式で入力してください。\n例：`!price LEDX`")
        return

    # 1) あいまい検索で正式名称を推定
    matched_name, score = fuzzy_match(query_text)
    if not matched_name:
        await message.channel.send("アイテム候補が見つかりませんでした。もう少し正確に入力してみてください。")
        return

    if score < FUZZY_THRESHOLD:
        await message.channel.send(f"もしかして: **{matched_name}** (類似度 {score})\nもう少し正確な名前を入力してみてください。")
        return

    # 2) ID ベースで詳細取得
    item_id = ITEM_NAME_TO_ID.get(matched_name)
    detail = None
    if item_id:
        detail = get_item_detail_by_id(item_id)

    # 3) 念のため name ベースでもフォールバック
    if not detail:
        detail = get_item_detail_by_name(matched_name)

    if not detail:
        await message.channel.send(f"詳細取得失敗: {matched_name}")
        return

    official_name = detail.get("name", matched_name)

    # 4) タスク判定 (tarkov.dev の usedInTasks と手動テーブルの両方を利用)
    used_in_tasks = detail.get("usedInTasks") or []
    auto_task_required = bool(used_in_tasks)
    manual_task_required = TASK_ITEMS.get(official_name, False)
    is_task_required = auto_task_required or manual_task_required

    if is_task_required:
        total_count = sum((t.get("count") or 0) for t in used_in_tasks) if used_in_tasks else 0
        if total_count > 0:
            task_text = f"タスク必要: ✅（合計 {total_count} 個）"
        else:
            task_text = "タスク必要: ✅"
    else:
        task_text = "タスク必要: ❌"

    # 5) ハイドアウト判定
    is_hideout_item = HIDEOUT_ITEMS.get(official_name, False)
    hideout_text = "ハイドアウト使用: ✅" if is_hideout_item else "ハイドアウト使用: ❌"

    # 6) 価格情報 (Tarkov Market)
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

    # 7) Embed で表示
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
