"""Get the Kotus conjugation of a Finnish verb."""

# Notes:
# - A = a/ä, O = o/ö, U = u/y, V = any vowel, C = any consonant
# - We merge some conjugations:
#   - conjugation 68 ("tupakoida") to 62 ("voida"); 68 allows some additional forms
#     (e.g. "tupakoitsen" in addition to "tupakoin")
#   - conjugation 74 ("katketa") to 75 ("selvitä"); 74 allows some additional forms
#     (e.g. "katkeisi" in addition to "katkeaisi")

import re, sys
import countsyll

# a typical verb in each conjugation; forms: infinitive, 1SG present, 3SG past, 3SG conditional,
# 3SG imperative, singular perfect, passive past;
# exception: for 77/78, only some third person forms
CONJUGATION_DESCRIPTIONS = {
    52: "sano|a, -n, -i, -isi, -koon, -nut, -ttiin",
    53: "muist|aa, -an, -i, -aisi, -akoon, -anut, -ettiin",
    54: "huu|taa, -dan, -si, -taisi, -takoon, -tanut, -dettiin",
    55: "sou|taa, -dan, -ti/-si, -taisi, -takoon, -tanut, -dettiin",
    56: "kaiv|aa, -an, -oi, -aisi, -akoon, -anut, -ettiin",
    57: "saar|taa, -ran, -si/-toi, -taisi, -takoon, -tanut, -rettiin",
    58: "lask|ea, -en, -i, -isi, -ekoon, -enut, -ettiin",
    59: "tun|tea, -nen, -si, -tisi, -tekoon, -tenut, -nettiin",
    60: "läh|teä, -den, -ti/läksi, -tisi, -teköön, -tenyt, -dettiin",
    61: "salli|a, -n, -, -si, -koon, -nut, -ttiin",
    62: "voi|da, -n, -, -si, -koon, -nut, -tiin",
    63: "saa|da, -n, sai, saisi, -koon, -nut, -tiin",
    64: "juo|da, -n, joi, joisi, -koon, -nut, -tiin",
    65: "käy|dä, -n, kävi, kävisi, -köön, -nyt, -tiin",
    66: "rohkais|ta, -en, -i, -isi, -koon, -sut, -tiin",
    67: "tul|la, -en, -i, -isi, -koon, -lut, -tiin",
    69: "valit|a, -sen, -si, -sisi, -koon, valinnut, -tiin",
    70: "juo|sta, -ksen, -ksi, -ksisi, -skoon, -ssut, -stiin",
    71: "näh|dä, näen, näki, näkisi, -köön, -nyt, -tiin",
    72: "vanhe|ta, -nen, -ni, -nisi, -tkoon, -nnut, -ttiin",
    73: "sala|ta, -an, -si, -isi, -tkoon, -nnut, -ttiin",
    75: "selvi|tä, -än, -si, -äisi, -tköön, -nnyt, -ttiin",
    76: "tai|taa, -dan, -si, -taisi, -takoon, -nnut/-tanut, -dettiin",
    77: "kumajaa, kumaji, kumajaisi",
    78: "kaikaa, kaikaisi",
}

# key = verb, value = set of conjugations
_MULTI_CONJUGATION_VERBS = {
    # different meanings
    "maistaa": {53, 56},
    #
    "keritä": {69, 75},
    #
    "isota": {72, 75},
    "sietä": {72, 75},
    "tyvetä": {72, 75},

    # same meanings
    "sortaa": {53, 54},
    "vuotaa": {53, 54},
    #
    "aueta": {72, 75},
    "iljetä": {72, 75},
    "juljeta": {72, 75},
    "oieta": {72, 75},
    "raueta": {72, 75},
    "sueta": {72, 75},
}

# exceptions to rules (key = noun, value = conjugation)
# order: first by syllable count, then by ending, then by conjugation, then alphabetically
# note: if there are more than one line of words per conjugation, separate them with empty comment
#       lines ("#") for readability
_EXCEPTIONS = {
    # === disyllabic ===

    # -tAA
    "kyntää": 53, "taustaa": 53,
    "huutaa": 54, "löytää": 54, "pyytää": 54,
    "entää": 55, "häätää": 55, "hyytää": 55, "kiitää": 55, "liitää": 55, "soutaa": 55, "yltää": 55,
    "antaa": 56, "kantaa": 56,
    "kaartaa": 57, "kaataa": 57, "saartaa": 57,
    "taitaa": 76, "tietää": 76,

    # -AA (not -tAA)
    "kuivaa": 53, "purkaa": 53, "sulaa": 53,
    #
    "lypsää": 54, "pieksää": 54,
    #
    "jaksaa": 56, "maksaa": 56, "virkkaa": 56,
    "jauhaa": 56,  # the only -hAA verb
    "nauraa": 56,  # the only -rAA verb
    "painaa": 56,  # the only -nAA verb
    #
    "telmää": 78,  # the only -mAA verb

    # -CA
    "käydä": 65,
    "kaita": 69,
    "nähdä": 71, "tehdä": 71,
    "koota": 75, "pietä": 75, "siitä": 75,

    # === trisyllabic ===

    # -VA
    "tuntea": 59,
    "lähteä": 60,
    "säikkyä": 61,

    # -AtA
    "hapata": 72, "mädätä": 72, "parata": 72,

    # -etA
    "haljeta": 75, "herjetä": 75, "hirvetä": 75, "hävetä": 75, "kammeta": 75, "kangeta": 75,
    "kasketa": 75, "katketa": 75, "kehjetä": 75, "keretä": 75, "kerjetä": 75, "kiivetä": 75,
    "kivetä": 75, "korveta": 75, "langeta": 75, "laueta": 75, "livetä": 75, "lohjeta": 75,
    "loveta": 75, "lumeta": 75, "nimetä": 75, "noeta": 75, "poiketa": 75, "puhjeta": 75,
    "ratketa": 75, "revetä": 75, "ristetä": 75, "ruveta": 75, "saveta": 75, "teljetä": 75,
    "todeta": 75, "tuketa": 75, "vyyhdetä": 75, "ängetä": 75,

    # -ita
    "solmita": 75,

    # -itä
    "häiritä": 69, "hillitä": 69, "kestitä": 69, "kyyditä": 69, "villitä": 69,

    # -ota
    "heikota": 72, "helpota": 72, "hienota": 72, "huonota": 72, "kehnota": 72, "leudota": 72,
    "loitota": 72, "ulota": 72,

    # -uta
    "paksuta": 72,

    # === quadrisyllabic and longer ===

    # -VA
    "hilsehtiä": 52,
    "pörhistyä": 61,
}

# note: rules in _RULES_2SYLL etc.:
# - sort by ending (first those that end with -AA, then others that end with -A, etc.; all vowels
#   before consonants)
# - each regex should match at least three verbs

# rules for disyllabic verbs (conjugation, regex)
_RULES_2SYLL = (
    # -AA
    (54, r"[lnr]t( aa | ää )$"),         # -ltAA/-ntAA/-rtAA
    (56, r"a[iu]?[lr]?[hst]?taa$"),      # -a(i/u)(l/r)(h/s/t)taa
    (53, r"( [ltv]ää | taa )$"),         # -lää/-tAA/-vää
    (56, r"( [jlpv]aa | a[lt]?kaa )$"),  # -jaa/-laa/-paa/-vaa; -a(l/t)kaa
    (78, r"[ks]( aa | ää )$"),           # -kAA/-sAA except those in conj. 56

    # -CA
    (63, r"( aa | ää | yy )d[aä]$"),   # -AAdA/-yydä
    (64, r"( ie | uo | yö )d[aä]$"),   # -iedA/-UOdA
    (62, r"id[aä]$"),                  # -idA
    (73, r"aata$"),                    # -aata
    (70, r"( ie | uo | yö )st[aä]$"),  # -iestA/-UOstA
    (66, r"st[aä]$"),                  # -stA except those in conj. 70
    (67, r"( ll | nn | rr )[aä]$"),    # -llA/-nnA/-rrA
)

# rules for trisyllabic verbs (conjugation, regex)
_RULES_3SYLL = (
    # -VV
    (77, r"j( aa | ää )$"),       # -jAA
    (53, r"[hst]t( aa | ää )$"),  # -htAA/-stAA/-ttAA
    (54, r"[lnr]t( aa | ää )$"),  # -ltAA/-ntAA/-rtAA
    (58, r"e[aä]$"),              # -eA
    (61, r"i[aä]$"),              # -iA
    (52, r"[oöuy][aä]$"),         # -OA/-UA
    (72, r"nee$"),                # -nee

    # -CV
    (62, r"[oö]id[aä]$"),             # -OidA
    (67, r"[ei]ll[aä]$"),             # -ellA/-illA
    (73, r"[aä]t[aä]$"),              # -AtA
    (72, r"et[aä]$"),                 # -etA (many are 75 instead)
    (69, r"( ita | kitä )$"),         # -ita/-kitä
    (75, r"( itä | [oöuy]t[aä] )$"),  # -itä/-OtA/-UtA
    (66, r"ist[aä]$"),                # -istA
)

# rules for quadrisyllabic and longer verbs (conjugation, regex)
_RULES_4SYLL = (
    # -VV
    (53, r"( is | [iuy]t )t( aa | ää )$"),  # -istAA/-ittAA/-UttAA
    (54, r"nt( aa | ää )$"),                # -ntAA
    (61, r"( ks | eht )i[aä]$"),            # -ksiA/-ehtiA
    (52, r"( ks | t )( ua | yä )$"),        # -ksUA/-tUA

    # -CV
    (62, r"[oö]id[aä]$"),        # -OidA
    (67, r"( e | ai )ll[aä]$"),  # -ellA/-ailla
    (73, r"[aä]t[aä]$"),         # -AtA
)

def get_conjugations(verb, useExceptions=True):
    """verb: a Finnish verb in infinitive
    return: a set of 0-2 Kotus conjugations (each 52-78)"""

    verb = verb.strip("'- ")

    try:
        return _MULTI_CONJUGATION_VERBS[verb]
    except KeyError:
        pass

    if useExceptions:
        try:
            return {_EXCEPTIONS[verb]}
        except KeyError:
            pass


    rules = [(), _RULES_2SYLL, _RULES_3SYLL, _RULES_4SYLL][countsyll.count_syllables(verb)-1]

    for (conjugation, regex) in rules:
        if re.search(regex, verb, re.VERBOSE) is not None:
            return {conjugation}

    return set()

def _check_redundant_exceptions():
    for verb in _EXCEPTIONS:
        detectedConjugations = get_conjugations(verb, False)
        if detectedConjugations and _EXCEPTIONS[verb] == list(detectedConjugations)[0]:
            print(f'Redundant exception: "{verb}"')

def main():
    _check_redundant_exceptions()

    if len(sys.argv) != 2:
        sys.exit(
            "Get the Kotus conjugation(s) (52-78) of a Finnish verb (not a compound). Argument: "
            "verb in infinitive"
        )
    verb = sys.argv[1]

    conjugations = get_conjugations(verb)
    if not conjugations:
        sys.exit("Unrecognized verb.")

    for c in sorted(conjugations):
        print(f'Conjugation {c} (like "{CONJUGATION_DESCRIPTIONS[c]}")')

if __name__ == "__main__":
    main()
