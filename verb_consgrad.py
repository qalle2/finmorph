"""Determine whether consonant gradation applies to a Finnish verb."""

import re, sys
import verbconj

# TODO: print whether the infinitive has weak or strong grade

# exceptions to rules - consonant gradation does not apply to these verbs;
# each item: (conjugation, verb); sort first by conjugation, then by verb
EXCEPTIONS_NO = {
    (52, "paapoa"), (52, "tutua"), (52, "tuutua"),

    (61, "futia"), (61, "tutia"),

    (72, "hiljetä"), (72, "väljetä"),

    (73, "bodata"), (73, "buuata"), (73, "dekoodata"), (73, "dokata"), (73, "fudata"),
    (73, "futata"), (73, "koodata"), (73, "laata"), (73, "mokata"), (73, "niiata"),
    (73, "petata"), (73, "prakata"), (73, "pykätä"), (73, "riiata"), (73, "roudata"),
    (73, "trokata"), (73, "tsiikata"),

    (74, "hirvetä"), (74, "kammota"), (74, "totota"), (74, "öljytä"),
}

# exceptions to rules - consonant gradation applies to these verbs;
# each item: (conjugation, verb); sort first by conjugation, then by verb
EXCEPTIONS_YES = {
    (52, "lohkoa"),

    (53, "purkaa"),

    (56, "alkaa"), (56, "jakaa"), (56, "virkkaa"),

    (59, "tuntea"),

    (60, "lähteä"),

    (61, "pyyhkiä"), (61, "vihkiä"),

    (66, "häväistä"), (66, "rangaista"), (66, "vavista"),

    (67, "jaella"), (67, "leikellä"), (67, "nakella"), (67, "ommella"),

    (72, "halveta"), (72, "huveta"), (72, "kalveta"), (72, "karjeta"), (72, "kaveta"),
    (72, "kevetä"), (72, "kiinnetä"), (72, "lämmetä"), (72, "rohjeta"), (72, "tarjeta"),
    (72, "ulota"), (72, "urjeta"),

    (73, "evätä"), (73, "halvata"), (73, "hangata"), (73, "huovata"), (73, "hylätä"),
    (73, "kaivata"), (73, "kammata"), (73, "karata"), (73, "kellata"), (73, "kelvata"),
    (73, "kerrata"), (73, "kullata"), (73, "langata"), (73, "luvata"), (73, "levätä"),
    (73, "mullata"), (73, "pelätä"), (73, "perata"), (73, "rynnätä"), (73, "salvata"),
    (73, "suunnata"), (73, "sännätä"), (73, "tavata"), (73, "temmata"), (73, "tingata"),
    (73, "uhata"), (73, "vallata"), (73, "verrata"), (73, "virrata"), (73, "vängätä"),

    (74, "herjetä"), (74, "hävetä"), (74, "innota"), (74, "kavuta"), (74, "keretä"),
    (74, "kerjetä"), (74, "kiivetä"), (74, "kivuta"), (74, "livetä"), (74, "revetä"),
    (74, "ruveta"), (74, "virota"), (74, "vivuta"),

    (75, "aallota"), (75, "hellitä"), (75, "keritä"), (75, "lämmitä"), (75, "selitä"),

    (76, "taitaa"), (76, "tietää"),

    (78, "tuikkaa"),
}

assert EXCEPTIONS_NO.isdisjoint(EXCEPTIONS_YES)

# consonant gradation applies to a verb if the verb and its conjugation match any of these rules;
# that is, the order of the rules doesn't matter; each rule: (conjugation, regex)
RULES = (
    # -VA
    ((52, 58, 61), r"( [aeiouyäölr][kpt] | [kn]k | [mp]p | [hnt]t )[eiouy][aä]$"),
    ((53, 54, 55, 57), r"[aeiouyäöhlnrt]t[aä][aä]$"),
    ((56,), r"( pp | [ahnt]t )aa$"),

    # -llA
    ((67,), r"( [dpr] | ll | nn | [aeiouyäölr]t )ell[aä]$"),

    # -VtA (many false positives in conj. 73; many false negatives in conj. 72-74)
    ((72,73,74,75), r"( hd | lj | [lnr]k | [lmr]p | [lnr]t )[aäeiouy]t[aä]$"),
    ((72,73,74,75), r"[aeiouyäö][dkpt]?[aäeiouy]t[aä]$"),
    ((74,), r"( hj | ng | mm | rr | rv )[eou]t[aä]$"),
)

def get_consonant_gradation(verb, conj, useExceptions=True):
    """Does consonant gradation apply to the verb (str) in the specified conjugation (int)?
    return: bool"""

    if useExceptions:
        if (conj, verb) in EXCEPTIONS_NO:
            return False
        if (conj, verb) in EXCEPTIONS_YES:
            return True

    return any(conj in c and re.search(r, verb, re.VERBOSE) is not None for (c, r) in RULES)

def main():
    # print warnings for redundant exceptions
    for (conj, verb) in sorted(EXCEPTIONS_NO):
        if not get_consonant_gradation(verb, conj, False):
            print(f"Redundant 'no' exception: '{verb}' in conjugation {conj}", file=sys.stderr)
    for (conj, verb) in sorted(EXCEPTIONS_YES):
        if get_consonant_gradation(verb, conj, False):
            print(f"Redundant 'yes' exception: '{verb}' in conjugation {conj}", file=sys.stderr)

    if len(sys.argv) != 2:
        sys.exit(
            "Argument: a Finnish verb (not a compound) in the infinitive. Print the Kotus "
            "conjugation(s) (52-78) and whether consonant gradation applies."
        )
    verb = sys.argv[1]

    conjugationsAndConsGradations = set()  # {(conjugation, consonant_gradation_applies), ...}
    for conj in verbconj.get_conjugations(verb):
        conjugationsAndConsGradations.add((conj, get_consonant_gradation(verb, conj)))

    if not conjugationsAndConsGradations:
        sys.exit("Unrecognized verb.")

    for (conj, consGrad) in sorted(conjugationsAndConsGradations):
        print(
            f'Conjugation {conj} (like "{verbconj.CONJUGATION_DESCRIPTIONS[conj]}") '
            + ["without", "with"][consGrad] + " consonant gradation"
        )

if __name__ == "__main__":
    main()
