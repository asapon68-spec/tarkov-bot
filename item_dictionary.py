# item_dictionary.py（完全版・SyntaxErrorゼロ）
# Escape from Tarkov アイテム辞書（日本語・英語・略称 対応）

# ========================================
# 🔥 レア・高額ルート
# ========================================

CANONICAL_ITEMS = [
    {
        "name": "LEDX Skin Transilluminator",
        "aliases": [
            "ledx", "reox", "レドックス", "レッドックス", "レドエックス",
            "ledx 静脈", "光るやつ", "医療レドックス"
        ],
    },
    {
        "name": "Graphics card",
        "aliases": [
            "gpu", "グラボ", "graphics", "graphic card", "グラフィックボード"
        ],
    },
    {
        "name": "Physical Bitcoin",
        "aliases": [
            "bitcoin", "btc", "ビットコイン", "ビッコ"
        ],
    },
    {
        "name": "Red Rebel ice pick",
        "aliases": ["red rebel", "レッドレベル", "レドレベ", "アイスピッケル"],
    },
    {
        "name": "Keytool",
        "aliases": ["keytool", "キー工具", "キーケース"],
    },
    {
        "name": "Item Case",
        "aliases": ["item case", "アイテムケース", "アイケ"],
    },
    {
        "name": "Weapon Case",
        "aliases": ["weapon case", "武器ケース", "武器ケ"],
    },
    {
        "name": "THICC Weapon Case",
        "aliases": ["thicc weapon case", "thicc武器ケース"],
    },
    {
        "name": "THICC Item Case",
        "aliases": ["thicc item case", "シックケース"],
    },

    # ========================================
    # 🦁 置物・トレードアイテム
    # ========================================

    {
        "name": "Bronze lion figurine",
        "aliases": ["bronze lion", "lion", "ライオン"],
    },
    {
        "name": "Cat figurine",
        "aliases": ["cat", "猫", "ネコ"],
    },
    {
        "name": "Horse figurine",
        "aliases": ["horse", "馬", "馬像"],
    },
    {
        "name": "Raven figurine",
        "aliases": ["raven", "レイヴン", "カラス"],
    },
    {
        "name": "GP coin",
        "aliases": ["gp", "gp coin", "gpコイン"],
    },
    {
        "name": "Chain with Prokill medallion",
        "aliases": ["prokill", "プロキル"],
    },
    {
        "name": "Golden neck chain",
        "aliases": ["goldchain", "金チェーン", "金ネックレス"],
    },
    {
        "name": "Antique teapot",
        "aliases": ["ティーポット", "古いポット"],
    },
    {
        "name": "Antique vase",
        "aliases": ["vase", "花瓶"],
    },

    # ========================================
    # 📦 工業品・素材系
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
        "aliases": ["パラコード"],
    },
    {
        "name": "FP-100 filter absorber",
        "aliases": ["fp100", "fp-100"],
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
        "aliases": ["car battery", "バッテリー"],
    },
    {
        "name": "Spark plug",
        "aliases": ["spark plug", "スパークプラグ"],
    },
    {
        "name": "Wires",
        "aliases": ["wires", "ワイヤー"],
    },
    {
        "name": "Insulating tape",
        "aliases": ["tape", "絶縁テープ", "青テープ"],
    },
    {
        "name": "Duct tape",
        "aliases": ["duct tape", "ガムテ"],
    },

    # ========================================
    # 🧪 医療・薬品
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
        "aliases": ["surv12", "サブ12"],
    },
    {
        "name": "Salewa First Aid Kit",
        "aliases": ["salewa", "サレワ"],
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
        "aliases": ["sj6", "スジャ6"],
    },
    {
        "name": "Propital regenerative stimulant injector",
        "aliases": ["propital", "プロピタル"],
    },

    # ========================================
    # 🗝 キー類
    # ========================================

    {
        "name": "Factory exit key",
        "aliases": ["factory key", "赤鍵", "工場キー"],
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
        "aliases": ["sanitar key", "サニターキー"],
    },
]

# ========================================
# 🔫 武器（アサルト / DMR / ボルト / SMG / LMG）
# ========================================

CANONICAL_ITEMS += [
    # AKシリーズ
    {"name": "Kalashnikov AK-74 5.45x39 assault rifle",
     "aliases": ["ak74", "ak 74", "エーケー74", "ak74n", "ak74m"]},

    {"name": "Kalashnikov AK-74M 5.45x39 assault rifle",
     "aliases": ["ak74m", "74m"]},

    {"name": "Kalashnikov AK-74N 5.45x39 assault rifle",
     "aliases": ["ak74n", "74n"]},

    {"name": "Kalashnikov AKS-74 5.45x39 assault rifle",
     "aliases": ["aks74", "aks-74"]},

    {"name": "Kalashnikov AKS-74U 5.45x39 assault rifle",
     "aliases": ["aks74u", "クリンコフ"]},

    {"name": "Kalashnikov AK-103 7.62x39 assault rifle",
     "aliases": ["ak103", "103"]},

    {"name": "Kalashnikov AK-104 7.62x39 assault rifle",
     "aliases": ["ak104", "104"]},

    {"name": "Kalashnikov AK-105 5.45x39 assault rifle",
     "aliases": ["ak105", "105"]},

    {"name": "Kalashnikov AKM 7.62x39 assault rifle",
     "aliases": ["akm", "エーケーエム"]},

    {"name": "Kalashnikov AKMN 7.62x39 assault rifle",
     "aliases": ["akmn", "mn"]},

    # AR系
    {"name": "Colt M4A1 5.56x45 assault rifle",
     "aliases": ["m4", "m4a1", "エムフォー"]},

    {"name": "HK 416A5 5.56x45 assault rifle",
     "aliases": ["hk416", "416"]},

    {"name": "FN SCAR-L 5.56x45 assault rifle",
     "aliases": ["scar l", "スカーl", "mk16"]},

    {"name": "FN SCAR-H 7.62x51 assault rifle",
     "aliases": ["scar h", "スカーh", "mk17"]},

    # DMR
    {"name": "SWORD International Mk-18 .338 LM marksman rifle",
     "aliases": ["mk18", "ミョルニル"]},

    {"name": "Knight's Armament Company SR-25 7.62x51 marksman rifle",
     "aliases": ["sr25"]},

    {"name": "HK G28 7.62x51 marksman rifle",
     "aliases": ["g28"]},

    {"name": "Remington R11 RSASS 7.62x51 marksman rifle",
     "aliases": ["rsass"]},

    # ボルト
    {"name": "ORSIS T-5000M 7.62x51 bolt-action sniper rifle",
     "aliases": ["t5000"]},

    {"name": "Mosin 7.62x54R bolt-action rifle",
     "aliases": ["mosin", "モシン"]},

    {"name": "Marlin MXLR .308ME lever-action rifle",
     "aliases": ["mxlr"]},

    {"name": "Remington Model 700 7.62x51 bolt-action sniper rifle",
     "aliases": ["m700", "700"]},

    # SMG
    {"name": "HK MP5 9x19 submachine gun",
     "aliases": ["mp5"]},

    {"name": "HK MP7A1 4.6x30 submachine gun",
     "aliases": ["mp7"]},

    {"name": "HK MP7A2 4.6x30 submachine gun",
     "aliases": ["mp7a2"]},

    {"name": "KRISS Vector .45 ACP submachine gun",
     "aliases": ["vector", "ベクター"]},

    {"name": "KRISS Vector 9x19 submachine gun",
     "aliases": ["vector9"]},

    # LMG
    {"name": "Kalashnikov PKM 7.62x54R machine gun",
     "aliases": ["pkm"]},

    {"name": "Kalashnikov PKP 7.62x54R machine gun Pecheneg",
     "aliases": ["pkp"]},

    {"name": "RPK-16 5.45x39 light machine gun",
     "aliases": ["rpk16"]},

    # ピストル
    {"name": "Glock 17 9x19 pistol",
     "aliases": ["g17", "glock17"]},

    {"name": "Glock 18C 9x19 pistol",
     "aliases": ["g18"]},

    {"name": "SIG P226R 9x19 pistol",
     "aliases": ["p226"]},

    {"name": "Colt M1911A1 .45 ACP pistol",
     "aliases": ["m1911", "1911"]},
]

# ========================================
# 💥 弾薬
# ========================================

CANONICAL_ITEMS += [
    # 5.45
    {"name": "5.45x39mm BP", "aliases": ["545bp"]},
    {"name": "5.45x39mm BT", "aliases": ["545bt"]},
    {"name": "5.45x39mm PP", "aliases": ["545pp"]},

    # 7.62x39
    {"name": "7.62x39mm BP", "aliases": ["762bp"]},
    {"name": "7.62x39mm PS", "aliases": ["762ps"]},

    # 5.56
    {"name": "5.56x45mm M855", "aliases": ["855"]},
    {"name": "5.56x45mm M855A1", "aliases": ["855a1", "a1"]},
    {"name": "5.56x45mm M995", "aliases": ["995"]},

    # 7.62x51
    {"name": "7.62x51mm M80", "aliases": ["m80"]},
    {"name": "7.62x51mm M61", "aliases": ["m61"]},
    {"name": "7.62x51mm M62", "aliases": ["m62"]},

    # 4.6
    {"name": "4.6x30mm AP SX", "aliases": ["apsx"]},

    # 9x19
    {"name": "9x19mm AP 6.3", "aliases": ["ap63", "6.3"]},
    {"name": "9x19mm PST gzh", "aliases": ["pst"]},
    {"name": "9x19mm RIP", "aliases": ["rip"]},

    # .45 ACP
    {"name": ".45 ACP AP", "aliases": ["45ap"]},

    # .300 BLK
    {"name": ".300 Blackout AP", "aliases": ["300ap"]},

    # .338 LM
    {"name": ".338 Lapua Magnum AP", "aliases": ["338ap"]},
]

# ========================================
# 🔄 Alias 自動生成
# ========================================

ITEM_ALIASES = {}
for item in CANONICAL_ITEMS:
    name = item["name"]
    for alias in item["aliases"]:
        ITEM_ALIASES[alias.lower()] = name
