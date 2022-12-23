"""Determine whether consonant gradation applies to a Finnish noun."""

import re, sys
from noundecl import get_declensions, DECLENSION_DESCRIPTIONS

# Exceptions to rules. Notes:
#   - Format: {(declension, noun), ...}.
#   - Order: first by declension, then alphabetically.
#   - Start a new line when declension changes.
_EXCEPTIONS_NO = frozenset((
    (1, "allegretto"), (1, "ampu"), (1, "apartamento"), (1, "auto"),
    (1, "bantu"), (1, "city"), (1, "deeku"), (1, "doku"), (1, "esperanto"),
    (1, "foto"), (1, "hutu"), (1, "hötö"), (1, "kurko"), (1, "laku"),
    (1, "lito"), (1, "mezzotinto"), (1, "moderato"), (1, "moto"), (1, "naku"),
    (1, "näpy"), (1, "party"), (1, "patu"), (1, "pipo"), (1, "pirtu"),
    (1, "pizzicato"), (1, "platy"), (1, "plootu"), (1, "proto"),
    (1, "royalty"), (1, "rubato"), (1, "saku"), (1, "šinto"), (1, "sotu"),
    (1, "sökö"), (1, "teku"), (1, "telefoto"), (1, "tempo"), (1, "tipu"),
    (1, "toto"), (1, "vibrato"), (1, "zloty"),
    (5, "graffiti"), (5, "hanti"), (5, "jämtti"), (5, "liti"), (5, "luti"),
    (5, "pieti"), (5, "preteriti"), (5, "satikuti"), (5, "toti"),
    (5, "vapiti"),
    (8, "raclette"),
    (9, "akvatinta"), (9, "basilika"), (9, "data"), (9, "delta"),
    (9, "emerita"), (9, "inka"), (9, "pampa"), (9, "prostata"), (9, "taata"),
    (9, "tanka"), (9, "toccata"),
    (10, "dorka"), (10, "jytä"), (10, "meikä"), (10, "moka"), (10, "nuuka"),
    (10, "perestroika"), (10, "poka"), (10, "pökä"), (10, "toka"),
    (34, "alaston"),
    (48, "rääpe"), (48, "toive"), (48, "väive"),
))
_EXCEPTIONS_YES = frozenset((
    (1, "kopu"), (1, "kupo"), (1, "kupu"), (1, "ropo"), (1, "sopu"),
    (1, "vihko"),
    (5, "hupi"), (5, "laki"), (5, "pelti"), (5, "pop"), (5, "raati"),
    (5, "vati"),
    (9, "hieta"), (9, "lieka"), (9, "nahka"),
    (10, "tuhka"), (10, "uhka"),
    (28, "jälsi"),
    (32, "ien"),
    (33, "hapan"), (33, "kerroin"), (33, "laidun"), (33, "näin"),
    (33, "poltin"), (33, "puin"), (33, "pyyhin"), (33, "särvin"),
    (35, "lämmin"),
    (41, "altis"), (41, "havas"), (41, "kinnas"), (41, "kiuas"), (41, "oas"),
    (41, "raitis"), (41, "rynnäs"), (41, "ryväs"), (41, "seiväs"),
    (41, "vannas"), (41, "varas"), (41, "varvas"),
    (43, "immyt"),
    (48, "aie"), (48, "hanke"), (48, "helve"), (48, "hiue"), (48, "hynte"),
    (48, "koe"), (48, "kynte"), (48, "lumme"), (48, "pohje"), (48, "pue"),
    (48, "pyyhe"), (48, "säe"), (48, "säie"), (48, "turve"), (48, "vehje"),
    (49, "auer"), (49, "ommel"), (49, "penger"), (49, "säen"), (49, "taival"),
    (49, "udar"), (49, "vemmel"),
))

assert _EXCEPTIONS_NO.isdisjoint(_EXCEPTIONS_YES)

# These rules specify which nouns consonant gradation applies to in each
# declension. Notes:
#   - Format: {declension: compiledRegex, ...}.
#   - If the declension is not listed, consonant gradation does not apply.
#   - Don't hunt for any single noun. If the regex is e.g. [AB]C, each of AC
#     and BC must match 2 nouns or more. Exception: if [AB] forms a logical
#     group, like all the vowels, then only [AB]C needs to match 2 nouns or
#     more.
_RULES = dict((d, re.compile(r + "$", re.VERBOSE)) for (d, r) in (
    ( 1, "( [aeiouyäölnr][kt] | kk | [aäeilmpr]p | [ht]t )[oöuy]"),
    ( 4, "kk[oö]"),
    ( 5, "( [kn]k | pp | [eiouyäöhnt]t )i"),
    ( 7, "( [^st]k | p | t )i"),
    ( 8, "(kk|pp|tt) e"),
    ( 9, "( [aiulr][kpt]a | [kn]ka | [mp]pa | [hnt]ta | ntä )"),
    (10, "( [aeiouyäölr][kpt] | [kn]k | [mp]p | [hnt]t )[aä]"),
    (14, "(kk|pp|tt)[aä]"),
    (16, "mpi"),
    (32, "t[aä]r"),
    (33, "( [aeiouyäö]t | d | j | ll | nn | rr | av )in"),
    (34, "t[oö]n"),
    (41, """(
        ( [aeiouyäölr][kpt] | d | g | ll | mm | rr )[aä]
        | [iuä][ei] | [uy]
    )s"""),
    (48, """
        (
        a | d | (ah|l)j | [aeiouyäölr][kt] | ll | nn | p | rr | (ar|e|i|o|u)v
        )e
    """),
    (49, "nn[ae][lr]"),
))

def get_consonant_gradation(noun, decl, useExceptions=True):
    """Returns whether consonant gradation applies to a Finnish noun in the
    specified declension.
    noun:          str
    decl:          Kotus declension (1-49)
    useExceptions: bool; should be True except for testing purposes
    return:        does consonant gradation apply? (bool)"""

    if useExceptions:
        if (decl, noun) in _EXCEPTIONS_NO:
            return False
        if (decl, noun) in _EXCEPTIONS_YES:
            return True

    if decl not in _RULES:
        return False

    return re.search(_RULES[decl], noun) is not None

def _get_redundant_exceptions():
    # generate words that are unnecessarily listed as exceptions
    for (decl, noun) in _EXCEPTIONS_NO:
        if not get_consonant_gradation(noun, decl, False):
            yield (decl, noun)
    for (decl, noun) in _EXCEPTIONS_YES:
        if get_consonant_gradation(noun, decl, False):
            yield (decl, noun)

def main():
    for (decl, noun) in _get_redundant_exceptions():
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
