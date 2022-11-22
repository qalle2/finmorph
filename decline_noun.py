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

# combinations of case/number that behave like genitive singular
LIKE_GEN_SG = (
    ("nom", "pl"),
    ("gen", "sg"),
    ("tra", "sg"),
    ("ine", "sg"),
    ("ela", "sg"),
    ("ade", "sg"),
    ("abl", "sg"),
    ("abe", "sg"),
)

# (from, to); the first match will be used
REGEXES_WEAKEN = (
    # t
    (r"([lnr])t([aeiouyäö])$", r"\1\1\2"),  # -ltV/-ntV/-rtV
    (r"tt([aeiouyäö])$", r"t\1"),           # -ttV
    (r"t([aeiouyäö])$",  r"d\1"),           # -tV
    # p
    (r"mp([aeiouyäö])$", r"mm\1"),  # -mpV
    (r"pp([aeiouyäö])$", r"p\1"),   # -ppV
    (r"p([aeiouyäö])$",  r"v\1"),   # -pV
    # k
    (r"([uy])k([uy])$",    r"\1v\2"),  # -UkU
    (r"ylkä$",             r"yljä"),   # -ylkä
    (r"([lr])k(e)$",       r"\1j\2"),  # -lke/-rke
    (r"(n)k([aeiouyäö])$", r"\1g\2"),  # -nkV
    (r"k([aeiouyäö])$",    r"\1"),     # -kV
)

# (from, to); the first match will be used
REGEXES_STRENGTHEN = (
    # k
    (r"([aeiouyäölnr])k(aa|ee)$",   r"\1kk\2"),  # e.g. tikas
    (r"(e)ng(ere)$",                r"\1nk\2"),  # e.g. penger
    (r"([hl])j(ee)$",               r"\1k\2"),   # e.g. hylje
    (r"([aeiouyäöh])(ene|ime)$",    r"\1k\2"),   # e.g. säen
    (r"([aeiouyäö]|ar)(aa|ee|ii)$", r"\1k\2"),   # e.g. ruis
    # p
    (r"([aeiouyäö])p(ee)$",             r"\1pp\2"),  # e.g. ape
    (r"([aeiouyäö])mm(ee|ele|imä|ye)$", r"\1mp\2"),  # e.g. lämmin
    (r"([aeiouyäö])v(aa|ale|ime)$",     r"\1p\2"),   # e.g. taival
    # t
    (r"([aeiouyäöln])t(aa|ää|ii|uu)$",        r"\1tt\2"),  # e.g. altis
    (r"([aeiouyäö])t(are|äre|ime|oma|ömä)$",  r"\1tt\2"),  # e.g. heitin
    (r"([lnr])\1(aa|ää|ee|are|ele|ere|ime)$", r"\1t\2"),   # e.g. kallas
    (r"([aeiouyäöh])d(aa|ee|are|ime)$",       r"\1t\2"),   # e.g. pidin
)

def consonant_gradation(word, strengthen=False):
    # apply consonant gradation
    # strengthen: strengthen if True, else weaken

    regexes = REGEXES_STRENGTHEN if strengthen else REGEXES_WEAKEN
    for (reFrom, reTo) in regexes:
        if re.search(reFrom, word) is not None:
            return re.sub(reFrom, reTo, word)
    return word

# declension: (regex_from, regex_to)
FINAL_CONS_CHANGES = {
    # -n
    10: (r"n$",   r""),
    32: (r"nen$", r"n"),
    33: (r"n$",   r"m"),
    34: (r"n$",   r"m"),
    35: (r"n$",   r"m"),
    36: (r"n$",   r"mp"),
    37: (r"n$",   r"mp"),
    38: (r"nen$", r"s"),
    # -s, -si
    27: (r"si$",  r"ti"),
    28: (r"si$",  r"ti"),
    31: (r"ksi$", r"hti"),
    39: (r"s$",   r"ks"),
    40: (r"s$",   r"t"),
    41: (r"s$",   r""),
    42: (r"s$",   r"h"),
    45: (r"s$",   r"nt"),
    # -t
    43: (r"t$",   r""),
    44: (r"t$",   r""),
    46: (r"t$",   r"nt"),
    47: (r"t$",   r""),
}

# declension: ((regex_from, regex_to), ...)
FINAL_VOWEL_CHANGES = {
    # - -> -e
    32: ((r"$", r"e"),),
    33: ((r"$", r"e"),),
    38: ((r"$", r"e"),),
    39: ((r"$", r"e"),),
    40: ((r"$", r"e"),),
    42: ((r"$", r"e"),),
    43: ((r"$", r"e"),),
    45: ((r"$", r"e"),),
    46: ((r"$", r"e"),),
    49: ((r"$", r"e"),),
    # - -> -i if not already -i
    5:  ((r"([^i])$", r"\1i"),),
    6:  ((r"([^i])$", r"\1i"),),
    # -i -> -e
    7:  ((r"i$", r"e"),),
    23: ((r"i$", r"e"),),
    24: ((r"i$", r"e"),),
    25: ((r"i$", r"e"),),
    26: ((r"i$", r"e"),),
    27: ((r"i$", r"e"),),
    28: ((r"i$", r"e"),),
    29: ((r"i$", r"e"),),
    30: ((r"i$", r"e"),),
    31: ((r"i$", r"e"),),
    # - -> -A
    34: ((r"^([^aou]+)$", r"\1ä"), (r"$", r"a")),
    35: ((r"^([^aou]+)$", r"\1ä"), (r"$", r"a")),
    36: ((r"^([^aou]+)$", r"\1ä"), (r"$", r"a")),
    37: ((r"^([^aou]+)$", r"\1ä"), (r"$", r"a")),
    44: ((r"^([^aou]+)$", r"\1ä"), (r"$", r"a")),
    # -i -> -A
    16: ((r"^([^aou]+)i$", r"\1ä"), (r"i$", r"a")),
    # -U -> -ee
    47: ((r"[uy]$", r"ee"),),
    # -V -> -VV
    41: ((r"([aeiouyäö])$", r"\1\1"),),
    48: ((r"([aeiouyäö])$", r"\1\1"),),
}

def decline_noun_gen_sg(word, decl, consGrad):
    # decline a noun for a case/number that behaves like genitive singular;
    # no case/number ending; e.g. "kaksi" -> "kahde"

    # irregular changes to final consonant
    (reFrom, reTo) = FINAL_CONS_CHANGES.get(decl, ("", ""))
    word = re.sub(reFrom, reTo, word)

    # irregular changes to final vowel
    for (reFrom, reTo) in FINAL_VOWEL_CHANGES.get(decl, ()):
        if re.search(reFrom, word) is not None:
            word = re.sub(reFrom, reTo, word)
            break

    #print(word, decl, consGrad)

    # consonant gradation
    if consGrad and decl in (32, 33, 34, 35, 41, 43, 48, 49) \
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

    # apostrophe
    if decl == 22:  # "parfait"
        word += "'"

    return word

def decline_noun(word, decl, consGrad, case, number):
    # decline a Finnish noun

    # use back or front vowels for endings?
    useBackVowels = re.search(r"^[^aou]+$", word) is None

    if (case, number) in LIKE_GEN_SG:
        word = decline_noun_gen_sg(word, decl, consGrad)

        if case == "nom":
            return word + "t"
        if case == "gen":
            return word + "n"
        if case == "tra":
            return word + "ksi"
        if case == "ine":
            return word + "ss" + ("a" if useBackVowels else "ä")
        if case == "ela":
            return word + "st" + ("a" if useBackVowels else "ä")
        if case == "ade":
            return word + "ll" + ("a" if useBackVowels else "ä")
        if case == "abl":
            return word + "lt" + ("a" if useBackVowels else "ä")
        if case == "abe":
            return word + "tt" + ("a" if useBackVowels else "ä")

    sys.exit("Case/number not implemented.")

def decline_noun_main(word, case, number):
    # get declension and consonant gradation of a Finnish noun;
    # generate (declension, consonant_gradation_applies)

    for decl in noundecl.get_declensions(word):
        consGrad = noun_consgrad.get_consonant_gradation(word, decl)
        yield decline_noun(word, decl, consGrad, case, number)

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

    declinedNouns = sorted(decline_noun_main(word, case, number))
    if not declinedNouns:
        sys.exit("Unrecognized noun.")

    print("/".join(declinedNouns))

if __name__ == "__main__":
    main()
