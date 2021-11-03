import itertools, sys
import util

if len(sys.argv) != 3:
    sys.exit(
        "Print words that only occur as non-final parts of compounds (not final or alone). "
        "Arguments: compound list file, word CSV file"
    )

# get compounds as tuples
compounds = {tuple(p.strip("'- ") for p in l.split("_")) for l in util.read_lines(sys.argv[1])}

# get non-final parts of compounds (not final or those that occur alone)
compositives = set(itertools.chain.from_iterable(c[:-1] for c in compounds))
compositives.difference_update(c[-1] for c in compounds)
compositives.difference_update(l.split(",")[0] for l in util.read_lines(sys.argv[2]))

for word in compositives:
    print(word)
