"""Determine whether consonant gradation applies to a Finnish noun."""

import re, sys
import countsyll, noundecl

# TODO: print whether NomSg has weak or strong grade

# exceptions to rules - consonant gradation does not apply to these nouns;
# each item: (declension, noun); sort first by declension, then by noun
EXCEPTIONS_NO = {
    (1, "ampu"), (1, "auto"), (1, "bantu"), (1, "city"), (1, "deeku"), (1, "doku"),
    (1, "foto"), (1, "hutu"), (1, "hötö"), (1, "kurko"), (1, "laku"), (1, "lito"),
    (1, "moto"), (1, "naku"), (1, "näpy"), (1, "party"), (1, "patu"), (1, "pipo"),
    (1, "pirtu"), (1, "platy"), (1, "plootu"), (1, "proto"), (1, "royalty"),  (1, "rubato"),
    (1, "saku"), (1, "šinto"), (1, "sotu"), (1, "sökö"), (1, "teku"), (1, "tempo"),
    (1, "tipu"), (1, "toto"), (1, "vibrato"), (1, "zloty"),

    (5, "graffiti"), (5, "hanti"), (5, "jämtti"), (5, "liti"), (5, "luti"), (5, "pieti"),
    (5, "preteriti"), (5, "satikuti"), (5, "toti"), (5, "vapiti"),

    (8, "raclette"),

    (9, "akvatinta"), (9, "basilika"), (9, "data"), (9, "delta"), (9, "emerita"), (9, "inka"),
    (9, "pampa"), (9, "prostata"), (9, "taata"), (9, "tanka"), (9, "toccata"),

    (10, "dorka"), (10, "jytä"), (10, "meikä"), (10, "moka"), (10, "nuuka"), (10, "perestroika"),
    (10, "poka"), (10, "pökä"), (10, "toka"),

    (33, "kaivin"),

    (41, "kallis"),

    (48, "aave"), (48, "alje"), (48, "haave"), (48, "harre"), (48, "hie"), (48, "hynte"),
    (48, "hyve"), (48, "ohje"), (48, "ruhje"), (48, "rynte"), (48, "rääpe"), (48, "toive"),
    (48, "vihje"), (48, "väive"),
}

# exceptions to rules - consonant gradation applies to these nouns;
# each item: (declension, noun); sort first by declension, then by noun
EXCEPTIONS_YES = {
    (1, "kopu"), (1, "kupo"), (1, "kupu"), (1, "ropo"), (1, "sopu"), (1, "vihko"),

    (5, "hupi"), (5, "laki"), (5, "pelti"), (5, "pop"), (5, "raati"), (5, "vati"),

    (8, "siitake"),

    (9, "hieta"), (9, "lieka"), (9, "nahka"),

    (10, "tuhka"), (10, "uhka"),

    (28, "jälsi"),

    (32, "ien"),

    (33, "hapan"), (33, "kerroin"), (33, "laidun"), (33, "puin"), (33, "pyyhin"), (33, "särvin"),

    (35, "lämmin"),

    (39, "havas"), (39, "kallas"), (39, "pallas"),

    (41, "havas"), (41, "ies"), (41, "kinnas"), (41, "kiuas"), (41, "oas"), (41, "ruis"),
    (41, "rynnäs"), (41, "ryväs"), (41, "seiväs"), (41, "vannas"), (41, "varas"), (41, "varvas"),
    (41, "äes"),

    (43, "immyt"),

    (48, "helve"), (48, "hiue"), (48, "karve"), (48, "lumme"), (48, "pyyhe"), (48, "tarve"),
    (48, "turve"),

    (49, "kannel"), (49, "säen"),
}

# consonant gradation applies to a noun if the noun and its declension match any of these rules;
# that is, the order of the rules doesn't matter; each rule: (declension, regex)
RULES = (
    # -VV
    (48, r"[aäio]e$"),

    # -CV (many false positives in decl. 1)
    ( 1, r"( [aeiouyäöklnr]k | [aäeilmpr]p | [aeiouyäöhlnrt]t )[oöuy]$"),
    ( 4, r"kk[oö]$"),
    ( 5, r"( [äey][kp] | [eiouyäö]t | [kn]k | [lp]p | [hnt]t )i$"),
    ( 7, r"( [aeiouyäöklnr]k | p | t )i$"),
    ( 8, r"( kk | pp | tt )e$"),
    ( 9, r"( [aiouyäölr][kpt] | [kn]k | [mp]p | [hnt]t )[aä]$"),
    (10, r"( [aeiouyäölr][kpt] | [kn]k | [mp]p | [hnt]t )[aä]$"),
    (14, r"( kk | pp | tt )[aä]$"),
    (16, r"mpi$"),
    (48, r"[aeiouyäö][dkptv]e$"),
    (48, r"( [lnr][kt] | h[dj] | l[jl] | mp | nn | rr )e$"),

    # -C
    (32, r"[nt][aä]r$"),
    (33, r"( [aeiouyäö][dtv] | hd | lj | ll | mm | nn | rr | lt )in$$"),
    (34, r"[aeiouyäö]t[oö]n$"),
    (41, r"( [aeiouyäölr][dkpt] | hd | ng | ll | mm | rr | nt )[aäiu]s$"),
    (49, r"( (va|mme)l | [dgn][ae]r )$"),
)

def get_consonant_gradation(noun, decl, useExceptions=True):
    """Does consonant gradation apply to the noun (str) in the specified declension (int)?
    return: bool"""

    # TODO: cons. grad of "siitake" should depend on declension; parse XML better

    if useExceptions:
        if (decl, noun) in EXCEPTIONS_NO:
            return False
        if (decl, noun) in EXCEPTIONS_YES:
            return True

    # a rule that depends on the number of syllables
    if decl == 1 and noun.endswith("to") and countsyll.count_syllables(noun) >= 4:
        return False

    return any(decl == d and re.search(r, noun, re.VERBOSE) is not None for (d, r) in RULES)

def main():
    # print warnings for redundant exceptions
    for (decl, noun) in sorted(EXCEPTIONS_NO):
        if not get_consonant_gradation(noun, decl, False):
            print(f"Redundant 'no' exception: '{noun}' in declension {decl}", file=sys.stderr)
    for (decl, noun) in sorted(EXCEPTIONS_YES):
        if get_consonant_gradation(noun, decl, False):
            print(f"Redundant 'yes' exception: '{noun}' in declension {decl}", file=sys.stderr)

    if len(sys.argv) != 2:
        sys.exit(
            "Argument: a Finnish noun (including adjectives/pronouns/numerals, excluding "
            "compounds) in nominative singular. Print the Kotus declension(s) (1-49) and whether "
            "consonant gradation applies."
        )
    noun = sys.argv[1]

    declensionsAndConsGradations = set()  # {(conjugation, consonant_gradation_applies), ...}
    for decl in noundecl.get_declensions(noun):
        declensionsAndConsGradations.add((decl, get_consonant_gradation(noun, decl)))

    if not declensionsAndConsGradations:
        sys.exit("Unrecognized noun.")

    for (decl, consGrad) in sorted(declensionsAndConsGradations):
        print(
            f'Declension {decl} (like "{noundecl.DECLENSION_DESCRIPTIONS[decl]}") '
            + ["without", "with"][consGrad] + " consonant gradation"
        )

if __name__ == "__main__":
    main()
