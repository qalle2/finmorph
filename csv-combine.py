import sys
import util

if len(sys.argv) < 2:
    sys.exit(
        "Arguments: one or more CSV files. For each distinct word, print a "
        "CSV line with all declensions/conjugations occurring with that word "
        "in the files."
    )

conjugationsByWord = {}  # word: set of conjugations

# read files
for file_ in sys.argv[1:]:
    for line in util.read_lines(file_):
        fields = line.split(",")
        word = fields[0]
        conjugations = {int(v, 10) for v in fields[1:]}
        conjugationsByWord.setdefault(word, set()).update(conjugations)

# print results
for word in conjugationsByWord:
    print(",".join(
        [word] + [str(c) for c in sorted(conjugationsByWord[word])]
    ))
