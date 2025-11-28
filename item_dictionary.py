# item_dictionary.py
# Escape from Tarkov アイテム辞書（日本語・英語・略称 対応）

CANONICAL_ITEMS = [

    # ======================================================
    # 🔥 レア・高額ルート
    # ======================================================

    {
        "name": "LEDX Skin Transilluminator",
        "aliases": [
            "ledx", "reox", "レドックス", "レッドックス", "レドエックス",
            "ledx 静脈", "光るやつ", "医療レドックス"
        ],
    },
    {
        "name": "Graphics card",
        "aliases": ["gpu", "グラボ", "ぐらぼ", "graphics", "graphic card", "グラフィックボード"],
    },
    {
        "name": "Physical Bitcoin",
        "aliases": ["bitcoin", "btc", "ビットコイン", "ビッコ", "コイン", "0.2btc"],
    },
    {
        "name": "Red Rebel ice pick",
        "aliases": ["red rebel", "レッドレベル", "レッレベ", "レドレベ", "アイスピッケル"],
    },
    {
        "name": "Keytool",
        "aliases": ["keytool", "キー工具", "キーケース", "キー用ツール"],
    },
    {
        "name": "Item Case",
        "aliases": ["item case", "アイテムケース", "アイテムケ", "アイケ"],
    },
    {
        "name": "Weapon Case",
        "aliases": ["weapon case", "武器ケース", "武器ケ"],
    },
    {
        "name": "THICC Weapon Case",
        "aliases": ["thicc weapon case", "thicc武器ケース", "thicc武器", "シック武器ケース"],
    },
    {
        "name": "THICC Item Case",
        "aliases": ["thicc item case", "thiccアイテムケース", "シックケース", "シックアイテム"],
    },

    # ======================================================
    # 🦁 置物・トレードアイテム
    # ======================================================

    {
        "name": "Bronze lion figurine",
        "aliases": ["bronze lion", "lion", "ライオン", "らいおん"],
    },
    {
        "name": "Cat figurine",
        "aliases": ["cat", "猫の置物", "ねこの置物", "ネコ", "キャット"],
    },
    {
        "name": "Horse figurine",
        "aliases": ["horse", "馬像", "うま像", "うまの置物"],
    },
    {
        "name": "Raven figurine",
        "aliases": ["raven", "レイヴン", "カラス置物"],
    },
    {
        "name": "GP coin",
        "aliases": ["gp", "gp coin", "gpコイン", "金コイン"],
    },
    {
        "name": "Chain with Prokill medallion",
        "aliases": ["prokill", "プロキル", "プロキルチェーン"],
    },
    {
        "name": "Golden neck chain",
        "aliases": ["goldchain", "金チェーン", "gold chain", "金ネックレス"],
    },
    {
        "name": "Antique teapot",
        "aliases": ["ティーポット", "ポット", "古いポット"],
    },
    {
        "name": "Antique vase",
        "aliases": ["vase", "花瓶", "骨董花瓶"],
    },

    # ======================================================
    # 📦 クラフト素材・工業品
    # ======================================================

    {
        "name": "Aramid fiber fabric",
        "aliases": ["aramid", "アラミド", "アラミド繊維"],
    },
    {
        "name": "Cordura polyamide fabric",
        "aliases": ["cordura", "コーデュラ"],
    },
    {
        "name": "Fleece fabric",
        "aliases": ["fleece", "フリース"],
    },
    {
        "name": "Ripstop fabric",
        "aliases": ["ripstop", "リップストップ"],
    },
    {
        "name": "Paracord",
        "aliases": ["パラコード", "para code"],
    },
    {
        "name": "FP-100 filter absorber",
        "aliases": ["fp-100", "fp100"],
    },
    {
        "name": "Water filter",
        "aliases": ["water filter", "ウォーターフィルター"],
    },
    {
        "name": "Electric motor",
        "aliases": ["motor", "モーター"],
    },
    {
        "name": "Fuel conditioner",
        "aliases": ["fuel conditioner", "燃料コンディショナー"],
    },
    {
        "name": "Car battery",
        "aliases": ["car battery", "車バッテリー", "バッテリー"],
    },
    {
        "name": "Spark plug",
        "aliases": ["spark plug", "スパークプラグ"],
    },
    {
        "name": "Wires",
        "aliases": ["wires", "ワイヤー", "電線"],
    },
    {
        "name": "Insulating tape",
        "aliases": ["tape", "青テープ", "絶縁テープ"],
    },
    {
        "name": "Duct tape",
        "aliases": ["duct tape", "ガムテ", "銀ガムテ"],
    },

    # ======================================================
    # 🧪 医療・薬品
    # ======================================================

    {
        "name": "Grizzly First Aid Kit",
        "aliases": ["grizzly", "グリズリー"],
    },
    {
        "name": "CMS surgical kit",
        "aliases": ["cms", "c.m.s", "手術キット"],
    },
    {
        "name": "Surv12 field surgical kit",
        "aliases": ["surv12", "サーブ12", "サブ12"],
    },
    {
        "name": "Salewa First Aid Kit",
        "aliases": ["salewa", "サレワ", "サリワ"],
    },
    {
        "name": "IFAK personal tactical first aid kit",
        "aliases": ["ifak", "アイファク"],
    },
    {
        "name": "AFAK personal tactical first aid kit",
        "aliases": ["afak", "エーファク"],
    },
    {
        "name": "Morphine injector",
        "aliases": ["morphine", "モルヒネ"],
    },
    {
        "name": "SJ6 combat stimulant injector",
        "aliases": ["sj6", "スジャ6", "走る薬"],
    },
    {
        "name": "Propital regenerative stimulant injector",
        "aliases": ["propital", "プロピタル"],
    },

    # ======================================================
    # 🗝 キー類（重要）
    # ======================================================

    {
        "name": "Factory exit key",
        "aliases": ["factory key", "工場キー", "赤鍵", "旧工場"],
    },
    {
        "name": "Dorm room 206 Key",
        "aliases": ["206", "206 key", "206寮"],
    },
    {
        "name": "Dorm room 214 Key",
        "aliases": ["214", "214 key"],
    },
    {
        "name": "Dorm room 105 Key",
        "aliases": ["105", "105 key"],
    },
    {
        "name": "Sanitar's office key",
        "aliases": ["sanitar key", "サニタールーム"],
    },

    # ======================================================
    # 🔫 武器（アサルト / DMR / SMG）
    # ======================================================

    {
        "name": "Kalashnikov AK-74 5.45x39 assault rifle",
        "aliases": ["ak74", "ak 74", "エーケー74", "赤ak", "ak74n", "ak74m"],
    },
    {
        "name": "Kalashnikov AK-74M 5.45x39 assault rifle",
        "aliases": ["ak74m", "74m"],
    },
    {
        "name": "Kalashnikov AK-74N 5.45x39 assault rifle",
        "aliases": ["ak74n", "74n"],
    },
    {
        "name": "Kalashnikov AKS-74U 5.45x39 assault rifle",
        "aliases": ["aks74u", "クリンコフ", "くりんこふ", "短ak"],
    },

    {
        "name": "Colt M4A1 5.56x45 assault rifle",
        "aliases": ["m4", "m4a1", "m4a1 carbine", "エムフォー"],
    },
    {
        "name": "HK 416A5 5.56x45 assault rifle",
        "aliases": ["hk416", "416", "416a5"],
    },
    {
        "name": "FN SCAR-L 5.56x45 assault rifle",
        "aliases": ["scar l", "スカーl", "mk16"],
    },
    {
        "name": "FN SCAR-H 7.62x51 assault rifle",
        "aliases": ["scar h", "スカーh", "mk17"],
    },

    # ======================================================
    # 💥 弾薬（Ammo）
    # ======================================================

    {
        "name": "5.45x39mm BP",
        "aliases": ["545bp", "bp545", "5.45bp"],
    },
    {
        "name": "5.45x39mm BT",
        "aliases": ["545bt", "bt545"],
    },
    {
        "name": "5.45x39mm PP",
        "aliases": ["545pp", "pp545"],
    },

    {
        "name": "7.62x39mm BP",
        "aliases": ["762bp", "bp762"],
    },
    {
        "name": "7.62x39mm PS",
        "aliases": ["762ps", "ps762"],
    },

    {
        "name": "5.56x45mm M855",
        "aliases": ["855", "m855"],
    },
    {
        "name": "5.56x45mm M855A1",
        "aliases": ["855a1", "m855a1", "a1"],
    },
    {
        "name": "5.56x45mm M995",
        "aliases": ["995", "m995"],
    },

    {
        "name": "7.62x51mm M80",
        "aliases": ["m80", "m80ball"],
    },
    {
        "name": "7.62x51mm M61",
        "aliases": ["m61", "m61ap"],
    },
    {
        "name": "7.62x51mm M62",
        "aliases": ["m62", "m62tracer"],
    },

    {
        "name": "4.6x30mm AP SX",
        "aliases": ["ap sx", "apsx", "4.6ap"],
    },

    {
        "name": "9x19mm AP 6.3",
        "aliases": ["ap63", "6.3", "ap6.3"],
    },
    {
        "name": "9x19mm PST gzh",
        "aliases": ["pst", "pstgzh"],
    },
    {
        "name": "9x19mm RIP",
        "aliases": ["rip", "rip9"],
    },

    {
        "name": ".45 ACP AP",
        "aliases": ["45ap", "ap45"],
    },

    {
        "name": ".300 Blackout AP",
        "aliases": ["300ap", "ap300"],
    },

    {
        "name": ".338 Lapua Magnum AP",
        "aliases": ["338ap", "ap338"],
    },
]

# 辞書生成
ITEM_ALIASES = {}

for item in CANONICAL_ITEMS:
    name = item["name"]
    for alias in item["aliases"]:
        ITEM_ALIASES[alias.strip().lower()] = name
