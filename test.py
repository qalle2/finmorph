"""Test noundecl.py or verbconj.py using a list of words created with extract_words.sh."""

import sys

def format_list(list_):
    return "/".join(str(item) for item in sorted(list_))

# validate argument count
if len(sys.argv) != 2:
    sys.exit("Test noundecl.py (argument 'n') or verbconj.py (argument 'v').")

# import module to test
if sys.argv[1] == "n":
    from noundecl import get_declensions as detect_conjugation
    filename = "nouns.csv"
elif sys.argv[1] == "v":
    from verbconj import get_conjugations as detect_conjugation
    filename = "verbs.csv"
else:
    sys.exit("Invalid command line argument.")

wordCount = errorCount = 0

with open(filename, "rt", encoding="utf8") as handle:
    handle.seek(0)
    for line in handle:
        # parse line to get word and correct declensions/conjugations
        (word, conjugations) = line.rstrip().split(";")
        conjugations = {int(c) for c in conjugations.split(",")}
        # also detect declensions/conjugations using module
        detectedConjugations = detect_conjugation(word)
        # print error/warning
        if detectedConjugations != conjugations:
            print(
                f"'{word}': expected declension(s)/conjugation(s) {format_list(conjugations)}, "
                f"got {format_list(detectedConjugations)}",
                file=sys.stderr
            )
            errorCount += 1
        wordCount += 1

print(f"Words: {wordCount}, errors: {errorCount}")
