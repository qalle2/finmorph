import sys
import util

# validate argument count
if len(sys.argv) != 2:
    sys.exit("Argument: which program to test ('n'=noundecl.py, 'v'=verbconj.py).")

if sys.argv[1] == "n":
    from noundecl import get_declensions as detect_conjugation
    inputFile = "generated-lists/nouns.csv"
elif sys.argv[1] == "v":
    from verbconj import get_conjugations as detect_conjugation
    inputFile = "generated-lists/verbs.csv"
else:
    sys.exit("Invalid argument.")

wordCount = errorCount = 0

for line in util.read_lines(inputFile):
    fields = line.split(",")
    assert len(fields) >= 2
    word = fields[0]
    conjugations = {int(c, 10) for c in fields[1:]}
    # merge conjugation 68 ("tupakoida") to 62 ("voida")
    if 68 in conjugations:
        conjugations.remove(68)
        conjugations.add(62)
    # merge conjugation 74 ("katketa") to 75 ("selvitä")
    if 74 in conjugations:
        conjugations.remove(74)
        conjugations.add(75)

    detectedConjugations = detect_conjugation(word)
    if detectedConjugations != conjugations:
        print(
            f"'{word}': expected declension(s)/conjugation(s) "
            + "/".join(str(c) for c in sorted(conjugations))
            + ", got "
            + "/".join(str(c) for c in sorted(detectedConjugations))
        )
        errorCount += 1
    wordCount += 1

print(f"Words: {wordCount}, errors: {errorCount}")
