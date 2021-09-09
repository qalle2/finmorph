import sys
import util

if len(sys.argv) != 4:
    sys.exit(
        "Arguments: CSV file with words and declensions/conjugations, first "
        "declension/conjugation, last declension/conjugation. Print lines that contain "
        "declensions/conjugations within that range."
    )

conjugationsToExtract = [int(c, 10) for c in sys.argv[2:4]]
conjugationsToExtract = set(range(conjugationsToExtract[0], conjugationsToExtract[1] + 1))

for line in util.read_lines(sys.argv[1]):
    fields = line.split(",")
    conjugations = {int(c, 10) for c in fields[1:]} & conjugationsToExtract
    if conjugations:
        print(",".join([fields[0]] + [str(c) for c in sorted(conjugations)]))
