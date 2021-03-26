"""Read Kotus XML data from stdin, print words in CSV format."""

import re
import sys

HELP_TEXT = """Read Kotus XML data from stdin, print words in CSV format (word, semicolon,
declensions/conjugations separated by commas)."""

# regular expression for a line in Kotus XML file: word and one/two declensions/conjugations;
# note: the first "*" must be non-greedy ("*?")
LINE_REGEX = re.compile(
    r"<s>([^<]+)</s> .*? >([0-9]+)</tn> ( .* >([0-9]+)</tn> )?", re.VERBOSE
)

for line in sys.stdin:
    match = LINE_REGEX.search(line)
    if match is not None:
        print(
            match.group(1) + ";"
            + ",".join(c for c in (match.group(2), match.group(4)) if c is not None)
        )
