# test splitcomp.py against known single words and compounds

import splitcomp, util

wordCount = errorCount = 0

# test single words
for line in util.read_lines("generated-lists/words.csv"):
    word = line.split(",")[0]
    detectedParts = splitcomp.split_compound(word)
    if len(detectedParts) != 1:
        print("{}: expected {}, got {}".format(
            word, word, "_".join(detectedParts)
        ))
        errorCount += 1
    wordCount += 1

# test compounds
for comp in util.read_lines("compounds.txt"):
    parts = tuple(p.strip("'- ") for p in comp.split("_"))
    origComp = comp.replace("_", "")
    detectedParts = splitcomp.split_compound(origComp)
    if detectedParts != parts:
        print("{}: expected {}, got {}".format(
            origComp, "_".join(parts), "_".join(detectedParts)
        ))
        errorCount += 1
    wordCount += 1

print(f"Words: {wordCount}, errors: {errorCount}")
