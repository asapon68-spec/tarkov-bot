# -*- coding: utf-8 -*-
"""
ALIASES 辞書
  キー  : ユーザーが入力しそうな文字列（全部小文字前提）
  値    : Tarkov Market / 英Wiki などで使われる「正式英語名」
"""

ALIASES = {
    # ========= 医療系 / メディカル =========
    "ledx": "LEDX Skin Transilluminator",
    "ledx 静脈発見器": "LEDX Skin Transilluminator",
    "ledx skin transilluminator": "LEDX Skin Transilluminator",
    "レドックス": "LEDX Skin Transilluminator",
    "レドックス 静脈": "LEDX Skin Transilluminator",

    "salewa": "Salewa first aid kit",
    "salewa first aid kit": "Salewa first aid kit",
    "サレワ": "Salewa first aid kit",

    "gas analyzer": "Gas analyzer",
    "gasan": "Gas analyzer",
    "ガスアナ": "Gas analyzer",
    "ガスアナライザー": "Gas analyzer",

    "aquapeps": "Aquapeps water purification tablets",
    "aquapeps 浄水タブレット": "Aquapeps water purification tablets",
    "浄水タブレット": "Aquapeps water purification tablets",

    "vitamins": "Bottle of OLOLO Multivitamins",
    "bottle of ololo multivitamins": "Bottle of OLOLO Multivitamins",
    "マルチビタミン": "Bottle of OLOLO Multivitamins",

    "h2o2": "Bottle of hydrogen peroxide",
    "過酸化水素水": "Bottle of hydrogen peroxide",

    "nacl": "Bottle of saline solution",
    "生理食塩水": "Bottle of saline solution",

    "syringe": "Disposable syringe",
    "使い捨て注射器": "Disposable syringe",

    "bloodset": "Medical bloodset",
    "輸血セット": "Medical bloodset",

    "medtools": "Medical tools",
    "手術器具": "Medical tools",

    "ophthalmoscope": "Ophthalmoscope",
    "検眼鏡": "Ophthalmoscope",

    "pile of meds": "Pile of meds",
    "医薬品": "Pile of meds",

    "defibrillat": "Portable defibrillator",
    "除細動器": "Portable defibrillator",

    # ========= 代表的ルート品 / バーター / コレクター =========
    "42": "42 Signature Blend English Tea",
    "42 紅茶": "42 Signature Blend English Tea",
    "42 signature blend english tea": "42 Signature Blend English Tea",
    "42 シグニチャーブレンド 英国紅茶": "42 Signature Blend English Tea",

    "apollo": "Apollo Soyuz cigarettes",
    "apollo soyuz cigarettes": "Apollo Soyuz cigarettes",
    "アポロ ソユーズ シガレット": "Apollo Soyuz cigarettes",

    "malboro": "Malboro Cigarettes",
    "マルボロ シガレット": "Malboro Cigarettes",

    "strike": "Strike Cigarettes",
    "ストライク シガレット": "Strike Cigarettes",

    "wilston": "Wilston cigarettes",
    "ウィルストン シガレット": "Wilston cigarettes",

    "aramid": "Aramid fiber fabric",
    "aramid fiber fabric": "Aramid fiber fabric",
    "アラミド繊維の生地": "Aramid fiber fabric",
    "アラミド": "Aramid fiber fabric",

    "cordura": "Cordura polyamide fabric",
    "cordura polyamide fabric": "Cordura polyamide fabric",
    "コーデュラナイロンの生地": "Cordura polyamide fabric",

    "fleece": "Fleece fabric",
    "フリースの生地": "Fleece fabric",

    "ripstop": "Ripstop fabric",
    "リップストップの生地": "Ripstop fabric",

    "bear buddy": "BEAR Buddy plush toy",
    "bear バディ": "BEAR Buddy plush toy",
    "bear バディのぬいぐるみ": "BEAR Buddy plush toy",

    "drlupo": "Can of Dr. Lupo's coffee beans",
    "drlupo's": "Can of Dr. Lupo's coffee beans",
    "dr. lupo's コーヒー豆": "Can of Dr. Lupo's coffee beans",

    "majaica": "Can of Majaica coffee beans",
    "マジャイカ コーヒー豆": "Can of Majaica coffee beans",

    "dogtag": "Dogtag",
    "ドッグタグ": "Dogtag",

    "paracord": "Paracord",
    "パラコード": "Paracord",

    "press pass": "Press pass (issued for NoiceGuy)",
    "press pass (issued for noiceguy)": "Press pass (issued for NoiceGuy)",
    "プレスカード": "Press pass (issued for NoiceGuy)",

    "loot lord": "Loot Lord plushie",
    "loot lord plushie": "Loot Lord plushie",
    "ルートロードのぬいぐるみ": "Loot Lord plushie",

    "gp coin": "GP coin",
    "gp コイン": "GP coin",

    "goldchain": "Golden neck chain",
    "gold chain": "Golden neck chain",
    "golden neck chain": "Golden neck chain",
    "金のチェーンネックレス": "Golden neck chain",

    "rooster": "Golden rooster figurine",
    "黄金のニワトリ": "Golden rooster figurine",

    "lion": "Bronze lion figurine",
    "青銅のライオン": "Bronze lion figurine",

    "cat": "Cat figurine",
    "ネコの置物": "Cat figurine",

    "raven": "Raven figurine",
    "カラスの置物": "Raven figurine",

    "rolex": "Roler Submariner gold wrist watch",
    "roler": "Roler Submariner gold wrist watch",
    "サブマリーナー": "Roler Submariner gold wrist watch",

    "0.2btc": "Physical Bitcoin",
    "physical bitcoin": "Physical Bitcoin",
    "ビットコインの金貨": "Physical Bitcoin",

    # ========= 電子部品 / 工業部品 =========
    "wires": "Bundle of wires",
    "bundle of wires": "Bundle of wires",
    "ビニル絶縁電線": "Bundle of wires",
    "ワイヤー": "Bundle of wires",

    "cpu fan": "CPU fan",
    "cpu ファン": "CPU fan",

    "caps": "Capacitors",
    "capacitors": "Capacitors",
    "コンデンサ": "Capacitors",

    "dvd": "DVD drive",
    "dvd drive": "DVD drive",

    "hdd": "Damaged hard drive",
    "damaged hard drive": "Damaged hard drive",
    "故障したハードディスク": "Damaged hard drive",

    "drill": "Electric drill",
    "electric drill": "Electric drill",
    "電動ドリル": "Electric drill",

    "motor": "Electric motor",
    "electric motor": "Electric motor",
    "モーター": "Electric motor",

    "ec": "Electronic components",
    "electronic components": "Electronic components",
    "電子部品": "Electronic components",

    "es lamp": "Energy-saving lamp",
    "energy-saving lamp": "Energy-saving lamp",
    "電球形蛍光灯": "Energy-saving lamp",

    "gpsa": "Far-forward GPS Signal Amplifier Unit",
    "gps 信号増幅器": "Far-forward GPS Signal Amplifier Unit",

    "gmcount": "Geiger-Muller counter",
    "geiger-muller counter": "Geiger-Muller counter",
    "ガイガーカウンター": "Geiger-Muller counter",

    "1gphone": "Golden 1GPhone smartphone",
    "1gphone オレンジゴールド": "Golden 1GPhone smartphone",

    "gpu": "Graphics card",
    "graphics card": "Graphics card",
    "グラボ": "Graphics card",
    "グラフィックボード": "Graphics card",

    "light bulb": "Light bulb",
    "bulb": "Light bulb",
    "白熱電球": "Light bulb",

    "magnet": "Magnet",
    "電磁石": "Magnet",

    "mb": "Microcontroller board",
    "microcontroller board": "Microcontroller board",
    "マイコンボード": "Microcontroller board",

    "sg-c10": "Military COFDM Wireless Signal Transmitter",
    "軍用 cofdm 無線信号送信機": "Military COFDM Wireless Signal Transmitter",

    "mcable": "Military cable",
    "military cable": "Military cable",
    "ミリタリーケーブル": "Military cable",

    "mcb": "Military circuit board",
    "military circuit board": "Military circuit board",
    "軍用回路基板": "Military circuit board",

    "mgt": "Military gyrotachometer",
    "軍用ジャイロタコメーター": "Military gyrotachometer",

    "pfilter": "Military power filter",
    "military power filter": "Military power filter",
    "軍用パワーフィルター": "Military power filter",

    "nixxor": "NIXXOR lens",
    "nixxor lens": "NIXXOR lens",
    "nixxor レンズ": "NIXXOR lens",

    "cpu": "PC CPU",
    "pc cpu": "PC CPU",

    "relay": "Phase control relay",
    "phase control relay": "Phase control relay",
    "三相監視リレー": "Phase control relay",

    "aesa": "Phased array element",
    "phased array element": "Phased array element",
    "フェーズドアレイ アンテナの部品": "Phased array element",

    "cord": "Power cord",
    "power cord": "Power cord",
    "電源ケーブル": "Power cord",

    "psu": "Power supply unit",
    "power supply unit": "Power supply unit",
    "電源ユニット": "Power supply unit",

    "pcb": "Printed circuit board",
    "printed circuit board": "Printed circuit board",
    "プリント基板": "Printed circuit board",

    "ram": "RAM",
    "メモリ": "RAM",

    "helix": "Radiator helix",
    "radiator helix": "Radiator helix",
    "電熱線": "Radiator helix",

    "spark plug": "Spark plug",
    "splug": "Spark plug",
    "スパークプラグ": "Spark plug",

    "t-plug": "T-Shaped plug",
    "t-shaped plug": "T-Shaped plug",

    "tetriz": "Tetriz portable game console",
    "tetriz ポータブルゲーム機": "Tetriz portable game console",

    "rfidr": "UHF RFID Reader",
    "uhf rfid reader": "UHF RFID Reader",

    "usb-a": "USB Adapter",
    "usb adapter": "USB Adapter",

    "uv lamp": "Ultraviolet lamp",
    "紫外線ランプ": "Ultraviolet lamp",

    "vpx": "VPX Flash Storage Module",
    "vpx flash storage module": "VPX Flash Storage Module",

    "virtex": "Virtex programmable processor",
    "virtex programmable processor": "Virtex programmable processor",

    "lcd": "Working LCD",
    "working lcd": "Working LCD",
    "液晶パネル": "Working LCD",

    "ssd": "SSD drive",
    "ssd drive": "SSD drive",

    "mfd": "Military flash drive",
    "military flash drive": "Military flash drive",

    "flash driv": "Secure Flash drive",
    "secure flash drive": "Secure Flash drive",
    "暗号化された usb フラッシュドライブ": "Secure Flash drive",
    "フラッシュドライブ": "Secure Flash drive",
    "フラド": "Secure Flash drive",

    # ========= バッテリー / 電源 =========
    "tank battery": "6-STEN-140-M military battery",
    "6-sten-140-m": "6-STEN-140-M military battery",
    "6-sten-140-m 軍用バッテリー": "6-STEN-140-M military battery",

    "aa batt.": "AA Battery",
    "aa battery": "AA Battery",
    "単3形 乾電池": "AA Battery",

    "car battery": "Car battery",
    "カーバッテリー": "Car battery",

    "cyclon": "Cyclon rechargeable battery",
    "cyclon rechargeable battery": "Cyclon rechargeable battery",

    "d batt.": "D Size battery",
    "d size battery": "D Size battery",
    "単1形 乾電池": "D Size battery",

    "greenbat": "GreenBat lithium battery",
    "greenbat lithium battery": "GreenBat lithium battery",

    "powerbank": "Portable Powerbank",
    "portable powerbank": "Portable Powerbank",
    "モバイルバッテリー": "Portable Powerbank",

    "rbattery": "Rechargeable battery",
    "rechargeable battery": "Rechargeable battery",

    # ========= 燃料 / 可燃物 =========
    "#fireklean": "#FireKlean gun lube",
    "#fireklean gun lube": "#FireKlean gun lube",

    "thermite": "Can of thermite",
    "can of thermite": "Can of thermite",
    "テルミット": "Can of thermite",

    "matches": "Classic matches",
    "classic matches": "Classic matches",
    "マッチ": "Classic matches",

    "crickent": "Crickent lighter",
    "crickent ライター": "Crickent lighter",

    "dry fuel": "Dry fuel",
    "固形燃料": "Dry fuel",

    "fuel": "Expeditionary fuel tank",
    "expeditionary fuel tank": "Expeditionary fuel tank",
    "携行燃料タンク": "Expeditionary fuel tank",

    "metal fuel": "Metal fuel tank",
    "metal fuel tank": "Metal fuel tank",
    "金属製燃料タンク": "Metal fuel tank",

    "propane": "Propane tank (5L)",
    "propane tank (5l)": "Propane tank (5L)",
    "プロパンタンク": "Propane tank (5L)",

    "survl": "SurvL Survivor Lighter",
    "survl サバイバルライター": "SurvL Survivor Lighter",

    "tp-200": "TP-200 TNT brick",
    "tp-200 tnt brick": "TP-200 TNT brick",

    "wd-40": "WD-40 (400ml)",
    "wd-40 (400ml)": "WD-40 (400ml)",

    "zibbo": "Zibbo lighter",
    "zibbo ライター": "Zibbo lighter",

    # ========= 日用品 / Household =========
    "alkali": "Alkaline cleaner for heat exchangers",
    "アルカリクリーナー": "Alkaline cleaner for heat exchangers",

    "salt": "Can of white salt",
    "can of white salt": "Can of white salt",
    "食用塩": "Can of white salt",

    "clin": "Clin window cleaner",
    "クリン ガラスクリーナー": "Clin window cleaner",

    "beardoil": "Deadlyslob's beard oil",
    "deadlyslob's beard oil": "Deadlyslob's beard oil",

    "poison": "LVNDMARK's rat poison",
    "lvndmark's 殺鼠剤": "LVNDMARK's rat poison",

    "ortodont": "Ortodontox toothpaste",
    "オルトドントックス 歯磨き粉": "Ortodontox toothpaste",

    "bleach": "Ox bleach",
    "ox 漂白剤": "Ox bleach",

    "paid": "PAID AntiRoach spray",
    "paid 殺虫剤": "PAID AntiRoach spray",

    "chlorine": "Pack of chlorine",
    "塩素剤": "Pack of chlorine",

    "sodium": "Pack of sodium bicarbonate",
    "炭酸水素ナトリウム": "Pack of sodium bicarbonate",

    "paper": "Printer paper",
    "コピー用紙": "Printer paper",

    "repellent": "Repellent",
    "虫よけスプレー": "Repellent",

    "shampoo": "Schaman shampoo",
    "シャーマン シャンプー": "Schaman shampoo",

    "dcleaner": "Smoked Chimney drain cleaner",
    "パイプクリーナー": "Smoked Chimney drain cleaner",

    "soap": "Soap",
    "固形石鹸": "Soap",

    "tp": "Toilet paper",
    "toilet paper": "Toilet paper",
    "トイレットペーパー": "Toilet paper",

    "toothpast": "Toothpaste",
    "toothpaste": "Toothpaste",
    "歯磨き粉": "Toothpaste",

    # ========= 建材 / Building materials =========
    "bolts": "Bolts",
    "ボルト": "Bolts",

    "hose": "Corrugated hose",
    "corrugated hose": "Corrugated hose",
    "コルゲートチューブ": "Corrugated hose",

    "duct tape": "Duct tape",
    "ダクトテープ": "Duct tape",

    "tape": "Insulating tape",
    "insulating tape": "Insulating tape",
    "絶縁テープ": "Insulating tape",

    "kektape": "KEKTAPE duct tape",
    "ケクテープ": "KEKTAPE duct tape",

    "m.parts": "Metal spare parts",
    "metal spare parts": "Metal spare parts",
    "金属製のスペアパーツ": "Metal spare parts",

    "mtube": "Military corrugated tube",
    "military corrugated tube": "Military corrugated tube",
    "軍用コルゲートチューブ": "Military corrugated tube",

    "nails": "Pack of nails",
    "箱入りのクギ": "Pack of nails",

    "screws": "Pack of screws",
    "袋入りのネジ": "Pack of screws",

    "plexiglass": "Piece of plexiglass",
    "プレキシグラス": "Piece of plexiglass",

    "pgauge": "Pressure gauge",
    "圧力計": "Pressure gauge",

    "nuts": "Screw nuts",
    "ナット": "Screw nuts",

    "shus": "Shustrilo sealing foam",
    "shustrilo sealing foam": "Shustrilo sealing foam",

    "tube": "Silicone tube",
    "silicone tube": "Silicone tube",
    "シリコンチューブ": "Silicone tube",

    "poxeram": "Tube of Poxeram cold welding",
    "ポキセラム": "Tube of Poxeram cold welding",

    "xeno": "Xenomorph sealing foam",
    "xenomorph sealing foam": "Xenomorph sealing foam",

    # ========= 情報系 / インテリ系 =========
    "intelligence": "Intelligence folder",
    "intelligence folder": "Intelligence folder",
    "機密情報フォルダー": "Intelligence folder",

    "smt": "Secure magnetic tape cassette",
    "secure magnetic tape cassette": "Secure magnetic tape cassette",

    "sasd": "SAS drive",
    "sas drive": "SAS drive",

    "diary": "Diary",
    "ダイアリー": "Diary",

    "sdairy": "Slim diary",
    "slim diary": "Slim diary",
    "ポケットダイアリー": "Slim diary",

    # ========= 代表的な武器（よく検索されそうなものだけ） =========
    "m4a1": "Colt M4A1 5.56x45 assault rifle",
    "colt m4a1 5.56x45 assault rifle": "Colt M4A1 5.56x45 assault rifle",
    "m4a1 standard": "Colt M4A1 5.56x45 assault rifle",

    "ak-74": "Kalashnikov AK-74 5.45x39 assault rifle",
    "ak74": "Kalashnikov AK-74 5.45x39 assault rifle",

    "ak-74m": "Kalashnikov AK-74M 5.45x39 assault rifle",
    "ak74m": "Kalashnikov AK-74M 5.45x39 assault rifle",

    "akm": "Kalashnikov AKM 7.62x39 assault rifle",
    "akmn": "Kalashnikov AKMN 7.62x39 assault rifle",

    "aks-74u": "Kalashnikov AKS-74U 5.45x39 assault rifle",
    "aks74u": "Kalashnikov AKS-74U 5.45x39 assault rifle",

    "as val": "AS VAL 9x39 special assault rifle",
    "as val 9x39 special assault rifle": "AS VAL 9x39 special assault rifle",

    "vss": "VSS Vintorez 9x39 special sniper rifle",
    "vss \"vintorez\"": "VSS Vintorez 9x39 special sniper rifle",

    "glock 17": "Glock 17 9x19 pistol",
    "glock17": "Glock 17 9x19 pistol",

    "glock 18c": "Glock 18C 9x19 machine pistol",
    "glock18c": "Glock 18C 9x19 machine pistol",

    "mp-153": "MP-153 12ga semi-automatic shotgun",
    "mp153": "MP-153 12ga semi-automatic shotgun",

    "mp-155": "MP-155 12ga semi-automatic shotgun",
    "mp155": "MP-155 12ga semi-automatic shotgun",

    "m870": "Remington Model 870 12ga pump-action shotgun",

    "saiga 12": "Saiga-12K ver.10 12ga semi-automatic shotgun",
    "saiga 12ga v.10": "Saiga-12K ver.10 12ga semi-automatic shotgun",

    "mpx": "SIG MPX 9x19 submachine gun",
    "mp9": "B&T MP9 9x19 submachine gun",
    "mp7": "HK MP7A1 4.6x30 submachine gun",
}
