import os
import requests
from dotenv import load_dotenv
from rapidfuzz import process, fuzz
import discord
from collections import defaultdict

# =========================
# 環境変数読み込み
# =========================
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
TARKOV_MARKET_API_KEY = os.getenv("TARKOV_MARKET_API_KEY", "").strip()
TWITCH_URL = os.getenv("TWITCH_URL", "").strip()  # 例: https://twitch.tv/JagamiOrochi
FUZZY_THRESHOLD = int(os.getenv("FUZZY_THRESHOLD", "70"))  # 類似度しきい値

if not DISCORD_TOKEN:
    raise SystemExit("DISCORD_TOKEN が設定されていません (.env / Render の環境変数を確認)")

# =========================
# 定数
# =========================
TARKOV_MARKET_ITEM_URL = "https://api.tarkov-market.app/api/v1/item?q={}&x-api-key={}"

# Discord Intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# =========================
# 🔠 エイリアス辞書（日本語名 / 略称 対応）
#   ここをどんどん増やしていくイメージ
#   "検索に使われそうな文字列": "Tarkov Market での正式英語名"
# =========================
ALIASES = {
    # ---- 高額系例 ----
    "ledx": "LEDX Skin Transilluminator",
    "ledx 静脈発見器": "LEDX Skin Transilluminator",
    "レドックス": "LEDX Skin Transilluminator",
    "レドクス": "LEDX Skin Transilluminator",
    "静脈発見器": "LEDX Skin Transilluminator",

    "gpu": "Graphics card",
    "グラボ": "Graphics card",
    "グラフィックカード": "Graphics card",
    "グラフィックボード": "Graphics card",
    "graphics card": "Graphics card",

    "ビットコイン": "Physical Bitcoin",
    "btcコイン": "Physical Bitcoin",
    "0.2btc": "Physical Bitcoin",
    "bitcoin": "Physical Bitcoin",

    # ---- 医療系例 ----
    "サレワ": "Salewa first aid kit",
    "salewa": "Salewa first aid kit",
    "saleva": "Salewa first aid kit",

    "ガスアナ": "Gas analyzer",
    "ガスアナライザー": "Gas analyzer",
    "gasan": "Gas analyzer",
    "gas analyzer": "Gas analyzer",

    # ---- よくあるルート品 ----
    "金チェーン": "Golden neck chain",
    "goldchain": "Golden neck chain",
    "ゴルチェ": "Golden neck chain",

    "金ライオン": "Bronze lion figurine",
    "ライオン": "Bronze lion figurine",
    "lion": "Bronze lion figurine",

    "猫の置物": "Cat figurine",
    "cat": "Cat figurine",

    "gpコイン": "GP coin",
    "gp coin": "GP coin",

    # ---- 武器系サンプル ----
    "m4": "Colt M4A1 5.56x45 assault rifle",
    "m4a1": "Colt M4A1 5.56x45 assault rifle",
    "colt m4a1": "Colt M4A1 5.56x45 assault rifle",

    "ak74": "Kalashnikov AK-74 5.45x39 assault rifle",
    "ak-74": "Kalashnikov AK-74 5.45x39 assault rifle",
    "ak 74": "Kalashnikov AK-74 5.45x39 assault rifle",
    "ak-74n": "Kalashnikov AK-74N 5.45x39 assault rifle",
    "ak74n": "Kalashnikov AK-74N 5.45x39 assault rifle",

    "as val": "AS VAL 9x39 special assault rifle",
    "asval": "AS VAL 9x39 special assault rifle",
    "ヴァル": "AS VAL 9x39 special assault rifle",

    "vss": "VSS Vintorez 9x39 special sniper rifle",
    "vss vintorez": "VSS Vintorez 9x39 special sniper rifle",

    # ---- フラッシュドライブ ----
    "フラッシュドライブ": "Secure Flash drive",
    "usbフラッシュ": "Secure Flash drive",
    "secure flash drive": "Secure Flash drive",

    # ---- 必要に応じて自分で追加する欄 ----
    # "例）アラミド": "Aramid fiber fabric",
    # "例）アポロ": "Apollo Soyuz cigarettes",
}

# 正規化用（全部小文字にして比較）
def normalize_key(s: str) -> str:
    return s.strip().lower()


# ALIASES キー一覧（正規化済み）
ALIAS_KEY_TO_OFFICIAL = {normalize_key(k): v for k, v in ALIASES.items()}
ALIAS_KEYS = list(ALIAS_KEY_TO_OFFICIAL.keys())

# 会話状態: ユーザーに「どれ？」と聞いたときの候補保存
# key: (channel_id, user_id) -> {"original_query": str, "candidates": [official_name1, ...]}
PENDING_SELECTIONS = {}


# =========================
# アイテム候補探索（辞書 + あいまい検索）
# =========================
def find_item_candidates(user_input: str):
    """
    入力文字列から、ALIASES とあいまい検索で候補を探す。
    戻り値:
      - status == "ok"         → 一意に確定 (official_name, best_score)
      - status == "ambiguous"  → 候補が複数 (candidates(list), max_score)
      - status == "none"       → ヒットなし
    """
    text = user_input.strip()
    if not text:
        return ("none", None)

    norm = normalize_key(text)

    # 1) 完全一致（辞書キー）
    if norm in ALIAS_KEY_TO_OFFICIAL:
        official = ALIAS_KEY_TO_OFFICIAL[norm]
        return ("ok", (official, 100))

    # 2) あいまい検索 (RapidFuzz)
    if not ALIAS_KEYS:
        return ("none", None)

    results = process.extract(
        norm,
        ALIAS_KEYS,
        scorer=fuzz.WRatio,
        limit=5
    )

    # スコアしきい値でフィルタ
    filtered = [(key, score) for key, score, _ in results if score >= FUZZY_THRESHOLD]
    if not filtered:
        return ("none", None)

    # official_name ごとにグループ化
    by_official = defaultdict(list)
    for key, score in filtered:
        official = ALIAS_KEY_TO_OFFICIAL.get(key, None)
        if not official:
            continue
        by_official[official].append(score)

    if not by_official:
        return ("none", None)

    # グループごとに最大スコアを計算
    items = []
    for official, scores in by_official.items():
        items.append((official, max(scores)))

    # スコアでソート（高い順）
    items.sort(key=lambda x: x[1], reverse=True)

    if len(items) == 1:
        # 一意候補
        return ("ok", (items[0][0], items[0][1]))

    # 複数候補 → 曖昧
    best_score = items[0][1]
    return ("ambiguous", (items, best_score))


# =========================
# Tarkov Market 価格取得
# =========================
def get_price_from_tarkov_market(official_name: str):
    """
    Tarkov Market API から価格情報を取得。
    APIキーが設定されていない場合は None を返す。
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


# =========================
# Embed 生成
# =========================
def build_item_embed(
    original_query: str,
    official_name: str,
    match_score: int,
    price_data: dict | None
):
    """
    Discord Embed を組み立てて返す。
    - Wiki リンクをタイトルに埋め込み
    - 一番上に Twitch の宣伝
    - Tarkov Market からの価格情報
    """

    # Wiki URL（英語版想定。必要ならここを日本語Wiki用に書き換え可）
    wiki_title_name = official_name.replace(" ", "_")
    wiki_url = f"https://escapefromtarkov.fandom.com/wiki/{wiki_title_name}"

    embed = discord.Embed(
        title=official_name,  # タイトル自体がリンクになる
        url=wiki_url,
        color=0x00FFCC
    )

    # 🔹 一番上に Twitch URL をドーン！
    if TWITCH_URL:
        embed.description = f"✨ **Follow my Twitch! → {TWITCH_URL}** ✨\n\n"
    else:
        embed.description = ""

    # 🔹 検索情報
    embed.description += (
        f"🔍 **検索ワード**: `{original_query}`\n"
        f"🎯 **マッチ**: `{official_name}` (score {match_score})\n\n"
    )

    # 🔹 価格情報
    if price_data:
        avg = price_data.get("avg24hPrice") or price_data.get("price") or 0
        trader_name = price_data.get("traderName") or price_data.get("trader") or "----"
        trader_price = price_data.get("traderPrice") or price_data.get("trader_price") or 0

        # 数値整形
        def fmt(x):
            try:
                v = int(x)
                return f"{v:,}₽"
            except Exception:
                return "取得不可"

        avg_s = fmt(avg) if avg else "取得不可"
        trader_price_s = fmt(trader_price) if trader_price else "取得不可"

        # 差額計算
        profit_s = "計算不可"
        try:
            if avg and trader_price:
                p = int(avg) - int(trader_price)
                sign = "+" if p >= 0 else ""
                profit_s = f"{sign}{p:,}₽"
        except Exception:
            pass

        price_text = (
            f"**フリマ平均：** {avg_s}\n"
            f"**トレーダー最高買取価格：** {trader_name}（{trader_price_s}）\n"
            f"**差額：** {profit_s}"
        )
    else:
        price_text = (
            "価格情報を取得できませんでした。\n"
            "・Tarkov Market APIキー未設定\n"
            "・アイテム未対応\n"
            "・一時的な通信エラー\n"
            "の可能性があります。"
        )

    embed.add_field(name="💰 価格情報", value=price_text, inline=False)

    # 🔹 アイテム画像（あれば）
    if price_data:
        img_url = (
            price_data.get("imgBig")
            or price_data.get("img")
            or price_data.get("icon")
        )
        if img_url:
            embed.set_thumbnail(url=img_url)

    # 🔹 フッターにクレジット
    footer_text = "Prices via Tarkov Market (api.tarkov-market.app)"
    embed.set_footer(text=footer_text)

    return embed


# =========================
# Discord イベント
# =========================
@client.event
async def on_ready():
    print(f"Bot 起動: {client.user} (id: {client.user.id})")
    print(f"ALIASES 登録数: {len(ALIASES)} 件")
    print(f"FUZZY_THRESHOLD: {FUZZY_THRESHOLD}")


@client.event
async def on_message(message: discord.Message):
    # 自分自身は無視
    if message.author == client.user:
        return

    content = message.content.strip()

    # 1) ペンディング選択中かどうか（「1」「2」などの返信）
    if content.isdigit():
        key = (message.channel.id, message.author.id)
        if key in PENDING_SELECTIONS:
            data = PENDING_SELECTIONS.pop(key)
            candidates = data["candidates"]
            original_query = data["original_query"]

            idx = int(content) - 1
            if 0 <= idx < len(candidates):
                official_name, score = candidates[idx]
                await handle_resolved_item(message, original_query, official_name, score)
            else:
                await message.channel.send("番号が範囲外です。1 から選んでください。")
            return

    # 2) ヘルプ
    if content.lower().startswith("!help"):
        help_text = (
            "🧾 **Tarkov Item BOT 使い方**\n"
            "`!アイテム名` でフリマ価格を表示します。\n\n"
            "例:\n"
            "・`!ledx`\n"
            "・`!レドックス`\n"
            "・`!グラボ`\n"
            "・`!gas analyzer`\n\n"
            "※ ある程度の誤字、日本語名、略称も対応します。\n"
            "※ 候補が複数ある場合は、番号で選択してもらいます。"
        )
        await message.channel.send(help_text)
        return

    # 3) 検索コマンド: "!～～～"
    if not content.startswith("!"):
        return

    query = content[1:].strip()
    if not query:
        await message.channel.send("使い方：`!アイテム名` の形式で入力してください。\n例：`!ledx` `!グラボ`")
        return

    # アイテム候補探索
    status, info = find_item_candidates(query)

    if status == "none":
        await message.channel.send(
            f"アイテム候補が見つかりませんでした。\n"
            f"`{query}` は辞書に登録されていないか、類似度が低すぎます。\n"
            "・スペルを確認\n"
            "・英語名 / 日本語名 / 略称 を変えて再度お試しください。"
        )
        return

    if status == "ok":
        official_name, score = info
        await handle_resolved_item(message, query, official_name, score)
        return

    if status == "ambiguous":
        items, best_score = info  # items = [(official, score), ...]
        # 上位候補を最大 5 件まで表示
        max_show = min(len(items), 5)
        text_lines = ["候補が複数見つかりました。番号で選んでください：\n"]
        for i in range(max_show):
            name, score = items[i]
            text_lines.append(f"{i+1}. **{name}** (score {score})")

        text_lines.append("\n例: `1` と送信すると 1 番を選びます。")

        await message.channel.send("\n".join(text_lines))

        # ペンディング状態に保存
        key = (message.channel.id, message.author.id)
        PENDING_SELECTIONS[key] = {
            "original_query": query,
            "candidates": items[:max_show],
        }
        return


async def handle_resolved_item(message: discord.Message, original_query: str, official_name: str, score: int):
    """
    候補が一意に決まったときに呼ばれる処理。
    Tarkov Market から価格を取り Embed を送信。
    """
    price_data = get_price_from_tarkov_market(official_name)
    embed = build_item_embed(
        original_query=original_query,
        official_name=official_name,
        match_score=score,
        price_data=price_data,
    )
    await message.channel.send(embed=embed)


# =========================
# 実行
# =========================
if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
