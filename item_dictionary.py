# item_dictionary.py
# Escape from Tarkov - Item Alias Dictionary
# 日本語・略称・英語すべて → 正式アイテム名へ変換する辞書

# ========================================
# 基本レアアイテム
# ========================================

CANONICAL_ITEMS = [

    {
        "name": "LEDX Skin Transilluminator",
        "aliases": [
            "ledx", "reox", "レドックス", "レッドックス",
            "レドエックス", "ledx 静脈", "光るやつ", "医療レドックス"
        ],
    },
    {
        "name": "Graphics card",
        "aliases": [
            "gpu", "グラボ", "ぐらぼ", "graphics", "graphic card", "グラフィックボード"
        ],
    },
    {
        "name": "Physical Bitcoin",
        "aliases": [
            "bitcoin", "btc", "ビットコイン", "ビッコ", "コイン", "0.2btc"
        ],
    },
    {
        "name": "Red Rebel ice pick",
        "aliases": [
            "red rebel", "レッドレベル", "レッレベ", "レドレベ", "アイスピッケル"
        ],
    },
    {
        "name": "Keytool",
        "aliases": [
            "keytool", "キー工具", "キーケース", "キー用ツール"
        ],
    },
    {
        "name": "Item Case",
        "aliases": [
            "item case", "アイテムケース", "アイテムケ", "アイケ"
        ],
    },
    {
        "name": "Weapon Case",
        "aliases": [
            "weapon case", "武器ケース", "武器ケ"
        ],
    },
    {
        "name": "THICC Weapon Case",
        "aliases": [
            "thicc weapon case", "thicc武器ケース", "thicc武器", "シック武器ケース"
        ],
    },
    {
        "name": "THICC Item Case",
        "aliases": [
            "thicc item case", "thiccアイテムケース", "シックケース", "シックアイテム"
        ],
    },

    # ========================================
    # フィギュア系
    # ========================================

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

    # ========================================
    # 工業・クラフト素材
    # ========================================

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

    # ========================================
    # 医療系
    # ========================================

    {
        "name": "Grizzly First Aid Kit",
        "aliases": ["grizzly", "グリズリー"],
    },
    {
        "name": "CMS surgical kit",
        "aliases": ["cms", "手術キット"],
    },
    {
        "name": "Surv12 field surgical kit",
        "aliases": ["surv12", "サーブ12", "サブ12"],
    },
    {
        "name": "Salewa First Aid Kit",
        "aliases": ["salewa", "サレワ"],
    },
    {
        "name": "IFAK personal tactical first aid kit",
        "aliases": ["ifak", "アイファク"],
    },

    # ========================================
    # キー類
    # ========================================

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

]

# ========================================
# 武器・銃器類（AK / AR / DMR / SMG / LMG / Pistol）
# ========================================

CANONICAL_ITEMS += [

    # AK 系
    {
        "name": "Kalashnikov AK-74 5.45x39 assault rifle",
        "aliases": ["ak74", "ak 74", "エーケー74", "ak74n", "ak74m"],
    },
    {
        "name": "Kalashnikov AK-103 7.62x39 assault rifle",
        "aliases": ["ak103", "103"],
    },

    # AR系
    {
        "name": "Colt M4A1 5.56x45 assault rifle",
        "aliases": ["m4", "m4a1", "エムフォー"],
    },
    {
        "name": "HK 416A5 5.56x45 assault rifle",
        "aliases": ["hk416", "416", "416a5"],
    },

    # DMR
    {
        "name": "SWORD International Mk-18 .338 LM marksman rifle",
        "aliases": ["mk18", "ミョルニル"],
    },
    {
        "name": "Knight's Armament Company SR-25 7.62x51 marksman rifle",
        "aliases": ["sr25", "sr-25"],
    },

    # SMG
    {
        "name": "HK MP5 9x19 submachine gun",
        "aliases": ["mp5", "mp-5"],
    },
    {
        "name": "HK MP7A1 4.6x30 submachine gun",
        "aliases": ["mp7", "mp7a1"],
    },

    # ピストル
    {
        "name": "Glock 17 9x19 pistol",
        "aliases": ["g17", "glock17"],
    },
]

# ========================================
# 弾薬
# ========================================

CANONICAL_ITEMS += [

    # 5.45
    {
        "name": "5.45x39mm BP",
        "aliases": ["bp545", "545bp"],
    },
    {
        "name": "5.45x39mm BT",
        "aliases": ["bt545", "545bt"],
    },

    # 7.62x39
    {
        "name": "7.62x39mm BP",
        "aliases": ["bp762", "762bp"],
    },

    # 5.56
    {
        "name": "5.56x45mm M855",
        "aliases": ["855", "m855"],
    },
    {
        "name": "5.56x45mm M995",
        "aliases": ["995", "m995"],
    },

    # 7.62x51
    {
        "name": "7.62x51mm M80",
        "aliases": ["m80"],
    },
    {
        "name": "7.62x51mm M61",
        "aliases": ["m61"],
    },

]

# ========================================
# 最終辞書構築
# ========================================

ITEM_ALIASES = {}

for item in CANONICAL_ITEMS:
    official = item["name"]
    for alias in item["aliases"]:
        ITEM_ALIASES[alias.lower()] = official
