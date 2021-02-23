"""Get the Kotus conjugation class of a Finnish noun.
Note: A = a/ä, O = o/ö, U = u/y, V = any vowel, C = any consonant"""

import re
import sys

# a typical noun in each class, in nominative/genitive/partitive singular (from Kotus)
CLASS_DESCRIPTIONS = {
    1:  ("valo",      "valon",        "valoa"),
    2:  ("palvelu",   "palvelun",     "palvelua"),
    3:  ("valtio",    "valtion",      "valtiota"),
    4:  ("laatikko",  "laatikon",     "laatikkoa"),
    5:  ("risti",     "ristin",       "ristiä"),
    6:  ("paperi",    "paperin",      "paperia"),
    7:  ("ovi",       "oven",         "ovea"),
    8:  ("nalle",     "nallen",       "nallea"),
    9:  ("kala",      "kalan",        "kalaa"),
    10: ("koira",     "koiran",       "koiraa"),
    11: ("omena",     "omenan",       "omenaa"),
    12: ("kulkija",   "kulkijan",     "kulkijaa"),
    13: ("katiska",   "katiskan",     "katiskaa"),
    14: ("solakka",   "solakan",      "solakkaa"),
    15: ("korkea",    "korkean",      "korkea(t)a"),
    16: ("vanhempi",  "vanhemman",    "vanhempaa"),
    17: ("vapaa",     "vapaan",       "vapaata"),
    18: ("maa",       "maan",         "maata"),
    19: ("suo",       "suon",         "suota"),
    20: ("filee",     "fileen",       "fileetä"),
    21: ("rosé",      "rosén",        "roséta"),
    22: ("parfait",   "parfait'n",    "parfait'ta"),
    23: ("tiili",     "tiilen",       "tiiltä"),
    24: ("uni",       "unen",         "unta"),
    25: ("toimi",     "toimen",       "tointa/toimea"),
    26: ("pieni",     "pienen",       "pientä"),
    27: ("käsi",      "käden",        "kättä"),
    28: ("kynsi",     "kynnen",       "kynttä"),
    29: ("lapsi",     "lapsen",       "lasta"),
    30: ("veitsi",    "veitsen",      "veistä"),
    31: ("kaksi",     "kahden",       "kahta"),
    32: ("sisar",     "sisaren",      "sisarta"),
    33: ("kytkin",    "kytkimen",     "kytkintä"),
    34: ("onneton",   "onnettoman",   "onnetonta"),
    35: ("lämmin",    "lämpimän",     "lämmintä"),
    36: ("sisin",     "sisimmän",     "sisintä"),
    37: ("vasen",     "vasemman",     "vasenta/vasempaa"),
    38: ("nainen",    "naisen",       "naista"),
    39: ("vastaus",   "vastauksen",   "vastausta"),
    40: ("kalleus",   "kalleuden",    "kalleutta"),
    41: ("vieras",    "vieraan",      "vierasta"),
    42: ("mies",      "miehen",       "miestä"),
    43: ("ohut",      "ohuen",        "ohutta"),
    44: ("kevät",     "kevään",       "kevättä"),
    45: ("kahdeksas", "kahdeksannen", "kahdeksatta"),
    46: ("tuhat",     "tuhannen",     "tuhatta"),
    47: ("kuollut",   "kuolleen",     "kuollutta"),
    48: ("hame",      "hameen",       "hametta"),
    49: ("askel(e)",  "askele(e)n",   "askel(et)ta"),
}

# noun: tuple with one or more conjugation classes
EXCEPTIONS = {
    # multiple conjugation classes, different meaning
    # incomplete list!
    "sini": (5, 7),

    # multiple conjugation classes, same meaning
    #
    "alpi":   (5, 7),
    "helpi":  (5, 7),
    "kaihi":  (5, 7),
    "karhi":  (5, 7),
    "kymi":   (5, 7),
    "vyyhti": (5, 7),
    #
    "csárdás": (5, 39),
    "kuskus":  (5, 39),
    #
    "hapsi": (7, 29),
    "uksi":  (7, 29),
    #
    "aneurysma": (9, 10),
    "kysta":     (9, 10),
    "lyyra":     (9, 10),
    #
    "merirosvous": (39, 40),
    "rosvous":     (39, 40),
    "siivous":     (39, 40),
    #
    "havas":  (39, 41),
    "kallas": (39, 41),
    "koiras": (39, 41),
    "olas":   (39, 41),
    "pallas": (39, 41),
    "uros":   (39, 41),
    #
    "menu":    (1, 21),
    "caddie":  (3, 8),
    "sioux":   (5, 22),
    "syli":    (5, 23),
    "ori":     (5, 48),
    "kolme":   (7, 8),
    "siitake": (8, 48),
    "humala":  (10, 11),
    "tanhua":  (12, 15),

    # class 1
    # -Vo
    "adagio": (1,),
    "duo": (1,),
    "trio": (1,),
    # -Co
    "osso buco": (1,),
    "ouzo": (1,),
    "taco": (1,),

    # class 3
    # -ie
    "collie": (3,),
    "lassie": (3,),
    "zombie": (3,),

    # class 5
    # -V/-VC (C = l/n/r/s/t)
    "becquerel": (5,),
    "cocktail": (5,),
    "gospel": (5,),
    "kennel": (5,),
    "mansi": (5,),
    "mosel": (5,),
    "soul": (5,),
    # other
    "borštš": (5,),
    "bungalow": (5,),
    "chips": (5,),
    "copyright": (5,),
    "design": (5,),
    "jazz": (5,),
    "jiddiš": (5,),
    "slivovits": (5,),
    "stroganov": (5,),

    # class 6
    # -l
    "diesel": (6,),
    "rial": (6,),
    # -m
    "edam": (6,),
    "liirumlaarum": (6,),
    "tandem": (6,),
    "ångström": (6,),
    # -p
    "gallup": (6,),

    # class 8
    # -ue
    "boutique": (8,),
    "petanque": (8,),

    # class 9
    # -Va
    "dia": (9,),
    "maya": (9,),
    "odysseia": (9,),
    # -ja
    "akileija": (9,),
    "dreija": (9,),
    "faija": (9,),
    "keija": (9,),
    "leija": (9,),
    "maija": (9,),
    "papukaija": (9,),
    "sija": (9,),
    "tyyssija": (9,),
    # -Vka
    "leuka": (9,),
    # -akka
    "almanakka": (9,),
    "avotakka": (9,),
    "bitumilakka": (9,),
    "hartsilakka": (9,),
    "hiuslakka": (9,),
    "japaninlakka": (9,),
    "kakka": (9,),
    "kangaspakka": (9,),
    "kirjelakka": (9,),
    "korjauslakka": (9,),
    "korttipakka": (9,),
    "krappilakka": (9,),
    "kultalakka": (9,),
    "kynsilakka": (9,),
    "kyyhkyslakka": (9,),
    "käsipakka": (9,),
    "lakka": (9,),
    "lehtijousipakka": (9,),
    "metallilakka": (9,),
    "oksalakka": (9,),
    "pakka": (9,),
    "palsternakka": (9,),
    "polttolakka": (9,),
    "pronssilakka": (9,),
    "rakka": (9,),
    "sakka": (9,),
    "selluloosalakka": (9,),
    "sinettilakka": (9,),
    "suojalakka": (9,),
    "takka": (9,),
    "vakka": (9,),
    "vesivaippatakka": (9,),
    # -Cikka
    "fikka": (9,),
    "flikka": (9,),
    "harmonikka": (9,),
    "hikka": (9,),
    "kikka": (9,),
    "likka": (9,),
    "plikka": (9,),
    "prikka": (9,),
    "rikka": (9,),
    "tikka": (9,),
    # -hka
    "leuhka": (9,),
    "reuhka": (9,),
    "tauhka": (9,),
    "viuhka": (9,),
    # -skA
    "haaska": (9,),
    "iskä": (9,),
    "paska": (9,),
    # -AmA
    "dalai-lama": (9,),
    "draama": (9,),
    "kama": (9,),
    "laama": (9,),
    "lama": (9,),
    "naama": (9,),
    "panoraama": (9,),
    "sama": (9,),
    "talouslama": (9,),
    # -ema
    "ekseema": (9,),
    "skeema": (9,),
    "teema": (9,),
    "teoreema": (9,),
    "treema": (9,),
    # -uma
    "auma": (9,),
    "lauma": (9,),
    "reuma": (9,),
    "sauma": (9,),
    "trauma": (9,),
    # -Cma
    "halma": (9,),
    "helma": (9,),
    "ilma": (9,),
    "kalma": (9,),
    "magma": (9,),
    "paradigma": (9,),
    "sialma": (9,),
    "sigma": (9,),
    "stigma": (9,),
    # -ppa
    "kauppa": (9,),
    # -sa
    "aisa": (9,),
    "kiusa": (9,),
    # -tA
    "aortta": (9,),
    "kajuutta": (9,),
    "krypta": (9,),
    "valuutta": (9,),
    "ympärystä": (9,),
    # -vA
    "hauva": (9,),
    "sauva": (9,),
    "vauva": (9,),

    # class 10
    # -Va
    "boa": (10,),
    "feijoa": (10,),
    "paranoia": (10,),
    # -jA
    "ehjä": (10,),
    "neljä": (10,),
    "rähjä": (10,),
    "väljä": (10,),
    "äijä": (10,),
    # -oikka/-uikka
    "hoikka": (10,),
    "huikka": (10,),
    "kuikka": (10,),
    "loikka": (10,),
    "luikka": (10,),
    "roikka": (10,),
    "suikka": (10,),
    "topparoikka": (10,),
    "troikka": (10,),
    "voikka": (10,),
    # -UkkA
    "houkka": (10,),
    "hukka": (10,),
    "häikkä": (10,),
    "jukka": (10,),
    "jöröjukka": (10,),
    "kukka": (10,),
    "kääkkä": (10,),
    "läikkä": (10,),
    "moukka": (10,),
    "mykkä": (10,),
    "nukka": (10,),
    "ruisrääkkä": (10,),
    "rukka": (10,),
    "räikkä": (10,),
    "soukka": (10,),
    "sukka": (10,),
    "tiskijukka": (10,),
    "toukka": (10,),
    "tukka": (10,),
    # -Cka (C != h/k)
    "huiska": (10,),
    "luiska": (10,),
    "vodka": (10,),
    # -imA
    "emintimä": (10,),
    "perimä": (10,),
    "piimä": (10,),
    "pykimä": (10,),
    "suuntima": (10,),
    "äimä": (10,),
    # -CmA
    "härmä": (10,),
    "kuisma": (10,),
    "käsikähmä": (10,),
    "lehmä": (10,),
    "nystermä": (10,),
    "pengermä": (10,),
    "rähmä": (10,),
    "sikermä": (10,),
    "särmä": (10,),
    "ämmä": (10,),
    # -pa
    "aikaansaapa": (10,),
    # -ta
    "halveksunta": (10,),
    "huuhdonta": (10,),
    "kunta": (10,),
    "musta": (10,),
    "punta": (10,),
    "pusta": (10,),
    "sonta": (10,),
    "suunta": (10,),
    # -Vtä
    "hätä": (10,),
    "itä": (10,),
    "mätä": (10,),
    "näätä": (10,),
    "setä": (10,),
    # -Ctä
    "emäntä": (10,),
    "hyväksyntä": (10,),
    "häntä": (10,),
    "isäntä": (10,),
    "kenttä": (10,),
    "lyhyenläntä": (10,),
    "mäntä": (10,),
    "pärstä": (10,),
    "räntä": (10,),
    "väheksyntä": (10,),
    "vähäläntä": (10,),
    "vähänläntä": (10,),
    # -n
    "kahdeksan": (10,),
    "seitsemän": (10,),
    "yhdeksän": (10,),

    # class 11
    # -ja
    "leukoija": (11,),
    # -ka
    "judoka": (11,),
    # -mA
    "hekuma": (11,),
    "kärhämä": (11,),
    "mahatma": (11,),
    "paatsama": (11,),
    "probleema": (11,),
    "ödeema": (11,),
    # -Vsa
    "mimoosa": (11,),

    # class 12
    # -Cja
    "espanja": (12,),
    "kampanja": (12,),
    "kanalja": (12,),
    "kastanja": (12,),
    "persilja": (12,),
    "samppanja": (12,),
    # -ua
    "herttua": (12,),
    "juolua": (12,),
    "liettua": (12,),
    "porstua": (12,),
    "saippua": (12,),
    # -iä
    "hipiä": (12,),
    "miniä": (12,),
    "nieriä": (12,),
    "näsiä": (12,),
    "päkiä": (12,),
    # -ika
    "ekliptika": (12,),
    "paprika": (12,),
    # -ma
    "salama": (12,),

    # class 13
    # -ea
    "atsalea": (13,),
    "attasea": (13,),
    "orkidea": (13,),
    # -ia
    "media": (13,),
    # -ja
    "mantilja": (13,),
    "papaija": (13,),
    "vanilja": (13,),
    # -Vka
    "heteka": (13,),
    "karakteristika": (13,),
    "majolika": (13,),
    "musaka": (13,),
    "psykofarmaka": (13,),
    "replika": (13,),
    "toonika": (13,),
    "tunika": (13,),
    # -hka
    "karahka": (13,),
    "revohka": (13,),
    # -skA
    "fingelska": (13,),
    "fingliska": (13,),
    "haarniska": (13,),
    "katiska": (13,),
    "latuska": (13,),
    "leiviskä": (13,),
    "läpyskä": (13,),
    "maatuska": (13,),
    "mormyska": (13,),
    "räpiskä": (13,),
    "rötiskä": (13,),
    "sakuska": (13,),
    "sapiska": (13,),
    "sapuska": (13,),
    "skandinaaviska": (13,),
    "säämiskä": (13,),
    "valmuska": (13,),
    # -ma
    "karisma": (13,),
    "maailma": (13,),
    "suurima": (13,),
    # -sa
    "karitsa": (13,),
    "kurmitsa": (13,),
    "kurpitsa": (13,),
    "lakritsa": (13,),
    "lavitsa": (13,),
    "meduusa": (13,),
    "prinsessa": (13,),
    "vaskitsa": (13,),
    "vernissa": (13,),
    # -tA
    "lolita": (13,),
    "peseta": (13,),
    "päällystä": (13,),
    "sofista": (13,),

    # class 14
    # -ekka/-okka
    "kopeekka": (14,),
    "lahokka": (14,),
    # -iikka
    "epiikka": (14,),
    "estetiikka": (14,),
    "etiikka": (14,),
    "fysiikka": (14,),
    "gotiikka": (14,),
    "grafiikka": (14,),
    "komiikka": (14,),
    "logiikka": (14,),
    "lyriikka": (14,),
    "magiikka": (14,),
    "metriikka": (14,),
    "mimiikka": (14,),
    "mystiikka": (14,),
    "optiikka": (14,),
    "plastiikka": (14,),
    "praktiikka": (14,),
    "psykometriikka": (14,),
    "rustiikka": (14,),
    "rytmiikka": (14,),
    "statiikka": (14,),
    "taktiikka": (14,),
    "tekniikka": (14,),
    "tragiikka": (14,),
    # -CkkA
    "karonkka": (14,),
    "kämmekkä": (14,),
    "mahorkka": (14,),
    "marsalkka": (14,),
    "masurkka": (14,),
    "ötökkä": (14,),
    # -ppa
    "ulappa": (14,),
    # -tta
    "navetta": (14,),
    "ometta": (14,),
    "pohatta": (14,),
    "savotta": (14,),

    # class 15
    "ainoa": (15,),

    # class 18
    # -VV
    "frisbee": (18,),
    "gnuu": (18,),
    "huuhaa": (18,),
    "jää": (18,),
    "jöö": (18,),
    "kanapee": (18,),
    "kuu": (18,),
    "kyy": (18,),
    "köö": (18,),
    "luu": (18,),
    "maa": (18,),
    "munaskuu": (18,),
    "muu": (18,),
    "pee": (18,),
    "peeaa": (18,),
    "pelakuu": (18,),
    "puu": (18,),
    "puusee": (18,),
    "pyy": (18,),
    "pää": (18,),
    "rokokoo": (18,),
    "suu": (18,),
    "syy": (18,),
    "sää": (18,),
    "tau": (18,),
    "tee": (18,),
    "tenkkapoo": (18,),
    "tiu": (18,),
    # other
    "go-go": (18,),

    # class 19
    # -VV
    "suo": (19,),
    "tie": (19,),
    "työ": (19,),
    "vuo": (19,),
    "vyö": (19,),
    "yö": (19,),

    # class 20
    # -VV
    "fondyy": (20,),
    "menyy": (20,),
    "miljöö": (20,),
    "nugaa": (20,),
    "politbyroo": (20,),
    "raguu": (20,),
    "revyy": (20,),
    "sampoo": (20,),
    "trikoo": (20,),
    "voodoo": (20,),

    # class 21
    # -Ve
    "brasserie": (21,),
    "brie": (21,),
    "fondue": (21,),
    "reggae": (21,),
    "tax-free": (21,),
    # -Vy
    "cowboy": (21,),
    "gay": (21,),
    "gray": (21,),
    "jersey": (21,),
    "jockey": (21,),
    "maahockey": (21,),
    "playboy": (21,),
    "speedway": (21,),
    "spray": (21,),
    # other
    "cha-cha-cha": (21,),
    "clou": (21,),
    "kung-fu": (21,),

    # class 22
    # -t
    "beignet": (22,),
    "bouquet": (22,),
    "buffet": (22,),
    "gourmet": (22,),
    "nougat": (22,),
    "parfait": (22,),
    "passepartout": (22,),
    "port salut": (22,),
    "ragoût": (22,),
    # other
    "bordeaux": (22,),
    "know-how": (22,),
    "show": (22,),
    "tournedos": (22,),

    # class 25 (all)
    "liemi": (25,),
    "loimi": (25,),
    "lumi": (25,),
    "luomi": (25,),
    "niemi": (25,),
    "taimi": (25,),
    "toimi": (25,),
    "tuomi": (25,),

    # class 26
    "jousi": (26,),

    # class 29
    "lapsi": (29,),

    # class 30 (all)
    "peitsi": (30,),
    "veitsi": (30,),

    # class 31 (all)
    "haaksi": (31,),
    "kaksi": (31,),
    "yksi": (31,),

    # class 32
    "nivel": (32,),
    "sävel": (32,),

    # class 33
    "hapan": (33,),
    "istuin": (33,),
    "laidun": (33,),
    "morsian": (33,),
    "puin": (33,),
    "sydän": (33,),

    # class 34
    "alaston": (34,),

    # class 35 (all)
    "lämmin": (35,),

    # class 36 (all)
    "alin": (36,),
    "enin": (36,),
    "likin": (36,),
    "lähin": (36,),
    "parahin": (36,),
    "parhain": (36,),
    "sisin": (36,),
    "taain": (36,),
    "tain": (36,),
    "uloin": (36,),
    "vanhin": (36,),
    "ylin": (36,),

    # class 37 (all)
    "vasen": (37,),

    # class 38
    "hänenlaisensa": (38,),

    # class 39
    # -eUs
    "fariseus": (39,),
    "kiveys": (39,),
    "loveus": (39,),
    "pikeys": (39,),
    "poikkeus": (39,),
    "risteys": (39,),
    "saddukeus": (39,),
    "saveus": (39,),
    "tyveys": (39,),
    # other
    "hius": (39,),
    "makuus": (39,),
    "stradivarius": (39,),

    # class 41
    # -is
    "altis": (41,),
    "aulis": (41,),
    "kallis": (41,),
    "kaunis": (41,),
    "kauris": (41,),
    "nauris": (41,),
    "raitis": (41,),
    "ruis": (41,),
    "ruumis": (41,),
    "saalis": (41,),
    "tiivis": (41,),
    "tyyris": (41,),
    "valmis": (41,),
    # other
    "ies": (41,),
    "kirves": (41,),
    "vantus": (41,),
    "äes": (41,),

    # class 42 (all)
    "mies": (42,),

    # class 43 (all)
    # -Ut
    "airut": (43,),
    "ehyt": (43,),
    "immyt": (43,),
    "kevyt": (43,),
    "kytkyt": (43,),
    "kätkyt": (43,),
    "lyhyt": (43,),
    "neitsyt": (43,),
    "ohut": (43,),
    "olut": (43,),
    "pehmyt": (43,),
    "tiehyt": (43,),

    # class 44 (all)
    "kevät": (44,),
    "venät": (44,),

    # class 45 (all)
    # -As
    "kahdeksas": (45,),
    "kolmas": (45,),
    "miljoonas": (45,),
    "neljäs": (45,),
    "nollas": (45,),
    "sadas": (45,),
    "seitsemäs": (45,),
    "yhdeksäs": (45,),
    # -es
    "kahdeksaskymmenes": (45,),
    "kahdes": (45,),
    "kahdeskymmenes": (45,),
    "kolmaskymmenes": (45,),
    "kuudes": (45,),
    "kuudeskymmenes": (45,),
    "kymmenes": (45,),
    "mones": (45,),
    "neljäskymmenes": (45,),
    "seitsemäskymmenes": (45,),
    "tuhannes": (45,),
    "viides": (45,),
    "viideskymmenes": (45,),
    "yhdeksäskymmenes": (45,),
    "yhdes": (45,),

    # class 46 (all)
    "tuhat": (46,),

    # class 47
    # -lUt
    "kuollut": (47,),
    "tervetullut": (47,),
    "täysinpalvellut": (47,),

    # class 48
    # -Ve
    "aie": (48,),
    "hie": (48,),
    "koe": (48,),
    "säie": (48,),
    # other
    "kiiru": (48,),

    # class 49
    # -l
    "sammal": (49,),
    "taival": (49,),
    # -n
    "muren": (49,),
    "säen": (49,),
    # -e
    "hepene": (49,),
    "murene": (49,),
    "säkene": (49,),
    "taipale": (49,),
}

# conjugation class, regex
ENDINGS = (
    # note: each part of each rule must apply to at least three words!
    # (the rest are listed as exceptions)

    # foreign final consonant(s)
    (5,  r"[bcdfghkmpx]$"),    # -C (C != l/n/r/s/t)
    (5,  r"[klnrs][lnrst]$"),  # -CC (2nd C = l/n/r/s/t)

    # -ia
    (12, "ia$"),

    # -CA (C = at least k/m/p/s/t and mostly j/v)
    #
    # general rule: class 9 if 2nd-to-last vowel is unrounded (A/e/i)
    (10, r"aisa$"),                           # exception
    (10, r"[oöu]i[jkmpst][aä]$"),             # exception
    (10, r"[aäe][jmv][aä]$"),                 # exception
    (10, r"iv[aä]$"),                         # exception
    (10, r"lm[aä]$"),                         # exception
    (10, r"[äe][lnr]kkä$"),                   # exception
    (10, r"[äei][hlmnrt]?[ps]?[kps]ä$"),      # exception
    (12, r"i[jn][aä]$"),                      # exception
    (13, r"aska$"),                           # exception
    (14, r"[^aei][aiuy]kka$"),                # exception
    (14, r"[äi]kkä$"),                        # exception
    (9,  r"[aäei][fhjklmnprstv]{1,3}[aä]$"),  # rule
    #
    # general rule: class 10 if 2nd-to-last vowel is rounded (O/U)
    (9,  r"[ai]u[kst]?[kt]a$"),               # exception
    (9,  r"[ou]nta$"),                        # exception
    (9,  r"[öy]ntä$"),                        # exception
    (13, r"usta$"),                           # exception
    (14, r"[^äöy]ykkä$"),                     # exception
    (10, r"[oöuy][fhjklmnprstv]{1,3}[aä]$"),  # rule

    # -CCO/-CCU
    (4,  r"kk[oö]$"),                                 # -kkO
    (1,  r"[^aeiouyäö][^aeiouyäö][ouyö]$"),           # -CCO/-CCU

    (3,  r"(oe|[aeiy]o|iö)$"),                        # -oe/-ao/-eo/-iO/-yo
    (17, r"(aa|oo)$"),                                # -aa/-oo
    (21, r"é$"),                                      # -é
    (28, r"[lnr]si$"),                                # -Csi
    (34, r"[aeiouyäö]t[oö]n$"),                       # -VtOn
    (38, r"nen$"),                                    # -nen
    (39, r"[^eiouyö][uy]s$"),                         # -AUs/-CUs
    (40, r"[eiouyö][uy]s$"),                          # -eUs/-iUs/-OUs/-UUs
    (41, r"[dghjklmnprstv][aä]s$"),                   # -CAs
    (47, r"n[uy]t$"),                                 # -nUt
    (48, r"ae$"),                                     # -ae
    (49, r"el$"),                                     # -el
)

def get_noun_class(noun, useExceptions=True):
    """noun: a Finnish noun in nominative singular
    return: a tuple of zero, one or two Kotus conjugation classes (1...49)"""

    if useExceptions:
        try:
            return EXCEPTIONS[noun]
        except KeyError:
            pass

    for (conjugation, regex) in ENDINGS:
        if re.search(regex, noun) is not None:
            return (conjugation,)

    return ()

def check_redundant_exceptions():
    """Are there redundant exceptions (same conjugation class as the rules would indicate)?"""

    for noun in EXCEPTIONS:
        if EXCEPTIONS[noun] == get_noun_class(noun, False):
            print(f"Redundant exception: '{noun}'")

def main():
    check_redundant_exceptions()

    if len(sys.argv) != 2:
        sys.exit(
            "Get Kotus conjugation class(es) of a Finnish noun. "
            "Argument: noun in nominative singular"
        )
    noun = sys.argv[1]

    conjugations = get_noun_class(noun)
    if len(conjugations) == 0:
        sys.exit("Unrecognized noun.")
    for c in conjugations:
        (nom, gen, part) = CLASS_DESCRIPTIONS[c]
        print(f"class {c} (like '{nom}' (genitive '{gen}', partitive '{part}'))")

if __name__ == "__main__":
    main()
