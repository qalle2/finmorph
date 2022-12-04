"""Decline a Finnish noun."""

import re, sys
from noun_consgrad import get_consonant_gradation
from noundecl import get_declensions

# - C = any consonant, V = any vowel, A = a/ä, O = o/ö, U = u/y
# - declensions (1-49) are from Kotus

# -----------------------------------------------------------------------------

# rules for changing final consonants and vowels
# - format: declension: ((regex_from, regex_to), ...)
# - "$" will be appended to regex_from
# - only the 1st match with regex_from will be applied
# - consonant gradation will be applied afterwards
#
# consonants (keys must be unique for any combination of case/number)
_CONSONANTS_GEN_SG_PAR_SG_GEN_PL = {
    # -n
    10: (("n",   ""),),   # kahdeksan
    32: (("nen", "n"),),  # kymmenen
    38: (("nen", "s"),),  # nainen
}
_CONSONANTS_GEN_SG_PAR_SG = {
    # -s
    40: (("s", "ti"),),  # kalleus
    # -si
    27: (("si", "ti"),),  # käsi
    28: (("si", "ti"),),  # kynsi
}
_CONSONANTS_GEN_SG_GEN_PL = {
    # -n
    34: (("n", "m"),),   # onneton
    35: (("n", "m"),),   # lämmin
    36: (("n", "mm"),),  # sisin
    37: (("n", "mm"),),  # vasen
    # -s
    41: (("s", ""),),  # vieras
    # -t
    43: (("t", ""),),  # ohut
    44: (("t", ""),),  # kevät
    47: (("t", ""),),  # kuollut
}
_CONSONANTS_GEN_SG = (  # also _CASES_LIKE_GEN_SG, EssSg, IllSg
    _CONSONANTS_GEN_SG_PAR_SG_GEN_PL
    | _CONSONANTS_GEN_SG_PAR_SG
    | _CONSONANTS_GEN_SG_GEN_PL
    | {
        # -n
        33: (("n", "m"),),  # kytkin
        # -s
        39: (("s", "ks"),),  # vastaus
        42: (("s", "h"),),   # mies
        45: (("s", "nt"),),  # kahdeksas
        # -si
        31: (("ksi", "hti"),),  # kaksi
        # -t
        46: (("t", "nt"),),  # tuhat
    }
)
_CONSONANTS_PAR_SG = (
    _CONSONANTS_GEN_SG_PAR_SG_GEN_PL
    | _CONSONANTS_GEN_SG_PAR_SG
    | {
        # -mi
        25: (("mi", "ni"),),  # toimi
        # -s
        45: (("s", "t"),),  # kahdeksas
        # -si
        29: (("[kp]si", "si"),),  # lapsi
        30: (("tsi",    "si"),),  # veitsi
        31: (("ksi",    "hi"),),  # kaksi
    }
)
_CONSONANTS_GEN_PL = (  # also PartPl, IllPl
    _CONSONANTS_GEN_SG_PAR_SG_GEN_PL
    | _CONSONANTS_GEN_SG_GEN_PL
    | {
        # -n
        33: (("n", "m"),),  # kytkin
        # -s
        39: (("s", "ks"),),  # vastaus
        40: (("s", "ks"),),  # kalleus
        42: (("s", "h"),),   # mies
        45: (("s", "ns"),),  # kahdeksas
        # -t
        46: (("t", "ns"),),  # tuhat
    }
)
del _CONSONANTS_GEN_SG_PAR_SG_GEN_PL
del _CONSONANTS_GEN_SG_PAR_SG
del _CONSONANTS_GEN_SG_GEN_PL
#
# vowels (keys must be unique for any combination of case/number)
_VOWELS_GEN_SG_PAR_SG = {
    # -C -> -Ci
    5: (("([^aeiouyäö])", r"\1i"),),  # risti, rock
    6: (("([^aeiouyäö])", r"\1i"),),  # paperi, nylon
    # -i -> -e
    7: (("i", "e"),),  # ovi
    # -i -> -A
    16: (("^([^aou]+)i", r"\1ä"), ("i", "a")),  # vanhempi
}
_VOWELS_GEN_SG_GEN_PL = {
    # - -> -A
    34: (("^([^aou]+)", r"\1ä"), ("", "a")),  # onneton
    35: (("^([^aou]+)", r"\1ä"), ("", "a")),  # lämmin
    36: (("^([^aou]+)", r"\1ä"), ("", "a")),  # sisin
    37: (("^([^aou]+)", r"\1ä"), ("", "a")),  # vasen
}
_VOWELS_GEN_SG = (  # also _CASES_LIKE_GEN_SG, EssSg, IllSg
    _VOWELS_GEN_SG_PAR_SG
    | _VOWELS_GEN_SG_GEN_PL
    | {
        # -i -> -e
        23: (("i", "e"),),  # tiili
        24: (("i", "e"),),  # uni
        25: (("i", "e"),),  # toimi
        26: (("i", "e"),),  # pieni
        27: (("i", "e"),),  # käsi
        28: (("i", "e"),),  # kynsi
        29: (("i", "e"),),  # lapsi
        30: (("i", "e"),),  # veitsi
        31: (("i", "e"),),  # kaksi
        40: (("i", "e"),),  # kalleus
        # - -> -e
        32: (("", "e"),),  # sisar
        33: (("", "e"),),  # kytkin
        38: (("", "e"),),  # nainen
        39: (("", "e"),),  # vastaus
        42: (("", "e"),),  # mies
        43: (("", "e"),),  # ohut
        45: (("", "e"),),  # kahdeksas
        46: (("", "e"),),  # tuhat
        49: (("", "e"),),  # askel, askele
        # -V -> -VV
        41: (("([aeiouyäö])", r"\1\1"),),  # vieras
        44: (("ä",            "ää"),),     # kevät
        48: (("([aeiouyäö])", r"\1\1"),),  # hame
        # -U -> -ee
        47: (("[uy]", "ee"),),  # kuollut
    }
)
_VOWELS_PAR_SG_GEN_PL = {
    # -i -> -
    23: (("i", ""),),  # tiili
    24: (("i", ""),),  # uni
    25: (("i", ""),),  # toimi
    26: (("i", ""),),  # pieni
    27: (("i", ""),),  # käsi
    28: (("i", ""),),  # kynsi
    29: (("i", ""),),  # lapsi
    30: (("i", ""),),  # veitsi
    31: (("i", ""),),  # kaksi
    40: (("i", ""),),  # kalleus
}
_VOWELS_PAR_SG = (
    _VOWELS_GEN_SG_PAR_SG
    | _VOWELS_PAR_SG_GEN_PL
)
_VOWELS_GEN_PL_ILL_PL = {
    5: (("i", "e"), ("([^aeiouyäö])", r"\1e")),  # risti, rock
    6: (("i", "e"), ("([^aeiouyäö])", r"\1e")),  # paperi, nylon
    #
    7:  (("i",          ""),),   # ovi
    10: (("[aä]",       ""),),   # koira
    15: (("[aä]",       ""),),   # korkea
    16: (("i",          ""),),   # vanhempi
    17: (("[aeiouyäö]", ""),),   # vapaa
    18: (("[aeiouyäö]", ""),),   # maa
    20: (("[aeiouyäö]", ""),),   # filee
    41: (("aa",         "a"),),  # vieras
    # -A -> -O
    9:  (("a", "o"), ("ä", "ö")),  # kala
    11: (("a", "o"), ("ä", "ö")),  # omena
    12: (("a", "o"), ("ä", "ö")),  # kulkija
    13: (("a", "o"), ("ä", "ö")),  # katiska
    14: (("a", "o"), ("ä", "ö")),  # solakka
    # -ie/-uo/-yö -> -e/-o/-ö
    19: (("ie", "e"), ("uo", "o"), ("yö", "ö")),  # suo
    # -U -> -e
    47: (("[uy]", "e"),),  # kuollut
}
_VOWELS_GEN_PL = (  # also PartPl
    _VOWELS_GEN_SG_GEN_PL
    | _VOWELS_PAR_SG_GEN_PL
    | _VOWELS_GEN_PL_ILL_PL
)
_VOWELS_ILL_PL = (
    _VOWELS_PAR_SG_GEN_PL
    | _VOWELS_GEN_PL_ILL_PL
)
del _VOWELS_GEN_SG_PAR_SG
del _VOWELS_GEN_SG_GEN_PL
del _VOWELS_PAR_SG_GEN_PL
del _VOWELS_GEN_PL_ILL_PL

_TEMP = {  # GenPl, PartPl, IllPl (both consonants and vowels)
    # -V -> -
    5:  (("i",          ""),),  # risti
    6:  (("i",          ""),),  # paperi
    7:  (("i",          ""),),  # ovi
    10: (("[aä]",       ""),),  # koira
    11: (("[aä]",       ""),),  # omena
    15: (("[aä]",       ""),),  # korkea
    16: (("i",          ""),),  # vanhempi
    17: (("[aeiouyäö]", ""),),  # vapaa
    18: (("[aeiouyäö]", ""),),  # maa
    20: (("[aeiouyäö]", ""),),  # filee
    23: (("i",          ""),),  # tiili
    24: (("i",          ""),),  # uni
    25: (("i",          ""),),  # toimi
    26: (("i",          ""),),  # pieni
    27: (("i",          ""),),  # käsi
    28: (("i",          ""),),  # kynsi
    29: (("i",          ""),),  # lapsi
    30: (("i",          ""),),  # veitsi
    31: (("i",          ""),),  # kaksi
    # -A -> -O
    9:  (("a", "o"), ("ä", "ö")),  # kala
    12: (("a", "o"), ("ä", "ö")),  # kulkija
    13: (("a", "o"), ("ä", "ö")),  # katiska
    # -ie/-uo/-yö -> -e/-o/-ö
    19: (("ie", "e"), ("uo", "o"), ("yö", "ö")),  # suo
    # -n
    35: (("n",   "m"),),  # lämmin
    38: (("nen", "s"),),  # nainen
    # -s
    40: (("s", "ks"),),  # kalleus
    41: (("s", ""),),    # vieras
    45: (("s", "ns"),),  # kahdeksas
    # -t
    43: (("t",     ""),),   # ohut
    44: (("t",     ""),),   # kevät
    47: (("[uy]t", "e"),),  # kuollut
}

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
    ("([hl])j(ee?|ime?|in)",                    r"\1k\2"),   # hylje
    ("([aeiouyäöh])(ene?|ime?|in)",             r"\1k\2"),   # säen
    ("([aeiouyäö]|ar)(aa|ee|ii)",               r"\1k\2"),   # ies
    ("(iu)([ae])",                              r"\1k\2"),   # kiuas
    ("(^[^aeiouyäö]?[aeiouyäö]|ai|var)([aei])", r"\1k\2"),   # ruis
    # p
    ("([aeiouyäölm])p(aa?|ää?|ee?|i|ame?|an)",        r"\1pp\2"),  # ape
    ("([aeiouyäö])mm(aa?|ää?|ee?|yy?|ele?|imä?|ye)?", r"\1mp\2"),  # lämmin
    ("([aeiouyäölr])v(aa?|ää?|ee?|[ai][lmn]e?)",      r"\1p\2"),   # taival
    # t
    (r"([aeiouyäölnr])t(([aeiouyäö])\3?)",    r"\1tt\2"),  # altis
    ("([aeiouyäöl])t([aeiouyäö][mnr][aäe]?)", r"\1tt\2"),  # heitin, tytär
    (r"([lnr])\1(aa?|ää?|ee?|[aei][lmnr]e?)", r"\1t\2"),   # kallas
    ("([aeiouyäöh])d(aa?|ee?|[aiu][mnr]e?)",  r"\1t\2"),   # pidin
    ("(u)(ere?)",                             r"\1t\2"),   # auer
))

# -----------------------------------------------------------------------------

def _change_endings(word, regexes):
    # change the final consonant/vowel of a word using a regex
    # regexes: ((regex_from, regex_to), ...)
    # only the first matching regex_from will be applied

    for (reFrom, reTo) in regexes:
        reFrom += "$"
        if re.search(reFrom, word) is not None:
            return re.sub(reFrom, reTo, word)
    return word

def _consonant_gradation(word, strengthen=False):
    # apply consonant gradation to the word
    # strengthen: False = strong to weak, True = weak to strong

    regexes = _CONS_GRAD_STRENGTHEN if strengthen else _CONS_GRAD_WEAKEN
    for (reFrom, reTo) in regexes:
        if re.search(reFrom, word) is not None:
            return re.sub(reFrom, reTo, word)
    #sys.exit("No rule found: " + word + " " + str(strengthen))
    return word

def _decline_gen_sg(word, decl, consGrad):
    # return inflected form for cases/numbers in _CASES_LIKE_GEN_SG;
    # no case/number ending; e.g. "kaksi" -> "kahde"

    origWord = word

    # irregular changes to final consonant and vowel
    word = _change_endings(word, _CONSONANTS_GEN_SG.get(decl, ()))
    word = _change_endings(word, _VOWELS_GEN_SG.get(decl, ()))

    # consonant gradation
    if consGrad and decl >= 32:
        # weak to strong
        word = _consonant_gradation(word, True)
    elif consGrad and decl <= 16 and not origWord == "pop" \
    or decl in (27, 28, 31, 40, 45, 46):
        # strong to weak
        word = _consonant_gradation(word)
        if origWord == "aika":
            word = "aja"
        elif origWord == "poika":
            word = "poja"

    return word

def _decline_ess_sg(word, decl, consGrad):
    # return inflected form for essive singular / illative singular;
    # no case/number ending; e.g. "kaksi" -> "kahte"

    # irregular changes to final consonant and vowel
    word = _change_endings(word, _CONSONANTS_GEN_SG.get(decl, ()))
    word = _change_endings(word, _VOWELS_GEN_SG.get(decl, ()))

    # weak -> strong consonant gradation
    if consGrad and decl >= 32 or decl in (36, 37):
        word = _consonant_gradation(word, True)

    return word

def _decline_par_sg(word, decl, consGrad):
    # return inflected form for partitive singular;
    # no case/number ending; e.g. "kaksi" -> "kaht"

    # irregular changes to final consonant and vowel
    word = _change_endings(word, _CONSONANTS_PAR_SG.get(decl, ()))
    word = _change_endings(word, _VOWELS_PAR_SG.get(decl, ()))

    return word

def _decline_gen_pl(word, decl, consGrad):
    # return inflected form for genitive plural / partitive plural;
    # no case/number ending; e.g. "kaksi" -> "kaks"

    # irregular changes to final consonant and vowel
    word = _change_endings(word, _CONSONANTS_GEN_PL.get(decl, ()))
    word = _change_endings(word, _VOWELS_GEN_PL.get(decl, ()))
    #word = _change_endings(word, _TEMP.get(decl, ()))

    return word

def _decline_ill_pl(word, decl, consGrad):
    # return inflected form for illative plural;
    # no case/number ending; e.g. "kaksi" -> "kaks"

    # irregular changes to final consonant and vowel
    word = _change_endings(word, _CONSONANTS_GEN_PL.get(decl, ()))
    word = _change_endings(word, _VOWELS_ILL_PL.get(decl, ()))
    #word = _change_endings(word, _TEMP.get(decl, ()))

    if consGrad and decl in (32, 33, 34, 35, 41, 43, 48, 49) \
    or decl in (36, 37):
        word = _consonant_gradation(word, True)

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

# endings for cases that behave like genitive singular, without final -A
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

# words with optional consonant gradation in GenSg and similar cases
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

# vowels in illative singular endings (-hVn) in declensions 21/22
_ILL_SG_VOWELS_DECL_21 = {
    # default is final vowel
    "bébé":      "e",
    "brasserie": "ei",
    "brie":      "i",
    "coupé":     "e",
    "cowboy":    "iy",
    "fondue":    "ey",
    "gay":       "iy",
    "gray":      "iy",
    "jersey":    "iy",
    "jockey":    "iy",
    "menu":      "uy",
    "moiré":     "e",
    "playboy":   "iy",
    "reggae":    "ei",
    "rosé":      "e",
    "speedway":  "iy",
    "spray":     "iy",
}
_ILL_SG_VOWELS_DECL_22 = {
    # default is "e"
    "bordeaux":     "o",
    "know-how":     "u",
    "nougat":       "a",
    "passepartout": "u",
    "port salut":   "uy",
    "ragoût":       "u",
    "show":         "u",
    "sioux":        "u",
    "tournedos":    "o",
}

def _decline_noun_specific(word, decl, consGrad, case, number):
    # generate inflected forms of a Finnish noun using specified declension
    # (1-49) and consonant gradation (bool)

    # exit early for nominative singular
    if case == "nom" and number == "sg":
        yield word
        return

    # inflect without adding case/number endings
    if word == "paras" and not (case == "par" and number == "sg"):
        altWord = "parhas"
    elif word == "veli":
        altWord = "velji"
    else:
        altWord = word
    #
    if (case, number) in _CASES_LIKE_GEN_SG:
        inflected = [_decline_gen_sg(altWord, decl, consGrad)]
    elif case in ("ess", "ill") and number == "sg":
        inflected = [_decline_ess_sg(altWord, decl, consGrad)]
    elif case == "par" and number == "sg":
        inflected = [_decline_par_sg(altWord, decl, consGrad)]
    elif case in ("gen", "par") and number == "pl":
        inflected = [_decline_gen_pl(altWord, decl, consGrad)]
    elif case == "ill" and number == "pl":
        inflected = [_decline_ill_pl(altWord, decl, consGrad)]
    else:
        sys.exit("Error: this should never happen.")
    del altWord

    # add variant with/without consonant gradation
    if (case, number) in _CASES_LIKE_GEN_SG \
    and word in _OPTIONAL_CONS_GRAD_GEN_SG:
        inflected.append(word)
    elif word in ("häive", "viive") and not (case == "par" and number == "sg"):
        inflected.append(word + "e")
    elif word == "pop" and (
        case in ("ess", "par", "ill") or case == "gen" and number == "pl"
    ):
        inflected.extend([_consonant_gradation(i, True) for i in inflected])
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

    # use "a", "ä" or both in -A endings?
    if (word, decl) in _BOTH_A_AND_AUML:
        aOrAuml = ("a", "ä")
    elif word in ("meri", "veri") and case == "par" and number == "sg":
        aOrAuml = ("a",)
    elif re.search(r"^[^aáou]+$", word) is not None:
        aOrAuml = ("ä",)
    else:
        aOrAuml = ("a",)

    # append case/number endings and generate words
    if (case, number) in _CASES_LIKE_GEN_SG:
        # many case/number combinations that resemble genitive singular
        if case in ("nom", "gen", "tra", "all"):
            yield from (i + _GEN_SG_LIKE_ENDINGS[case] for i in inflected)
        else:
            yield from (
                i + _GEN_SG_LIKE_ENDINGS[case] + a
                for i in inflected for a in aOrAuml
            )
    elif case == "ess" and number == "sg":
        # essive singular
        yield from (f"{i}n{a}" for i in inflected for a in aOrAuml)
    elif case == "ill" and number == "sg":
        # illative singular
        if decl == 20:
            yield from (f"{i}h{i[-1]}n" for i in inflected)
            yield from (i + "seen" for i in inflected)
        elif decl in (18, 19):
            yield from (f"{i}h{i[-1]}n" for i in inflected)
        elif decl == 21:
            yield from (
                f"{i}h{v}n"
                for i in inflected
                for v in _ILL_SG_VOWELS_DECL_21.get(word, i[-1])
            )
            if word == "jersey":
                yield from (i + "yn" for i in inflected)  # additional
        elif decl == 22:
            for i in inflected:
                yield from (
                    f"{i}h{v}n" for v in _ILL_SG_VOWELS_DECL_22.get(word, "e")
                )
        elif decl in (17, 41, 44, 47, 48) \
        or decl == 49 and word.endswith("e"):
            yield from (i + "seen" for i in inflected)
        else:
            yield from (f"{i}{i[-1]}n" for i in inflected)
    elif case == "par" and number == "sg":
        # partitive singular
        # -A
        if decl in (1, 2) or 4 <= decl <= 16:  # valo, palvelu, ...
            yield from (i + a for i in inflected for a in aOrAuml)
        elif decl == 25 and word not in ("liemi", "lumi"):  # toimi
            yield from (
                f"{i[:-1]}me{a}" for i in inflected for a in aOrAuml
            )
        elif decl == 37:  # vasen
            yield from (
                f"{i[:-1]}mp{2*a}" for i in inflected for a in aOrAuml
            )
        elif word == "moni":
            yield from (f"{i}t{2*a}" for i in inflected for a in aOrAuml)
        # -tA
        if decl == 48 or decl == 49 and word.endswith("e"):  # hame, askel
            yield from (f"{i}tt{a}" for i in inflected for a in aOrAuml)
        elif decl in (3, 15) or decl >= 17:  # valtio, korkea, ...
            yield from (f"{i}t{a}" for i in inflected for a in aOrAuml)
            if word == "jersey":
                yield word + "ä"
    elif case in ("gen", "par", "ill") and number == "pl":
        # genitive plural, partitive plural, illative plural
        # -jen/-jA/-ihin (some -ihin forms are output elsewhere)
        if decl in (1, 2, 4, 8, 9, 11, 13, 14) \
        or case == "par" and decl in (5, 6) \
        or case == "ill" and decl == 5:
            if case == "gen":
                yield from (i + "jen" for i in inflected)
            elif case == "par":
                yield from (f"{i}j{a}" for i in inflected for a in aOrAuml)
            else:
                yield from (i + "ihin" for i in inflected)
        # -iden/-itA/-ihin/-isiin (some -ihin forms are output elsewhere)
        if decl in (2, 3, 4, 6, 41, 43, 44, 47, 48) \
        or 11 <= decl <= 22 and not decl == 16 \
        or decl == 49 and word.endswith("e"):
            infl2 = inflected
            if word == "häive":
                infl2 = ("häipe", "häive")
            elif word == "viive":
                infl2 = ("viipe", "viive")
            elif case in ("gen", "par") and consGrad and decl in (4, 14):
                # laatikko, solakka
                infl2 = tuple(_consonant_gradation(i) for i in infl2)
            elif case in ("gen", "par") and consGrad and decl in (41, 43, 48):
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
            if case == "ill":
                if decl == 11:  # omena
                    infl2 = tuple(re.sub("[oö]$", "", i) for i in infl2)
            else:
                # -ien/-iA
                if consGrad and decl in (32, 33, 34, 49) \
                or decl in (35, 36, 37):
                    # lämmin, sisin, vasen
                    infl2 = tuple(_consonant_gradation(i, True) for i in infl2)
                #
                if word == "veli" or decl in (5, 6):
                    infl2 = tuple(re.sub("e$", "", i) for i in infl2)
                elif decl in (10, 34, 35, 36, 37):
                    # koira, onneton, lämmin, sisin, vasen
                    infl2 = tuple(re.sub("[aä]$", "", i) for i in infl2)
                elif decl == 11:  # omena
                    infl2 = tuple(re.sub("[oö]$", "", i) for i in infl2)
                elif decl == 33:  # kytkin
                    infl2 = tuple(re.sub("n$", "m", i) for i in infl2)
                elif decl == 42:  # mies
                    infl2 = tuple(re.sub("s$", "h", i) for i in infl2)
            if case == "gen":
                yield from (i + "ien" for i in infl2)
            elif case == "par":
                yield from (f"{i}i{a}" for i in infl2 for a in aOrAuml)
            else:
                yield from (i + "iin" for i in infl2)
            # -ten
            if case == "gen" and word != "uksi" \
            and decl not in (5, 6, 7, 10, 11, 16, 23, 31, 35, 40, 45):
                infl2 = inflected
                if decl in (27, 28):  # käsi, kynsi
                    infl2 = tuple(re.sub("s$", "t", i) for i in infl2)
                elif decl in (29, 30):  # lapsi, veitsi
                    infl2 = tuple(re.sub("[pt]s$", "s", i) for i in infl2)
                elif decl == 34:  # onneton
                    infl2 = tuple(re.sub("m[aä]$", "n", i) for i in infl2)
                elif decl in (36, 37):  # sisin, vasen
                    infl2 = tuple(re.sub("mm[aä]$", "n", i) for i in infl2)
                elif decl == 39:  # vastaus
                    infl2 = tuple(re.sub("ks$", "s", i) for i in infl2)
                elif decl == 42:  # mies
                    infl2 = tuple(re.sub("h$", "s", i) for i in infl2)
                elif decl == 46:  # tuhat
                    infl2 = tuple(re.sub("ns$", "n", i) for i in infl2)
                yield from (re.sub("m$", "n", i) + "ten" for i in infl2)
    else:
        sys.exit("Error: this should never happen.")

def decline_noun(word, case, number):
    """Generate inflected forms of a Finnish noun. May contain duplicates."""

    for decl in get_declensions(word):
        # errors in source data
        if word in ("alpi", "helpi") and decl == 5 \
        or word == "siitake" and decl == 8:
            consGrad = False
        elif word in ("auer", "hynte", "näin", "pue", "ryntys"):
            consGrad = True
        else:
            consGrad = get_consonant_gradation(word, decl)
        yield from _decline_noun_specific(word, decl, consGrad, case, number)

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
