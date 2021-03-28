"""Read input from 'extract_words.py' from stdin. Print lines with a mono- or disyllabic word."""

import re
import sys

HELP_TEXT = """Read input from 'extract_words.py' from stdin. Print lines with a mono- or
disyllabic word."""

# regular expression for a monosyllabic or disyllabic Finnish word
# vowels/diphthongs: single/double a/e/i/o/u/y/ä/ö; a/e/i/o/u + i/u, e/i/y/ä/ö + i/y, ie, uo, yö
# note: a word can't contain both ä/ö and a/o/u
REGEX_MONO_OR_DI = re.compile(
    r"^"
    # zero or more consonants
    r"[bcdfghjklmnpqrsštvwxzž]*"
    #
    r"("
    # vowel, consonant, vowel (vowels may be short/long/diphthong; consonant may be apostrophe)
    r"  ([eiaou][iu]?|ee|ie|aa|oo|uo|yy?) [bcdfghjklmnpqrsštvwxzž']+ ([eiaou][iu]?|aa|ee|oo)"
    r"| ([eiäöy][iy]?|ee|ie|ää|öö|yö)     [bcdfghjklmnpqrsštvwxzž']+ ([eiäöy][iy]?|ee|ää|öö)"
    # one vowel
    r"| [aeiouyäö]"
    # two vowels (in one or two syllables)
    r"| [eiaouy] [eiaou]"
    r"| [eiäöy]  [eiäöy]"
    # three vowels in two syllables
    r"| ([eiaou][iu]|ee|ii|ie|aa|oo|uu|yy|uo) [eiaou]"
    r"| ([eiyäö][iy]|ee|ii|ie|ää|öö|yy|yö)    [eiyäö]"
    r"| [eiaouy] ([eiaou][iu]|ee|aa|oo)"
    r"| [eiyäö]  ([eiyäö][iy]|ee|ää|öö)"
    # four vowels in two syllables
    r"| (ei|ii|uu)(au|oi|oo|uu)"
    r")"
    #
    # zero or more consonants
    r"[bcdfghjklmnpqrsštvwxzž]*"
    r"$",
    re.IGNORECASE | re.VERBOSE
)

# print lines from stdin in which the part before semicolon matches the regex
for line in sys.stdin:
    if line.count(";") != 1:
        sys.exit("Every input line must contain exactly one semicolon.")
    if REGEX_MONO_OR_DI.search(line.split(";")[0]) is not None:
        print(line.rstrip())
