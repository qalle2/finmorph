"""Get the Kotus conjugation of a Finnish verb."""

# note: A = a/ä, O = o/ö, U = u/y, V = any vowel, C = any consonant

import re, sys
from countsyll import count_syllables

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

# These rules and exceptions specify how to detect the conjugation of a verb,
# based on how many syllables the verb has (3 means 3 or more).
# Notes - rules:
#   - Format: (declension, regex); the first matching regex will determine the
#     declension.
#   - "$" is automatically appended to the regexes, so put the whole regex in
#     parentheses if necessary.
#   - No more than one rule per declension per ending (e.g. -VV).
#   - Under each ending (e.g. -VV), if rules don't depend on each other, sort
#     them by declension.
#   - Don't hunt for any single verb. If the regex is e.g. [AB]C, each of AC
#     and BC must match 2 verbs or more. Exception: if [AB] forms a logical
#     group, like all the vowels, then only [AB]C needs to match 2 verbs or
#     more.
# Notes - exceptions:
#   - Format: verb: declension.
#   - Order: first by ending, then by declension.
#   - Begin a new line when declension changes.

# rules and exceptions for disyllabic verbs
_RULES_2SYLL = tuple((c, re.compile(r, re.VERBOSE)) for (c, r) in (
    # -AA
    (57, "aartaa$"),
    (54, "( [lnr]taa | sää | [lnr]tää )$"),  # must be after 57
    (55, "iitää$"),
    (56, "( [^t] | at | a[iu]?[hst]t | [lr]tt )aa$"),
    (53, "(aa|ää)$"),  # must be the last one

    # -dA
    (62, "ida$"),
    (63, "(aa|ää|yy) d[aä]$"),
    (64, "(ie|uo|yö) d[aä]$"),
    (71, "hdä$"),

    # -CA (not -dA)
    (70, "(ie|uo|yö) st[aä]$"),
    (66, "st[aä]$"),  # must be after 70
    (67, "(ll|nn|rr) [aä]$"),
    (73, "ata$"),
))
_EXCEPTIONS_2SYLL = {
    # -AA
    "kuivaa": 53, "kyntää": 53, "polttaa": 53, "purkaa": 53, "sulaa": 53,
    "taustaa": 53,
    "huutaa": 54, "löytää": 54, "pyytää": 54,
    "entää": 55, "hyytää": 55, "häätää": 55, "soutaa": 55, "yltää": 55,
    "antaa": 56, "kantaa": 56,
    "kaataa": 57,
    "taitaa": 76, "tietää": 76,

    # -CA
    "käydä": 65,
    "kaita": 69,
    "koota": 74, "pietä": 74,
    "siitä": 75,
}

# rules and exceptions for trisyllabic and longer verbs
_RULES_3SYLL = tuple((c, re.compile(r, re.VERBOSE)) for (c, r) in (
    # -VA
    (52, "[oöuy][aä]$"),
    (53, "[hst]t(aa|ää)$"),
    (54, "[lnr]t(aa|ää)$"),
    (58, "e[aä]$"),
    (61, "i[aä]$"),

    # -dA
    (68, "nnöidä$"),
    (62, "[aouö]i d[aä]$"),

    # -VtA
    (69, "(ita|kitä)$"),
    (74, "( get[aä] | ivetä | [oöu]t[aä] )$"),
    (72, "et[aä]$"),  # must be after 74
    (73, "(ata|ätä)$"),
    (75, "[iy]tä$"),

    # -CA (not -VtA)
    (66, "st[aä]$"),
    (67, "ll[aä]$"),
))
_EXCEPTIONS_3SYLL = {
    # -VA
    "tuntea": 59,
    "lähteä": 60,
    "säikkyä": 61,

    # -CA
    "ahkeroida": 68, "aprikoida": 68, "aterioida": 68, "haravoida": 68,
    "heilimöidä": 68, "hekumoida": 68, "hihhuloida": 68, "ikävöidä": 68,
    "ilakoida": 68, "ilkamoida": 68, "kapaloida": 68, "kapinoida": 68,
    "karkeloida": 68, "keikaroida": 68, "kekkaloida": 68, "kekkuloida": 68,
    "kihelmöidä": 68, "kipenöidä": 68, "kipinöidä": 68, "kipunoida": 68,
    "koheloida": 68, "kuutioida": 68, "kyynelöidä": 68, "käpälöidä": 68,
    "kärhämöidä": 68, "käräjöidä": 68, "liehakoida": 68, "luennoida": 68,
    "mankeloida": 68, "mellakoida": 68, "metelöidä": 68, "murkinoida": 68,
    "pakinoida": 68, "patikoida": 68, "pokkuroida": 68, "pomiloida": 68,
    "pullikoida": 68, "rettelöidä": 68, "rähinöidä": 68, "seppelöidä": 68,
    "sukuloida": 68, "teikaroida": 68, "tupakoida": 68, "urakoida": 68,
    "vihannoida": 68, "viheriöidä": 68,
    "hillitä": 69, "häiritä": 69, "kestitä": 69, "kyyditä": 69, "villitä": 69,
    "hapata": 72, "heikota": 72, "helpota": 72, "hienota": 72, "huonota": 72,
    "kehnota": 72, "leudota": 72, "loitota": 72, "mädätä": 72, "paksuta": 72,
    "parata": 72, "ulota": 72,
    "haljeta": 74, "herjetä": 74, "hirvetä": 74, "hymytä": 74, "hyrskytä": 74,
    "hävetä": 74, "höyrytä": 74, "kammeta": 74, "kasketa": 74, "katketa": 74,
    "kehjetä": 74, "keretä": 74, "kerjetä": 74, "korveta": 74, "könytä": 74,
    "laueta": 74, "lohjeta": 74, "loveta": 74, "lumeta": 74, "noeta": 74,
    "poiketa": 74, "puhjeta": 74, "ratketa": 74, "revetä": 74, "ristetä": 74,
    "ruveta": 74, "saveta": 74, "syyhytä": 74, "teljetä": 74, "todeta": 74,
    "tuketa": 74, "tähytä": 74, "vyyhdetä": 74, "älytä": 74, "öljytä": 74,
    "aallota": 75, "bingota": 75, "diskota": 75, "haluta": 75, "hamuta": 75,
    "hulmuta": 75, "kohuta": 75, "lassota": 75, "lastuta": 75, "liesuta": 75,
    "lietsuta": 75, "loimuta": 75, "loiskuta": 75, "meluta": 75, "muodota": 75,
    "nimetä": 75, "nujuta": 75, "peitota": 75, "piiluta": 75, "solmita": 75,
}

def get_conjugations(verb, useExceptions=True):
    """verb: a Finnish verb in infinitive
    return: a tuple of 0-2 Kotus conjugations (each 52-76)"""

    verb = verb.strip("'- ")

    try:
        return _MULTI_CONJUGATION_VERBS[verb]
    except KeyError:
        pass

    syllCnt = count_syllables(verb)

    if useExceptions:
        if syllCnt == 1:
            sys.exit("Error: there should be no monosyllabic verbs.")
        elif syllCnt == 2:
            exceptions = _EXCEPTIONS_2SYLL
        else:
            exceptions = _EXCEPTIONS_3SYLL
        try:
            return (exceptions[verb],)
        except KeyError:
            pass

    if syllCnt == 2:
        rules = _RULES_2SYLL
    else:
        rules = _RULES_3SYLL

    for (conjugation, regex) in rules:
        if regex.search(verb) is not None:
            return (conjugation,)
    return ()

def _get_redundant_exceptions():
    # generate verbs that are unnecessarily on the exceptions list
    for excList in (_EXCEPTIONS_2SYLL, _EXCEPTIONS_3SYLL):
        for verb in excList:
            detectedConjs = get_conjugations(verb, False)
            if detectedConjs and excList[verb] == list(detectedConjs)[0]:
                yield verb

def main():
    for noun in _get_redundant_exceptions():
        print(f"Redundant exception: '{noun}'", file=sys.stderr)

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
