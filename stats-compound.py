import collections, sys

INTRO = """\
Compound counts by number of parts and number of letters.
This file was generated automatically.

            2part 3part 4part 5part Total
            ----- ----- ----- ----- -----"""

def read_lines(filename):
    with open(filename, "rt", encoding="utf8") as handle:
        handle.seek(0)
        yield from (l.rstrip("\n") for l in handle)

def main():
    if len(sys.argv) != 2:
        sys.exit(
            "Print a table of compound counts by number of parts and number "
            "of letters. Argument: compoundListFile"
        )
    filename = sys.argv[1]

    compounds = {
        tuple(p.strip("'- ") for p in c.split("_"))
        for c in read_lines(filename)
    }

    twoPartCompsByLen = collections.Counter()
    threePartCompsByLen = collections.Counter()
    fourPartCompsByLen = collections.Counter()
    fivePartCompsByLen = collections.Counter()
    compsByLen = collections.Counter()

    counters = (
        twoPartCompsByLen, threePartCompsByLen, fourPartCompsByLen,
        fivePartCompsByLen, compsByLen
    )

    for (i, counter) in enumerate(counters):
        counter.update(
            sum(len(p) for p in c) for c in compounds
            if i == 4 or len(c) == i + 2
        )

    print(INTRO)
    for length in sorted(compsByLen):
        print(
            f"{length:2} letters: "
            + " ".join(f"{c[length]:5}" for c in counters)
        )
    print("     TOTAL: " + " ".join(f"{sum(c.values()):5}" for c in counters))

main()
