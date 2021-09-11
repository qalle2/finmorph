import collections, sys
import util

INTRO = """\
Compound counts by number of parts and number of letters.
This file was generated automatically.

            2part 3part 4part 5part Total
            ----- ----- ----- ----- -----"""

if len(sys.argv) != 2:
    sys.exit(
        "Print a table of compound counts by number of parts and number of letters. Argument: "
        "compound list file."
    )

compounds = {tuple(p.strip("'- ") for p in c.split("_")) for c in util.read_lines(sys.argv[1])}

twoPartCompsByLen = collections.Counter()
threePartCompsByLen = collections.Counter()
fourPartCompsByLen = collections.Counter()
fivePartCompsByLen = collections.Counter()
compsByLen = collections.Counter()

counters = (
    twoPartCompsByLen, threePartCompsByLen, fourPartCompsByLen, fivePartCompsByLen, compsByLen
)

for (i, counter) in enumerate(counters):
    counter.update(sum(len(p) for p in c) for c in compounds if i == 4 or len(c) == i + 2)

print(INTRO)
for length in sorted(compsByLen):
    print(f"{length:2} letters: " + " ".join(f"{c[length]:5}" for c in counters))
print("     TOTAL: " + " ".join(f"{sum(c.values()):5}" for c in counters))
