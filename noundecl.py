"""Get the Kotus declension of a Finnish noun."""

# Note: A = a/ä, O = o/ö, U = u/y, V = any vowel, C = any consonant.

import re, sys
import countsyll

# A typical noun in each declension.
# Forms: nominative sg, genitive sg, genitive pl, partitive sg, partitive pl,
# illative sg, illative pl.
# No genitive plurals that end with -in or -itten.
DECLENSION_DESCRIPTIONS = {
    1:  "valo, -n, -jen, -a, -ja, -on, -ihin",
    2:  "palvelu, -n, -jen/-iden, -a, -ja/-ita, -un, -ihin",
    3:  "valtio, -n, -iden, -ta, -ita, -on, -ihin",
    4:  "laatik|ko, -on, -kojen/-oiden, -koa, -koja/-oita, -koon, -(k)oihin",
    5:  "rist|i, -in, -ien, -iä, -ejä, -iin, -eihin",
    6:  "paper|i, -in, -ien/-eiden, -ia, -eja/-eita, -iin, -eihin",
    7:  "ov|i, -en, -ien, -ea, -ia, -een, -iin",
    8:  "nalle, -n, -jen, -a, -ja, -en, -ihin",
    9:  "kal|a, -an, -ojen, -aa, -oja, -aan, -oihin",
    10: "koir|a, -an, -ien, -aa, -ia, -aan, -iin",
    11: "omen|a, -an, -ien/-oiden/-ojen, -aa, -ia/-oita/-oja, -aan, " \
        "-iin/-oihin",
    12: "kulkij|a, -an, -oiden, -aa, -oita, -aan, -oihin",
    13: "katisk|a, -an, -oiden/-ojen, -aa, -oita/-oja, -aan, -oihin",
    14: "solak|ka, -an, -oiden/-kojen, -kaa, -oita/-koja, -kaan, -(k)oihin",
    15: "korke|a, -an, -iden, -a(t)a, -ita, -aan, -isiin/-ihin",
    16: "vanhem|pi, -man, -pien, -paa, -pia, -paan, -piin",
    17: "vapa|a, -an, -iden, -ata, -ita, -aseen, -isiin/-ihin",
    18: "ma|a, -an, -iden, -ata, -ita, -ahan, -ihin",
    19: "s|uo, -uon, -oiden, -uota, -oita, -uohon, -oihin",
    20: "file|e, -en, -iden, -etä, -itä, -ehen/-eseen, -ihin/-isiin",
    21: "rosé, -n, -iden, -ta, -ita, -hen, -ihin",
    22: "parfait, -'n, -'iden, -'ta, -'ita, -'hen, -'ihin",
    23: "tiil|i, -en, -ien, -tä, -iä, -een, -iin",
    24: "un|i, -en, -ien/-ten, -ta, -ia, -een, -iin",
    25: "toi|mi, -men, -mien/-nten, -mea/-nta, -mia, -meen, -miin",
    26: "pien|i, -en, -ten/-ien, -tä, -iä, -een, -iin",
    27: "kä|si, -den, -sien/-tten, -ttä, -siä, -teen, -siin",
    28: "kyn|si, -nen, -sien/-tten, -ttä, -siä, -teen, -siin",
    29: "la|psi, -psen, -sten/-psien, -sta, -psia, -pseen, -psiin",
    30: "vei|tsi, -tsen, -tsien/-sten, -stä, -tsiä, -tseen, -tsiin",
    31: "ka|ksi, -hden, -ksien, -hta, -ksia, -hteen, -ksiin",
    32: "sisar, -en, -ien/-ten, -ta, -ia, -een, -iin",
    33: "kytki|n, -men, -mien/-nten, -ntä, -miä, -meen, -miin",
    34: "onnet|on, -toman, -tomien/-onten, -onta, -tomia, -tomaan, -tomiin",
    35: "läm|min, -pimän, -pimien, -mintä, -pimiä, -pimään, -pimiin",
    36: "sisi|n, -mmän, -mpien/-nten, -ntä, -mpiä, -mpään, -mpiin",
    37: "vase|n, -mman, -mpien/-nten, -nta/-mpaa, -mpia, -mpaan, -mpiin",
    38: "nai|nen, -sen, -sten/-sien, -sta, -sia, -seen, -siin",
    39: "vastau|s, -ksen, -sten/-ksien, -sta, -ksia, -kseen, -ksiin",
    40: "kalleu|s, -den, -ksien, -tta, -ksia, -teen, -ksiin",
    41: "viera|s, -an, -iden, -sta, -ita, -aseen, -isiin/-ihin",
    42: "mie|s, -hen, -sten/-hien, -stä, -hiä, -heen, -hiin",
    43: "ohu|t, -en, -iden, -tta, -ita, -een, -isiin/-ihin",
    44: "kevä|t, -än, -iden, -ttä, -itä, -äseen, -isiin/-ihin",
    45: "kahdeksa|s, -nnen, -nsien, -tta, -nsia, -nteen, -nsiin",
    46: "tuha|t, -nnen, -nsien/-nten, -tta, -nsia, -nteen, -nsiin",
    47: "kuoll|ut, -een, -eiden, -utta, -eita, -eeseen, -eisiin/-eihin",
    48: "hame, -en, -iden, -tta, -ita, -eseen, -isiin/-ihin",
    49: "askel|(e), -e(e)n, -ien/-eiden/-(eit)ten, -(et)ta, -ia/-eita, " \
        "-ee(see)n, -(eis)iin/-eihin",
}

# key = noun, value = tuple of declensions
_MULTI_DECLENSION_NOUNS = {
    # different meanings
    "lahti": (5, 7),
    "laki": (5, 7),
    "palvi": (5, 7),
    "ripsi": (5, 7),
    "saksi": (5, 7),
    "sini": (5, 7),
    #
    "kuori": (5, 26),
    "viini": (5, 26),
    "vuori": (5, 26),
    #
    "peitsi": (5, 30),
    #
    "puola": (9, 10),
    #
    "kikkara": (11, 12),
    #
    "kuusi": (24, 27),
    #
    "ahtaus": (39, 40,),
    "karvaus": (39, 40,),
    "rosvous": (39, 40),
    "siivous": (39, 40),
    "vakaus": (39, 40),
    #
    "kymmenes": (39, 45),

    # same meanings
    "menu": (1, 21),
    #
    "caddie": (3, 8),
    #
    "alpi": (5, 7),
    "helpi": (5, 7),
    "kaihi": (5, 7),
    "karhi": (5, 7),
    "kymi": (5, 7),
    "vyyhti": (5, 7),
    #
    "sioux": (5, 22),
    #
    "syli": (5, 23),
    #
    "csárdás": (5, 39),
    "kuskus": (5, 39),
    #
    "ori": (5, 48),
    #
    "kolme": (7, 8),  # 8 in singular, 7 in plural
    #
    "hapsi": (7, 29),
    "uksi": (7, 29),
    #
    "siitake": (8, 48),
    #
    "aneurysma": (9, 10),
    "kysta": (9, 10),
    "lyyra": (9, 10),
    #
    "humala": (10, 11),
    #
    "tanhua": (12, 15),
    #
    "havas": (39, 41),
    "kallas": (39, 41),
    "koiras": (39, 41),
    "olas": (39, 41),
    "pallas": (39, 41),
    "tuomas": (39, 41),
    "uros": (39, 41),
}

# exceptions to rules
# - format: noun: declension
# - order: first by syllable count, then by ending, then by declension
_EXCEPTIONS = {
    # === Monosyllabic ===

    # -VV
    "brie": 21,
    "clou": 21,
    #
    "hie": 48,

    # -n
    "ien": 32,
    #
    "näin": 33,
    "puin": 33,
    #
    "tain": 36,

    # -s
    "AIDS": 5,
    #
    "hius": 39,
    "taus": 39,
    #
    "ies": 41,
    "ruis": 41,
    #
    "mies": 42,

    # -C (not -n/-s)
    "LED": 5,
    #
    "show": 22,

    # === Disyllabic ===

    # -VV
    "duo": 1,
    "trio": 1,
    #
    "boutique": 8,
    "petanque": 8,
    #
    "dia": 9,
    "maya": 9,
    #
    "boa": 10,
    #
    "hynttyy": 17,
    #
    "frisbee": 18,
    "huuhaa": 18,
    "peeaa": 18,
    "puusee": 18,
    #
    "nugaa": 20,
    "raguu": 20,
    "sampoo": 20,
    "trikoo": 20,
    "voodoo": 20,
    #
    "fondue": 21,
    "reggae": 21,
    "tax-free": 21,
    #
    "aie": 48,
    "säie": 48,

    # -Ca
    "krypta": 9,
    "lymfa": 9,
    "suola": 9,
    #
    "saaja": 10,
    "saapa": 10,
    "saava": 10,

    # -Cä
    "iskä": 9,
    "nyintä": 9,
    "ryintä": 9,

    # -Ce
    "akne": 8,
    "ale": 8,
    "beige": 8,
    "bäne": 8,
    "crème fraîche": 8,
    "crêpe": 8,
    "deadline": 8,
    "duchesse": 8,
    "folklore": 8,
    "forte": 8,
    "freestyle": 8,
    "genre": 8,
    "gruyère": 8,
    "hardware": 8,
    "itse": 8,
    "jade": 8,
    "jeppe": 8,
    "joule": 8,
    "kalle": 8,
    "kurre": 8,
    "lande": 8,
    "lime": 8,
    "madame": 8,
    "mangrove": 8,
    "manne": 8,
    "milk shake": 8,
    "mousse": 8,
    "nalle": 8,
    "nasse": 8,
    "nisse": 8,
    "nukke": 8,
    "ope": 8,
    "pelle": 8,
    "penne": 8,
    "polle": 8,
    "poplore": 8,
    "pose": 8,
    "psyyke": 8,
    "puzzle": 8,
    "quenelle": 8,
    "ragtime": 8,
    "saame": 8,
    "sake": 8,
    "single": 8,
    "soft ice": 8,
    "software": 8,
    "striptease": 8,
    "tele": 8,
    "tilde": 8,
    "toope": 8,
    "vaudeville": 8,
    #
    "bile": 20,

    # -Ci
    "LYHKI": 5,
    "mansi": 5,
    "sutki": 5,
    "tuoli": 5,
    #
    "appi": 7,
    "haahti": 7,
    "hanhi": 7,
    "hanki": 7,
    "happi": 7,
    "hauki": 7,
    "helmi": 7,
    "henki": 7,
    "hiki": 7,
    "hirvi": 7,
    "joki": 7,
    "järvi": 7,
    "kaikki": 7,
    "kanki": 7,
    "kaski": 7,
    "kiiski": 7,
    "kivi": 7,
    "koipi": 7,
    "koski": 7,
    "käki": 7,
    "kärhi": 7,
    "lehti": 7,
    "leski": 7,
    "lovi": 7,
    "länki": 7,
    "läpi": 7,
    "mäki": 7,
    "nimi": 7,
    "noki": 7,
    "nummi": 7,
    "nurmi": 7,
    "närhi": 7,
    "onki": 7,
    "onni": 7,
    "ovi": 7,
    "parvi": 7,
    "piki": 7,
    "pilvi": 7,
    "polvi": 7,
    "poski": 7,
    "povi": 7,
    "päitsi": 7,
    "pälvi": 7,
    "reki": 7,
    "rupi": 7,
    "saarni": 7,
    "saksi": 7,
    "salmi": 7,
    "sappi": 7,
    "sarvi": 7,
    "savi": 7,
    "seimi": 7,
    "siipi": 7,
    "soppi": 7,
    "sormi": 7,
    "suitsi": 7,
    "suksi": 7,
    "suomi": 7,
    "suvi": 7,
    "sänki": 7,
    "sääksi": 7,
    "sääski": 7,
    "talvi": 7,
    "tammi": 7,
    "tilhi": 7,
    "torvi": 7,
    "tuki": 7,
    "tuppi": 7,
    "typpi": 7,
    "tyvi": 7,
    "tähti": 7,
    "vaski": 7,
    "veli": 7,
    "viiksi": 7,
    "vuoksi": 7,
    "väki": 7,
    #
    "kumpi": 16,
    #
    "moni": 23,
    "riihi": 23,
    "tiili": 23,
    "tuli": 23,
    #
    "hiili": 24,
    "hiiri": 24,
    "huuli": 24,
    "kusi": 24,
    "meri": 24,
    "ruuhi": 24,
    "uni": 24,
    #
    "lumi": 25,
    "luomi": 25,
    "taimi": 25,
    "tuomi": 25,
    #
    "jousi": 26,
    "juuri": 26,
    "kaari": 26,
    "niini": 26,
    "nuori": 26,
    "saari": 26,
    "suuri": 26,
    "sääri": 26,
    "teeri": 26,
    "tuuli": 26,
    "tyyni": 26,
    "veri": 26,
    "vieri": 26,
    "ääni": 26,
    "ääri": 26,
    #
    "heisi": 27,
    "hiisi": 27,
    "kausi": 27,
    "kesi": 27,
    "käsi": 27,
    "köysi": 27,
    "liesi": 27,
    "mesi": 27,
    "niisi": 27,
    "paasi": 27,
    "reisi": 27,
    "susi": 27,
    "sysi": 27,
    "tosi": 27,
    "täysi": 27,
    "uusi": 27,
    "vesi": 27,
    "viisi": 27,
    "vuosi": 27,
    #
    "lapsi": 29,
    #
    "veitsi": 30,
    #
    "haaksi": 31,
    "kaksi": 31,
    "yksi": 31,

    # -CO/-CU
    "go-go": 18,
    #
    "kung-fu": 21,
    #
    "kiiru": 48,

    # -l
    "kennel": 5,
    #
    "diesel": 6,
    "rial": 6,
    #
    "nivel": 32,
    "sävel": 32,
    #
    "seppel": 49,

    # -n
    "drive-in": 5,
    "hymen": 5,
    "kelvin": 5,
    "pinyin": 5,
    #
    "bourbon": 6,
    "chanson": 6,
    "kaanon": 6,
    "lumen": 6,
    "luumen": 6,
    "nailon": 6,
    "nelson": 6,
    "nylon": 6,
    "pyton": 6,
    #
    "hapan": 33,
    "laidun": 33,
    "sydän": 33,
    #
    "lämmin": 35,
    #
    "alin": 36,
    "enin": 36,
    "likin": 36,
    "lähin": 36,
    "parhain": 36,
    "sisin": 36,
    "taain": 36,
    "uloin": 36,
    "vanhin": 36,
    "ylin": 36,
    #
    "vasen": 37,

    # -r
    "agar": 6,
    "bitter": 6,
    "blazer": 6,
    "dealer": 6,
    "kassler": 6,
    "laser": 6,
    "loafer": 6,
    "schäfer": 6,
    "sitar": 6,
    "snooker": 6,
    "vesper": 6,
    "voucher": 6,
    "weber": 6,
    #
    "sisar": 32,
    "tatar": 32,
    "tytär": 32,
    #
    "auer": 49,
    "udar": 49,

    # -s
    "blues": 5,
    "couscous": 5,
    #
    "aidas": 39,
    "atlas": 39,
    "emäs": 39,
    "haljas": 39,
    "harjas": 39,
    "holhous": 39,
    "jalas": 39,
    "juudas": 39,
    "kaimas": 39,
    "kannas": 39,
    "kehruus": 39,
    "kehräs": 39,
    "kirous": 39,
    "kiveys": 39,
    "kokous": 39,
    "kumous": 39,
    "kuvas": 39,
    "lihas": 39,
    "linkous": 39,
    "loveus": 39,
    "lumous": 39,
    "luudas": 39,
    "madras": 39,
    "makuus": 39,
    "mullas": 39,
    "nahas": 39,
    "nuohous": 39,
    "ohjas": 39,
    "patous": 39,
    "persuus": 39,
    "pikeys": 39,
    "poikkeus": 39,
    "priimas": 39,
    "putous": 39,
    "risteys": 39,
    "rukous": 39,
    "sammas": 39,
    "saveus": 39,
    "tarjous": 39,
    "tervas": 39,
    "teräs": 39,
    "tyveys": 39,
    "vastas": 39,
    "verhous": 39,
    "vihdas": 39,
    "viinas": 39,
    "vitsas": 39,
    #
    "ahnaus": 40,
    "harmaus": 40,
    "hartaus": 40,
    "hauraus": 40,
    "herraus": 40,
    "hitaus": 40,
    "hurskaus": 40,
    "irstaus": 40,
    "karsaus": 40,
    "kiivaus": 40,
    "kirkkaus": 40,
    "kitsaus": 40,
    "kuulaus": 40,
    "kärkkäys": 40,
    "liukkaus": 40,
    "maukkaus": 40,
    "puhtaus": 40,
    "raihnaus": 40,
    "rakkaus": 40,
    "raskaus": 40,
    "reippaus": 40,
    "riettaus": 40,
    "rikkaus": 40,
    "runsaus": 40,
    "sairaus": 40,
    "suulaus": 40,
    "työläys": 40,
    "valppaus": 40,
    "vapaus": 40,
    "varkaus": 40,
    "vauraus": 40,
    "vehmaus": 40,
    "viekkaus": 40,
    "vieraus": 40,
    "viisaus": 40,
    "vilkkaus": 40,
    "vuolaus": 40,
    "ylväys": 40,
    #
    "altis": 41,
    "aulis": 41,
    "kallis": 41,
    "kaunis": 41,
    "kauris": 41,
    "kirves": 41,
    "nauris": 41,
    "raitis": 41,
    "ruumis": 41,
    "ryntys": 41,
    "saalis": 41,
    "tiivis": 41,
    "tyyris": 41,
    "valmis": 41,
    "vantus": 41,
    "äes": 41,
    #
    "kahdes": 45,
    "kolmas": 45,
    "kuudes": 45,
    "mones": 45,
    "neljäs": 45,
    "nollas": 45,
    "sadas": 45,
    "viides": 45,
    "yhdes": 45,

    # -t
    "input": 5,
    "output": 5,
    #
    "beignet": 22,
    "bouquet": 22,
    "buffet": 22,
    "gourmet": 22,
    "nougat": 22,
    "parfait": 22,
    "ragoût": 22,
    #
    "kevät": 44,
    "venät": 44,
    #
    "tuhat": 46,

    # -C (not -l/-n/-r/-s/-t)
    "edam": 6,
    "gallup": 6,
    #
    "bordeaux": 22,
    "know-how": 22,

    # === Trisyllabic ===

    # -VV
    "aaloe": 3,
    "collie": 3,
    "embryo": 3,
    "lassie": 3,
    "oboe": 3,
    "zombie": 3,
    #
    "feijoa": 10,
    #
    "apnea": 12,
    "hebrea": 12,
    "heprea": 12,
    "idea": 12,
    "pallea": 12,
    "urea": 12,
    #
    "media": 13,
    #
    "ainoa": 15,
    #
    "homssantuu": 18,
    "kanapee": 18,
    "munaskuu": 18,
    "pelakuu": 18,
    "rokokoo": 18,
    "tenkkapoo": 18,
    #
    "brasserie": 21,

    # -Ca
    "alfalfa": 9,
    "ameba": 9,
    "antiikva": 9,
    "aortta": 9,
    "canasta": 9,
    "chinchilla": 9,
    "dilemma": 9,
    "ekseema": 9,
    "guava": 9,
    "kimaira": 9,
    "koala": 9,
    "marimba": 9,
    "nautiikka": 9,
    "papilla": 9,
    "prostata": 9,
    "regatta": 9,
    "ruustinna": 9,
    "sialma": 9,
    "sinsilla": 9,
    "tequila": 9,
    "tiaara": 9,
    "toccata": 9,
    "tonsilla": 9,
    #
    "amfora": 10,
    "ankara": 10,
    "avara": 10,
    "gallona": 10,
    "hankala": 10,
    "huuhdonta": 10,
    "ihana": 10,
    "jumala": 10,
    "kamala": 10,
    "katala": 10,
    "kavala": 10,
    "kolonna": 10,
    "kumara": 10,
    "leijona": 10,
    "madonna": 10,
    "matala": 10,
    "nokkela": 10,
    "ovela": 10,
    "pomada": 10,
    "reskontra": 10,
    "sukkela": 10,
    "tukala": 10,
    #
    "ahava": 11,
    "algebra": 11,
    "apaja": 11,
    "hapera": 11,
    "harava": 11,
    "hatara": 11,
    "hattara": 11,
    "hekuma": 11,
    "hutera": 11,
    "itara": 11,
    "judoka": 11,
    "kihara": 11,
    "lattana": 11,
    "leukoija": 11,
    "mahatma": 11,
    "maruna": 11,
    "mimoosa": 11,
    "murena": 11,
    "ohrana": 11,
    "omena": 11,
    "orpana": 11,
    "paatsama": 11,
    "papana": 11,
    "pipana": 11,
    "poppana": 11,
    "probleema": 11,
    "sikkara": 11,
    "sikuna": 11,
    "tomera": 11,
    "vanttera": 11,
    "ödeema": 11,
    #
    "harppuuna": 12,
    "kamera": 12,
    "kolera": 12,
    "littera": 12,
    "ooppera": 12,
    "paprika": 12,
    "passiiva": 12,
    "salama": 12,
    #
    "aivina": 13,
    "aktiiva": 13,
    "apila": 13,
    "arina": 13,
    "artikla": 13,
    "gerbera": 13,
    "hetaira": 13,
    "ipana": 13,
    "kahina": 13,
    "kampela": 13,
    "karisma": 13,
    "ketara": 13,
    "kitara": 13,
    "kohina": 13,
    "kopina": 13,
    "kuhina": 13,
    "maailma": 13,
    "madeira": 13,
    "manila": 13,
    "mantilja": 13,
    "marina": 13,
    "matara": 13,
    "maukuna": 13,
    "meduusa": 13,
    "papaija": 13,
    "paukkina": 13,
    "perenna": 13,
    "piekana": 13,
    "porina": 13,
    "prinsessa": 13,
    "rahina": 13,
    "ramina": 13,
    "reppana": 13,
    "reseda": 13,
    "retsina": 13,
    "ruutana": 13,
    "sairaala": 13,
    "sikala": 13,
    "sikkura": 13,
    "smetana": 13,
    "suurima": 13,
    "takila": 13,
    "taverna": 13,
    "tempera": 13,
    "tuoksina": 13,
    "vaahtera": 13,
    "vanilja": 13,
    "vernissa": 13,
    "viola": 13,
    #
    "ulappa": 14,
    #
    "cha-cha-cha": 21,

    # -Cä
    "emäntä": 10,
    "isäntä": 10,
    "jäkälä": 10,
    "peeärrä": 10,
    "pykälä": 10,
    #
    "kiverä": 11,
    "käkkärä": 11,
    "käpälä": 11,
    "kärhämä": 11,
    "lättänä": 11,
    "mäkärä": 11,
    "säkkärä": 11,
    "täkänä": 11,
    "veiterä": 11,
    "äpärä": 11,
    #
    "jäkkärä": 12,
    "väkkärä": 12,
    #
    "kärinä": 13,
    "määkinä": 13,
    "mölinä": 13,
    "mörinä": 13,
    "möyrinä": 13,
    "siivilä": 13,

    # -Ce
    "à la carte": 8,
    "agaave": 8,
    "andante": 8,
    "beagle": 8,
    "beguine": 8,
    "bouillabaisse": 8,
    "bourgogne": 8,
    "charlotte russe": 8,
    "chenille": 8,
    "chippendale": 8,
    "college": 8,
    "cum laude": 8,
    "empire": 8,
    "ensemble": 8,
    "entrecôte": 8,
    "force majeure": 8,
    "freelance": 8,
    "ginger ale": 8,
    "image": 8,
    "karate": 8,
    "kurare": 8,
    "ladylike": 8,
    "lasagne": 8,
    "mobile": 8,
    "open house": 8,
    "poste restante": 8,
    "promille": 8,
    "ratatouille": 8,
    "tabbule": 8,
    "vivace": 8,
    #
    "jäntere": 48,
    #
    "askare": 49,
    "askele": 49,
    "huhmare": 49,
    "kantele": 49,
    "kyynele": 49,
    "petkele": 49,
    "pientare": 49,
    "saivare": 49,
    "taipale": 49,
    "utare": 49,

    # -Ci
    "aatami": 5,
    "afgaani": 5,
    "afääri": 5,
    "alleeli": 5,
    "biennaali": 5,
    "bordyyri": 5,
    "brodyyri": 5,
    "brosyyri": 5,
    "butaani": 5,
    "dipoli": 5,
    "doktriini": 5,
    "etaani": 5,
    "eteeni": 5,
    "fenkoli": 5,
    "fenoli": 5,
    "fertiili": 5,
    "fibriini": 5,
    "fosfori": 5,
    "gaeli": 5,
    "gerbiili": 5,
    "gluteeni": 5,
    "guldeni": 5,
    "humaani": 5,
    "imaami": 5,
    "japani": 5,
    "jasmiini": 5,
    "joriini": 5,
    "kaimaani": 5,
    "kajaali": 5,
    "karbiini": 5,
    "kardaani": 5,
    "kašmiri": 5,
    "kefiiri": 5,
    "kiniini": 5,
    "klausuuli": 5,
    "koktaili": 5,
    "konsiili": 5,
    "koraali": 5,
    "Koraani": 5,
    "korpraali": 5,
    "kosini": 5,
    "kreoli": 5,
    "kretliini": 5,
    "kvartääri": 5,
    "kvasaari": 5,
    "labiili": 5,
    "lantaani": 5,
    "laviini": 5,
    "liaani": 5,
    "ligniini": 5,
    "likvori": 5,
    "lojaali": 5,
    "lysoli": 5,
    "mangaani": 5,
    "martini": 5,
    "matami": 5,
    "membraani": 5,
    "mentoli": 5,
    "metaani": 5,
    "migreeni": 5,
    "modaali": 5,
    "moguli": 5,
    "mongoli": 5,
    "monstrumi": 5,
    "morfiini": 5,
    "noduuli": 5,
    "nomini": 5,
    "oktaani": 5,
    "oopiumi": 5,
    "orgaani": 5,
    "paapuuri": 5,
    "palsami": 5,
    "panini": 5,
    "patiini": 5,
    "pedaali": 5,
    "pendeli": 5,
    "pepsiini": 5,
    "pineeni": 5,
    "pluraali": 5,
    "podsoli": 5,
    "porfiini": 5,
    "porfyyri": 5,
    "primaari": 5,
    "primääri": 5,
    "profaani": 5,
    "profiili": 5,
    "propaani": 5,
    "rabbiini": 5,
    "retliini": 5,
    "reviiri": 5,
    "risiini": 5,
    "rutiini": 5,
    "salami": 5,
    "samaani": 5,
    "sampaani": 5,
    "satyyri": 5,
    "seireeni": 5,
    "strykniini": 5,
    "syaani": 5,
    "sykliini": 5,
    "tanniini": 5,
    "tapani": 5,
    "tatami": 5,
    "teiini": 5,
    "toksiini": 5,
    "triennaali": 5,
    "tyyrpuuri": 5,
    "vigvami": 5,
    "viriili": 5,
    "vulgaari": 5,
    "vulgääri": 5,
    "šamaani": 5,
    #
    "antenni": 6,
    "atolli": 6,
    "atomi": 6,
    "basenji": 6,
    "basilli": 6,
    "betoni": 6,
    "biisoni": 6,
    "biljardi": 6,
    "bisarri": 6,
    "bosoni": 6,
    "buzuki": 6,
    "daktyyli": 6,
    "detalji": 6,
    "entsyymi": 6,
    "flanelli": 6,
    "foneemi": 6,
    "fotoni": 6,
    "gaselli": 6,
    "gibboni": 6,
    "glukoosi": 6,
    "haaremi": 6,
    "hampuusi": 6,
    "hotelli": 6,
    "ikoni": 6,
    "kanjoni": 6,
    "kantoni": 6,
    "kardoni": 6,
    "karpaasi": 6,
    "kinuski": 6,
    "kolhoosi": 6,
    "kommuuni": 6,
    "kondomi": 6,
    "koturni": 6,
    "leptoni": 6,
    "likööri": 6,
    "meloni": 6,
    "monsuuni": 6,
    "monttööri": 6,
    "motelli": 6,
    "muslimi": 6,
    "narkoosi": 6,
    "neuroosi": 6,
    "oliivi": 6,
    "pakaasi": 6,
    "peijooni": 6,
    "pekoni": 6,
    "piisoni": 6,
    "plantaasi": 6,
    "pogromi": 6,
    "poliisi": 6,
    "ponttoni": 6,
    "proteesi": 6,
    "putelli": 6,
    "refleksi": 6,
    "sabloni": 6,
    "saluki": 6,
    "sardelli": 6,
    "serviisi": 6,
    "sirkoni": 6,
    "sirtaki": 6,
    "sotiisi": 6,
    "sottiisi": 6,
    "sovhoosi": 6,
    "standardi": 6,
    "sypressi": 6,
    "systeemi": 6,
    "taifuuni": 6,
    "teutoni": 6,
    "tienesti": 6,
    "toteemi": 6,
    "trapetsi": 6,
    "tribuuni": 6,
    "trotyyli": 6,
    "tsinuski": 6,
    "turkoosi": 6,
    "ukaasi": 6,
    "valloni": 6,
    "valööri": 6,
    "vinyyli": 6,
    "viskoosi": 6,
    "volyymi": 6,
    "zirkoni": 6,
    "zoonoosi": 6,
    "äksiisi": 6,

    # -Co
    "allegro": 1,
    "crescendo": 1,
    "embargo": 1,
    "flamenco": 1,
    "flamingo": 1,
    "guano": 1,
    "kalusto": 1,
    "kojeisto": 1,
    "koneikko": 1,
    "kuidusto": 1,
    "kuormasto": 1,
    "lainaamo": 1,
    "laitteisto": 1,
    "lajisto": 1,
    "lasisto": 1,
    "libido": 1,
    "munkisto": 1,
    "murteisto": 1,
    "naisisto": 1,
    "oikeisto": 1,
    "piano": 1,
    "pojisto": 1,
    "praktikko": 1,
    "raiteisto": 1,
    "rubato": 1,
    "ruovisto": 1,
    "ruususto": 1,
    "saraikko": 1,
    "sombrero": 1,
    "vaihteisto": 1,
    "vibrato": 1,
    "virasto": 1,

    # -Cö
    "hyllystö": 1,
    "käyrästö": 1,
    "lehdistö": 1,
    "lepistö": 1,
    "linssistö": 1,
    "lähistö": 1,
    "merkistö": 1,
    "pillistö": 1,
    "pylväistö": 1,
    "sisältö": 1,
    "testistö": 1,
    "tyypistö": 1,
    "väylästö": 1,

    # -CU
    "heavy": 1,
    "huitaisu": 1,
    "jiujitsu": 1,
    "karibu": 1,
    "kyhäily": 1,
    "treasury": 1,

    # -n
    "charleston": 5,
    "maraton": 5,
    #
    "backgammon": 6,
    "donjuan": 6,
    "stadion": 6,
    "stilleben": 6,
    "triatlon": 6,
    #
    "kahdeksan": 10,
    "seitsemän": 10,
    "yhdeksän": 10,
    #
    "kumpikaan": 16,
    "kumpikin": 16,
    #
    "kymmenen": 32,
    #
    "morsian": 33,
    #
    "parahin": 36,

    # -r
    "bestseller": 6,
    "freelancer": 6,
    "laudatur": 6,
    "outsider": 6,
    "rottweiler": 6,

    # -s
    "calvados": 5,
    "marakas": 5,
    "moussakas": 5,
    #
    "tournedos": 22,
    #
    "ananas": 39,
    "iskias": 39,
    #
    "vanhurskaus": 40,
    #
    "kahdeksas": 45,
    "miljoonas": 45,
    "seitsemäs": 45,
    "tuhannes": 45,
    "yhdeksäs": 45,

    # -t
    "passepartout": 22,
    "port salut": 22,

    # -C (not -n/-r/-s/-t)
    "CD-ROM": 5,

    # === Quadrisyllabic and longer ===

    # -VV
    "adagio": 1,
    #
    "odysseia": 9,
    #
    "paranoia": 10,
    #
    "atsalea": 13,
    "attasea": 13,
    "orkidea": 13,
    #
    "politbyroo": 20,
    "varietee": 20,

    # -Ca
    "abrakadabra": 9,
    "akileija": 9,
    "ballerina": 9,
    "basilika": 9,
    "dalai-lama": 9,
    "enchilada": 9,
    "hoosianna": 9,
    "ikebana": 9,
    "jakaranda": 9,
    "karateka": 9,
    "mykorritsa": 9,
    "panoraama": 9,
    "paradigma": 9,
    "praasniekka": 9,
    "propaganda": 9,
    "teoreema": 9,
    "valeriaana": 9,
    #
    "gorgonzola": 10,
    "halveksunta": 10,
    "hyperbola": 10,
    "karambola": 10,
    "protokolla": 10,
    "terrakotta": 10,
    #
    "marihuana": 11,
    #
    "ekliptika": 12,
    #
    "karakteristika": 13,
    "majolika": 13,
    "nomenklatuura": 13,
    "psykofarmaka": 13,
    "skandinaaviska": 13,
    #
    "estetiikka": 14,
    "poliklinikka": 14,
    "psykometriikka": 14,
    #
    "hänenlaisensa": 38,

    # -Cä
    "hyväksyntä": 10,
    "väheksyntä": 10,

    # -Ce
    "bavaroise": 8,
    "eau de Cologne": 8,
    "faksimile": 8,
    "karaoke": 8,
    "komedienne": 8,
    "mezzoforte": 8,
    "minestrone": 8,
    "tagliatelle": 8,
    "tragedienne": 8,
    "ukulele": 8,
    #
    "väkevöite": 48,

    # -Ci
    "follikkeli": 5,
    "kateederi": 5,
    "kollektori": 5,
    "kompostori": 5,
    "multippeli": 5,
    "varistori": 5,
    #
    "akupunktuuri": 6,
    "azerbaidžani": 6,
    "diakoni": 6,
    "firaabeli": 6,
    "inspehtori": 6,
    "prostaglandiini": 6,
    "reversiibeli": 6,
    "revolveri": 6,
    "testosteroni": 6,
    "ubikinoni": 6,
    "unioni": 6,
    "universumi": 6,
    "variaabeli": 6,
    #
    "minunlaiseni": 38,
    "sinunlaisesi": 38,

    # -Co
    "karkaisimo": 1,
    "koksittamo": 1,
    "miljoonikko": 1,
    "pantomiimikko": 1,
    "papurikko": 1,
    "pateetikko": 1,
    "poleemikko": 1,
    "poliitikko": 1,
    "pragmaatikko": 1,
    "romantikko": 1,
    "semiootikko": 1,
    "untuvikko": 1,
    "uskalikko": 1,
    #
    "katajisto": 2,
    "koordinaatisto": 2,
    "luettelo": 2,

    # -Cö
    "petäjikkö": 1,

    # -CU
    "elostelu": 1,
    "istuskelu": 1,

    # -r
    "agar-agar": 6,
    "appenzeller": 6,
    "approbatur": 6,
    "art director": 6,
    "babysitter": 6,
    "besserwisser": 6,
    "biedermeier": 6,
    "copywriter": 6,
    "improbatur": 6,
    "tonic water": 6,

    # -s
    "director musices": 5,
    #
    "stradivarius": 39,
    "trikomoonas": 39,

    # -C (not -r/-s)
    "liirumlaarum": 6,
    #
    "säteilytin": 33,
    #
    "kumpainenkaan": 38,
}

# These rules specify how to detect declensions from words, based on how many
# syllables the word has (1/2/3/more).
# The format of the rules is (declension, regex); the first matching regex will
# determine the declension.
# Notes:
# - One rule per declension, except when the declension contains very different
#   kinds of words (e.g. -VV and -C).
# - When rules don't depend on each other, sort them by declension under each
#   section (-VV etc.).
# - Each regex should match at least three words.
# - Use this as the list of all consonants: bcdfghjklmnpqrsštvwxzž (a-z minus
#   vowels plus š/ž).
# - Don't use capital letters or punctuation in rules; handle those words as
#   exceptions.

# rules for monosyllabic nouns (declension, regex)
_RULES_1SYLL = tuple((d, re.compile(r, re.VERBOSE)) for (d, r) in (
    # -VV (44 nouns, 3 exceptions)
    (19, "(ie|uo|yö)$"),
    (21, "ay$"),
    (18, "[aeiouyäö]{2}$"),

    # -CV (8 nouns, no exceptions)
    ( 8, "e$"),

    # -C (52 nouns, 10 exceptions)
    ( 5, "[bcdfghjklmnpqrsštvwxzž]$"),
))

# rules for disyllabic nouns (declension, regex)
_RULES_2SYLL = tuple((d, re.compile(r, re.VERBOSE)) for (d, r) in (
    # -VV (107 nouns, 22 exceptions)
    (17, "(aa|oo|uu)$"),
    (18, "[ai]i$"),
    (20, "(ee|öö|yy)$"),
    (21, "[aeo]y$"),
    (48, "[aäou]e$"),

    # -Ca (1022 nouns, 6 exceptions)
    (
        9,
        "( [ae] | [aei][iu] | [bcdfghjklmnpqrsštvwxzž]i | ^i )"
        "[bcdfghjklmnpqrsštvwxzž]+a$"
    ),
    (
        10,
        "( [oy] | [ou][iu] | [bcdfghjklmnpqrsštvwxzž]u | ^u )"
        "[bcdfghjklmnpqrsštvwxzž]+a$"
    ),

    # -Cä (230 nouns, 3 exceptions)
    (10, "[bcdfghjklmnpqrsštvwxzž]ä$"),

    # -Ce (409 nouns, 52 exceptions)
    (48, "[bcdfghjklmnpqrsštvwxzž]e$"),

    # -Cé (4 nouns, no exceptions)
    (21, "[bcdfghjklmnpqrsštvwxzž]é$"),

    # -Ci (1312 nouns, 134 exceptions)
    ( 7, "( [lrt]k | [lmr]p )i$"),
    (23, "[ou]hi$"),
    (25, "(ie|oi)mi$"),
    (26, "(ie|uo)[ln]i$"),
    (28, "[lnr]si$"),
    ( 5, "[bcdfghjklmnpqrsštvwxzž]i$"),

    # -CO/-CU (1417 nouns, 3 exceptions)
    ( 1, "[bcdfghjklmnpqrsštvwxzž][oöuy]$"),

    # -C (1921 nouns, 180 exceptions)
    ( 6, "( [eö]m | or )$"),
    (32, "[hmsv] en$"),
    (33, "in$"),
    (34, "[aeiouyäö] t[oö]n$"),
    (38, "nen$"),
    (40, "[eioöuy][uy]s$"),
    (39, "[eioöuy]s$"),
    (41, "[aä]s$"),
    (47, "(ll|n) [uy]t$"),
    (43, "[bcdfghjklmnpqrsštvwxzž] [uy]t$"),
    (49, "( [mv]al | [kmn]el | [är]en | [kmnv]ar | [gn]er )$"),
    ( 5, "[bcdfghjklmnpqrsštvwxzž]$"),
))

# rules for trisyllabic nouns (declension, regex)
_RULES_3SYLL = tuple((d, re.compile(r, re.VERBOSE)) for (d, r) in (
    # -VV (455 nouns, 22 exceptions)
    ( 3, "[aäei][oö]$"),
    (12, "[iuy][aä]$"),
    (15, "e[aä]$"),
    (18, "[aeiouyäö]i$"),
    (20, "ee$"),
    (48, "[uy]e$"),

    # -Ca (1504 nouns, 135 exceptions)
    ( 9, "( d | nk | ss | nt | (ee|ii|uu)tt )a$"),
    (10, "( [aou]ja | ma | o[ou]na | era | isa | va )$"),
    (11, "ona$"),
    (14, "(kk|tt)a$"),
    (13, "( [gkt] | ll | (ee|ii|[lu]u|[ag]i)n | uur | ts )a$"),
    (12, "[jlnr]a$"),

    # -Cä (520 nouns, 23 exceptions)
    ( 9, "( d | nk | ss | nt | (ee|ii|uu)tt )[aä]$"),
    (10, "( [äöy]jä | elä | mä | ärä | erä | isä | vä )$"),
    (14, "(kk|tt)ä$"),
    (13, "( [gkt] | ll | (ee|ii|[lu]u|[ag]i)n | uur | ts )ä$"),
    (12, "[jlnr]ä$"),

    # -Ce (476 nouns, 41 exceptions)
    ( 8, "tte$"),
    (49, "(pel|en|er)e$"),
    (48, "[bcdfghjklmnpqrsštvwxzž]e$"),

    # -Ci (2083 nouns, 196 exceptions)
    ( 6, "( [aäeiou]l | [au]m | [aäei]n | [aäeiouy]r )i$"),
    (16, "[eo]mpi$"),
    ( 5, "[bcdfghjklmnpqrsštvwxzž]i$"),

    # -CO/-CU (1161 nouns, 51 exceptions)
    ( 1, "( (nk|nt|tt)[oö] | aisto | t[uy] )$"),
    ( 4, "kk[oö]$"),
    ( 2, "[bcdfghjklmnpqrsštvwxzž][oöuy]$"),

    # -C (4427 nouns, 35 exceptions)
    (32, "t[aä]r$"),
    (33, "in$"),
    (34, "t[oö]n$"),
    (38, "nen$"),
    (40, "[ioöuy][uy]s$"),
    (39, "[eioöuy]s$"),
    (41, "[aä]s$"),
    (47, "[ln][uy]t$"),
    ( 5, "[bcdfghjklmnpqrsštvwxzž]$"),
))

# rules for quadrisyllabic and longer nouns (declension, regex)
_RULES_4SYLL = tuple((d, re.compile(r, re.VERBOSE)) for (d, r) in (
    # -VV (649 nouns, 8 exceptions)
    ( 3, "[bcdfghjklmnpqrsštvwxzž]i[oö]$"),
    (12, "[bcdfghjklmnpqrsštvwxzž][ei]a$"),

    # -Ca (903 nouns, 34 exceptions)
    ( 9, "( [air]kka | lla | i[in]na | ssa | ta | ža )$"),
    (12, "( [lnst]ija | la )$"),
    (10, "[bcdfghjklmnpqrsštvwxzž]a$"),

    # -Cä (275 nouns, 2 exceptions)
    ( 9, "tä$"),
    (12, "[lnst]ijä$"),
    (10, "[bcdfghjklmnpqrsštvwxzž]ä$"),

    # -Ci (2282 nouns, 21 exceptions)
    (
        6,
        "( [gkp]el | [drt]um | [klnptv]ar | [dgknt]er | "
        "(i|l|s|kt|st|tt)or )i$"
    ),
    ( 5, "[bcdfghjklmnpqrsštvwxzž]i$"),

    # -CO/-CU (627 nouns, 19 exceptions)
    ( 2, "( m[oö] | l[uy] )$"),
    ( 4, "[dgjlmnprstv]ikk[oö]$"),
    ( 1, "[bcdfghjklmnpqrsštvwxzž][oöuy]$"),

    # -C (4573 nouns, 16 exceptions)
    (32, "t[aä]r$"),
    (34, "t[oö]n$"),
    (38, "nen(kin)?$"),
    (40, "[iuy][uy]s$"),
    (39, "[eioöuy]s$"),
    (41, "[aä]s$"),
    (47, "n[uy]t$"),
    ( 5, "[bcdfghjklmnpqrsštvwxzž]$"),
))

def get_declensions(noun, useExceptions=True):
    """noun: a Finnish noun in nominative singular
    return: a tuple of 0-2 Kotus declensions (each 1-49)"""

    noun = noun.strip("'- ")

    try:
        return _MULTI_DECLENSION_NOUNS[noun]
    except KeyError:
        pass

    if useExceptions:
        try:
            return (_EXCEPTIONS[noun],)
        except KeyError:
            pass

    syllCnt = countsyll.count_syllables(noun)
    if syllCnt == 1:
        rules = _RULES_1SYLL
    elif syllCnt == 2:
        rules = _RULES_2SYLL
    elif syllCnt == 3:
        rules = _RULES_3SYLL
    else:
        rules = _RULES_4SYLL

    for (declension, regex) in rules:
        if regex.search(noun) is not None:
            return (declension,)
    return ()

def _check_redundant_exceptions():
    for noun in _EXCEPTIONS:
        detectedDeclensions = get_declensions(noun, False)
        if detectedDeclensions \
        and _EXCEPTIONS[noun] == list(detectedDeclensions)[0]:
            print(f'Redundant exception: "{noun}"')

def main():
    _check_redundant_exceptions()

    if len(sys.argv) != 2:
        sys.exit(
            "Argument: a Finnish noun (including adjectives/pronouns/"
            "numerals, excluding compounds) in nominative singular. Print "
            "the Kotus declension(s) (1-49)."
        )
    noun = sys.argv[1]

    declensions = get_declensions(noun)
    if not declensions:
        sys.exit("Unrecognized noun.")

    for d in sorted(declensions):
        print(f'Declension {d} (like "{DECLENSION_DESCRIPTIONS[d]}")')

if __name__ == "__main__":
    main()
