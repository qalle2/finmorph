"""Read input from 'extract_words.py' from stdin. Print lines with specified number of syllables.
Not designed to catch but may catch some:
    - recent loanwords written as in source language (i.e. words that contain c/q/w/x)
    - compounds"""

import re
import sys

HELP_TEXT = """Read input from 'extract_words.py' from stdin.
Command line argument: number of syllables (1...3)
Print lines with specified number of syllables."""

# regular expressions
# vowel types: back=a/o/u, neutral=e/i, front=ä/ö/y; a word can't have both back&front vowels
REGEX_MONOSYLLABIC = re.compile(
    r"^"
    r"[bdfghjklmnprsštvzž]*"                                # (C)(C)
    r"([eiaou][iu]?|[eiäöy][iy]?|aa|ää|ie|ee|uo|oo|yö|öö)"  # V(V)
    r"[bdfghjklmnprsštvzž]*"                                # (C)(C)
    r"$",
    re.IGNORECASE
)
REGEX_DISYLLABIC = re.compile(
    r"^"
    r"[bdfghjklmnprsštvzž]*"          # (C)(C)
    r"("
    r"([eiaou][iu]?|ie|ee|aa|uo|oo)"  # V(V); back/neutral
    r"[bdfghjklmnprsštvzž']+"         # C(C)/'
    r"([eiaou][iu]?|ee|aa|oo)"        # V(V); back/neutral (no ie/uo)
    r"|"
    r"([eiäöy][iy]?|ie|ee|ää|yö|öö)"  # V(V); front/neutral
    r"[bdfghjklmnprsštvzž']+"         # C(C)/'
    r"([eiäöy][iy]?|ee|ää|öö)"        # V(V); front/neutral (no ie/yö)
    r")"
    r"[bdfghjklmnprsštvzž]*"          # (C)(C)
    r"$",
    re.IGNORECASE
)
REGEX_TRISYLLABIC = re.compile(
    r"^"
    r"[bdfghjklmnprsštvzž]*"          # (C)(C)
    r"("
    r"([eiaou][iu]?|ie|ee|aa|uo|oo)"  # V(V); back/neutral
    r"[bdfghjklmnprsštvzž']+"         # C(C)/'
    r"([eiaou][iu]?|ee|aa|oo)"        # V(V); back/neutral (no ie/uo)
    r"[bdfghjklmnprsštvzž']+"         # C(C)/'
    r"([eiaou][iu]?|ee|aa|oo)"        # V(V); back/neutral (no ie/uo)
    r"|"
    r"([eiäöy][iy]?|ie|ee|ää|yö|öö)"  # V(V); front/neutral
    r"[bdfghjklmnprsštvzž']+"         # C(C)/'
    r"([eiäöy][iy]?|ee|ää|öö)"        # V(V); front/neutral (no ie/yö)
    r"[bdfghjklmnprsštvzž']+"         # C(C)/'
    r"([eiäöy][iy]?|ee|ää|öö)"        # V(V); front/neutral (no ie/yö)
    r")"
    r"[bdfghjklmnprsštvzž]*"          # (C)(C)
    r"$",
    re.IGNORECASE
)

# parse argument
if len(sys.argv) != 2:
    sys.exit(HELP_TEXT)
try:
    syllableCnt = int(sys.argv[1], 10)
    if not 1 <= syllableCnt <= 3:
        raise ValueError
except ValueError:
    sys.exit("Invalid argument.")

if syllableCnt == 1:
    regex = REGEX_MONOSYLLABIC
elif syllableCnt == 2:
    regex = REGEX_DISYLLABIC
else:
    regex = REGEX_TRISYLLABIC

# print lines from stdin in which the part before semicolon matches the regex
for line in sys.stdin:
    if line.count(";") != 1:
        sys.exit("Every input line must contain exactly one semicolon.")
    if regex.search(line[:line.index(";")]) is not None:
        print(line.rstrip())
