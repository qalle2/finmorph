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

# consonant gradation - strong to weak;
# (regex_from, regex_to); the first match will be used
_CONS_GRAD_WEAKEN = (
    # k
    ("([uy])k([uy])$",    r"\1v\2"),  # -UkU
    ("ylkä$",             r"yljä"),   # -ylkä
    ("([lr])k(e)$",       r"\1j\2"),  # -lke/-rke
    ("(n)k([aeiouyäö])$", r"\1g\2"),  # -nkV
    ("k([aeiouyäö])$",    r"\1"),     # -kV
    # p
    ("mp([aeiouyäö])$", r"mm\1"),  # -mpV
    ("pp([aeiouyäö])$", r"p\1"),   # -ppV
    ("p([aeiouyäö])$",  r"v\1"),   # -pV
    # t
    ("([lnr])t([aeiouyäö])$", r"\1\1\2"),  # -ltV/-ntV/-rtV
    ("tt([aeiouyäö])$", r"t\1"),           # -ttV
    ("t([aeiouyäö])$",  r"d\1"),           # -tV
)

# consonant gradation - weak to strong;
# (regex_from, regex_to); the first match will be used
_CONS_GRAD_STRENGTHEN = (
    # k
    ("([aeiouyäölnr])k(aa|ee)$",   r"\1kk\2"),  # e.g. tikas
    ("(e)ng(ere)$",                r"\1nk\2"),  # e.g. penger
    ("([hl])j(ee)$",               r"\1k\2"),   # e.g. hylje
    ("([aeiouyäöh])(ene|ime)$",    r"\1k\2"),   # e.g. säen
    ("([aeiouyäö]|ar)(aa|ee|ii)$", r"\1k\2"),   # e.g. ruis
    # p
    ("([aeiouyäö])p(ee)$",             r"\1pp\2"),  # e.g. ape
    ("([aeiouyäö])mm(ee|ele|imä|ye)$", r"\1mp\2"),  # e.g. lämmin
    ("([aeiouyäö])v(aa|ale|ime)$",     r"\1p\2"),   # e.g. taival
    # t
    ("([aeiouyäöln])t(aa|ää|ii|uu)$",         r"\1tt\2"),  # e.g. altis
    ("([aeiouyäö])t(are|äre|ime|oma|ömä)$",   r"\1tt\2"),  # e.g. heitin
    (r"([lnr])\1(aa|ää|ee|are|ele|ere|ime)$", r"\1t\2"),   # e.g. kallas
    ("([aeiouyäöh])d(aa|ee|are|ime)$",        r"\1t\2"),   # e.g. pidin
    ("(u)(ere)$",                             r"\1t\2"),   # e.g. auer
)

# declension: ((regex_from, regex_to), ...);
# for genitive singular, essive singular and partitive singular
_FINAL_CONS_CHANGES_COMMON = {
    # -n
    10: (("n$",   ""),),   # only kahdeksan
    32: (("nen$", "n"),),  # only kymmenen
    38: (("nen$", "s"),),  # e.g. nainen
    # -si, -s
    27: (("si$", "ti"),),  # e.g. käsi
    28: (("si$", "ti"),),  # e.g. kynsi
    40: (("s$",  "t"),),   # e.g. kalleus
}

# declension: ((regex_from, regex_to), ...);
# for genitive singular and essive singular
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

# declension: ((regex_from, regex_to), ...);
# for partitive singular
_FINAL_CONS_CHANGES_PAR_SG = {
    # -s, -si
    29: (("[kp]si$", "si"),),
    30: (("tsi$",    "si"),),
    31: (("ksi$",    "hi"),),
    45: (("s$",      "t"),),
}

# declension: ((regex_from, regex_to), ...);
# for genitive singular, essive singular and partitive singular
_FINAL_VOWEL_CHANGES_COMMON = {
    # - -> -i if not already -i
    5:  (("([^i])$", r"\1i"),),  # e.g. rock
    6:  (("([^i])$", r"\1i"),),  # e.g. nylon
    # -i -> -e
    7:  (("i$", "e"),),  # e.g. ovi
    # -i -> -A
    16: (("^([^aou]+)i$", r"\1ä"), ("i$", "a")),  # e.g. vanhempi
}

# declension: ((regex_from, regex_to), ...);
# for genitive singular and essive singular
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

# declension: ((regex_from, regex_to), ...);
# for partitive singular
_FINAL_VOWEL_CHANGES_PAR_SG = {
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
}

# these words allow both "a" and "ä" in their -A endings;
# (word, declension)
_BOTH_A_AND_AUML = frozenset((
    ("buffet", 22),
    ("caddie", 3),
    ("caddie", 8),
    ("port salut", 22),
    ("menu", 21),
))

# vowels to use in illative singular endings (-hVn) in declensions 21 and 22
_ILL_SG_VOWELS_21_22 = {
    # 21 (default is "i")
    "menu": "uy",
    "rosé": "e",
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

# grammatical cases supported (first 3 letters of each)
_CASES = (
    "nom", "gen", "par", "ess", "tra", "ine", "ela", "ill", "ade", "abl",
    "all", "abe", "ins"
)

# grammatical numbers supported (singular, plural)
_NUMBERS = ("sg", "pl")

def _consonant_gradation(word, strengthen=False):
    # apply consonant gradation
    # strengthen: False = strong to weak, True = weak to strong

    regexes = _CONS_GRAD_STRENGTHEN if strengthen else _CONS_GRAD_WEAKEN
    for (reFrom, reTo) in regexes:
        if re.search(reFrom, word) is not None:
            return re.sub(reFrom, reTo, word)
    return word

def _apply_regex(word, decl, regexes):
    # regexes: {declension: ((regex_from, regex_to), ...), ...}
    # only the first matching regex_from will be applied

    for (reFrom, reTo) in regexes.get(decl, ()):
        if re.search(reFrom, word) is not None:
            return re.sub(reFrom, reTo, word)
    return word

def _decline_gen_sg(word, decl, consGrad):
    # return inflected form for a case/number that behaves like
    # genitive singular; no case/number ending; e.g. "kaksi" -> "kahde"

    #print(word, decl, consGrad)

    # irregular changes to final consonant and vowel
    word = _apply_regex(word, decl, _FINAL_CONS_CHANGES_COMMON)
    word = _apply_regex(word, decl, _FINAL_CONS_CHANGES_GEN_SG_ESS_SG)
    word = _apply_regex(word, decl, _FINAL_VOWEL_CHANGES_COMMON)
    word = _apply_regex(word, decl, _FINAL_VOWEL_CHANGES_GEN_SG_ESS_SG)

    # consonant gradation
    if (
        consGrad and decl >= 32
        or word == "näime" and decl == 33
        or word == "puee" and decl == 48
        or word == "auere" and decl == 49
    ):
        # strengthening
        word = _consonant_gradation(word, True)
    elif consGrad and not (
        word == "alpi" and decl == 5
        or word == "helpi" and decl == 5
        or word == "siitake" and decl == 8
    ) or decl in (27, 28, 31, 36, 37, 40, 45, 46):
        # weakening
        # (source data incorrectly handles consonant gradation in words with
        # more than one declension)
        word = _consonant_gradation(word)
        if word == "aia":
            word = "aja"  # exception for "aika" (not "taika")
        else:
            word = re.sub(r"aaa$", r"aa'a", word)

    return word

def _decline_ess_sg(word, decl, consGrad):
    # return inflected form for a case/number that behaves like
    # essive singular; no case/number ending; e.g. "kaksi" -> "kahte"

    #print(word, decl, consGrad)

    # irregular changes to final consonant and vowel
    word = _apply_regex(word, decl, _FINAL_CONS_CHANGES_COMMON)
    word = _apply_regex(word, decl, _FINAL_CONS_CHANGES_GEN_SG_ESS_SG)
    word = _apply_regex(word, decl, _FINAL_VOWEL_CHANGES_COMMON)
    word = _apply_regex(word, decl, _FINAL_VOWEL_CHANGES_GEN_SG_ESS_SG)

    # strengthening consonant gradation
    if consGrad and decl >= 32 \
    or word in ("auere", "näime", "puee"):
        word = _consonant_gradation(word, True)

    return word

def _decline_par_sg(word, decl, consGrad):
    # return inflected form for a case/number that behaves like
    # partitive singular; no case/number ending; e.g. "kaksi" -> "kaht"

    #print(word, decl, consGrad)

    # irregular changes to final consonant and vowel
    word = _apply_regex(word, decl, _FINAL_CONS_CHANGES_COMMON)
    word = _apply_regex(word, decl, _FINAL_CONS_CHANGES_PAR_SG)
    word = _apply_regex(word, decl, _FINAL_VOWEL_CHANGES_COMMON)
    word = _apply_regex(word, decl, _FINAL_VOWEL_CHANGES_PAR_SG)

    # strengthening consonant gradation
    if consGrad and decl >= 32:
        word = _consonant_gradation(word, True)

    return word

def _decline_noun_specific(word, decl, consGrad, case, number):
    # generate inflected forms (one or more) of a Finnish noun using specified
    # declension and consonant gradation

    # use "a", "ä" or both in -A endings?
    if (word, decl) in _BOTH_A_AND_AUML:
        endingVowels = ("a", "ä")
    elif re.search(r"^[^aáou]+$", word) is not None:
        endingVowels = ("ä",)
    else:
        endingVowels = ("a",)

    if case == "nom" and number == "sg":
        yield word

    elif number == "pl" and case == "nom" or number == "sg" \
    and case in ("gen", "tra", "ine", "ela", "ade", "abl", "all", "abe"):
        word = _decline_gen_sg(word, decl, consGrad)
        if decl == 22:
            word += "'"

        if case == "nom":
            yield word + "t"
        elif case == "gen":
            yield word + "n"
        elif case == "tra":
            yield word + "ksi"
        elif case == "ine":
            yield from (word + "ss" + v for v in endingVowels)
        elif case == "ela":
            yield from (word + "st" + v for v in endingVowels)
        elif case == "ade":
            yield from (word + "ll" + v for v in endingVowels)
        elif case == "abl":
            yield from (word + "lt" + v for v in endingVowels)
        elif case == "all":
            yield word + "lle"
        elif case == "abe":
            yield from (word + "tt" + v for v in endingVowels)

    elif case == "ess" and number == "sg":
        word = _decline_ess_sg(word, decl, consGrad)
        if decl == 22:
            word += "'"
        yield from (word + "n" + v for v in endingVowels)

    elif case == "ill" and number == "sg":
        word = _decline_ess_sg(word, decl, consGrad)

        if decl == 20:
            yield f"{word}h{word[-1]}n"
            yield f"{word}seen"
        elif decl in (18, 19):
            yield f"{word}h{word[-1]}n"
        elif decl == 21:
            yield from (
                f"{word}h{v}n" for v in _ILL_SG_VOWELS_21_22.get(word, "i")
            )
        elif decl == 22:
            yield from (
                f"{word}'h{v}n" for v in _ILL_SG_VOWELS_21_22.get(word, "e")
            )
        elif decl in (17, 41, 44, 47, 48) \
        or decl == 49 and word.endswith("ee"):
            yield word + "seen"
        else:
            yield word + word[-1] + "n"

    elif case == "par" and number == "sg":
        word = _decline_par_sg(word, decl, consGrad)
        if decl == 22:
            word += "'"

        if decl == 15:
            # e.g. korkeaa/korkeata
            yield from (word + v for v in endingVowels)
            yield from (word + "t" + v for v in endingVowels)
        elif decl == 25:
            # e.g. toimea/tointa
            yield from (word + "e" + v for v in endingVowels)
            yield from (word[:-1] + "nt" + v for v in endingVowels)
        elif decl == 37:
            # e.g. vasempaa/vasenta
            yield from (word[:-1] + "mp" + v + v for v in endingVowels)
            yield from (word + "t" + v for v in endingVowels)
        elif decl == 48 or decl == 49 and word.endswith("e"):
            yield from (word + "tt" + v for v in endingVowels)
        elif decl == 3 or decl >= 17:
            yield from (word + "t" + v for v in endingVowels)
        else:
            yield from (word + v for v in endingVowels)

    else:
        sys.exit("Case/number not implemented.")

def decline_noun(word, case, number):
    """Generate inflected forms of a Finnish noun."""
    for decl in noundecl.get_declensions(word):
        consGrad = noun_consgrad.get_consonant_gradation(word, decl)
        yield from _decline_noun_specific(word, decl, consGrad, case, number)

def main():
    if len(sys.argv) != 4:
        sys.exit(
            "Decline a Finnish noun. Arguments: NOUN CASE NUMBER. Cases: "
            + ", ".join(_CASES) + ". Numbers: " + ", ".join(_NUMBERS) + "."
        )

    (word, case, number) = sys.argv[1:]
    if case not in _CASES:
        sys.exit("Invalid case.")
    if number not in _NUMBERS:
        sys.exit("Invalid number.")

    declinedNouns = set(decline_noun(word, case, number))
    if not declinedNouns:
        sys.exit("Unrecognized noun.")

    for noun in sorted(declinedNouns):
        print(noun)

if __name__ == "__main__":
    main()
