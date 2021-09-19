"""Count the number of syllables in a Finnish word."""

import re, sys

# syllable counts for some words; reasons:
#   - I like to keep foreign vowel letters ("àáâåèéêîôû") out of the rules
#   - I like to keep foreign diphthongs (e.g. "ay") out of the rules
#   - some words have fewer pronounced than written syllables (e.g. "house")
#   - punctuation (excl. "'")
#   - acronym
_EXCEPTIONS = {
    "aerobic": 3,
    "à la carte": 3,
    "baseball": 2,
    "beauty box": 3,
    "bébé": 2,
    "becquerel": 3,
    "best man": 2,
    "bordeaux": 2,
    "bouillabaisse": 3,
    "bouquet": 2,
    "boutique": 2,
    "boyfriend": 2,
    "brasserie": 3,
    "bridge": 1,
    "business": 2,
    "byte": 1,
    "CD-ROM": 3,
    "cha-cha-cha": 3,
    "charlotte russe": 3,
    "cheerleader": 3,
    "chippendale": 3,
    "clearing": 2,
    "coupé": 2,
    "cowboy": 2,
    "crème fraîche": 2,
    "crêpe": 2,
    "csárdás": 2,
    "cum laude": 3,
    "deadline": 2,
    "dealer": 2,
    "drive-in": 2,
    "duchesse": 2,
    "duo": 2,
    "entrecôte": 3,
    "fan club": 2,
    "folklore": 2,
    "fondue": 2,
    "force majeure": 3,
    "freestyle": 2,
    "gay": 1,
    "ginger ale": 3,
    "go-go": 2,
    "grape": 1,
    "gray": 1,
    "gruyère": 2,
    "hardware": 2,
    "hereford": 2,
    "hi-hat": 2,
    "hioa": 3,  # I won't make the trisyllabic word regex more complex just because of this
    "high tech": 2,
    "hi-tec": 2,
    "hi-tech": 2,
    "hot dog": 2,
    "house": 1,
    "jacquard": 2,
    "jam session": 3,
    "jet lag": 2,
    "jet set": 2,
    "jive": 1,
    "joystick": 2,
    "jukebox": 2,
    "knock-out": 2,
    "know-how": 2,
    "kung-fu": 2,
    "ladylike": 3,
    "layout": 2,
    "leasing": 2,
    "loafer": 2,
    "lotion": 2,
    "madame": 2,
    "mainstream": 2,
    "make-up": 2,
    "mangrove": 2,
    "maya": 2,
    "milk shake": 2,
    "moiré": 2,
    "non-food": 2,
    "non-iron": 3,
    "non-woven": 3,
    "open house": 3,
    "passepartout": 3,
    "petanque": 2,
    "pick-up": 2,
    "playback": 2,
    "playboy": 2,
    "playoff": 2,
    "poplore": 2,
    "port salut": 3,
    "poste restante": 3,
    "quenelle": 2,
    "quiche": 1,
    "ragoût": 2,
    "ragtime": 2,
    "ratatouille": 3,
    "rave": 1,
    "reggae": 2,
    "rock and roll": 3,
    "roll-on": 2,
    "rosé": 2,
    "royalty": 3,
    "self-made man": 3,
    "skinhead": 2,
    "soft ice": 2,
    "software": 2,
    "speedway": 2,
    "spray": 1,
    "squash": 1,
    "striptease": 2,
    "tax-free": 2,
    "trance": 1,
    "treasury": 3,
    "trenchcoat": 2,
    "vaudeville": 2,
    "vinaigrette": 3,
    "ångström": 2,
}

# regex for monosyllabic words, e.g. "yö", "snacks"
# (C)V(C)
_RE_1SYLL = re.compile(
    r"""^
    [b-df-hj-np-tv-xzšž]*
    ( [aeiou][iu]? | [äeiöy][iy]? | aa | ää | ee | oo | öö | ie | uo | yö )
    [b-df-hj-np-tv-xzšž]*
    $""",
    re.IGNORECASE | re.VERBOSE
)

# regex for disyllabic words, e.g. "aie", "äes", "stretching"
# (C)VCV(C) or (C)V'V(C)
_RE_2SYLL = re.compile(
    r"""^
    [b-df-hj-np-tv-xzšž]*
    (
        ( [aeiou][iu]? | [äeiöy][iy]? | aa | ää | ee | oo | öö | ie | uo | yö )
        [b-df-hj-np-tv-xzšž]+
        ( [aeiou][iu]? | [äeiöy][iy]? | aa | ää | ee | oo | öö )
        |
        (
            [äeioöuy]a
            | [aeioöuy]ä
            | [aäoöuy]e
            | [aäeiöy]o
            | [aäeiou]ö
            | [aeiouyäö]{3,4}
        )
    )
    [b-df-hj-np-tv-xzšž]*
    $""",
    re.IGNORECASE | re.VERBOSE
)

# regex for trisyllabic words, e.g. "alue", "ioni", "liu'uttaa"
# (C)VCVCV(C), (C)VCV'V(C) or (C)V'VCV(C)
# note: "hioa" is handled as an exception
_RE_3SYLL = re.compile(
    r"""^
    [b-df-hj-np-tv-xzšž]*
    (
        ( [aeiou][iu]? | [äeiöy][iy]? | aa | ää | ee | oo | öö | ie | uo | yö )
        [b-df-hj-np-tv-xzšž]+
        (
            ( [aeiou][iu]? | [äeiöy][iy]? | aa | ää | ee | oo | öö )
            [b-df-hj-np-tv-xzšž]+
            ( [aeiou][iu]? | [äeiöy][iy]? | aa | ää | ee | oo | öö )
            |
            (
                | [äeioöuy]a
                | [aeioöuy]ä
                | [aäioöuy]e
                | [aäeiöuy]o
                | [aäeiouy]ö
                | [aeiouyäö]{3,4}
            )
        )
        |
        (
            [äeioöuy]a
            | [aeioöuy]ä
            | [aäoöuy]e
            | [aäeiöy]o
            | [aäeiou]ö
            | [aeiouyäö]{3,4}
            | [aeiou](a'a|i'i|u'u)
        )
        [b-df-hj-np-tv-xzšž]+
        ( [aeiou][iu]? | [äeiöy][iy]? | aa | ää | ee | oo | öö )
    )
    [b-df-hj-np-tv-xzšž]*
    $""",
    re.IGNORECASE | re.VERBOSE
)

def count_syllables(word, useExceptions=True):
    """word: a Finnish word
    return: number of syllables (1-4; note: 4 = 4 or more syllables or an unknown word)"""

    if useExceptions:
        try:
            return _EXCEPTIONS[word]
        except KeyError:
            pass

    word = word.strip("-")
    for (i, regex) in enumerate((_RE_1SYLL, _RE_2SYLL, _RE_3SYLL)):
        if regex.search(word) is not None:
            return i + 1
    return 4

def _check_redundant_exceptions():
    for word in _EXCEPTIONS:
        if count_syllables(word, False) == _EXCEPTIONS[word]:
            print(f'Redundant exception: "{word}"')

def main():
    #_check_redundant_exceptions()

    if len(sys.argv) != 2:
        sys.exit("Count the number of syllables in a Finnish word. Argument: word")

    syllCnt = count_syllables(sys.argv[1])
    print(f"Syllables: {syllCnt}" + (" or more, or the word is unknown" if syllCnt == 4 else ""))

if __name__ == "__main__":
    main()
