import sys

def read_lines(filename):
    with open(filename, "rt", encoding="utf8") as handle:
        handle.seek(0)
        yield from (l.rstrip("\n") for l in handle)

def main():
    if len(sys.argv) != 3:
        sys.exit(
            "Arguments: CSV file with words and declensions/conjugations, "
            "list file with compounds. Print CSV lines without those that "
            "contain a compound."
        )
    (wordFile, compoundFile) = sys.argv[1:]

    compounds = {l.replace("_", "") for l in read_lines(compoundFile)}

    for line in read_lines(wordFile):
        if line.split(",")[0] not in compounds:
            print(line)

main()
