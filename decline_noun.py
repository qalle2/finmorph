# decline a Finnish noun

import re, sys
import noun_consgrad
import noundecl

# Kotus declensions:
# 1=valo, 2=palvelu, 3=valtio, 4=laatikko, 5=risti, 6=paperi, 7=ovi, 8=nalle,
# 9=kala, 10=koira/kahdeksan, 11=omena, 12=kulkija, 13=katiska, 14=solakka,
# 15=korkea, 16=vanhempi, 17=vapaa, 18=maa, 19=suo, 20=filee, 21=rosé,
# 22=parfait, 23=tiili, 24=uni, 25=toimi, 26=pieni, 27=käsi, 28=kynsi,
# 29=lapsi, 30=veitsi, 31=kaksi, 32=sisar/kymmenen, 33=kytkin, 34=onneton,
# 35=lämmin, 36=sisin, 37=vasen, 38=nainen, 39=vastaus, 40=kalleus, 41=vieras,
# 42=mies, 43=ohut, 44=kevät, 45=kahdeksas, 46=tuhat, 47=kuollut, 48=hame,
# 49=askel/askele

# (regex_from, regex_to); the first match will be used
REGEXES_WEAKEN = (
    # t
    ("([lnr])t([aeiouyäö])$", r"\1\1\2"),  # -ltV/-ntV/-rtV
    ("tt([aeiouyäö])$", r"t\1"),           # -ttV
    ("t([aeiouyäö])$",  r"d\1"),           # -tV
    # p
    ("mp([aeiouyäö])$", r"mm\1"),  # -mpV
    ("pp([aeiouyäö])$", r"p\1"),   # -ppV
    ("p([aeiouyäö])$",  r"v\1"),   # -pV
    # k
    ("([uy])k([uy])$",    r"\1v\2"),  # -UkU
    ("ylkä$",             r"yljä"),   # -ylkä
    ("([lr])k(e)$",       r"\1j\2"),  # -lke/-rke
    ("(n)k([aeiouyäö])$", r"\1g\2"),  # -nkV
    ("k([aeiouyäö])$",    r"\1"),     # -kV
)

# (regex_from, regex_to); the first match will be used
REGEXES_STRENGTHEN = (
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
)

# declension: ((regex_from, regex_to), ...);
# for genitive singular, essive singular and partitive singular
FINAL_CONS_CHANGES_COMMON = {
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
FINAL_CONS_CHANGES_GEN_SG_ESS_SG = {
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
FINAL_CONS_CHANGES_PAR_SG = {
    # -s, -si
    29: (("psi$", "si"),),
    30: (("tsi$", "si"),),
    31: (("ksi$", "hi"),),
    45: (("s$",   "t"),),
}

# declension: ((regex_from, regex_to), ...);
# for genitive singular, essive singular and partitive singular
FINAL_VOWEL_CHANGES_COMMON = {
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
FINAL_VOWEL_CHANGES_GEN_SG_ESS_SG = {
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
FINAL_VOWEL_CHANGES_PAR_SG = {
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

def consonant_gradation(word, strengthen=False):
    # apply consonant gradation
    # strengthen: strengthen if True, else weaken

    regexes = REGEXES_STRENGTHEN if strengthen else REGEXES_WEAKEN
    for (reFrom, reTo) in regexes:
        if re.search(reFrom, word) is not None:
            return re.sub(reFrom, reTo, word)
    return word

def apply_replacement(word, decl, regexes):
    # regexes: {declension: ((regex_from, regex_to), ...), ...}
    # only the first matching regex_from will be applied

    for (reFrom, reTo) in regexes.get(decl, ()):
        if re.search(reFrom, word) is not None:
            return re.sub(reFrom, reTo, word)
    return word

def decline_noun_gen_sg(word, decl, consGrad):
    # return inflected form for a case/number that behaves like
    # genitive singular; no case/number ending; e.g. "kaksi" -> "kahde"

    #print(word, decl, consGrad)

    # irregular changes to final consonant and vowel
    word = apply_replacement(word, decl, FINAL_CONS_CHANGES_COMMON)
    word = apply_replacement(word, decl, FINAL_CONS_CHANGES_GEN_SG_ESS_SG)
    word = apply_replacement(word, decl, FINAL_VOWEL_CHANGES_COMMON)
    word = apply_replacement(word, decl, FINAL_VOWEL_CHANGES_GEN_SG_ESS_SG)

    # consonant gradation
    if consGrad and decl >= 32 \
    or word == "näime" and decl == 33 \
    or word == "puee" and decl == 48:
        # strengthening
        word = consonant_gradation(word, True)
    elif consGrad and not (
        word == "alpi" and decl == 5
        or word == "helpi" and decl == 5
        or word == "siitake" and decl == 8
    ) or decl in (27, 28, 31, 36, 37, 40, 45, 46):
        # weakening
        # (source data incorrectly handles consonant gradation in words with
        # more than one declension)
        word = consonant_gradation(word)
        if word == "aia":
            word = "aja"  # exception for "aika" (not "taika")
        else:
            word = re.sub(r"aaa$", r"aa'a", word)

    return word

def decline_noun_ess_sg(word, decl, consGrad):
    # return inflected form for a case/number that behaves like
    # essive singular; no case/number ending; e.g. "kaksi" -> "kahte"

    #print(word, decl, consGrad)

    # irregular changes to final consonant and vowel
    word = apply_replacement(word, decl, FINAL_CONS_CHANGES_COMMON)
    word = apply_replacement(word, decl, FINAL_CONS_CHANGES_GEN_SG_ESS_SG)
    word = apply_replacement(word, decl, FINAL_VOWEL_CHANGES_COMMON)
    word = apply_replacement(word, decl, FINAL_VOWEL_CHANGES_GEN_SG_ESS_SG)

    # strengthening consonant gradation
    if consGrad and decl >= 32:
        word = consonant_gradation(word, True)

    return word

def decline_noun_par_sg(word, decl, consGrad):
    # return inflected form for a case/number that behaves like
    # partitive singular; no case/number ending; e.g. "kaksi" -> "kaht"

    #print(word, decl, consGrad)

    # irregular changes to final consonant and vowel
    word = apply_replacement(word, decl, FINAL_CONS_CHANGES_COMMON)
    word = apply_replacement(word, decl, FINAL_CONS_CHANGES_PAR_SG)
    word = apply_replacement(word, decl, FINAL_VOWEL_CHANGES_COMMON)
    word = apply_replacement(word, decl, FINAL_VOWEL_CHANGES_PAR_SG)

    # strengthening consonant gradation
    if consGrad and decl >= 32:
        word = consonant_gradation(word, True)

    return word

def decline_noun(word, decl, consGrad, case, number):
    # generate inflected forms (one or two) of a Finnish noun using specified
    # declension and consonant gradation

    # use back or front vowels for endings?
    useBackVowels = re.search(r"^[^aáou]+$", word) is None

    if number == "pl" and case == "nom" or number == "sg" \
    and case in ("gen", "tra", "ine", "ela", "ade", "abl", "abe"):
        word = decline_noun_gen_sg(word, decl, consGrad)
        if decl == 22:
            word += "'"

        if case == "nom":
            yield word + "t"
        elif case == "gen":
            yield word + "n"
        elif case == "tra":
            yield word + "ksi"
        elif case == "ine":
            yield word + "ss" + ("a" if useBackVowels else "ä")
        elif case == "ela":
            yield word + "st" + ("a" if useBackVowels else "ä")
        elif case == "ade":
            yield word + "ll" + ("a" if useBackVowels else "ä")
        elif case == "abl":
            yield word + "lt" + ("a" if useBackVowels else "ä")
        elif case == "abe":
            yield word + "tt" + ("a" if useBackVowels else "ä")

    elif case == "ess" and number == "sg":
        word = decline_noun_ess_sg(word, decl, consGrad)
        if decl == 22:
            word += "'"
        yield word + "n" + ("a" if useBackVowels else "ä")

    elif case == "ill" and number == "sg":
        # there can be multiple forms
        word = decline_noun_ess_sg(word, decl, consGrad)
        if decl == 20:
            # e.g. fileehen/fileeseen
            yield word + "h" + word[-1] + "n"
            yield word + "seen"
        elif decl in (18, 19):
            yield word + "h" + word[-1] + "n"
        elif decl == 21:
            if word == "rosé":
                yield word + "hen"
            else:
                yield word + "hin"
        elif decl == 22:
            if word == "parfait":
                yield word + "'hen"
            else:
                yield word + "'h" + word[-2] + "n"
        elif decl in (17, 41, 44, 47, 48) \
        or decl == 49 and word.endswith("ee"):
            yield word + "seen"
        else:
            yield word + word[-1] + "n"

    elif case == "par" and number == "sg":
        # there can be multiple forms

        word = decline_noun_par_sg(word, decl, consGrad)
        if decl == 22:
            word += "'"

        if decl == 15:
            # e.g. korkeaa/korkeata
            yield word + ("a" if useBackVowels else "ä")
            yield word + "t" + ("a" if useBackVowels else "ä")
        elif decl == 25:
            # e.g. toimea/tointa
            yield word + "e" + ("a" if useBackVowels else "ä")
            yield word[:-1] + "nt" + ("a" if useBackVowels else "ä")
        elif decl == 37:
            # e.g. vasempaa/vasenta
            yield word[:-1] + "mp" + ("aa" if useBackVowels else "ää")
            yield word + "t" + ("a" if useBackVowels else "ä")
        elif decl == 48 or decl == 49 and word.endswith("e"):
            yield word + "tt" + ("a" if useBackVowels else "ä")
        elif decl == 3 or decl >= 17:
            yield word + "t" + ("a" if useBackVowels else "ä")
        else:
            yield word + ("a" if useBackVowels else "ä")

    else:
        sys.exit("Case/number not implemented.")

def decline_noun_main(word, case, number):
    # generate inflected forms of a Finnish noun
    for decl in noundecl.get_declensions(word):
        consGrad = noun_consgrad.get_consonant_gradation(word, decl)
        yield from decline_noun(word, decl, consGrad, case, number)

def main():
    if len(sys.argv) != 4:
        sys.exit(
            "Decline a Finnish noun. Arguments: noun case number. Cases: "
            "nom, gen, par, ess, tra, ine, ela, ill, ade, abl, all, abe, ins. "
            "Numbers: sg, pl."
        )

    (word, case, number) = sys.argv[1:]
    if case not in (
        "nom", "gen", "par", "ess", "tra", "ine", "ela", "ill", "ade", "abl",
        "all", "abe", "ins"
    ):
        sys.exit("Invalid case.")
    if number not in ("sg", "pl"):
        sys.exit("Invalid number.")

    declinedNouns = sorted(set(decline_noun_main(word, case, number)))
    if not declinedNouns:
        sys.exit("Unrecognized noun.")

    print("/".join(declinedNouns))

if __name__ == "__main__":
    main()
