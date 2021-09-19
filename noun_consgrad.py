import re, sys
import countsyll, noundecl

# TODO: print whether NomSg has weak or strong grade

# exceptions to rules; key = noun, value = whether consonant gradation applies;
# sort first by ending, starting from the last letter, then by False/True, then alphabetically
EXCEPTIONS = {
    # decl. 1
    "ampu": False, "auto": False, "bantu": False, "city": False, "deeku": False, "doku": False,
    "foto": False, "hutu": False, "hötö": False, "kurko": False, "laku": False, "lito": False,
    "moto": False, "naku": False, "näpy": False, "party": False, "patu": False, "pipo": False,
    "pirtu": False, "platy": False, "plootu": False, "proto": False, "royalty": False,
    "rubato": False, "saku": False, "šinto": False, "sotu": False, "sökö": False, "teku": False,
    "tempo": False, "tipu": False, "toto": False, "vibrato": False, "zloty": False,
    #
    "kopu": True, "kupo": True, "kupu": True, "ropo": True, "sopu": True, "vihko": True,

    # decl. 5
    "graffiti": False, "hanti": False, "jämtti": False, "liti": False, "luti": False,
    "pieti": False, "preteriti": False, "satikuti": False, "toti": False, "vapiti": False,
    #
    "hupi": True, "laki": True, "pelti": True, "pop": True, "raati": True, "vati": True,

    # decl. 8
    "raclette": False,
    #
    "siitake": True,

    # decl. 9
    "akvatinta": False, "basilika": False, "data": False, "delta": False, "emerita": False,
    "inka": False, "pampa": False, "prostata": False, "taata": False, "tanka": False,
    "toccata": False,
    #
    "hieta": True,
    "lieka": True,
    "nahka": True,

    # decl. 10
    "dorka": False, "jytä": False, "meikä": False, "moka": False, "nuuka": False,
    "perestroika": False, "poka": False, "pökä": False, "toka": False,
    #
    "setä": True, "tuhka": True, "uhka": True,

    # decl. 28
    "jälsi": True,

    # decl. 33
    "kaivin": False,
    #
    "hapan": True, "kerroin": True, "laidun": True, "puin": True, "pyyhin": True, "särvin": True,

    # decl. 32
    "ien": True,

    # decl. 35
    "lämmin": True,

    # decl. 39
    "havas": True, "kallas": True, "pallas": True,

    # decl. 41
    "kallis": False,
    #
    "ies": True, "kinnas": True, "kiuas": True, "oas": True, "ruis": True, "rynnäs": True,
    "ryväs": True, "seiväs": True, "vannas": True, "varas": True, "varvas": True, "äes": True,

    # decl. 43
    "immyt": True,

    # decl. 48
    "aave": False, "alje": False, "haave": False, "harre": False, "hie": False, "hynte": False,
    "hyve": False, "ohje": False, "ruhje": False, "rynte": False, "rääpe": False, "toive": False,
    "vihje": False, "väive": False,
    #
    "helve": True, "hiue": True, "karve": True, "lumme": True, "pyyhe": True, "tarve": True,
    "turve": True,

    # decl. 49
    "kannel": True, "säen": True,
}

# consonant gradation applies to a noun if the noun and its declension match any of these rules;
# that is, the order of the rules doesn't matter;
# each rule: (tuple of declensions (empty=any), regex)
RULES = (
    # == -VV ==

    ((48,), r"[aäio]e$"),

    # == -CV ==

    ((1,),     r"( [aeiouyäöklnr]k | [aäeilmpr]p | [aeiouyäöhlnrt]t )[oöuy]$"),
    ((4,),     r"kk[oö]$"),
    ((5,),     r"( [äey][kp] | [eiouyäö]t | [kn]k | [lp]p | [hnt]t )i$"),
    ((7,),     r"( [aeiouyäöklnr]k | p | t )i$"),
    ((8,),     r"( kk | pp | tt )e$"),
    ((9, 10,), r"( [aiouyäölr][kpt] | [kn]k | [mp]p | [hnt]t )[aä]$"),
    ((14,),    r"( kk | pp | tt )[aä]$"),
    ((16,),    r"mpi$"),
    ((48,),    r"[aeiouyäö][dkptv]e$"),
    ((48,),    r"( [lnr][kt] | h[dj] | l[jl] | mp | nn | rr )e$"),

    # == -C ==

    ((32,), r"[nt][aä]r$"),
    ((33,), r"( [aeiouyäö][dtv] | hd | lj | ll | mm | nn | rr | lt )in$$"),
    ((34,), r"[aeiouyäö]t[oö]n$"),
    ((41,), r"( [aeiouyäölr][dkpt] | hd | ng | ll | mm | rr | nt )[aäiu]s$"),
    ((49,), r"( (va|mme)l | [dgn][ae]r )$"),
)

def get_consonant_gradation(noun, decl):
    """Does consonant gradation apply to the noun (str) in the specified declension (int)?
    return: bool"""

    # TODO: cons. grad of "siitake" should depend on declension; parse XML better

    try:
        return EXCEPTIONS[noun]
    except KeyError:
        pass

    # a rule that depends on the number of syllables
    if decl == 1 and noun.endswith("to") and countsyll.count_syllables(noun) >= 4:
        return False

    return any(
        (not d or decl in d) and re.search(r, noun, re.VERBOSE) is not None for (d, r) in RULES
    )

def main():
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
