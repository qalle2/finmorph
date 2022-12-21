import sys

def read_lines(filename):
    with open(filename, "rt", encoding="utf8") as handle:
        handle.seek(0)
        yield from (l.rstrip("\n") for l in handle)

def main():
    if len(sys.argv) != 3:
        sys.exit(
            "Get words that occur as finals of compounds. Print them and "
            "their declensions/conjugations in CSV format. Arguments: "
            "wordCsvFile compoundListFile"
        )
    (wordFile, compoundFile) = sys.argv[1:]

    # get the final part for each compound
    compoundToFinal = {}  # e.g. {"putkiyhde": "yhde", ...}
    for word in read_lines(compoundFile):
        compoundToFinal[word.replace("_", "")] \
        = word.split("_")[-1].strip("'- ")

    # get conjugations for finals
    conjsByFinal = {}  # e.g. {"yhde": {48}, ...}
    for line in read_lines(wordFile):
        fields = line.split(",")
        word = fields[0]
        if word in compoundToFinal:
            final = compoundToFinal[word]
            conjs = {int(c) for c in fields[1:]} - {50, 51}
            conjsByFinal.setdefault(final, set()).update(conjs)

    for final in sorted(conjsByFinal):
        print(",".join(
            [final] + [str(c) for c in sorted(conjsByFinal.get(final, {}))]
        ))

main()
