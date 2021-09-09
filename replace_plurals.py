import sys
import util

if len(sys.argv) != 3:
    sys.exit(
        "Arguments: CSV file with words and declensions/conjugations, CSV file with plurals and "
        "singulars. Print words and declensions/conjugations in CSV format, with plurals replaced "
        "with singulars."
    )

# get singular forms by plural forms
singularsByPlural = {}  # e.g. {"häät": "hää", ...}
for line in util.read_lines(sys.argv[2]):
    fields = line.split(",")
    assert len(fields) == 2 and not fields[1].isnumeric()
    singularsByPlural[fields[0]] = fields[1]

# read words and declensions/conjugations; replace plurals with singulars
conjugationsByWord = {}  # e.g. {"hää": {18}, ...}
for line in util.read_lines(sys.argv[1]):
    fields = line.split(",")
    word = singularsByPlural.get(fields[0], fields[0])
    conjugations = {int(c, 10) for c in fields[1:]}
    conjugationsByWord.setdefault(word, set()).update(conjugations)

# print results
for word in sorted(conjugationsByWord):
    print(",".join([word] + [str(c) for c in sorted(conjugationsByWord[word])]))
