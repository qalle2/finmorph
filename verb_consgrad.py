import re, sys
import verbconj

EXCEPTIONS = {
    # -tVA
    "futia": False, "tutia": False, "tutua": False, "tuutua": False,

    # -kVA/-pVA
    "alkaa": True, "jakaa": True, "lohkoa": True, "pyyhkiä": True, "tuikkaa": True, "vihkiä": True,
    "virkkaa": True,
    #
    "paapoa": False,

    # -VVtA
    "siitä": True,
    "buuata": False, "laata": False, "niiata": False, "riiata": False,

    # -dVtA/-gVtA
    "bingota": False, "blandata": False, "blondata": False, "bodata": False, "bongata": False,
    "dekoodata": False, "fudata": False, "gryndata": False, "hengata": False, "koodata": False,
    "roudata": False, "svengata": False,

    # -hVtA
    "uhata": True,

    # -jVtA
    "hyljätä": True, "peljätä": True,
    #
    "hiljetä": False, "hurjeta": False, "norjeta": False, "sorjeta": False, "tyhjetä": False,
    "väljetä": False,

    # -kVtA/-pVtA/-tVtA
    "dokata": False, "futata": False, "mokata": False, "petata": False, "prakata": False,
    "pykätä": False, "totota": False, "trokata": False, "tsiikata": False,

    # -lVtA
    "aallota": True, "hellitä": True, "hylätä": True, "kellata": True, "kullata": True,
    "mullata": True, "pelätä": True, "selitä": True, "ulota": True, "vallata": True,

    # -mVtA
    "kammata": True, "kammeta": True, "kimmota": True, "kummuta": True, "lämmetä": True,
    "lämmitä": True, "sammota": True, "temmata": True,

    # -nVtA
    "innota": True, "kiinnetä": True, "rynnätä": True, "suunnata": True, "sännätä": True,

    # -rVtA
    "irrota": True, "karata": True, "keretä": True, "kerrata": True, "perata": True,
    "varrota": True, "verrata": True, "virota": True, "virrata": True,

    # -vVtA
    "evätä": True, "halvata": True, "halveta": True, "hervota": True, "huovata": True,
    "huveta": True, "hävetä": True, "kaivata": True, "kalveta": True, "kaveta": True,
    "kavuta": True, "kelvata": True, "kevetä": True, "kiivetä": True, "kirvota": True,
    "kivuta": True, "korveta": True, "levätä": True, "livetä": True, "luvata": True,
    "revetä": True, "ruveta": True, "salvata": True, "tavata": True, "turvota": True,
    "vivuta": True,

    # -CtA
    "häväistä": True, "rangaista": True, "vavista": True,

    # -llA
    "jaella": True, "leikellä": True, "nakella": True, "ommella": True,
    #
    "anella": False, "elellä": False, "laulella": False, "painella": False, "palella": False,
    "sanella": False, "valella": False,
}

# TODO: reduce number of exceptions (take number of syllables into account?)
CONS_GRAD_REGEX = re.compile(r"""
    (
    [aeiouyäöhlnrt]t[aeiouyäö][aä]
    | ( [aeiouyäölr][kp] | [kn]k | [pm]p )[eiouy][aä]
    | ( [aeiouyäölr][kpt] | h?d | ng | nk | mp | nt | [aeiouyäö] )[aäeouy]t[aä]
    | [hlr]jet[aä]
    | ( [dlnpr] | [aeiouyäölr]t )ell[aä]
    | ( rk | pp )aa
    )$
""", re.VERBOSE)

def get_consonant_gradation(verb, conj):
    """Does consonant gradation apply to the verb (str) in the specified conjugation (int)?
    return: bool"""

    # the only verb to which consonant graduation applies in some but not all conjugations
    if verb == "keritä" and conj == 75:
        return True

    try:
        return EXCEPTIONS[verb]
    except KeyError:
        pass

    return CONS_GRAD_REGEX.search(verb) is not None

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
