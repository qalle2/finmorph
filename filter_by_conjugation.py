"""Read input from 'extract_words.py' from stdin, print lines that contain specified
declensions/conjugations."""

import sys

HELP_TEXT = """Read input from 'extract_words.py' from stdin, print lines that contain specified
declensions/conjugations.
Command line arguments: first and last declension/conjugation to extract; e.g.:
    1  49 (nouns)
    52 78 (verbs)"""

# parse arguments
if len(sys.argv) != 3:
    sys.exit(HELP_TEXT)
try:
    conjugationsToExtract = [int(a, 10) for a in sys.argv[1:3]]
except ValueError:
    sys.exit("Invalid integer in arguments.")
conjugationsToExtract = range(conjugationsToExtract[0], conjugationsToExtract[1] + 1)

for line in sys.stdin:
    if line.count(";") != 1:
        sys.exit("Every line must contain exactly one semicolon.")
    (word, conjugations) = line.rstrip().split(";")
    conjugations = {int(c, 10) for c in conjugations.split(",")}
    conjugations = {c for c in conjugations if c in conjugationsToExtract}
    if conjugations:
        print(word + ";" + ",".join(str(c) for c in sorted(conjugations)))
