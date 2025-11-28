import os
import requests
from dotenv import load_dotenv
from rapidfuzz import process, fuzz
import discord
from typing import Tuple, List, Optional, Dict

# =============== 環境変数読み込み ===============
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
TARKOV_MARKET_API_KEY = os.getenv("TARKOV_MARKET_API_KEY", "").strip()
TWITCH_URL = os.getenv("TWITCH_URL", "").strip()
FUZZY_THRESHOLD = int(os.getenv("FUZZY_THRESHOLD", "70"))  # 類似度しきい値（0-100）

if not DISCORD_TOKEN:
    raise SystemExit("DISCORD_TOKEN が設定されていません (.env を確認して下さい)")

# =============== Tarkov Market API URL ===============
TARKOV_MARKET_ITEM_URL = "https://api.tarkov-market.app/api/v1/item?q={}&x-api-key={}"

# =============== Discord クライアント設定 ===============
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# =============== ALIASES 読み込み ===============
try:
    from aliases import ALIASES  # 日本語 / 略称 → 正式英語名
except ImportError:
    ALIASES = {}

ALIAS_KEYS = list(ALIASES.keys())


# =============== 名前解決関連関数 ===============
def resolve_from_aliases(query: str) -> Tuple[Optional[str], Optional[List[str]]]:
    """
    日本語 / 略称 / 英語 を ALIASES から解決する。
    戻り値:
      (official_name, None)  … 1件に確定
      (None, [候補…])       … 複数候補のため質問が必要
      (None, None)           … 辞書からは見つからず
    """
    if not ALIASES:
        return None, None

    q = query.strip().lower()
    if not q:
        return None, None

    # 1) 完全一致
    if q in ALIASES:
        return ALIASES[q], None

    # 2) 部分一致（例：「アラミド」→「アラミド繊維の生地」など）
    candidates = {ALIASES[key] for key in ALIAS_KEYS if q in key}
    if len(candidates) == 1:
        return next(iter(candidates)), None
    if len(candidates) > 1:
        # 複数あれば、質問用候補リストを返す
        return None, sorted(candidates)

    # 3) fuzzy（曖昧検索）
    match = process.extractOne(q, ALIAS_KEYS, scorer=fuzz.WRatio)
    if match:
        key, score, _ = match
        if score >= FUZZY_THRESHOLD:
            return ALIASES[key], None
        else:
            # スコアが低い場合は候補としていくつか出す
            matches = process.extract(q, ALIAS_KEYS, scorer=fuzz.WRatio, limit=5)
            good = [ALIASES[k] for k, s, _ in matches if s >= FUZZY_THRESHOLD - 10]
            good = sorted(set(good))
            if len(good) == 1:
                return good[0], None
            if good:
                return None, good

    return None, None


# ユーザーごとの「どれを選ぶ？」状態を持つ
PENDING_SELECTION: Dict[tuple, List[str]] = {}


# =============== Tarkov Market 価格取得 ===============
def get_price_from_tarkov_market(query_name: str):
    """
    Tarkov Market API から価格情報を取得。
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


# =============== Discord イベント ===============
@client.event
async def on_ready():
    print(f"Bot 起動: {client.user} (id: {client.user.id})")


@client.event
async def on_message(message: discord.Message):
    # 自分自身は無視
    if message.author == client.user:
        return

    content = message.content.strip()

    # ---------- 数字だけの返信 = 候補からの選択 ----------
    key = (message.channel.id, message.author.id)
    if key in PENDING_SELECTION and content.isdigit():
        idx = int(content) - 1
        options = PENDING_SELECTION[key]
        if 0 <= idx < len(options):
            official_name = options[idx]
            del PENDING_SELECTION[key]
            await send_item_info(message, official_name, f"候補{idx+1}を選択")
            return
        else:
            await message.channel.send("番号が範囲外です。1 〜 {} で選んでください。".format(len(options)))
            return

    # ---------- ヘルプ ----------
    if content.lower().startswith("!help"):
        txt = (
            "🧰 **Tarkov Item BOT 使い方**\n"
            "```text\n"
            "!アイテム名\n"
            "例:  !ledx\n"
            "      !レドックス\n"
            "      !ガスアナ\n"
            "```\n"
            "日本語名 / 略称 / 英語名 どれでもOK（辞書にある範囲）。\n"
        )
        await message.channel.send(txt)
        return

    # ---------- プレフィックス '!' 以外は無視 ----------
    if not content.startswith("!"):
        return

    query_text = content[1:].strip()
    if not query_text:
        await message.channel.send("使い方：`!アイテム名` の形式で入力してください。\n例：`!ledx` `!グラボ`")
        return

    # 新しい検索なので、過去の候補状態は消す
    if key in PENDING_SELECTION:
        del PENDING_SELECTION[key]

    # 1) 日本語 / 略称 辞書から解決
    official_name, options = resolve_from_aliases(query_text)

    if options:
        # 候補が複数あるので、ユーザーに選んでもらう
        PENDING_SELECTION[key] = options
        lines = ["候補が複数見つかりました。番号で選んでください："]
        for i, name in enumerate(options, start=1):
            lines.append(f"{i}. {name}")
        await message.channel.send("\n".join(lines))
        return

    # 2) 辞書で決まらなかった場合は、そのままの文字列で API を叩く
    if not official_name:
        official_name = query_text

    await send_item_info(message, official_name, query_text)


async def send_item_info(message: discord.Message, official_name: str, query_text: str):
    """
    実際に Tarkov Market から情報を取って Embed を送る部分。
    """
    price_data = get_price_from_tarkov_market(official_name)

    if price_data:
        avg = price_data.get("avg24hPrice") or price_data.get("price") or 0
        trader_name = price_data.get("traderName") or price_data.get("trader") or "----"
        trader_price = price_data.get("traderPrice") or price_data.get("trader_price") or 0

        # 画像・Wikiリンク など
        icon_url = price_data.get("icon") or price_data.get("img") or None
        wiki_link = price_data.get("wikiLink") or price_data.get("wiki") or None

        # 数値の整形
        try:
            avg_i = int(avg)
            avg_s = f"{avg_i:,}₽"
        except Exception:
            avg_s = str(avg) if avg else "取得不可"

        try:
            trader_i = int(trader_price)
            trader_s = f"{trader_i:,}₽"
        except Exception:
            trader_s = str(trader_price) if trader_price else "取得不可"

        # 差額
        profit_s = "計算不可"
        try:
            if isinstance(avg, (int, float)) and isinstance(trader_price, (int, float)):
                diff = int(avg) - int(trader_price)
                profit_s = f"{diff:+,}₽"
        except Exception:
            pass

        price_text = (
            f"フリマ平均: {avg_s}\n"
            f"トレーダー最高買取価格: {trader_name}（{trader_s}）\n"
            f"差額: {profit_s}"
        )
    else:
        price_text = "価格情報: 取得不可（APIキー未設定 or アイテム未対応 or 検索ヒットなし）"
        icon_url = None
        wiki_link = None

    # Embed 作成
    embed = discord.Embed(
        title=official_name,
        description=f"検索ワード: `{query_text}`",
        color=0x00FF00
    )
    embed.add_field(name="価格情報", value=price_text, inline=False)

    if wiki_link:
        embed.add_field(name="Wiki", value=wiki_link, inline=False)

    if icon_url:
        embed.set_thumbnail(url=icon_url)

    # フッター（Twitch + Tarkov Market クレジット）
    if TWITCH_URL:
        footer_text = f"✨ Follow my Twitch! → {TWITCH_URL} ✨ | Data from Tarkov Market"
    else:
        footer_text = "Data from Tarkov Market"
    embed.set_footer(text=footer_text)

    await message.channel.send(embed=embed)


# =============== 実行 ===============
if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
