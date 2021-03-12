"""Get the Kotus conjugation class of a Finnish verb.
Note: A = a/ä, O = o/ö, U = u/y, V = any vowel, C = any consonant"""

import re
import sys

# a typical verb in each class, in infinitive and 3SG past (from Kotus)
CLASS_DESCRIPTIONS = {
    52: ("sanoa",     "sanoi"),
    53: ("muistaa",   "muisti"),
    54: ("huutaa",    "huusi"),
    55: ("soutaa",    "souti/sousi"),
    56: ("kaivaa",    "kaivoi"),
    57: ("saartaa",   "saarsi/saartoi"),
    58: ("laskea",    "laski"),
    59: ("tuntea",    "tunsi"),
    60: ("lähteä",    "lähti/(läksi)"),
    61: ("sallia",    "salli"),
    62: ("voida",     "voi"),
    63: ("saada",     "sai"),
    64: ("juoda",     "joi"),
    65: ("käydä",     "kävi"),
    66: ("rohkaista", "rohkaisi"),
    67: ("tulla",     "tuli"),
    68: ("tupakoida", "tupakoi/(tupakoitsi)"),
    69: ("valita",    "valitsi"),
    70: ("juosta",    "juoksi"),
    71: ("nähdä",     "näki"),
    72: ("vanheta",   "vanheni"),
    73: ("salata",    "salasi"),
    74: ("katketa",   "katkesi"),
    75: ("selvitä",   "selvisi"),
    76: ("taitaa",    "taisi"),
}

# verb: tuple with one or more conjugation classes
EXCEPTIONS = {
    # multiple classes with different meanings
    "isota":  (72, 74),
    "keritä": (69, 75),
    "sietä":  (72, 74),
    "tyvetä": (72, 74),

    # multiple classes with same meanings
    "aueta":   (72, 74),
    "iljetä":  (72, 74),
    "juljeta": (72, 74),
    "oieta":   (72, 74),
    "raueta":  (72, 74),
    "sortaa":  (53, 54),
    "sueta":   (72, 74),
    "vuotaa":  (53, 54),

    "hilsehtiä": (52,),

    "kuivaa": (53,),
    "kyntää": (53,),
    "purkaa": (53,),
    "sulaa":  (53,),

    "huutaa": (54,),
    "löytää": (54,),
    "pyytää": (54,),

    "hyytää": (55,),
    "häätää": (55,),
    "kiitää": (55,),
    "liitää": (55,),
    "soutaa": (55,),

    "ahtaa":   (56,),
    "alkaa":   (56,),
    "auttaa":  (56,),
    "haastaa": (56,),
    "haistaa": (56,),
    "jakaa":   (56,),
    "jaksaa":  (56,),
    "jatkaa":  (56,),
    "kaihtaa": (56,),
    "karttaa": (56,),
    "kastaa":  (56,),
    "kattaa":  (56,),
    "laistaa": (56,),
    "laittaa": (56,),
    "maattaa": (56,),
    "mahtaa":  (56,),
    "maistaa": (56,),
    "maittaa": (56,),
    "maksaa":  (56,),
    "malttaa": (56,),
    "mataa":   (56,),
    "maustaa": (56,),
    "naittaa": (56,),
    "paahtaa": (56,),
    "paistaa": (56,),
    "palttaa": (56,),
    "raastaa": (56,),
    "raataa":  (56,),
    "saattaa": (56,),
    "sataa":   (56,),
    "taittaa": (56,),
    "vaihtaa": (56,),
    "varttaa": (56,),
    "virkkaa": (56,),

    "entää": (55,),
    "yltää": (55,),

    "ajaa":   (56,),
    "antaa":  (56,),
    "kantaa": (56,),

    "kaartaa": (57,),
    "kaataa":  (57,),
    "saartaa": (57,),

    "tuntea": (59,),

    "lähteä": (60,),

    "pörhistyä": (61,),
    "säikkyä":   (61,),

    "jäädä": (63,),
    "myydä": (63,),
    "saada": (63,),

    "juoda": (64,),
    "luoda": (64,),
    "lyödä": (64,),
    "myödä": (64,),
    "suoda": (64,),
    "syödä": (64,),
    "tuoda": (64,),
    "viedä": (64,),

    "käydä": (65,),

    "ahkeroida":   (68,),
    "aprikoida":   (68,),
    "aterioida":   (68,),
    "emännöidä":   (68,),
    "haravoida":   (68,),
    "heilimöidä":  (68,),
    "hekumoida":   (68,),
    "hihhuloida":  (68,),
    "ikävöidä":    (68,),
    "ilakoida":    (68,),
    "ilkamoida":   (68,),
    "isännöidä":   (68,),
    "kapaloida":   (68,),
    "kapinoida":   (68,),
    "karkeloida":  (68,),
    "keikaroida":  (68,),
    "kekkaloida":  (68,),
    "kekkuloida":  (68,),
    "kihelmöidä":  (68,),
    "kipenöidä":   (68,),
    "kipinöidä":   (68,),
    "kipunoida":   (68,),
    "koheloida":   (68,),
    "kuutioida":   (68,),
    "kyynelöidä":  (68,),
    "käpälöidä":   (68,),
    "kärhämöidä":  (68,),
    "käräjöidä":   (68,),
    "liehakoida":  (68,),
    "liikennöidä": (68,),
    "luennoida":   (68,),
    "mankeloida":  (68,),
    "mellakoida":  (68,),
    "metelöidä":   (68,),
    "murkinoida":  (68,),
    "pakinoida":   (68,),
    "patikoida":   (68,),
    "pokkuroida":  (68,),
    "pomiloida":   (68,),
    "pullikoida":  (68,),
    "rettelöidä":  (68,),
    "rähinöidä":   (68,),
    "seppelöidä":  (68,),
    "sukuloida":   (68,),
    "teikaroida":  (68,),
    "tupakoida":   (68,),
    "urakoida":    (68,),
    "vihannoida":  (68,),
    "viheriöidä":  (68,),

    "juosta": (70,),
    "piestä": (70,),
    "syöstä": (70,),

    "nähdä": (71,),
    "tehdä": (71,),

    "hapata":  (72,),
    "heikota": (72,),
    "helpota": (72,),
    "hienota": (72,),
    "huonota": (72,),
    "kehnota": (72,),
    "leudota": (72,),
    "loitota": (72,),
    "mädätä":  (72,),
    "paksuta": (72,),
    "parata":  (72,),
    "ulota":   (72,),

    "haljeta":  (74,),
    "herjetä":  (74,),
    "hirvetä":  (74,),
    "hävetä":   (74,),
    "kammeta":  (74,),
    "kangeta":  (74,),
    "kasketa":  (74,),
    "katketa":  (74,),
    "kehjetä":  (74,),
    "keretä":   (74,),
    "kerjetä":  (74,),
    "kiivetä":  (74,),
    "kivetä":   (74,),
    "korveta":  (74,),
    "langeta":  (74,),
    "laueta":   (74,),
    "livetä":   (74,),
    "lohjeta":  (74,),
    "loveta":   (74,),
    "lumeta":   (74,),
    "noeta":    (74,),
    "pietä":    (74,),
    "poiketa":  (74,),
    "puhjeta":  (74,),
    "ratketa":  (74,),
    "revetä":   (74,),
    "ristetä":  (74,),
    "ruveta":   (74,),
    "saveta":   (74,),
    "teljetä":  (74,),
    "todeta":   (74,),
    "tuketa":   (74,),
    "vyyhdetä": (74,),
    "ängetä":   (74,),

    "eritä":   (75,),
    "hellitä": (75,),
    "hirvitä": (75,),
    "hävitä":  (75,),
    "levitä":  (75,),
    "lämmitä": (75,),
    "nimetä":  (75,),
    "pehmitä": (75,),
    "selitä":  (75,),
    "selvitä": (75,),
    "siitä":   (75,),
    "silitä":  (75,),
    "solmita": (75,),
    "viritä":  (75,),

    "aallota":  (75,),
    "bingota":  (75,),
    "diskota":  (75,),
    "haluta":   (75,),
    "hamuta":   (75,),
    "hulmuta":  (75,),
    "hälytä":   (75,),
    "jyrytä":   (75,),
    "kohuta":   (75,),
    "kärytä":   (75,),
    "lassota":  (75,),
    "lastuta":  (75,),
    "liesuta":  (75,),
    "lietsuta": (75,),
    "loimuta":  (75,),
    "loiskuta": (75,),
    "lyijytä":  (75,),
    "lymytä":   (75,),
    "meluta":   (75,),
    "muodota":  (75,),
    "myrskytä": (75,),
    "mölytä":   (75,),
    "möyrytä":  (75,),
    "nujuta":   (75,),
    "peitota":  (75,),
    "piiluta":  (75,),
    "pyrytä":   (75,),
    "pöllytä":  (75,),
    "pölytä":   (75,),
    "rymytä":   (75,),
    "ryöpytä":  (75,),
    "röyhytä":  (75,),
    "tyrskytä": (75,),

    "taitaa": (76,),
    "tietää": (76,),

    "läpsää": (78,),
}

# regex, conjugation class
ENDINGS = (
    ("(oa|öä|ua|yä)$",                  52),  # -OA/-UA
    ("([aeiouyäöhst]t(aa|ää)|[lv]ää)$", 53),  # -VtAA/-htAA/-stAA/-ttAA/-lää/-vää
    ("([lnr]t(aa|ää)|sää)$",            54),  # -ltAA/-ntAA/-rtAA/-sää
    ("[hlnprv]aa$",                     56),  # -haa/-laa/-naa/-paa/-raa/-vaa
    ("e[aä]$",                          58),  # -eA
    ("i[aä]$",                          61),  # -iA
    ("id[aä]$",                         62),  # -idA
    ("st[aä]$",                         66),  # -stA
    ("[lnr][aä]$",                      67),  # -lA/-nA/-rA
    ("it[aä]$",                         69),  # -itA
    ("(et[aä]|ee)$",                    72),  # -etA/-ee
    ("(ata|ätä)$",                      73),  # -AtA
    ("([ou]ta|[yö]tä)$",                74),  # -OtA/-UtA
    ("(jaa|jää)$",                      77),  # -jAA
    ("([ks]aa|[km]ää)$",                78),  # -kAA/-mää/-saa
)

def get_verb_class(verb):
    """verb: a Finnish verb in infinitive
    return: a tuple of zero, one or two Kotus conjugation classes (52...76)"""

    try:
        return EXCEPTIONS[verb]
    except KeyError:
        pass

    for (regex, conjugation) in ENDINGS:
        if re.search(regex, verb) is not None:
            return (conjugation,)

    return ()

def main():
    if len(sys.argv) != 2:
        sys.exit(
            "Get Kotus conjugation class(es) of a Finnish verb. Argument: verb in infinitive"
        )
    verb = sys.argv[1]

    conjugations = get_verb_class(verb)
    if len(conjugations) == 0:
        sys.exit("Unrecognized verb.")
    for c in conjugations:
        (infinitive, past) = CLASS_DESCRIPTIONS[c]
        print(f'conjugation {c} (like "{infinitive}" (3SG past "{past}"))')

if __name__ == "__main__":
    main()
