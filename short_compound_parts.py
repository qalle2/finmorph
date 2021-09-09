# print distinct short parts in "compounds.txt" and one word they occur in

import itertools
import util

# read compounds as a list of tuples
compounds = [tuple(p.strip("'- ") for p in l.split("_")) for l in util.read_lines("compounds.txt")]

# get short distinct parts, sort case-insensitively
shortParts = sorted(set(p for p in itertools.chain.from_iterable(compounds) if len(p) <= 3))
shortParts.sort(key=lambda p: p.lower())

# print each short part and the first compound it occurs in
for part in shortParts:
    for comp in compounds:
        if part in comp:
            print(f"{part:3}: " + "_".join(comp))
            break
