import os
import requests
from dotenv import load_dotenv
from rapidfuzz import process, fuzz
import discord

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN").strip()
TARKOV_MARKET_API_KEY = os.getenv("TARKOV_MARKET_API_KEY","").strip()
TWITCH_URL = os.getenv("TWITCH_URL","").strip()
FUZZY_THRESHOLD = int(os.getenv("FUZZY_THRESHOLD","60"))

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# アイテムリスト
ITEM_NAMES = []
ITEM_NAME_TO_ID = {}

# タスク必要アイテム例
TASK_ITEMS = {
    "LEDX": True,
    "Salewa": True,
    "Gas Analyzer": True
}

# ハイドアウト使用アイテム例
HIDEOUT_ITEMS = [
    "Thermal Paste",
    "LEDX",
    "Medstation"
]

# アイテム取得
def fetch_items():
    global ITEM_NAMES, ITEM_NAME_TO_ID
    query = """
    query { items { id name normalizedName } }
    """
    try:
        r = requests.post("https://api.tarkov.dev/graphql", json={"query": query}, timeout=30)
        items = r.json().get("data", {}).get("items", [])
        for it in items:
            name = it.get("name") or it.get("normalizedName")
            if name:
                ITEM_NAMES.append(name)
                ITEM_NAME_TO_ID[name] = it.get("id")
        print(f"アイテム取得完了: {len(ITEM_NAMES)} 件")
    except:
        print("アイテム取得失敗")

# あいまい検索
def fuzzy_match(user_input):
    match = process.extractOne(user_input, ITEM_NAMES, scorer=fuzz.WRatio)
    if match:
        name, score, _ = match
        return name, int(score)
    return None, 0

# アイテム詳細取得
def get_item_detail(name_or_id):
    query = """
    query($name:String,$id:ID){
      items(name:$name,id:$id){id name usedInTasks{id name count}}
    }
    """
    try:
        r = requests.post("https://api.tarkov.dev/graphql", json={"query":query,"variables":{"name":name_or_id,"id":name_or_id}}, timeout=30)
        items = r.json().get("data", {}).get("items", [])
        if items: return items[0]
    except:
        return None
    return None

# 価格取得
def get_price(name):
    if not TARKOV_MARKET_API_KEY: return None
    url = f"https://api.tarkov-market.app/api/v1/item?q={requests.utils.quote(name)}&x-api-key={TARKOV_MARKET_API_KEY}"
    try:
        r = requests.get(url, timeout=15)
        data = r.json()
        if data: return data[0]
    except:
        return None
    return None

@client.event
async def on_ready():
    print(f"Bot 起動: {client.user}")
    fetch_items()

@client.event
async def on_message(message):
    if message.author == client.user: return
    content = message.content.strip()
    if content.startswith("!price"):
        query_text = content.replace("!price","").strip()
        if not query_text:
            await message.channel.send("使い方：`!price <アイテム名>`")
            return
        name, score = fuzzy_match(query_text)
        if not name or score < FUZZY_THRESHOLD:
            await message.channel.send(f"候補: {name} (score:{score}) — 類似度低")
            return
        detail = get_item_detail(name)
        if not detail:
            await message.channel.send(f"詳細取得失敗: {name}")
            return

        # タスク判定
        is_task_item = TASK_ITEMS.get(name, False)
        task_text = "タスク必要: ✅" if is_task_item else "タスク必要: ❌"

        # ハイドアウト判定
        is_hideout_item = name in HIDEOUT_ITEMS
        hideout_text = "ハイドアウト使用: ✅" if is_hideout_item else "ハイドアウト使用: ❌"

        # 価格情報
        price_data = get_price(name)
        if price_data:
            avg = price_data.get("avg24hPrice") or price_data.get("price") or 0
            trader_name = price_data.get("traderName") or price_data.get("trader")
            trader_price = price_data.get("traderPrice") or price_data.get("trader_price") or 0
            price_text = f"フリマ平均: {int(avg):,}₽\n{trader_name or '----'} 買取: {int(trader_price):,}₽"
        else:
            price_text = "価格情報: 取得不可（APIキー未設定）"

        embed = discord.Embed(title=detail.get("name",name), color=0x00ff00)
        embed.add_field(name="アイテム情報", value=f"{task_text}\n{hideout_text}", inline=False)
        embed.add_field(name="価格情報", value=price_text, inline=False)
        if TWITCH_URL:
            embed.set_footer(text=f"Powered by {TWITCH_URL}")
        await message.channel.send(embed=embed)

client.run(DISCORD_TOKEN)
