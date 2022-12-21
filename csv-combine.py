import sys

def read_lines(filename):
    with open(filename, "rt", encoding="utf8") as handle:
        handle.seek(0)
        yield from (l.rstrip("\n") for l in handle)

def main():
    if len(sys.argv) < 2:
        sys.exit(
            "Arguments: one or more CSV files. For each distinct word, print "
            "a CSV line with all declensions/conjugations occurring with that "
            "word in the files."
        )
    filenames = sys.argv[1:]

    conjugationsByWord = {}  # {word: set of conjugations, ...}

    for filename in filenames:
        for line in read_lines(filename):
            fields = line.split(",")
            word = fields[0]
            conjugations = {int(v) for v in fields[1:]}
            conjugationsByWord.setdefault(word, set()).update(conjugations)

    for word in sorted(conjugationsByWord):
        print(",".join(
            [word] + [str(c) for c in sorted(conjugationsByWord[word])]
        ))

main()
