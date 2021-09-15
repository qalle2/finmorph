import re, sys
import verbconj

# sort first by ending, starting from the last letter, then by False/True, then alphabetically
EXCEPTIONS = {
    # -VA
    "futia": False, "paapoa": False, "tutia": False, "tutua": False, "tuutua": False,
    #
    "alkaa": True, "jakaa": True, "lohkoa": True, "purkaa": True, "pyyhkiä": True, "tuikkaa": True,
    "vihkiä": True, "virkkaa": True,

    # -ellA
    "jaella": True, "leikellä": True, "nakella": True, "ommella": True,

    # -VVtA
    "buuata": False, "laata": False, "niiata": False, "riiata": False,
    #
    "siitä": True,

    # -VCVtA
    "bodata": False, "dekoodata": False, "dokata": False, "fudata": False, "futata": False,
    "koodata": False, "mokata": False, "petata": False, "prakata": False, "pykätä": False,
    "roudata": False, "totota": False, "trokata": False, "tsiikata": False,
    #
    "evätä": True, "huovata": True, "huveta": True, "hylätä": True, "hävetä": True,
    "kaivata": True, "karata": True, "kaveta": True, "kavuta": True, "keretä": True,
    "kevetä": True, "kiivetä": True, "kivuta": True, "levätä": True, "livetä": True,
    "luvata": True, "pelätä": True, "perata": True, "revetä": True, "ruveta": True, "selitä": True,
    "tavata": True, "uhata": True, "ulota": True, "virota": True, "vivuta": True,

    # -CCVtA
    "bongata": False, "hengata": False, "hiljetä": False, "hirvetä": False, "kammota": False,
    "pöllytä": False, "svengata": False, "väljetä": False, "öljytä": False,
    #
    "halvata": True, "halveta": True, "herjetä": True, "kalveta": True, "kammata": True,
    "karjeta": True, "kellata": True, "kelvata": True, "kerjetä": True, "kerrata": True,
    "kullata": True, "lämmetä": True, "mullata": True, "rohjeta": True, "rynnätä": True,
    "salvata": True, "suunnata": True, "sännätä": True, "tarjeta": True, "temmata": True,
    "urjeta": True, "vallata": True, "verrata": True, "virrata": True,

    # -stA
    "häväistä": True, "rangaista": True, "vavista": True,
}

# consonant gradation applies to a word if the word and its conjugation match any of these rules
# each rule: (tuple of conjugations (empty=any), regex)
RULES = (
    # == -VV ==

    ((), r"[aeiouyäöklnr]k[eioöuy][aä]$"),     # -V/-k/-l/-n/-r + keA/kiA/kOA/kUA
    ((), r"[aeiouyäölmpr]p[aeiouyäö][aä]$"),   # -V/-l/-m/-p/-r + pVA
    ((), r"[aeiouyäöhlnrt]t[aeiouyäö][aä]$"),  # -V/-h/-l/-n/-r/-t + tVA

    # == -llA ==

    ((), r"( [dpr] | ll | nn | [aeiouyäölr]t )ell[aä]$"),  # -d/-p/-r/-ll/-nn/-Vt/-lt/-rt + ellA

    # == -VVtA ==

    ((), r"[aeiouyäö][aäeoö]t[aä]$"),  # -VAtA/-VetA/-VOtA

    # == -VCVtA ==

    ((72, 73, 74, 75), r"[aeiouyäö][dkpt][aeiouyäö]t[aä]$"),  # -Vd/-Vk/-Vp/-Vt + VtA

    # == -CCVtA ==

    ((), r"( hd | lj | [mr]p | [lnr]t )[aeiouyäö]t[aä]$"),  # -hd/-lj/-mp/-rp/-lt/-nt/-rt + VtA
    ((72, 73), r"nk[aeiouyäö]t[aä]$"),                      # -nkVtA
    ((72, 73, 74), r"( rk | lp )[aeiouyäö]t[aä]$"),         # -rk/-lp + VtA
    ((72, 74), r"nn[aeiouyäö]t[aä]$"),                      # -nnVtA
    ((73,), r"lk[aeiouyäö]t[aä]$"),                         # -lkVtA
    ((73, 74), r"ng[aeiouyäö]t[aä]$"),                      # -ngVtA
    ((74,), r"( hj | rr | rv )[aeiouyäö]t[aä]$"),           # -hj/-rr/-rv + VtA
    ((74, 75), r"mm[aeiouyäö]t[aä]$"),                      # -mmVtA
    ((75,), r"ll[aeiouyäö]t[aä]$"),                         # -llVtA
)

def get_consonant_gradation(verb, conj):
    """Does consonant gradation apply to the verb (str) in the specified conjugation (int)?
    return: bool"""

    # the only verb to which consonant gradation applies in some but not all conjugations
    if verb == "keritä":
        return conj == 75

    try:
        return EXCEPTIONS[verb]
    except KeyError:
        pass

    return any(
        (not ruleConjus or conj in ruleConjus) and re.search(regex, verb, re.VERBOSE) is not None
        for (ruleConjus, regex) in RULES
    )

def main():
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
            + ["without", "with"][consGrad]
            + " consonant gradation"
        )

if __name__ == "__main__":
    main()
