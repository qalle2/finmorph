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

# exceptions to rules by declension and ending (noun: declension)
_EXCEPTIONS = {
    # 1 - VV
    "adagio": 1,
    "duo": 1,
    "trio": 1,
    # 1 - kkO
    "koneikko": 1,
    "miljoonikko": 1,
    "pantomiimikko": 1,
    "papurikko": 1,
    "pateetikko": 1,
    "petäjikkö": 1,
    "poleemikko": 1,
    "poliitikko": 1,
    "pragmaatikko": 1,
    "praktikko": 1,
    "romantikko": 1,
    "saraikko": 1,
    "semiootikko": 1,
    "untuvikko": 1,
    "uskalikko": 1,
    # 1 - stO
    "hyllystö": 1,
    "kalusto": 1,
    "käyrästö": 1,
    "kojeisto": 1,
    "kuidusto": 1,
    "kuormasto": 1,
    "lähistö": 1,
    "laitteisto": 1,
    "lajisto": 1,
    "lasisto": 1,
    "lehdistö": 1,
    "lepistö": 1,
    "linssistö": 1,
    "merkistö": 1,
    "munkisto": 1,
    "murteisto": 1,
    "naisisto": 1,
    "oikeisto": 1,
    "pillistö": 1,
    "pojisto": 1,
    "pylväistö": 1,
    "raiteisto": 1,
    "ruovisto": 1,
    "ruususto": 1,
    "testistö": 1,
    "tyypistö": 1,
    "vaihteisto": 1,
    "väylästö": 1,
    "virasto": 1,
    # 1 - CV (not kkO, stO)
    "allegro": 1,
    "crescendo": 1,
    "elostelu": 1,
    "embargo": 1,
    "flamenco": 1,
    "flamingo": 1,
    "guano": 1,
    "heavy": 1,
    "huitaisu": 1,
    "istuskelu": 1,
    "jiujitsu": 1,
    "karibu": 1,
    "karkaisimo": 1,
    "koksittamo": 1,
    "kyhäily": 1,
    "lainaamo": 1,
    "libido": 1,
    "piano": 1,
    "rubato": 1,
    "sisältö": 1,
    "sombrero": 1,
    "treasury": 1,
    "vibrato": 1,

    # 2
    "katajisto": 2,
    "koordinaatisto": 2,
    "luettelo": 2,

    # 3 - VV
    "aaloe": 3,
    "collie": 3,
    "embryo": 3,
    "lassie": 3,
    "oboe": 3,
    "zombie": 3,

    # 5 - VVli
    "alleeli": 5,
    "biennaali": 5,
    "fertiili": 5,
    "gaeli": 5,
    "gerbiili": 5,
    "kajaali": 5,
    "klausuuli": 5,
    "koktaili": 5,
    "konsiili": 5,
    "koraali": 5,
    "korpraali": 5,
    "kreoli": 5,
    "labiili": 5,
    "lojaali": 5,
    "modaali": 5,
    "noduuli": 5,
    "pedaali": 5,
    "pluraali": 5,
    "profiili": 5,
    "triennaali": 5,
    "tuoli": 5,
    "viriili": 5,
    # 5 - CVli
    "dipoli": 5,
    "fenkoli": 5,
    "fenoli": 5,
    "follikkeli": 5,
    "lysoli": 5,
    "mentoli": 5,
    "moguli": 5,
    "mongoli": 5,
    "multippeli": 5,
    "pendeli": 5,
    "podsoli": 5,
    # 5 - mi
    "aatami": 5,
    "imaami": 5,
    "matami": 5,
    "monstrumi": 5,
    "oopiumi": 5,
    "palsami": 5,
    "salami": 5,
    "tatami": 5,
    "vigvami": 5,
    # 5 - VVni
    "afgaani": 5,
    "butaani": 5,
    "doktriini": 5,
    "etaani": 5,
    "eteeni": 5,
    "fibriini": 5,
    "gluteeni": 5,
    "humaani": 5,
    "jasmiini": 5,
    "joriini": 5,
    "kaimaani": 5,
    "karbiini": 5,
    "kardaani": 5,
    "kiniini": 5,
    "Koraani": 5,
    "kretliini": 5,
    "lantaani": 5,
    "laviini": 5,
    "liaani": 5,
    "ligniini": 5,
    "mangaani": 5,
    "membraani": 5,
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
    "strykniini": 5,
    "syaani": 5,
    "sykliini": 5,
    "tanniini": 5,
    "teiini": 5,
    "toksiini": 5,
    # 5 - CVni
    "guldeni": 5,
    "japani": 5,
    "kosini": 5,
    "martini": 5,
    "nomini": 5,
    "panini": 5,
    "tapani": 5,
    # 5 - VVri
    "afääri": 5,
    "bordyyri": 5,
    "brodyyri": 5,
    "brosyyri": 5,
    "kefiiri": 5,
    "kvartääri": 5,
    "kvasaari": 5,
    "paapuuri": 5,
    "porfyyri": 5,
    "primaari": 5,
    "primääri": 5,
    "reviiri": 5,
    "satyyri": 5,
    "tyyrpuuri": 5,
    "vulgaari": 5,
    "vulgääri": 5,
    # 5 - CVri
    "fosfori": 5,
    "kašmiri": 5,
    "kateederi": 5,
    "kollektori": 5,
    "kompostori": 5,
    "likvori": 5,
    "varistori": 5,
    # 5 - n
    "charleston": 5,
    "drive-in": 5,
    "hymen": 5,
    "kelvin": 5,
    "maraton": 5,
    "pinyin": 5,
    # 5 - s
    "AIDS": 5,
    "blues": 5,
    "calvados": 5,
    "couscous": 5,
    "director musices": 5,
    "marakas": 5,
    "moussakas": 5,
    # 5 - other (not li, mi, ni, ri, n, s)
    "CD-ROM": 5,
    "input": 5,
    "kennel": 5,
    "LED": 5,
    "LYHKI": 5,
    "mansi": 5,
    "output": 5,
    "sutki": 5,

    # 6
    "agar": 6,
    "agar-agar": 6,
    "äksiisi": 6,
    "akupunktuuri": 6,
    "antenni": 6,
    "appenzeller": 6,
    "approbatur": 6,
    "art director": 6,
    "atolli": 6,
    "atomi": 6,
    "azerbaidžani": 6,
    "babysitter": 6,
    "backgammon": 6,
    "basenji": 6,
    "basilli": 6,
    "besserwisser": 6,
    "bestseller": 6,
    "betoni": 6,
    "biedermeier": 6,
    "biisoni": 6,
    "biljardi": 6,
    "bisarri": 6,
    "bitter": 6,
    "blazer": 6,
    "bosoni": 6,
    "bourbon": 6,
    "buzuki": 6,
    "chanson": 6,
    "copywriter": 6,
    "daktyyli": 6,
    "dealer": 6,
    "detalji": 6,
    "diakoni": 6,
    "diesel": 6,
    "donjuan": 6,
    "edam": 6,
    "entsyymi": 6,
    "firaabeli": 6,
    "flanelli": 6,
    "foneemi": 6,
    "fotoni": 6,
    "freelancer": 6,
    "gallup": 6,
    "gaselli": 6,
    "gibboni": 6,
    "glukoosi": 6,
    "haaremi": 6,
    "hampuusi": 6,
    "hotelli": 6,
    "ikoni": 6,
    "improbatur": 6,
    "inspehtori": 6,
    "kaanon": 6,
    "kanjoni": 6,
    "kantoni": 6,
    "kardoni": 6,
    "karpaasi": 6,
    "kassler": 6,
    "kinuski": 6,
    "kolhoosi": 6,
    "kommuuni": 6,
    "kondomi": 6,
    "koturni": 6,
    "laser": 6,
    "laudatur": 6,
    "leptoni": 6,
    "liirumlaarum": 6,
    "likööri": 6,
    "loafer": 6,
    "lumen": 6,
    "luumen": 6,
    "meloni": 6,
    "monsuuni": 6,
    "monttööri": 6,
    "motelli": 6,
    "muslimi": 6,
    "nailon": 6,
    "narkoosi": 6,
    "nelson": 6,
    "neuroosi": 6,
    "nylon": 6,
    "oliivi": 6,
    "outsider": 6,
    "pakaasi": 6,
    "peijooni": 6,
    "pekoni": 6,
    "piisoni": 6,
    "plantaasi": 6,
    "pogromi": 6,
    "poliisi": 6,
    "ponttoni": 6,
    "prostaglandiini": 6,
    "proteesi": 6,
    "putelli": 6,
    "pyton": 6,
    "refleksi": 6,
    "reversiibeli": 6,
    "revolveri": 6,
    "rial": 6,
    "rottweiler": 6,
    "sabloni": 6,
    "saluki": 6,
    "sardelli": 6,
    "schäfer": 6,
    "serviisi": 6,
    "sirkoni": 6,
    "sirtaki": 6,
    "sitar": 6,
    "snooker": 6,
    "sotiisi": 6,
    "sottiisi": 6,
    "sovhoosi": 6,
    "stadion": 6,
    "standardi": 6,
    "stilleben": 6,
    "sypressi": 6,
    "systeemi": 6,
    "taifuuni": 6,
    "testosteroni": 6,
    "teutoni": 6,
    "tienesti": 6,
    "tonic water": 6,
    "toteemi": 6,
    "trapetsi": 6,
    "triatlon": 6,
    "tribuuni": 6,
    "trotyyli": 6,
    "tsinuski": 6,
    "turkoosi": 6,
    "ubikinoni": 6,
    "ukaasi": 6,
    "unioni": 6,
    "universumi": 6,
    "valloni": 6,
    "valööri": 6,
    "variaabeli": 6,
    "vesper": 6,
    "vinyyli": 6,
    "viskoosi": 6,
    "volyymi": 6,
    "voucher": 6,
    "weber": 6,
    "zirkoni": 6,
    "zoonoosi": 6,

    # 7 - ki
    "hanki": 7,
    "hauki": 7,
    "henki": 7,
    "hiki": 7,
    "joki": 7,
    "kaikki": 7,
    "käki": 7,
    "kanki": 7,
    "kaski": 7,
    "kiiski": 7,
    "koski": 7,
    "länki": 7,
    "leski": 7,
    "mäki": 7,
    "noki": 7,
    "onki": 7,
    "piki": 7,
    "poski": 7,
    "reki": 7,
    "sääski": 7,
    "sänki": 7,
    "tuki": 7,
    "väki": 7,
    "vaski": 7,
    # 7 - mi
    "helmi": 7,
    "nimi": 7,
    "nummi": 7,
    "nurmi": 7,
    "salmi": 7,
    "seimi": 7,
    "sormi": 7,
    "suomi": 7,
    "tammi": 7,
    # 7 - pi
    "appi": 7,
    "happi": 7,
    "koipi": 7,
    "läpi": 7,
    "rupi": 7,
    "sappi": 7,
    "siipi": 7,
    "soppi": 7,
    "tuppi": 7,
    "typpi": 7,
    # 7 - si
    "päitsi": 7,
    "sääksi": 7,
    "saksi": 7,
    "suitsi": 7,
    "suksi": 7,
    "viiksi": 7,
    "vuoksi": 7,
    # 7 - vi
    "hirvi": 7,
    "järvi": 7,
    "kivi": 7,
    "lovi": 7,
    "ovi": 7,
    "pälvi": 7,
    "parvi": 7,
    "pilvi": 7,
    "polvi": 7,
    "povi": 7,
    "sarvi": 7,
    "savi": 7,
    "suvi": 7,
    "talvi": 7,
    "torvi": 7,
    "tyvi": 7,
    # 7 - other
    "haahti": 7,
    "hanhi": 7,
    "kärhi": 7,
    "lehti": 7,
    "närhi": 7,
    "onni": 7,
    "saarni": 7,
    "tähti": 7,
    "tilhi": 7,
    "veli": 7,

    # 8
    "agaave": 8,
    "akne": 8,
    "à la carte": 8,
    "ale": 8,
    "andante": 8,
    "bäne": 8,
    "bavaroise": 8,
    "beagle": 8,
    "beguine": 8,
    "beige": 8,
    "bouillabaisse": 8,
    "bourgogne": 8,
    "boutique": 8,
    "charlotte russe": 8,
    "chenille": 8,
    "chippendale": 8,
    "college": 8,
    "crème fraîche": 8,
    "crêpe": 8,
    "cum laude": 8,
    "deadline": 8,
    "duchesse": 8,
    "eau de Cologne": 8,
    "empire": 8,
    "ensemble": 8,
    "entrecôte": 8,
    "faksimile": 8,
    "folklore": 8,
    "force majeure": 8,
    "forte": 8,
    "freelance": 8,
    "freestyle": 8,
    "genre": 8,
    "ginger ale": 8,
    "gruyère": 8,
    "hardware": 8,
    "image": 8,
    "itse": 8,
    "jade": 8,
    "jeppe": 8,
    "joule": 8,
    "kalle": 8,
    "karaoke": 8,
    "karate": 8,
    "komedienne": 8,
    "kurare": 8,
    "kurre": 8,
    "ladylike": 8,
    "lande": 8,
    "lasagne": 8,
    "lime": 8,
    "madame": 8,
    "mangrove": 8,
    "manne": 8,
    "mezzoforte": 8,
    "milk shake": 8,
    "minestrone": 8,
    "mobile": 8,
    "mousse": 8,
    "nalle": 8,
    "nasse": 8,
    "nisse": 8,
    "nukke": 8,
    "ope": 8,
    "open house": 8,
    "pelle": 8,
    "penne": 8,
    "petanque": 8,
    "polle": 8,
    "poplore": 8,
    "pose": 8,
    "poste restante": 8,
    "promille": 8,
    "psyyke": 8,
    "puzzle": 8,
    "quenelle": 8,
    "ragtime": 8,
    "ratatouille": 8,
    "saame": 8,
    "sake": 8,
    "single": 8,
    "soft ice": 8,
    "software": 8,
    "striptease": 8,
    "tabbule": 8,
    "tagliatelle": 8,
    "tele": 8,
    "tilde": 8,
    "toope": 8,
    "tragedienne": 8,
    "ukulele": 8,
    "vaudeville": 8,
    "vivace": 8,

    # 9 - Va
    "dia": 9,
    "maya": 9,
    "odysseia": 9,
    # 9 - Ca
    "abrakadabra": 9,
    "akileija": 9,
    "alfalfa": 9,
    "ameba": 9,
    "antiikva": 9,
    "aortta": 9,
    "ballerina": 9,
    "basilika": 9,
    "canasta": 9,
    "chinchilla": 9,
    "dalai-lama": 9,
    "dilemma": 9,
    "ekseema": 9,
    "enchilada": 9,
    "guava": 9,
    "hoosianna": 9,
    "ikebana": 9,
    "jakaranda": 9,
    "karateka": 9,
    "kimaira": 9,
    "koala": 9,
    "krypta": 9,
    "lymfa": 9,
    "marimba": 9,
    "mykorritsa": 9,
    "nautiikka": 9,
    "panoraama": 9,
    "papilla": 9,
    "paradigma": 9,
    "praasniekka": 9,
    "propaganda": 9,
    "prostata": 9,
    "regatta": 9,
    "ruustinna": 9,
    "sialma": 9,
    "sinsilla": 9,
    "suola": 9,
    "teoreema": 9,
    "tequila": 9,
    "tiaara": 9,
    "toccata": 9,
    "tonsilla": 9,
    "valeriaana": 9,
    # 9 - ä
    "iskä": 9,
    "nyintä": 9,
    "ryintä": 9,

    # 10 - VA
    "boa": 10,
    "feijoa": 10,
    "paranoia": 10,
    # 10 - ntA
    "emäntä": 10,
    "halveksunta": 10,
    "huuhdonta": 10,
    "hyväksyntä": 10,
    "isäntä": 10,
    "väheksyntä": 10,
    # 10 - Ca (not nta)
    "amfora": 10,
    "ankara": 10,
    "avara": 10,
    "gallona": 10,
    "gorgonzola": 10,
    "hankala": 10,
    "hyperbola": 10,
    "ihana": 10,
    "jumala": 10,
    "kamala": 10,
    "karambola": 10,
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
    "protokolla": 10,
    "reskontra": 10,
    "saaja": 10,
    "saapa": 10,
    "saava": 10,
    "sukkela": 10,
    "terrakotta": 10,
    "tukala": 10,
    # 10 - Cä (not ntä)
    "jäkälä": 10,
    "peeärrä": 10,
    "pykälä": 10,
    # 10 - n
    "kahdeksan": 10,
    "seitsemän": 10,
    "yhdeksän": 10,

    # 11 - mA
    "hekuma": 11,
    "kärhämä": 11,
    "mahatma": 11,
    "ödeema": 11,
    "paatsama": 11,
    "probleema": 11,
    # 11 - nA
    "lattana": 11,
    "lättänä": 11,
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
    # 11 - rA
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
    "säkkärä": 11,
    "sikkara": 11,
    "tomera": 11,
    "vanttera": 11,
    "veiterä": 11,
    # 11 - CA (not mA, nA, rA)
    "ahava": 11,
    "apaja": 11,
    "harava": 11,
    "judoka": 11,
    "käpälä": 11,
    "leukoija": 11,
    "mimoosa": 11,

    # 12 - VA
    "apnea": 12,
    "hebrea": 12,
    "heprea": 12,
    "idea": 12,
    "pallea": 12,
    "urea": 12,
    # 12 - rA
    "jäkkärä": 12,
    "kamera": 12,
    "kolera": 12,
    "littera": 12,
    "ooppera": 12,
    "väkkärä": 12,
    # 12 - CA (not rA)
    "ekliptika": 12,
    "harppuuna": 12,
    "paprika": 12,
    "passiiva": 12,
    "salama": 12,

    # 13 - VA
    "atsalea": 13,
    "attasea": 13,
    "media": 13,
    "orkidea": 13,
    # 13 - lA
    "apila": 13,
    "artikla": 13,
    "kampela": 13,
    "manila": 13,
    "sairaala": 13,
    "siivilä": 13,
    "sikala": 13,
    "takila": 13,
    "viola": 13,
    # 13 - nA
    "aivina": 13,
    "arina": 13,
    "ipana": 13,
    "kahina": 13,
    "kärinä": 13,
    "kohina": 13,
    "kopina": 13,
    "kuhina": 13,
    "määkinä": 13,
    "marina": 13,
    "maukuna": 13,
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
    # 13 - rA
    "gerbera": 13,
    "hetaira": 13,
    "ketara": 13,
    "kitara": 13,
    "madeira": 13,
    "matara": 13,
    "nomenklatuura": 13,
    "sikkura": 13,
    "tempera": 13,
    "vaahtera": 13,
    # 13 - CA (not lA, nA, rA)
    "aktiiva": 13,
    "karakteristika": 13,
    "karisma": 13,
    "maailma": 13,
    "majolika": 13,
    "mantilja": 13,
    "meduusa": 13,
    "papaija": 13,
    "prinsessa": 13,
    "psykofarmaka": 13,
    "reseda": 13,
    "skandinaaviska": 13,
    "suurima": 13,
    "vanilja": 13,
    "vernissa": 13,

    # 14
    "estetiikka": 14,
    "poliklinikka": 14,
    "psykometriikka": 14,
    "ulappa": 14,

    # 15
    "ainoa": 15,

    # 16
    "kumpi": 16,
    "kumpikaan": 16,
    "kumpikin": 16,

    # 17
    "hynttyy": 17,

    # 18 - VV
    "frisbee": 18,
    "homssantuu": 18,
    "huuhaa": 18,
    "kanapee": 18,
    "munaskuu": 18,
    "peeaa": 18,
    "pelakuu": 18,
    "puusee": 18,
    "rokokoo": 18,
    "tenkkapoo": 18,
    # 18 - CV
    "go-go": 18,

    # 20 - VV
    "nugaa": 20,
    "politbyroo": 20,
    "raguu": 20,
    "sampoo": 20,
    "trikoo": 20,
    "varietee": 20,
    "voodoo": 20,
    # 20 - CV
    "bile": 20,

    # 21
    "brasserie": 21,
    "brie": 21,
    "cha-cha-cha": 21,
    "clou": 21,
    "fondue": 21,
    "kung-fu": 21,
    "reggae": 21,
    "tax-free": 21,

    # 22 - t
    "beignet": 22,
    "bouquet": 22,
    "buffet": 22,
    "gourmet": 22,
    "nougat": 22,
    "parfait": 22,
    "passepartout": 22,
    "port salut": 22,
    "ragoût": 22,
    # 22 - C (not t)
    "bordeaux": 22,
    "know-how": 22,
    "show": 22,
    "tournedos": 22,

    # 23
    "moni": 23,
    "riihi": 23,
    "tiili": 23,
    "tuli": 23,

    # 24
    "hiili": 24,
    "hiiri": 24,
    "huuli": 24,
    "kusi": 24,
    "meri": 24,
    "ruuhi": 24,
    "uni": 24,

    # 25
    "lumi": 25,
    "luomi": 25,
    "taimi": 25,
    "tuomi": 25,

    # 26 - ri
    "juuri": 26,
    "kaari": 26,
    "nuori": 26,
    "saari": 26,
    "suuri": 26,
    "sääri": 26,
    "teeri": 26,
    "veri": 26,
    "vieri": 26,
    "ääri": 26,
    # 26 - Ci (not ri)
    "jousi": 26,
    "niini": 26,
    "tuuli": 26,
    "tyyni": 26,
    "ääni": 26,

    # 27 - VVsi
    "heisi": 27,
    "hiisi": 27,
    "kausi": 27,
    "köysi": 27,
    "liesi": 27,
    "niisi": 27,
    "paasi": 27,
    "reisi": 27,
    "täysi": 27,
    "uusi": 27,
    "viisi": 27,
    "vuosi": 27,
    # 27 - CVsi
    "kesi": 27,
    "käsi": 27,
    "mesi": 27,
    "susi": 27,
    "sysi": 27,
    "tosi": 27,
    "vesi": 27,

    # 29
    "lapsi": 29,

    # 30
    "veitsi": 30,

    # 31
    "haaksi": 31,
    "kaksi": 31,
    "yksi": 31,

    # 32
    "ien": 32,
    "kymmenen": 32,
    "nivel": 32,
    "sävel": 32,
    "sisar": 32,
    "tatar": 32,
    "tytär": 32,

    # 33
    "näin": 33,
    "puin": 33,
    "hapan": 33,
    "laidun": 33,
    "sydän": 33,
    "morsian": 33,
    "säteilytin": 33,

    # 35
    "lämmin": 35,

    # 36 - Vin
    "tain": 36,
    "parhain": 36,
    "taain": 36,
    "uloin": 36,
    # 38 - Cin
    "alin": 36,
    "enin": 36,
    "likin": 36,
    "lähin": 36,
    "sisin": 36,
    "vanhin": 36,
    "ylin": 36,
    "parahin": 36,

    # 37
    "vasen": 37,

    # 38
    "hänenlaisensa": 38,
    "kumpainenkaan": 38,
    "minunlaiseni": 38,
    "sinunlaisesi": 38,

    # 39 - As
    "aidas": 39,
    "ananas": 39,
    "atlas": 39,
    "emäs": 39,
    "haljas": 39,
    "harjas": 39,
    "iskias": 39,
    "jalas": 39,
    "juudas": 39,
    "kaimas": 39,
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
    "teräs": 39,
    "tervas": 39,
    "trikomoonas": 39,
    "vastas": 39,
    "vihdas": 39,
    "viinas": 39,
    "vitsas": 39,
    # 39 - VUs
    "hius": 39,
    "holhous": 39,
    "kehruus": 39,
    "kirous": 39,
    "kiveys": 39,
    "kokous": 39,
    "kumous": 39,
    "linkous": 39,
    "loveus": 39,
    "lumous": 39,
    "makuus": 39,
    "nuohous": 39,
    "patous": 39,
    "persuus": 39,
    "pikeys": 39,
    "poikkeus": 39,
    "putous": 39,
    "risteys": 39,
    "rukous": 39,
    "saveus": 39,
    "stradivarius": 39,
    "tarjous": 39,
    "taus": 39,
    "tyveys": 39,
    "verhous": 39,

    # 40 - AUs
    "ahnaus": 40,
    "harmaus": 40,
    "hartaus": 40,
    "hauraus": 40,
    "herraus": 40,
    "hitaus": 40,
    "hurskaus": 40,
    "irstaus": 40,
    "kärkkäys": 40,
    "karsaus": 40,
    "kiivaus": 40,
    "kirkkaus": 40,
    "kitsaus": 40,
    "kuulaus": 40,
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

    # 41 - es
    "äes": 41,
    "ies": 41,
    "kirves": 41,
    # 41 - is
    "altis": 41,
    "aulis": 41,
    "kallis": 41,
    "kaunis": 41,
    "kauris": 41,
    "nauris": 41,
    "raitis": 41,
    "ruis": 41,
    "ruumis": 41,
    "ryntys": 41,
    "saalis": 41,
    "tiivis": 41,
    "tyyris": 41,
    "valmis": 41,
    # 41 - us
    "vantus": 41,

    # 42
    "mies": 42,

    # 44
    "kevät": 44,
    "venät": 44,

    # 45 - As
    "kahdeksas": 45,
    "kolmas": 45,
    "miljoonas": 45,
    "neljäs": 45,
    "nollas": 45,
    "sadas": 45,
    "seitsemäs": 45,
    "yhdeksäs": 45,
    # 45 - es
    "kahdes": 45,
    "kuudes": 45,
    "mones": 45,
    "tuhannes": 45,
    "viides": 45,
    "yhdes": 45,

    # 46
    "tuhat": 46,

    # 48 - e
    "aie": 48,
    "hie": 48,
    "jäntere": 48,
    "säie": 48,
    "väkevöite": 48,
    # 48 - u
    "kiiru": 48,

    # 49 - e
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
    # 49 - C
    "auer": 49,
    "seppel": 49,
    "udar": 49,
}

# Note: rules in _RULES_1SYLL etc.:
# - Handle as many words as possible with rules instead of exceptions.
# - Make rules as short as possible (feel free to reorder them if needed).
# - One rule per declension. Exception: when the declension contains very
#   different kinds of words (e.g. -VV and -C), use one rule per declension
#   per section.
# - When rules don't depend on each other, sort them by declension.
# - If a rule depends on another, always mention it.
# - Each regex should match at least three words.
# - Use this as the list of all consonants: bcdfghjklmnpqrsštvwxzž (a-z minus
#   vowels plus š/ž).
# - No capital letters in rules; handle those words as exceptions.

# rules for monosyllabic nouns (declension, regex)
_RULES_1SYLL = tuple((d, re.compile(r, re.VERBOSE)) for (d, r) in (
    (5,  r"[bcdfghjklmnpqrsštvwxzž]$"),  # -C
    (19, r"( ie | uo | yö )$"),          # -ie/-UO
    (21, r"ay$"),                        # -ay
    (18, r"[aeiouyäö]{2}$"),             # -VV except those in decl. 19, 21
    (8,  r"e$"),                         # -e except those in decl. 18, 19
))

# rules for disyllabic nouns (declension, regex)
_RULES_2SYLL = tuple((d, re.compile(r, re.VERBOSE)) for (d, r) in (
    # === -VV ===

    (17, r"( aa | oo | uu )$"),  # -aa/-oo/-uu
    (18, r"[ai]i$"),             # -ai/-ii
    (20, r"( ee | öö | yy )$"),  # -ee/-öö/-yy
    (21, r"[aeo]y$"),            # -ay/-ey/-oy
    (48, r"[aäou]e$"),           # -Ae/-oe/-ue

    # === -CV ===

    # -CO/-CU
    (1, r"[bcdfghjklmnpqrsštvwxzž][oöuy]$"),
    # -lki/-rki/-tki/-lpi/-mpi/-rpi
    (7, r"( [lrt]k | [lmr]p )i$"),
    # -a/-e/-ai/-ei/-ii/-au/-eu/-iu/-Ci/i + (C)(C)Ca
    (
        9,
        r"( [ae] | [aei][iu] | [bcdfghjklmnpqrsštvwxzž]i | ^i )"
        r"[bcdfghjklmnpqrsštvwxzž]+a$"
    ),
    # -o/-y/-oi/-ui/-ou/-uu/-Cu/u + (C)(C)Ca
    (
        10,
        r"( [oy] | [ou][iu] | [bcdfghjklmnpqrsštvwxzž]u | ^u )"
        r"[bcdfghjklmnpqrsštvwxzž]+a$"
    ),
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
    (5,  r"[bcdfghjklmnpqrsštvwxzž]i$"),

    # -Ce
    (48, r"[bcdfghjklmnpqrsštvwxzž]e$"),

    # === -C ===

    (6,  r"( [eö]m | or )$"),                           # -em/-öm/-or
    (32, r"[hmsv]en$"),                                 # -hen/-men/-sen/-ven
    (33, r"in$"),                                       # -in
    (34, r"[aeiouyäö]t[oö]n$"),                         # -VtOn
    (38, r"nen$"),                                      # -nen
    (40, r"[eioöuy][uy]s$"),                            # -eUs/-iUs/-OUs/-UUs
    # -es/-is/-Os/-Us except those in decl. 40 (many exceptions)
    (39, r"[eioöuy]s$"),
    (41, r"[aä]s$"),                                    # -As (many exceptions)
    (47, r"( ll | n )[uy]t$"),                          # -llUt/-nUt
    # -CUt except those in declension 47
    (43, r"[bcdfghjklmnpqrsštvwxzž][uy]t$"),
    # some of -C + a/e + l/n/r
    (49, r"( [mv]al | [kmn]el | [är]en | [kmnv]ar | [gn]er )$"),
    # -C except those in decl. 6, 32-34, 38-41, 49 (many exceptions)
    (5,  r"[bcdfghjklmnpqrsštvwxzž]$"),
))

# rules for trisyllabic nouns (declension, regex)
_RULES_3SYLL = tuple((d, re.compile(r, re.VERBOSE)) for (d, r) in (
    # === -VV ===

    (3,  r"[aäei][oö]$"),   # -AO/-eO/-iO
    (12, r"[iuy][aä]$"),    # -iA/-UA
    (15, r"e[aä]$"),        # -eA
    (18, r"[aeiouyäö]i$"),  # -Vi
    (20, r"ee$"),           # -ee
    (48, r"[uy]e$"),        # -Ue

    # === -CA ===

    # -dA/-nkA/-ssA/-ntA/-VVttA
    (9,  r"( d | nk | ss | nt | (ee|ii|uu)tt )[aä]$"),
    # -AjA/-OjA/-UjA/-elä/-mA/-oona/-ouna/-ärä/-erA/-isA/-vA
    (
        10,
        r"( [aäoöuy]j[aä] | elä | m[aä] | o[ou]na | ärä | er[aä] | is[aä] | "
        r"v[aä] )$"
    ),
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

    # some of -Vli/-Vmi/-Vni/-Vri
    (6, r"( [aäeiou]l | [au]m | [aäei]n | [aäeiouy]r )i$"),
    (16, r"[eo]mpi$"),                                       # -empi/-ompi
    # -Ci except those in decl. 6, 16
    (5, r"[bcdfghjklmnpqrsštvwxzž]i$"),

    # === -CO/-CU ===

    (1, r"( (nk|nt|tt)[oö] | aisto | t[uy] )$"),  # -nkO/-ntO/-aisto/-ttO/-tU
    (4, r"kk[oö]$"),                              # -kkO
    # -CO/-CU except those in declensions 1, 4
    (2, r"[bcdfghjklmnpqrsštvwxzž][oöuy]$"),

    # === -C ===

    (32, r"t[aä]r$"),                               # -tAr
    (33, r"in$"),                                   # -in
    (34, r"t[oö]n$"),                               # -tOn
    (38, r"nen$"),                                  # -nen
    (40, r"[ioöuy][uy]s$"),                         # -iUs/-OUs/-UUs
    # -es/-is/-Os/-Us except those in decl. 40
    (39, r"[eioöuy]s$"),
    (41, r"[aä]s$"),                                # -As
    (47, r"[ln][uy]t$"),                            # -lUt/-nUt
    # -C except those in decl. 32-34, 38-41, 47
    (5,  r"[bcdfghjklmnpqrsštvwxzž]$"),
))

# rules for quadrisyllabic and longer nouns (declension, regex)
_RULES_4SYLL = tuple((d, re.compile(r, re.VERBOSE)) for (d, r) in (
    # === -VV ===

    (3,  r"[bcdfghjklmnpqrsštvwxzž]i[oö]$"),  # -CiO
    (12, r"[bcdfghjklmnpqrsštvwxzž][ei]a$"),  # -Cea/-Cia

    # === -CA ===

    # -akka/-ikka/-rkka/-lla/-iina/-inna/-ssa/-tA/-ža
    (9,  r"( [air]kka | lla | i[in]na | ssa | t[aä] | ža )$"),
    # -lijA/-nijA/-sijA/-tijA/-la
    (12, r"( [lnst]ij[aä] | la )$"),
    # -CA except those in declensions 9, 12
    (10, r"[bcdfghjklmnpqrsštvwxzž][aä]$"),

    # === -Ci ===

    # some of -Vli, -Vmi, -Vri
    (
        6,
        r"( [gkp]el | [drt]um | [klnptv]ar | [dgknt]er | "
        r"(i|l|s|kt|st|tt)or )i$"
    ),
    # -Ci except those in declension 6
    (5, r"[bcdfghjklmnpqrsštvwxzž]i$"),

    # === -CO/-CU ===

    (2, r"( m[oö] | l[uy] )$"),               # -mO/-lU
    (4, r"[dgjlmnprstv]ikk[oö]$"),            # -CikkO (not -kikko)
    # -CO/-CU excluding those in decl. 2, 4
    (1, r"[bcdfghjklmnpqrsštvwxzž][oöuy]$"),

    # === -C ===

    (32, r"t[aä]r$"),                               # -tAr
    (34, r"t[oö]n$"),                               # -tOn
    (38, r"nen(kin)?$"),                            # -nen(kin)
    (40, r"[iuy][uy]s$"),                           # -iUs/-UUs
    # -es/-is/-Os/-Us except those in decl. 40
    (39, r"[eioöuy]s$"),
    (41, r"[aä]s$"),                                # -As
    (47, r"n[uy]t$"),                               # -nUt
    # -C except those in decl. 32, 34, 38-41, 47
    (5, r"[bcdfghjklmnpqrsštvwxzž]$"),
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

    rules = [_RULES_1SYLL, _RULES_2SYLL, _RULES_3SYLL, _RULES_4SYLL][
        countsyll.count_syllables(noun)-1
    ]

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
