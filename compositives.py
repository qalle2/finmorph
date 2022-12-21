import itertools, sys

def read_lines(filename):
    with open(filename, "rt", encoding="utf8") as handle:
        handle.seek(0)
        yield from (l.rstrip("\n") for l in handle)

def main():
    if len(sys.argv) != 3:
        sys.exit(
            "Print words that only occur as non-final parts of compounds (not "
            "final or alone). Arguments: compound list file, word CSV file"
        )
    (compoundFile, wordFile) = sys.argv[1:]

    # get compounds as tuples
    compounds = {
        tuple(p.strip("'- ") for p in l.split("_"))
        for l in read_lines(compoundFile)
    }

    # get non-final parts of compounds
    compositives = set(
        itertools.chain.from_iterable(c[:-1] for c in compounds)
    )
    # delete those that also occur as final parts
    compositives.difference_update(c[-1] for c in compounds)
    # delete those that also occur alone
    compositives.difference_update(
        l.split(",")[0] for l in read_lines(wordFile)
    )

    for word in compositives:
        print(word)

main()
