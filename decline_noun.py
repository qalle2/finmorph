"""Decline a Finnish noun."""

import re, sys
import noun_consgrad
import noundecl

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

# regular expressions for consonant gradation;
# (regex_from, regex_to);
# notes:
# - only the first match will be applied
# - the final consonants and vowels of words have already been changed
#
# strong to weak
_CONS_GRAD_WEAKEN = (
    # k
    ("kk([aeiouyäö])$",               r"k\1"),    # -kkV
    ("nk([aeiouyäö])$",               r"ng\1"),   # -nkV
    ("ylkä$",                         r"yljä"),   # -ylkä
    ("([lr])ke$",                     r"\1je"),   # -lke/-rke
    ("euku$",                         "eu'u"),    # -euku
    ("([uy])k([uy])$",                r"\1v\2"),  # -UkU
    ("([aeiouyäöhlr])k([aeiouyäö])$", r"\1\2"),   # -VkV/-hkV/-lkV/-rkV
    # p
    ("pp([aeiouyäö])$",               r"p\1"),    # -ppV
    ("mp([aeiouyäö])$",               r"mm\1"),   # -mpV
    ("([aeiouyäölr])p([aeiouyäö])$",  r"\1v\2"),  # -VpV/-lpV/-rpV
    # t
    ("tt([aeiouyäö])$",             r"t\1"),     # -ttV
    ("([lnr])t([aeiouyäö])$",       r"\1\1\2"),  # -ltV/-ntV/-rtV
    ("([aeiouyäöh])t([aeiouyäö])$", r"\1d\2"),   # -VtV/-htV
)
#
# weak to strong
_CONS_GRAD_STRENGTHEN = (
    # k
    ("([aeiouyäölnr])k(aa?|ee?)$",        r"\1kk\2"),  # tikas
    ("([aeiouyäö])ng(aa?|ää?|ere?)$",     r"\1nk\2"),  # penger
    ("([hl])j(ee?)$",                     r"\1k\2"),   # hylje
    ("([aeiouyäöh])(ene?|ime|in)$",       r"\1k\2"),   # säen
    ("([aeiouyäö]|ar)(aa|ee|ii)$",        r"\1k\2"),   # ies
    ("(iu)([ae])$",                       r"\1k\2"),   # kiuas
    ("^([a-zäö]?[aeiouyäö]|var)([aei])$", r"\1k\2"),   # ruis
    # p
    ("([aeiouyäölmr])p(aa?|ää?|ee?)$",               r"\1pp\2"),  # ape
    ("([aeiouyäö])mm(aa?|ää?|ee?|yy?|ele?|imä|ye)$", r"\1mp\2"),  # lämmin
    ("([aeiouyäölr])v(aa?|ää?|ee?|[ai][lmn]e?)$",    r"\1p\2"),   # taival
    # t
    ("([aeiouyäölnr])t(aa?|ää?|ee?|ii?|uu?|yy?)$", r"\1tt\2"),  # altis
    ("([aeiouyäö])t(a|ä|[aäioö][mnr][aäe]?)$",     r"\1tt\2"),  # heitin
    (r"([lnr])\1(aa?|ää?|ee?|[aei][lmnr]e?)$",     r"\1t\2"),   # kallas
    ("([aeiouyäöh])d(aa?|ee?|[ai][mnr]e?)$",       r"\1t\2"),   # pidin
    ("(u)(ere?)$",                                 r"\1t\2"),   # auer
)

def _consonant_gradation(word, strengthen=False):
    # apply consonant gradation to the word
    # strengthen: False = strong to weak, True = weak to strong

    regexes = _CONS_GRAD_STRENGTHEN if strengthen else _CONS_GRAD_WEAKEN
    for (reFrom, reTo) in regexes:
        if re.search(reFrom, word) is not None:
            return re.sub(reFrom, reTo, word)
    return word

# -----------------------------------------------------------------------------

def _change_suffixes(word, decl, regexes):
    # change the final consonant/vowel of a word using a regex
    # regexes: {declension: ((regex_from, regex_to), ...), ...}
    # only the first matching regex_from will be applied

    for (reFrom, reTo) in regexes.get(decl, ()):
        if re.search(reFrom, word) is not None:
            return re.sub(reFrom, reTo, word)
    return word

# declension: ((regex_from, regex_to), ...); only 1st match will be applied
_CONSONANTS_GEN_ESS_PAR = {
    # -n
    10: (("n$",   ""),),   # kahdeksan
    32: (("nen$", "n"),),  # kymmenen
    38: (("nen$", "s"),),  # nainen
}
_CONSONANTS_GEN_SG_ESS_SG_PAR_SG = {
    # -s, -si
    27: (("si$", "ti"),),  # käsi
    28: (("si$", "ti"),),  # kynsi
    40: (("s$",  "ti"),),  # kalleus
}
_CONSONANTS_GEN_SG_ESS_SG = {
    # -n
    33: (("n$", "m"),),   # kytkin
    34: (("n$", "m"),),   # onneton
    35: (("n$", "m"),),   # lämmin
    36: (("n$", "mm"),),  # sisin
    37: (("n$", "mm"),),  # vasen
    # -s, -si
    31: (("ksi$", "hti"),),  # kaksi
    39: (("s$",   "ks"),),   # vastaus
    41: (("s$",   ""),),     # vieras
    42: (("s$",   "h"),),    # mies
    45: (("s$",   "nt"),),   # kahdeksas
    # -t
    43: (("t$", ""),),    # ohut
    44: (("t$", ""),),    # kevät
    46: (("t$", "nt"),),  # tuhat
    47: (("t$", ""),),    # kuollut
}
_VOWELS_GEN_SG_ESS_SG_PAR_SG = {
    # -C -> -Ci
    5: (("([^aeiouyäö])$", r"\1i"),),  # rock
    6: (("([^aeiouyäö])$", r"\1i"),),  # nylon
    # -i -> -e
    7: (("i$", "e"),),  # ovi
    # -i -> -A
    16: (("^([^aou]+)i$", r"\1ä"), ("i$", "a")),  # vanhempi
}
_VOWELS_GEN_SG_ESS_SG = {
    # -i -> -e
    23: (("i$", "e"),),
    24: (("i$", "e"),),
    25: (("i$", "e"),),
    26: (("i$", "e"),),
    27: (("i$", "e"),),
    28: (("i$", "e"),),
    29: (("i$", "e"),),
    30: (("i$", "e"),),
    31: (("i$", "e"),),
    40: (("i$", "e"),),
    # - -> -e
    32: (("$", "e"),),
    33: (("$", "e"),),
    38: (("$", "e"),),
    39: (("$", "e"),),
    42: (("$", "e"),),
    43: (("$", "e"),),
    45: (("$", "e"),),
    46: (("$", "e"),),
    49: (("$", "e"),),
    # - -> -A
    34: (("^([^aou]+)$", r"\1ä"), ("$", "a")),
    35: (("^([^aou]+)$", r"\1ä"), ("$", "a")),
    36: (("^([^aou]+)$", r"\1ä"), ("$", "a")),
    37: (("^([^aou]+)$", r"\1ä"), ("$", "a")),
    # -V -> -VV
    41: (("([aeiouyäö])$", r"\1\1"),),  # vieras
    44: (("([aeiouyäö])$", r"\1\1"),),  # kevät
    48: (("([aeiouyäö])$", r"\1\1"),),  # hame
    # -U -> -ee
    47: (("[uy]$", "ee"),),  # kuollut
}

def _decline_gen_sg(word, decl, consGrad):
    # return inflected form for a case/number that behaves like
    # genitive singular; no case/number ending; e.g. "kaksi" -> "kahde"

    origWord = word

    # irregular changes to final consonant and vowel
    word = _change_suffixes(word, decl, _CONSONANTS_GEN_ESS_PAR)
    word = _change_suffixes(word, decl, _CONSONANTS_GEN_SG_ESS_SG_PAR_SG)
    word = _change_suffixes(word, decl, _CONSONANTS_GEN_SG_ESS_SG)
    word = _change_suffixes(word, decl, _VOWELS_GEN_SG_ESS_SG_PAR_SG)
    word = _change_suffixes(word, decl, _VOWELS_GEN_SG_ESS_SG)

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
        else:
            word = re.sub(r"aaa$", r"aa'a", word)

    return word

def _decline_ess_sg(word, decl, consGrad):
    # return inflected form for a case/number that behaves like
    # essive singular; no case/number ending; e.g. "kaksi" -> "kahte"

    origWord = word

    # irregular changes to final consonant and vowel
    word = _change_suffixes(word, decl, _CONSONANTS_GEN_ESS_PAR)
    word = _change_suffixes(word, decl, _CONSONANTS_GEN_SG_ESS_SG_PAR_SG)
    word = _change_suffixes(word, decl, _CONSONANTS_GEN_SG_ESS_SG)
    word = _change_suffixes(word, decl, _VOWELS_GEN_SG_ESS_SG_PAR_SG)
    word = _change_suffixes(word, decl, _VOWELS_GEN_SG_ESS_SG)

    # strengthening consonant gradation
    if consGrad and decl >= 32 or decl in (36, 37):
        word = _consonant_gradation(word, True)

    return word

_CONSONANTS_PAR_SG = {
    # -mi
    25: (("mi$", "ni"),),  # toimi
    # -s, -si
    29: (("[kp]si$", "si"),),  # lapsi
    30: (("tsi$",    "si"),),  # veitsi
    31: (("ksi$",    "hi"),),  # kaksi
    45: (("s$",      "t"),),   # kahdeksas
}
_VOWELS_PAR_SG = {
    # -i -> -
    23: (("i$", ""),),
    24: (("i$", ""),),
    25: (("i$", ""),),
    26: (("i$", ""),),
    27: (("i$", ""),),
    28: (("i$", ""),),
    29: (("i$", ""),),
    30: (("i$", ""),),
    31: (("i$", ""),),
    40: (("i$", ""),),
}

def _decline_par_sg(word, decl, consGrad):
    # return inflected form for a case/number that behaves like
    # partitive singular; no case/number ending; e.g. "kaksi" -> "kaht"

    # irregular changes to final consonant and vowel
    word = _change_suffixes(word, decl, _CONSONANTS_GEN_ESS_PAR)
    word = _change_suffixes(word, decl, _CONSONANTS_GEN_SG_ESS_SG_PAR_SG)
    word = _change_suffixes(word, decl, _CONSONANTS_PAR_SG)
    word = _change_suffixes(word, decl, _VOWELS_GEN_SG_ESS_SG_PAR_SG)
    word = _change_suffixes(word, decl, _VOWELS_PAR_SG)

    return word

_CONSONANTS_GEN_PL_PAR_PL = {
    # -n
    34: (("n$",   "m"),),   # onneton
    35: (("n$",   "m"),),   # lämmin
    36: (("n$",   "mm"),),  # sisin
    37: (("n$",   "mm"),),  # vasen
    # -s
    40: (("s$", "ks"),),  # kalleus
    41: (("s$", ""),),    # vieras
    45: (("s$", "ns"),),  # kahdeksas
    # -t
    43: (("t$", ""),),    # ohut
    44: (("t$", ""),),    # kevät
    46: (("t$", "ns"),),  # tuhat
    47: (("t$", ""),),    # kuollut
}
_VOWELS_GEN_PL_PAR_PL = {
    # -i -> -
    7:  (("i$", ""),),  # ovi
    16: (("i$", ""),),  # vanhempi
    # -a -> -
    10: (("a$", ""),),  # koira
    # -A -> -O
    9:  (("a$", "o"), ("ä$", "ö")),  # kala
    11: (("a$", "o"), ("ä$", "ö")),  # omena
    12: (("a$", "o"), ("ä$", "ö")),  # kulkija
    13: (("a$", "o"), ("ä$", "ö")),  # katiska
    14: (("a$", "o"), ("ä$", "ö")),  # solakka
    # -VV -> V
    17: ((r"([ay])\1$", r"\1"),),  # vapaa
    18: ((r"([ai])\1$", r"\1"),),  # maa
    20: ((r"([ae])\1$", r"\1"),),  # filee
    41: ((r"([a])\1$",  r"\1"),),  # vieras
    #
    15: (("[aä]$", ""),),   # korkea
    47: (("[uy]$", "e"),),  # kuollut
    #
    19: (("ie$", "e"), ("uo$", "o"), ("yö$", "ö")),  # suo
}
_VOWELS_GEN_PL = {
    # -i -> -
    5: (("i$", ""),),  # risti
    6: (("i$", ""),),  # paperi
}

def _decline_gen_pl(word, decl, consGrad):
    # return inflected form for a case/number that behaves like
    # genitive plural; no case/number ending; e.g. "kaksi" -> "kaks"

    # irregular changes to final consonant and vowel
    word = _change_suffixes(word, decl, _CONSONANTS_GEN_ESS_PAR)
    word = _change_suffixes(word, decl, _CONSONANTS_GEN_PL_PAR_PL)
    word = _change_suffixes(word, decl, _VOWELS_GEN_PL_PAR_PL)
    word = _change_suffixes(word, decl, _VOWELS_GEN_PL)
    if 23 <= decl <= 31:
        word = re.sub("i$", "", word)  # -i -> -
    elif 34 <= decl <= 37:
        word += ("a" if re.search(r"^[^aáou]+$", word) is None else "ä")

    return word

_VOWELS_PAR_PL = {
    # -i -> -e, -C -> -Ce
    5: (("i$", "e"), ("([^aeiouyäö])$", r"\1e")),  # risti, sioux
    6: (("i$", "e"), ("([^aeiouyäö])$", r"\1e")),  # paperi, lumen
}

def _decline_par_pl(word, decl, consGrad):
    # return inflected form for a case/number that behaves like
    # partitive plural; no case/number ending; e.g. "kaksi" -> "kaks"

    # irregular changes to final consonant and vowel
    word = _change_suffixes(word, decl, _CONSONANTS_GEN_ESS_PAR)
    word = _change_suffixes(word, decl, _CONSONANTS_GEN_PL_PAR_PL)
    word = _change_suffixes(word, decl, _VOWELS_GEN_PL_PAR_PL)
    word = _change_suffixes(word, decl, _VOWELS_PAR_PL)
    if 23 <= decl <= 31:
        word = re.sub("i$", "", word)  # -i -> -
    elif 34 <= decl <= 37:
        word += ("a" if re.search(r"^[^aáou]+$", word) is None else "ä")

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
    elif case == "gen" and number == "pl":
        inflected = _decline_gen_pl(word, decl, consGrad)
    elif case == "par" and number == "pl":
        inflected = _decline_par_pl(word, decl, consGrad)
    else:
        sys.exit("Error: this should never happen.")

    # add variants of inflected form
    words = [inflected]
    if (case, number) in _CASES_LIKE_GEN_SG \
    and word in _OPTIONAL_CONS_GRAD_GEN_SG:
        words.append(word)
    elif word in ("häive", "viive"):
        if not (case in ("nom", "par") and number == "sg"):
            words.append(word + "e")
    elif word == "paras":
        if case in ("gen", "par") and number == "pl":
            words = ["parha"]
        elif not (case in ("nom", "par") and number == "sg"):
            words = ["parhaa"]
    elif word == "pop":
        if case in ("ess", "ill", "par") and number == "sg":
            words.append("poppi")
        elif case == "gen" and number == "pl":
            words.append("popp")
        elif case == "par" and number == "pl":
            words.append("poppe")
    elif word == "ryntys":
        if case in ("ess", "ill") and number == "sg":
            words = ["rynttyy"]
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
        elif decl == 25:  # toimi
            yield from (f"{w[:-1]}me{v}" for w in words for v in endingVowels)
        elif decl == 37:  # vasen
            yield from (
                f"{w[:-1]}mp{2*v}" for w in words for v in endingVowels
            )
        # -tA
        if decl == 48 or decl == 49 and word.endswith("e"):  # hame, askel
            yield from (f"{w}tt{v}" for w in words for v in endingVowels)
        elif decl in (3, 15) or decl >= 17:
            yield from (f"{w}t{v}" for w in words for v in endingVowels)
            if word == "jersey":
                yield word + "ä"
    elif case in ("gen", "par") and number == "pl":
        # genitive plural or partitive plural
        # -jen/-jA
        if decl in (1, 2, 4, 8, 9, 11, 13, 14) \
        or case == "par" and decl in (5, 6):
            if case == "gen":
                yield from (w + "jen" for w in words)
            else:
                yield from (f"{w}j{v}" for w in words for v in endingVowels)
        # -iden/-itA
        if decl in (2, 3, 4, 6, 41, 43, 44, 47, 48) \
        or 11 <= decl <= 22 and not decl == 16 \
        or decl == 49 and word.endswith("e"):
            words2 = words
            if word == "häive":
                words2 = ("häipe", "häive")
            elif word == "viive":
                words2 = ("viipe", "viive")
            elif consGrad and decl in (4, 14):
                words2 = tuple(_consonant_gradation(w) for w in words2)
            elif consGrad and decl in (41, 43, 48):
                words2 = tuple(_consonant_gradation(w, True) for w in words2)
            #
            if case == "gen":
                if decl == 6:  # paperi, lumen
                    words2 = tuple(re.sub("$", "e", w) for w in words2)
                yield from (w + "iden" for w in words2)
            else:
                yield from (f"{w}it{v}" for w in words2 for v in endingVowels)
        # -ien/-iA/-ten
        if decl in (7, 10, 11, 16, 42, 45, 46) or 23 <= decl <= 40 \
        or decl == 49 and not word.endswith("e") \
        or case == "gen" and decl in (5, 6):
            # -ien/-iA
            words2 = words
            if consGrad and decl in (32, 33, 34, 49) or decl in (35, 36, 37):
                # lämmin, sisin, vasen
                words2 = tuple(_consonant_gradation(w, True) for w in words2)
            #
            if decl in (10, 34, 35, 36, 37):
                # koira, onneton, lämmin, sisin, vasen
                words2 = tuple(re.sub("[aä]$", "", w) for w in words2)
            elif decl == 11:  # omena
                words2 = tuple(re.sub("[oö]$", "", w) for w in words2)
            elif decl == 33:  # kytkin
                words2 = tuple(re.sub("n$", "m", w) for w in words2)
            elif decl == 39:  # vastaus
                words2 = tuple(re.sub("s$", "ks", w) for w in words2)
            elif decl == 42:  # mies
                words2 = tuple(re.sub("s$", "h", w) for w in words2)
            #
            if case == "gen":
                yield from (w + "ien" for w in words2)
            else:
                yield from (f"{w}i{v}" for w in words2 for v in endingVowels)
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
                elif decl == 46:  # tuhat
                    words2 = tuple(re.sub("ns$", "n", w) for w in words2)
                yield from (re.sub("m$", "n", w) + "ten" for w in words2)
    else:
        sys.exit("Error: this should never happen.")

def decline_noun(word, case, number):
    """Generate inflected forms of a Finnish noun. May contain duplicates."""
    for decl in noundecl.get_declensions(word):
        # errors in source data
        if word == "siitake" and decl == 8 \
        or word in ("alpi", "helpi") and decl == 5:
            consGrad = False
        elif word in ("auer", "hynte", "näin", "pue", "ryntys"):
            consGrad = True
        else:
            consGrad = noun_consgrad.get_consonant_gradation(word, decl)
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
