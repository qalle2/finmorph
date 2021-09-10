import itertools, sys
import util

if len(sys.argv) != 2:
    sys.exit(
        "Print words that only occur as non-final parts of compounds (not final). Argument: "
        "compound list file"
    )

# read compounds as tuples
compounds = {tuple(p.strip("'- ") for p in l.split("_")) for l in util.read_lines(sys.argv[1])}
# get non-finals
nonFinals = set(itertools.chain.from_iterable(c[:-1] for c in compounds))
# delete finals
nonFinals.difference_update(c[-1] for c in compounds)
for word in nonFinals:
    print(word)
