"""Read Kotus XML file from stdin, print words in specified declensions/conjugations.
(For creating quick-to-parse test files for nounclass_test.py and verbclass_test.py.)"""

import re
import sys

HELP_TEXT = """Read Kotus XML file from stdin.
Command line arguments: first and last declension/conjugation to extract; e.g.:
    1  49 (nouns)
    52 78 (verbs)
Print lines with:
    word
    semicolon
    declensions/conjugations separated by commas"""

# regular expression for a line in Kotus XML file: word and one/two declensions/conjugations;
# note: the first "*" must be non-greedy ("*?")
LINE_REGEX = re.compile(
    r"<s>([^<]+)</s> .*? >([0-9]+)</tn> ( .* >([0-9]+)</tn> )?", re.VERBOSE
)

# validate argument count
if len(sys.argv) != 3:
    sys.exit(HELP_TEXT)

# parse arguments
try:
    conjugationsToExtract = [int(a, 10) for a in sys.argv[1:3]]
except ValueError:
    sys.exit("Invalid integer in arguments.")
conjugationsToExtract = range(conjugationsToExtract[0], conjugationsToExtract[1] + 1)

# process lines from stdin
for line in sys.stdin:
    match = LINE_REGEX.search(line)
    if match is not None:
        conjugations = {int(c) for c in (match.group(2), match.group(4)) if c is not None}
        conjugations = {c for c in conjugations if c in conjugationsToExtract}
        if conjugations:
            conjugationsStr = ",".join(str(c) for c in sorted(conjugations))
            print(f"{match.group(1)};{conjugationsStr}")
