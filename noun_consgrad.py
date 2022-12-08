"""Determine whether consonant gradation applies to a Finnish noun."""

import re, sys
from noundecl import get_declensions, DECLENSION_DESCRIPTIONS

# exceptions to rules;
# (declension, noun): does_consonant_gradation_apply
_EXCEPTIONS = {
    (1, "allegretto"): False,
    (1, "ampu"): False,
    (1, "apartamento"): False,
    (1, "auto"): False,
    (1, "bantu"): False,
    (1, "city"): False,
    (1, "deeku"): False,
    (1, "doku"): False,
    (1, "esperanto"): False,
    (1, "foto"): False,
    (1, "hötö"): False,
    (1, "hutu"): False,
    (1, "kopu"): True,
    (1, "kupo"): True,
    (1, "kupu"): True,
    (1, "kurko"): False,
    (1, "laku"): False,
    (1, "lito"): False,
    (1, "mezzotinto"): False,
    (1, "moderato"): False,
    (1, "moto"): False,
    (1, "naku"): False,
    (1, "näpy"): False,
    (1, "party"): False,
    (1, "patu"): False,
    (1, "pipo"): False,
    (1, "pirtu"): False,
    (1, "pizzicato"): False,
    (1, "platy"): False,
    (1, "plootu"): False,
    (1, "proto"): False,
    (1, "ropo"): True,
    (1, "royalty"): False,
    (1, "rubato"): False,
    (1, "saku"): False,
    (1, "šinto"): False,
    (1, "sökö"): False,
    (1, "sopu"): True,
    (1, "sotu"): False,
    (1, "teku"): False,
    (1, "telefoto"): False,
    (1, "tempo"): False,
    (1, "tipu"): False,
    (1, "toto"): False,
    (1, "vibrato"): False,
    (1, "vihko"): True,
    (1, "zloty"): False,
    (5, "alpi"): False,
    (5, "graffiti"): False,
    (5, "hanti"): False,
    (5, "helpi"): False,
    (5, "hupi"): True,
    (5, "jämtti"): False,
    (5, "laki"): True,
    (5, "liti"): False,
    (5, "luti"): False,
    (5, "pelti"): True,
    (5, "pieti"): False,
    (5, "pop"): True,
    (5, "preteriti"): False,
    (5, "raati"): True,
    (5, "satikuti"): False,
    (5, "toti"): False,
    (5, "vapiti"): False,
    (5, "vati"): True,
    (8, "raclette"): False,
    (9, "akvatinta"): False,
    (9, "basilika"): False,
    (9, "data"): False,
    (9, "delta"): False,
    (9, "emerita"): False,
    (9, "hieta"): True,
    (9, "inka"): False,
    (9, "lieka"): True,
    (9, "nahka"): True,
    (9, "pampa"): False,
    (9, "prostata"): False,
    (9, "taata"): False,
    (9, "tanka"): False,
    (9, "toccata"): False,
    (10, "dorka"): False,
    (10, "jytä"): False,
    (10, "meikä"): False,
    (10, "moka"): False,
    (10, "nuuka"): False,
    (10, "perestroika"): False,
    (10, "poka"): False,
    (10, "pökä"): False,
    (10, "toka"): False,
    (10, "tuhka"): True,
    (10, "uhka"): True,
    (28, "jälsi"): True,
    (32, "ien"): True,
    (33, "hapan"): True,
    (33, "kaivin"): False,
    (33, "kerroin"): True,
    (33, "laidun"): True,
    (33, "näin"): True,
    (33, "puin"): True,
    (33, "pyyhin"): True,
    (33, "särvin"): True,
    (35, "lämmin"): True,
    (39, "havas"): True,
    (39, "kallas"): True,
    (39, "pallas"): True,
    (41, "äes"): True,
    (41, "havas"): True,
    (41, "ies"): True,
    (41, "kallis"): False,
    (41, "kinnas"): True,
    (41, "kiuas"): True,
    (41, "oas"): True,
    (41, "ruis"): True,
    (41, "rynnäs"): True,
    (41, "ryntys"): True,
    (41, "ryväs"): True,
    (41, "seiväs"): True,
    (41, "vannas"): True,
    (41, "varas"): True,
    (41, "varvas"): True,
    (43, "immyt"): True,
    (48, "aave"): False,
    (48, "alje"): False,
    (48, "haave"): False,
    (48, "helve"): True,
    (48, "hie"): False,
    (48, "hiue"): True,
    (48, "hyve"): False,
    (48, "karve"): True,
    (48, "lumme"): True,
    (48, "ohje"): False,
    (48, "pue"): True,
    (48, "pyyhe"): True,
    (48, "rääpe"): False,
    (48, "ruhje"): False,
    (48, "rynte"): False,
    (48, "tarve"): True,
    (48, "toive"): False,
    (48, "turve"): True,
    (48, "väive"): False,
    (48, "vihje"): False,
    (49, "auer"): True,
    (49, "kannel"): True,
    (49, "säen"): True,
}

# consonant gradation applies to a noun if it matches the regex of its
# declension; if the declension is not listed, consonant gradation does not
# apply; key = declension, value = compiled regex
_RULES = dict((d, re.compile(r, re.VERBOSE)) for (d, r) in (
    (1,  "( [aeiouyäöklnr]k | [aäeilmpr]p | [aeiouyäöhlnrt]t )[oöuy]$"),
    (4,  "kk[oö]$"),
    (5,  "( [äey][kp] | [eiouyäö]t | [kn]k | [lp]p | [hnt]t )i$"),
    (7,  "( [aeiouyäöklnr]k | p | t )i$"),
    (8,  "( kk | pp | tt )e$"),
    (9,  "( [aiouyäölr][kpt] | [kn]k | [mp]p | [hnt]t )[aä]$"),
    (10, "( [aeiouyäölr][kpt] | [kn]k | [mp]p | [hnt]t )[aä]$"),
    (14, "( kk | pp | tt )[aä]$"),
    (16, "mpi$"),
    (32, "[nt][aä]r$"),
    (33, "( [aeiouyäö][dtv] | hd | lj | ll | mm | nn | rr | lt )in$$"),
    (34, "[aeiouyäö]t[oö]n$"),
    (41, "( [aeiouyäölr][dkpt] | hd | ng | ll | mm | rr | nt )[aäiu]s$"),
    (48, """
        ( [aäio]e$ )
        | ( [aeiouyäö][dkptv]e$ )
        | ( ( [lnr][kt] | h[dj] | l[jl] | mp | nn | rr )e$ )
    """),
    (49, "( (va|mme)l | [dgn][ae]r )$"),
))

def get_consonant_gradation(noun, decl, useExceptions=True):
    """Returns whether consonant gradation applies to a Finnish noun in the
    specified declension.
    noun:          str
    decl:          Kotus declension (1-49)
    useExceptions: bool; should be True except for testing purposes
    return:        does consonant gradation apply? (bool)"""

    if useExceptions and (decl, noun) in _EXCEPTIONS:
        return _EXCEPTIONS[(decl, noun)]
    if decl not in _RULES:
        return False
    return re.search(_RULES[decl], noun) is not None

def main():
    # print warnings for redundant exceptions
    for (decl, noun) in sorted(_EXCEPTIONS):
        if _EXCEPTIONS[(decl, noun)] \
        == get_consonant_gradation(noun, decl, False):
            print(
                f"Redundant exception: '{noun}' in declension {decl}",
                file=sys.stderr
            )

    if len(sys.argv) != 2:
        sys.exit(
            "Argument: a Finnish noun (including adjectives/pronouns/"
            "numerals, excluding compounds) in nominative singular. Print "
            "the Kotus declension(s) (1-49) and whether consonant gradation "
            "applies."
        )
    noun = sys.argv[1]

    declsAndConsGrads = set()  # {(conjugation, cons_gradation_applies), ...}
    for decl in get_declensions(noun):
        declsAndConsGrads.add((decl, get_consonant_gradation(noun, decl)))

    if not declsAndConsGrads:
        sys.exit("Unrecognized noun.")

    for (decl, consGrad) in sorted(declsAndConsGrads):
        print(
            f"Declension {decl} "
            f'(like "{DECLENSION_DESCRIPTIONS[decl]}") '
            + ["without", "with"][consGrad] + " consonant gradation"
        )

if __name__ == "__main__":
    main()
