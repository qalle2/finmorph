"""Detect the Kotus conjugation class of a Finnish verb.
Note: A = a/ä, O = o/ö, U = u/y, V = any vowel, C = any consonant"""

import re
import sys

# verb: tuple with one or more conjugation classes
EXCEPTIONS = {
    # multiple classes
    "isota":  (72, 74),
    "keritä": (69, 75),
    "sietä":  (72, 74),
    "tyvetä": (72, 74),

    # -VtAA
    #
    "huutaa": (54,),
    "löytää": (54,),
    "pyytää": (54,),
    "vuotaa": (54,),
    #
    "hyytää": (55,),
    "häätää": (55,),
    "kiitää": (55,),
    "liitää": (55,),
    "soutaa": (55,),
    #
    "mataa":  (56,),
    "raataa": (56,),
    "sataa":  (56,),
    #
    "kaataa": (57,),
    #
    "taitaa": (76,),
    "tietää": (76,),

    # -htAA
    "ahtaa":   (56,),
    "kaihtaa": (56,),
    "mahtaa":  (56,),
    "paahtaa": (56,),
    "vaihtaa": (56,),

    # -ltAA
    "yltää": (55,),

    # -ntAA
    #
    "kyntää": (53,),
    #
    "entää": (55,),
    #
    "antaa":  (56,),
    "kantaa": (56,),

    # -rtAA
    #
    "sortaa": (53,),
    #
    "kaartaa": (57,),
    "saartaa": (57,),

    # -stAA
    "haastaa": (56,),
    "haistaa": (56,),
    "kastaa":  (56,),
    "laistaa": (56,),
    "maistaa": (56,),
    "maustaa": (56,),
    "paistaa": (56,),
    "raastaa": (56,),

    # -ttAA
    "auttaa":  (56,),
    "karttaa": (56,),
    "kattaa":  (56,),
    "laittaa": (56,),
    "maattaa": (56,),
    "maittaa": (56,),
    "malttaa": (56,),
    "naittaa": (56,),
    "palttaa": (56,),
    "saattaa": (56,),
    "taittaa": (56,),
    "varttaa": (56,),

    # -CAA excluding -tAA
    #
    "elää":   (53,),
    "kuivaa": (53,),
    "kylvää": (53,),
    "purkaa": (53,),
    "sulaa":  (53,),
    #
    "lypsää":  (54,),
    "pieksää": (54,),

    # -VA excluding -AA
    #
    "hilsehtiä": (52,),
    #
    "tuntea": (59,),
    #
    "lähteä": (60,),
    #
    "pörhistyä": (61,),
    "säikkyä":   (61,),

    # -OidA
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

    # -VdA excluding -idA
    #
    "jäädä": (63,),
    "myydä": (63,),
    "saada": (63,),
    #
    "juoda": (64,),
    "luoda": (64,),
    "lyödä": (64,),
    "myödä": (64,),
    "suoda": (64,),
    "syödä": (64,),
    "tuoda": (64,),
    "viedä": (64,),
    #
    "käydä": (65,),

    # -hdA
    "nähdä": (71,),
    "tehdä": (71,),

    # -AtA
    "hapata": (72,),
    "mädätä": (72,),
    "parata": (72,),

    # -etA
    #
    "aueta":    (74,),
    "haljeta":  (74,),
    "herjetä":  (74,),
    "hirvetä":  (74,),
    "hävetä":   (74,),
    "iljetä":   (74,),
    "juljeta":  (74,),
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
    "oieta":    (74,),
    "pietä":    (74,),
    "poiketa":  (74,),
    "puhjeta":  (74,),
    "ratketa":  (74,),
    "raueta":   (74,),
    "revetä":   (74,),
    "ristetä":  (74,),
    "ruveta":   (74,),
    "saveta":   (74,),
    "sueta":    (74,),
    "teljetä":  (74,),
    "todeta":   (74,),
    "tuketa":   (74,),
    "vyyhdetä": (74,),
    "ängetä":   (74,),
    #
    "nimetä": (75,),

    # -itA
    "eritä":   (75,),
    "hellitä": (75,),
    "hirvitä": (75,),
    "hävitä":  (75,),
    "levitä":  (75,),
    "lämmitä": (75,),
    "pehmitä": (75,),
    "selitä":  (75,),
    "selvitä": (75,),
    "siitä":   (75,),
    "silitä":  (75,),
    "solmita": (75,),
    "viritä":  (75,),

    # -OtA/-UtA
    #
    "heikota": (72,),
    "helpota": (72,),
    "hienota": (72,),
    "huonota": (72,),
    "kehnota": (72,),
    "leudota": (72,),
    "loitota": (72,),
    "ulota":   (72,),
    "paksuta": (72,),
    #
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

    # -stA
    "juosta": (70,),
    "piestä": (70,),
    "syöstä": (70,),

    # incomplete verb (actually present 3SG form)
    "erkanee":  (72,),
    "karkenee": (72,),
    "korkenee": (72,),
    "mustenee": (72,),
    "paranee":  (72,),
    "ulkonee":  (72,),
}

# regex, conjugation class
ENDINGS = (
    ("([aeiouhst]taa|[eiyäöhst]tää)$", 53),  # -VtAA/-htAA/-stAA/-ttAA (~2700 verbs)
    ("[lnr]t(aa|ää)$", 54),                  # -ltAA/-ntAA/-rtAA       ( ~310 verbs)
    ("[hjklnprsv](aa|ää)$", 56),             #  -CAA excl. -tAA        (   20 verbs)
    ("e[aä]$", 58),                          #   -eA                   (   32 verbs)
    ("i[aä]$", 61),                          #   -iA                   (  400 verbs)
    ("[ouyö][aä]$", 52),                     #   -OA/-UA               (~2200 verbs)
    ("([aou]ida|öidä)$", 62),                # -VidA                   ( ~680 verbs)
    ("(ata|ätä)$", 73),                      #  -AtA                   ( ~910 verbs)
    ("et[aä]$", 72),                         #  -etA                   ( ~130 verbs)
    ("it[aä]$", 69),                         #  -itA                   (   48 verbs)
    ("([ou]ta|[yö]tä)$", 74),                #  -OtA/-UtA              ( ~130 verbs)
    ("st[aä]$", 66),                         #  -stA                   ( ~270 verbs)
    ("(ll|nn|rr)[aä]$", 67),                 #   -CA excl. -dA/-tA     (~1300 verbs)
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

assert get_verb_class("sanoa")     == (52,)
assert get_verb_class("muistaa")   == (53,)
assert get_verb_class("huutaa")    == (54,)
assert get_verb_class("soutaa")    == (55,)
assert get_verb_class("kaivaa")    == (56,)
assert get_verb_class("saartaa")   == (57,)
assert get_verb_class("laskea")    == (58,)
assert get_verb_class("tuntea")    == (59,)
assert get_verb_class("lähteä")    == (60,)
assert get_verb_class("sallia")    == (61,)
assert get_verb_class("voida")     == (62,)
assert get_verb_class("saada")     == (63,)
assert get_verb_class("juoda")     == (64,)
assert get_verb_class("käydä")     == (65,)
assert get_verb_class("rohkaista") == (66,)
assert get_verb_class("tulla")     == (67,)
assert get_verb_class("tupakoida") == (68,)
assert get_verb_class("valita")    == (69,)
assert get_verb_class("juosta")    == (70,)
assert get_verb_class("nähdä")     == (71,)
assert get_verb_class("vanheta")   == (72,)
assert get_verb_class("salata")    == (73,)
assert get_verb_class("katketa")   == (74,)
assert get_verb_class("selvitä")   == (75,)
assert get_verb_class("taitaa")    == (76,)

def main():
    if len(sys.argv) != 2:
        sys.exit(
            "Get Kotus conjugation class(es) of a Finnish verb. Argument: verb in infinitive"
        )
    verb = sys.argv[1]

    conjugation = get_verb_class(verb)
    if len(conjugation) == 0:
        sys.exit("Unrecognized verb.")
    elif len(conjugation) == 1:
        print(conjugation[0])
    else:
        print("/".join(str(c) for c in conjugation))

if __name__ == "__main__":
    main()
