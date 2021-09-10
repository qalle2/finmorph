import sys
import splitcomp, util

# validate argument count
if len(sys.argv) != 2:
    sys.exit(
        "Test splitcomp.py. Argument: number of individual words per compound (0-5; 0=any). "
        "splitcomp.py will be tested against known single words and compounds with that many "
        "individual words."
    )

try:
    partCount = int(sys.argv[1], 10)
    if not 0 <= partCount <= 5:
        raise ValueError
except ValueError:
    sys.exit("Invalid argument.")

wordCount = errorCount = 0

if partCount <= 1:
    # test single words
    for line in util.read_lines("generated-lists/words.csv"):
        word = line.split(",")[0]
        detectedParts = splitcomp.split_compound(word)
        if len(detectedParts) != 1:
            print(f'"{word}": expected "{word}", got "{"_".join(detectedParts)}"')
            errorCount += 1
        wordCount += 1

if partCount != 1:
    # test compounds
    for comp in util.read_lines("compounds.txt"):
        parts = tuple(p.strip("'- ") for p in comp.split("_"))
        if partCount == 0 or len(parts) == partCount:
            origComp = comp.replace("_", "")
            detectedParts = splitcomp.split_compound(origComp)
            if detectedParts != parts:
                print(
                    f'"{origComp}": expected "{"_".join(parts)}", got "{"_".join(detectedParts)}"'
                )
                errorCount += 1
            wordCount += 1

print(f"Words: {wordCount}, errors: {errorCount}")
