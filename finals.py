import sys
import util

if len(sys.argv) != 3:
    sys.exit(
        "Get words that only occur as finals of compounds. Print them and their "
        "declensions/conjugations in CSV format. Arguments: wordCsvFile compoundListFile"
    )

(csvFile, listFile) = sys.argv[1:]

# map compounds to finals
compoundToFinal = {}  # e.g. {"putkiyhde": "yhde", ...}
for word in util.read_lines(listFile):
    compoundToFinal[word.replace("_", "")] = word.split("_")[-1].strip("'- ")

finalsToKeep = set(compoundToFinal.values())

# get conjugations for finals
conjugationsByFinal = {}  # e.g. {"yhde": {48}, ...}
for line in util.read_lines(csvFile):
    fields = line.split(",")
    word = fields[0]
    conjugations = {int(c, 10) for c in fields[1:]} - {50, 51}

    finalsToKeep.discard(word)

    if word in compoundToFinal:
        final = compoundToFinal[word]
        conjugationsByFinal.setdefault(final, set()).update(conjugations)

for final in sorted(finalsToKeep):
    print(",".join([final] + [str(c) for c in sorted(conjugationsByFinal.get(final, {}))]))
