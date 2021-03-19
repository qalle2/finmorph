"""Get the Kotus declension of a Finnish noun.
Note: A = a/ä, O = o/ö, U = u/y, V = any vowel, C = any consonant"""

import re
import sys

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
    8:  "nalle, -n, -jen, -a, -ja, -en, -eihin",
    9:  "kal|a, -an, -ojen, -aa, -oja, -aan, -oihin",
    10: "koir|a, -an, -ien, -aa, -ia, -aan, -iin",
    11: "omen|a, -an, -ien/-oiden/-ojen, -aa, -ia/-oita/-oja, -aan, -iin/-oihin",
    12: "kulkij|a, -an, -oiden, -aa, -oita, -aan, -oihin",
    13: "katisk|a, -an, -oiden/-ojen, -aa, -oita/-oja, -aan, -oihin",
    14: "solak|ka, -an, -oiden/-kojen, -kaa, -oita/-koja, -kaan, -(k)oihin",
    15: "korke|a, -an, -iden, -a(t)a, -ita, -aan, -isiin/-ihin",
    16: "vanhem|pi, -man, -pien, -paa, -pia, -paan, -piin",
    17: "vapa|a, -an, -iden, -ata, -ita, -aseen, -iseen/-ihin",
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
    40: "kalleu|s, -den, -ksien, -tta, -ksia, -teen, ksiin",
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
MULTI_DECLENSION_NOUNS = {
    "menu": {1, 21},

    "caddie": {3, 8},

    "alpi": {5, 7},
    "helpi": {5, 7},
    "kaihi": {5, 7},
    "karhi": {5, 7},
    "kymi": {5, 7},
    "lahti": {5, 7},
    "laki": {5, 7},
    "palvi": {5, 7},
    "ripsi": {5, 7},
    "sini": {5, 7},
    "vyyhti": {5, 7},

    "sioux": {5, 22},

    "syli": {5, 23},

    "kuori": {5, 26},
    "viini": {5, 26},
    "vuori": {5, 26},

    "peitsi": {5, 30},

    "csárdás": {5, 39},
    "kuskus":  {5, 39},

    "ori": {5, 48},

    "kolme": {7, 8},

    "hapsi": {7, 29},
    "uksi":  {7, 29},

    "siitake": {8, 48},

    "aneurysma": {9, 10},
    "kysta": {9, 10},
    "lyyra": {9, 10},
    "puola": {9, 10},

    "humala": {10, 11},

    "kikkara": {11, 12},

    "tanhua": {12, 15},

    "kuusi": {24, 27},

    "ahtaus": {39, 40,},
    "karvaus": {39, 40,},
    "merirosvous": {39, 40},
    "rosvous": {39, 40},
    "siivous":  {39, 40},
    "vakaus":  {39, 40},

    "havas":  {39, 41},
    "kallas": {39, 41},
    "koiras": {39, 41},
    "olas": {39, 41},
    "pallas": {39, 41},
    "uros": {39, 41},

    "kymmenes": {39, 45},
}

# exceptions to rules (key = noun, value = declension)
EXCEPTIONS = {
    # === Unique combinations of *two-letter* ending and declension ===

    # For example, "nugaa" is the only word that both ends with -aa and is in declension 20.
    # a/ä, o/ö, u/y, uppercase/lowercase distinguished. Order: ending backwards, declension.

    "nugaa": 20,
    "reseda": 13,
    "cha-cha-cha": 21,
    "media": 13,
    "paranoia": 10,
    "judoka": 11,
    "salama": 12,
    "ainoa": 15,
    "ulappa": 14,
    "mimoosa": 11,
    "hänenlaisensa": 38,
    "maya": 9,
    "pizza": 9,

    "kebab": 5,

    "armagnac": 5,

    "skinhead": 5,
    "LED": 5,
    "apartheid": 5,
    "talmud": 5,

    "reggae": 21,
    "bébé": 21,
    "tax-free": 21,
    "tie": 19,
    "koe": 48,
    "coupé": 21,
    "moiré": 21,
    "rosé": 21,
    "fondue": 21,
    "säe": 48,

    "golf": 5,

    "ajatollah": 5,
    "squash": 5,

    "ruuhi": 24,
    "LYHKI": 5,
    "veli": 7,
    "uni": 24,
    "moni": 23,
    "minunlaiseni": 38,
    "jousi": 26,
    "lapsi": 29,
    "sinunlaisesi": 38,
    "paaši": 5,
    "tienesti": 6,
    "ratatui": 18,
    "oliivi": 6,
    "kiwi": 5,
    "paparazzi": 5,
    "täi": 18,

    "telemark": 5,
    "tomahawk": 5,

    "rial": 6,
    "diesel": 6,
    "cocktail": 5,
    "soul": 5,

    "edam": 6,
    "tandem": 6,
    "requiem": 5,
    "simsalabim": 5,
    "napalm": 5,
    "CD-ROM": 5,
    "liirumlaarum": 6,
    "ångström": 6,

    "donjuan": 6,
    "kahdeksan": 10,
    "kumpikaan": 16,
    "kumpainenkaan": 38,
    "vasen": 37,
    "design": 5,
    "lämmin": 35,
    "kumpikin": 16,
    "laidun": 33,
    "sydän": 33,

    "plasebo": 2,
    "go-go": 18,
    "navaho": 2,
    "navajo": 2,
    "duo": 1,
    "angervo": 2,
    "embryo": 3,

    "quickstep": 5,
    "gallup": 6,

    "AIDS": 5,
    "mies": 42,
    "jiddiš": 5,
    "calvados": 5,
    "tournedos": 22,
    "chips": 5,
    "slivovits": 5,
    "borštš": 5,
    "vantus": 41,
    "couscous": 5,

    "tuhat": 46,
    "nougat": 22,
    "oltavat": 10,
    "aktiivat": 13,
    "molemmat": 16,
    "rintsikat": 14,
    "bileet": 20,
    "liittoutuneet": 47,
    "copyright": 5,
    "parfait": 22,
    "tarot": 5,
    "kapiot": 3,
    "pippalot": 2,
    "talkoot": 17,
    "illatsut": 2,
    "port salut": 22,
    "passepartout": 22,
    "ragoût": 22,
    "rynttyyt": 41,
    "hynttyyt": 17,
    "häät": 18,

    "tau": 18,
    "ecu": 1,
    "kakadu": 2,
    "tofu": 1,
    "kung-fu": 21,
    "spurgu": 1,
    "tiu": 18,
    "kikuju": 2,
    "clou": 21,
    "kiiru": 48,
    "kenguru": 2,
    "raguu": 20,

    "stroganov": 5,
    "bungalow": 5,

    "thorax": 5,
    "lux": 5,
    "bordeaux": 22,

    "jazz": 5,

    "iskä": 9,
    "käpälä": 11,
    "siivilä": 13,
    "kärhämä": 11,
    "päällystä": 13,

    "dödö": 1,
    "kylvö": 1,
    "miljöö": 20,

    # === Other: -A ===

    # -aa
    "ei-kenenkään-maa": 18,
    "huuhaa": 18,
    "peeaa": 18,

    # -da
    "sekunda": 9,
    #
    "pomada": 10,

    # -ea
    "aramea": 12,
    "bougainvillea": 12,
    "idea": 12,
    "komitea": 12,
    "kommunikea": 12,
    "matinea": 12,
    "pallea": 12,
    "urea": 12,
    #
    "atsalea": 13,
    "attasea": 13,
    "orkidea": 13,

    # -fa
    "lymfa": 9,

    # -ga
    "kollega": 13,
    "malaga": 13,
    "oomega": 13,

    # -ia
    "dia": 9,
    "odysseia": 9,

    # -aja
    "laaja": 9,
    "maja": 9,
    "paja": 9,
    "raaja": 9,
    "taaja": 9,
    "vaja": 9,
    #
    "nauraja": 10,
    #
    "apaja": 11,

    # -ija
    "akileija": 9,
    "dreija": 9,
    "faija": 9,
    "keija": 9,
    "leija": 9,
    "maija": 9,
    "papukaija": 9,
    "sija": 9,
    "tyyssija": 9,
    #
    "leukoija": 11,
    #
    "papaija": 13,

    # -lja
    #
    "kanalja": 12,
    "persilja": 12,
    #
    "mantilja": 13,
    "vanilja": 13,

    # -kka
    "hiuslakka": 9,
    "nautiikka": 9,
    "yövilkka": 9,
    #
    "maankolkka": 10,
    #
    "estetiikka": 14,  # really? "estetiikoiden" sounds wrong
    "jalkapatikka": 14,
    "korvatillikka": 14,
    "poliklinikka": 14,
    "psykometriikka": 14,

    # -ka (not -kka)
    "seljanka": 9,
    #
    "ekliptika": 12,
    "paprika": 12,
    #
    "karakteristika": 13,
    "majolika": 13,
    "psykofarmaka": 13,
    "skandinaaviska": 13,

    # -AlA
    "hankala": 10,
    #
    "kanala": 12,
    "manala": 12,
    "räkälä": 12,
    #
    "sairaala": 13,
    "sikala": 13,

    # -elA
    "hopeahela": 9,
    #
    "hintelä": 10,
    "nokkela": 10,
    "ovela": 10,
    "sukkela": 10,
    "vikkelä": 10,
    "äitelä": 10,
    #
    "kampela": 13,

    # -ila
    "apila": 13,
    "manila": 13,
    "takila": 13,

    # -ola
    "suola": 9,
    #
    "gorgonzola": 10,
    "hyperbola": 10,
    "karambola": 10,
    #
    "viola": 13,

    # -llA
    "papilla": 9,
    "sinsilla": 9,
    "tonsilla": 9,
    #
    "paella": 13,

    # -mA
    "auma": 9,
    "dalai-lama": 9,
    "kama": 9,
    "lama": 9,
    "lauma": 9,
    "reuma": 9,
    "sama": 9,
    "sauma": 9,
    "sialma": 9,
    "talouslama": 9,
    "trauma": 9,
    #
    "siunaama": 10,
    "suuntima": 10,
    "virtaama": 10,
    #
    "hekuma": 11,
    "mahatma": 11,
    "paatsama": 11,
    "probleema": 11,
    "ödeema": 11,
    #
    "karisma": 13,
    "maailma": 13,
    "suurima": 13,

    # -nA
    "ballerina": 9,
    "ikebana": 9,
    "lapsenkina": 9,
    "medisiina": 9,
    "okariina": 9,
    #
    "ihana": 10,
    "kruuna": 10,
    "kränä": 10,
    "yliminä": 10,
    #
    "jellona": 11,
    "korona": 11,
    "lattana": 11,
    "lättänä": 11,
    "mammona": 11,
    "marihuana": 11,
    "maruna": 11,
    "murena": 11,
    "ohrana": 11,
    "omena": 11,
    "orpana": 11,
    "papana": 11,
    "pipana": 11,
    "poppana": 11,
    "sikuna": 11,
    "täkänä": 11,
    #
    "harppuuna": 12,
    #
    "aivina": 13,
    "aluna": 13,
    "arina": 13,
    "ipana": 13,
    "kahina": 13,
    "kohina": 13,
    "kopina": 13,
    "kuhina": 13,
    "kärinä": 13,
    "marina": 13,
    "maukuna": 13,
    "määkinä": 13,
    "mölinä": 13,
    "mörinä": 13,
    "möyrinä": 13,
    "paukkina": 13,
    "perenna": 13,
    "piekana": 13,
    "porina": 13,
    "rahina": 13,
    "ramina": 13,
    "reppana": 13,
    "retsina": 13,
    "ruutana": 13,
    "smetana": 13,
    "taverna": 13,
    "tuoksina": 13,
    "ukraina": 13,
    "vagina": 13,

    # -pA
    "kauppa": 9,
    #
    "aikaansaapa": 10,

    # -rA
    "ahkera": 10,
    "ankara": 10,
    "avara": 10,
    "eripura": 10,
    "katkera": 10,
    "koira": 10,
    "kovera": 10,
    "kumara": 10,
    "kupera": 10,
    "uuttera": 10,
    #
    "algebra": 11,
    "äpärä": 11,
    "hapera": 11,
    "hatara": 11,
    "hattara": 11,
    "hutera": 11,
    "itara": 11,
    "käkkärä": 11,
    "kihara": 11,
    "kiverä": 11,
    "mäkärä": 11,
    "sikkara": 11,
    "säkkärä": 11,
    "tomera": 11,
    "vanttera": 11,
    "veiterä": 11,
    #
    "angora": 12,
    "jäkkärä": 12,
    "kamera": 12,
    "kolera": 12,
    "littera": 12,
    "ooppera": 12,
    "väkkärä": 12,
    #
    "gerbera": 13,
    "hetaira": 13,
    "ketara": 13,
    "kitara": 13,
    "madeira": 13,
    "matara": 13,
    "sikkura": 13,
    "tempera": 13,
    "vaahtera": 13,

    # -sA
    "mykorritsa": 9,
    #
    "meduusa": 13,
    "vernissa": 13,

    # -tA
    "aortta": 9,
    "kajuutta": 9,
    "krypta": 9,
    "valuutta": 9,
    "ympärystä": 9,
    #
    "emäntä": 10,
    "halveksunta": 10,
    "huuhdonta": 10,
    "hyväksyntä": 10,
    "isäntä": 10,
    "lyhyenläntä": 10,
    "noita": 10,
    "suunta": 10,
    "väheksyntä": 10,
    "vähäläntä": 10,
    "vähänläntä": 10,
    #
    "lolita": 13,
    "peseta": 13,
    "sofista": 13,
    #
    "navetta": 14,
    "ometta": 14,
    "pohatta": 14,
    "savotta": 14,

    # -vA
    "aava": 9,
    "eeva": 9,
    "guava": 9,
    "iva": 9,
    "kaava": 9,
    "kiva": 9,
    "klaava": 9,
    "laava": 9,
    "lava": 9,
    "naava": 9,
    "neva": 9,
    "niva": 9,
    "pehva": 9,
    "terva": 9,
    #
    "murhaava": 10,
    #
    "ahava": 11,
    "harava": 11,

    # === Other: -e ===

    # -de
    "cum laude": 8,
    "jade": 8,
    "lande": 8,
    "tilde": 8,

    # -ee
    "frisbee": 18,
    "kanapee": 18,
    "pee": 18,
    "puusee": 18,
    "tee": 18,

    # -he
    "crème fraîche": 8,
    "quiche": 8,

    # -ie
    "collie": 3,
    "lassie": 3,
    "zombie": 3,
    #
    "brasserie": 21,
    "brie": 21,

    # -ke
    "karaoke": 8,
    "ladylike": 8,
    "milk shake": 8,
    "nukke": 8,
    "psyyke": 8,
    "sake": 8,

    # -le
    "ale": 8,
    "beagle": 8,
    "chenille": 8,
    "chippendale": 8,
    "ensemble": 8,
    "faksimile": 8,
    "freestyle": 8,
    "ginger ale": 8,
    "joule": 8,
    "kalle": 8,
    "kellokalle": 8,
    "mobile": 8,
    "nalle": 8,
    "pelle": 8,
    "polle": 8,
    "promille": 8,
    "puzzle": 8,
    "quenelle": 8,
    "ratatouille": 8,
    "single": 8,
    "tabbule": 8,
    "tagliatelle": 8,
    "tele": 8,
    "ukulele": 8,
    "vaudeville": 8,
    #
    "askele": 49,
    "kantele": 49,
    "kyynele": 49,
    "ompele": 49,
    "petkele": 49,
    "taipale": 49,
    "seppele": 49,
    "vempele": 49,

    # -me
    "lime": 8,
    "madame": 8,
    "ragtime": 8,
    "saame": 8,

    # -ne
    "akne": 8,
    "beguine": 8,
    "deadline": 8,
    "komedienne": 8,
    "manne": 8,
    "minestrone": 8,
    "penne": 8,
    "tragedienne": 8,
    #
    "hepene": 49,
    "murene": 49,
    "säkene": 49,

    # -oe
    "aaloe": 3,
    "oboe": 3,

    # -pe
    "crêpe": 8,
    "grape": 8,
    "jeppe": 8,
    "ope": 8,
    "toope": 8,

    # -re
    "empire": 8,
    "folklore": 8,
    "force majeure": 8,
    "genre": 8,
    "gruyère": 8,
    "hardware": 8,
    "kurare": 8,
    "kurre": 8,
    "poplore": 8,
    "software": 8,
    #
    "jäntere": 48,
    "tere": 48,
    #
    "askare": 49,
    "huhmare": 49,
    "pientare": 49,
    "saivare": 49,
    "utare": 49,

    # -se
    "bavaroise": 8,
    "bouillabaisse": 8,
    "charlotte russe": 8,
    "duchesse": 8,
    "house": 8,
    "itse": 8,
    "mousse": 8,
    "nasse": 8,
    "nisse": 8,
    "open house": 8,
    "pose": 8,
    "striptease": 8,

    # -te
    "à la carte": 8,
    "andante": 8,
    "bourette": 8,
    "byte": 8,
    "entrecôte": 8,
    "forte": 8,
    "karate": 8,
    "mezzoforte": 8,
    "poste restante": 8,
    "raclette": 8,
    "ringette": 8,
    "vinaigrette": 8,

    # -ue
    "boutique": 8,
    "petanque": 8,

    # -ve
    "agaave": 8,
    "jive": 8,
    "mangrove": 8,

    # === Other: -i ===

    # -di
    "biljardi": 6,
    "standardi": 6,

    # -ki
    "sutki": 5,
    #
    "buzuki": 6,
    "kinuski": 6,
    "saluki": 6,
    "sirtaki": 6,
    "tsinuski": 6,
    #
    "hanki": 7,
    "hauki": 7,
    "henki": 7,
    "hiki": 7,
    "joki": 7,
    "kaikki": 7,
    "kallionlaki": 7,
    "kanki": 7,
    "kaski": 7,
    "kiiski": 7,
    "kitalaki": 7,
    "koski": 7,
    "leski": 7,
    "noki": 7,
    "onki": 7,
    "päälaki": 7,
    "piki": 7,
    "poski": 7,
    "reki": 7,
    "sääski": 7,
    "sänki": 7,
    "suulaki": 7,
    "taivaanlaki": 7,
    "tuki": 7,
    "tunturinlaki": 7,
    "vaaranlaki": 7,
    "vaski": 7,

    # -li
    "amiraali": 5,
    "desibeli": 5,
    "follikkeli": 5,
    "hanttapuli": 5,
    "hyperbeli": 5,
    "ihomaali": 5,
    "kajaali": 5,
    "kapituli": 5,
    "koraali": 5,
    "laventeli": 5,
    "lojaali": 5,
    "modaali": 5,
    "moguli": 5,
    "multippeli": 5,
    "paraabeli": 5,
    "pedaali": 5,
    "pendeli": 5,
    "permeaabeli": 5,
    "pilipali": 5,
    "pluraali": 5,
    "portugali": 5,
    "riskaabeli": 5,
    "taranteli": 5,
    "tuoli": 5,
    "urinaali": 5,
    #
    "aioli": 6,
    "atolli": 6,
    "basilli": 6,
    "brokkoli": 6,
    "daktyyli": 6,
    "debiili": 6,
    "flanelli": 6,
    "fossiili": 6,
    "fraktaali": 6,
    "gaselli": 6,
    "gondoli": 6,
    "hotelli": 6,
    "idoli": 6,
    "konsoli": 6,
    "kupoli": 6,
    "linoli": 6,
    "manttaali": 6,
    "moduuli": 6,
    "motelli": 6,
    "neutraali": 6,
    "paneeli": 6,
    "petroli": 6,
    "pistooli": 6,
    "putelli": 6,
    "sardelli": 6,
    "seniili": 6,
    "siviili": 6,
    "skandaali": 6,
    "stabiili": 6,
    "steriili": 6,
    "symboli": 6,
    "tekstiili": 6,
    "tivoli": 6,
    "trioli": 6,
    "trotyyli": 6,
    "vaskooli": 6,
    "venkoli": 6,
    "venttiili": 6,
    "vinyyli": 6,
    #
    "tiili": 23,
    "tuli": 23,
    #
    "hiili": 24,
    "huuli": 24,
    #
    "tuuli": 26,

    # -mi
    "monstrumi": 5,
    "opossumi": 5,
    "palsami": 5,
    "praktikumi": 5,
    "puomi": 5,
    "tupajumi": 5,
    "vigvami": 5,
    #
    "albumi": 6,
    "atomi": 6,
    "bitumi": 6,
    "entsyymi": 6,
    "foneemi": 6,
    "keraami": 6,
    "kondomi": 6,
    "muslimi": 6,
    "pogromi": 6,
    "postuumi": 6,
    "syklaami": 6,
    "systeemi": 6,
    "toteemi": 6,
    "vakuumi": 6,
    "volyymi": 6,
    #
    "helmi": 7,
    "korkkitammi": 7,
    "nimi": 7,
    "nummi": 7,
    "nurmi": 7,
    "salmi": 7,
    "seimi": 7,
    "sormi": 7,
    "suomi": 7,
    "tammi": 7,
    #
    "lumi": 25,
    "taimi": 25,

    # -ni
    "afgaani": 5,
    "alumiini": 5,
    "amoriini": 5,
    "aniliini": 5,
    "butaani": 5,
    "etyleeni": 5,
    "fibriini": 5,
    "gluteeni": 5,
    "humaani": 5,
    "igumeeni": 5,
    "jasmiini": 5,
    "joriini": 5,
    "kaimaani": 5,
    "kaoliini": 5,
    "karbiini": 5,
    "kardaani": 5,
    "kiniini": 5,
    "Koraani": 5,
    "kosini": 5,
    "lantaani": 5,
    "laviini": 5,
    "ligniini": 5,
    "mangaani": 5,
    "metaani": 5,
    "migreeni": 5,
    "morfiini": 5,
    "oktaani": 5,
    "orgaani": 5,
    "patiini": 5,
    "pepsiini": 5,
    "pineeni": 5,
    "porfiini": 5,
    "profaani": 5,
    "propaani": 5,
    "rabbiini": 5,
    "retliini": 5,
    "risiini": 5,
    "rutiini": 5,
    "samaani": 5,
    "šamaani": 5,
    "sampaani": 5,
    "seireeni": 5,
    "tanniini": 5,
    "toksiini": 5,
    #
    "antenni": 6,
    "azerbaidžani": 6,
    "betoni": 6,
    "biisoni": 6,
    "blondiini": 6,
    "bosoni": 6,
    "brahmaani": 6,
    "diakoni": 6,
    "fotoni": 6,
    "gibboni": 6,
    "hälytyssireeni": 6,
    "ikoni": 6,
    "kanjoni": 6,
    "kantoni": 6,
    "kanttiini": 6,
    "kardoni": 6,
    "kommuuni": 6,
    "korsteeni": 6,
    "koturni": 6,
    "kumppani": 6,
    "kvitteni": 6,
    "leptoni": 6,
    "meloni": 6,
    "monsuuni": 6,
    "muffini": 6,
    "palosireeni": 6,
    "pekoni": 6,
    "pelmeni": 6,
    "piisoni": 6,
    "pingviini": 6,
    "ponttoni": 6,
    "prostaglandiini": 6,
    "romani": 6,
    "sabloni": 6,
    "sirkoni": 6,
    "spontaani": 6,
    "sulttaani": 6,
    "sumusireeni": 6,
    "taifuuni": 6,
    "testosteroni": 6,
    "teutoni": 6,
    "tribuuni": 6,
    "tšetšeeni": 6,
    "tulppaani": 6,
    "turkmeeni": 6,
    "ubikinoni": 6,
    "unioni": 6,
    "uraani": 6,
    "valloni": 6,
    "zirkoni": 6,
    "zucchini": 6,
    #
    "onni": 7,
    "saarni": 7,
    #
    "niini": 26,
    "tyyni": 26,
    "ääni": 26,

    # -pi
    "appi": 7,
    "happi": 7,
    "lempi": 7,
    "rupi": 7,
    "sappi": 7,
    "soppi": 7,
    "tuppi": 7,
    "typpi": 7,
    #
    "kumpi": 16,

    # -ri
    "editori": 5,
    "fingerpori": 5,
    "fosfori": 5,
    "irtovuori": 5,
    "isobaari": 5,
    "kaliiberi": 5,
    "kaliiperi": 5,
    "kateederi": 5,
    "kefiiri": 5,
    "kollektori": 5,
    "kompostori": 5,
    "kvasaari": 5,
    "likvori": 5,
    "lämpövuori": 5,
    "makaaberi": 5,
    "manööveri": 5,
    "monitori": 5,
    "okulaari": 5,
    "paapuuri": 5,
    "palaveri": 5,
    "pioneeri": 5,
    "plari": 5,
    "primaari": 5,
    "psori": 5,
    "pulloveri": 5,
    "raparperi": 5,
    "rastafari": 5,
    "reseptori": 5,
    "reviiri": 5,
    "semafori": 5,
    "silkkivuori": 5,
    "sinooberi": 5,
    "sinooperi": 5,
    "slipoveri": 5,
    "tikkivuori": 5,
    "varistori": 5,
    "vingerpori": 5,
    "vulgaari": 5,
    "välivuori": 5,
    "yöbaari": 5,
    #
    "akupunktuuri": 6,
    "asuuri": 6,
    "bisarri": 6,
    "diaari": 6,
    "emiiri": 6,
    "frisyyri": 6,
    "jepari": 6,
    "juniori": 6,
    "kentauri": 6,
    "keulavisiiri": 6,
    "kivääri": 6,
    "kondori": 6,
    "kortteeri": 6,
    "kulttuuri": 6,
    "kupari": 6,
    "likööri": 6,
    "marttyyri": 6,
    "misääri": 6,
    "monttööri": 6,
    "pankkiiri": 6,
    "pillipiipari": 6,
    "pipari": 6,
    "ripari": 6,
    "seniori": 6,
    "standaari": 6,
    "struktuuri": 6,
    "suurvisiiri": 6,
    "sähköpunktuuri": 6,
    "tekstuuri": 6,
    "turnyyri": 6,
    "valööri": 6,
    "vampyyri": 6,
    "vapari": 6,
    #
    "hiiri": 24,
    "meri": 24,
    #
    "aitovieri": 26,
    "kaari": 26,
    "saari": 26,
    "suuri": 26,
    "sääri": 26,
    "teeri": 26,
    "veri": 26,
    "vieri": 26,
    "ääri": 26,

    # -si
    "desi": 5,
    "kreisi": 5,
    "kuosi": 5,
    "mansi": 5,
    "ysi": 5,
    #
    "glukoosi": 6,
    "hampuusi": 6,
    "karpaasi": 6,
    "kolhoosi": 6,
    "narkoosi": 6,
    "neuroosi": 6,
    "pakaasi": 6,
    "plantaasi": 6,
    "poliisi": 6,
    "proteesi": 6,
    "refleksi": 6,
    "serviisi": 6,
    "sotiisi": 6,
    "sottiisi": 6,
    "sovhoosi": 6,
    "sypressi": 6,
    "trapetsi": 6,
    "turkoosi": 6,
    "ukaasi": 6,
    "viskoosi": 6,
    "zoonoosi": 6,
    "äksiisi": 6,
    #
    "sääksi": 7,
    "silmäripsi": 7,
    "suksi": 7,
    "viiksi": 7,
    "vuoksi": 7,
    #
    "kusi": 24,
    #
    "hiisi": 27,
    "hopeakuusi": 27,
    "käsi": 27,
    "niisi": 27,
    "paasi": 27,
    "uusi": 27,
    "viisi": 27,
    #
    "veitsi": 30,
    #
    "haaksi": 31,
    "kaksi": 31,
    "yksi": 31,

    # -ti
    "haahti": 7,
    "lehti": 7,
    "lintulahti": 7,
    "merenlahti": 7,
    "tähti": 7,

    # -vi
    "hirvi": 7,
    "järvi": 7,
    "kivi": 7,
    "lovi": 7,
    "ovi": 7,
    "pälvi": 7,
    "pilvi": 7,
    "polvi": 7,
    "povi": 7,
    "sarvi": 7,
    "savi": 7,
    "suvi": 7,
    "talvi": 7,
    "torvi": 7,
    "tyvi": 7,

    # === Other: -O ===

    # -do
    "aikido": 2,
    "tornado": 2,
    "torpedo": 2,

    # -go
    "hidalgo": 2,
    "imago": 2,
    "indigo": 2,
    "origo": 2,

    # -io
    "adagio": 1,
    "trio": 1,

    # -kkO
    "baarimikko": 1,
    "haaksirikko": 1,
    "juhannuskokko": 1,
    "keliaakikko": 1,
    "koneikko": 1,
    "kumpareikko": 1,
    "laiskajaakko": 1,
    "miljoonikko": 1,
    "pantomiimikko": 1,
    "papurikko": 1,
    "paranooikko": 1,
    "pateetikko": 1,
    "petäjikkö": 1,
    "poleemikko": 1,
    "poliitikko": 1,
    "pragmaatikko": 1,
    "praktikko": 1,
    "romantikko": 1,
    "saraikko": 1,
    "sarvijaakko": 1,
    "semiootikko": 1,
    "untuvikko": 1,
    "uskalikko": 1,

    # -lO
    "alakulo": 1,
    "auringonkilo": 1,
    "neljänneskilo": 1,
    "painokilo": 1,
    "sigarillo": 1,
    "staalo": 1,
    "varttikilo": 1,

    # -mo
    "karkaisimo": 1,
    "koksittamo": 1,
    "lainaamo": 1,
    "maammo": 1,
    #
    "asemo": 2,
    "hiomo": 2,
    "ohimo": 2,

    # -nO
    "andantino": 1,
    "cappuccino": 1,
    #
    "kartano": 2,
    "keltano": 2,
    "kimono": 2,
    "sopraano": 2,

    # -OO
    "jöö": 18,
    "köö": 18,
    "rokokoo": 18,
    "tenkkapoo": 18,
    #
    "politbyroo": 20,
    "sampoo": 20,
    "trikoo": 20,
    "voodoo": 20,

    # -ro
    "allegro": 1,
    "autogiro": 1,
    "bistro": 1,
    "korohoro": 1,
    "sombrero": 1,

    # -sO
    "calypso": 2,
    "espresso": 2,
    "pajatso": 2,
    "parnasso": 2,

    # -stO
    "astiasto": 1,
    "elimistö": 1,
    "eliöstö": 1,
    "hyllystö": 1,
    "kalusto": 1,
    "kojeisto": 1,
    "kuidusto": 1,
    "käyrästö": 1,
    "lajisto": 1,
    "lasisto": 1,
    "lehdistö": 1,
    "lepistö": 1,
    "lähistö": 1,
    "merkistö": 1,
    "munkisto": 1,
    "naisisto": 1,
    "oikeisto": 1,
    "pillistö": 1,
    "ruovisto": 1,
    "ruususto": 1,
    "testistö": 1,
    "tyypistö": 1,
    "virasto": 1,
    "väylästö": 1,
    "ylimystö": 1,
    "älymystö": 1,
    #
    "aarteisto": 2,
    "huoneisto": 2,
    "jaosto": 2,
    "kaislisto": 2,
    "katajisto": 2,
    "kiinteistö": 2,
    "koordinaatisto": 2,
    "päällystö": 2,
    "suonikalvosto": 2,
    "säännöstö": 2,
    "tarpeisto": 2,
    "valtuusto": 2,
    "väestö": 2,

    # -VtO
    "legato": 2,
    "spiccato": 2,
    "transito": 2,

    # === Other: -U ===

    # -lU
    "elostelu": 1,
    "istuskelu": 1,
    "kyhäily": 1,
    #
    "ajelu": 2,
    "utelu": 2,

    # -sU
    "huitaisu": 1,
    "pliisu": 1,

    # -uu
    "gnuu": 18,
    "homssantuu": 18,
    "munaskuu": 18,
    "pelakuu": 18,

    # === Other: -C ===

    # -al
    "emmental": 5,
    "kajal": 5,
    "pascal": 5,
    "sial": 5,
    "sisal": 5,
    "trial": 5,
    #
    "sammal": 49,
    "taival": 49,

    # -el
    "becquerel": 5,
    "gospel": 5,
    "kennel": 5,
    "mosel": 5,
    #
    "nivel": 32,
    "sävel": 32,

    # -An
    "seitsemän": 10,
    "yhdeksän": 10,
    #
    "hapan": 33,
    "morsian": 33,

    # -en
    "eeden": 5,
    "evergreen": 5,
    "hymen": 5,
    "loden": 5,
    "non-woven": 5,
    "röntgen": 5,
    "zen": 5,
    #
    "lumen": 6,
    "luumen": 6,
    "stilleben": 6,
    #
    "kymmenen": 32,
    #
    "muren": 49,
    "säen": 49,

    # -in
    "drive-in": 5,
    "kelvin": 5,
    "pinyin": 5,
    #
    "alin": 36,
    "enin": 36,
    "likin": 36,
    "lähin": 36,
    "parahin": 36,
    "parhain": 36,
    "sisin": 36,
    "taain": 36,
    "tain": 36,
    "uloin": 36,
    "vanhin": 36,
    "ylin": 36,

    # -on
    "maraton": 5,
    #
    "backgammon": 6,
    "bourbon": 6,
    "chanson": 6,
    "kaanon": 6,
    "nailon": 6,
    "nelson": 6,
    "nylon": 6,
    "pyton": 6,
    "stadion": 6,
    "triatlon": 6,
    #
    "alaston": 34,

    # -ar
    "cheddar": 5,
    "par": 5,
    #
    "agar": 6,
    "agar-agar": 6,
    "sitar": 6,
    #
    "askar": 49,
    "huhmar": 49,
    "piennar": 49,
    "saivar": 49,
    "udar": 49,

    # -er
    "cheerleader": 5,
    "denier": 5,
    "designer": 5,
    "genever": 5,
    "khmer": 5,
    "košer": 5,
    #
    "appenzeller": 6,
    "babysitter": 6,
    "besserwisser": 6,
    "bestseller": 6,
    "biedermeier": 6,
    "bitter": 6,
    "blazer": 6,
    "copywriter": 6,
    "dealer": 6,
    "freelancer": 6,
    "kassler": 6,
    "laser": 6,
    "loafer": 6,
    "outsider": 6,
    "rottweiler": 6,
    "schäfer": 6,
    "snooker": 6,
    "tonic water": 6,
    "weber": 6,
    "vesper": 6,
    "voucher": 6,
    #
    "auer": 49,
    "kinner": 49,
    "manner": 49,
    "penger": 49,
    "tanner": 49,

    # -ir
    "geisir": 5,
    "geysir": 5,
    "kašmir": 5,
    "mohair": 5,

    # -or
    "helibor": 5,
    "junior": 5,
    "primus motor": 5,
    "senior": 5,
    #
    "art director": 6,
    "nestor": 6,
    "tšador": 6,
    "tutor": 6,

    # -ur
    "glamour": 5,
    "romadur": 5,
    #
    "approbatur": 6,
    "improbatur": 6,
    "laudatur": 6,

    # -VAs
    "iskias": 39,

    # -CAs
    "marakas": 5,
    "moussakas": 5,
    #
    "aidas": 39,
    "ananas": 39,
    "atlas": 39,
    "emäs": 39,
    "haljas": 39,
    "harjas": 39,
    "jalas": 39,
    "juudas": 39,
    "kannas": 39,
    "kehräs": 39,
    "kuvas": 39,
    "lihas": 39,
    "luudas": 39,
    "madras": 39,
    "mullas": 39,
    "nahas": 39,
    "ohjas": 39,
    "priimas": 39,
    "sammas": 39,
    "tervas": 39,
    "teräs": 39,
    "trikomoonas": 39,
    "vastas": 39,
    "vihdas": 39,
    "vitsas": 39,
    #
    "kahdeksas": 45,
    "kolmas": 45,
    "miljoonas": 45,
    "neljäs": 45,
    "nollas": 45,
    "sadas": 45,
    "seitsemäs": 45,
    "yhdeksäs": 45,

    # -es
    "blues": 5,
    "director musices": 5,
    #
    "ies": 41,
    "kirves": 41,
    "äes": 41,
    #
    "kahdeksaskymmenes": 45,
    "kahdes": 45,
    "kahdeskymmenes": 45,
    "kolmaskymmenes": 45,
    "kuudes": 45,
    "kuudeskymmenes": 45,
    "mones": 45,
    "neljäskymmenes": 45,
    "seitsemäskymmenes": 45,
    "tuhannes": 45,
    "viides": 45,
    "viideskymmenes": 45,
    "yhdeksäskymmenes": 45,
    "yhdes": 45,

    # -is
    "altis": 41,
    "aulis": 41,
    "kallis": 41,
    "kaunis": 41,
    "kauris": 41,
    "nauris": 41,
    "raitis": 41,
    "ruis": 41,
    "ruumis": 41,
    "saalis": 41,
    "tiivis": 41,
    "tyyris": 41,
    "valmis": 41,

    # -AUs
    "ahnaus": 40,
    "epävakaus": 40,
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
    "tilanahtaus": 40,
    "työläys": 40,
    "valppaus": 40,
    "vanhurskaus": 40,
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

    # -eUs
    "fariseus": 39,
    "kiveys": 39,
    "loveus": 39,
    "pikeys": 39,
    "poikkeus": 39,
    "risteys": 39,
    "saddukeus": 39,
    "saveus": 39,
    "tyveys": 39,

    # -ius
    "hius": 39,
    "stradivarius": 39,

    # -OUs
    "holhous": 39,
    "ilmarosvous": 39,
    "kirous": 39,
    "kokous": 39,
    "kumous": 39,
    "linkous": 39,
    "lumous": 39,
    "nuohous": 39,
    "patous": 39,
    "putous": 39,
    "rukous": 39,
    "tarjous": 39,
    "verhous": 39,

    # -uus
    "makuus": 39,

    # -At
    "beat": 5,
    "hi-hat": 5,
    "trenchcoat": 5,
    #
    "bermudat": 9,
    #
    "atulat": 12,
    "orgiat": 12,
    #
    "kevät": 44,
    "venät": 44,

    # -et
    "debet": 5,
    "ekstranet": 5,
    "jet set": 5,
    "knesset": 5,
    "market": 5,
    "offset": 5,
    "skeet": 5,
    "tiibet": 5,
    "whippet": 5,
    #
    "sakset": 7,
    #
    "bänet": 8,
    "ravet": 8,
    #
    "beignet": 22,
    "bouquet": 22,
    "buffet": 22,
    "gourmet": 22,

    # -it
    #
    "kutrit": 5,
    "paarit": 5,
    "sanskrit": 5,
    #
    "bikinit": 6,
    "henkselit": 6,

    # -Ut
    "vällyt": 1,
    #
    "burnout": 5,
    "input": 5,
    "knock-out": 5,
    "layout": 5,
    "output": 5,
    "stout": 5,
    #
    "airut": 43,
    "ehyt": 43,
    "immyt": 43,
    "kevyt": 43,
    "kytkyt": 43,
    "kätkyt": 43,
    "lyhyt": 43,
    "neitsyt": 43,
    "ohut": 43,
    "olut": 43,
    "pehmyt": 43,
    "tiehyt": 43,

    # -w
    "know-how": 22,
    "show": 22,
}

# declension, regex
# note: each regex must apply to at least three words
RULES = (
    # === -A ===

    (9,  r"([aei][nrs]?|[ai]u)ha$"),  # a(C)/e(C)/i(C)/au/iu + ha

    (10, r"[äoöu]ij[aä]$"),         # -äijä/-OijA/-uija
    (12, r"(i|...n)j[aä]$"),        # -ijA/-???njA
    (9,  r"([aei][hlnrt]|ra)ja$"),  # -aC/-eC/-iC/-ra + ja

    (
        14,
        r"^[^aeiouyäö]*([aeiouyäö][iu]?|aa|ää|ie|uo|yö)[^aeiouyäö]+"
        r"([aeiouyäö]|ee|ii)[^aeiouyäö]?kk[aä]$"
    ),  # trisyllabic -kkA
    (
        13, r"^[^aeiouyäö]*([aeiouyäö]|aa|ää|ei|oo)[^aeiouyäö]+[aeiouyäö][^aeiouyäö]*k[aä]$"
    ),  # trisyllabic -kA
    (10, r"[ou]i[^aeiouyäö]*ka$"),    # oi/ui + (C)(C)ka
    (9,  r"[aei]u?[^aeiouyäö]*ka$"),  # a/e/i/au/eu/iu + (C)(C)ka

    (9,  r"([aeiou][ai]|[ae]u)la$"),                        # -Va/-Vi/-au/-eu + la
    (10, r"[aeiouyäö]{2}l[aä]$"),                           # -VVlA
    (10, r"^[^aeiouyäö][aeiouyäö][^aeiouyäö][aäe]l[aä]$"),  # CVC + Ala/elA
    (12, r"...[aeiouyäö]l[aä]$"),                           # -???VlA
    (13, r"^[^aeiouyäö]?[aeiouyäö][^aeiouyäö]+[aeiouyäö][^aeiouyäö]l[aä]$"),  # -ClA (trisyllabic)
    (9,  r"[aei][^aeiouyäö]?la$"),                          # -a/-e/-i + (C)la

    (10, r"(...l|(ui|o|u)[^aeiouyäö]*)ma$"),  # -???lma/-ui(C)(C)ma/-o(C)(C)ma/-u(C)(C)ma
    (9,  r"(aa|ee|[^ou]i|[^aeiouyäö])ma$"),   # -aama/-eema/-ima/-Cma (not -oima/-uima)

    (13, r"..(ee|ii|uu)na$"),                  # ?? + ee/ii/uu + na
    (9,  r"[aei][aieu][^aeiouyäö]*na$"),       # a/e/i + a/e/i/u + (C)(C)na
    (10, r"[aeiouyäö]{2}[^aeiouyäö]*n[aä]$"),  # -VV(C)(C)nA
    (12, r"..[aäiuy]n[aä]$"),                  # ?? + A/i/U + nA
    (9,  r"[aei][^aeiouyäö]*na$"),             # a/e/i + (C)(C)na

    (9,  r"(a|e|[^ou]i)[^aeiouyäö]*pa$"),  # a/e/i (not oi/ui) + (C)(C)pa

    (9,  r"[aei][aeiu][^aeiouyäö]*ra$"),  # a/e/i + a/e/i/u + (C)(C)ra
    (13, r"...uura$"),                    # -???uura
    (12, r"...[auy]r[aä]$"),              # ???   + a/U     + rA
    (9,  r"(a|e|i|eu)[^aeiouyäö]*ra$"),   # a/e/i           + (C)(C)ra

    (13, r"...(es|it)sa$"),              # ??? + es/it    + sa
    (10, r"(oi|...[au]i)sa$"),           # oi/???ai/???ui + sa
    (9,  r"([aei]|iu)[^aeiouyäö]*sa$"),  # a/e/i/iu       + (C)(C)sa

    (9,  r"[ai]u[st]?ta$"),         # au/iu + (s/t)ta
    (9,  r"...nt[aä]$"),            # -???ntA
    (13, r"..usta$"),               # -usta
    (9,  r"[aei][^aeiouyäö]*ta$"),  # a/e/i + (C)(C)ta

    (9,  r"(haa|au|[ai]i|[ai][^aeiouyäö])va$"),  # haa/au/ai/ii/aC/iC + va

    (9,  r"[aei][^aeiouyäö]*[bdfgšž]a$"),  # a/e/i + (C)(C) + ba/da/fa/ga/ša/ža

    (10, r"oa$"),                            # -oa
    (12, r"(i[aä]|ua|[^aeiouyäö][nr]ea)$"),  # -iA/-ua/-Cnea/-Crea
    (15, r"e[aä]$"),                         # -eA
    (17, r"..aa$"),                          # -??aa
    (18, r"(aa|ää)$"),                       # -AA

    (10, r"[aä]$"),  # -A

    # === -e ===

    (20, r"..ee$"),                 # -ee
    (8,  r"(c|g|gn)e$"),            # -ce/-ge/-gne
    (49, r"ere$"),                  # -ere
    (48, r"[aiuydhjklmnprstv]e$"),  # -e

    # === -i ===

    (23, r"(ii|o|[ou]u)hi$"),  # -iihi/-ohi/-ouhi/-uuhi
    (7,  r"(l|n|är)hi$"),      # -lhi/-nhi/-ärhi

    (6,  r"[^aeiouyäö]ji$"),  # -Cji

    (7,  r"[älrt]ki$"),  # -äki/-lki/-rki/-tki

    (26, r"^.(ie|uo)li$"),             # ?ieli/?uoli
    (6,  r"^.{1,3}[^aeiouyäö]aali$"),  # ?(?)(?)Caali
    (6,  r".[^aeiouyäö][aäeuy]li$"),   # -?CAli/-?Celi/-?CUli

    (25, r"^.(ie|uo|oi)mi$"),          # ?iemi/?uomi/?oimi
    (6,  r"...[^aeiouyäö][aeuy]mi$"),  # -???Cami/-???Cemi/-???CUmi

    (26, r"(ie|uo)ni$"),                             # -ieni/-uoni
    (7,  r"sini$"),                                  # -sini
    (6,  r"^.{2,3}[^aeiouyäö](aa|ää|ee|ii|oo)ni$"),  # ??(?)C + AA/ee/ii/oo + ni

    (16, r"[eo]mpi$"),           # -empi/-ompi
    (7,  r"([älmr]|[io]i)pi$"),  # -äpi/-lpi/-mpi/-rpi/-iipi/-oipi

    (26, r"(juu|[knv]uo)ri$"),                  # -juuri/-kuori/-nuori/-vuori
    (5,  r"([^lp]pa|do)ri$"),                   # -pari/-dori (not -lpari/-ppari)
    (6,  r"^...?[^aeiouyäö](aa|ee|ii|uu)ri$"),  # ??(?)C + aa/ee/ii/uu + ri
    (6,  r".[^aeiouyäö][aeouyä]ri$"),           # -?C + A/e/o/U + ri

    (24, r"kuusi$"),               # -kuusi
    (5,  r"(ee|ii|oo|uu|yy)si$"),  # -eesi/-iisi/-oosi/-UUsi
    (27, r"(e|ei|o|u|y)si$"),      # -esi/-eisi/-osi/-Usi
    (28, r"[lnr]si$"),             # -lsi/-nsi/-rsi

    (7,  r"parvi$"),  # -parvi

    (18, r"[aeio]i$"),             # -ai/-ei/-ii/-oi
    (5,  r"[bdfghjklmnprstv]i$"),  # -Ci

    # === -O ===

    (1,  r"(po|kuu)ro$"),  # -poro/-kuuro

    (4,  r"...[aäiouy]kk[oö]$"),                       # -??? + A/i/o/U + kkO
    (4,  r"^[aeiouyäö][^aeiouyäö][aeiouyäö]kk[oö]$"),  # VCVkkO
    (2,  r"^.{2,4}[ai]sk[oö]$"),                       # ??(?)(?) + a/i + skO

    (2,  r"^.{4,5}st[oö]$"),                           # ????(?)stO
    (2,  r"^[aeiouyäö][^aeiouyäö][aeiouyäö]st[oö]$"),  # VCVstO

    (2,  r"...(.[lmr]|in|is)o$"),  # -??? + ?lo/?mo/?ro/ino/iso
    (2,  r"...[äei][lmrs]ö$"),     # -??? + ä/e/i + lö/mö/rö/sö

    (17, r"oo$"),                 # -oo
    (19, r"(uo|yö)$"),            # -UO
    (3,  r"([aei]o|iö)$"),        # -ao/-eo/-iO
    (1,  r"(o|[hjklmnprst]ö)$"),  # -o/-Cö

    # === -U ===

    (17, r"..uu$"),     # -??uu
    (20, r"..yy$"),     # -??yy
    (18, r"(uu|yy)$"),  # -UU
    (21, r"[aeo]y$"),   # -ay/-ey/-oy

    (2,  r"...(el|il|is)[uy]$"),    # -??? + elU/ilU/isU
    (1,  r"[bdhjklmnprstv][uy]$"),  # -CU

    # === -C ===

    # -Vl
    (49, r"el$"),

    # -Vn
    (34, r"[aeiouyäö]t[oö]n$"),    # -VtOn
    (18, r".ilmeinen$"),           # -?ilmeinen
    (38, r"[aäioöuy]nen(kin)?$"),  # -A/-i/-O/-U + nen(kin)
    (32, r"[himsv]en$"),           # -en
    (33, r"in$"),                  # -in
    (5,  r"[ao]n$"),               # -an/-on

    # -Vr
    (32, r"[st][aä]r$"),  # -sAr/-tAr

    # -Vs
    (39, r"siivous$"),        # -siivous
    (40, r"[eioöuy][uy]s$"),  # -eUs/-iUs/-OUs/-UUs
    (41, r"[aä]s$"),          # -As
    (39, r"[eioöuy]s$"),      # -es/-is/-Os/-Us

    # -Vt (incl. plurals)
    #
    (41, r"aat$"),     # -aat
    (12, r".{6}at$"),  # -??????at
    (10, r"ät$"),      # -ät
    (9,  r"at$"),      # -t
    #
    (48, r"eet$"),        # -eet
    (38, r"[iouy]set$"),  # -iset/-oset/-Uset
    (39, r"kset$"),       # -kset
    (33, r"imet$"),       # -imet
    (7,  r"et$"),         # -et
    #
    (6,  r"[aäeu]rit$"),     # -Arit/-erit/-urit
    (5,  r"[dfglmstv]it$"),  # -Cit
    #
    (47, r"(ll|n)[uy]t$"),    # -llUt/-nUt (participles)
    (1,  r"[oöuy]t$"),        # -Ot/-Ut

    # -C
    (5,  r"(ag|ak|am|ap|ec|ed|ek|ic|od|og|ok|om|op|ox|ub|um|up)$"),  # -VC (C != l/n/r/s/t)
    (5,  r"(ch|ck|ff|ks|lk|ll|nd|ng|nk|ns|nt|rd|rn|rt|ss|st)$"),     # -CC
)

def get_declensions(noun, useExceptions=True):
    """noun: a Finnish noun in nominative singular (or plural if singular isn't used)
    return: set of 0...2 Kotus declensions (each 1...49)"""

    try:
        return MULTI_DECLENSION_NOUNS[noun]
    except KeyError:
        pass

    if useExceptions:
        try:
            return {EXCEPTIONS[noun]}
        except KeyError:
            pass

    for (declension, regex) in RULES:
        if re.search(regex, noun) is not None:
            return {declension}

    return set()

def check_redundant_exceptions():
    """Are there redundant exceptions (same declension as the rules would indicate)?"""

    for noun in EXCEPTIONS:
        detectedDeclensions = get_declensions(noun, False)
        if detectedDeclensions and EXCEPTIONS[noun] == list(detectedDeclensions)[0]:
            print(f"Redundant exception: '{noun}'")

def main():
    check_redundant_exceptions()

    if len(sys.argv) != 2:
        sys.exit(
            "Get Kotus declension(s) of a Finnish noun. Argument: noun in nominative singular"
        )
    noun = sys.argv[1]

    declensions = get_declensions(noun)
    if not declensions:
        sys.exit("Unrecognized noun.")
    for d in declensions:
        print(f'declension {d} (like "{DECLENSION_DESCRIPTIONS[d]}")')

if __name__ == "__main__":
    main()
