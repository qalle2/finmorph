"""Get the Kotus declension of a Finnish noun."""

# Note: A = a/ä, O = o/ö, U = u/y, V = any vowel, C = any consonant.

import re, sys
import countsyll

# A typical noun in each declension.
# Forms: nominative sg, genitive sg, genitive pl, partitive sg, partitive pl, illative sg,
# illative pl.
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
    11: "omen|a, -an, -ien/-oiden/-ojen, -aa, -ia/-oita/-oja, -aan, -iin/-oihin",
    12: "kulkij|a, -an, -oiden, -aa, -oita, -aan, -oihin",
    13: "katisk|a, -an, -oiden/-ojen, -aa, -oita/-oja, -aan, -oihin",
    14: "solak|ka, -an, -oiden/-kojen, -kaa, -oita/-koja, -kaan, -(k)oihin",
    15: "korke|a, -an, -iden, -a(t)a, -ita, -aan, -isiin/-ihin",
    16: "vanhem|pi, -man, -pien, -paa, -pia, -paan, -piin",
    17: "vapa|a, -an, -iden, -ata, -ita, -aseen, -isiin/-ihin",
    18: "maa, -n, maiden, -ta, maita, -han, maihin",
    19: "suo, -n, soiden, -ta, soita, -hon, soihin",
    20: "file|e, -en, -iden, -etä, -itä, -ehen/-eseen, -ihin/-isiin",
    21: "rosé, -n, -iden, -ta, -ita, -hen, -ihin",
    22: "parfait, -'n, -'iden, -'ta, -'ita, -'hen, -'ihin",
    23: "tiil|i, -en, -ien, -tä, -iä, -een, -iin",
    24: "un|i, -en, -ien/-ten, -ta, -ia, -een, -iin",
    25: "toim|i, -en, -ien/tointen, -ea/tointa, -ia, -een, -iin",
    26: "pien|i, -en, -ten/-ien, -tä, -iä, -een, -iin",
    27: "käsi, käden, -en/kätten, kättä, -ä, käteen, -in",
    28: "kyn|si, -nen, -sien/-tten, -ttä, -siä, -teen, -siin",
    29: "laps|i, -en, lasten/-ien, lasta, -ia, -een, -iin",
    30: "veits|i, -en, -ien/veisten, veistä, -iä, -een, -iin",
    31: "kaksi, kahden, -en, kahta, -a, kahteen, -in",
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
    49: "askel|(e), -e(e)n, -ien/-eiden/-(eit)ten, -(et)ta, -ia/-eita, -ee(see)n, -(eis)iin/-eihin",
}

# nouns with more than one declension (key = noun, value = set of declensions)
_MULTI_DECLENSION_NOUNS = {
    # different meanings
    "lahti": {5, 7},
    "laki": {5, 7},
    "palvi": {5, 7},
    "ripsi": {5, 7},
    "saksi": {5, 7},  # "sakset" vs. "anglosaksi"
    "sini": {5, 7},
    #
    "kuori": {5, 26},
    "viini": {5, 26},
    "vuori": {5, 26},
    #
    "peitsi": {5, 30},
    #
    "puola": {9, 10},
    #
    "kikkara": {11, 12},
    #
    "ilmeinen": {18, 38},  # 18 (e.g. "vähäilmeinen") is probably an error
    #
    "kuusi": {24, 27},
    #
    "ahtaus": {39, 40,},
    "karvaus": {39, 40,},
    "vakaus":  {39, 40},
    #
    "kymmenes": {39, 45},

    # same meanings
    "menu": {1, 21},
    #
    "caddie": {3, 8},
    #
    "finaali": {5, 6},  # "finaali" vs. "semifinaali"
    #
    "alpi": {5, 7},
    "helpi": {5, 7},
    "kaihi": {5, 7},
    "karhi": {5, 7},
    "kymi": {5, 7},
    "vyyhti": {5, 7},
    #
    "sioux": {5, 22},
    #
    "syli": {5, 23},
    #
    "csárdás": {5, 39},
    "kuskus":  {5, 39},
    #
    "ori": {5, 48},
    #
    "kolme": {7, 8},  # 8 in singular, 7 in plural
    #
    "hapsi": {7, 29},
    "uksi":  {7, 29},
    #
    "siitake": {8, 48},
    #
    "aneurysma": {9, 10},
    "kysta": {9, 10},
    "lyyra": {9, 10},
    #
    "humala": {10, 11},
    #
    "tanhua": {12, 15},
    #
    "rosvous": {39, 40},
    "siivous":  {39, 40},
    #
    "havas":  {39, 41},
    "kallas": {39, 41},
    "koiras": {39, 41},
    "olas": {39, 41},
    "pallas": {39, 41},
    "uros": {39, 41},
}

# exceptions to rules (key = noun, value = declension)
# order: first by syllable count, then by ending, then by declension, then alphabetically
# note: if there are more than one line of words per declension, separate them with empty comment
#       lines ("#") for readability
_EXCEPTIONS = {
    # === monosyllabic ===

    # less than three monosyllabic nouns in these declensions
    "show": 22,
    "ien": 32,
    "näin": 33, "puin": 33,
    "tain": 36,
    "hius": 39, "taus": 39,
    "ies": 41, "ruis": 41,
    "mies": 42,
    "hie": 48,

    "AIDS": 5, "LED": 5,
    "brie": 21, "clou": 21,

    # === disyllabic ===

    # less than three disyllabic nouns in these declensions
    "kumpi": 16,
    "veitsi": 30,
    "lämmin": 35,
    "vasen": 37,
    "kevät": 44, "venät": 44,
    "tuhat": 46,

    # -VV
    "duo": 1, "trio": 1,
    "boutique": 8, "petanque": 8,
    "dia": 9, "maya": 9,
    "boa": 10,
    "hynttyy": 17,
    "frisbee": 18, "huuhaa": 18, "peeaa": 18, "puusee": 18,
    "nugaa": 20, "raguu": 20, "sampoo": 20, "trikoo": 20, "voodoo": 20,
    "fondue": 21, "reggae": 21, "tax-free": 21,
    "aie": 48, "säie": 48,

    # -CA
    "iskä": 9, "krypta": 9, "lymfa": 9, "nyintä": 9, "ryintä": 9, "suola": 9,
    "saaja": 10, "saapa": 10, "saava": 10,

    # -VCe
    "ale": 8, "beige": 8, "bäne": 8, "crêpe": 8, "deadline": 8, "folklore": 8, "freestyle": 8,
    "gruyère": 8, "hardware": 8, "jade": 8, "joule": 8, "lime": 8, "madame": 8, "mangrove": 8,
    "milk shake": 8, "ope": 8, "poplore": 8, "pose": 8, "psyyke": 8, "ragtime": 8, "saame": 8,
    "sake": 8, "soft ice": 8, "software": 8, "striptease": 8, "tele": 8, "toope": 8,
    #
    "bile": 20,

    # -CCe
    "akne": 8, "crème fraîche": 8, "duchesse": 8, "forte": 8, "genre": 8, "itse": 8, "jeppe": 8,
    "kalle": 8, "kurre": 8, "lande": 8, "manne": 8, "mousse": 8, "nalle": 8, "nasse": 8,
    "nisse": 8, "nukke": 8, "pelle": 8, "penne": 8, "polle": 8, "puzzle": 8, "quenelle": 8,
    "single": 8, "tilde": 8, "vaudeville": 8,

    # -VCi
    "tuoli": 5,
    #
    "hauki": 7, "hiki": 7, "joki": 7, "kivi": 7, "koipi": 7, "käki": 7, "lovi": 7, "läpi": 7,
    "mäki": 7, "nimi": 7, "noki": 7, "ovi": 7, "piki": 7, "povi": 7, "reki": 7, "rupi": 7,
    "savi": 7, "seimi": 7, "siipi": 7, "suomi": 7, "suvi": 7, "tuki": 7, "tyvi": 7, "veli": 7,
    "väki": 7,
    #
    "moni": 23, "riihi": 23, "tiili": 23, "tuli": 23,
    "hiili": 24, "hiiri": 24, "huuli": 24, "kusi": 24, "meri": 24, "ruuhi": 24, "uni": 24,
    "lumi": 25, "luomi": 25, "taimi": 25, "tuomi": 25,
    #
    "jousi": 26, "juuri": 26, "kaari": 26, "niini": 26, "nuori": 26, "saari": 26, "suuri": 26,
    "sääri": 26, "teeri": 26, "tuuli": 26, "tyyni": 26, "veri": 26, "vieri": 26, "ääni": 26,
    "ääri": 26,
    #
    "heisi": 27, "hiisi": 27, "kausi": 27, "kesi": 27, "käsi": 27, "köysi": 27, "liesi": 27,
    "mesi": 27, "niisi": 27, "paasi": 27, "reisi": 27, "susi": 27, "sysi": 27, "tosi": 27,
    "täysi": 27, "uusi": 27, "vesi": 27, "viisi": 27, "vuosi": 27,

    # -CCi
    "LYHKI": 5, "mansi": 5, "sutki": 5,
    #
    "appi": 7, "haahti": 7, "hanhi": 7, "hanki": 7, "happi": 7, "helmi": 7, "henki": 7, "hirvi": 7,
    "järvi": 7, "kaikki": 7, "kanki": 7, "kaski": 7, "kiiski": 7, "koski": 7, "kärhi": 7,
    "lehti": 7, "leski": 7, "länki": 7, "nummi": 7, "nurmi": 7, "närhi": 7, "onki": 7, "onni": 7,
    "parvi": 7, "pilvi": 7, "polvi": 7, "poski": 7, "päitsi": 7, "pälvi": 7, "saarni": 7,
    "saksi": 7, "salmi": 7, "sappi": 7, "sarvi": 7, "soppi": 7, "sormi": 7, "suitsi": 7,
    "suksi": 7, "sänki": 7, "sääksi": 7, "sääski": 7, "talvi": 7, "tammi": 7, "tilhi": 7,
    "torvi": 7, "tuppi": 7, "typpi": 7, "tähti": 7, "vaski": 7, "viiksi": 7, "vuoksi": 7,
    #
    "lapsi": 29,
    "haaksi": 31, "kaksi": 31, "yksi": 31,

    # -CO
    "go-go": 18,

    # -CU
    "kung-fu": 21,
    "kiiru": 48,

    # -Vl
    "kennel": 5,
    "diesel": 6, "rial": 6,
    "nivel": 32, "sävel": 32,
    "seppel": 49, "udar": 49,

    # -Vn
    "drive-in": 5, "hymen": 5, "kelvin": 5, "pinyin": 5,
    #
    "bourbon": 6, "chanson": 6, "kaanon": 6, "lumen": 6, "luumen": 6, "nailon": 6, "nelson": 6,
    "nylon": 6, "pyton": 6,
    #
    "hapan": 33, "laidun": 33, "sydän": 33,
    #
    "alin": 36, "enin": 36, "likin": 36, "lähin": 36, "parhain": 36, "sisin": 36, "taain": 36,
    "uloin": 36, "vanhin": 36, "ylin": 36,

    # -Vr
    "agar": 6, "bitter": 6, "blazer": 6, "dealer": 6, "kassler": 6, "laser": 6, "loafer": 6,
    "schäfer": 6, "sitar": 6, "snooker": 6, "weber": 6, "vesper": 6, "voucher": 6,
    #
    "sisar": 32, "tatar": 32, "tytär": 32,
    "auer": 49,

    # -CAs
    "aidas": 39, "atlas": 39, "emäs": 39, "haljas": 39, "harjas": 39, "jalas": 39, "juudas": 39,
    "kaimas": 39, "kannas": 39, "kehräs": 39, "kuvas": 39, "lihas": 39, "luudas": 39, "madras": 39,
    "mullas": 39, "nahas": 39, "ohjas": 39, "priimas": 39, "sammas": 39, "tervas": 39, "teräs": 39,
    "vastas": 39, "vihdas": 39, "viinas": 39, "vitsas": 39,
    #
    "kolmas": 45, "neljäs": 45, "nollas": 45, "sadas": 45,

    # -es
    "blues": 5,
    "kirves": 41, "äes": 41,
    "kahdes": 45, "kuudes": 45, "mones": 45, "viides": 45, "yhdes": 45,

    # -is
    "altis": 41, "aulis": 41, "kallis": 41, "kaunis": 41, "kauris": 41, "nauris": 41, "raitis": 41,
    "ruumis": 41, "saalis": 41, "tiivis": 41, "tyyris": 41, "valmis": 41,

    # -AUs
    "ahnaus": 40, "harmaus": 40, "hartaus": 40, "hauraus": 40, "herraus": 40, "hitaus": 40,
    "hurskaus": 40, "irstaus": 40, "karsaus": 40, "kiivaus": 40, "kirkkaus": 40, "kitsaus": 40,
    "kuulaus": 40, "kärkkäys": 40, "liukkaus": 40, "maukkaus": 40, "puhtaus": 40, "raihnaus": 40,
    "rakkaus": 40, "raskaus": 40, "reippaus": 40, "riettaus": 40, "rikkaus": 40, "runsaus": 40,
    "sairaus": 40, "suulaus": 40, "työläys": 40, "valppaus": 40, "vapaus": 40, "varkaus": 40,
    "vauraus": 40, "vehmaus": 40, "viekkaus": 40, "vieraus": 40, "viisaus": 40, "vilkkaus": 40,
    "vuolaus": 40, "ylväys": 40,

    # -eUs
    "kiveys": 39, "loveus": 39, "pikeys": 39, "poikkeus": 39, "risteys": 39, "saveus": 39,
    "tyveys": 39,

    # -OUs
    "couscous": 5,
    #
    "holhous": 39, "kirous": 39, "kokous": 39, "kumous": 39, "linkous": 39, "lumous": 39,
    "nuohous": 39, "patous": 39, "putous": 39, "rukous": 39, "tarjous": 39, "verhous": 39,

    # -UUs
    "kehruus": 39, "makuus": 39, "persuus": 39,

    # -CUs
    "ryntys": 41, "vantus": 41,

    # -Vt
    "input": 5, "output": 5,
    #
    "beignet": 22, "bouquet": 22, "buffet": 22, "gourmet": 22, "nougat": 22, "parfait": 22,
    "ragoût": 22,

    # -C (not -l/-n/-r/-s/-t)
    "edam": 6, "gallup": 6,
    "bordeaux": 22, "know-how": 22,

    # === trisyllabic ===

    # less than three trisyllabic nouns in these declensions
    "brasserie": 21, "cha-cha-cha": 21,
    "parahin": 36,

    # -VV
    "aaloe": 3, "collie": 3, "embryo": 3, "lassie": 3, "oboe": 3, "zombie": 3,
    "feijoa": 10,
    "apnea": 12, "hebrea": 12, "heprea": 12, "idea": 12, "pallea": 12, "urea": 12,
    "media": 13,
    "ainoa": 15,
    "homssantuu": 18, "kanapee": 18, "munaskuu": 18, "pelakuu": 18, "rokokoo": 18, "tenkkapoo": 18,

    # -VlA
    "koala": 9, "tequila": 9,
    #
    "hankala": 10, "jumala": 10, "jäkälä": 10, "kamala": 10, "katala": 10, "kavala": 10,
    "matala": 10, "nokkela": 10, "ovela": 10, "pykälä": 10, "sukkela": 10, "tukala": 10,
    #
    "apila": 13, "kampela": 13, "manila": 13, "sairaala": 13, "siivilä": 13, "sikala": 13,
    "takila": 13, "viola": 13,

    # -VmA
    "ekseema": 9,
    "hekuma": 11, "kärhämä": 11, "paatsama": 11, "probleema": 11, "ödeema": 11,
    "salama": 12,
    "suurima": 13,

    # -VnA
    "gallona": 10, "ihana": 10, "leijona": 10,
    #
    "lattana": 11, "lättänä": 11, "maruna": 11, "murena": 11, "ohrana": 11, "omena": 11,
    "orpana": 11, "papana": 11, "pipana": 11, "poppana": 11, "sikuna": 11, "täkänä": 11,
    #
    "harppuuna": 12,
    #
    "aivina": 13, "arina": 13, "ipana": 13, "kahina": 13, "kohina": 13, "kopina": 13, "kuhina": 13,
    "kärinä": 13, "marina": 13, "maukuna": 13, "määkinä": 13, "mölinä": 13, "mörinä": 13,
    "möyrinä": 13, "paukkina": 13, "piekana": 13, "porina": 13, "rahina": 13, "ramina": 13,
    "reppana": 13, "retsina": 13, "ruutana": 13, "smetana": 13, "tuoksina": 13,

    # -VrA
    "kimaira": 9, "tiaara": 9,
    "amfora": 10, "ankara": 10, "avara": 10, "kumara": 10,
    #
    "hapera": 11, "hatara": 11, "hattara": 11, "hutera": 11, "itara": 11, "kihara": 11,
    "kiverä": 11, "käkkärä": 11, "mäkärä": 11, "sikkara": 11, "säkkärä": 11, "tomera": 11,
    "vanttera": 11, "veiterä": 11, "äpärä": 11,
    #
    "jäkkärä": 12, "kamera": 12, "kolera": 12, "littera": 12, "ooppera": 12, "väkkärä": 12,
    #
    "gerbera": 13, "hetaira": 13, "ketara": 13, "kitara": 13, "madeira": 13, "matara": 13,
    "sikkura": 13, "tempera": 13, "vaahtera": 13,

    # -VCA (not -VlA/-VmA/-VnA/-VrA)
    "ameba": 9, "guava": 9, "prostata": 9, "toccata": 9,
    "pomada": 10,
    #
    "ahava": 11, "apaja": 11, "harava": 11, "judoka": 11, "käpälä": 11, "leukoija": 11,
    "mimoosa": 11,
    #
    "paprika": 12, "passiiva": 12,
    "aktiiva": 13, "meduusa": 13, "papaija": 13, "reseda": 13,

    # -CCA
    "alfalfa": 9, "antiikva": 9, "aortta": 9, "canasta": 9, "chinchilla": 9, "dilemma": 9,
    "marimba": 9, "nautiikka": 9, "papilla": 9, "regatta": 9, "ruustinna": 9, "sialma": 9,
    "sinsilla": 9, "tonsilla": 9,
    #
    "emäntä": 10, "huuhdonta": 10, "isäntä": 10, "kolonna": 10, "madonna": 10, "peeärrä": 10,
    "reskontra": 10,
    #
    "algebra": 11, "mahatma": 11,
    #
    "artikla": 13, "karisma": 13, "maailma": 13, "mantilja": 13, "perenna": 13, "prinsessa": 13,
    "taverna": 13, "vanilja": 13, "vernissa": 13,
    #
    "ulappa": 14,

    # -VCe
    "agaave": 8, "beguine": 8, "chippendale": 8, "college": 8, "cum laude": 8, "empire": 8,
    "entrecôte": 8, "force majeure": 8, "ginger ale": 8, "image": 8, "karate": 8, "kurare": 8,
    "ladylike": 8, "mobile": 8, "open house": 8, "tabbule": 8, "vivace": 8,
    #
    "jäntere": 48,
    #
    "askare": 49, "askele": 49, "huhmare": 49, "kantele": 49, "kyynele": 49, "petkele": 49,
    "pientare": 49, "saivare": 49, "taipale": 49, "utare": 49,

    # -CCe
    "à la carte": 8, "andante": 8, "beagle": 8, "bouillabaisse": 8, "bourgogne": 8,
    "charlotte russe": 8, "chenille": 8, "ensemble": 8, "freelance": 8, "lasagne": 8,
    "poste restante": 8, "promille": 8, "ratatouille": 8,

    # -Vki
    "buzuki": 6, "saluki": 6, "sirtaki": 6,

    # -ali
    "biennaali": 5, "kajaali": 5, "koraali": 5, "korpraali": 5, "lojaali": 5, "modaali": 5,
    "pedaali": 5, "pluraali": 5, "triennaali": 5,

    # -eli
    "alleeli": 5, "gaeli": 5, "pendeli": 5,

    # -ili
    "fertiili": 5, "gerbiili": 5, "koktaili": 5, "konsiili": 5, "labiili": 5, "profiili": 5,
    "viriili": 5,

    # -oli
    "dipoli": 5, "fenkoli": 5, "fenoli": 5, "kreoli": 5, "lysoli": 5, "mentoli": 5, "mongoli": 5,
    "podsoli": 5,

    # -uli
    "klausuuli": 5, "moguli": 5, "noduuli": 5,

    # -yli
    "daktyyli": 6, "trotyyli": 6, "vinyyli": 6,

    # -Vmi
    "aatami": 5, "imaami": 5, "matami": 5, "monstrumi": 5, "oopiumi": 5, "palsami": 5, "salami": 5,
    "tatami": 5, "vigvami": 5,
    #
    "atomi": 6, "entsyymi": 6, "foneemi": 6, "haaremi": 6, "kondomi": 6, "muslimi": 6,
    "pogromi": 6, "systeemi": 6, "toteemi": 6, "volyymi": 6,

    # -ani
    "afgaani": 5, "butaani": 5, "etaani": 5, "humaani": 5, "japani": 5, "kaimaani": 5,
    "kardaani": 5, "Koraani": 5, "lantaani": 5, "liaani": 5, "mangaani": 5, "membraani": 5,
    "metaani": 5, "oktaani": 5, "orgaani": 5, "profaani": 5, "propaani": 5, "samaani": 5,
    "šamaani": 5, "sampaani": 5, "syaani": 5, "tapani": 5,

    # -eni
    "eteeni": 5, "gluteeni": 5, "guldeni": 5, "migreeni": 5, "pineeni": 5, "seireeni": 5,

    # -ini
    "doktriini": 5, "fibriini": 5, "jasmiini": 5, "joriini": 5, "karbiini": 5, "kiniini": 5,
    "kosini": 5, "kretliini": 5, "laviini": 5, "ligniini": 5, "martini": 5, "morfiini": 5,
    "nomini": 5, "panini": 5, "patiini": 5, "pepsiini": 5, "porfiini": 5, "rabbiini": 5,
    "retliini": 5, "risiini": 5, "rutiini": 5, "strykniini": 5, "sykliini": 5, "tanniini": 5,
    "teiini": 5, "toksiini": 5,

    # -oni
    "betoni": 6, "biisoni": 6, "bosoni": 6, "fotoni": 6, "gibboni": 6, "ikoni": 6, "kanjoni": 6,
    "kantoni": 6, "kardoni": 6, "leptoni": 6, "meloni": 6, "peijooni": 6, "pekoni": 6,
    "piisoni": 6, "ponttoni": 6, "sabloni": 6, "sirkoni": 6, "teutoni": 6, "valloni": 6,
    "zirkoni": 6,

    # -uni
    "kommuuni": 6, "monsuuni": 6, "taifuuni": 6, "tribuuni": 6,

    # -Vri
    "afääri": 5, "bordyyri": 5, "brodyyri": 5, "brosyyri": 5, "fosfori": 5, "kašmiri": 5,
    "kefiiri": 5, "kvartääri": 5, "kvasaari": 5, "likvori": 5, "paapuuri": 5, "porfyyri": 5,
    "primaari": 5, "primääri": 5, "reviiri": 5, "satyyri": 5, "tyyrpuuri": 5, "vulgaari": 5,
    "vulgääri": 5,
    #
    "likööri": 6, "monttööri": 6, "valööri": 6,

    # -Vsi
    "glukoosi": 6, "hampuusi": 6, "karpaasi": 6, "kolhoosi": 6, "narkoosi": 6, "neuroosi": 6,
    "pakaasi": 6, "plantaasi": 6, "poliisi": 6, "proteesi": 6, "serviisi": 6, "sotiisi": 6,
    "sottiisi": 6, "sovhoosi": 6, "turkoosi": 6, "ukaasi": 6, "viskoosi": 6, "zoonoosi": 6,
    "äksiisi": 6,

    # -Vvi
    "oliivi": 6,

    # -CCi
    "antenni": 6, "atolli": 6, "basenji": 6, "basilli": 6, "biljardi": 6, "bisarri": 6,
    "detalji": 6, "flanelli": 6, "gaselli": 6, "hotelli": 6, "kinuski": 6, "koturni": 6,
    "motelli": 6, "putelli": 6, "refleksi": 6, "sardelli": 6, "standardi": 6, "sypressi": 6,
    "tienesti": 6, "trapetsi": 6, "tsinuski": 6,

    # -stO
    "hyllystö": 1, "kalusto": 1, "kojeisto": 1, "kuidusto": 1, "kuormasto": 1, "käyrästö": 1,
    "laitteisto": 1, "lajisto": 1, "lasisto": 1, "lehdistö": 1, "lepistö": 1, "linssistö": 1,
    "lähistö": 1, "merkistö": 1, "munkisto": 1, "murteisto": 1, "naisisto": 1, "oikeisto": 1,
    "pillistö": 1, "pojisto": 1, "pylväistö": 1, "raiteisto": 1, "ruovisto": 1, "ruususto": 1,
    "testistö": 1, "tyypistö": 1, "vaihteisto": 1, "virasto": 1, "väylästö": 1,

    # -CO (not -stO)
    "allegro": 1, "crescendo": 1, "embargo": 1, "flamenco": 1, "flamingo": 1, "guano": 1,
    "heavy": 1, "koneikko": 1, "lainaamo": 1, "libido": 1, "piano": 1, "praktikko": 1, "rubato": 1,
    "saraikko": 1, "sisältö": 1, "sombrero": 1, "vibrato": 1,

    # -CU
    "huitaisu": 1, "jiujitsu": 1, "karibu": 1, "kyhäily": 1, "treasury": 1,

    # -n
    "charleston": 5, "maraton": 5,
    "backgammon": 6, "donjuan": 6, "stadion": 6, "stilleben": 6, "triatlon": 6,
    "kahdeksan": 10, "seitsemän": 10, "yhdeksän": 10,
    "kumpikaan": 16, "kumpikin": 16,
    "kymmenen": 32,
    "morsian": 33,

    # -r
    "bestseller": 6, "freelancer": 6, "laudatur": 6, "outsider": 6, "rottweiler": 6,

    # -s
    "calvados": 5, "marakas": 5, "moussakas": 5,
    "tournedos": 22,
    "ananas": 39, "iskias": 39,
    "vanhurskaus": 40,
    "kahdeksas": 45, "miljoonas": 45, "seitsemäs": 45, "yhdeksäs": 45,
    "tuhannes": 45,

    # -C (not -n/-r/-s)
    "CD-ROM": 5,
    "passepartout": 22, "port salut": 22,

    # === quadrisyllabic and longer ===

    # less than three quadrisyllabic or longer nouns in these declensions
    "marihuana": 11,
    "politbyroo": 20, "varietee": 20,
    "väkevöite": 48,

    # -VV
    "adagio": 1,
    "odysseia": 9,
    "paranoia": 10,
    "atsalea": 13, "attasea": 13, "orkidea": 13,

    # -VVCA
    "akileija": 9, "panoraama": 9, "teoreema": 9, "valeriaana": 9,
    "nomenklatuura": 13,

    # -CVCA
    "ballerina": 9, "basilika": 9, "dalai-lama": 9, "enchilada": 9, "ikebana": 9, "jakaranda": 9,
    "karateka": 9, "propaganda": 9,
    #
    "gorgonzola": 10, "hyperbola": 10, "karambola": 10,
    "ekliptika": 12,
    "karakteristika": 13, "majolika": 13, "psykofarmaka": 13,

    # -CCA
    "abrakadabra": 9, "hoosianna": 9, "mykorritsa": 9, "paradigma": 9, "praasniekka": 9,
    "halveksunta": 10, "hyväksyntä": 10, "protokolla": 10, "terrakotta": 10, "väheksyntä": 10,
    "skandinaaviska": 13,
    "estetiikka": 14, "poliklinikka": 14, "psykometriikka": 14,
    "hänenlaisensa": 38,

    # -VCe
    "bavaroise": 8, "faksimile": 8, "karaoke": 8, "minestrone": 8, "ukulele": 8,

    # -CCe
    "eau de Cologne": 8, "komedienne": 8, "mezzoforte": 8, "tagliatelle": 8, "tragedienne": 8,

    # -VCi
    "follikkeli": 5, "kateederi": 5, "kollektori": 5, "kompostori": 5, "multippeli": 5,
    "varistori": 5,
    #
    "akupunktuuri": 6, "azerbaidžani": 6, "diakoni": 6, "firaabeli": 6, "inspehtori": 6,
    "prostaglandiini": 6, "reversiibeli": 6, "revolveri": 6, "testosteroni": 6, "ubikinoni": 6,
    "unioni": 6, "universumi": 6, "variaabeli": 6,
    #
    "minunlaiseni": 38, "sinunlaisesi": 38,

    # -ikkO
    "miljoonikko": 1, "pantomiimikko": 1, "papurikko": 1, "pateetikko": 1, "petäjikkö": 1,
    "poleemikko": 1, "poliitikko": 1, "pragmaatikko": 1, "romantikko": 1, "semiootikko": 1,
    "untuvikko": 1, "uskalikko": 1,

    # -CO (not -kO)
    "karkaisimo": 1, "koksittamo": 1,
    "katajisto": 2, "koordinaatisto": 2, "luettelo": 2,

    # -CU
    "elostelu": 1, "istuskelu": 1,

    # -r
    "agar-agar": 6, "appenzeller": 6, "approbatur": 6, "art director": 6, "babysitter": 6,
    "besserwisser": 6, "biedermeier": 6, "copywriter": 6, "improbatur": 6, "tonic water": 6,

    # -C (not -r)
    "director musices": 5,
    "backgammon": 6, "liirumlaarum": 6,
    "säteilytin": 33,
    "kumpainenkaan": 38,
    "stradivarius": 39, "trikomoonas": 39,
}

# Note: rules in _RULES_1SYLL etc.:
# - Handle as many words as possible with rules instead of exceptions.
# - Make rules as short as possible (feel free to reorder them if needed).
# - One rule per declension. Exception: when the declension contains very different kinds of words
#   (e.g. -VV and -C), use one rule per declension per section.
# - When rules don't depend on each other, sort them by declension.
# - If a rule depends on another, always mention it.
# - Each regex should match at least three words.
# - Use this as the list of all consonants: bcdfghjklmnpqrsštvwxzž (a-z minus vowels plus š/ž).
# - No capital letters in rules; handle those words as exceptions.

# rules for monosyllabic nouns (declension, regex)
_RULES_1SYLL = (
    ( 5, r"[bcdfghjklmnpqrsštvwxzž]$"),  # -C
    (19, r"( ie | uo | yö )$"),          # -ie/-UO
    (21, r"ay$"),                        # -ay
    (18, r"[aeiouyäö]{2}$"),             # -VV except those in decl. 19, 21
    ( 8, r"e$"),                         # -e except those in decl. 18, 19
)

# rules for disyllabic nouns (declension, regex)
_RULES_2SYLL = (
    # === -VV ===

    (17, r"( aa | oo | uu )$"),  # -aa/-oo/-uu
    (18, r"[ai]i$"),             # -ai/-ii
    (20, r"( ee | öö | yy )$"),  # -ee/-öö/-yy
    (21, r"[aeo]y$"),            # -ay/-ey/-oy
    (48, r"[aäou]e$"),           # -Ae/-oe/-ue

    # === -CV ===

    # -CO/-CU
    ( 1, r"[bcdfghjklmnpqrsštvwxzž][oöuy]$"),
    # -lki/-rki/-tki/-lpi/-mpi/-rpi
    ( 7, r"( [lrt]k | [lmr]p )i$"),
    # -a/-e/-ai/-ei/-ii/-au/-eu/-iu/-Ci/i + (C)(C)Ca
    ( 9, r"( [ae] | [aei][iu] | [bcdfghjklmnpqrsštvwxzž]i | ^i )[bcdfghjklmnpqrsštvwxzž]+a$"),
    # -o/-y/-oi/-ui/-ou/-uu/-Cu/u + (C)(C)Ca
    (10, r"( [oy] | [ou][iu] | [bcdfghjklmnpqrsštvwxzž]u | ^u )[bcdfghjklmnpqrsštvwxzž]+a$"),
    # -Cä
    (10, r"[bcdfghjklmnpqrsštvwxzž]ä$"),
    # -Cé
    (21, r"[bcdfghjklmnpqrsštvwxzž]é$"),
    # -ohi/-uhi
    (23, r"[ou]hi$"),
    # -iemi/-oimi
    (25, r"( ie | oi )mi$"),
    # -ieli/-uoli/-ieni/-uoni
    (26, r"( ie | uo )[ln]i$"),
    # -lsi/-nsi/-rsi
    (28, r"[lnr]si$"),
    # -Ci except those in declensions 7, 23, 25-26, 28 (many exceptions)
    ( 5, r"[bcdfghjklmnpqrsštvwxzž]i$"),

    # -Ce
    (48, r"[bcdfghjklmnpqrsštvwxzž]e$"),

    # === -C ===

    ( 6, r"( [eö]m | or )$"),                # -em/-öm/-or
    (32, r"[hmsv]en$"),                      # -hen/-men/-sen/-ven
    (33, r"in$"),                            # -in
    (34, r"[aeiouyäö]t[oö]n$"),              # -VtOn
    (38, r"nen$"),                           # -nen
    (40, r"[eioöuy][uy]s$"),                 # -eUs/-iUs/-OUs/-UUs
    (39, r"[eioöuy]s$"),                     # -es/-is/-Os/-Us except those in decl. 40 (many exc.)
    (41, r"[aä]s$"),                         # -As (many exceptions)
    (47, r"( ll | n )[uy]t$"),               # -llUt/-nUt
    (43, r"[bcdfghjklmnpqrsštvwxzž][uy]t$"), # -CUt except those in declension 47
    (49, r"( [mv]al | [kmn]el | [är]en | [kmnv]ar | [gn]er )$"),  # some of -C + a/e + l/n/r
    ( 5, r"[bcdfghjklmnpqrsštvwxzž]$"),  # -C except those in decl. 6, 32-34, 38-41, 49 (many exc.)
)

# rules for trisyllabic nouns (declension, regex)
_RULES_3SYLL = (
    # === -VV ===

    ( 3, r"[aäei][oö]$"),   # -AO/-eO/-iO
    (12, r"[iuy][aä]$"),    # -iA/-UA
    (15, r"e[aä]$"),        # -eA
    (18, r"[aeiouyäö]i$"),  # -Vi
    (20, r"ee$"),           # -ee
    (48, r"[uy]e$"),        # -Ue

    # === -CA ===

    # -dA/-nkA/-ssA/-ntA/-VVttA
    ( 9, r"( d | nk | ss | nt | (ee|ii|uu)tt )[aä]$"),
    # -AjA/-OjA/-UjA/-elä/-mA/-oona/-ouna/-ärä/-erA/-isA/-vA
    (10, r"( [aäoöuy]j[aä] | elä | m[aä] | o[ou]na | ärä | er[aä] | is[aä] | v[aä] )$"),
    # -ona except those in declension 10
    (11, r"ona$"),
    # -kkA/-ttA except those in declension 9
    (14, r"(kk|tt)[aä]$"),
    # some of -gA/-kA/-lA/-nA/-rA/-sA/-tA except those in declension 14
    (13, r"( [gkt] | ll | (ee|ii|[lu]u|[ag]i)n | uur | ts )[aä]$"),
    # -jA/-lA/-nA/-rA except those in declensions 10, 11, 13
    (12, r"[jlnr][aä]$"),

    # === -Ce ===

    (8, r"tte$"),                         # -tte
    (49, r"( pel | en | er )e$"),         # -pele/-ene/-ere
    (48, r"[bcdfghjklmnpqrsštvwxzž]e$"),  # -Ce except those in declension 49

    # === -Ci ===

    (6, r"( [aäeiou]l | [au]m | [aäei]n | [aäeiouy]r )i$"),  # some of -Vli/-Vmi/-Vni/-Vri
    (16, r"[eo]mpi$"),                                       # -empi/-ompi
    (5, r"[bcdfghjklmnpqrsštvwxzž]i$"),                      # -Ci except those in decl. 6, 16

    # === -CO/-CU ===

    (1, r"( (nk|nt|tt)[oö] | aisto | t[uy] )$"),  # -nkO/-ntO/-aisto/-ttO/-tU
    (4, r"kk[oö]$"),                              # -kkO
    (2, r"[bcdfghjklmnpqrsštvwxzž][oöuy]$"),      # -CO/-CU except those in declensions 1, 4

    # === -C ===

    (32, r"t[aä]r$"),                    # -tAr
    (33, r"in$"),                        # -in
    (34, r"t[oö]n$"),                    # -tOn
    (38, r"nen$"),                       # -nen
    (40, r"[ioöuy][uy]s$"),              # -iUs/-OUs/-UUs
    (39, r"[eioöuy]s$"),                 # -es/-is/-Os/-Us except those in decl. 40
    (41, r"[aä]s$"),                     # -As
    (47, r"[ln][uy]t$"),                 # -lUt/-nUt
    ( 5, r"[bcdfghjklmnpqrsštvwxzž]$"),  # -C except those in decl. 32-34, 38-41, 47
)

# rules for quadrisyllabic and longer nouns (declension, regex)
_RULES_4SYLL = (
    # === -VV ===

    ( 3, r"[bcdfghjklmnpqrsštvwxzž]i[oö]$"),  # -CiO
    (12, r"[bcdfghjklmnpqrsštvwxzž][ei]a$"),  # -Cea/-Cia

    # === -CA ===

    # -akka/-ikka/-rkka/-lla/-iina/-inna/-ssa/-tA/-ža
    ( 9, r"( [air]kka | lla | i[in]na | ssa | t[aä] | ža )$"),
    # -lijA/-nijA/-sijA/-tijA/-la
    (12, r"( [lnst]ij[aä] | la )$"),
    # -CA except those in declensions 9, 12
    (10, r"[bcdfghjklmnpqrsštvwxzž][aä]$"),

    # === -Ci ===

    # some of -Vli, -Vmi, -Vri
    (6, r"( [gkp]el | [drt]um | [klnptv]ar | [dgknt]er | (i|l|s|kt|st|tt)or )i$"),
    # -Ci except those in declension 6
    (5, r"[bcdfghjklmnpqrsštvwxzž]i$"),

    # === -CO/-CU ===

    (2, r"( m[oö] | l[uy] )$"),               # -mO/-lU
    (4, r"[dgjlmnprstv]ikk[oö]$"),            # -CikkO (not -kikko)
    (1, r"[bcdfghjklmnpqrsštvwxzž][oöuy]$"),  # -CO/-CU excluding those in decl. 2, 4

    # === -C ===

    (32, r"t[aä]r$"),                   # -tAr
    (34, r"t[oö]n$"),                   # -tOn
    (38, r"nen(kin)?$"),                # -nen(kin)
    (40, r"[iuy][uy]s$"),               # -iUs/-UUs
    (39, r"[eioöuy]s$"),                # -es/-is/-Os/-Us except those in decl. 40
    (41, r"[aä]s$"),                    # -As
    (47, r"n[uy]t$"),                   # -nUt
    (5, r"[bcdfghjklmnpqrsštvwxzž]$"),  # -C except those in decl. 32, 34, 38-41, 47
)

def get_declensions(noun, useExceptions=True):
    """noun: a Finnish noun in nominative singular
    return: a set of 0-2 Kotus declensions (each 1-49)"""

    noun = noun.strip("'- ")

    try:
        return _MULTI_DECLENSION_NOUNS[noun]
    except KeyError:
        pass

    if useExceptions:
        try:
            return {_EXCEPTIONS[noun]}
        except KeyError:
            pass

    rules = [_RULES_1SYLL, _RULES_2SYLL, _RULES_3SYLL, _RULES_4SYLL][
        countsyll.count_syllables(noun)-1
    ]

    for (declension, regex) in rules:
        if re.search(regex, noun, re.VERBOSE) is not None:
            return {declension}

    return set()

def _check_redundant_exceptions():
    for noun in _EXCEPTIONS:
        detectedDeclensions = get_declensions(noun, False)
        if detectedDeclensions and _EXCEPTIONS[noun] == list(detectedDeclensions)[0]:
            print(f'Redundant exception: "{noun}"')

def main():
    _check_redundant_exceptions()

    if len(sys.argv) != 2:
        sys.exit(
            "Argument: a Finnish noun (including adjectives/pronouns/numerals, excluding "
            "compounds) in nominative singular. Print the Kotus declension(s) (1-49)."
        )
    noun = sys.argv[1]

    declensions = get_declensions(noun)
    if not declensions:
        sys.exit("Unrecognized noun.")

    for d in sorted(declensions):
        print(f'Declension {d} (like "{DECLENSION_DESCRIPTIONS[d]}")')

if __name__ == "__main__":
    main()
