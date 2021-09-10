# print a table of compound counts by number of parts and number of letters

import collections
import util

compounds = {
    tuple(c.split("_")) for c in util.read_lines("compounds.txt") if " " not in c and "-" not in c
}

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

print("Number of compounds without spaces/hyphens by number of parts and number of letters:")
print()
print("            2part 3part 4part 5part Total")
print("            ----- ----- ----- ----- -----")

for length in sorted(compsByLen):
    print(f"{length:2} letters: " + " ".join(f"{c[length]:5}" for c in counters))

print("     TOTAL: " + " ".join(f"{sum(c.values()):5}" for c in counters))
