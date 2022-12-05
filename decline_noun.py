"""Decline a Finnish noun."""

import re, sys
from noun_consgrad import get_consonant_gradation
from noundecl import get_declensions

# - C = any consonant, V = any vowel, A = a/ä, O = o/ö, U = u/y
# - declensions (1-49) are from Kotus

# -----------------------------------------------------------------------------

# combinations of case/number that behave like genitive singular
_CASES_LIKE_GEN_SG = frozenset((
    ("nom", "pl"),
    ("gen", "sg"),
    ("tra", "sg"),
    ("ine", "sg"),
    ("ela", "sg"),
    ("ade", "sg"),
    ("abl", "sg"),
    ("all", "sg"),
    ("abe", "sg"),
))

# rules for changing endings of words
# - format: declension: ((regex_from, regex_to), ...)
# - "$" will be appended to regex_from
# - only the 1st match with regex_from will be applied
# - consonant gradation and case/number endings will be applied afterwards
# - for clarity, avoid making changes here that need to be undone later
#
_CHANGES_GEN_SG = {  # also _CASES_LIKE_GEN_SG, EssSg, IllSg
    5:  (("([^aeiouyäö])", r"\1i"),),   # risti, rock
    6:  (("([^aeiouyäö])", r"\1i"),),   # paperi, nylon
    7:  (("i",             "e"),),      # ovi
    10: (("n",             ""),),       # koira, kahdeksan
    16: (("^([^aou]+)i", r"\1ä"), ("i", "a")),  # vanhempi
    23: (("i",             "e"),),      # tiili
    24: (("i",             "e"),),      # uni
    25: (("i",             "e"),),      # toimi
    26: (("i",             "e"),),      # pieni
    27: (("si",            "te"),),     # käsi
    28: (("si",            "te"),),     # kynsi
    29: (("i",             "e"),),      # lapsi
    30: (("i",             "e"),),      # veitsi
    31: (("ksi",           "hte"),),    # kaksi
    32: (("nen", "ne"), ("([lnr])", r"\1e")),  # sisar, kymmenen
    33: (("n",             "me"),),     # kytkin
    34: (("^([^aou]+)n", r"\1mä"),  ("^([a-zäö]+)n", r"\1ma")),   # onneton
    35: (("^([^aou]+)n", r"\1mä"),  ("^([a-zäö]+)n", r"\1ma")),   # lämmin
    36: (("^([^aou]+)n", r"\1mmä"), ("^([a-zäö]+)n", r"\1mma")),  # sisin
    37: (("^([^aou]+)n", r"\1mmä"), ("^([a-zäö]+)n", r"\1mma")),  # vasen
    38: (("nen",           "se"),),     # nainen
    39: (("s",             "kse"),),    # vastaus
    40: (("s",             "te"),),     # kalleus
    41: (("([aeiouyäö])s", r"\1\1"),),  # vieras
    42: (("s",             "he"),),     # mies
    43: (("t",             "e"),),      # ohut
    44: (("t",             "ä"),),      # kevät
    45: (("s",             "nte"),),    # kahdeksas
    46: (("t",             "nte"),),    # tuhat
    47: (("[uy]t",         "ee"),),     # kuollut
    48: (("([aeiouyäö])",  r"\1\1"),),  # hame
    49: (("",              "e"),),      # askel, askele
}
_CHANGES_PAR_SG = {
    5:  (("([^aeiouyäö])", r"\1i"),),  # risti, rock
    6:  (("([^aeiouyäö])", r"\1i"),),  # paperi, nylon
    7:  (("i",             "e"),),     # ovi
    10: (("n",             ""),),      # koira, kahdeksan
    16: (("^([^aou]+)i", r"\1ä"), ("i", "a")),  # vanhempi
    23: (("i",             ""),),      # tiili
    24: (("i",             ""),),      # uni
    25: (("i",             ""),),      # toimi
    26: (("i",             ""),),      # pieni
    27: (("si",            "t"),),     # käsi
    28: (("si",            "t"),),     # kynsi
    29: (("[kp]si",        "s"),),     # lapsi
    30: (("tsi",           "s"),),     # veitsi
    31: (("ksi",           "h"),),     # kaksi
    32: (("nen",           "n"),),     # sisar, kymmenen
    38: (("nen",           "s"),),     # nainen
    40: (("s",             "t"),),     # kalleus
    45: (("s",             "t"),),     # kahdeksas
}
_CHANGES_GEN_PL = {  # also PartPl, IllPl
    5:  (("i",          ""),),     # risti, rock
    6:  (("i",          ""),),     # paperi, nylon
    7:  (("i",          ""),),     # ovi
    9:  (("a", "o"), ("ä", "ö")),  # kala
    10: (("[aä]n?",     ""),),     # koira, kahdeksan
    12: (("a", "o"), ("ä", "ö")),  # kulkija
    13: (("a", "o"), ("ä", "ö")),  # katiska
    14: (("a", "o"), ("ä", "ö")),  # solakka
    15: (("[aä]",       ""),),     # korkea
    16: (("i",          ""),),     # vanhempi
    17: (("[aeiouyäö]", ""),),     # vapaa
    18: (("[aeiouyäö]", ""),),     # maa
    19: (("ie", "e"), ("uo", "o"), ("yö", "ö")),  # suo
    20: (("[aeiouyäö]", ""),),     # filee
    23: (("i",          ""),),     # tiili
    24: (("i",          ""),),     # uni
    25: (("i",          ""),),     # toimi
    26: (("i",          ""),),     # pieni
    27: (("i",          ""),),     # käsi
    28: (("i",          ""),),     # kynsi
    29: (("i",          ""),),     # lapsi
    30: (("i",          ""),),     # veitsi
    31: (("i",          ""),),     # kaksi
    32: (("nen",        "n"),),    # sisar, kymmenen
    35: (("n",          "m"),),    # lämmin
    38: (("nen",        "s"),),    # nainen
    40: (("s",          "ks"),),   # kalleus
    41: (("s",          ""),),     # vieras
    43: (("t",          ""),),     # ohut
    44: (("t",          ""),),     # kevät
    45: (("s",          "ns"),),   # kahdeksas
    47: (("[uy]t",      "e"),),    # kuollut
}

def _change_ending(word, decl, case, number):
    # change the ending of the word (before applying consonant gradation or
    # adding case/number endings)

    # inflect irregular words as if they were another word
    if word == "paras" and not (case == "par" and number == "sg"):
        word = "parhas"
    elif word == "veli":
        word = "velji"

    # get regexes to apply
    if (case, number) in _CASES_LIKE_GEN_SG \
    or case in ("ess", "ill") and number == "sg":
        changes = _CHANGES_GEN_SG.get(decl, ())
    elif case == "par" and number == "sg":
        changes = _CHANGES_PAR_SG.get(decl, ())
    elif case in ("gen", "par", "ill") and number == "pl":
        changes = _CHANGES_GEN_PL.get(decl, ())
    else:
        sys.exit("error")

    # apply the first regex that matches
    for (regexFrom, regexTo) in changes:
        regexFrom += "$"
        if re.search(regexFrom, word) is not None:
            return re.sub(regexFrom, regexTo, word)
    return word

# -----------------------------------------------------------------------------

# rules for consonant gradation
# - format: (regex_from, regex_to)
# - "$" will be appended to regex_from
# - only the 1st match with regex_from will be applied
# - the final consonants and vowels have already been changed
#
# strong to weak
_CONS_GRAD_WEAKEN = tuple((re.compile(f + "$"), t) for (f, t) in (
    # k
    ("kk([aeiouyäö])",               r"k\1"),      # -kkV
    ("nk([aeiouyäö])",               r"ng\1"),     # -nkV
    ("ylkä",                         r"yljä"),     # -ylkä
    ("([lr])ke",                     r"\1je"),     # -lke/-rke
    (r"([aeiouyäö])([aeiouyäö])k\2", r"\1\2'\2"),  # -VVkV (2nd V = 3rd V)
    ("([klmps][uy])k([uy])",         r"\1v\2"),    # -CUkU
    ("([aeiouyäöhlr])k([aeiouyäö])", r"\1\2"),     # -VkV/-hkV/-lkV/-rkV
    # p
    ("pp([aeiouyäö])",               r"p\1"),    # -ppV
    ("mp([aeiouyäö])",               r"mm\1"),   # -mpV
    ("([aeiouyäölr])p([aeiouyäö])",  r"\1v\2"),  # -VpV/-lpV/-rpV
    # t
    ("tt([aeiouyäö])",             r"t\1"),     # -ttV
    ("([lnr])t([aeiouyäö])",       r"\1\1\2"),  # -ltV/-ntV/-rtV
    ("([aeiouyäöh])t([aeiouyäö])", r"\1d\2"),   # -VtV/-htV
))
#
# weak to strong
_CONS_GRAD_STRENGTHEN = tuple((re.compile(f + "$"), t) for (f, t) in (
    # k
    ("([aeiouyäölnr])k(aa?|ee?)",               r"\1kk\2"),  # tikas
    ("([aeiouyäö])ng(aa?|ää?|ere?)",            r"\1nk\2"),  # penger
    ("([hl])j(ee?|ime|in)",                     r"\1k\2"),   # hylje
    ("([aeiouyäöh])(ene?|ime|in)",              r"\1k\2"),   # säen
    ("([aeiouyäö]|ar)(aa|ee|ii)",               r"\1k\2"),   # ies
    ("(iu)([ae])",                              r"\1k\2"),   # kiuas
    ("(^[^aeiouyäö]?[aeiouyäö]|ai|var)([aei])", r"\1k\2"),   # ruis
    # p
    ("([aeiouyäölm])p(aa?|ää?|ee?|i|ame|an)",         r"\1pp\2"),  # ape
    ("([aeiouyäö])mm(aa?|ää?|ee?|yy?|ye|ele?|imä?)?", r"\1mp\2"),  # lämmin
    ("([aeiouyäölr])v(aa?|ää?|ee?|ale?|ime|in)",      r"\1p\2"),   # taival
    # t
    (r"([aeiouyäölnr])t(([aeiouyäö])\3?)",         r"\1tt\2"),  # altis
    ("([aeiouyäöl])t(ime|oma|ömä|[ioö]n|[aä]re?)", r"\1tt\2"),  # heitin, tytär
    (r"([lnr])\1(aa?|ää?|ee?|[ae][lr]e?|ime|in)",  r"\1t\2"),   # kallas
    ("([aeiouyäöh])d(aa?|ee?|are?|[iu]me|[iu]n)",  r"\1t\2"),   # pidin
    ("(u)(ere?)",                                  r"\1t\2"),   # auer
))

def _consonant_gradation(word, strengthen=False):
    # apply consonant gradation to the word
    # strengthen: False = strong to weak, True = weak to strong

    regexes = _CONS_GRAD_STRENGTHEN if strengthen else _CONS_GRAD_WEAKEN
    for (reFrom, reTo) in regexes:
        if re.search(reFrom, word) is not None:
            return re.sub(reFrom, reTo, word)
    #sys.exit("No rule found: " + word + " " + str(strengthen))
    return word

# -----------------------------------------------------------------------------

# allow both -a and -ä in -A endings (noun, declension)
_BOTH_A_AND_AUML = frozenset((
    ("buffet",     22),
    ("caddie",      3),
    ("caddie",      8),
    ("fondue",     21),
    ("gay",        21),
    ("gray",       21),
    ("jockey",     21),
    ("reggae",     21),
    ("speedway",   21),
    ("spray",      21),
    ("port salut", 22),
    ("menu",       21),
))

# endings for _CASES_LIKE_GEN_SG, without final -A
_GEN_SG_LIKE_ENDINGS = {
    "nom": "t",
    "gen": "n",
    "tra": "ksi",
    "ine": "ss",
    "ela": "st",
    "ade": "ll",
    "abl": "lt",
    "all": "lle",
    "abe": "tt",
}

# vowels in illative singular endings (-hVn) in declension 21 (default is final
# vowel)
_ILL_SG_VOWELS_DECL_21 = {
    "bébé":      ("e",),
    "brasserie": ("e", "i"),
    "brie":      ("i",),
    "coupé":     ("e",),
    "cowboy":    ("i", "y"),
    "fondue":    ("e", "y"),
    "gay":       ("i", "y"),
    "gray":      ("i", "y"),
    "jersey":    ("i", "y"),
    "jockey":    ("i", "y"),
    "menu":      ("u", "y"),
    "moiré":     ("e",),
    "playboy":   ("i", "y"),
    "reggae":    ("e", "i"),
    "rosé":      ("e",),
    "speedway":  ("i", "y"),
    "spray":     ("i", "y"),
}

# vowels in illative singular endings (-hVn) in declension 22 (default is "e")
_ILL_SG_VOWELS_DECL_22 = {
    "bordeaux":     ("o",),
    "know-how":     ("u",),
    "nougat":       ("a",),
    "passepartout": ("u",),
    "port salut":   ("u", "y"),
    "ragoût":       ("u",),
    "show":         ("u",),
    "sioux":        ("u",),
    "tournedos":    ("o",),
}

def _get_a_or_auml(word, decl, case, number):
    # use "a", "ä" or both in -A endings?

    if (word, decl) in _BOTH_A_AND_AUML:
        return ("a", "ä")
    elif word in ("meri", "veri") and case == "par" and number == "sg":
        return ("a",)
    elif re.search(r"^[^aáou]+$", word) is not None:
        return ("ä",)
    else:
        return ("a",)

def _get_results_gen_sg(word, inflected, decl, case):
    # generate results for cases/numbers in _CASES_LIKE_GEN_SG

    infl2 = tuple(i + _GEN_SG_LIKE_ENDINGS[case] for i in inflected)

    if case in ("ine", "ela", "ade", "abl", "abe"):
        aOrAuml = _get_a_or_auml(word, decl, "gen", "sg")
        infl2 = tuple(i + a for i in infl2 for a in aOrAuml)
    yield from infl2

def _get_results_ess_sg(word, inflected, decl):
    # generate results for essive singular

    aOrAuml = _get_a_or_auml(word, decl, "ess", "sg")
    yield from (f"{i}n{a}" for i in inflected for a in aOrAuml)

def _get_results_ill_sg(word, inflected, decl):
    # generate results for illative singular

    # -:n
    if decl <= 16 or 23 <= decl <= 40 or decl in (42, 43, 45, 46) \
    or decl == 49 and not word.endswith("e") or word == "jersey":
        yield from (f"{i}{i[-1]}n" for i in inflected)

    # -hVn
    if 18 <= decl <= 22:
        if decl == 21:
            vowels = _ILL_SG_VOWELS_DECL_21.get(word, word[-1])
        elif decl == 22:
            vowels = _ILL_SG_VOWELS_DECL_22.get(word, "e")
        else:
            vowels = set(i[-1] for i in inflected)
        yield from (f"{i}h{v}n" for i in inflected for v in vowels)

    # -seen
    if decl in (17, 20, 41, 44, 47, 48) or decl == 49 and word.endswith("e"):
        yield from (i + "seen" for i in inflected)

def _get_results_par_sg(word, inflected, decl):
    # generate results for partitive singular

    aOrAuml = _get_a_or_auml(word, decl, "par", "sg")

    # -A
    if decl in (1, 2, 25, 37) and word not in ("liemi", "lumi") \
    or 4 <= decl <= 16 or word in ("jersey", "moni"):
        infl2 = inflected
        if decl == 25:  # toimi
            infl2 = tuple(i + "e" for i in inflected)
        elif decl == 37:  # vasen
            infl2 = tuple(re.sub("n$", "mpa", i) for i in inflected)
        elif word == "moni":
            infl2 = tuple(i + "ta" for i in inflected)
        yield from (i + a for i in infl2 for a in aOrAuml)

    # -tA
    if decl in (3, 15) or decl >= 17:
        infl2 = inflected
        if decl == 25:  # toimi
            infl2 = tuple(re.sub("m$", "n", i) for i in infl2)
        elif decl == 48 or decl == 49 and word.endswith("e"):
            infl2 = tuple(i + "t" for i in infl2)  # hame, askele
        yield from (f"{i}t{a}" for i in infl2 for a in aOrAuml)

def _get_results_gen_pl(word, inflected, decl, consGrad, case):
    # generate results for genitive plural, partitive plural or illative plural

    aOrAuml = _get_a_or_auml(word, decl, case, "pl")

    # -jen/-jA/-ihin (some -ihin forms are output elsewhere)
    if decl in (1, 2, 4, 8, 9, 11, 13, 14) \
    or case == "par" and decl in (5, 6) \
    or case == "ill" and decl == 5:
        infl2 = inflected
        if decl in (5, 6):  # risti, paperi
            infl2 = tuple(i + "e" for i in infl2)
        elif decl == 11:  # omena
            infl2 = tuple(
                re.sub("a$", "o", re.sub("ä$", "ö", i)) for i in infl2
            )
        #
        if case == "gen":
            yield from (i + "jen" for i in infl2)
        elif case == "par":
            yield from (f"{i}j{a}" for i in infl2 for a in aOrAuml)
        else:
            yield from (i + "ihin" for i in infl2)

    # -iden/-itA/-ihin/-isiin (some -ihin forms are output elsewhere)
    if decl in (2, 3, 4, 6, 41, 43, 44, 47, 48) \
    or 11 <= decl <= 22 and not decl == 16 \
    or decl == 49 and word.endswith("e"):
        infl2 = inflected
        if decl == 6:  # paperi
            infl2 = tuple(re.sub("$", "e", i) for i in infl2)
        elif decl == 11:  # omena
            infl2 = tuple(
                re.sub("a$", "o", re.sub("ä$", "ö", i)) for i in infl2
            )
        elif case in ("gen", "par") and consGrad and decl in (4, 14):
            # laatikko, solakka
            infl2 = tuple(_consonant_gradation(i) for i in infl2)
        elif consGrad and decl in (41, 43, 48) \
        and word not in ("häive", "viive"):
            infl2 = tuple(_consonant_gradation(i, True) for i in infl2)
        #
        if case == "gen":
            yield from (i + "iden" for i in infl2)
        elif case == "par":
            yield from (f"{i}it{a}" for i in infl2 for a in aOrAuml)
        else:
            yield from (i + "ihin" for i in infl2)
            # -isiin
            if decl in (15, 17, 20, 41, 43, 44, 47, 48, 49):
                yield from (i + "isiin" for i in infl2)

    # -ien/-iA/-ten/-iin
    if decl in (7, 10, 11, 16, 42, 45, 46) or 23 <= decl <= 40 \
    or decl == 49 and not word.endswith("e") \
    or case == "gen" and decl in (5, 6):
        infl2 = inflected
        if decl == 11:  # omena
            infl2 = tuple(re.sub("[aä]$", "", i) for i in infl2)
        elif decl == 39:  # vastaus
            infl2 = tuple(re.sub("s$", "ks", i) for i in infl2)
        elif consGrad and decl in (32, 49):  # sisar, askel
            infl2 = tuple(_consonant_gradation(i, True) for i in infl2)
        elif decl in (33, 34):  # kytkin, onneton
            if consGrad:
                infl2 = tuple(_consonant_gradation(i, True) for i in infl2)
            infl2 = tuple(re.sub("n$", "m", i) for i in infl2)
        elif decl in (36, 37):  # alin, vasen
            infl2 = tuple(re.sub("n$", "mm", i) for i in infl2)
            infl2 = tuple(_consonant_gradation(i, True) for i in infl2)
        elif decl == 42:  # mies
            infl2 = tuple(re.sub("s$", "h", i) for i in infl2)
        elif decl == 46:  # tuhat
            infl2 = tuple(re.sub("t$", "ns", i) for i in infl2)
        #
        if case == "gen":
            yield from (i + "ien" for i in infl2)
        elif case == "par":
            yield from (f"{i}i{a}" for i in infl2 for a in aOrAuml)
        else:
            yield from (i + "iin" for i in infl2)
        # -ten
        if case == "gen" and word != "uksi" and (
            24 <= decl <= 39 and decl not in (31, 35) or decl in (42, 46, 49)
        ):
            infl2 = inflected
            if decl == 25:  # toimi
                infl2 = tuple(re.sub("m$", "n", i) for i in infl2)
            elif decl in (27, 28):  # käsi, kynsi
                infl2 = tuple(re.sub("s$", "t", i) for i in infl2)
            elif decl in (29, 30):  # lapsi, veitsi
                infl2 = tuple(re.sub("[pt]s$", "s", i) for i in infl2)
            elif decl == 46:  # tuhat
                infl2 = tuple(re.sub("t$", "n", i) for i in infl2)
            yield from (i + "ten" for i in infl2)

# -----------------------------------------------------------------------------

# supported grammatical cases, numbers and combinations of them
CASES = (
    "nom", "gen", "par", "ess", "tra", "ine", "ela", "ill", "ade", "abl",
    "all", "abe", "ins"
)
NUMBERS = ("sg", "pl")
CASES_AND_NUMBERS = (
    ("nom", "sg"),
    ("nom", "pl"),
    ("gen", "sg"),
    ("gen", "pl"),
    ("par", "sg"),
    ("par", "pl"),
    ("ess", "sg"),
    ("tra", "sg"),
    ("ine", "sg"),
    ("ela", "sg"),
    ("ill", "sg"),
    ("ill", "pl"),
    ("ade", "sg"),
    ("abl", "sg"),
    ("all", "sg"),
    ("abe", "sg"),
)

# words with optional consonant gradation in _CASES_LIKE_GEN_SG
_OPTIONAL_CONS_GRAD_GEN_SG = frozenset((
    "bourette",
    "haiku", "huti",
    "koto", "kuti",
    "lento", "leuku", "loota", "lunki",
    "mutu", "myky", "mökä",
    "nahka", "nuti",
    "parka", "peti",
    "raita", "ringette",
    "seljanka", "sinfonietta", "säkä",
    "tuhka", "tutti",
    "uhka",
    "veto", "vihko", "vika", "vinaigrette",
))

def decline_noun_specific(word, decl, consGrad, case, number):
    """Get inflected forms of a Finnish noun.
    word:     a noun in nominative singular (str)
    decl:     Kotus declension (1-49)
    consGrad: does consonant gradation apply in certain cases/numbers? (bool)
    case:     grammatical case (see CASES)
    number:   grammatical number (see NUMBERS)
    generate: inflected forms of word"""

    assert isinstance(word, str)
    assert 1 <= decl <= 49
    assert isinstance(consGrad, bool)
    assert case in CASES
    assert number in NUMBERS
    assert (case, number) in CASES_AND_NUMBERS

    # exit early for nominative singular
    if case == "nom" and number == "sg":
        yield word
        return

    # change ending (without adding case/number endings)
    inflected = [_change_ending(word, decl, case, number)]

    # apply consonant gradation
    if (case, number) in _CASES_LIKE_GEN_SG and (
        consGrad and decl <= 16 and not word == "pop"
        or decl in (27, 28, 31, 40, 45, 46)
    ):
        # strong to weak
        if word == "aika":
            inflected = ["aja"]
        elif word == "poika":
            inflected = ["poja"]
        else:
            inflected = [_consonant_gradation(inflected[0])]
    elif (
        consGrad and decl >= 32 and (
            (
                (case, number) in _CASES_LIKE_GEN_SG
                or case in ("ess", "ill") and number == "sg"
            )
            or case in ("gen", "par", "ill") and number == "pl" and decl == 35
        )
        or decl in (36, 37) and case in ("ess", "ill") and number == "sg"
    ):
        # weak to strong
        inflected = [_consonant_gradation(inflected[0], True)]

    # add variant with/without consonant gradation
    if (case, number) in _CASES_LIKE_GEN_SG \
    and word in _OPTIONAL_CONS_GRAD_GEN_SG:
        inflected.append(word)
    elif word in ("häive", "viive"):
        if case in ("gen", "par", "ill") and number == "pl":
            inflected.append(re.sub("ve$", "pe", word))
        elif not (case == "par" and number == "sg"):
            inflected.append(word + "e")
    elif word == "pop" and (
        case in ("ess", "par", "ill") or case == "gen" and number == "pl"
    ):
        if case in ("gen", "par", "ill") and number == "pl":
            inflected.extend([i + i[-1] for i in inflected])
        else:
            inflected.extend(
                [_consonant_gradation(i, True) for i in inflected]
            )
    elif decl in (4, 14) and case == "ill" and number == "pl":
        # laatikko, solakka
        inflected.extend([_consonant_gradation(i) for i in inflected])
    # add irregular variant
    elif word == "hapan" and (
        (case, number) in _CASES_LIKE_GEN_SG \
        or case in ("ess", "ill") and number == "sg"
    ):
        inflected.extend([re.sub("e$", "a", i) for i in inflected])

    # append apostrophe
    if decl == 22:
        inflected = [i + "'" for i in inflected]

    inflected = tuple(inflected)
    #print(f"{inflected=}, {decl=}, {consGrad=}")

    # append case/number endings and generate words
    if (case, number) in _CASES_LIKE_GEN_SG:
        yield from _get_results_gen_sg(word, inflected, decl, case)
    elif case == "ess" and number == "sg":
        yield from _get_results_ess_sg(word, inflected, decl)
    elif case == "ill" and number == "sg":
        yield from _get_results_ill_sg(word, inflected, decl)
    elif case == "par" and number == "sg":
        yield from _get_results_par_sg(word, inflected, decl)
    elif case in ("gen", "par", "ill") and number == "pl":
        yield from _get_results_gen_pl(word, inflected, decl, consGrad, case)
    else:
        sys.exit("error")

def decline_noun(word, case, number):
    """Get inflected forms of a Finnish noun. Autodetects declension(s) and
    whether consonant gradation applies.
    word:     a noun in nominative singular (str)
    case:     grammatical case (see CASES)
    number:   grammatical number (see NUMBERS)
    generate: inflected forms of word"""

    assert isinstance(word, str)
    assert case in CASES
    assert number in NUMBERS
    assert (case, number) in CASES_AND_NUMBERS

    for decl in get_declensions(word):
        # errors in source data
        if word in ("alpi", "helpi") and decl == 5 \
        or word == "siitake" and decl == 8:
            consGrad = False
        elif word in ("auer", "hynte", "näin", "pue", "ryntys"):
            consGrad = True
        else:
            consGrad = get_consonant_gradation(word, decl)
        yield from set(
            decline_noun_specific(word, decl, consGrad, case, number)
        )

def main():
    if len(sys.argv) == 2:
        word = sys.argv[1]
        allCases = True
    elif len(sys.argv) == 4:
        (word, case, number) = sys.argv[1:]
        if case not in CASES:
            sys.exit("Invalid case.")
        if number not in NUMBERS:
            sys.exit("Invalid number.")
        if (case, number) not in CASES_AND_NUMBERS:
            sys.exit("Unsupported combination of case and number.")
        allCases = False
    else:
        sys.exit(
            "Decline a Finnish noun. Arguments: NOUN [CASE NUMBER]. Cases: "
            + ", ".join(CASES) + ". Numbers: " + ", ".join(NUMBERS) + ". "
            + "If case & number omitted, print all supported combinations."
        )

    for (c, n) in (CASES_AND_NUMBERS if allCases else ((case, number),)):
        declinedNouns = set(decline_noun(word, c, n))
        if not declinedNouns:
            sys.exit("Unrecognized noun.")
        print(c.title() + n.title() + ": " + ", ".join(sorted(declinedNouns)))

if __name__ == "__main__":
    main()
