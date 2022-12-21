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

# These rules and exceptions specify how to detect the declension of a noun,
# based on how many syllables the word has (4 means 4 or more).
# Notes - rules:
#   - Format: (declension, regex); the first matching regex will determine the
#     declension.
#   - "$" is automatically appended to the regexes, so put the whole regex in
#     parentheses if necessary.
#   - No more than one rule per declension per ending (e.g. -VV).
#   - Under each ending (e.g. -VV), if rules don't depend on each other, sort
#     them by declension.
#   - Don't hunt for any single word. If the regex is e.g. [AB]C, each of AC
#     and BC must match 2 words or more. Exception: if [AB] forms a logical
#     group, like all the vowels, then only [AB]C needs to match 2 words or
#     more.
#   - Don't use capital letters or punctuation in rules; handle those words as
#     exceptions.
# Notes - exceptions:
#   - Format: word: declension.
#   - Order: first by ending, then by declension.
#   - Begin a new line when declension changes.

# rules and exceptions for monosyllabic words
_RULES_1SYLL = tuple((d, re.compile(r + "$", re.VERBOSE)) for (d, r) in (
    # -VV
    (18, r"([aeiouyäö]) (\1|i|u)"),
    (19, "(ie|uo|yö)"),
    (21, "ay"),

    # -CV
    ( 8, "[cghpstv]e"),

    # -C
    (33, "in"),
    (39, "us"),
    ( 5, "[bcdfghklnprsštxz]"),
))
_EXCEPTIONS_1SYLL = {
    # -VV
    "brie": 21, "clou": 21,
    "hie": 48,

    # -n
    "ien": 32,
    "tain": 36,

    # -s
    "AIDS": 5,
    "ies": 41, "ruis": 41,
    "mies": 42,

    # -C (not -n/-s)
    "LED": 5,
    "show": 22,
}

# rules and exceptions for disyllabic words
_RULES_2SYLL = tuple((d, re.compile(r + "$", re.VERBOSE)) for (d, r) in (
    # -VV
    (17, "(aa|oo|uu)"),
    (18, "(ai|ii)"),
    (20, "(ee|yy|öö)"),
    (21, "(ay|ey|oy)"),
    (48, "[aiouä]e"),

    # -Ca
    (10, "(oi|ui|o|^u|[^aei]u|y) [bdfghjklmnprstv]+a"),
    ( 9, "[bdfghjklmnprsštvzž]a"),

    # -Cä
    (10, "[hjklmnprstv]ä"),

    # -Ce
    ( 8, "(im|op|ss) e"),
    (48, "[cdghjklmnprstv]e"),

    # -Cé
    (21, "[bprs]é"),

    # -Ci
    ( 7, "( [lnr]h | (l|än|r|os|t|ä)k | [lmr]p | alv )i"),
    (23, "[ou]hi"),
    (25, "(ie|oi|uo) mi"),
    (26, "( (ie|uo)[ln] | er ) i"),
    (27, "( [^aeiouyäö][eouy] | [aäeö][iuy] ) si"),
    (28, "[lnr]si"),
    ( 5, "[bdfghjklmnprsštvw]i"),

    # -CO/-CU
    ( 1, "[bcdfghjklmnprstvz][oöuy]"),

    # -n
    ( 6, "[ls]on"),
    (32, "[msv]en"),
    (33, "[iuä]n"),
    (34, "[aeiouyäö]t[oö]n"),
    (38, "nen"),
    ( 5, "n"),  # must be the last one

    # -s
    (40, "( [^v]eu | ey | [ioöuy][uy] )s"),
    (41, "( [^h]a | yrä | [^jmr]ä | (aa|au|uu|yy)[lmnr]i | l[^aeiouyäö]i )s"),
    (45, "des"),
    (39, "[aeiouyäö]s"),  # must be after 40, 41, 45
    ( 5, "s"),  # must be the last one

    # -C (not -n/-s)
    ( 6, "([^n]e|o) r"),
    (32, "( vel | t[aä]r )"),
    (43, "[^n]yt"),
    (47, "[ln][uy]t"),
    (49, "[kmnv][ae][lr]"),
    ( 5, "[bcdfghklmprštx]"),  # must be the last one
))
_EXCEPTIONS_2SYLL = {
    # -VV
    "duo": 1, "trio": 1,
    "boutique": 8, "petanque": 8,
    "dia": 9, "maya": 9,
    "boa": 10,
    "hynttyy": 17,
    "frisbee": 18, "huuhaa": 18, "peeaa": 18, "puusee": 18,
    "nugaa": 20, "raguu": 20, "sampoo": 20, "trikoo": 20, "voodoo": 20,
    "fondue": 21, "reggae": 21, "tax-free": 21,

    # -CA
    "iskä": 9, "krypta": 9, "lymfa": 9, "nyintä": 9, "ryintä": 9, "suola": 9,
    "saaja": 10, "saapa": 10, "saava": 10,

    # -Ce
    "akne": 8, "ale": 8, "beige": 8, "bäne": 8, "crème fraîche": 8, "crêpe": 8,
    "deadline": 8, "folklore": 8, "forte": 8, "freestyle": 8, "genre": 8,
    "gruyère": 8, "hardware": 8, "itse": 8, "jade": 8, "jeppe": 8, "joule": 8,
    "kalle": 8, "kurre": 8, "lande": 8, "madame": 8, "mangrove": 8, "manne": 8,
    "milk shake": 8, "nalle": 8, "nukke": 8, "pelle": 8, "penne": 8,
    "polle": 8, "poplore": 8, "pose": 8, "psyyke": 8, "puzzle": 8,
    "quenelle": 8, "saame": 8, "sake": 8, "single": 8, "soft ice": 8,
    "software": 8, "striptease": 8, "tele": 8, "tilde": 8, "vaudeville": 8,
    "bile": 20,

    # -hi/-ki/-pi/-vi
    "LYHKI": 5, "orhi": 5, "sutki": 5,
    "appi": 7, "hanki": 7, "happi": 7, "hauki": 7, "henki": 7, "hiki": 7,
    "hirvi": 7, "joki": 7, "järvi": 7, "kaikki": 7, "kanki": 7, "kaski": 7,
    "kiiski": 7, "kivi": 7, "koipi": 7, "leski": 7, "lovi": 7, "läpi": 7,
    "noki": 7, "onki": 7, "ovi": 7, "parvi": 7, "piki": 7, "pilvi": 7,
    "polvi": 7, "povi": 7, "pälvi": 7, "reki": 7, "rupi": 7, "sappi": 7,
    "sarvi": 7, "savi": 7, "siipi": 7, "soppi": 7, "suvi": 7, "sääski": 7,
    "torvi": 7, "tuki": 7, "tuppi": 7, "typpi": 7, "tyvi": 7, "vaski": 7,
    "kumpi": 16,
    "riihi": 23,
    "ruuhi": 24,

    # -li/-ni/-ri
    "lieri": 5, "tuoli": 5,
    "onni": 7, "saarni": 7, "veli": 7,
    "moni": 23, "tiili": 23, "tuli": 23,
    "hiili": 24, "hiiri": 24, "huuli": 24, "meri": 24, "uni": 24,
    "juuri": 26, "kaari": 26, "niini": 26, "nuori": 26, "saari": 26,
    "suuri": 26, "sääri": 26, "tuuli": 26, "tyyni": 26, "ääni": 26, "ääri": 26,

    # -mi
    "puomi": 5,
    "helmi": 7, "nimi": 7, "nummi": 7, "nurmi": 7, "salmi": 7, "seimi": 7,
    "sormi": 7, "suomi": 7, "tammi": 7,
    "lumi": 25, "taimi": 25,

    # -si
    "desi": 5, "kreisi": 5, "mansi": 5,
    "päitsi": 7, "suitsi": 7, "suksi": 7, "sääksi": 7, "viiksi": 7,
    "vuoksi": 7,
    "kusi": 24,
    "jousi": 26,
    "hiisi": 27, "käsi": 27, "liesi": 27, "niisi": 27, "paasi": 27, "uusi": 27,
    "viisi": 27, "vuosi": 27,
    "lapsi": 29,
    "veitsi": 30,
    "haaksi": 31, "kaksi": 31, "yksi": 31,

    # -ti
    "haahti": 7, "lehti": 7, "tähti": 7,

    # -CO/-CU
    "go-go": 18,
    "kung-fu": 21,
    "kiiru": 48,

    # -n
    "dralon": 5, "drive-in": 5, "hymen": 5, "kelvin": 5, "pinyin": 5,
    "bourbon": 6, "kaanon": 6, "lumen": 6, "luumen": 6, "pyton": 6,
    "höyhen": 32,
    "hapan": 33,
    "lämmin": 35,
    "alin": 36, "enin": 36, "likin": 36, "lähin": 36, "parhain": 36,
    "sisin": 36, "taain": 36, "uloin": 36, "vanhin": 36, "ylin": 36,
    "vasen": 37,
    "muren": 49, "säen": 49,

    # -As
    "aidas": 39, "atlas": 39, "haljas": 39, "harjas": 39, "jalas": 39,
    "juudas": 39, "kaimas": 39, "kannas": 39, "kuvas": 39, "luudas": 39,
    "madras": 39, "mullas": 39, "ohjas": 39, "priimas": 39, "sammas": 39,
    "tervas": 39, "vastas": 39, "vihdas": 39, "viinas": 39, "vitsas": 39,
    "kolmas": 45, "nollas": 45, "sadas": 45, "neljäs": 45,

    # -es
    "blues": 5,
    "lehdes": 39,
    "eräs": 41, "kirves": 41, "äes": 41,
    "mones": 45,

    # -is
    "raitis": 41, "tiivis": 41,

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
    "holhous": 39, "kirous": 39, "kokous": 39, "kumous": 39, "linkous": 39,
    "lumous": 39, "nuohous": 39, "patous": 39, "putous": 39, "rukous": 39,
    "tarjous": 39, "verhous": 39,

    # -Us (not -AUs/-OUs)
    "kehruus": 39, "kiveys": 39, "makuus": 39, "persuus": 39, "pikeys": 39,
    "poikkeus": 39, "risteys": 39, "tyveys": 39,
    "ryntys": 41, "vantus": 41,

    # -C (not -n/-s)
    "kennel": 5, "košer": 5,
    "agar": 6, "diesel": 6, "edam": 6, "gallup": 6, "rial": 6, "sitar": 6,
    "tandem": 6, "ångström": 6,
    "beignet": 22, "bordeaux": 22, "bouquet": 22, "buffet": 22, "gourmet": 22,
    "know-how": 22, "nougat": 22, "parfait": 22, "ragoût": 22,
    "sisar": 32,
    "airut": 43, "ohut": 43, "olut": 43,
    "kevät": 44, "venät": 44,
    "tuhat": 46,
    "auer": 49, "penger": 49, "seppel": 49, "udar": 49,
}

# rules and exceptions for trisyllabic words
_RULES_3SYLL = tuple((d, re.compile(r + "$", re.VERBOSE)) for (d, r) in (
    # -VV
    ( 3, "(ie|oe|ao|eo|io|yo|iö)"),
    (12, "(ia|ua|iä)"),
    (15, "(ea|eä|oa)"),
    (18, "(ai|ei|ui|oo|uu)"),
    (20, "ee"),
    (48, "[uy]e"),

    # -ja/-la/-na/-ra
    # (12 is a good "all the rest" declension for these)
    (10, "( [aou]j | on?n | ker )a"),
    (11, "(pan|tar|ter)a"),
    (13, "( ll | (ee|ii|uu)n | (i|uu)r )a"),
    (12, "[jlnr]a"),

    # -Ca (not -ja/-la/-na/-ra)
    # (9 and 10 are good "all the rest" declensions for these)
    (13, "( g | [aeihs]k | ts | st )a"),
    (14, "kka"),
    ( 9, "( [bdfkt] | ss )a"),
    (10, "[msv]a"),

    # -Cä
    (11, "( päl | häm | [kt]än | (ve|kä)r )ä"),
    (12, "( ij | (i|y|mä)l | n | yr )ä"),
    (13, "s[kt]ä"),
    (14, "kkä"),
    ( 9, "ntä"),
    (10, "[jlmrsv]ä"),

    # -Ce
    ( 8, "(c|g|ill|gn|s|nt|tt) e"),
    (49, "( pel | en | (ta|va|e)r )e"),
    (48, "[dklnrt]e"),

    # -Ci
    ( 6, """(
        [^aeiouyäö]j
        | [aäeiou]l
        | ( [hrs]a | u )m
        | ( [bktv]aa | e | [dmpt]ii | [kt]o )n
        | ( [aeiouy] | [^ä]ä )r
    )i"""),
    (16, "mpi"),
    ( 5, "[bdfgjklmnprstv]i"),

    # -CO/-CU
    ( 1, "( nko | [iuy]ano | (n|ais|jis|t)to | (l|n|pis|t)tö | t[uy] )"),
    ( 4, "kk[oö]"),
    ( 2, "[cbdghjklmnrstv][oöuy]"),

    # -n
    (10, "än"),
    (33, "in"),
    (34, "t[oö]n"),
    (38, "nen"),
    ( 5, "n"),

    # -r
    ( 6, "ler"),
    (32, "[aä]r"),
    ( 5, "r"),

    # -s
    ( 5, "[^aeiouyäö]s"),
    (40, "[ioöuy][uy]s"),
    (45, "[ms][aä]s"),
    (41, "[aä]s"),
    (39, "s"),

    # -C (not -n/-r/-s)
    (47, "[ln][uy]t"),
    ( 5, "[cdgklmptvwx]"),
))
_EXCEPTIONS_3SYLL = {
    # -VV
    "feijoa": 10,
    "apnea": 12, "hebrea": 12, "heprea": 12, "idea": 12, "pallea": 12,
    "urea": 12,
    "media": 13,
    "kanapee": 18,
    "brasserie": 21,

    # -ja
    "apaja": 11,
    "mantilja": 13, "papaija": 13, "vanilja": 13,

    # -la
    "chinchilla": 9, "koala": 9, "papilla": 9, "sinsilla": 9, "tequila": 9,
    "tonsilla": 9,
    "hankala": 10, "jumala": 10, "kamala": 10, "katala": 10, "kavala": 10,
    "matala": 10, "nokkela": 10, "ovela": 10, "sukkela": 10, "tukala": 10,
    "apila": 13, "artikla": 13, "kampela": 13, "manila": 13, "sairaala": 13,
    "sikala": 13, "takila": 13, "viola": 13,

    # -ma
    "dilemma": 9, "ekseema": 9, "sialma": 9,
    "hekuma": 11, "mahatma": 11, "ödeema": 11, "paatsama": 11, "probleema": 11,
    "salama": 12,
    "karisma": 13, "maailma": 13, "suurima": 13,

    # -na
    "ruustinna": 9,
    "ihana": 10, "tsasouna": 10,
    "jellona": 11, "korona": 11, "lattana": 11, "leukoija": 11, "mammona": 11,
    "maruna": 11, "murena": 11, "ohrana": 11, "omena": 11, "sikuna": 11,
    "haapana": 12, "harppuuna": 12, "keppana": 12, "pirpana": 12,
    "aivina": 13, "aluna": 13, "arina": 13, "ipana": 13, "kahina": 13,
    "kohina": 13, "kopina": 13, "kuhina": 13, "marina": 13, "maukuna": 13,
    "paukkina": 13, "perenna": 13, "piekana": 13, "porina": 13, "rahina": 13,
    "ramina": 13, "reppana": 13, "retsina": 13, "ruutana": 13, "smetana": 13,
    "taverna": 13, "tuoksina": 13, "ukraina": 13, "vagina": 13,

    # -ra
    "kimaira": 9, "tiaara": 9,
    "amfora": 10, "ankara": 10, "avara": 10, "kovera": 10, "kumara": 10,
    "kupera": 10, "reskontra": 10, "uuttera": 10,
    "algebra": 11, "hapera": 11, "kihara": 11, "sikkara": 11, "tomera": 11,
    "kattara": 12, "littera": 12,
    "gerbera": 13, "ketara": 13, "kitara": 13, "matara": 13, "sikkura": 13,
    "tempera": 13, "vaahtera": 13,

    # -Ca (not -ja/-la/-ma/-na/-ra)
    "antiikva": 9, "canasta": 9, "guava": 9, "nautiikka": 9,
    "huuhdonta": 10, "pomada": 10,
    "ahava": 11, "harava": 11, "judoka": 11, "mimoosa": 11,
    "paprika": 12, "passiiva": 12,
    "aktiiva": 13, "lolita": 13, "meduusa": 13, "peseta": 13, "prinsessa": 13,
    "reseda": 13, "vernissa": 13,
    "navetta": 14, "ometta": 14, "pohatta": 14, "savotta": 14, "ulappa": 14,
    "cha-cha-cha": 21,

    # -Cä
    "emäntä": 10, "isäntä": 10,
    "veiterä": 11, "äpärä": 11,
    "jäkkärä": 12, "räkälä": 12, "väkkärä": 12,
    "kärinä": 13, "määkinä": 13, "mölinä": 13, "mörinä": 13, "möyrinä": 13,
    "siivilä": 13,

    # -Ce
    "à la carte": 8, "agaave": 8, "beagle": 8, "beguine": 8, "chippendale": 8,
    "cum laude": 8, "empire": 8, "ensemble": 8, "entrecôte": 8,
    "force majeure": 8, "ginger ale": 8, "karate": 8, "kurare": 8,
    "ladylike": 8, "mobile": 8, "tabbule": 8,
    "jäntere": 48,
    "askare": 49, "askele": 49, "huhmare": 49, "kantele": 49, "kyynele": 49,
    "petkele": 49, "taipale": 49,

    # -li
    "alleeli": 5, "biennaali": 5, "dipoli": 5, "fenkoli": 5, "fenoli": 5,
    "fertiili": 5, "gaeli": 5, "gerbiili": 5, "kajaali": 5, "klausuuli": 5,
    "koktaili": 5, "konsiili": 5, "koraali": 5, "korpraali": 5, "kreoli": 5,
    "labiili": 5, "lojaali": 5, "lysoli": 5, "mentoli": 5, "modaali": 5,
    "moguli": 5, "mongoli": 5, "noduuli": 5, "pedaali": 5, "pendeli": 5,
    "pluraali": 5, "podsoli": 5, "profiili": 5, "triennaali": 5, "viriili": 5,
    "atolli": 6, "basilli": 6, "daktyyli": 6, "flanelli": 6, "gaselli": 6,
    "hotelli": 6,
    "motelli": 6, "putelli": 6, "sardelli": 6, "trotyyli": 6, "vinyyli": 6,

    # -mi
    "monstrumi": 5, "oopiumi": 5, "palsami": 5,
    "atomi": 6, "entsyymi": 6, "foneemi": 6, "haaremi": 6, "keraami": 6,
    "kondomi": 6, "muslimi": 6, "pogromi": 6, "syklaami": 6, "systeemi": 6,
    "timjami": 6, "toteemi": 6, "volyymi": 6,

    # -ni
    "butaani": 5, "etaani": 5, "eteeni": 5, "gluteeni": 5, "guldeni": 5,
    "jasmiini": 5, "ketoni": 5, "lantaani": 5, "metaani": 5, "migreeni": 5,
    "oktaani": 5, "patiini": 5, "pineeni": 5, "protoni": 5, "rutiini": 5,
    "seireeni": 5,
    "antenni": 6, "banaani": 6, "bensiini": 6, "biisoni": 6, "bikini": 6,
    "bosoni": 6, "brahmaani": 6, "bramaani": 6, "delfiini": 6, "fasaani": 6,
    "floriini": 6, "germaani": 6, "gibboni": 6, "kaniini": 6, "kanjoni": 6,
    "kardoni": 6, "kommuuni": 6, "koturni": 6, "kumppani": 6, "meloni": 6,
    "monsuuni": 6, "muffini": 6, "murjaani": 6, "musliini": 6, "peijooni": 6,
    "piisoni": 6, "pingviini": 6, "popliini": 6, "posliini": 6, "praliini": 6,
    "romaani": 6, "romani": 6, "rubiini": 6, "sabloni": 6, "slogaani": 6,
    "syrjääni": 6, "taifuuni": 6, "terriini": 6, "tribuuni": 6, "trikiini": 6,
    "tulppaani": 6, "turbiini": 6, "uraani": 6, "valloni": 6, "varaani": 6,
    "vegaani": 6, "vitriini": 6, "zucchini": 6,

    # -ri
    "bordyyri": 5, "brodyyri": 5, "brosyyri": 5, "fosfori": 5, "kefiiri": 5,
    "kašmiri": 5, "kvasaari": 5, "likvori": 5, "paapuuri": 5, "porfyyri": 5,
    "primaari": 5, "reviiri": 5, "satyyri": 5, "tyyrpuuri": 5, "vulgaari": 5,
    "bisarri": 6, "kivääri": 6, "likööri": 6, "misääri": 6, "monttööri": 6,
    "valööri": 6,

    # -si
    "glukoosi": 6, "hampuusi": 6, "karpaasi": 6, "kolhoosi": 6, "narkoosi": 6,
    "neuroosi": 6, "pakaasi": 6, "plantaasi": 6, "poliisi": 6, "proteesi": 6,
    "refleksi": 6, "serviisi": 6, "sotiisi": 6, "sottiisi": 6, "sovhoosi": 6,
    "sypressi": 6, "trapetsi": 6, "turkoosi": 6, "ukaasi": 6, "viskoosi": 6,
    "zoonoosi": 6, "äksiisi": 6,

    # -Ci (not -li/-mi/-ni/-ri/-si)
    "biljardi": 6, "buzuki": 6, "kinuski": 6, "oliivi": 6, "saluki": 6,
    "sirtaki": 6, "standardi": 6, "tienesti": 6, "tsinuski": 6,

    # -Co
    "allegro": 1, "crescendo": 1, "embargo": 1, "flamenco": 1, "flamingo": 1,
    "kalusto": 1, "kojeisto": 1, "koneikko": 1, "kuidusto": 1, "kuormasto": 1,
    "lainaamo": 1, "laitteisto": 1, "lasisto": 1, "libido": 1, "munkisto": 1,
    "murteisto": 1, "naisisto": 1, "oikeisto": 1, "praktikko": 1,
    "raiteisto": 1, "rubato": 1, "ruovisto": 1, "ruususto": 1, "saraikko": 1,
    "sombrero": 1, "vaihteisto": 1, "vibrato": 1, "virasto": 1,

    # -Cö
    "hyllystö": 1, "käyrästö": 1, "lehdistö": 1, "linssistö": 1, "lähistö": 1,
    "merkistö": 1, "pillistö": 1, "pylväistö": 1, "syvänkö": 1, "testistö": 1,
    "väylästö": 1, "ylänkö": 1,

    # -CU
    "heavy": 1, "huitaisu": 1, "jiujitsu": 1, "karibu": 1, "kyhäily": 1,
    "treasury": 1,

    # -n
    "charleston": 5, "maraton": 5,
    "backgammon": 6, "donjuan": 6, "stadion": 6, "stilleben": 6, "triatlon": 6,
    "kahdeksan": 10,
    "kumpikaan": 16, "kumpikin": 16,
    "kymmenen": 32,
    "morsian": 33,
    "parahin": 36,

    # -s
    "calvados": 5, "marakas": 5, "moussakas": 5,
    "tournedos": 22,
    "ananas": 39, "iskias": 39,
    "vanhurskaus": 40,
    "miljoonas": 45, "tuhannes": 45,

    # -C (not -n/-s)
    "CD-ROM": 5,
    "freelancer": 6, "laudatur": 6, "outsider": 6,
    "passepartout": 22, "port salut": 22,
}

# rules and exceptions for quadrisyllabic and longer words
_RULES_4SYLL = tuple((d, re.compile(r + "$", re.VERBOSE)) for (d, r) in (
    # -VV
    ( 3, "i[oö]"),
    (12, "[ei]a"),
    (20, r"([aeiouyäö])\1"),

    # -Ca
    (12, "( [^o]ij | tol )a"),
    (10, "( (o.?|u)[dgjklmnrst] | aj | (ea|ne|l)m | v )a"),
    ( 9, "[djklmnrstž]a"),

    # -Cä
    (12, "[^ö]ijä"),
    (10, "(j|m|ynt|v) ä"),
    ( 9, "tä"),

    # -Ci
    ( 6,
        "( [^aeiouyäöbt]el | [^aeiouyäö]ar | [dt]er | (i|s|[^aeiouyäö]t)or )i"
    ),
    ( 5, "[bdfgklmnprstvz]i"),

    # -CO/-CU
    ( 2, "( m[oö] | l[uy] )"),
    ( 4, "[^aeiouyäö]ikk[oö]"),
    ( 1, "[cdklmnrstz][oöuy]"),

    # -s
    (40, "[iuy][uy]s"),
    (39, "[eioöuy]s"),
    (41, "[aä]s"),
    ( 5, "s"),

    # -C (not -s)
    ( 6, "[eu]r"),
    (32, "[aä]r"),
    (34, "t[oö]n"),
    (38, "[^o]n"),
    (47, "[uy]t"),
    ( 5, "[dghkmnrt]"),
))
_EXCEPTIONS_4SYLL = {
    # -VV
    "adagio": 1,
    "odysseia": 9,
    "paranoia": 10,
    "atsalea": 13, "attasea": 13, "orkidea": 13,

    # -Ca
    "akileija": 9,
    "halveksunta": 10, "kardemumma": 10, "konkkaronkka": 10,
    "marihuana": 11,
    "anoppila": 12, "ekliptika": 12,
    "karakteristika": 13, "majolika": 13, "nomenklatuura": 13,
    "psykofarmaka": 13, "skandinaaviska": 13,
    "estetiikka": 14, "poliklinikka": 14, "psykometriikka": 14,
    "hänenlaisensa": 38,

    # -Ce
    "bavaroise": 8, "eau de Cologne": 8, "faksimile": 8, "karaoke": 8,
    "komedienne": 8, "mezzoforte": 8, "minestrone": 8, "tagliatelle": 8,
    "tragedienne": 8, "ukulele": 8,
    "väkevöite": 48,

    # -ri
    "kateederi": 5, "kollektori": 5, "kompostori": 5, "rastafari": 5,
    "reseptori": 5, "varistori": 5,
    "akupunktuuri": 6, "konteineri": 6, "manageri": 6, "revolveri": 6,
    "spinaakkeri": 6, "trikolori": 6,

    # -Ci (not -ri)
    "follikkeli": 5, "multippeli": 5,
    "azerbaidžani": 6, "diakoni": 6, "firaabeli": 6, "liirumlaarumi": 6,
    "memorandumi": 6, "prostaglandiini": 6, "reversiibeli": 6,
    "testosteroni": 6, "ubikinoni": 6, "ultimaatumi": 6, "variaabeli": 6,
    "unioni": 6, "universumi": 6,
    "minunlaiseni": 38, "sinunlaisesi": 38,

    # -Co
    "karkaisimo": 1, "keliaakikko": 1, "koksittamo": 1, "miljoonikko": 1,
    "pantomiimikko": 1, "papurikko": 1, "pateetikko": 1, "poleemikko": 1,
    "poliitikko": 1, "pragmaatikko": 1, "romantikko": 1, "semiootikko": 1,
    "untuvikko": 1, "uskalikko": 1,
    "katajisto": 2, "koordinaatisto": 2, "luettelo": 2,

    # -Cö/-CU
    "elostelu": 1, "istuskelu": 1, "petäjikkö": 1,

    # -C
    "director musices": 5,
    "agar-agar": 6, "art director": 6, "liirumlaarum": 6,
    "säteilytin": 33,
    "stradivarius": 39, "trikomoonas": 39,
}

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

    syllCnt = countsyll.count_syllables(noun)

    if useExceptions:
        if syllCnt == 1:
            exceptions = _EXCEPTIONS_1SYLL
        elif syllCnt == 2:
            exceptions = _EXCEPTIONS_2SYLL
        elif syllCnt == 3:
            exceptions = _EXCEPTIONS_3SYLL
        else:
            exceptions = _EXCEPTIONS_4SYLL
        try:
            return (exceptions[noun],)
        except KeyError:
            pass

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

def _get_redundant_exceptions():
    # generate words that are unnecessarily on the exceptions list
    for excList in (
        _EXCEPTIONS_1SYLL, _EXCEPTIONS_2SYLL, _EXCEPTIONS_3SYLL,
        _EXCEPTIONS_4SYLL
    ):
        for noun in excList:
            detectedDecls = get_declensions(noun, False)
            if detectedDecls and excList[noun] == list(detectedDecls)[0]:
                yield noun

def main():
    for noun in _get_redundant_exceptions():
        print(f"Redundant exception: '{noun}'", file=sys.stderr)

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
