import os
import json
import discord
import requests
from rapidfuzz import process, fuzz

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
TWITCH_URL = os.getenv("TWITCH_URL", "https://www.twitch.tv/jagami_orochi")
FUZZY_THRESHOLD = 60
GITHUB_JSON_URL = os.getenv(
    "ITEM_JSON_URL",
    "https://raw.githubusercontent.com/asapon68-spec/tarkov-bot/main/items.json"
)

if not DISCORD_TOKEN:
    raise SystemExit("❌ DISCORD_TOKEN が設定されていません")


def load_items_from_github():
    try:
        print("📦 GitHub から items.json 読み込み中 ...")
        r = requests.get(GITHUB_JSON_URL, timeout=10)
        r.raise_for_status()
        print("✅ JSON ロード成功")
        return r.json()
    except Exception as e:
        print("❌ JSONロードエラー:", e)
        return {}


ITEM_DB = load_items_from_github()
ITEM_NAMES = list(ITEM_DB.keys())


def fuzzy_match(query):
    result = process.extract(query, ITEM_NAMES, scorer=fuzz.WRatio, limit=5)
    return [(name, score) for name, score, _ in result if score >= FUZZY_THRESHOLD]


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"🚀 BOT 起動: {client.user}")


@client.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip()
    if not content.startswith("!"):
        return

    query = content[1:].strip()
    matches = fuzzy_match(query)

    if not matches:
        await message.channel.send(f"❌ `{query}` に一致するアイテムがありませんでした。")
        return

    best_name, _ = matches[0]
    item = ITEM_DB[best_name]

    trader_text = "----"
    if isinstance(item.get("trader_price"), dict):
        trader_text = "\n".join(
            f"{name}: {value:,}₽" for name, value in item["trader_price"].items()
        )

    embed = discord.Embed(
        title=best_name,
        url=item.get("wiki", ""),
        description=f"🔍 検索: `{query}`\n🎯 一致: `{best_name}`",
        color=0x00AAFF,
    )

    if item.get("icon"):
        embed.set_thumbnail(url=item["icon"])

    embed.add_field(name="💰 買取価格", value=trader_text, inline=False)
    embed.add_field(
        name="📌 その他",
        value=(
            f"タスク必要： **{item.get('task', '❌')}**\n"
            f"ハイドアウト必要： **{item.get('hideout', '❌')}**"
        ),
        inline=False,
    )

    embed.set_footer(text=f"DB: GitHub JSON｜✨ FOLLOW → {TWITCH_URL}")
    await message.channel.send(embed=embed)


client.run(DISCORD_TOKEN)
