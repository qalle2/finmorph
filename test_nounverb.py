import sys
import util

if len(sys.argv) != 2:
    sys.exit(
        "Argument: which program to test ('n'=noundecl.py, 'v'=verbconj.py, "
        "'nc'=noun_consgrad.py, 'vc'=verb_consgrad.py)."
    )

# get declension/conjugation function and list of words to test
if sys.argv[1] in ("n", "nc"):
    from noundecl import get_declensions as detect_conjugation
    testFile = "generated-lists/nouns.csv"
elif sys.argv[1] in ("v", "vc"):
    from verbconj import get_conjugations as detect_conjugation
    testFile = "generated-lists/verbs.csv"
else:
    sys.exit("Invalid argument.")

# get consonant gradation detection function and list of words to which
# consonant gradation applies
if sys.argv[1] == "nc":
    from noun_consgrad import get_consonant_gradation as detect_gradation
    consGradFile = "generated-lists/words-consgrad.csv"
elif sys.argv[1] == "vc":
    from verb_consgrad import get_consonant_gradation as detect_gradation
    consGradFile = "generated-lists/words-consgrad.csv"
else:
    consGradFile = None

if consGradFile is not None:
    # get combinations of word and conjugation to which consonant gradation
    # applies; e.g. consGradConjugationsByWord["sika"] = {9}
    consGradConjugationsByWord = {}
    for line in util.read_lines(consGradFile):
        fields = line.split(",")
        assert len(fields) >= 2
        consGradConjugationsByWord[fields[0]] \
        = {int(c, 10) for c in fields[1:]}

    # these are errors in the source data; fix them here for now
    consGradConjugationsByWord["alpi"].remove(5)
    consGradConjugationsByWord["auer"] = {49}
    consGradConjugationsByWord["helpi"].remove(5)
    consGradConjugationsByWord["hynte"] = {48}
    consGradConjugationsByWord["näin"] = {33}
    consGradConjugationsByWord["pue"] = {48}
    consGradConjugationsByWord["ryntys"] = {41}
    consGradConjugationsByWord["siitake"].remove(8)

wordCount = errorCount = 0

for line in util.read_lines(testFile):
    # get word and correct declensions/conjugations
    fields = line.split(",")
    assert len(fields) >= 2
    word = fields[0]
    conjugations = set(int(c, 10) for c in fields[1:])
    if word == "tuomas":
        conjugations.add(39)  # error in source data as well
    conjugations = tuple(sorted(conjugations))

    if sys.argv[1] in ("n", "v"):
        # test declension/conjugation detection function
        detectedConjugations = detect_conjugation(word)
        if detectedConjugations != conjugations:
            print(
                f"'{word}': expected declension(s)/conjugation(s) "
                + "/".join(str(c) for c in sorted(conjugations))
                + ", got "
                + "/".join(str(c) for c in sorted(detectedConjugations))
            )
            errorCount += 1
    else:
        # mode "nc" or "vc"; test consonant gradation detection function
        for conj in detect_conjugation(word):
            detectedGradation = detect_gradation(word, conj)
            if detectedGradation \
            and conj not in consGradConjugationsByWord.setdefault(word, set()):
                word2 = f"'{word}'"
                print(
                    f"{word2:20} in decl./conj. {conj:2}: "
                    "expected no consonant gradation but got it"
                )
                errorCount += 1
            elif not detectedGradation \
            and conj in consGradConjugationsByWord.setdefault(word, set()):
                word2 = f"'{word}'"
                print(
                    f"{word2:20} in decl./conj. {conj:2}: "
                    "expected consonant gradation but got none"
                )
                errorCount += 1

    wordCount += 1

print(f"Words: {wordCount}, errors: {errorCount}")
