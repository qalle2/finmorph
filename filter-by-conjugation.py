import sys

def read_lines(filename):
    with open(filename, "rt", encoding="utf8") as handle:
        handle.seek(0)
        yield from (l.rstrip("\n") for l in handle)

def main():
    if len(sys.argv) != 4:
        sys.exit(
            "Arguments: CSV file with words and declensions/conjugations, "
            "first declension/conjugation, last declension/conjugation. Print "
            "lines that contain declensions/conjugations within that range."
        )
    filename = sys.argv[1]
    conjsToExtract = [int(c) for c in sys.argv[2:]]
    conjsToExtract = set(range(conjsToExtract[0], conjsToExtract[1] + 1))

    for line in read_lines(filename):
        fields = line.split(",")
        conjs = {int(c) for c in fields[1:]} & conjsToExtract
        if conjs:
            print(",".join([fields[0]] + [str(c) for c in sorted(conjs)]))

main()
