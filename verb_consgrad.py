"""Determine whether consonant gradation applies to a Finnish verb."""

import re, sys
from verbconj import get_conjugations, CONJUGATION_DESCRIPTIONS

# exceptions to rules;
# (conjugation, noun): does_consonant_gradation_apply
_EXCEPTIONS = {
    (52, "lohkoa"): True,
    (52, "paapoa"): False,
    (52, "tutua"): False,
    (52, "tuutua"): False,
    (59, "tuntea"): True,  # the only verb in its conjugation
    (60, "lähteä"): True,  # the only verb in its conjugation
    (61, "futia"): False,
    (61, "pyyhkiä"): True,
    (61, "tutia"): False,
    (61, "vihkiä"): True,
    (66, "häväistä"): True,
    (66, "rangaista"): True,
    (66, "vavista"): True,
    (72, "halveta"): True,
    (72, "hiljetä"): False,
    (72, "huveta"): True,
    (72, "kalveta"): True,
    (72, "karjeta"): True,
    (72, "kaveta"): True,
    (72, "kevetä"): True,
    (72, "lämmetä"): True,
    (72, "rohjeta"): True,
    (72, "tarjeta"): True,
    (72, "ulota"): True,
    (72, "urjeta"): True,
    (72, "väljetä"): False,
    (73, "bodata"): False,
    (73, "bongata"): False,
    (73, "buuata"): False,
    (73, "dekoodata"): False,
    (73, "dokata"): False,
    (73, "evätä"): True,
    (73, "fudata"): False,
    (73, "futata"): False,
    (73, "halvata"): True,
    (73, "hengata"): False,
    (73, "huovata"): True,
    (73, "hylätä"): True,
    (73, "kaivata"): True,
    (73, "kammata"): True,
    (73, "karata"): True,
    (73, "kellata"): True,
    (73, "kelvata"): True,
    (73, "kerrata"): True,
    (73, "koodata"): False,
    (73, "kullata"): True,
    (73, "laata"): False,
    (73, "levätä"): True,
    (73, "luvata"): True,
    (73, "mokata"): False,
    (73, "mullata"): True,
    (73, "niiata"): False,
    (73, "pelätä"): True,
    (73, "perata"): True,
    (73, "petata"): False,
    (73, "prakata"): False,
    (73, "pykätä"): False,
    (73, "riiata"): False,
    (73, "roudata"): False,
    (73, "rynnätä"): True,
    (73, "salvata"): True,
    (73, "suunnata"): True,
    (73, "svengata"): False,
    (73, "sännätä"): True,
    (73, "tavata"): True,
    (73, "temmata"): True,
    (73, "trokata"): False,
    (73, "tsiikata"): False,
    (73, "uhata"): True,
    (73, "vallata"): True,
    (73, "verrata"): True,
    (73, "virrata"): True,
    (74, "herjetä"): True,
    (74, "hirvetä"): False,
    (74, "hävetä"): True,
    (74, "kammota"): False,
    (74, "kavuta"): True,
    (74, "keretä"): True,
    (74, "kerjetä"): True,
    (74, "kiivetä"): True,
    (74, "kivuta"): True,
    (74, "livetä"): True,
    (74, "revetä"): True,
    (74, "ruveta"): True,
    (74, "totota"): False,
    (74, "virota"): True,
    (74, "vivuta"): True,
    (75, "keritä"): True,
    (75, "pöllytä"): False,
    (75, "selitä"): True,
}

# consonant gradation applies to a verb if it matches the regex of its
# conjugation; if the conjugation is not listed, consonant gradation does not
# apply; key = conjugation, value = compiled regex
_RULES = dict((c, re.compile(r, re.VERBOSE)) for (c, r) in (
    (52, "( [aeiouyäölr][kpt] | [kn]k | [mp]p | [hnt]t )[ouy][aä]$"),
    (53, "( [aeiouyäö][kt] | rk | [hnrt]t )(aa|ää)$"),
    (54, "[aeiouyäölnr]t(aa|ää)$"),
    (55, "[aeiouyäöln]t(aa|ää)$"),
    (56, "( [akl]k | pp | [ahnt]t )aa$"),
    (57, "[ar]t(aa|ää)$"),
    (58, "( [aeiouyäölr][kpt] | nk )e[aä]$"),
    (61, "( [aeiouyäö][kpt] | [klnr]k | [lmpr]p | [hnt]t )[iy][aä]$"),
    (67, "( [adpr] | [ai]k | ll | mm | nn | [aeiouyäölr]t )ell[aä]$"),
    (72, "( nn | hd | lj | nk | rk | lp | [aeiouyäö][dkpt]? )[aeoä]t[aä]$"),
    (73, """
        ( hd | ng | lj | [lnr]k | [lmr]p | [lnr]t | [aeiouyäö][dkpt]? )
        (ata|ätä)$
    """),
    (74, """
        ( hd | ng | [hl]j | rk | mm | nn | [lm]p | rr | rv | [aeiou][dkpt]? )
        [eou]t[aä]$
    """),
    (75, "( i | ll | mm | [ioö][dpt] )[ioy]t[aä]$"),
    (76, "t(aa|ää)$"),
))

def get_consonant_gradation(verb, conj, useExceptions=True):
    """Returns whether consonant gradation applies to a Finnish verb in the
    specified declension.
    verb:          str
    conj:          Kotus conjugation (52-76)
    useExceptions: bool; should be True except for testing purposes
    return:        does consonant gradation apply? (bool)"""

    if useExceptions and (conj, verb) in _EXCEPTIONS:
        return _EXCEPTIONS[(conj, verb)]
    if conj not in _RULES:
        return False
    return re.search(_RULES[conj], verb) is not None

def main():
    # print warnings for redundant exceptions
    for (conj, verb) in sorted(_EXCEPTIONS):
        if _EXCEPTIONS[(conj, verb)] \
        == get_consonant_gradation(verb, conj, False):
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
