import itertools, sys
import util

if len(sys.argv) != 3:
    sys.exit(
        "Print words that only occur as non-final parts of compounds (not final or alone). "
        "Arguments: wordCsvFile compoundListFile"
    )

(wordCsvFile, compoundListFile) = sys.argv[1:]

# read all non-finals
nonFinals = set(itertools.chain.from_iterable(
    tuple(p.strip("'- ") for p in l.split("_")[:-1])
    for l in util.read_lines(compoundListFile)
))
# delete those that occur as finals or alone
nonFinals.difference_update(
    w.split(",")[0] for w in util.read_lines(wordCsvFile)
)
for word in nonFinals:
    print(word)
