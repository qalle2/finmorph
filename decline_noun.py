"""Decline a Finnish noun."""

import re, sys
from noun_consgrad import get_consonant_gradation
from noundecl import get_declensions

# C = any consonant, V = any vowel, A = a/ä, O = o/ö, U = u/y

# Kotus declensions:
# 1=valo, 2=palvelu, 3=valtio, 4=laatikko, 5=risti, 6=paperi, 7=ovi, 8=nalle,
# 9=kala, 10=koira/kahdeksan, 11=omena, 12=kulkija, 13=katiska, 14=solakka,
# 15=korkea, 16=vanhempi, 17=vapaa, 18=maa, 19=suo, 20=filee, 21=rosé,
# 22=parfait, 23=tiili, 24=uni, 25=toimi, 26=pieni, 27=käsi, 28=kynsi,
# 29=lapsi, 30=veitsi, 31=kaksi, 32=sisar/kymmenen, 33=kytkin, 34=onneton,
# 35=lämmin, 36=sisin, 37=vasen, 38=nainen, 39=vastaus, 40=kalleus, 41=vieras,
# 42=mies, 43=ohut, 44=kevät, 45=kahdeksas, 46=tuhat, 47=kuollut, 48=hame,
# 49=askel/askele

# -----------------------------------------------------------------------------

# rules for changing final consonants and vowels
# - format: declension: ((regex_from, regex_to), ...)
# - "$" will be appended to regex_from
# - only the 1st match with regex_from will be applied
# - consonant gradation will be applied afterwards
#
# consonants (for any combination of case/number, keys must be unique)
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
# vowels (for any combination of case/number, keys must be unique)
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
    ("([aeiouyäölm])p(aa?|ää?|ee?|ame?|an)",          r"\1pp\2"),  # ape
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

    return word

def _decline_ill_pl(word, decl, consGrad):
    # return inflected form for illative plural;
    # no case/number ending; e.g. "kaksi" -> "kaks"

    # irregular changes to final consonant and vowel
    word = _change_endings(word, _CONSONANTS_GEN_PL.get(decl, ()))
    word = _change_endings(word, _VOWELS_ILL_PL.get(decl, ()))

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

    # use "a", "ä" or both in -A endings?
    if (word, decl) in _BOTH_A_AND_AUML:
        endingVowels = "aä"
    elif word in ("meri", "veri") and case == "par" and number == "sg":
        endingVowels = "a"
    elif re.search(r"^[^aáou]+$", word) is not None:
        endingVowels = "ä"
    else:
        endingVowels = "a"

    # make changes before appending case/number ending
    if case == "nom" and number == "sg":
        inflected = word
    elif (case, number) in _CASES_LIKE_GEN_SG:
        inflected = _decline_gen_sg(word, decl, consGrad)
    elif case in ("ess", "ill") and number == "sg":
        inflected = _decline_ess_sg(word, decl, consGrad)
    elif case == "par" and number == "sg":
        inflected = _decline_par_sg(word, decl, consGrad)
    elif case in ("gen", "par") and number == "pl":
        inflected = _decline_gen_pl(word, decl, consGrad)
    elif case == "ill" and number == "pl":
        inflected = _decline_ill_pl(word, decl, consGrad)
    else:
        sys.exit("Error: this should never happen.")

    # add variants of inflected form
    words = [inflected]
    if (case, number) in _CASES_LIKE_GEN_SG \
    and word in _OPTIONAL_CONS_GRAD_GEN_SG:
        words.append(word)
    elif word == "hapan":
        if (case, number) in _CASES_LIKE_GEN_SG \
        or case in ("ess", "ill") and number == "sg":
            words.append("happama")
    elif word in ("häive", "viive"):
        if not (case in ("nom", "par") and number == "sg"):
            words.append(word + "e")
    elif word == "paras":
        if case in ("gen", "par", "ill") and number == "pl":
            words = ["parha"]
        elif not (case in ("nom", "par") and number == "sg"):
            words = ["parhaa"]
    elif word == "pop":
        if case in ("ess", "ill", "par") and number == "sg":
            words.append("poppi")
        elif case in ("gen", "ill", "par") and number == "pl":
            words.append("poppe")
    elif word == "ryntys":
        if case in ("ess", "ill") and number == "sg":
            words = ["rynttyy"]
    elif word in ("tau", "tiu"):
        if case == "ill" and number == "pl":
            words = [word]  # restore
    elif word == "veli":
        if case == "ill" and number == "pl":
            words = ["velj"]
        elif not (case == "nom" and number == "sg"):
            words = ["velje"]
    elif decl in (4, 14):
        if case == "ill" and number == "pl":
            words.append(_consonant_gradation(inflected))
    del inflected

    # append apostrophe
    if decl == 22 and not (case == "nom" and number == "sg"):
        words = [w + "'" for w in words]

    words = tuple(words)

    #print(words, decl, consGrad)

    # append case/number endings and generate words
    if case == "nom" and number == "sg":
        yield from words
    elif (case, number) in _CASES_LIKE_GEN_SG:
        # many case/number combinations that resemble genitive singular
        if case in ("nom", "gen", "tra", "all"):
            yield from (w + _GEN_SG_LIKE_ENDINGS[case] for w in words)
        else:
            yield from (
                w + _GEN_SG_LIKE_ENDINGS[case] + v
                for w in words for v in endingVowels
            )
    elif case == "ess" and number == "sg":
        # essive singular
        yield from (f"{w}n{v}" for w in words for v in endingVowels)
    elif case == "ill" and number == "sg":
        # illative singular
        if decl == 20:
            yield from (f"{w}h{w[-1]}n" for w in words)
            yield from (w + "seen" for w in words)
        elif decl in (18, 19):
            yield from (f"{w}h{w[-1]}n" for w in words)
        elif decl == 21:
            yield from (
                f"{w}h{v}n"
                for w in words for v in _ILL_SG_VOWELS_DECL_21.get(word, w[-1])
            )
            if word == "jersey":
                yield from (w + "yn" for w in words)  # additional
        elif decl == 22:
            for w in words:
                yield from (
                    f"{w}h{v}n" for v in _ILL_SG_VOWELS_DECL_22.get(word, "e")
                )
        elif decl in (17, 41, 44, 47, 48) \
        or decl == 49 and word.endswith("e"):
            yield from (w + "seen" for w in words)
        else:
            yield from (f"{w}{w[-1]}n" for w in words)
    elif case == "par" and number == "sg":
        # partitive singular
        # -A
        if decl in (1, 2) or 4 <= decl <= 16:
            yield from (w + v for w in words for v in endingVowels)
        elif decl == 25 and word not in ("liemi", "lumi"):  # toimi
            yield from (f"{w[:-1]}me{v}" for w in words for v in endingVowels)
        elif decl == 37:  # vasen
            yield from (
                f"{w[:-1]}mp{2*v}" for w in words for v in endingVowels
            )
        elif word == "moni":
            yield from (f"{w}t{2*v}" for w in words for v in endingVowels)
        # -tA
        if decl == 48 or decl == 49 and word.endswith("e"):  # hame, askel
            yield from (f"{w}tt{v}" for w in words for v in endingVowels)
        elif decl in (3, 15) or decl >= 17:
            yield from (f"{w}t{v}" for w in words for v in endingVowels)
            if word == "jersey":
                yield word + "ä"
    elif case in ("gen", "par", "ill") and number == "pl":
        # genitive plural, partitive plural, illative plural
        # -jen / -jA / part of -ihin
        if decl in (1, 2, 4, 8, 9, 11, 13, 14) \
        or case == "par" and decl in (5, 6) \
        or case == "ill" and decl == 5 \
        or word in ("tau", "tiu"):
            words2 = words
            if case in ("gen", "par") and word in ("tau", "tiu"):
                words2 = (word,)  # restore original
            #
            if case == "gen":
                yield from (w + "jen" for w in words2)
            elif case == "par":
                yield from (f"{w}j{v}" for w in words2 for v in endingVowels)
            else:
                yield from (w + "ihin" for w in words2)
        # -iden, -itA, -isiin, part of -ihin
        if decl in (2, 3, 4, 6, 41, 43, 44, 47, 48) \
        or 11 <= decl <= 22 and not decl == 16 and word not in ("tau", "tiu") \
        or decl == 49 and word.endswith("e"):
            words2 = words
            if word == "häive":
                words2 = ("häipe", "häive")
            elif word == "viive":
                words2 = ("viipe", "viive")
            elif case in ("gen", "par") and consGrad and decl in (4, 14):
                words2 = tuple(_consonant_gradation(w) for w in words2)
            elif case in ("gen", "par") and consGrad and decl in (41, 43, 48):
                words2 = tuple(_consonant_gradation(w, True) for w in words2)
            #
            if case == "gen":
                yield from (w + "iden" for w in words2)
            elif case == "par":
                yield from (f"{w}it{v}" for w in words2 for v in endingVowels)
            else:
                yield from (w + "ihin" for w in words2)
                # -isiin
                if decl in (15, 17, 20, 41, 43, 44, 47, 48, 49):
                    yield from (w + "isiin" for w in words2)
        # -ien/-iA/-ten/-iin
        if decl in (7, 10, 11, 16, 42, 45, 46) or 23 <= decl <= 40 \
        or decl == 49 and not word.endswith("e") \
        or case == "gen" and decl in (5, 6):
            words2 = words
            if case == "ill":
                if decl == 11:  # omena
                    words2 = tuple(re.sub("[oö]$", "", w) for w in words2)
            else:
                # -ien/-iA
                if consGrad and decl in (32, 33, 34, 49) \
                or decl in (35, 36, 37):
                    # lämmin, sisin, vasen
                    words2 = tuple(
                        _consonant_gradation(w, True) for w in words2
                    )
                #
                if word == "veli" or decl in (5, 6):
                    words2 = tuple(re.sub("e$", "", w) for w in words2)
                elif decl in (10, 34, 35, 36, 37):
                    # koira, onneton, lämmin, sisin, vasen
                    words2 = tuple(re.sub("[aä]$", "", w) for w in words2)
                elif decl == 11:  # omena
                    words2 = tuple(re.sub("[oö]$", "", w) for w in words2)
                elif decl == 33:  # kytkin
                    words2 = tuple(re.sub("n$", "m", w) for w in words2)
                elif decl == 42:  # mies
                    words2 = tuple(re.sub("s$", "h", w) for w in words2)
            if case == "gen":
                yield from (w + "ien" for w in words2)
            elif case == "par":
                yield from (f"{w}i{v}" for w in words2 for v in endingVowels)
            else:
                yield from (w + "iin" for w in words2)
            # -ten
            if case == "gen" and word != "uksi" \
            and decl not in (5, 6, 7, 10, 11, 16, 23, 31, 35, 40, 45):
                words2 = words
                if decl in (27, 28):  # käsi, kynsi
                    words2 = tuple(re.sub("s$", "t", w) for w in words2)
                elif decl in (29, 30):  # lapsi, veitsi
                    words2 = tuple(re.sub("[pt]s$", "s", w) for w in words2)
                elif decl == 34:  # onneton
                    words2 = tuple(re.sub("m[aä]$", "n", w) for w in words2)
                elif decl in (36, 37):  # sisin, vasen
                    words2 = tuple(re.sub("mm[aä]$", "n", w) for w in words2)
                elif decl == 39:  # vastaus
                    words2 = tuple(re.sub("ks$", "s", w) for w in words2)
                elif decl == 42:  # mies
                    words2 = tuple(re.sub("h$", "s", w) for w in words2)
                elif decl == 46:  # tuhat
                    words2 = tuple(re.sub("ns$", "n", w) for w in words2)
                yield from (re.sub("m$", "n", w) + "ten" for w in words2)
    else:
        sys.exit("Error: this should never happen.")

def decline_noun(word, case, number):
    """Generate inflected forms of a Finnish noun. May contain duplicates."""

    for decl in get_declensions(word):
        # errors in source data
        if word == "siitake" and decl == 8 \
        or word in ("alpi", "helpi") and decl == 5:
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

    if allCases:
        for (case, number) in CASES_AND_NUMBERS:
            declinedNouns = set(decline_noun(word, case, number))
            if not declinedNouns:
                sys.exit("Unrecognized noun.")
            print(
                case.title() + number.title() + ": "
                + ", ".join(sorted(declinedNouns))
            )
    else:
        declinedNouns = set(decline_noun(word, case, number))
        if not declinedNouns:
            sys.exit("Unrecognized noun.")
        for noun in sorted(declinedNouns):
            print(noun)

if __name__ == "__main__":
    main()
