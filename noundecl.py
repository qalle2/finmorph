"""Get the declensions of a Finnish noun."""

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
# - if all nouns beginning with the same letter do not fit on the same line,
#   insert a newline before the first such noun; examples:
#   - allowed:     charlie <newline> delta, dixie, echo
#   - not allowed: charlie, delta <newline> dixie, echo
#   (this convention makes it easier to add or delete words at the start of a
#   long list)
_EXCEPTIONS = {
    # === Monosyllabic ===

    # -VV
    "brie": 21, "clou": 21,
    #
    "hie": 48,

    # -n
    "ien": 32,
    #
    "näin": 33, "puin": 33,
    #
    "tain": 36,

    # -s
    "AIDS": 5,
    #
    "hius": 39, "taus": 39,
    #
    "ies": 41, "ruis": 41,
    #
    "mies": 42,

    # -C (not -n/-s)
    "LED": 5,
    #
    "show": 22,

    # === Disyllabic ===

    # -VV
    "duo": 1, "trio": 1,
    #
    "boutique": 8, "petanque": 8,
    #
    "dia": 9, "maya": 9,
    #
    "boa": 10,
    #
    "hynttyy": 17,
    #
    "frisbee": 18, "huuhaa": 18, "peeaa": 18, "puusee": 18,
    #
    "nugaa": 20, "raguu": 20, "sampoo": 20, "trikoo": 20, "voodoo": 20,
    #
    "fondue": 21, "reggae": 21, "tax-free": 21,
    #
    "aie": 48, "säie": 48,

    # -Ca
    "krypta": 9, "lymfa": 9, "suola": 9,
    #
    "saaja": 10, "saapa": 10, "saava": 10,

    # -Cä
    "iskä": 9, "nyintä": 9, "ryintä": 9,

    # -Ce
    "ale": 8, "bäne": 8, "deadline": 8, "folklore": 8, "forte": 8, "itse": 8,
    "jade": 8, "joule": 8, "kalle": 8, "kurre": 8, "mangrove": 8, "manne": 8,
    "nalle": 8,
    "pelle": 8, "penne": 8, "polle": 8, "poplore": 8, "pose": 8, "psyyke": 8,
    "quenelle": 8, "striptease": 8, "tele": 8, "vaudeville": 8,
    #
    "bile": 20,
    #
    "hake": 48, "hame": 48, "kare": 48,

    # -Ci
    "holvi": 5, "kolvi": 5, "kurvi": 5, "loki": 5, "LYHKI": 5, "lärvi": 5,
    "mansi": 5, "olvi": 5, "orhi": 5, "puomi": 5, "sorvi": 5, "sutki": 5,
    "tuoli": 5, "varvi": 5,
    #
    "appi": 7,
    "haahti": 7, "hanhi": 7, "hanki": 7, "happi": 7, "hauki": 7, "helmi": 7,
    "henki": 7, "hiki": 7,
    "kaikki": 7, "kanki": 7, "kaski": 7, "kiiski": 7, "kivi": 7, "koipi": 7,
    "koski": 7, "lehti": 7, "leski": 7, "lovi": 7, "länki": 7,
    "nimi": 7, "nummi": 7, "nurmi": 7, "onki": 7, "onni": 7, "ovi": 7,
    "piki": 7, "poski": 7, "povi": 7, "päitsi": 7, "rupi": 7,
    "saarni": 7, "saksi": 7, "salmi": 7, "sappi": 7, "savi": 7, "seimi": 7,
    "siipi": 7, "soppi": 7, "sormi": 7, "suitsi": 7, "suksi": 7, "suomi": 7,
    "suvi": 7, "sänki": 7, "sääksi": 7, "sääski": 7,
    "tammi": 7, "tuki": 7, "tuppi": 7, "typpi": 7, "tähti": 7,
    "vaski": 7, "veli": 7, "viiksi": 7, "vuoksi": 7,
    #
    "kumpi": 16,
    #
    "moni": 23, "tiili": 23, "tuli": 23,
    #
    "hiili": 24, "hiiri": 24, "huuli": 24, "kusi": 24, "meri": 24, "ruuhi": 24,
    "uni": 24,
    #
    "lumi": 25, "taimi": 25,
    #
    "juuri": 26, "kaari": 26, "niini": 26, "nuori": 26,
    "saari": 26, "suuri": 26, "sääri": 26, "tuuli": 26, "tyyni": 26,
    "veri": 26, "vieri": 26, "ääni": 26, "ääri": 26,
    #
    "heisi": 27, "hiisi": 27, "kausi": 27, "kesi": 27, "käsi": 27, "köysi": 27,
    "liesi": 27, "mesi": 27, "niisi": 27, "paasi": 27, "reisi": 27,
    "susi": 27, "sysi": 27, "tosi": 27, "täysi": 27, "uusi": 27,
    "vesi": 27, "viisi": 27, "vuosi": 27,
    #
    "lapsi": 29,
    #
    "veitsi": 30,
    #
    "haaksi": 31, "kaksi": 31, "yksi": 31,

    # -CO/-CU
    "go-go": 18,
    #
    "kung-fu": 21,
    #
    "kiiru": 48,

    # -l
    "kennel": 5,
    #
    "diesel": 6, "rial": 6,
    #
    "nivel": 32, "sävel": 32,
    #
    "seppel": 49,

    # -n
    "dralon": 5, "drive-in": 5, "hymen": 5, "kelvin": 5, "pinyin": 5,
    #
    "kaanon": 6, "lumen": 6, "luumen": 6, "pyton": 6,
    #
    "hapan": 33, "laidun": 33, "sydän": 33,
    #
    "lämmin": 35,
    #
    "alin": 36, "enin": 36, "likin": 36, "lähin": 36, "parhain": 36,
    "sisin": 36, "taain": 36, "uloin": 36, "vanhin": 36, "ylin": 36,
    #
    "vasen": 37,

    # -r
    "sitar": 6,
    #
    "sisar": 32, "tatar": 32, "tytär": 32,
    #
    "udar": 49,

    # -As
    "aidas": 39, "atlas": 39, "emäs": 39, "haljas": 39, "harjas": 39,
    "jalas": 39, "juudas": 39,
    "kaimas": 39, "kannas": 39, "kehräs": 39, "kuvas": 39,
    "lihas": 39, "luudas": 39, "madras": 39, "mullas": 39, "nahas": 39,
    "ohjas": 39, "priimas": 39, "sammas": 39, "tervas": 39, "teräs": 39,
    "vastas": 39, "vihdas": 39, "viinas": 39, "vitsas": 39,
    #
    "kolmas": 45, "nollas": 45, "sadas": 45,

    # -es
    "blues": 5,
    #
    "lehdes": 39,
    #
    "mones": 45,

    # -is
    "kallis": 41, "raitis": 41, "tiivis": 41,

    # -VUs
    "couscous": 5,
    #
    "kehruus": 39, "kirous": 39, "kiveys": 39, "kokous": 39, "kumous": 39,
    "linkous": 39, "lumous": 39, "makuus": 39,
    "patous": 39, "persuus": 39, "pikeys": 39, "poikkeus": 39, "putous": 39,
    "risteys": 39, "rukous": 39, "tarjous": 39, "tyveys": 39,
    #
    "ahnaus": 40,
    "harmaus": 40, "hartaus": 40, "hauraus": 40, "herraus": 40, "hitaus": 40,
    "hurskaus": 40, "irstaus": 40,
    "karsaus": 40, "kiivaus": 40, "kirkkaus": 40, "kitsaus": 40, "kuulaus": 40,
    "kärkkäys": 40, "lahous": 40, "liukkaus": 40, "mahous": 40, "maukkaus": 40,
    "puhtaus": 40,
    "raihnaus": 40, "rakkaus": 40, "raskaus": 40, "reippaus": 40,
    "riettaus": 40, "rikkaus": 40, "runsaus": 40, "sairaus": 40, "suulaus": 40,
    "työläys": 40,
    "valppaus": 40, "vapaus": 40, "varkaus": 40, "vauraus": 40, "vehmaus": 40,
    "viekkaus": 40, "vieraus": 40, "viisaus": 40, "vilkkaus": 40,
    "vuolaus": 40, "ylväys": 40,

    # -CUs
    "ryntys": 41, "vantus": 41,

    # -t
    "input": 5, "output": 5,
    #
    "beignet": 22, "bouquet": 22, "buffet": 22, "gourmet": 22, "nougat": 22,
    "parfait": 22, "ragoût": 22,
    #
    "kevät": 44, "venät": 44,
    #
    "tuhat": 46,

    # -C (not -l/-n/-r/-s/-t)
    "bordeaux": 22, "know-how": 22,

    # === Trisyllabic ===

    # -VV
    "feijoa": 10,
    #
    "pallea": 12, "urea": 12,
    #
    "media": 13,
    #
    "brasserie": 21,

    # -ba/-da/-fa/-ha/-sa
    "alfalfa": 9, "ameba": 9, "marimba": 9,
    #
    "pomada": 10,
    #
    "prinsessa": 13, "reseda": 13, "vernissa": 13,
    #
    "cha-cha-cha": 21,

    # -ja
    "apaja": 11,
    #
    "mantilja": 13, "papaija": 13, "vanilja": 13,

    # -ka
    "nautiikka": 9,
    #
    "paprika": 12,

    # -la
    "kavala": 10, "nokkela": 10, "ovela": 10, "sukkela": 10,
    #
    "vankila": 12,
    #
    "apila": 13, "kampela": 13, "sikala": 13, "takila": 13,

    # -ma
    "dilemma": 9, "ekseema": 9, "sialma": 9,
    #
    "hekuma": 11, "paatsama": 11, "probleema": 11, "ödeema": 11,
    #
    "salama": 12,
    #
    "karisma": 13, "maailma": 13, "suurima": 13,

    # -na
    "ruustinna": 9,
    #
    "gallona": 10, "ihana": 10, "leijona": 10,
    #
    "lattana": 11, "maruna": 11, "murena": 11, "ohrana": 11, "omena": 11,
    "sikuna": 11,
    #
    "haapana": 12, "harppuuna": 12, "keppana": 12, "nahina": 12, "pirpana": 12,
    #
    "arina": 13, "ipana": 13, "kohina": 13, "kopina": 13, "kuhina": 13,
    "marina": 13, "paukkina": 13, "porina": 13, "reppana": 13, "retsina": 13,
    "smetana": 13,

    # -ra
    "kimaira": 9, "tiaara": 9,
    #
    "amfora": 10, "ankara": 10, "avara": 10, "kumara": 10, "kupera": 10,
    "uuttera": 10,
    #
    "hapera": 11, "sikkara": 11, "tomera": 11,
    #
    "kattara": 12, "littera": 12,
    #
    "gerbera": 13, "ketara": 13, "kitara": 13, "matara": 13, "sikkura": 13,
    "tempera": 13, "vaahtera": 13,

    # -ta
    "canasta": 9, "prostata": 9, "toccata": 9,
    #
    "huuhdonta": 10,

    # -va
    "ahava": 11, "harava": 11,
    #
    "passiiva": 12,
    #
    "aktiiva": 13,

    # -Cä
    "emäntä": 10, "isäntä": 10,
    #
    "veiterä": 11, "äpärä": 11,
    #
    "jäkkärä": 12, "räkälä": 12, "väkkärä": 12,
    #
    "kärinä": 13, "määkinä": 13, "mölinä": 13, "mörinä": 13, "möyrinä": 13,
    "siivilä": 13,

    # -Ce
    "ginger ale": 8, "ladylike": 8, "tabbule": 8,
    #
    "jäntere": 48,
    #
    "askare": 49, "askele": 49, "kantele": 49, "petkele": 49, "taipale": 49,

    # -Ci
    "afgaani": 5, "alleeli": 5, "biennaali": 5, "butaani": 5, "doktriini": 5,
    "etaani": 5, "eteeni": 5, "etruski": 5,
    "fenkoli": 5, "fertiili": 5, "fibriini": 5, "fosfori": 5,
    "gerbiili": 5, "gluteeni": 5, "humaani": 5, "imaami": 5,
    "jasmiini": 5, "joriini": 5,
    "kaimaani": 5, "kajaali": 5, "karbiini": 5, "kardaani": 5, "kefiiri": 5,
    "ketoni": 5, "kiniini": 5, "konsiili": 5, "koraali": 5, "Koraani": 5,
    "korpraali": 5, "kretliini": 5, "kvasaari": 5,
    "labiili": 5, "lantaani": 5, "laviini": 5, "liaani": 5, "ligniini": 5,
    "likvori": 5, "lojaali": 5,
    "mangaani": 5, "membraani": 5, "mesoni": 5, "metaani": 5, "migreeni": 5,
    "modaali": 5, "moguli": 5, "monstrumi": 5, "morfiini": 5,
    "oktaani": 5, "oopiumi": 5, "orgaani": 5, "otsoni": 5,
    "paapuuri": 5, "palsami": 5, "patiini": 5, "pedaali": 5, "pendeli": 5,
    "pepsiini": 5, "pineeni": 5, "pluraali": 5, "porfiini": 5, "primaari": 5,
    "profaani": 5, "profiili": 5, "propaani": 5, "protoni": 5, "pyloni": 5,
    "rabbiini": 5, "retliini": 5, "reviiri": 5, "risiini": 5, "rutiini": 5,
    "samaani": 5, "šamaani": 5, "sampaani": 5, "seireeni": 5, "strykniini": 5,
    "syaani": 5, "sykliini": 5, "sykloni": 5,
    "tanniini": 5, "teiini": 5, "toksiini": 5, "triennaali": 5, "tyyrpuuri": 5,
    "viriili": 5, "vulgaari": 5,
    #
    "antenni": 6, "atolli": 6, "atomi": 6,
    "basilli": 6, "biljardi": 6, "bisarri": 6, "daktyyli": 6, "entsyymi": 6,
    "flanelli": 6, "foneemi": 6, "frisyyri": 6, "gaselli": 6, "glukoosi": 6,
    "hampuusi": 6, "hotelli": 6,
    "kanjoni": 6, "karpaasi": 6, "kivääri": 6, "kolhoosi": 6, "kommuuni": 6,
    "konsoli": 6, "koturni": 6, "kumppani": 6, "kupoli": 6,
    "likööri": 6, "linoli": 6,
    "marttyyri": 6, "misääri": 6, "moduuli": 6, "monsuuni": 6, "monttööri": 6,
    "motelli": 6, "muslimi": 6, "narkoosi": 6, "neuroosi": 6,
    "oliivi": 6,
    "pakaasi": 6, "plantaasi": 6, "pogromi": 6, "poliisi": 6, "proteesi": 6,
    "putelli": 6, "refleksi": 6,
    "sardelli": 6, "serviisi": 6, "sirtaki": 6, "sotiisi": 6, "sottiisi": 6,
    "sovhoosi": 6, "standardi": 6, "sypressi": 6, "systeemi": 6,
    "taifuuni": 6, "tienesti": 6, "toteemi": 6, "trapetsi": 6, "tribuuni": 6,
    "trotyyli": 6, "turkoosi": 6, "turnyyri": 6, "ukaasi": 6,
    "valööri": 6, "vampyyri": 6, "vinyyli": 6, "viskoosi": 6, "volyymi": 6,
    "zoonoosi": 6, "äksiisi": 6,

    # -Co
    "hampaisto": 1,
    "kalusto": 1, "kojeisto": 1, "koneikko": 1, "kuidusto": 1, "kuormasto": 1,
    "lainaamo": 1, "laitteisto": 1, "lajisto": 1, "lasisto": 1,
    "munkisto": 1, "murteisto": 1, "naisisto": 1, "oikeisto": 1,
    "parhaisto": 1, "pensaisto": 1, "poikaisto": 1, "pojisto": 1,
    "praktikko": 1,
    "raiteisto": 1, "rattaisto": 1, "ruovisto": 1, "ruususto": 1,
    "saraikko": 1, "sombrero": 1, "vaihteisto": 1, "virasto": 1,

    # -Cö
    "hyllystö": 1, "käyrästö": 1, "lehdistö": 1, "linssistö": 1, "lähistö": 1,
    "merkistö": 1, "pillistö": 1, "syvänkö": 1, "testistö": 1, "väylästö": 1,
    "ylänkö": 1,

    # -CU
    "huitaisu": 1, "kyhäily": 1,

    # -n
    "charleston": 5, "maraton": 5,
    #
    "kumpikaan": 16, "kumpikin": 16,
    #
    "kymmenen": 32,
    #
    "parahin": 36,

    # -s
    "calvados": 5, "marakas": 5, "moussakas": 5,
    #
    "tournedos": 22,
    #
    "iskias": 39,
    #
    "vanhurskaus": 40,
    #
    "tuhannes": 45,

    # -C (not -n/-r/-s)
    "CD-ROM": 5,
    #
    "passepartout": 22, "port salut": 22,

    # === Quadrisyllabic and longer ===

    # -VV
    "adagio": 1,
    #
    "odysseia": 9,
    #
    "paranoia": 10,
    #
    "politbyroo": 20, "varietee": 20,

    # -Ca
    "abrakadabra": 9, "akileija": 9, "ballerina": 9, "basilika": 9,
    "dalai-lama": 9, "enchilada": 9, "hoosianna": 9, "ikebana": 9,
    "jakaranda": 9, "karateka": 9, "mykorritsa": 9,
    "panoraama": 9, "paradigma": 9, "praasniekka": 9, "propaganda": 9,
    "teoreema": 9, "valeriaana": 9,
    #
    "gorgonzola": 10, "halveksunta": 10, "hyperbola": 10, "karambola": 10,
    "protokolla": 10, "terrakotta": 10,
    #
    "marihuana": 11,
    #
    "ekliptika": 12,
    #
    "karakteristika": 13, "majolika": 13, "nomenklatuura": 13,
    "psykofarmaka": 13, "skandinaaviska": 13,
    #
    "estetiikka": 14, "poliklinikka": 14, "psykometriikka": 14,
    #
    "hänenlaisensa": 38,

    # -Cä
    "hyväksyntä": 10, "väheksyntä": 10,

    # -Ce
    "bavaroise": 8, "eau de Cologne": 8, "faksimile": 8,
    "karaoke": 8, "komedienne": 8, "mezzoforte": 8, "minestrone": 8,
    "tagliatelle": 8, "tragedienne": 8, "ukulele": 8,
    #
    "väkevöite": 48,

    # -Ci
    "follikkeli": 5, "kateederi": 5, "kollektori": 5, "kompostori": 5,
    "multippeli": 5, "varistori": 5,
    #
    "akupunktuuri": 6, "azerbaidžani": 6, "diakoni": 6, "firaabeli": 6,
    "inspehtori": 6, "prostaglandiini": 6, "reversiibeli": 6, "revolveri": 6,
    "testosteroni": 6, "ubikinoni": 6, "unioni": 6, "universumi": 6,
    "variaabeli": 6,
    #
    "minunlaiseni": 38, "sinunlaisesi": 38,

    # -Co
    "karkaisimo": 1, "koksittamo": 1, "miljoonikko": 1,
    "pantomiimikko": 1, "papurikko": 1, "pateetikko": 1, "poleemikko": 1,
    "poliitikko": 1, "pragmaatikko": 1, "romantikko": 1, "semiootikko": 1,
    "untuvikko": 1, "uskalikko": 1,
    #
    "katajisto": 2, "koordinaatisto": 2, "luettelo": 2,

    # -Cö
    "petäjikkö": 1,

    # -CU
    "elostelu": 1, "istuskelu": 1,

    # -r
    "agar-agar": 6, "appenzeller": 6, "approbatur": 6, "art director": 6,
    "babysitter": 6, "besserwisser": 6, "biedermeier": 6, "copywriter": 6,
    "improbatur": 6, "tonic water": 6,

    # -s
    "director musices": 5,
    #
    "stradivarius": 39, "trikomoonas": 39,

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
# - One rule per declension, except when the declension contains different
#   kinds of words (e.g. -VV and -C).
# - When rules don't depend on each other, sort them by declension under each
#   section (-VV etc.).
# - Each regex should match at least three words.
# - Don't use capital letters or punctuation in rules; handle those words as
#   exceptions.

# rules for monosyllabic nouns (declension, regex)
_RULES_1SYLL = tuple((d, re.compile(r + "$", re.VERBOSE)) for (d, r) in (
    # -VV (44 nouns, 3 exceptions)
    (19, "(ie|uo|yö)"),
    (21, "ay"),
    (18, r"([aeiouyäö]) (\1|i|u)"),

    # -CV (8 nouns, no exceptions)
    ( 8, "e"),

    # -C (52 nouns, 10 exceptions)
    ( 5, "[bcdfghklnprsštxz]"),
))

# rules for disyllabic nouns (declension, regex)
_RULES_2SYLL = tuple((d, re.compile(r + "$", re.VERBOSE)) for (d, r) in (
    # -VV (107 nouns, 22 exceptions)
    (17, "(aa|oo|uu)"),
    (18, "[ai]i"),
    (20, "(ee|öö|yy)"),
    (21, "[aeo]y"),
    (48, "[aäou]e"),

    # -Ca (1022 nouns, 6 exceptions)
    (
        9,
        "( [ae] | [aei][iu] | [bcdfghjklmnpqrsštvwxzž]i | ^i )"
        "[bdfghjklmnprsštvzž]+a"
    ),
    (
        10,
        "( [oy] | [ou][iu] | [bcdfghjklmnpqrsštvwxzž]u | ^u )"
        "[bdfghjklmnprstv]+a"
    ),

    # -Cä (230 nouns, 3 exceptions)
    (10, "[hjklmnprstv]ä"),

    # -Ce (409 nouns, 27 exceptions)
    ( 8, "(c|[ln]d|g|ch|[ak]k|[gyz]l|[ai]m|kn|[êop]p|[aèn]r|ss)e"),
    (48, "[dhjklmnprstv]e"),

    # -Cé (4 nouns, no exceptions)
    (21, "[bprs]é"),

    # -Ci (1312 nouns, 120 exceptions)
    ( 7, "( [lr]h | [elortä]k | [lmrä]p | [lry]v )i"),
    (23, "(ii|o|u)hi"),
    (25, "(ie|oi|uo)mi"),
    (26, "( (ie|uo)[ln] | eer | ous )i"),
    (28, "[lnr]si"),
    ( 5, "[bdfghjklmnprsštvw]i"),

    # -CO/-CU (1417 nouns, 3 exceptions)
    ( 1, "[bcdfghjklmnprstvz][oöuy]"),

    # -s (1451 nouns, 94 exceptions)
    (45, "(de|jä)s"),
    (40, "( [iu]u | [^v]eu | [^ch]ou | [eiöy]y )s"),
    (41, "( a | ä | (ä|rv)e | (aa|au|uu|yy)[lmnr]i | l[mt]i )s"),
    (39, "[eioöuy]s"),
    ( 5, "s"),

    # -C (not -s; 439 nouns, 50 exceptions)
    ( 6, "( (da|e|ö)m | [bls]on | lup | (ga|[bfhklpstz]e|o)r )"),
    (32, "[hmsv]en"),
    (33, "in"),
    (34, "[aeiouyäö] t[oö]n"),
    (38, "nen"),
    (47, "(ll|n)[uy]t"),
    (43, "[^o][uy]t"),
    (49, "( [mv]al | [kmn]el | [är]en | [kmnv]ar | [gnu]er )"),
    ( 5, "[bcdfghklmnprštx]"),
))

# rules for trisyllabic nouns (declension, regex)
_RULES_3SYLL = tuple((d, re.compile(r + "$", re.VERBOSE)) for (d, r) in (
    # -VV (455 nouns, 5 exceptions)
    ( 3, "( [io]e | [aäei][oö] | yo )"),
    (12, "( (d|n|br|pr)ea | [iuy][aä] )"),
    (15, "( e[aä] | oa )"),
    (18, "( pee | [aeu]i | oo | uu )"),
    (20, "ee"),
    (48, "[uy]e"),

    # -da/-ga/-pa/-va (161 nouns, 6 exceptions)
    ( 9, "(d|uav|kv)a"),
    (10, "( [^u]a | [^i]i | [eour] )va"),
    (13, "(ed|g)a"),
    (14, "ppa"),

    # -ja (292 nouns, 4 exceptions)
    (10, "[aou]ja"),
    (11, "oija"),
    (12, "( [^o]i | l | n )ja"),

    # -ka (224 nouns, 2 exceptions)
    ( 9, "nka"),
    (11, "oka"),
    (13, "[aeihs]ka"),
    (14, "kka"),

    # -la (103 nouns, 9 exceptions)
    ( 9, "( oa | ui | [hps]il )la"),
    (13, "( aa | ni | k | [ei]l | io )la"),
    (12, "( (nd|rj|[kor]k|im|n|pp|r|rs|[lnt]t|v)[aei] | [^i]o | u )la"),
    (10, "[kmtv]ala"),

    # -ma (173 nouns, 11 exceptions)
    (10, "[aeioul]ma"),
    (11, "(ee|t) ma"),

    # -na (172 nouns, 26 exceptions)
    (10, "( [ao]n | o[ou] ) na"),
    (11, "(pa|o) na"),
    (13, "( (ek|ut)a | ee | (a|g|ah|i|am|ks|iv)i | en | (uk|l|u)u | r )na"),
    (12, "na"),

    # -ra (83 nouns, 20 exceptions)
    (10, "(fa|ke|ve|t)ra"),
    (11, "(ha|ta|b|te)ra"),
    (13, "(i|uu)ra"),
    (12, "ra"),

    # -sa (73 nouns, 2 exceptions)
    ( 9, "issa"),
    (10, "isa"),
    (11, "osa"),
    (13, "(t|uu)sa"),

    # -ta (219 nouns, 4 exceptions)
    ( 9, "( n | (ga|ee|ii|r|uu)t )ta"),
    (13, "(e|i|is|us) ta"),
    (14, "[hmv][aeo] tta"),

    # -Cä (520 nouns, 13 exceptions)
    ( 9, "ntä"),
    (11, "( päl | häm | [kt]än | (ve|kä)r )ä"),
    (12, "( ij | (i|y|mä)l | n | yr )ä"),
    (13, "(sk|st)ä"),
    (14, "kkä"),
    (10, "[jlmrsv]ä"),

    # -Ce (476 nouns, 9 exceptions)
    ( 8, """
        (
        c | ud | g | (da|b|g|bi|[iu]l)l | (g|ui)n | (ra|i|u)r | s
        | (ra|[nôrt])t | v
        )e
    """),
    (49, "( [np]el | en | ([mtv]a|e)r )e"),
    (48, "[dklnrt]e"),

    # -Ci (2083 nouns, 154 exceptions)
    ( 6, """(
        [ln]j
        | ( [lz]u | us )k
        | ( [aä] | [^a]e | ii | [bdikorv]o | [^u]u )l
        | ( [ahjrs]a | re | do | u )m
        | ( [am]a | [^d]e | [fhik]i | [bdklost]o | ä )n
        | ( [aeou] | ii | [^y]y | [^ä]ä )r
    )i"""),
    (16, "mpi"),
    ( 5, "[bdfgjklmnprstv]i"),

    # -Co (533 nouns, 27 exceptions)
    ( 1, "( c | (bi|n)d | [nr]g | nk | [iu]an | gr | ([br]a|n|t)t )o"),
    ( 4, "kko"),
    ( 2, "[bdghjklmnrstv]o"),

    # -Cö (136 nouns, 11 exceptions)
    ( 1, "( [lnt] | [pä]is )tö"),
    ( 4, "kkö"),
    ( 2, "[klmrst]ö"),

    # -CU (492 nouns, 2 exceptions)
    ( 1, "( (b|its|t)u | [rtv]y )"),
    ( 2, "[djlrs][uy]"),

    # -n (1639 nouns, 6 exceptions)
    ( 6, "(ua|be|dio|lo|mo)n"),
    (10, "(sa|ä)n"),
    (33, "(ia|i)n"),
    (34, "t[oö]n"),
    (38, "nen"),
    ( 5, "n"),

    # -r (32 nouns, no exceptions)
    ( 6, "( [cl]e | ide | tu )r"),
    (32, "[aä]r"),
    ( 5, "r"),

    # -s (2701 nouns, 7 exceptions)
    # could get rid of 1 exception each with these rules:
    #     -dos = 5, -[^k]ias = 41, -kaus = 40
    ( 5, "[nst]s"),
    (40, "[ioöuy][uy]s"),
    (45, "( (on|s)a | [ms]ä )s"),
    (41, "( (g|i|k|in|l|u)a | ä )s"),
    (39, "s"),

    # -C (not -n/-r/-s; 57 nouns, 3 exceptions)
    (47, "[ln][uy]t"),
    ( 5, "[cdgklmptvwx]"),
))

# rules for quadrisyllabic and longer nouns (declension, regex)
_RULES_4SYLL = tuple((d, re.compile(r + "$", re.VERBOSE)) for (d, r) in (
    # -VV (649 nouns, 5 exceptions)
    ( 3, "i[oö]"),
    (13, "(id|al|as)ea"),
    (12, "[ei]a"),

    # TODO: optimize the rest

    # -Ca (903 nouns, 34 exceptions)
    ( 9, "( [air]kka | lla | i[in]na | ssa | ta | ža )"),
    (12, "( [lnst]ija | la )"),
    (10, "[dgjkmnrsv]a"),

    # -Cä (275 nouns, 2 exceptions)
    ( 9, "tä"),
    (12, "[lnst]ijä"),
    (10, "[jmv]ä"),

    # -Ci (2282 nouns, 21 exceptions)
    (
        6,
        "( [gkp]el | [drt]um | [klnptv]ar | [dgknt]er | "
        "(i|l|s|kt|st|tt)or )i"
    ),
    ( 5, "[bdfgklmnprstvz]i"),

    # -CO/-CU (627 nouns, 19 exceptions)
    ( 2, "( m[oö] | l[uy] )"),
    ( 4, "[dgjlmnprstv]ikk[oö]"),
    ( 1, "[cdklmnrstz][oöuy]"),

    # -C (4573 nouns, 16 exceptions)
    (32, "t[aä]r"),
    (34, "t[oö]n"),
    (38, "nen(kin)?"),
    (40, "[iuy][uy]s"),
    (39, "[eioöuy]s"),
    (41, "[aä]s"),
    (47, "n[uy]t"),
    ( 5, "[dghkmnrt]"),
))

def get_declensions(noun, useExceptions=True):
    """Get the Kotus declension(s) of a Finnish noun (including adjectives/
    pronouns/numerals, excluding compounds).
    noun:          the noun in nominative singular
    useExceptions: use True except for testing purposes
    return:        a tuple of 0-2 declensions (each 1-49)"""

    assert isinstance(noun, str)

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
            print(f"Redundant exception: '{noun}'")

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
