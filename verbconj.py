"""Get the Kotus conjugation of a Finnish verb.
Note: A = a/ä, O = o/ö, U = u/y, V = any vowel, C = any consonant"""

import re
import sys

# a typical verb in each conjugation; forms: infinitive, 1SG present, 3SG past, 3SG conditional,
# 3SG imperative, singular perfect, passive past
CONJUGATION_DESCRIPTIONS = {
    52: "sano|a, -n, -i, -isi, -koon, -nut, -ttiin",
    53: "muist|aa, -an, -i, -aisi, -akoon, -anut, -ettiin",
    54: "huu|taa, -dan, -si, -taisi, -takoon, -tanut, -dettiin",
    55: "sou|taa, -dan, -ti/-si, -taisi, -takoon, -tanut, -dettiin",
    56: "kaiv|aa, -an, -oi, -aisi, -akoon, -anut, -ettiin",
    57: "saar|taa, -ran, -si/-toi, -taisi, -takoon, -tanut, -rettiin",
    58: "lask|ea, -en, -i, -isi, -ekoon, -enut, -ettiin",
    59: "tun|tea, -nen, -si, -tisi, -tekoon, -tenut, -nettiin",
    60: "lä|hteä, -hden, -hti/-ksi, -htisi, -hteköön, -htenyt, -hdettiin",
    61: "sall|ia, -in, -i, -isi, -ikoon, -inut, -ittiin",
    62: "vo|ida, -in, -i, -isi, -ikoon, -inut, -itiin",
    63: "sa|ada, -an, -i, -isi, -akoon, -anut, -atiin",
    64: "j|uoda, -uon, -oi, -oisi, -uokoon, -uonut, -uotiin",
    65: "kä|ydä, -yn, -vi, -visi, -yköön, -ynyt, -ytiin",
    66: "rohkais|ta, -en, -i, -isi, -koon, -sut, -tiin",
    67: "tul|la, -en, -i, -isi, -koon, -lut, -tiin",
    68: "tupakoi|da, -(tse)n, -(tsi), -(tsi)si, -koon, -nut, -tiin",
    69: "vali|ta, -tsen, -tsi, -tsisi, -tkoon, -nnut, -ttiin",
    70: "juo|sta, -ksen, -ksi, -ksisi, -skoon, -ssut, -stiin",
    71: "nä|hdä, -en, -ki, -kisi, -hköön, -hnyt, -htiin",
    72: "vanhe|ta, -nen, -ni, -nisi, -tkoon, -nnut, -ttiin",
    73: "sala|ta, -an, -si, -isi, -tkoon, -nnut, -ttiin",
    74: "katke|ta, -an, -si, -(a)isi, -tkoon, -nnut, -ttiin",
    75: "selvi|tä, -än, -si, -äisi, -tköön, -nnyt, -ttiin",
    76: "tai|taa, -dan, -si, -taisi, -takoon, -nnut/-tanut, -dettiin",
}

# key = verb, value = set of conjugations
MULTI_CONJUGATION_VERBS = {
    # different meanings
    "keritä": {69, 75},
    #
    "isota": {72, 74},
    "sietä": {72, 74},
    "tyvetä": {72, 74},

    # same meanings
    "sortaa": {53, 54},
    "vuotaa": {53, 54},
    #
    "aueta": {72, 74},
    "iljetä": {72, 74},
    "juljeta": {72, 74},
    "oieta": {72, 74},
    "raueta": {72, 74},
    "sueta": {72, 74},
}

# key = verb, value = conjugation
# sort first by ending, then by conjugation, then alphabetically
EXCEPTIONS = {
    # === conjugations with less than three verbs ===

    "tuntea": 59,
    #
    "lähteä": 60,
    #
    "käydä": 65,
    #
    "nähdä": 71,
    "tehdä": 71,
    #
    "taitaa": 76,
    "tietää": 76,

    # === -VV ===

    # -tAA
    "kyntää": 53,
    #
    "huutaa": 54,
    "löytää": 54,
    "maantaa": 54,
    "pyytää": 54,
    #
    "entää": 55,
    "hyytää": 55,
    "häätää": 55,
    "kiitää": 55,
    "liitää": 55,
    "soutaa": 55,
    "yltää": 55,
    #
    "auttaa": 56,
    "maustaa": 56,
    #
    "kaartaa": 57,
    "kaataa": 57,
    "saartaa": 57,

    # -CAA (not -tAA)
    "elää": 53,
    "kuivaa": 53,
    "kylvää": 53,
    "purkaa": 53,
    "sulaa": 53,
    #
    "lypsää": 54,
    "pieksää": 54,
    #
    "ajaa": 56,
    "alkaa": 56,
    "jakaa": 56,
    "jaksaa": 56,
    "jatkaa": 56,
    "maksaa": 56,
    "virkkaa": 56,
    #
    "telmää": 78,

    # -VA (not -AA)
    "hilsehtiä": 52,
    #
    "pörhistyä": 61,
    "säikkyä": 61,

    # === -dA ===

    # -OidA
    "ahkeroida": 68,
    "aprikoida": 68,
    "aterioida": 68,
    "emännöidä": 68,
    "haravoida": 68,
    "heilimöidä": 68,
    "hekumoida": 68,
    "hihhuloida": 68,
    "ikävöidä": 68,
    "ilakoida": 68,
    "ilkamoida": 68,
    "isännöidä": 68,
    "kapaloida": 68,
    "kapinoida": 68,
    "karkeloida": 68,
    "keikaroida": 68,
    "kekkaloida": 68,
    "kekkuloida": 68,
    "kihelmöidä": 68,
    "kipenöidä": 68,
    "kipinöidä": 68,
    "kipunoida": 68,
    "koheloida": 68,
    "kuutioida": 68,
    "kyynelöidä": 68,
    "käpälöidä": 68,
    "kärhämöidä": 68,
    "käräjöidä": 68,
    "liehakoida": 68,
    "liikennöidä": 68,
    "luennoida": 68,
    "mankeloida": 68,
    "mellakoida": 68,
    "metelöidä": 68,
    "murkinoida": 68,
    "pakinoida": 68,
    "patikoida": 68,
    "pokkuroida": 68,
    "pomiloida": 68,
    "pullikoida": 68,
    "rettelöidä": 68,
    "rähinöidä": 68,
    "seppelöidä": 68,
    "sukuloida": 68,
    "teikaroida": 68,
    "tupakoida": 68,
    "urakoida": 68,
    "vihannoida": 68,
    "viheriöidä": 68,

    # === -tA ===

    # -AtA
    "hapata": 72,
    "mädätä": 72,
    "parata": 72,

    # -etA
    "haljeta": 74,
    "herjetä": 74,
    "hirvetä": 74,
    "hävetä": 74,
    "kammeta": 74,
    "kangeta": 74,
    "kasketa": 74,
    "katketa": 74,
    "kehjetä": 74,
    "keretä": 74,
    "kerjetä": 74,
    "kiivetä": 74,
    "kivetä": 74,
    "korveta": 74,
    "langeta": 74,
    "laueta": 74,
    "livetä": 74,
    "lohjeta": 74,
    "loveta": 74,
    "lumeta": 74,
    "noeta": 74,
    "pietä": 74,
    "poiketa": 74,
    "puhjeta": 74,
    "ratketa": 74,
    "revetä": 74,
    "ristetä": 74,
    "ruveta": 74,
    "saveta": 74,
    "teljetä": 74,
    "todeta": 74,
    "tuketa": 74,
    "vyyhdetä": 74,
    "ängetä": 74,
    #
    "nimetä": 75,

    # -itA
    "hellitä": 75,
    "hirvitä": 75,
    "lämmitä": 75,
    "pehmitä": 75,
    "selvitä": 75,
    "solmita": 75,

    # -OtA
    "heikota": 72,
    "helpota": 72,
    "hienota": 72,
    "huonota": 72,
    "kehnota": 72,
    "leudota": 72,
    "loitota": 72,
    "ulota": 72,
    #
    "aallota": 75,
    "bingota": 75,
    "diskota": 75,
    "lassota": 75,
    "muodota": 75,
    "peitota": 75,

    # -UtA
    "paksuta": 72,
    #
    "hymytä": 74,
    "hyrskytä": 74,
    "höyrytä": 74,
    "könytä": 74,
    "syyhytä": 74,
    "tähytä": 74,
    "älytä": 74,
    "öljytä": 74,
    #
    "haluta": 75,
    "hamuta": 75,
    "hulmuta": 75,
    "kohuta": 75,
    "lastuta": 75,
    "liesuta": 75,
    "lietsuta": 75,
    "loimuta": 75,
    "loiskuta": 75,
    "meluta": 75,
    "nujuta": 75,
    "piiluta": 75,
}

# regex, conjugation
# notes: each rule must apply to at least three verbs; one significant digit in numbers of verbs
RULES = (
    # -AA
    (r"^.?a[ai]?([hnst]?|[lr]t)taa$", 56),  # (?) + a/aa/ai + h/n/s/t/lt/rt + taa (  30 verbs)
    (r"[lnr]t(aa|ää)$",               54),  # -ltAA/-ntAA/-rtAA                   ( 300 verbs)
    (r"t(aa|ää)$",                    53),  # -tAA                                (3000 verbs)
    (r"[ks](aa|ää)$",                 78),  # -kAA/-sAA                           (  30 verbs)
    (r"j(aa|ää)$",                    77),  # -jAA                                (   3 verbs)
    (r"[hlnprv]aa$",                  56),  # h/l/n/p/r/v + aa                    (  10 verbs)
    # -VA (not -AA)
    (r"[oöuy][aä]$", 52),  # -OA/-UA (2000 verbs)
    (r"i[aä]$",      61),  # -iA     ( 400 verbs)
    (r"e[aä]$",      58),  # -eA     (  30 verbs)
    # -CtA
    (r"(ie|uo|yö)st[aä]$", 70),  # -iestA/-UOstA (  3 verbs)
    (r"st[aä]$",           66),  # -stA          (300 verbs)
    # -VtA
    (r"[aä]t[aä]$",     73),  # -AtA          (900 verbs)
    (r"et[aä]$",        72),  # -etA          (100 verbs)
    (r"[oöu]t[aä]$",    74),  # -OtA/-uta     (100 verbs)
    (r"(ita|....itä)$", 69),  # -ita/-????itä ( 50 verbs)
    (r"[iy]tä$",        75),  # -itä/-ytä     ( 20 verbs)
    # -CA (not -tA)
    (r"[lnr][aä]$",       67),  # -lA/-nA/-rA (1000 verbs)
    (r"(uo|yö|ie)d[aä]$", 64),  # -UOdA/-iedä (   8 verbs)
    (r"(aa|ää|yy)d[aä]$", 63),  # -AAdA/-yydä (   3 verbs)
    (r"d[aä]$",           62),  # -dA         ( 700 verbs)
    # -nee
    (r"nee$", 72),  # -nee (6 verbs)
)

def get_conjugations(verb, useExceptions=True):
    """verb: a Finnish verb in infinitive
    return: a set of zero, one or two Kotus conjugations (52...76)"""

    try:
        return MULTI_CONJUGATION_VERBS[verb]
    except KeyError:
        pass

    if useExceptions:
        try:
            return {EXCEPTIONS[verb]}
        except KeyError:
            pass

    for (regex, conjugation) in RULES:
        if re.search(regex, verb) is not None:
            return {conjugation}

    return set()

def check_redundant_exceptions():
    for verb in EXCEPTIONS:
        detectedConjugations = get_conjugations(verb, False)
        if detectedConjugations and EXCEPTIONS[verb] == list(detectedConjugations)[0]:
            print(f"Redundant exception: '{verb}'")

def main():
    check_redundant_exceptions()

    if len(sys.argv) != 2:
        sys.exit(
            "Get Kotus conjugation(s) of a Finnish verb. Argument: verb in infinitive"
        )
    verb = sys.argv[1]

    conjugations = get_conjugations(verb)
    if not conjugations:
        sys.exit("Unrecognized verb.")
    for c in conjugations:
        print(f'conjugation {c} (like "{CONJUGATION_DESCRIPTIONS[c]}")')

if __name__ == "__main__":
    main()
