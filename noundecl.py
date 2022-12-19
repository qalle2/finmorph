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

# nouns that have two declensions instead of one
# - format: noun: tuple of declensions in ascending order
# - start a new line when declension changes
_MULTI_DECLENSION_NOUNS = {
    # different meanings
    "lahti": (5, 7), "laki": (5, 7), "palvi": (5, 7), "ripsi": (5, 7),
    "saksi": (5, 7), "sini": (5, 7),
    "kuori": (5, 26), "viini": (5, 26), "vuori": (5, 26),
    "peitsi": (5, 30),
    "puola": (9, 10),
    "kikkara": (11, 12),
    "kuusi": (24, 27),
    "ahtaus": (39, 40), "karvaus": (39, 40), "rosvous": (39, 40),
    "siivous": (39, 40), "vakaus": (39, 40),
    "kymmenes": (39, 45),

    # same meanings
    "menu": (1, 21),
    "caddie": (3, 8),
    "alpi": (5, 7), "helpi": (5, 7), "kaihi": (5, 7), "karhi": (5, 7),
    "kymi": (5, 7), "vyyhti": (5, 7),
    "sioux": (5, 22),
    "syli": (5, 23),
    "csárdás": (5, 39), "kuskus": (5, 39),
    "ori": (5, 48),
    "kolme": (7, 8),
    "hapsi": (7, 29), "uksi": (7, 29),
    "siitake": (8, 48),
    "aneurysma": (9, 10), "kysta": (9, 10), "lyyra": (9, 10),
    "humala": (10, 11),
    "tanhua": (12, 15),
    "havas": (39, 41), "kallas": (39, 41), "koiras": (39, 41),
    "olas": (39, 41), "pallas": (39, 41), "tuomas": (39, 41), "uros": (39, 41),
}

# exceptions to rules
# - format: noun: declension
# - order: first by syllable count, then by ending, then by declension
# - start a new line when declension changes
_EXCEPTIONS = {
    # === Monosyllabic ===

    # -VV
    "brie": 21, "clou": 21,
    "hie": 48,

    # -n
    "ien": 32,
    "näin": 33, "puin": 33,
    "tain": 36,

    # -s
    "AIDS": 5,
    "hius": 39, "taus": 39,
    "ies": 41, "ruis": 41,
    "mies": 42,

    # -C (not -n/-s)
    "LED": 5,
    "show": 22,

    # === Disyllabic ===

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

    # -Ce
    "ale": 8, "bäne": 8, "deadline": 8, "folklore": 8, "forte": 8, "itse": 8,
    "jade": 8, "joule": 8, "kalle": 8, "kurre": 8, "mangrove": 8, "manne": 8,
    "nalle": 8, "pelle": 8, "penne": 8, "polle": 8, "poplore": 8, "pose": 8,
    "psyyke": 8, "quenelle": 8, "striptease": 8, "tele": 8, "vaudeville": 8,
    "bile": 20,
    "hake": 48, "hame": 48, "kare": 48,

    # -ki
    "LYHKI": 5, "sutki": 5,
    "hanki": 7, "hauki": 7, "henki": 7, "kaikki": 7, "kanki": 7, "kaski": 7,
    "kiiski": 7, "leski": 7, "onki": 7, "sääski": 7, "tuki": 7, "vaski": 7,

    # -ri
    "lieri": 5,
    "hiiri": 24, "meri": 24,
    "juuri": 26, "kaari": 26, "nuori": 26, "saari": 26, "suuri": 26,
    "sääri": 26, "ääri": 26,

    # -si
    "kreisi": 5, "mansi": 5,
    "päitsi": 7, "suitsi": 7, "suksi": 7, "sääksi": 7, "viiksi": 7,
    "vuoksi": 7,
    "kusi": 24,
    "hiisi": 27, "käsi": 27, "liesi": 27, "niisi": 27, "paasi": 27, "uusi": 27,
    "viisi": 27, "vuosi": 27,
    "lapsi": 29,
    "veitsi": 30,
    "haaksi": 31, "kaksi": 31, "yksi": 31,

    # -Ci (not -ki/-ri/-si)
    "puomi": 5, "tuoli": 5, "varvi": 5,
    "appi": 7, "haahti": 7, "happi": 7, "helmi": 7, "järvi": 7, "lehti": 7,
    "nummi": 7, "onni": 7, "ovi": 7, "polvi": 7, "saarni": 7, "salmi": 7,
    "sappi": 7, "seimi": 7, "soppi": 7, "sormi": 7, "suomi": 7, "suvi": 7,
    "torvi": 7, "tuppi": 7, "typpi": 7, "tähti": 7, "veli": 7,
    "kumpi": 16,
    "tiili": 23,
    "hiili": 24, "huuli": 24, "ruuhi": 24, "uni": 24,
    "taimi": 25,
    "niini": 26, "tuuli": 26, "tyyni": 26, "ääni": 26,

    # -CO/-CU
    "go-go": 18,
    "kung-fu": 21,
    "kiiru": 48,

    # -l
    "kennel": 5,
    "diesel": 6, "rial": 6,
    "nivel": 32, "sävel": 32,
    "seppel": 49,

    # -n
    "drive-in": 5, "kelvin": 5,
    "lumen": 6, "luumen": 6,
    "lämmin": 35,
    "alin": 36,
    "vasen": 37,
    "muren": 49, "säen": 49,

    # -r
    "sitar": 6,
    "sisar": 32, "tatar": 32, "tytär": 32,
    "udar": 49,

    # -As
    "aidas": 39, "atlas": 39, "haljas": 39, "harjas": 39, "jalas": 39,
    "juudas": 39, "kaimas": 39, "kannas": 39, "kuvas": 39, "luudas": 39,
    "madras": 39, "mullas": 39, "ohjas": 39, "priimas": 39, "sammas": 39,
    "tervas": 39, "teräs": 39, "vastas": 39, "vihdas": 39, "viinas": 39,
    "vitsas": 39, "kolmas": 45, "nollas": 45, "sadas": 45,

    # -es
    "blues": 5,
    "lehdes": 39,
    "mones": 45,

    # -is
    "kallis": 41, "raitis": 41, "tiivis": 41,

    # -AUs
    "ahnaus": 40, "harmaus": 40, "hartaus": 40, "hauraus": 40, "herraus": 40,
    "hitaus": 40, "hurskaus": 40, "irstaus": 40, "karsaus": 40, "kiivaus": 40,
    "kirkkaus": 40, "kitsaus": 40, "kuulaus": 40, "kärkkäys": 40,
    "liukkaus": 40, "maukkaus": 40, "puhtaus": 40, "raihnaus": 40,
    "rakkaus": 40, "raskaus": 40, "reippaus": 40, "riettaus": 40,
    "rikkaus": 40, "runsaus": 40, "sairaus": 40, "suulaus": 40, "työläys": 40,
    "valppaus": 40, "vapaus": 40, "varkaus": 40, "vauraus": 40, "vehmaus": 40,
    "viekkaus": 40, "vieraus": 40, "viisaus": 40, "vilkkaus": 40,
    "vuolaus": 40, "ylväys": 40,

    # -OUs
    "couscous": 5,
    "kirous": 39, "kokous": 39, "kumous": 39, "linkous": 39, "lumous": 39,
    "patous": 39, "putous": 39, "rukous": 39, "tarjous": 39,
    "lahous": 40, "mahous": 40,

    # -Us (not -AUs/-OUs)
    "kehruus": 39, "kiveys": 39, "makuus": 39, "persuus": 39, "pikeys": 39,
    "poikkeus": 39, "risteys": 39, "tyveys": 39,
    "ryntys": 41, "vantus": 41,

    # -t
    "input": 5, "output": 5,
    "beignet": 22, "bouquet": 22, "buffet": 22, "gourmet": 22, "nougat": 22,
    "parfait": 22, "ragoût": 22,
    "kevät": 44, "venät": 44,
    "tuhat": 46,

    # -C (not -l/-n/-r/-s/-t)
    "bordeaux": 22, "know-how": 22,

    # === Trisyllabic ===

    # -VV
    "feijoa": 10,
    "pallea": 12, "urea": 12,
    "media": 13,
    "brasserie": 21,

    # -ja
    "apaja": 11,
    "mantilja": 13, "papaija": 13, "vanilja": 13,

    # -la
    "chinchilla": 9, "papilla": 9, "sinsilla": 9, "tonsilla": 9,
    "hankala": 10, "jumala": 10, "kamala": 10, "katala": 10, "kavala": 10,
    "matala": 10, "nokkela": 10, "ovela": 10, "sukkela": 10, "tukala": 10,
    "apila": 13, "kampela": 13, "sikala": 13, "takila": 13,

    # -na
    "ruustinna": 9,
    "ihana": 10,
    "jellona": 11, "lattana": 11, "maruna": 11, "murena": 11, "ohrana": 11,
    "omena": 11, "sikuna": 11,
    "haapana": 12, "harppuuna": 12, "keppana": 12, "pirpana": 12,
    "aivina": 13, "arina": 13, "ipana": 13, "kahina": 13, "kohina": 13,
    "kopina": 13, "kuhina": 13, "marina": 13, "maukuna": 13, "paukkina": 13,
    "piekana": 13, "porina": 13, "rahina": 13, "ramina": 13, "reppana": 13,
    "retsina": 13, "ruutana": 13, "smetana": 13, "tuoksina": 13,

    # -ra
    "kimaira": 9, "tiaara": 9,
    "amfora": 10, "ankara": 10, "avara": 10, "kumara": 10, "kupera": 10,
    "uuttera": 10,
    "hapera": 11, "sikkara": 11, "tomera": 11,
    "kattara": 12, "littera": 12,
    "gerbera": 13, "ketara": 13, "kitara": 13, "matara": 13, "sikkura": 13,
    "tempera": 13, "vaahtera": 13,

    # -Ca (not -ja/-la/-na/-ra)
    "ekseema": 9, "nautiikka": 9,
    "huuhdonta": 10, "pomada": 10,
    "ahava": 11, "harava": 11, "hekuma": 11, "paatsama": 11,
    "paprika": 12, "passiiva": 12, "salama": 12,
    "vernissa": 13,
    "navetta": 14, "ometta": 14, "pohatta": 14,
    "cha-cha-cha": 21,

    # -Cä
    "emäntä": 10, "isäntä": 10,
    "veiterä": 11, "äpärä": 11,
    "jäkkärä": 12, "räkälä": 12, "väkkärä": 12,
    "kärinä": 13, "määkinä": 13, "mölinä": 13, "mörinä": 13, "möyrinä": 13,
    "siivilä": 13,

    # -Ce
    "ginger ale": 8, "ladylike": 8, "tabbule": 8,
    "jäntere": 48,
    "askare": 49, "askele": 49, "kantele": 49, "petkele": 49, "taipale": 49,

    # -li
    "alleeli": 5, "biennaali": 5, "fenkoli": 5, "fertiili": 5, "gerbiili": 5,
    "kajaali": 5, "konsiili": 5, "koraali": 5, "korpraali": 5, "labiili": 5,
    "lojaali": 5, "modaali": 5, "moguli": 5, "pedaali": 5, "pendeli": 5,
    "pluraali": 5, "profiili": 5, "triennaali": 5, "viriili": 5,
    "atolli": 6, "basilli": 6, "daktyyli": 6, "flanelli": 6, "gaselli": 6,
    "hotelli": 6, "konsoli": 6, "kupoli": 6, "linoli": 6, "moduuli": 6,
    "motelli": 6, "putelli": 6, "sardelli": 6, "trotyyli": 6, "vinyyli": 6,

    # -mi
    "imaami": 5, "monstrumi": 5, "oopiumi": 5, "palsami": 5,
    "atomi": 6, "entsyymi": 6, "foneemi": 6, "muslimi": 6, "pogromi": 6,
    "systeemi": 6, "toteemi": 6, "volyymi": 6,

    # -ni
    "afgaani": 5, "butaani": 5, "doktriini": 5, "etaani": 5, "eteeni": 5,
    "fibriini": 5, "gluteeni": 5, "humaani": 5, "jasmiini": 5, "joriini": 5,
    "kaimaani": 5, "karbiini": 5, "kardaani": 5, "ketoni": 5, "kiniini": 5,
    "Koraani": 5, "kretliini": 5, "lantaani": 5, "laviini": 5, "liaani": 5,
    "ligniini": 5, "mangaani": 5, "membraani": 5, "mesoni": 5, "metaani": 5,
    "migreeni": 5, "morfiini": 5, "oktaani": 5, "orgaani": 5, "otsoni": 5,
    "patiini": 5, "pepsiini": 5, "pineeni": 5, "porfiini": 5, "profaani": 5,
    "propaani": 5, "protoni": 5, "pyloni": 5, "rabbiini": 5, "retliini": 5,
    "risiini": 5, "rutiini": 5, "samaani": 5, "šamaani": 5, "sampaani": 5,
    "seireeni": 5, "strykniini": 5, "syaani": 5, "sykliini": 5, "sykloni": 5,
    "tanniini": 5, "teiini": 5, "toksiini": 5,
    "antenni": 6, "kanjoni": 6, "kommuuni": 6, "koturni": 6, "kumppani": 6,
    "monsuuni": 6, "taifuuni": 6, "tribuuni": 6,

    # -ri
    "fosfori": 5, "kefiiri": 5, "kvasaari": 5, "likvori": 5, "paapuuri": 5,
    "primaari": 5, "reviiri": 5, "tyyrpuuri": 5, "vulgaari": 5,
    "bisarri": 6, "frisyyri": 6, "kivääri": 6, "likööri": 6, "marttyyri": 6,
    "misääri": 6, "monttööri": 6, "turnyyri": 6, "valööri": 6, "vampyyri": 6,

    # -si
    "glukoosi": 6, "hampuusi": 6, "karpaasi": 6, "kolhoosi": 6, "narkoosi": 6,
    "neuroosi": 6, "pakaasi": 6, "plantaasi": 6, "poliisi": 6, "proteesi": 6,
    "refleksi": 6, "serviisi": 6, "sotiisi": 6, "sottiisi": 6, "sovhoosi": 6,
    "sypressi": 6, "trapetsi": 6, "turkoosi": 6, "ukaasi": 6, "viskoosi": 6,
    "zoonoosi": 6, "äksiisi": 6,

    # -Ci (not -li/-mi/-ni/-ri/-si)
    "etruski": 5,
    "biljardi": 6, "oliivi": 6, "sirtaki": 6, "standardi": 6, "tienesti": 6,

    # -Co
    "hampaisto": 1, "kalusto": 1, "kojeisto": 1, "koneikko": 1, "kuidusto": 1,
    "kuormasto": 1, "lainaamo": 1, "laitteisto": 1, "lajisto": 1, "lasisto": 1,
    "munkisto": 1, "murteisto": 1, "naisisto": 1, "oikeisto": 1,
    "parhaisto": 1, "pensaisto": 1, "poikaisto": 1, "pojisto": 1,
    "praktikko": 1, "raiteisto": 1, "rattaisto": 1, "ruovisto": 1,
    "ruususto": 1, "saraikko": 1, "sombrero": 1, "vaihteisto": 1, "virasto": 1,

    # -Cö
    "hyllystö": 1, "käyrästö": 1, "lehdistö": 1, "linssistö": 1, "lähistö": 1,
    "merkistö": 1, "pillistö": 1, "syvänkö": 1, "testistö": 1, "väylästö": 1,
    "ylänkö": 1,

    # -CU
    "huitaisu": 1, "kyhäily": 1,

    # -n
    "charleston": 5, "maraton": 5,
    "kumpikaan": 16, "kumpikin": 16,
    "kymmenen": 32,
    "parahin": 36,

    # -s
    "marakas": 5, "moussakas": 5,
    "tournedos": 22,
    "tuhannes": 45,

    # -C (not -n/-s)
    "CD-ROM": 5,
    "passepartout": 22, "port salut": 22,

    # === Quadrisyllabic and longer ===

    # -VV
    "adagio": 1,
    "odysseia": 9,
    "paranoia": 10,
    "politbyroo": 20, "varietee": 20,

    # -Ca
    "halveksunta": 10,
    "marihuana": 11,
    "ekliptika": 12,
    "majolika": 13,
    "estetiikka": 14, "poliklinikka": 14, "psykometriikka": 14,
    "hänenlaisensa": 38,

    # -Ce
    "bavaroise": 8, "eau de Cologne": 8, "faksimile": 8, "karaoke": 8,
    "komedienne": 8, "mezzoforte": 8, "minestrone": 8, "tagliatelle": 8,
    "tragedienne": 8, "ukulele": 8,
    "väkevöite": 48,

    # -Ci
    "follikkeli": 5, "kateederi": 5, "kollektori": 5, "kompostori": 5,
    "multippeli": 5, "varistori": 5,
    "akupunktuuri": 6, "diakoni": 6, "firaabeli": 6, "inspehtori": 6,
    "prostaglandiini": 6, "reversiibeli": 6, "revolveri": 6, "testosteroni": 6,
    "unioni": 6, "universumi": 6, "variaabeli": 6,
    "minunlaiseni": 38, "sinunlaisesi": 38,

    # -Co
    "karkaisimo": 1, "koksittamo": 1, "miljoonikko": 1, "pantomiimikko": 1,
    "papurikko": 1, "pateetikko": 1, "poleemikko": 1, "poliitikko": 1,
    "pragmaatikko": 1, "romantikko": 1, "semiootikko": 1, "uskalikko": 1,
    "katajisto": 2, "koordinaatisto": 2,
    "kanervikko": 4,

    # -Cö/-CU/-C
    "elostelu": 1, "istuskelu": 1, "petäjikkö": 1,
    "säteilytin": 33,
    "stradivarius": 39,
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
# - Don't look at more than the last four letters of the word.
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
    # TODO: these could be still optimized

    # -VV (107 nouns, 22 exceptions)
    (17, "(aa|oo|uu)"),
    (18, "[ai]i"),
    (20, "(ee|öö|yy)"),
    (21, "[aeo]y"),
    (48, "[aäou]e"),

    # -Ca (1022 nouns, 6 exceptions)
    (10, "( [ou]i | [oy] | (^|[^aei])u ) [bdfghjklmnprstv]+a"),
    ( 9, "[bdfghjklmnprsštvzž]a"),

    # -Cä (230 nouns, 3 exceptions)
    (10, "[hjklmnprstv]ä"),

    # -Ce (409 nouns, 27 exceptions)
    ( 8, "(c|[ln]d|g|ch|[ak]k|[gyz]l|[ai]m|kn|[êop]p|[aèn]r|ss)e"),
    (48, "[dhjklmnprstv]e"),

    # -Cé (4 nouns, no exceptions)
    (21, "[bprs]é"),

    # -Ci (1312 nouns, 83 exceptions)
    ( 7, """(
        (l|n|är)h | (hi|pi|e|l|än|jo|no|r|os|t|ä)k | (ni|am|ur)m
        | (ii|oi|l|m|r|ru|ä)p | (sa|ki|al|il|äl|lo|po|ar|ir|y)v
    )i"""),
    (23, "(iih|oh|uh|tul|mon)i"),
    (25, "(ie|oi|uo|lu)mi"),
    (26, "(iel|uol|ien|uon|er|ous)i"),
    (27, "(ke|me|ve|ei|to|au|su|sy|äy|öy)si"),
    (28, "[lnr]si"),
    ( 5, "[bdfghjklmnprsštvw]i"),

    # -CO/-CU (1417 nouns, 3 exceptions)
    ( 1, "[bcdfghjklmnprstvz][oöuy]"),

    # -n (242 nouns, 9 exceptions)
    ( 6, "(b|[^a]l|an|s|yt) on"),  # -on
    (32, "(h|[^y]m|s|v) en"),  # -en
    (36, "(aa|ha|nh|äh|ik|yl|en|lo|is) in"),  # -in
    (33, "(pa|[^y]i|u|ä) n"),  # -An/-in/-un
    (34, "( [aiu]to | ö )n"),  # -On
    (38, "nen"),  # -en
    ( 5, "n"),

    # -s (1451 nouns, 90 exceptions)
    (45, "(de|jä)s"),
    (40, "( [iu]u | [^v]eu | [^ch]ou | [eiöy]y )s"),
    (41, """(
        [^h]a | (er|yr|[^mr])ä | (ä|rv)e | (aa|au|uu|yy)[lmnr]i | l[mt]i
    )s"""),
    (39, "[aeiouyäö]s"),
    ( 5, "s"),

    # -C (not -n/-s; 237 nouns, 25 exceptions)
    ( 6, "( (da|e|ö)m | lup | (ga|[^gnšu]e|o)r )"),
    (47, "(ll|n)[uy]t"),
    (43, "[^o][uy]t"),
    (49, "( [mv]al | [kmn]el | [kmnv]ar | [gnu]er )"),
    ( 5, "[bcdfghklmprštx]"),
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

    # -ja/-la/-na/-ra (650 nouns, 74 exceptions)
    # (12 is a good "all the rest" declension for these)
    ( 9, "(oa|ui)la"),
    (10, "( [aou]j | (on|jo|lo|oo|ou)n | (ke|ve|t)r )a"),
    (11, "( oij | (pa|mo|ro)n | (ha|ta|b|te)r )a"),
    (13, "( (aa|ni|k|l|io)l | (ee|ai|gi|ii|en|r|lu|uu)n | (i|uu)r )a"),
    (12, "[jlnr]a"),

    # -Ca except -ja/-la/-na/-ra (854 nouns, 16 exceptions)
    # (9 and 10 are good "all the rest" declensions for these)
    (11, "( ok | (ee|t)m | os )a"),
    (13, """(
        ed | g | [aeihs]k | (ri|il|s)m | (es|t|uu)s | (e|i|is|us)t | iiv )a
    """),
    (14, "(kk|p|ott)a"),
    ( 9, "( [bdfkt] | (al|m)m | (ua|k)v | ss )a"),
    (10, "[msv]a"),

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

    # -s (2701 nouns, 4 exceptions)
    ( 5, "(do|n|s|t)s"),
    (40, "( kau | [ioöuy][uy] )s"),
    (45, "( (on|s)a | [ms]ä )s"),
    (41, "( (g|[^k]i|k|in|l|u)a | ä )s"),
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

    # -Ca (903 nouns, 8 exceptions)
    (10, """(
        o(nd|g|ij|ik|kk|nkk|ll|m|am|im|n|nn|r|s|tt) | u(d|j|m|mm|s)
        | aj | [bz]ol | (ea|ne|l)m | v
    )a"""),
    (12, "( [lnst]ij | (i|to)l )a"),
    (13, "( (a|ti|s)k | ur )a"),
    ( 9, "[djklmnrstž]a"),

    # -Cä (275 nouns, no exceptions)
    (12, "[^ö]ijä"),
    (10, "(j|m|ynt|v)ä"),
    ( 9, "tä"),

    # -Ci (2282 nouns, 19 exceptions)
    ( 6, """(
        [gkp]el | [drt]um | (ža|no)n
        | [klnptv]ar | [dgknt]er | (i|l|s|kt|st|tt)or
    )i"""),
    ( 5, "[bdfgklmnprstvz]i"),

    # -CO/-CU (627 nouns, 15 exceptions)
    ( 2, "( m[oö] | l[uy] | elo )"),
    ( 4, "[dgjlmnprst]ikk[oö]"),
    ( 1, "[cdklmnrstz][oöuy]"),

    # -s (1354 nouns, 1 exception)
    (40, "[iuy][uy]s"),
    (39, "( na | [^c]e | [ioöuy] )s"),
    (41, "[aä]s"),
    ( 5, "s"),

    # -C (not -s; 3219 nouns, 1 exception)
    ( 6, "( rum | (ga|e|cto|u)r )"),
    (32, "[aä]r"),
    (34, "t[oö]n"),
    (38, "[^o]n"),
    (47, "[uy]t"),
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
            print(f"Redundant exception: '{noun}'", file=sys.stderr)

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
