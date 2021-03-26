"""Read Kotus XML data from stdin, print words in CSV format."""

import re
import sys

HELP_TEXT = """Read Kotus XML data from stdin, print words in CSV format (word, semicolon,
declensions/conjugations separated by commas). Merge identical words (assuming they're on
successive lines)."""

# regular expression for a line in Kotus XML file: word and one/two declensions/conjugations;
# note: the first "*" must be non-greedy ("*?")
LINE_REGEX = re.compile(
    r"<s>([^<]+)</s> .*? >([0-9]+)</tn> ( .* >([0-9]+)</tn> )?", re.VERBOSE
)

conjugations = set()  # declensions/conjugations of one word
prevWord = None  # previous word

for line in sys.stdin:
    match = LINE_REGEX.search(line)
    if match is not None:
        word = match.group(1)
        if prevWord is None:
            # start the first word
            prevWord = word
        elif word != prevWord:
            # print the previous word and start a new one
            print(prevWord + ";" + ",".join(str(c) for c in sorted(conjugations)))
            conjugations.clear()
            prevWord = word
        # collect declensions/conjugations from successive identical words
        conjugations.update(int(c) for c in (match.group(2), match.group(4)) if c is not None)

if prevWord is not None:
    # print the last word
    print(prevWord + ";" + ",".join(str(c) for c in sorted(conjugations)))
