"""Get the Kotus conjugation class of a Finnish noun.
Note: A = a/ä, O = o/ö, U = u/y, V = any vowel, C = any consonant"""

import re
import sys

# errors: 9436
# all -VV and -A words conjugate correctly

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
    "sini": (5, 7),
    "puola": (9, 10),

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
    # -o
    "adagio": (1,),
    "duo": (1,),
    "osso buco": (1,),
    "ouzo": (1,),
    "taco": (1,),
    "trio": (1,),

    # class 3
    # -Ve
    "aaloe": (3,),
    "collie": (3,),
    "lassie": (3,),
    "oboe": (3,),
    "zombie": (3,),

    # class 5
    # -V
    "mansi": (5,),
    # -Vl
    "becquerel": (5,),
    "cocktail": (5,),
    "gospel": (5,),
    "kennel": (5,),
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
    # native
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
    # English loans
    "beagle": (8,),
    "byte": (8,),
    "chippendale": (8,),
    "deadline": (8,),
    "folklore": (8,),
    "freestyle": (8,),
    "ginger ale": (8,),
    "grape": (8,),
    "hardware": (8,),
    "house": (8,),
    "jive": (8,),
    "ladylike": (8,),
    "lime": (8,),
    "mangrove": (8,),
    "milk shake": (8,),
    "open house": (8,),
    "poplore": (8,),
    "puzzle": (8,),
    "ragtime": (8,),
    "single": (8,),
    "software": (8,),
    "striptease": (8,),
    # Romance/Greek loans
    "agaave": (8,),
    "akne": (8,),
    "à la carte": (8,),
    "andante": (8,),
    "bavaroise": (8,),
    "beguine": (8,),
    "bouillabaisse": (8,),
    "bourette": (8,),
    "bourgogne": (8,),
    "boutique": (8,),
    "chenille": (8,),
    "crème fraîche": (8,),
    "crêpe": (8,),
    "cum laude": (8,),
    "duchesse": (8,),
    "empire": (8,),
    "ensemble": (8,),
    "entrecôte": (8,),
    "faksimile": (8,),
    "force majeure": (8,),
    "forte": (8,),
    "genre": (8,),
    "gruyère": (8,),
    "jade": (8,),
    "joule": (8,),
    "komedienne": (8,),
    "lasagne": (8,),
    "madame": (8,),
    "mezzoforte": (8,),
    "minestrone": (8,),
    "mobile": (8,),
    "mousse": (8,),
    "penne": (8,),
    "petanque": (8,),
    "promille": (8,),
    "psyyke": (8,),
    "quenelle": (8,),
    "quiche": (8,),
    "raclette": (8,),
    "ratatouille": (8,),
    "ringette": (8,),
    "tabbule": (8,),
    "tagliatelle": (8,),
    "tele": (8,),
    "tilde": (8,),
    "tragedienne": (8,),
    "vaudeville": (8,),
    "vinaigrette": (8,),
    # other loans
    "karaoke": (8,),
    "karate": (8,),
    "kurare": (8,),
    "saame": (8,),
    "sake": (8,),
    "ukulele": (8,),

    # class 9
    # -Va
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
    # -la
    "hopeahela": (9,),
    "suola": (9,),
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
    "astma": (9,),
    "halma": (9,),
    "helma": (9,),
    "ilma": (9,),
    "kalma": (9,),
    "sialma": (9,),
    # -ana
    "kana": (9,),
    "lana": (9,),
    "mana": (9,),
    "sana": (9,),
    "vana": (9,),
    # -na
    "ballerina": (9,),
    "hana": (9,),
    "ikebana": (9,),
    "jana": (9,),
    "kina": (9,),
    "lapsenkina": (9,),
    "tina": (9,),
    # -ppa
    "kauppa": (9,),
    # -ra
    "hara": (9,),
    "hera": (9,),
    "kara": (9,),
    "para": (9,),
    "sara": (9,),
    "siera": (9,),
    "tiera": (9,),
    "vara": (9,),
    # -sa
    "aisa": (9,),
    "kiusa": (9,),
    # -tA
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
    # -Va
    "boa": (10,),
    "feijoa": (10,),
    "paranoia": (10,),
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
    # -nA
    "gallona": (10,),
    "heinä": (10,),
    "hynä": (10,),
    "höynä": (10,),
    "ihana": (10,),
    "juna": (10,),
    "jäynä": (10,),
    "kruuna": (10,),
    "kränä": (10,),
    "kynä": (10,),
    "känä": (10,),
    "leijona": (10,),
    "muna": (10,),
    "nenä": (10,),
    "puna": (10,),
    "roina": (10,),
    "ruuna": (10,),
    "ryönä": (10,),
    "seinä": (10,),
    "tsasouna": (10,),
    "yliminä": (10,),
    # -pa
    "aikaansaapa": (10,),
    # -ra
    "ankara": (10,),
    "avara": (10,),
    "eripura": (10,),
    "jyrä": (10,),
    "kehrä": (10,),
    "koira": (10,),
    "kumara": (10,),
    "kura": (10,),
    "kuura": (10,),
    "mura": (10,),
    "peeärrä": (10,),
    "suura": (10,),
    "tuura": (10,),
    "tyrä": (10,),
    "ura": (10,),
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
    # -ra
    "algebra": (11,),
    "hapera": (11,),
    "hatara": (11,),
    "hattara": (11,),
    "hutera": (11,),
    "itara": (11,),
    "kihara": (11,),
    "kiverä": (11,),
    "sikkara": (11,),
    "tomera": (11,),
    "vanttera": (11,),
    "veiterä": (11,),
    "äpärä": (11,),
    # -Vsa
    "mimoosa": (11,),
    # -va
    "ahava": (11,),
    "harava": (11,),

    # class 12
    # -ea
    "amenorrea": (12,),
    "apnea": (12,),
    "aramea": (12,),
    "bougainvillea": (12,),
    "gonorrea": (12,),
    "hebrea": (12,),
    "heprea": (12,),
    "idea": (12,),
    "komitea": (12,),
    "kommunikea": (12,),
    "matinea": (12,),
    "pallea": (12,),
    "seborrea": (12,),
    "uniapnea": (12,),
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
    # -ea
    "atsalea": (13,),
    "attasea": (13,),
    "orkidea": (13,),
    # -ia
    "media": (13,),
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
    "angiina": (13,),
    "arina": (13,),
    "ipana": (13,),
    "kahina": (13,),
    "kamiina": (13,),
    "kohina": (13,),
    "kopina": (13,),
    "kuhina": (13,),
    "kärinä": (13,),
    "marina": (13,),
    "masiina": (13,),
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
    "resiina": (13,),
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
    "ei-kenenkään-maa": (18,),
    "frisbee": (18,),
    "gnuu": (18,),
    "homssantuu": (18,),
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

    # foreign final consonant(s)
    (5,  r"[bcdfghkmpx]$"),    # -C (C != l/n/r/s/t)
    (5,  r"[klnrs][lnrst]$"),  # -CC (2nd C = l/n/r/s/t)

    # -bA/-dA/-fA/-gA/-šA/-zA/-žA
    (9,  r"[aei][dfklmntz]?[bdfgšzž]a$"),  # -a(C)Ca/-e(C)Ca/-i(C)Ca (2nd C is foreign)
    (10, r"[ouy][fglmn]?[bdfg]a$"),        # -o(C)Ca/-u(C)Ca/-y(C)ca (2nd C is foreign)

    # -hA
    (9,  r"([aei][nrs]?|[ai]u)ha$"),  # a(C)/e(C)/i(C)/au/iu + ha
    (10, r"h[aä]$"),                  # -hA

    # -jA
    (12, r"panja$"),                # -panja
    (12, r"[aeklmnprstv]ij[aä]$"),  # a/e/C       + ijA
    (9,  r"([aei][hlnrt]|ra)ja$"),  # aC/eC/iC/ra + ja
    (10, r"j[aä]$"),                # -jA

    # -kA
    (9,  r"[aei][aeiou][hks]?ka$"),        # aV/eV/iV     + (C)ka
    (10, r"[aeiouyäö]{2}[ks]?k[aä]$"),     # VV           + (C)kA
    (13, r"....sk[aä]$"),                  # ????         + skA
    (9,  r"....[lnp]akka$"),               # ???? + l/n/p + akka
    (14, r"..[aäiuy]kk[aä]$"),             # ??   + A/i/U + kkA
    (9,  r"[aei][fhklmnrst]*ka$"),         # a/e/i        + (C)(C)ka
    (10, r"[aeiouyäö][dhklnrst]*k[aä]$"),  # V            + (C)(C)kA

    # -lA
    (10, "(äi|[ou][ou]|[äöy]y)l[aä]$"),    # äi/oo/uo/OU/UU/äy + lA
    (9,  "[aeiou]{2}la$"),                 # -VVla
    (12, "...[aäeiouy]l[aä]$"),            # -???VlA
    (10, "((..[aei]|[ou][hlp]?)la|lä)$"),  # -??ala/-??ela/-??ila/-o(C)la/-u(C)la/-lä
    (9,  "la$"),                           # -la

    # -mA
    #
    (10, r"[ou]ima$"),                 # o/u + ima
    (10, r"[aäe]m[aä]$"),              # A/e + mA
    (10, r"lm[aä]$"),                  # lmA
    #
    (9,  r"[aäei][ghkmrs]?m[aä]$"),    # A/e/i + (C)mA
    (10, r"[oöuy](rs|[hmr])?m[aä]$"),  # O/U   + (C)(C)mA

    # -nA
    (10, r"[ou]ona$"),                   # -oona/-uona
    (13, r"(ee|uu)na$"),                 # -eena/-uuna
    (9,  r"([aeio][iu]|aa|ie)na$"),      # -VVna (VV != ee/oo/uo/uu)
    (12, r"[hklmnprstv][aäiuy]n[aä]$"),  # -CVnA
    (9,  r"[aei][ghnr]na$"),             # -aCna/-eCna/-iCna
    (10, r"[ou][hnr]na$"),               # -oCna/-uCna
    (10, r"[hns]nä$"),                   # -Cnä

    # -pA
    #
    (10, r"[ou]ipa$"),                      # -oipa/-uipa
    (10, r"[äei]([lmr]p|[lp]?)pä$"),        # ä/e/i + (C)(C) + pä
    #
    (9,  r"[aäei]([mr]p|[lmprs])?p[aä]$"),  # A/e/i + (C)(C)pA
    (10, r"[oöuy]([lmr]p|[lmpr])?p[aä]$"),  # O/U   + (C)(C)pA

    # -rA
    #
    (11, r"kärä$"),                               # kä            + rä
    #
    (9,  r"(aa|au|eu)ra$"),                       # aa/au/eu      + ra
    (9,  r"[ae]([bhprt]|kt|mb|nt|kst)ra$"),       # a/e + C(C)(C) + ra
    (9,  r"i[ht]?ra$"),                           # i(C)          + ra
    (10, r"([äeoö]|ou|[äöy]y)r[aä]$") ,           # ä/e/O/ou/Vy   + rA
    (10, r"[ouy]([bhkprt]|mb|nd|nt)r[aä]$"),      # o/U + C(C)    + rA
    (12, r"[kmpstv][auy]r[aä]$"),                 # Ca/Cu/Cy      + rA
    (13, r"uura$"),                               # uu            + ra

    # -sA
    #
    (10, r"[aou]isa$"),                              # -aisa/-oisa/-uisa
    (10, r"[äei][lnprst]?sä$"),                      # ä/e/i + (C) + sä
    #
    (9,  r"[aäei]([lmnr][pst]|[klmnprst])?s[aä]$"),  # A/e/i + (C)(C)sA
    (10, r"[oöuy]([mn][pst]|[klprst])?s[aä]$"),      # O/U   + (C)(C)sA

    # -tA
    #
    (9,  r"[ai]u[st]?ta$"),                              # a/i + u + (s/t) + ta
    (9,  r"[oöuy]nt[aä]$"),                              # O/U + ntA
    (10, r"[oöu]it[aä]$"),                               # O/u + itA
    (13, r"usta$"),                                      # -usta
    #
    (9,  r"[aäei]([lmnr][kpst]|[fghklmnprst])?t[aä]$"),  # A/e/i + (C)(C)tA
    (10, r"[oöuy]([lnr]t|[fhlrt])?t[aä]$"),              # O/U   + (C)(C)tA

    # -vA
    (9,  r"(haa|au|[ai]i|[ai][hklrst])va$"),  # haa/au/ai/ii/aC/iC + va
    (10, r"v[aä]$"),                          # -vA

    # -CCO/-CCU
    (4,  r"kk[oö]$"),                                 # -kkO
    (1,  r"[^aeiouyäö][^aeiouyäö][ouyö]$"),           # -CCO/-CCU

    # -V (not -CA)
    (3,  r"([aeiy]o|iö)$"),                     # -ao/-eo/-iO/-yo
    (8,  "[cg]e$"),                             # -ce/-ge
    (12, "(i[aä]|ua)$"),                        # -iA/-ua
    (15, "e[aä]$"),                             # -eA
    (17, r"(aa|oo|uu)$"),                       # -aa/-oo/-uu
    (18, "[aeiouä]i$"),                         # -Vi
    (20, "ee$"),                                # -ee
    (48, "([aäiouydhjklmnpstv]|[aäiour]r)e$"),  # -Ve/-Ce (not -ee/-ce/-ge/-ere)
    (49, "ere$"),                               # -ere

    (21, r"é$"),                                      # -é
    (28, r"[lnr]si$"),                                # -Csi
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
