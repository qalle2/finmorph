"""Get the Kotus conjugation of a Finnish verb."""

# note: A = a/ä, O = o/ö, U = u/y, V = any vowel, C = any consonant

import re, sys

# a typical verb in each conjugation;
# forms: infinitive, 1SG present, 3SG past, 3SG conditional, 3SG imperative,
# singular perfect, passive past
CONJUGATION_DESCRIPTIONS = {
    52: "sano|a, -n, -i, -isi, -koon, -nut, -ttiin",
    53: "muis|taa, -tan, -ti, -taisi, -takoon, -tanut, -tettiin",
    54: "huu|taa, -dan, -si, -taisi, -takoon, -tanut, -dettiin",
    55: "sou|taa, -dan, -ti/-si, -taisi, -takoon, -tanut, -dettiin",
    56: "kaiv|aa, -an, -oi, -aisi, -akoon, -anut, -ettiin",
    57: "saar|taa, -ran, -si/-toi, -taisi, -takoon, -tanut, -rettiin",
    58: "lask|ea, -en, -i, -isi, -ekoon, -enut, -ettiin",
    59: "tun|tea, -nen, -si, -tisi, -tekoon, -tenut, -nettiin",
    60: "lä|hteä, -hden, -hti/-ksi, -htisi, -hteköön, -htenyt, -hdettiin",
    61: "salli|a, -n, -, -si, -koon, -nut, -ttiin",
    62: "voi|da, -n, -, -si, -koon, -nut, -tiin",
    63: "sa|ada, -an, -i, -isi, -akoon, -anut, -atiin",
    64: "j|uoda, -uon, -oi, -oisi, -uokoon, -uonut, -uotiin",
    65: "kä|ydä, -yn, -vi, -visi, -yköön, -ynyt, -ytiin",
    66: "rohkai|sta, -sen, -si, -sisi, -skoon, -ssut, -stiin",
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

# key = verb, value = tuple of conjugations
_MULTI_CONJUGATION_VERBS = {
    # different meanings
    "maistaa": (53, 56),
    #
    "keritä": (69, 75),
    #
    "isota": (72, 74),
    "sietä": (72, 74),
    "tyvetä": (72, 74),

    # same meanings
    "sortaa": (53, 54),
    "vuotaa": (53, 54),
    #
    "aueta": (72, 74),
    "iljetä": (72, 74),
    "juljeta": (72, 74),
    "oieta": (72, 74),
    "raueta": (72, 74),
    "sueta": (72, 74),
}

# exceptions to rules (verb: conjugation)
_EXCEPTIONS = {
    "elää": 53,
    "kuivaa": 53,
    "kylvää": 53,
    "kyntää": 53,
    "purkaa": 53,
    "sulaa": 53,

    "huutaa": 54,
    "lypsää": 54,
    "löytää": 54,
    "pieksää": 54,
    "pyytää": 54,

    # all the verbs in this conjugation
    "entää": 55,
    "hyytää": 55,
    "häätää": 55,
    "kiitää": 55,
    "liitää": 55,
    "soutaa": 55,
    "yltää": 55,

    "ahtaa": 56,
    "alkaa": 56,
    "antaa": 56,
    "auttaa": 56,
    "haistaa": 56,
    "jakaa": 56,
    "jaksaa": 56,
    "jatkaa": 56,
    "kantaa": 56,
    "kastaa": 56,
    "kattaa": 56,
    "laistaa": 56,
    "mahtaa": 56,
    "maksaa": 56,
    "mataa": 56,
    "maustaa": 56,
    "paistaa": 56,
    "sataa": 56,
    "virkkaa": 56,

    # all the verbs in this conjugation
    "kaartaa": 57,
    "kaataa": 57,
    "saartaa": 57,

    "tuntea": 59,  # the only verb in this conjugation

    "lähteä": 60,  # the only verb in this conjugation

    "säikkyä": 61,

    "hälinöidä": 62,

    "käydä": 65,  # the only verb in this conjugation

    # all the verbs in this conjugation
    "ahkeroida": 68,
    "aprikoida": 68,
    "aterioida": 68,
    "haravoida": 68,
    "hekumoida": 68,
    "hihhuloida": 68,
    "ikävöidä": 68,
    "ilakoida": 68,
    "ilkamoida": 68,
    "kapaloida": 68,
    "kapinoida": 68,
    "karkeloida": 68,
    "keikaroida": 68,
    "kekkaloida": 68,
    "kekkuloida": 68,
    "kihelmöidä": 68,
    "kipenöidä": 68,
    "kipunoida": 68,
    "koheloida": 68,
    "kuutioida": 68,
    "kyynelöidä": 68,
    "käpälöidä": 68,
    "kärhämöidä": 68,
    "liehakoida": 68,
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
    "seppelöidä": 68,
    "sukuloida": 68,
    "teikaroida": 68,
    "tupakoida": 68,
    "urakoida": 68,
    "vihannoida": 68,

    "hillitä": 69,
    "häiritä": 69,
    "villitä": 69,

    "hapata": 72,
    "heikota": 72,
    "helpota": 72,
    "hienota": 72,
    "huonota": 72,
    "kehnota": 72,
    "leudota": 72,
    "loitota": 72,
    "mädätä": 72,
    "paksuta": 72,
    "parata": 72,
    "ulota": 72,

    "haljeta": 74,
    "herjetä": 74,
    "hirvetä": 74,
    "hymytä": 74,
    "hyrskytä": 74,
    "hävetä": 74,
    "höyrytä": 74,
    "kammeta": 74,
    "kasketa": 74,
    "katketa": 74,
    "kehjetä": 74,
    "keretä": 74,
    "kerjetä": 74,
    "kiivetä": 74,
    "kivetä": 74,
    "korveta": 74,
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
    "ruveta": 74,
    "saveta": 74,
    "teljetä": 74,
    "tuketa": 74,
    "vyyhdetä": 74,
    "älytä": 74,
    "öljytä": 74,

    "aallota": 75,
    "bingota": 75,
    "diskota": 75,
    "haluta": 75,
    "hamuta": 75,
    "hulmuta": 75,
    "kohuta": 75,
    "lassota": 75,
    "lastuta": 75,
    "liesuta": 75,
    "lietsuta": 75,
    "loimuta": 75,
    "loiskuta": 75,
    "meluta": 75,
    "muodota": 75,
    "nimetä": 75,
    "nujuta": 75,
    "peitota": 75,
    "piiluta": 75,
    "röyhytä": 75,
    "solmita": 75,

    # all the verbs in this conjugation
    "taitaa": 76,
    "tietää": 76,
}

# rules for detecting the conjugation
# - format: (conjugation, regex)
# - sort by ending (first those that end with -AA, then others that end with
#   -A, etc.; all vowels before consonants)
# - tip: use a command like this to search for patterns:
#       grep "ENDING," verbs.csv | python3 text-util/grouplines.py -7

_RULES = tuple((c, re.compile(r, re.VERBOSE)) for (c, r) in (
    # -CAA (53 must be last)
    (54, "[lnr] t(aa|ää)$"),
    (56, "( aa | a[ai]h | aas | a[ailr]t )taa$ | [hjlnprv]aa$"),
    (53, "t(aa|ää)$"),

    # -VA (not -AA)
    (52, "[oöuy][aä]$"),
    (58, "e[aä]$"),
    (61, "i[aä]$"),

    # -dA (68 must be before 62)
    (68, "(im|in|nn|ri|äj) öidä$"),
    (62, "[aouö]i d[aä]$"),
    (63, "(aa|ää|yy) d[aä]$"),
    (64, "(ie|uo|yö) d[aä]$"),
    (71, "hdä$"),

    # -VtA (74 must be before 72 and 75; 69 must be before 75)
    (69, "( ita | [dkt]itä )$"),
    (73, "(ata|ätä)$"),
    (74, "( [dg]eta | [gt]etä | [oöu]t[aä] | [hn]ytä )$"),
    (72, "et[aä]$"),
    (75, "[iy]tä$"),

    # -stA (70 must be before 66)
    (70, "(ie|uo|yö) st[aä]$"),
    (66, "st[aä]$"),

    # -CA (not -tA)
    (67, "(ll|nn|rr) [aä]$"),
))

def get_conjugations(verb, useExceptions=True):
    """verb: a Finnish verb in infinitive
    return: a tuple of 0-2 Kotus conjugations (each 52-76)"""

    verb = verb.strip("'- ")

    try:
        return _MULTI_CONJUGATION_VERBS[verb]
    except KeyError:
        pass

    if useExceptions:
        try:
            return (_EXCEPTIONS[verb],)
        except KeyError:
            pass

    for (conjugation, regex) in _RULES:
        if regex.search(verb) is not None:
            return (conjugation,)
    return ()

def _check_redundant_exceptions():
    for verb in _EXCEPTIONS:
        detectedConjugations = get_conjugations(verb, False)
        if detectedConjugations \
        and _EXCEPTIONS[verb] == list(detectedConjugations)[0]:
            print(f'Redundant exception: "{verb}"')

def main():
    _check_redundant_exceptions()

    if len(sys.argv) != 2:
        sys.exit(
            "Argument: a Finnish verb (not a compound) in the infinitive. "
            "Print the Kotus conjugation(s) (52-76)."
        )
    verb = sys.argv[1]

    conjugations = get_conjugations(verb)
    if not conjugations:
        sys.exit("Unrecognized verb.")

    for c in sorted(conjugations):
        print(f'Conjugation {c} (like "{CONJUGATION_DESCRIPTIONS[c]}")')

if __name__ == "__main__":
    main()
