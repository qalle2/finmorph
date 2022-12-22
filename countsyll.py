"""Count the number of syllables in a Finnish word."""

# Note: A = a/ä, O = o/ö, U = u/y, V = any vowel, C = one or more consonants.

import re, sys

# regex snippets from which the rules are assembled

# zero or more consonants
_CON_OPT = "[b-df-hj-np-tv-xzšž]*"
# one or more consonants
_CON_REQ = "[b-df-hj-np-tv-xzšž]+"
# any short vowel, long vowel or diphthong, in stressed/unstressed syllables
# (ie & UO in stressed syllables only)
_VOW_STR \
= "( [aeiou][iu]? | [äeiöy][iy]? | aa | ää | ee | oo | öö | ie | uo | yö )"
_VOW_UNSTR \
= "( [aeiou][iu]? | [äeiöy][iy]? | aa | ää | ee | oo | öö )"
# any two vowels in hiatus (syllable break between), in stressed/unstressed
# syllables (ie & UO in unstressed syllables only)
_HIA_STR = (
    "("
        "[äeioöuy]a"
        "| [aeioöuy]ä"
        "| [aäoöuy]e"
        "| [aäeiöy]o"
        "| [aäeiou]ö"
        "| [aeiouyäö]{3,4}"
        "| [aeiou](a'a|i'i|u'u)"
    ")"
)
_HIA_UNSTR = (
    "("
        "[äeioöuy]a"
        "| [aeioöuy]ä"
        "| [aäoöuyi]e"
        "| [aäeiöyu]o"
        "| [aäeiouy]ö"
        "| [aeiouyäö]{3,4}"
        "| [aeiou](a'a|i'i|u'u)"
    ")"
)

# These rules (regexes) and exceptions specify how to count the number of
# syllables in a word.
# Notes - rules:
#   - No foreign vowel letters ("àáâåèéêîôû").
#   - No foreign diphthongs (e.g. "ay").
#   - No punctuation except for "'".
#   - The rules are case insensitive.
# Notes - exceptions:
#   - Start a new line when the first letter changes.

# monosyllabic words: (C)V(C)
# examples: "yö", "snacks"
_REGEX_1SYLL = re.compile(
    "^" + _CON_OPT + _VOW_STR + _CON_OPT + "$",
    re.IGNORECASE | re.VERBOSE
)
_EXCEPTIONS_1SYLL = frozenset((
    "bridge", "byte",
    "gay", "grape", "gray",
    "house",
    "jive",
    "quiche",
    "rave",
    "spray", "squash",
    "trance",
))

# disyllabic words: (C)VCV(C), (C)V'V(C)
# examples: "aho", "aie", "äes", "stretching"
_REGEX_2SYLL = re.compile(
    "^" + _CON_OPT + "("
        + _VOW_STR + _CON_REQ + _VOW_UNSTR
    + "|"
        + _HIA_STR
    + ")" + _CON_OPT + "$",
    re.IGNORECASE | re.VERBOSE
)
_EXCEPTIONS_2SYLL = frozenset((
    "baseball", "bébé", "best man", "bordeaux", "bouquet", "boutique",
    "boyfriend", "business",
    "clearing", "coupé", "cowboy", "crème fraîche", "crêpe", "csárdás",
    "deadline", "dealer", "drive-in", "duchesse", "duo",
    "fan club", "folklore", "fondue", "freestyle",
    "go-go", "gruyère",
    "hardware", "hereford", "hi-hat", "high tech", "hi-tec", "hi-tech",
    "hot dog",
    "jacquard", "jet lag", "jet set", "joystick", "jukebox",
    "knock-out", "know-how", "kung-fu",
    "layout", "leasing", "loafer", "lotion",
    "madame", "mainstream", "make-up", "mangrove", "maya", "milk shake",
    "moiré",
    "non-food",
    "petanque", "pick-up", "playback", "playboy", "playoff", "poplore",
    "quenelle",
    "ragoût", "ragtime", "reggae", "roll-on", "rosé",
    "skinhead", "soft ice", "software", "speedway", "striptease",
    "tax-free", "trenchcoat",
    "vaudeville",
    "ångström",
))

# trisyllabic words: (C)VCVCV(C), (C)VCV'V(C), (C)V'VCV(C)
# examples: "epeli", "alue", "ioni", "liu'uttaa"
# note: "hioa" is handled as an exception
_REGEX_3SYLL = re.compile(
    "^" + _CON_OPT + "("
        + _VOW_STR + _CON_REQ + _VOW_UNSTR + _CON_REQ + _VOW_UNSTR
    + "|"
        + _VOW_STR + _CON_REQ + _HIA_UNSTR
    + "|"
        + _HIA_STR + _CON_REQ + _VOW_UNSTR
    + ")" + _CON_OPT + "$",
    re.IGNORECASE | re.VERBOSE
)
_EXCEPTIONS_3SYLL = frozenset((
    "aerobic", "à la carte",
    "beauty box", "becquerel", "bouillabaisse", "brasserie",
    "CD-ROM", "cha-cha-cha", "charlotte russe", "cheerleader", "chippendale",
    "cum laude", "entrecôte", "force majeure", "ginger ale",
    "hioa",  # a native word
    "jam session",
    "ladylike",
    "non-iron", "non-woven",
    "open house",
    "passepartout", "port salut", "poste restante",
    "ratatouille", "rock and roll", "royalty",
    "self-made man",
    "treasury",
    "vinaigrette",
))

def count_syllables(word, useExceptions=True):
    """Count the number of syllables in a Finnish word.
    word:          the word
    useExceptions: use True except for testing purposes
    return:        the number of syllables (1-4; 4 means 4 or more syllables
                   or an unknown word)"""

    if useExceptions:
        if word in _EXCEPTIONS_1SYLL:
            return 1
        if word in _EXCEPTIONS_2SYLL:
            return 2
        if word in _EXCEPTIONS_3SYLL:
            return 3

    word = word.strip("-")

    if _REGEX_1SYLL.search(word) is not None:
        return 1
    if _REGEX_2SYLL.search(word) is not None:
        return 2
    if _REGEX_3SYLL.search(word) is not None:
        return 3
    return 4

def _get_redundant_exceptions():
    # generate words that are unnecessarily on the exceptions list
    for excList in (_EXCEPTIONS_1SYLL, _EXCEPTIONS_2SYLL, _EXCEPTIONS_3SYLL):
        for word in excList:
            syllCnt = count_syllables(word, False)
            if syllCnt == 1 and word in _EXCEPTIONS_1SYLL \
            or syllCnt == 2 and word in _EXCEPTIONS_2SYLL \
            or syllCnt == 3 and word in _EXCEPTIONS_3SYLL:
                yield word

def main():
    for word in _get_redundant_exceptions():
        if re.search("[ao]y", word) is None:
            print(f"Redundant exception: '{word}'", file=sys.stderr)

    if len(sys.argv) != 2:
        sys.exit(
            "Count the number of syllables in a Finnish word. Argument: word"
        )

    syllCnt = count_syllables(sys.argv[1])
    print(
        f"Syllables: {syllCnt}"
        + (" or more, or the word is unknown" if syllCnt == 4 else "")
    )

if __name__ == "__main__":
    main()
