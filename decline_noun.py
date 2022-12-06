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

_CHANGES_SINGULAR_COMMON = {  # a temporary dict
    5:  (("([^aeiouyäö])", r"\1i"),),   # risti, rock
    6:  (("([^aeiouyäö])", r"\1i"),),   # paperi, nylon
    7:  (("i",             "e"),),      # ovi
    10: (("n",             ""),),       # koira, kahdeksan
    16: (("^([^aou]+)i", r"\1ä"), ("i", "a")),  # vanhempi
}
_CHANGES_GEN_SG = _CHANGES_SINGULAR_COMMON | {
    # also _CASES_LIKE_GEN_SG, EssSg, IllSg
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
_CHANGES_PAR_SG = _CHANGES_SINGULAR_COMMON | {
    23: (("i",      ""),),   # tiili
    24: (("i",      ""),),   # uni
    25: (("i",      ""),),   # toimi
    26: (("i",      ""),),   # pieni
    27: (("si",     "t"),),  # käsi
    28: (("si",     "t"),),  # kynsi
    29: (("[kp]si", "s"),),  # lapsi
    30: (("tsi",    "s"),),  # veitsi
    31: (("ksi",    "h"),),  # kaksi
    32: (("nen",    "n"),),  # sisar, kymmenen
    38: (("nen",    "s"),),  # nainen
    40: (("s",      "t"),),  # kalleus
    45: (("s",      "t"),),  # kahdeksas
}
del _CHANGES_SINGULAR_COMMON

_CHANGES_PLURAL_COMMON = {  # a temporary dict
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
_CHANGES_GEN_PL = _CHANGES_PLURAL_COMMON | {
    5:  (("i", ""),),  # risti, rock
    6:  (("i", ""),),  # paperi, nylon
}
_CHANGES_PAR_PL = _CHANGES_PLURAL_COMMON | {  # also IllPl, EssPl
    5:  (("i", "e"), ("([^aeiouyäö])", r"\1e")),  # risti, rock
    6:  (("i", "e"), ("([^aeiouyäö])", r"\1e")),  # paperi, nylon
    33: (("n", "m"),),   # kytkin
    34: (("n", "m"),),   # onneton
    36: (("n", "mm"),),  # sisin
    37: (("n", "mm"),),  # vasen
    39: (("s", "ks"),),  # vastaus
    42: (("s", "h"),),   # mies
    46: (("t", "ns"),),  # tuhat
}
del _CHANGES_PLURAL_COMMON

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
    elif case == "gen" and number == "pl":
        changes = _CHANGES_GEN_PL.get(decl, ())
    elif case in ("par", "ill", "ess") and number == "pl":
        changes = _CHANGES_PAR_PL.get(decl, ())
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
    ("([hl])j(ee?|ime?)",                       r"\1k\2"),   # hylje
    ("([aeiouyäöh])(ene?|ime?)",                r"\1k\2"),   # säen
    ("([aeiouyäö]|ar)(aa|ee|ii)",               r"\1k\2"),   # ies
    ("(iu)([ae])",                              r"\1k\2"),   # kiuas
    ("(^[^aeiouyäö]?[aeiouyäö]|ai|var)([aei])", r"\1k\2"),   # ruis
    # p
    ("([aeiouyäölm])p(aa?|ää?|ee?|i|ame?)",           r"\1pp\2"),  # ape
    ("([aeiouyäö])mm(aa?|ää?|ee?|yy?|ye|ele?|imä?)?", r"\1mp\2"),  # lämmin
    ("([aeiouyäölr])v(aa?|ää?|ee?|ale?|ime?)",        r"\1p\2"),   # taival
    # t
    (r"([aeiouyäölnr])t(([aeiouyäö])\3?)",      r"\1tt\2"),  # altis
    ("([aeiouyäöl])t(ime?|oma?|ömä?|[aä]re?)",  r"\1tt\2"),  # heitin
    (r"([lnr])\1(aa?|ää?|ee?|[ae][lr]e?|ime?)", r"\1t\2"),   # kallas
    ("([aeiouyäöh])d(aa?|ee?|are?|[iu]me?)",    r"\1t\2"),   # pidin
    ("(u)(ere?)",                               r"\1t\2"),   # auer
))

def _consonant_gradation(word, strengthen=False):
    # apply consonant gradation to the word
    # strengthen: False = strong to weak, True = weak to strong

    if word == "ylkä" and not strengthen:
        return "yljä"

    regexes = _CONS_GRAD_STRENGTHEN if strengthen else _CONS_GRAD_WEAKEN
    for (reFrom, reTo) in regexes:
        if re.search(reFrom, word) is not None:
            return re.sub(reFrom, reTo, word)
    return word

# apply consonant gradation whenever possible in these cases/numbers, ignoring
# source data
_DECL_GEN_SG_ALWAYS_WEAKEN = frozenset((
    27, 28, 31, 40, 45, 46  # käsi, kynsi, kaksi, kalleus, kahdeksas, tuhat
))
_DECL_ESS_SG_ALWAYS_STRENGTHEN = frozenset((36, 37))  # sisin, vasen

def _consonant_gradation_main(word, inflected, decl, consGrad, case, number):
    # apply consonant gradation to the word (before appending case/number
    # endings)

    if (case, number) in _CASES_LIKE_GEN_SG:
        if consGrad and decl <= 16 or decl in _DECL_GEN_SG_ALWAYS_WEAKEN:
            if decl == 5 and word == "pop":
                return inflected
            elif decl == 9 and word == "aika":
                return "aja"
            elif decl == 10 and word == "poika":
                return "poja"
            return _consonant_gradation(inflected)
        elif consGrad and decl >= 32:
            return _consonant_gradation(inflected, True)
    elif case == "ess" or case == "ill" and number == "sg":
        if consGrad and decl >= 32 \
        or decl in _DECL_ESS_SG_ALWAYS_STRENGTHEN:
            return _consonant_gradation(inflected, True)
    elif case == "gen" and number == "pl":
        if consGrad and decl == 35:  # lämmin
            return _consonant_gradation(inflected, True)
    elif case in ("par", "ill") and number == "pl":
        if consGrad and decl >= 32 and word not in ("häive", "viive") \
        or decl in _DECL_ESS_SG_ALWAYS_STRENGTHEN:
            return _consonant_gradation(inflected, True)

    return inflected  # no consonant gradation

# -----------------------------------------------------------------------------

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

def _get_word_variant(word, inflected, decl, case, number):
    # return a variant of inflected word or None

    # a variant with/without consonant gradation
    if (case, number) in _CASES_LIKE_GEN_SG \
    and word in _OPTIONAL_CONS_GRAD_GEN_SG:
        return word
    elif word in ("häive", "viive"):
        if not (case == "par" and number == "sg"):
            return _consonant_gradation(inflected, True)
    elif word == "pop":
        if case in ("ess", "par", "ill"):
            return "poppi" if number == "sg" else "poppe"
        elif case == "gen" and number == "pl":
            return "popp"
    elif decl in (4, 14):  # laatikko, solakka
        if case in ("ill", "ess") and number == "pl":
            return _consonant_gradation(inflected)
    # an irregular variant
    elif word == "hapan":
        if (case, number) in _CASES_LIKE_GEN_SG \
        or case in ("ess", "ill") and number == "sg":
            return "happama"

    return None  # no variant

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
    elif re.search(r"^[^aáou]+$", word) is None \
    or word in ("meri", "veri") and case == "par" and number == "sg":
        return ("a",)
    return ("ä",)

def _get_results_gen_sg(word, infl, decl, case):
    # generate results for cases/numbers in _CASES_LIKE_GEN_SG
    # (word = original word, infl = inflected forms with consonant gradation)

    if case in ("nom", "gen", "tra", "all"):
        yield from (i + _GEN_SG_LIKE_ENDINGS[case] for i in infl)
    else:
        aOrAuml = _get_a_or_auml(word, decl, "gen", "sg")
        yield from (
            i + _GEN_SG_LIKE_ENDINGS[case] + a for i in infl for a in aOrAuml
        )

def _get_results_ess_sg(word, infl, decl):
    # generate results for essive singular
    # (word = original word, infl = inflected forms with consonant gradation)

    aOrAuml = _get_a_or_auml(word, decl, "ess", "sg")
    yield from (i + "n" + a for i in infl for a in aOrAuml)

_DECL_ILL_SG_VN = frozenset((
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27,
    28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 42, 43, 45, 46
))
_DECL_ILL_SG_HVN = frozenset((18, 19, 20, 21, 22))
_DECL_ILL_SG_SEEN = frozenset((17, 20, 41, 44, 47, 48))

def _get_results_ill_sg(word, infl, decl):
    # generate results for illative singular
    # (word = original word, infl = inflected forms with consonant gradation)

    isDecl49a = (decl == 49 and not word.endswith("e"))
    isDecl49b = (decl == 49 and word.endswith("e"))

    # -:n
    if decl in _DECL_ILL_SG_VN or isDecl49a or word == "jersey":
        yield from (i + i[-1] + "n" for i in infl)

    # -hVn
    if decl in _DECL_ILL_SG_HVN:
        if decl == 21:
            vowels = _ILL_SG_VOWELS_DECL_21.get(word, word[-1])
        elif decl == 22:
            vowels = _ILL_SG_VOWELS_DECL_22.get(word, "e")
        else:
            vowels = set(i[-1] for i in infl)
        yield from (i + "h" + v + "n" for i in infl for v in vowels)

    # -seen
    if decl in _DECL_ILL_SG_SEEN or isDecl49b:
        yield from (i + "seen" for i in infl)

_DECL_PAR_SG_A = frozenset((
    1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 25, 37
))
_EXCEPTIONS_PAR_SG_A = frozenset(("jersey", "liemi", "lumi", "moni"))
_DECL_PAR_SG_TA = frozenset((
    3, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33,
    34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49
))

def _get_results_par_sg(word, infl, decl):
    # generate results for partitive singular
    # (word = original word, infl = inflected forms with consonant gradation)

    isDecl49b = (decl == 49 and word.endswith("e"))
    aOrAuml = _get_a_or_auml(word, decl, "par", "sg")

    # -A
    if (decl in _DECL_PAR_SG_A) ^ (word in _EXCEPTIONS_PAR_SG_A):
        if decl == 25:  # toimi
            yield from (i + "e" + a for i in infl for a in aOrAuml)
        elif decl == 37:  # vasen
            yield "vasempaa"
        elif word == "moni":
            yield "montaa"
        else:
            yield from (i + a for i in infl for a in aOrAuml)

    # -tA
    if decl in _DECL_PAR_SG_TA:
        if decl == 25:  # toimi
            yield from (
                re.sub("m$", "n", i) + "t" + a for i in infl for a in aOrAuml
            )
        elif decl == 48 or isDecl49b:  # hame, askele
            yield from (i + "tt" + a for i in infl for a in aOrAuml)
        else:
            yield from (i + "t" + a for i in infl for a in aOrAuml)

# declensions by which endings they allow in genitive plural
_DECL_GEN_PL_JEN = frozenset((1, 2, 4, 8, 9, 11, 13, 14))
_DECL_GEN_PL_IDEN = frozenset((
    2, 3, 4, 6, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 41, 43, 44, 47, 48
))
_DECL_GEN_PL_IEN = frozenset((
    5, 6, 7, 10, 11, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
    36, 37, 38, 39, 40, 42, 45, 46
))
_DECL_GEN_PL_TEN = frozenset((
    24, 25, 26, 27, 28, 29, 30, 32, 33, 34, 36, 37, 38, 39, 42, 46
))

def _get_results_gen_pl(word, infl, decl, consGrad):
    # generate results for genitive plural
    # (word = original word, infl = inflected forms with consonant gradation)

    isDecl49a = (decl == 49 and not word.endswith("e"))
    isDecl49b = (decl == 49 and word.endswith("e"))

    # -jen
    if decl in _DECL_GEN_PL_JEN:
        if decl == 11:  # omena
            yield from (
                re.sub("a$", "o", re.sub("ä$", "ö", i)) + "jen" for i in infl
            )
        else:
            yield from (i + "jen" for i in infl)

    # -iden
    if decl in _DECL_GEN_PL_IDEN or isDecl49b:
        if decl == 6:  # paperi
            yield from (re.sub("$", "e", i) + "iden" for i in infl)
        elif decl == 11:  # omena
            yield from (
                re.sub("a$", "o", re.sub("ä$", "ö", i)) + "iden" for i in infl
            )
        elif consGrad and decl in (4, 14):  # laatikko, solakka
            yield from (_consonant_gradation(i) + "iden" for i in infl)
        elif consGrad and decl in (41, 43, 48) \
        and word not in ("häive", "viive"):  # vieras, ohut, hame
            yield from (_consonant_gradation(i, True) + "iden" for i in infl)
        else:
            yield from (i + "iden" for i in infl)

    # -ien
    if decl in _DECL_GEN_PL_IEN or isDecl49a:
        if decl == 11:  # omena
            yield from (re.sub("[aä]$", "", i) + "ien" for i in infl)
        elif decl == 39:  # vastaus
            yield from (re.sub("s$", "ks", i) + "ien" for i in infl)
        elif consGrad and decl in (32, 49):  # sisar, askel
            yield from (_consonant_gradation(i, True) + "ien" for i in infl)
        elif consGrad and decl in (33, 34):  # kytkin, onneton
            yield from (
                _consonant_gradation(re.sub("n$", "m", i), True) + "ien"
                for i in infl
            )
        elif decl in (33, 34):  # kytkin, onneton
            yield from (re.sub("n$", "m", i) + "ien" for i in infl)
        elif decl in (36, 37):  # alin, vasen
            yield from (
                _consonant_gradation(re.sub("n$", "mm", i), True) + "ien"
                for i in infl
            )
        elif decl == 42:  # mies
            yield from (re.sub("s$", "h", i) + "ien" for i in infl)
        elif decl == 46:  # tuhat
            yield from (re.sub("t$", "ns", i) + "ien" for i in infl)
        else:
            yield from (i + "ien" for i in infl)

    # -ten
    if decl in _DECL_GEN_PL_TEN and word != "uksi" or isDecl49a:
        if decl == 25:  # toimi
            yield from (re.sub("m$", "n", i) + "ten" for i in infl)
        elif decl in (27, 28):  # käsi, kynsi
            yield from (re.sub("s$", "t", i) + "ten" for i in infl)
        elif decl in (29, 30):  # lapsi, veitsi
            yield from (re.sub("[pt]s$", "s", i) + "ten" for i in infl)
        elif decl == 46:  # tuhat
            yield from (re.sub("t$", "n", i) + "ten" for i in infl)
        else:
            yield from (i + "ten" for i in infl)

def _get_results_par_pl(word, infl, decl, consGrad):
    # generate results for partitive plural
    # (word = original word, infl = inflected forms with consonant gradation)

    isDecl49a = (decl == 49 and not word.endswith("e"))
    isDecl49b = (decl == 49 and word.endswith("e"))
    aOrAuml = _get_a_or_auml(word, decl, "par", "pl")

    # -jA
    if decl in _DECL_GEN_PL_JEN or decl in (5, 6):
        if decl == 11:  # omena
            yield from (
                re.sub("a$", "o", re.sub("ä$", "ö", i)) + "j" + a
                for i in infl for a in aOrAuml
            )
        else:
            yield from (i + "j" + a for i in infl for a in aOrAuml)

    # -itA
    if decl in _DECL_GEN_PL_IDEN or isDecl49b:
        if decl == 11:  # omena
            yield from (
                re.sub("a$", "o", re.sub("ä$", "ö", i)) + "it" + a
                for i in infl for a in aOrAuml
            )
        elif consGrad and decl in (4, 14):  # laatikko, solakka
            yield from (
                _consonant_gradation(i) + "it" + a
                for i in infl for a in aOrAuml
            )
        else:
            yield from (i + "it" + a for i in infl for a in aOrAuml)

    # -iA
    if decl in _DECL_GEN_PL_IEN and decl not in (5, 6) or isDecl49a:
        if decl == 11:  # omena
            yield from (
                re.sub("[aä]$", "", i) + "i" + a for i in infl for a in aOrAuml
            )
        else:
            yield from (i + "i" + a for i in infl for a in aOrAuml)

# declensions by which endings they allow in illative plural
_DECL_ILL_PL_IHIN = frozenset((
    1, 2, 3, 4, 5, 6, 8, 9, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22,
    41, 43, 44, 47, 48
))
_DECL_ILL_PL_ISIIN = frozenset((15, 17, 20, 41, 43, 44, 47, 48))
_DECL_ILL_PL_IIN = frozenset((
    7, 10, 11, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37,
    38, 39, 40, 42, 45, 46
))

def _get_results_ill_pl(word, infl, decl):
    # generate results for illative plural
    # (word = original word, infl = inflected forms with consonant gradation)

    isDecl49a = (decl == 49 and not word.endswith("e"))
    isDecl49b = (decl == 49 and word.endswith("e"))

    # -ihin
    if decl in _DECL_ILL_PL_IHIN or isDecl49b:
        if decl == 11:  # omena
            yield from (
                re.sub("a$", "o", re.sub("ä$", "ö", i)) + "ihin" for i in infl
            )
        else:
            yield from (i + "ihin" for i in infl)

    # -isiin
    if decl in _DECL_ILL_PL_ISIIN or isDecl49b:
        yield from (i + "isiin" for i in infl)

    # -iin
    if decl in _DECL_ILL_PL_IIN or isDecl49a:
        if decl == 11:  # omena
            yield from (re.sub("[aä]$", "", i) + "iin" for i in infl)
        else:
            yield from (i + "iin" for i in infl)

def _get_results_ess_pl(word, infl, decl):
    # generate results for essive plural
    # (word = original word, infl = inflected forms with consonant gradation)

    aOrAuml = _get_a_or_auml(word, decl, "ess", "pl")

    if decl == 11:  # omena
        yield from (
            re.sub("a$", "o", re.sub("ä$", "ö", i)) + "in" + a
            for i in infl for a in aOrAuml
        )
        yield from (
            re.sub("[aä]$", "", i) + "in" + a for i in infl for a in aOrAuml
        )
    else:
        yield from (i + "in" + a for i in infl for a in aOrAuml)

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
    ("ess", "pl"),
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
    inflected = _change_ending(word, decl, case, number)

    # apply consonant gradation
    inflected = _consonant_gradation_main(
        word, inflected, decl, consGrad, case, number
    )

    # add variant if there's one
    variant = _get_word_variant(word, inflected, decl, case, number)
    inflected = [inflected]
    if variant is not None:
        inflected.append(variant)
    del variant

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
    elif case == "gen" and number == "pl":
        yield from _get_results_gen_pl(word, inflected, decl, consGrad)
    elif case == "par" and number == "pl":
        yield from _get_results_par_pl(word, inflected, decl, consGrad)
    elif case == "ill" and number == "pl":
        yield from _get_results_ill_pl(word, inflected, decl)
    elif case == "ess" and number == "pl":
        yield from _get_results_ess_pl(word, inflected, decl)
    else:
        sys.exit("error")

def decline_noun(word, case, number):
    """Get inflected forms of a Finnish noun. Autodetects declension(s) and
    whether consonant gradation applies.
    word:   a noun in nominative singular (str)
    case:   grammatical case (see CASES)
    number: grammatical number (see NUMBERS)
    return: set of inflected forms (may be empty if the noun was not
            recognized)"""

    assert isinstance(word, str)
    assert case in CASES
    assert number in NUMBERS
    assert (case, number) in CASES_AND_NUMBERS

    results = set()

    for decl in get_declensions(word):
        # errors in source data, or optional consonant gradation
        if word in ("häive", "viive") \
        or word in ("alpi", "helpi") and decl == 5 \
        or word == "siitake" and decl == 8:
            consGrad = False
        elif word in ("auer", "hynte", "näin", "pue", "ryntys"):
            consGrad = True
        else:
            consGrad = get_consonant_gradation(word, decl)
        results.update(
            decline_noun_specific(word, decl, consGrad, case, number)
        )

    return results

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
