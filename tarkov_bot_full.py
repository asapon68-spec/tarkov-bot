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
# Tarkov Market API URL
# =========================
TARKOV_MARKET_ITEM_URL = "https://api.tarkov-market.app/api/v1/item?q={}&x-api-key={}"

# Discord Intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# -------------------------
# エイリアス辞書（日本語名 / 略称 → 公式英語名）
#   ここをどんどん増やしていけば日本語検索が超強くなる
# -------------------------
ALIASES = {
    # --- ルートアイテムの例 ---
    "42": "42 Signature Blend English Tea",
    "42シグニチャーブレンド": "42 Signature Blend English Tea",
    "英国紅茶": "42 Signature Blend English Tea",

    "アポロ": "Apollo Soyuz cigarettes",
    "Apollo": "Apollo Soyuz cigarettes",
    "アポロソユーズ": "Apollo Soyuz cigarettes",

    "アラミド": "Aramid fiber fabric",
    "アラミド繊維の生地": "Aramid fiber fabric",
    "Aramid": "Aramid fiber fabric",

    "BEARバディ": "BEAR Buddy plush toy",
    "BEAR Buddy": "BEAR Buddy plush toy",

    "DrLupo": "Can of Dr. Lupo's coffee beans",
    "DrLupo's": "Can of Dr. Lupo's coffee beans",
    "ルポコーヒー": "Can of Dr. Lupo's coffee beans",

    # --- 医療例 ---
    "LEDX": "LEDX Skin Transilluminator",
    "レドックス": "LEDX Skin Transilluminator",
    "静脈発見器": "LEDX Skin Transilluminator",

    "Salewa": "Salewa first aid kit",
    "サレワ": "Salewa first aid kit",

    # --- 有名アイテム例 ---
    "ガスアナ": "Gas analyzer",
    "ガスアナライザー": "Gas analyzer",
    "GasAn": "Gas analyzer",

    "グラボ": "Graphics card",
    "GPU": "Graphics card",
    "Graphics card": "Graphics card",

    "フラッシュドライブ": "Secure Flash drive",
    "Flash drive": "Secure Flash drive",

    # 必要に応じてここへどんどん追加していく
}

# -------------------------
# タスク必要情報
#   official_name: [ {task, count, fir}, ... ]
#   ※順番は Wiki の記述順にしてある
# -------------------------
TASK_REQUIREMENTS = {
    # 例1: 42 Signature Blend English Tea
    "42 Signature Blend English Tea": [
        {"task": "Collector", "count": 1, "fir": True},
    ],

    # 例2: Apollo Soyuz cigarettes（タスク無し例）
    "Apollo Soyuz cigarettes": [
        # ここは Wiki 上タスク無しなら空のままでもOK
        # 何も入れなければ「タスクに必要: なし」と表示される
    ],

    # 例3: Aramid fiber fabric
    "Aramid fiber fabric": [
        {"task": "Textile - Part1", "count": 5, "fir": True},
    ],

    # 例4: Gas analyzer（代表的なタスク持ち）
    "Gas analyzer": [
        {"task": "Sanitary Standards - Part1", "count": 1, "fir": False},
        {"task": "Sanitary Standards - Part2", "count": 2, "fir": False},
        {"task": "Network Provider - Part1", "count": 4, "fir": False},
    ],

    # 例5: LEDX
    "LEDX Skin Transilluminator": [
        {"task": "Private Clinic", "count": 1, "fir": False},
        {"task": "Crisis", "count": 2, "fir": False},
    ],

    # 例6: BEAR Buddy plush toy
    "BEAR Buddy plush toy": [
        {"task": "Collector", "count": 1, "fir": True},
    ],

    # ここを、あなたが貼ってくれた Wiki 情報を元に
    # どんどん増やしていくイメージ。
    # 「タスク名そのまま」「個数」「(in raid) の有無」を見て追加する。
}

# -------------------------
# 表示用 Wiki リンク（任意）
#   正確なURLが分かるものだけ入れてOK
# -------------------------
WIKI_LINKS = {
    # 例としていくつかだけ
    "42 Signature Blend English Tea": "https://wikiwiki.jp/eft/42%20Signature%20Blend%20English%20Tea",
    "Gas analyzer": "https://wikiwiki.jp/eft/Gas%20analyzer",
    "LEDX Skin Transilluminator": "https://wikiwiki.jp/eft/LEDX%20Skin%20Transilluminator",
    # 正しいURLがわかるものを少しずつ足していけばOK
}

# -------------------------
# Fuzzy 用アイテム名リスト
#   ALIASES の official_name + そのまま official_name を集約
# -------------------------
ITEM_NAMES = set()

def init_items():
    """起動時に、あいまい検索対象の official_name リストを作る"""
    global ITEM_NAMES
    # ALIASES の value（公式英名）
    for off in ALIASES.values():
        ITEM_NAMES.add(off)
    # TASK_REQUIREMENTS に定義されている official_name も追加
    for off in TASK_REQUIREMENTS.keys():
        ITEM_NAMES.add(off)
    ITEM_NAMES = sorted(ITEM_NAMES)
    print(f"アイテム候補数: {len(ITEM_NAMES)}")

# -------------------------
# あいまい検索 + 候補リスト生成
# -------------------------
def search_candidates(user_input: str, limit: int = 5):
    """
    ユーザー入力から official_name 候補リストを返す。
    戻り値: [(official_name, score), ...] （score降順）
    """
    if not ITEM_NAMES:
        return []

    # 検索対象文字列の候補：
    #   - ALIASES のキー（日本語/略称）
    #   - official_name（英語正式名）
    search_space = set(ALIASES.keys()) | set(ITEM_NAMES)

    results = process.extract(
        user_input,
        list(search_space),
        scorer=fuzz.WRatio,
        limit=limit
    )

    # official_name ごとにスコア最大値を集計
    aggregated = {}
    for cand, score, _ in results:
        official = ALIASES.get(cand, cand)
        if official not in aggregated or aggregated[official] < score:
            aggregated[official] = score

    # (official_name, score) のリストへ
    items = sorted(aggregated.items(), key=lambda x: x[1], reverse=True)
    return items

# ユーザーごとの選択待ち状態
PENDING_SELECTION = {}
# 形式:
# PENDING_SELECTION[user_id] = {
#     "candidates": [ (official_name, score), ... ],
#     "original_query": "ユーザーが最初に打った文字列"
# }

# -------------------------
# Tarkov Market 価格取得
# -------------------------
def get_price_from_tarkov_market(official_name: str):
    """
    Tarkov Market API から価格情報を取得。
    APIキーが未設定なら None。
    """
    if not TARKOV_MARKET_API_KEY:
        return None

    try:
        url = TARKOV_MARKET_ITEM_URL.format(
            requests.utils.quote(official_name),
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

# -------------------------
# Discord イベント
# -------------------------
@client.event
async def on_ready():
    print(f"Bot 起動: {client.user} (id: {client.user.id})")
    init_items()

@client.event
async def on_message(message: discord.Message):
    # 自分自身は無視
    if message.author == client.user:
        return

    user_id = message.author.id
    content = message.content.strip()

    # まず、「候補選択待ち」の状態を処理
    if user_id in PENDING_SELECTION:
        state = PENDING_SELECTION[user_id]

        # 数字だけのメッセージなら候補選択として扱う
        if content.isdigit():
            idx = int(content) - 1
            candidates = state["candidates"]
            if 0 <= idx < len(candidates):
                official_name, score = candidates[idx]
                # 選択が決まったので状態解除
                del PENDING_SELECTION[user_id]
                await send_item_info(message, state["original_query"], official_name, score)
                return
            else:
                await message.channel.send("番号が範囲外です。1〜{} の番号で選択してください。".format(len(candidates)))
                return
        else:
            # 別のコマンドを打ったと判断して状態解除
            del PENDING_SELECTION[user_id]
            # そのまま下の通常処理へ続行

    # ヘルプ
    if content.lower().startswith("!help"):
        txt = (
            "Tarkov item BOT 使い方\n"
            "`!アイテム名` でフリマ価格とタスク情報を表示します。\n"
            "例: `!LEDX` `!ガスアナ` `!グラボ`\n"
        )
        await message.channel.send(txt)
        return

    # コマンドフォーマット: 先頭が "!"
    if not content.startswith("!"):
        return

    query_text = content[1:].strip()  # 先頭の "!" を除去
    if not query_text:
        await message.channel.send("使い方：`!アイテム名` の形式で入力してください。\n例：`!LEDX` `!グラボ`")
        return

    # あいまい検索で候補を取得
    candidates = search_candidates(query_text, limit=5)
    if not candidates:
        await message.channel.send("それっぽいアイテムが見つかりませんでした。別の名前で試してみてください。")
        return

    # 上位結果
    top_name, top_score = candidates[0]

    # 自動確定できるかどうかの判断
    if len(candidates) == 1 and top_score >= FUZZY_THRESHOLD:
        # 候補1件・スコア高い → そのまま確定
        await send_item_info(message, query_text, top_name, top_score)
        return

    if len(candidates) >= 2:
        second_score = candidates[1][1]
    else:
        second_score = 0

    # スコア差が十分 & スコア自体もそこそこ高い → 自動確定
    if top_score >= FUZZY_THRESHOLD and (top_score - second_score) >= 20:
        await send_item_info(message, query_text, top_name, top_score)
        return

    # 自動確定が微妙な場合 → 質問形式で候補提示
    lines = ["候補が複数あります。どれを表示しますか？"]
    for i, (name, score) in enumerate(candidates, start=1):
        lines.append(f"{i}. {name}（類似度 {score}）")
    lines.append("番号を半角数字で送ってください。例：`1`")

    await message.channel.send("\n".join(lines))

    # このユーザーを「選択待ち状態」にする
    PENDING_SELECTION[user_id] = {
        "candidates": candidates,
        "original_query": query_text,
    }

# -------------------------
# アイテム情報を実際に Embed で送る処理
# -------------------------
async def send_item_info(message: discord.Message, query_text: str, official_name: str, score: int):
    """確定した official_name を元に、価格＋タスク情報をEmbedで送る"""

    # 価格情報
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

        profit = 0
        profit_s = "算出不可"
        try:
            if avg and trader_price:
                profit = int(avg) - int(trader_price)
                sign = "+" if profit >= 0 else ""
                profit_s = f"{sign}{profit:,}₽"
        except Exception:
            pass

        price_text = (
            f"フリマ平均: {avg_s}\n"
            f"トレーダー最高買取: {trader_name}（{trader_price_s}）\n"
            f"差額: {profit_s}"
        )
    else:
        price_text = "価格情報: 取得不可（APIキー未設定か、対象外アイテムの可能性）"

    # タスク情報
    tasks = TASK_REQUIREMENTS.get(official_name, [])
    if tasks:
        lines = []
        for t in tasks:
            name = t.get("task", "Unknown Task")
            count = t.get("count", 0)
            fir = t.get("fir", False)
            fir_txt = "FIR必要" if fir else "FIR不要"
            lines.append(f"・{name}: {count}個（{fir_txt}）")
        task_text = "\n".join(lines)
    else:
        task_text = "なし"

    # Wiki リンク（あれば）
    wiki_url = WIKI_LINKS.get(official_name)
    if wiki_url:
        wiki_text = wiki_url
    else:
        wiki_text = "（未登録）"

    # Embed 作成
    embed = discord.Embed(
        title=official_name,
        description=f"検索ワード: `{query_text}` / マッチ: 類似度 {score}",
        color=0x00FF00
    )

    embed.add_field(name="タスクに必要", value=task_text, inline=False)
    embed.add_field(name="価格情報", value=price_text, inline=False)
    embed.add_field(name="Wiki", value=wiki_text, inline=False)

    footer_parts = []
    if TWITCH_URL:
        footer_parts.append(f"✨ Follow my Twitch! → {TWITCH_URL} ✨")
    footer_parts.append("Price data from Tarkov Market")

    embed.set_footer(text=" | ".join(footer_parts))

    await message.channel.send(embed=embed)

# -------------------------
# 実行
# -------------------------
if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
