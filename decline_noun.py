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

# regexes for changing final consonants and vowels
# key = declension, value = ((regex_from, regex_to), ...)
# note: only the first match will be applied
#
# consonants - genitive singular, essive singular, partitive singular
_FINAL_CONS_CHANGES_COMMON = {
    # -n
    10: (("n$",   ""),),   # e.g. kahdeksan
    32: (("nen$", "n"),),  # e.g. kymmenen
    38: (("nen$", "s"),),  # e.g. nainen
    # -si, -s
    27: (("si$", "ti"),),  # e.g. käsi
    28: (("si$", "ti"),),  # e.g. kynsi
    40: (("s$",  "t"),),   # e.g. kalleus
}
#
# consonants - genitive singular, essive singular
_FINAL_CONS_CHANGES_GEN_SG_ESS_SG = {
    # -n
    33: (("n$", "m"),),
    34: (("n$", "m"),),
    35: (("n$", "m"),),
    36: (("n$", "mp"),),
    37: (("n$", "mp"),),
    # -s, -si
    31: (("ksi$", "hti"),),
    39: (("s$",   "ks"),),
    41: (("s$",   ""),),
    42: (("s$",   "h"),),
    45: (("s$",   "nt"),),
    # -t
    43: (("t$", ""),),
    44: (("t$", ""),),
    46: (("t$", "nt"),),
    47: (("t$", ""),),
}
#
# consonants - partitive singular
_FINAL_CONS_CHANGES_PAR_SG = {
    # -s, -si
    29: (("[kp]si$", "si"),),
    30: (("tsi$",    "si"),),
    31: (("ksi$",    "hi"),),
    45: (("s$",      "t"),),
}
#
# vowels - genitive singular, essive singular, partitive singular
_FINAL_VOWEL_CHANGES_COMMON = {
    # - -> -i if not already -i
    5:  (("([^i])$", r"\1i"),),  # e.g. rock
    6:  (("([^i])$", r"\1i"),),  # e.g. nylon
    # -i -> -e
    7:  (("i$", "e"),),  # e.g. ovi
    # -i -> -A
    16: (("^([^aou]+)i$", r"\1ä"), ("i$", "a")),  # e.g. vanhempi
}
#
# vowels - genitive singular, essive singular
_FINAL_VOWEL_CHANGES_GEN_SG_ESS_SG = {
    # - -> -e
    32: (("$", "e"),),
    33: (("$", "e"),),
    38: (("$", "e"),),
    39: (("$", "e"),),
    40: (("$", "e"),),
    42: (("$", "e"),),
    43: (("$", "e"),),
    45: (("$", "e"),),
    46: (("$", "e"),),
    49: (("$", "e"),),
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
    # - -> -A
    34: (("^([^aou]+)$", r"\1ä"), ("$", "a")),
    35: (("^([^aou]+)$", r"\1ä"), ("$", "a")),
    36: (("^([^aou]+)$", r"\1ä"), ("$", "a")),
    37: (("^([^aou]+)$", r"\1ä"), ("$", "a")),
    # -U -> -ee
    47: (("[uy]$", "ee"),),
    # -V -> -VV
    41: (("([aeiouyäö])$", r"\1\1"),),
    44: (("([aeiouyäö])$", r"\1\1"),),
    48: (("([aeiouyäö])$", r"\1\1"),),
}

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
    ("([aeiouyäölnr])k(aa|ee)$",   r"\1kk\2"),  # e.g. tikas
    ("([aeiouyäö])ng(aa|ää|ere)$", r"\1nk\2"),  # e.g. penger
    ("([hl])j(ee)$",               r"\1k\2"),   # e.g. hylje
    ("([aeiouyäöh])(ene|ime)$",    r"\1k\2"),   # e.g. säen
    ("([aeiouyäö]|ar)(aa|ee|ii)$", r"\1k\2"),   # e.g. ruis
    # p
    ("([aeiouyäölmr])p(aa|ää|ee)$",        r"\1pp\2"),  # e.g. ape
    ("([aeiouyäö])mm(aa|ee|ele|imä|ye)$",  r"\1mp\2"),  # e.g. lämmin
    ("([aeiouyäölr])v(aa|ää|ee|ale|ime)$", r"\1p\2"),   # e.g. taival
    # t
    ("([aeiouyäölnr])t(aa|ää|ee|ii|uu|yy)$",  r"\1tt\2"),  # e.g. altis
    ("([aeiouyäö])t(are|äre|ime|oma|ömä)$",   r"\1tt\2"),  # e.g. heitin
    (r"([lnr])\1(aa|ää|ee|are|ele|ere|ime)$", r"\1t\2"),   # e.g. kallas
    ("([aeiouyäöh])d(aa|ee|are|ime)$",        r"\1t\2"),   # e.g. pidin
    ("(u)(ere)$",                             r"\1t\2"),   # e.g. auer
)

# these words allow both "a" and "ä" in their -A endings;
# (word, declension)
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

# vowels to use in illative singular endings (-hVn) in declensions 21 and 22
_ILL_SG_VOWELS_21_22 = {
    # 21 (default is final vowel)
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
    # 22 (default is "e")
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

# consonant gradation in GenSg and similar cases is optional for these words
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

# grammatical cases supported (first 3 letters of each)
_CASES = (
    "nom", "gen", "par", "ess", "tra", "ine", "ela", "ill", "ade", "abl",
    "all", "abe", "ins"
)

# grammatical numbers supported (singular, plural)
_NUMBERS = ("sg", "pl")

# currently supported combinations of (case, number)
_SUPPORTED_CASES = (
    ("nom", "sg"),
    ("nom", "pl"),
    ("gen", "sg"),
    ("par", "sg"),
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

def _apply_regex(word, decl, regexes):
    # regexes: {declension: ((regex_from, regex_to), ...), ...}
    # only the first matching regex_from will be applied

    for (reFrom, reTo) in regexes.get(decl, ()):
        if re.search(reFrom, word) is not None:
            return re.sub(reFrom, reTo, word)
    return word

def _consonant_gradation(word, strengthen=False):
    # apply consonant gradation
    # strengthen: False = strong to weak, True = weak to strong

    regexes = _CONS_GRAD_STRENGTHEN if strengthen else _CONS_GRAD_WEAKEN
    for (reFrom, reTo) in regexes:
        if re.search(reFrom, word) is not None:
            return re.sub(reFrom, reTo, word)
    return word

def _decline_gen_sg(word, decl, consGrad):
    # return inflected form for a case/number that behaves like
    # genitive singular; no case/number ending; e.g. "kaksi" -> "kahde"

    origWord = word

    # irregular changes to final consonant and vowel
    word = _apply_regex(word, decl, _FINAL_CONS_CHANGES_COMMON)
    word = _apply_regex(word, decl, _FINAL_CONS_CHANGES_GEN_SG_ESS_SG)
    word = _apply_regex(word, decl, _FINAL_VOWEL_CHANGES_COMMON)
    word = _apply_regex(word, decl, _FINAL_VOWEL_CHANGES_GEN_SG_ESS_SG)

    # consonant gradation (consonant gradation data has some errors)
    if consGrad and decl >= 32 or origWord in (
        "auer", "hynte", "näin", "pue", "ryntys"
    ):
        # strengthening
        word = _consonant_gradation(word, True)
    elif consGrad and not (
        origWord == "pop"
        or origWord in ("alpi", "helpi") and decl == 5
        or origWord == "siitake" and decl == 8
    ) or decl in (27, 28, 31, 36, 37, 40, 45, 46):
        # weakening
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
    word = _apply_regex(word, decl, _FINAL_CONS_CHANGES_COMMON)
    word = _apply_regex(word, decl, _FINAL_CONS_CHANGES_GEN_SG_ESS_SG)
    word = _apply_regex(word, decl, _FINAL_VOWEL_CHANGES_COMMON)
    word = _apply_regex(word, decl, _FINAL_VOWEL_CHANGES_GEN_SG_ESS_SG)

    # strengthening consonant gradation
    # (consonant gradation data has some errors)
    if consGrad and decl >= 32 or origWord in ("auer", "hynte", "näin", "pue"):
        word = _consonant_gradation(word, True)

    return word

def _decline_par_sg(word, decl, consGrad):
    # return inflected form for a case/number that behaves like
    # partitive singular; no case/number ending; e.g. "kaksi" -> "kaht"

    # irregular changes to final consonant and vowel
    word = _apply_regex(word, decl, _FINAL_CONS_CHANGES_COMMON)
    word = _apply_regex(word, decl, _FINAL_CONS_CHANGES_PAR_SG)
    word = _apply_regex(word, decl, _FINAL_VOWEL_CHANGES_COMMON)
    if 23 <= decl <= 31:
        word = re.sub("i$", "", word)

    # strengthening consonant gradation
    if consGrad and decl >= 32:
        word = _consonant_gradation(word, True)

    return word

def _decline_noun_specific(word, decl, consGrad, case, number):
    # generate inflected forms of a Finnish noun using specified declension
    # (1-49) and consonant gradation (bool)

    #print(word, decl, consGrad)

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
    else:
        sys.exit("Error: this should never happen.")

    # add variants of inflected form and store all in a tuple
    if (case, number) in _CASES_LIKE_GEN_SG \
    and word in _OPTIONAL_CONS_GRAD_GEN_SG:
        words = (inflected, word)
    elif word in ("häive", "viive") \
    and not (case in ("nom", "par") and number == "sg"):
        words = (inflected, word + "e")
    elif word == "paras" \
    and not (case in ("nom", "par") and number == "sg"):
        words = ("parhaa",)
    elif word == "pop" and case in ("ess", "ill", "par") and number == "sg":
        words = (inflected, "poppi")
    elif word == "ryntys" and case in ("ess", "ill") and number == "sg":
        words = ("rynttyy",)
    elif word == "tuomas" and case == "ill" and number == "sg":
        words = (inflected, word[:-1] + "k")
    elif word == "tuomas" and not (case in ("nom", "par") and number == "sg"):
        words = (inflected, word[:-1] + "kse")
    else:
        words = (inflected,)

    # append apostrophe
    if decl == 22 and not (case == "nom" and number == "sg"):
        words = tuple(f"{w}'" for w in words)

    # append case/number endings and generate words
    if case == "nom" and number == "sg":
        yield from words
    elif (case, number) in _CASES_LIKE_GEN_SG:
        # many case/number combinations that resemble genitive singular
        if case in ("nom", "gen", "tra", "all"):
            yield from (f"{w}{_GEN_SG_LIKE_ENDINGS[case]}" for w in words)
        else:
            yield from (
                f"{w}{_GEN_SG_LIKE_ENDINGS[case]}{v}"
                for w in words for v in endingVowels
            )
    elif case == "ess" and number == "sg":
        # essive singular
        yield from (f"{w}n{v}" for w in words for v in endingVowels)
    elif case == "ill" and number == "sg":
        # illative singular
        if decl == 20:
            yield from (f"{w}h{w[-1]}n" for w in words)
            yield from (f"{w}seen" for w in words)
        elif decl in (18, 19):
            yield from (f"{w}h{w[-1]}n" for w in words)
        elif decl == 21:
            yield from (
                f"{w}h{v}n"
                for w in words
                for v in _ILL_SG_VOWELS_21_22.get(word, w[-1])
            )
            if word == "jersey":
                yield from (w + "yn" for w in words)  # additional
        elif decl == 22:
            for w in words:
                yield from (
                    f"{w}h{v}n"
                    for v in _ILL_SG_VOWELS_21_22.get(word, "e")
                )
        elif decl in (17, 41, 44, 47, 48) \
        or decl == 49 and word.endswith("e"):
            yield from (f"{w}seen" for w in words)
        else:
            yield from (f"{w}{w[-1]}n" for w in words)
    elif case == "par" and number == "sg":
        # partitive singular
        if decl == 25:
            # e.g. toimi -> toim -> toimea/tointa
            yield from (f"{w}e{v}" for w in words for v in endingVowels)
            yield from (f"{w[:-1]}nt{v}" for w in words for v in endingVowels)
        elif decl == 37:
            # e.g. vasen -> vasempaa/vasenta
            yield from (
                f"{w[:-1]}mp{2*v}" for w in words for v in endingVowels
            )
            yield from (f"{w}t{v}" for w in words for v in endingVowels)
        else:
            if decl == 15 or word == "jersey":
                # e.g. korkeaa/korkeata
                middles = ("t", "")
            elif decl == 48 or decl == 49 and word.endswith("e"):
                # e.g. hametta, askeletta
                middles = ("tt",)
            elif decl == 3 or decl >= 17:
                middles = ("t",)
            else:
                middles = ("",)
            yield from (
                f"{w}{m}{v}"
                for w in words for m in middles for v in endingVowels
            )
    else:
        sys.exit("This should never happen.")

def decline_noun(word, case, number):
    """Generate inflected forms of a Finnish noun. May contain duplicates."""
    for decl in noundecl.get_declensions(word):
        consGrad = noun_consgrad.get_consonant_gradation(word, decl)
        yield from _decline_noun_specific(word, decl, consGrad, case, number)

def main():
    if len(sys.argv) == 2:
        word = sys.argv[1]
        allCases = True
    elif len(sys.argv) == 4:
        (word, case, number) = sys.argv[1:]
        if case not in _CASES:
            sys.exit("Invalid case.")
        if number not in _NUMBERS:
            sys.exit("Invalid number.")
        if (case, number) not in _SUPPORTED_CASES:
            sys.exit("Unsupported combination of case and number.")
        allCases = False
    else:
        sys.exit(
            "Decline a Finnish noun. Arguments: NOUN [CASE NUMBER]. Cases: "
            + ", ".join(_CASES) + ". Numbers: " + ", ".join(_NUMBERS) + ". "
            + "If case & number omitted, print all supported combinations."
        )

    if allCases:
        for (case, number) in _SUPPORTED_CASES:
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
