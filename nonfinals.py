import itertools, sys

def read_lines(filename):
    with open(filename, "rt", encoding="utf8") as handle:
        handle.seek(0)
        yield from (l.rstrip("\n") for l in handle)

def main():
    if len(sys.argv) != 2:
        sys.exit(
            "Print words that only occur as non-final parts of compounds (not "
            "final). Argument: compoundLisFile"
        )
    filename = sys.argv[1]

    # read compounds as tuples
    compounds = {
        tuple(p.strip("'- ") for p in l.split("_"))
        for l in read_lines(sys.argv[1])
    }

    # get non-final parts
    nonFinals = set(itertools.chain.from_iterable(c[:-1] for c in compounds))
    # delete parts that also occur as finals
    nonFinals.difference_update(c[-1] for c in compounds)

    for word in nonFinals:
        print(word)

main()
