"""Get the Kotus conjugation class of a Finnish noun.
Note: A = a/ä, O = o/ö, U = u/y, V = any vowel, C = any consonant"""

import re
import sys

# conjugated correctly: -VV/-A/-e

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
    "kikkara": (11, 12),
    "kuusi": (24, 27),
    "sini": (5, 7),
    "puola": (9, 10),
    "vuori": (5, 26),

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
    # -VV
    "adagio": (1,),
    "duo": (1,),
    "trio": (1,),
    # -Co
    "ouzo": (1,),
    "taco": (1,),

    # class 3
    "aaloe": (3,),
    "collie": (3,),
    "lassie": (3,),
    "oboe": (3,),
    "zombie": (3,),

    # class 5
    "becquerel": (5,),
    "cocktail": (5,),
    "gospel": (5,),
    "kennel": (5,),
    "mosel": (5,),
    "soul": (5,),

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
    # -VV
    "boutique": (8,),
    "petanque": (8,),
    # -Ce (native)
    "ale": (8,),
    "itse": (8,),
    "jeppe": (8,),
    "kalle": (8,),
    "kellokalle": (8,),
    "kurre": (8,),
    "lande": (8,),
    "manne": (8,),
    "nalle": (8,),
    "nasse": (8,),
    "nisse": (8,),
    "nukke": (8,),
    "ope": (8,),
    "pelle": (8,),
    "polle": (8,),
    "pose": (8,),
    "toope": (8,),
    # -Ce (loans)
    "agaave": (8,),
    "akne": (8,),
    "à la carte": (8,),
    "andante": (8,),
    "bavaroise": (8,),
    "beagle": (8,),
    "beguine": (8,),
    "bouillabaisse": (8,),
    "bourette": (8,),
    "bourgogne": (8,),
    "byte": (8,),
    "charlotte russe": (8,),
    "chenille": (8,),
    "chippendale": (8,),
    "crème fraîche": (8,),
    "crêpe": (8,),
    "cum laude": (8,),
    "deadline": (8,),
    "duchesse": (8,),
    "empire": (8,),
    "ensemble": (8,),
    "entrecôte": (8,),
    "faksimile": (8,),
    "folklore": (8,),
    "force majeure": (8,),
    "forte": (8,),
    "freestyle": (8,),
    "genre": (8,),
    "ginger ale": (8,),
    "grape": (8,),
    "gruyère": (8,),
    "hardware": (8,),
    "house": (8,),
    "jade": (8,),
    "jive": (8,),
    "joule": (8,),
    "karaoke": (8,),
    "karate": (8,),
    "komedienne": (8,),
    "kurare": (8,),
    "ladylike": (8,),
    "lasagne": (8,),
    "lime": (8,),
    "madame": (8,),
    "mangrove": (8,),
    "mezzoforte": (8,),
    "milk shake": (8,),
    "minestrone": (8,),
    "mobile": (8,),
    "mousse": (8,),
    "open house": (8,),
    "penne": (8,),
    "poplore": (8,),
    "poste restante": (8,),
    "promille": (8,),
    "psyyke": (8,),
    "puzzle": (8,),
    "quenelle": (8,),
    "quiche": (8,),
    "raclette": (8,),
    "ragtime": (8,),
    "ratatouille": (8,),
    "ringette": (8,),
    "saame": (8,),
    "sake": (8,),
    "single": (8,),
    "software": (8,),
    "striptease": (8,),
    "tabbule": (8,),
    "tagliatelle": (8,),
    "tele": (8,),
    "tilde": (8,),
    "tragedienne": (8,),
    "ukulele": (8,),
    "vaudeville": (8,),
    "vinaigrette": (8,),

    # class 9
    # -VV
    "dia": (9,),
    "maya": (9,),
    "odysseia": (9,),
    # -da
    "sekunda": (9,),
    # -fa
    "lymfa": (9,),
    # -ja
    "akileija": (9,),
    "dreija": (9,),
    "faija": (9,),
    "keija": (9,),
    "laaja": (9,),
    "leija": (9,),
    "maija": (9,),
    "maja": (9,),
    "paja": (9,),
    "papukaija": (9,),
    "raaja": (9,),
    "sija": (9,),
    "taaja": (9,),
    "tyyssija": (9,),
    "vaja": (9,),
    # -ka
    "avotakka": (9,),
    "flikka": (9,),
    "harmonikka": (9,),
    "iskä": (9,),
    "plikka": (9,),
    "prikka": (9,),
    "sekamelska": (9,),
    "vesivaippatakka": (9,),
    # -la
    "hopeahela": (9,),
    "suola": (9,),
    # -ma
    "dalai-lama": (9,),
    "liesma": (9,),
    "talouslama": (9,),
    # -na
    "ballerina": (9,),
    "ikebana": (9,),
    "lapsenkina": (9,),
    "medisiina": (9,),
    "okariina": (9,),
    # -pa
    "kauppa": (9,),
    # -sa
    "mykorritsa": (9,),
    # -ta
    "aortta": (9,),
    "kajuutta": (9,),
    "krypta": (9,),
    "valuutta": (9,),
    "ympärystä": (9,),
    # -va
    "aava": (9,),
    "eeva": (9,),
    "guava": (9,),
    "iva": (9,),
    "kaava": (9,),
    "kiva": (9,),
    "klaava": (9,),
    "laava": (9,),
    "lava": (9,),
    "naava": (9,),
    "neva": (9,),
    "niva": (9,),
    "pehva": (9,),
    "terva": (9,),

    # class 10
    # -da
    "pomada": (10,),
    # -ja
    "nauraja": (10,),
    # -ka
    "jöröjukka": (10,),
    "tiskijukka": (10,),
    # -lA
    "gorgonzola": (10,),
    "hankala": (10,),
    "hintelä": (10,),
    "hyperbola": (10,),
    "jumala": (10,),
    "jäkälä": (10,),
    "kamala": (10,),
    "karambola": (10,),
    "katala": (10,),
    "kavala": (10,),
    "matala": (10,),
    "nokkela": (10,),
    "pykälä": (10,),
    "sukkela": (10,),
    "tukala": (10,),
    "vetelä": (10,),
    "vikkelä": (10,),
    "äitelä": (10,),
    # -ma
    "avauma": (10,),
    "siunaama": (10,),
    "virtaama": (10,),
    # -nA
    "ihana": (10,),
    "kruuna": (10,),
    "kränä": (10,),
    "yliminä": (10,),
    # -pa
    "aikaansaapa": (10,),
    # -ra
    "ahkera": (10,),
    "ankara": (10,),
    "avara": (10,),
    "eripura": (10,),
    "katkera": (10,),
    "koira": (10,),
    "kovera": (10,),
    "kumara": (10,),
    "kupera": (10,),
    "uuttera": (10,),
    # -tA
    "emäntä": (10,),
    "halveksunta": (10,),
    "huuhdonta": (10,),
    "hyväksyntä": (10,),
    "isäntä": (10,),
    "lyhyenläntä": (10,),
    "noita": (10,),
    "suunta": (10,),
    "väheksyntä": (10,),
    "vähäläntä": (10,),
    "vähänläntä": (10,),
    # -va
    "murhaava": (10,),
    # -n
    "kahdeksan": (10,),
    "seitsemän": (10,),
    "yhdeksän": (10,),

    # class 11
    # -ja
    "apaja": (11,),
    "leukoija": (11,),
    # -ka
    "judoka": (11,),
    # -lA
    "käpälä": (11,),
    # -mA
    "hekuma": (11,),
    "kärhämä": (11,),
    "mahatma": (11,),
    "paatsama": (11,),
    "probleema": (11,),
    "ödeema": (11,),
    # -nA
    "jellona": (11,),
    "korona": (11,),
    "lattana": (11,),
    "lättänä": (11,),
    "mammona": (11,),
    "marihuana": (11,),
    "maruna": (11,),
    "murena": (11,),
    "ohrana": (11,),
    "omena": (11,),
    "orpana": (11,),
    "papana": (11,),
    "pipana": (11,),
    "poppana": (11,),
    "sikuna": (11,),
    "täkänä": (11,),
    # -rA
    "algebra": (11,),
    "hapera": (11,),
    "hatara": (11,),
    "hattara": (11,),
    "hutera": (11,),
    "itara": (11,),
    "kihara": (11,),
    "kiverä": (11,),
    "käkkärä": (11,),
    "mäkärä": (11,),
    "sikkara": (11,),
    "säkkärä": (11,),
    "tomera": (11,),
    "vanttera": (11,),
    "veiterä": (11,),
    "äpärä": (11,),
    # -sa
    "mimoosa": (11,),
    # -va
    "ahava": (11,),
    "harava": (11,),

    # class 12
    # -VV
    "aramea": (12,),
    "bougainvillea": (12,),
    "idea": (12,),
    "komitea": (12,),
    "kommunikea": (12,),
    "matinea": (12,),
    "pallea": (12,),
    "urea": (12,),
    # -ja
    "kanalja": (12,),
    "kastanja": (12,),
    "persilja": (12,),
    # -ka
    "ekliptika": (12,),
    "paprika": (12,),
    # -ma
    "salama": (12,),
    # -na
    "harppuuna": (12,),
    # -rA
    "angora": (12,),
    "jäkkärä": (12,),
    "kamera": (12,),
    "kolera": (12,),
    "littera": (12,),
    "ooppera": (12,),
    "väkkärä": (12,),

    # class 13
    # -VV
    "atsalea": (13,),
    "attasea": (13,),
    "media": (13,),
    "orkidea": (13,),
    # -da
    "reseda": (13,),
    # -ga
    "kollega": (13,),
    "malaga": (13,),
    "oomega": (13,),
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
    # -lA
    "apila": (13,),
    "artikla": (13,),
    "gorilla": (13,),
    "kampela": (13,),
    "manila": (13,),
    "manilla": (13,),
    "mitella": (13,),
    "paella": (13,),
    "postilla": (13,),
    "sairaala": (13,),
    "siivilä": (13,),
    "sikala": (13,),
    "takila": (13,),
    "tortilla": (13,),
    "viola": (13,),
    # -ma
    "karisma": (13,),
    "maailma": (13,),
    "suurima": (13,),
    # -nA
    "aivina": (13,),
    "aluna": (13,),
    "arina": (13,),
    "ipana": (13,),
    "kahina": (13,),
    "kohina": (13,),
    "kopina": (13,),
    "kuhina": (13,),
    "kärinä": (13,),
    "marina": (13,),
    "maukuna": (13,),
    "määkinä": (13,),
    "mölinä": (13,),
    "mörinä": (13,),
    "möyrinä": (13,),
    "paukkina": (13,),
    "perenna": (13,),
    "piekana": (13,),
    "porina": (13,),
    "rahina": (13,),
    "ramina": (13,),
    "reppana": (13,),
    "retsina": (13,),
    "ruutana": (13,),
    "smetana": (13,),
    "taverna": (13,),
    "tuoksina": (13,),
    "ukraina": (13,),
    "vagina": (13,),
    # -ra
    "gerbera": (13,),
    "hetaira": (13,),
    "ketara": (13,),
    "kitara": (13,),
    "madeira": (13,),
    "matara": (13,),
    "sikkura": (13,),
    "tempera": (13,),
    "vaahtera": (13,),
    # -sa
    "meduusa": (13,),
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
    # -pa
    "ulappa": (14,),
    # -ta
    "navetta": (14,),
    "ometta": (14,),
    "pohatta": (14,),
    "savotta": (14,),

    # class 15
    "ainoa": (15,),

    # class 18
    # -VV
    "ei-kenenkään-maa": (18,),
    "frisbee": (18,),
    "gnuu": (18,),
    "homssantuu": (18,),
    "huuhaa": (18,),
    "kanapee": (18,),
    "munaskuu": (18,),
    "peeaa": (18,),
    "pelakuu": (18,),
    "puusee": (18,),
    "rokokoo": (18,),
    "tenkkapoo": (18,),
    # -CV
    "go-go": (18,),

    # class 19
    "tie": (19,),

    # class 20
    "nugaa": (20,),
    "politbyroo": (20,),
    "raguu": (20,),
    "sampoo": (20,),
    "trikoo": (20,),
    "voodoo": (20,),

    # class 21
    # -VV
    "brasserie": (21,),
    "brie": (21,),
    "fondue": (21,),
    "reggae": (21,),
    "tax-free": (21,),
    # -CV
    "cha-cha-cha": (21,),
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

    # class 30
    "peitsi": (30,),
    "veitsi": (30,),

    # class 31
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
    "minunlaiseni": (38,),
    "sinunlaisesi": (38,),

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
    "jäntere": (48,),
    "kiiru": (48,),
    "tere": (48,),

    # class 49
    # -l/-n
    "muren": (49,),
    "sammal": (49,),
    "säen": (49,),
    "taival": (49,),
    # -aCe/-eCe
    "askare": (49,),
    "askele": (49,),
    "hepene": (49,),
    "huhmare": (49,),
    "kantele": (49,),
    "kyynele": (49,),
    "murene": (49,),
    "ompele": (49,),
    "petkele": (49,),
    "pientare": (49,),
    "taipale": (49,),
    "saivare": (49,),
    "seppele": (49,),
    "säkene": (49,),
    "utare": (49,),
    "vempele": (49,),
}

# conjugation class, regex
ENDINGS = (
    # note: each part of each rule must apply to at least three words!
    # (the rest are listed as exceptions)

    # final consonant cluster or foreign final consonant (not l/n/r/s/t)
    (5,  r"([^aeiouyäö]{2}|[^aeiouyäölnrst])$"),

    # -bA/-dA/-fA/-gA/-šA/-zA/-žA
    (9,  r"[aei][^aeiouyäö]*[bdfgšzž]a$"),  # a/e/i + (C)(C)Ca (last C is foreign)
    (10, r"[bdfgšzž]a$"),                   # -Ca              (C is foreign)

    # -hA
    (9,  r"([aei][nrs]?|[ai]u)ha$"),  # a(C)/e(C)/i(C)/au/iu + ha
    (10, r"h[aä]$"),                  # -hA

    # -jA
    (12, r"panja$"),                # -panja
    (12, r"[aeklmnprstv]ij[aä]$"),  # a/e/C       + ijA
    (9,  r"([aei][hlnrt]|ra)ja$"),  # aC/eC/iC/ra + ja
    (10, r"j[aä]$"),                # -jA

    # -kA
    (9,  r"[aei][aeiu][^aeiouyäö]*ka$"),       # a/e/i + a/e/i/u + (C)(C)ka
    (10, r"[aeiouyäö]{2}[^aeiouyäö]*k[aä]$"),  # VV              + (C)(C)kA
    (13, r"....sk[aä]$"),                      # ????            + skA
    (9,  r"....[lnp]akka$"),                   # ???? + la/na/pa + kka
    (14, r"..[aäiuy]kk[aä]$"),                 # ??   + A/i/U    + kkA
    (9,  r"[aei][^aeiouyäö]*ka$"),             # a/e/i           + (C)(C)ka
    (10, r"k[aä]$"),                           # -kA

    # -lA
    (10, r"(äi|[ou][ou]|[äöy]y)l[aä]$"),    # äi/oo/uo/OU/UU/äy + lA
    (9,  r"[aeiou]{2}la$"),                 # -VVla
    (12, r"...[aäeiouy]l[aä]$"),            # -???VlA
    (10, r"((..[aei]|[ou][hlp]?)la|lä)$"),  # -??ala/-??ela/-??ila/-o(C)la/-u(C)la/-lä
    (9,  r"la$"),                           # -la

    # -mA
    (10, r"...[ae]uma$"),                      # ???au/???eu + ma
    (9,  r"([ai]a|ee|[aei]i|[ae]u)[lr]?ma$"),  # aa/ia/ee/ai/ei/ii/au/eu + (C)ma
    (10, r"[aeiouyäö]{2}s?m[aä]$"),            # -VV(C)mA
    (10, r"(..[aei]l?|[ou][hlmrs]*)ma$"),      # ??a(l)/??e(l)/??i(l)/o(C)(C)/u(C)(C) + ma
    (10, r"mä$"),                              # -mä
    (9,  r"ma$"),                              # -ma

    # -nA
    (13, r"..(ee|ii|uu)na$"),                  # ?? + ee/ii/uu + na
    (9,  r"[aei][aieu][^aeiouyäö]*na$"),       # a/e/i + a/e/i/u + (C)(C)na
    (10, r"[aeiouyäö]{2}[^aeiouyäö]*n[aä]$"),  # -VV(C)(C)nA
    (12, r"..[aäiuy]n[aä]$"),                  # ?? + A/i/U + nA
    (10, r"([ou][^aeiouyäö]*na|nä)$"),         # -o(C)(C)na/-u(C)(C)na/-nä
    (9,  r"na$"),                              # -na

    # -pA
    (9,  r"(a|e|[^ou]i)[^aeiouyäö]*pa$"),  # a/e/i (not oi/ui) + (C)(C)pa
    (10, r"p[aä]$"),                       # -pA

    # -rA
    (9,  r"[aei][aeiu][^aeiouyäö]*ra$"),  # a/e/i + a/e/i/u + (C)(C)ra
    (13, r"...uura$"),                    # -???uura
    (12, r"...[auy]r[aä]$"),              # ???   + a/U     + rA
    (9,  r"(a|e|i|eu)[^aeiouyäö]*ra$"),   # a/e/i           + (C)(C)ra
    (10, r"r[aä]$"),                      # -rA

    # -sA
    (13, r"...(es|it)sa$"),              # ??? + es/it    + sa
    (10, r"(oi|...[au]i)sa$"),           # oi/???ai/???ui + sa
    (9,  r"([aei]|iu)[^aeiouyäö]*sa$"),  # a/e/i/iu       + (C)(C)sa
    (10, r"s[aä]$"),                     # -sA

    # -tA
    (9,  r"[ai]u[st]?ta$"),         # au/iu + (s/t)ta
    (9,  r"...nt[aä]$"),            # -???ntA
    (13, r"..usta$"),               # -usta
    (9,  r"[aei][^aeiouyäö]*ta$"),  # a/e/i + (C)(C)ta
    (10, r"t[aä]$"),                # -tA

    # -vA
    (9,  r"(haa|au|[ai]i|[ai][hklrst])va$"),  # haa/au/ai/ii/aC/iC + va
    (10, r"v[aä]$"),                          # -vA

    # -VV
    (3,  r"([aeiy]o|iö)$"),                  # -ao/-eo/-iO/-yo
    (21, r"(ou|[aeo]y)$"),                   # -ay/-ey/-oU
    (10, r"oi?a$"),                          # -o(i)a
    (12, r"(i[aä]|ua|[^aeiouyäö][nr]ea)$"),  # -iA/-ua/-Cnea/-Crea
    (15, r"e[aä]$"),                         # -eA
    (17, r"..(aa|oo|uu)$"),                  # ?? + aa/oo/uu
    (20, r"..(ee|öö|yy)$"),                  # ?? + ee/öö/yy
    (48, r"([aäiouy]e)$"),                   # A/i/o/U + e
    (19, r"(uo|yö)$"),                       # -UO
    (18, r"[aeiouyäö]{2}$"),                 # -VV

    # -e
    (8,  "[cg]e$"),  # -ce/-ge
    (49, "ere$"),    # -ere
    (48, "e$"),      # -e

    # -i
    #
    (24, r"kuusi$"),
    (26, r"(kuo|vuo|juu)ri$"),
    (5,  r"(ba|p|va)ari$"),
    (5,  r"(ää)ri$"),
    #
    (27, r"(ei|au|äy|öy)si$"),  # ei/AU/öy + si
    (28, r"[lnr]si$"),          # l/n/r + si
    (6,  r"[aäe]ri$"),
    (5,  r"i$"),
    # TODO: continue from here

    (21, r"é$"),                                      # -é
    (34, r"[aeiouyäö]t[oö]n$"),                       # -VtOn
    (38, r"nen$"),                                    # -nen
    (39, r"[^eiouyö][uy]s$"),                         # -AUs/-CUs
    (40, r"[eiouyö][uy]s$"),                          # -eUs/-iUs/-OUs/-UUs
    (41, r"[dghjklmnprstv][aä]s$"),                   # -CAs
    (47, r"n[uy]t$"),                                 # -nUt
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
