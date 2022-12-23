"""Determine whether consonant gradation applies to a Finnish verb."""

import re, sys
from verbconj import get_conjugations, CONJUGATION_DESCRIPTIONS

# Exceptions to rules. Notes:
#   - Format: {(conjugation, verb), ...}.
#   - Order: first by conjugation, then alphabetically.
#   - Start a new line when conjugation changes.
_EXCEPTIONS_NO = frozenset((
    (52, "paapoa"), (52, "tutua"), (52, "tuutua"),
    (56, "jatkaa"),
    (61, "futia"), (61, "tutia"),
    (72, "hiljetä"), (72, "väljetä"),
    (73, "bodata"), (73, "bongata"), (73, "buuata"), (73, "dekoodata"),
    (73, "dokata"), (73, "fudata"), (73, "futata"), (73, "hengata"),
    (73, "koodata"), (73, "laata"), (73, "mokata"), (73, "niiata"),
    (73, "petata"), (73, "prakata"), (73, "pykätä"), (73, "riiata"),
    (73, "roudata"), (73, "svengata"), (73, "trokata"), (73, "tsiikata"),
    (74, "hirvetä"), (74, "kammota"), (74, "totota"),
))
_EXCEPTIONS_YES = frozenset((
    (52, "lohkoa"),
    (53, "purkaa"),
    (59, "tuntea"),
    (60, "lähteä"),
    (61, "pyyhkiä"), (61, "vihkiä"),
    (66, "häväistä"), (66, "rangaista"), (66, "vavista"),
    (67, "jaella"), (67, "ommella"),
    (72, "halveta"), (72, "huveta"), (72, "kalveta"), (72, "karjeta"),
    (72, "kaveta"), (72, "kevetä"), (72, "kiinnetä"), (72, "loitota"),
    (72, "lämmetä"), (72, "rohjeta"), (72, "tarjeta"), (72, "ulota"),
    (72, "urjeta"),
    (73, "evätä"), (73, "halvata"), (73, "huovata"), (73, "hylätä"),
    (73, "kaivata"), (73, "kammata"), (73, "karata"), (73, "kellata"),
    (73, "kelvata"), (73, "kerrata"), (73, "kullata"), (73, "levätä"),
    (73, "luvata"), (73, "mullata"), (73, "pelätä"), (73, "perata"),
    (73, "rynnätä"), (73, "salvata"), (73, "suunnata"), (73, "sännätä"),
    (73, "tavata"), (73, "temmata"), (73, "uhata"), (73, "vallata"),
    (73, "verrata"), (73, "virrata"),
    (74, "herjetä"), (74, "hävetä"), (74, "kavuta"), (74, "keretä"),
    (74, "kerjetä"), (74, "kiivetä"), (74, "kivuta"), (74, "livetä"),
    (74, "revetä"), (74, "ruveta"), (74, "virota"), (74, "vivuta"),
    (75, "aallota"), (75, "hellitä"), (75, "keritä"), (75, "lämmitä"),
    (75, "muodota"), (75, "peitota"), (75, "ryöpytä"), (75, "selitä"),
    (75, "siitä"),
))

assert _EXCEPTIONS_NO.isdisjoint(_EXCEPTIONS_YES)

# These rules specify which verbs consonant gradation applies to in each
# conjugation. Notes:
#   - Format: {conjugation: compiledRegex, ...}.
#   - If the conjugation is not listed, consonant gradation does not apply.
#   - Don't hunt for any single verb. If the regex is e.g. [AB]C, each of AC
#     and BC must match 2 verbs or more. Exception: if [AB] forms a logical
#     group, like all the vowels, then only [AB]C needs to match 2 verbs or
#     more.
_RULES = dict((c, re.compile(r + "$", re.VERBOSE)) for (c, r) in (
    (52, "( [^hst]k | p | [^s]t )[oöuy][aä]"),
    (53, "[^s]t(aa|ää)"),
    (54, "t(aa|ää)"),
    (55, "t(aa|ää)"),
    (56, "( k | p | [^s]t )aa"),
    (57, "t(aa|ää)"),
    (58, "( [^st]k | p | t )e[aä]"),
    (61, "( [^hst]k | p | [^s]t )[iy][aä]"),
    (67, "( [dpr] | [^s][kt] | ll | nn )ell[aä]"),
    (72, "( d | lj | [^ht]k | p | [aeiouyäö] )[aeiouyäö]t[aä]"),
    (73, "( [^n]d | ng | lj | [^fhpst][kpt] | [aeiouyäö] ) (ata|ätä)"),
    (74, "( [aeioudg] | [hl]j | [^hst][kpt] | mm | nn | rr | rv ) [eou]t[aä]"),
    (76, "t(aa|ää)"),
))

def get_consonant_gradation(verb, conj, useExceptions=True):
    """Returns whether consonant gradation applies to a Finnish verb in the
    specified declension.
    verb:          str
    conj:          Kotus conjugation (52-76)
    useExceptions: bool; should be True except for testing purposes
    return:        does consonant gradation apply? (bool)"""

    if useExceptions:
        if (conj, verb) in _EXCEPTIONS_NO:
            return False
        if (conj, verb) in _EXCEPTIONS_YES:
            return True

    if conj not in _RULES:
        return False

    return re.search(_RULES[conj], verb) is not None

def _get_redundant_exceptions():
    # generate verbs that are unnecessarily listed as exceptions
    for (conj, verb) in _EXCEPTIONS_NO:
        if not get_consonant_gradation(verb, conj, False):
            yield (conj, verb)
    for (conj, verb) in _EXCEPTIONS_YES:
        if get_consonant_gradation(verb, conj, False):
            yield (conj, verb)

def main():
    for (conj, verb) in _get_redundant_exceptions():
        print(
            f"Redundant exception: '{verb}' in conjugation {conj}",
            file=sys.stderr
        )

    if len(sys.argv) != 2:
        sys.exit(
            "Argument: a Finnish verb (not a compound) in the infinitive. "
            "Print the Kotus conjugation(s) (52-78) and whether consonant "
            "gradation applies."
        )
    verb = sys.argv[1]

    conjsAndConsGrads = set()  # {(conjugation, cons_gradation_applies), ...}
    for conj in get_conjugations(verb):
        conjsAndConsGrads.add((conj, get_consonant_gradation(verb, conj)))

    if not conjsAndConsGrads:
        sys.exit("Unrecognized verb.")

    for (conj, consGrad) in sorted(conjsAndConsGrads):
        print(
            f"Conjugation {conj} "
            f'(like "{CONJUGATION_DESCRIPTIONS[conj]}") '
            + ("without", "with")[consGrad] + " consonant gradation"
        )

if __name__ == "__main__":
    main()
