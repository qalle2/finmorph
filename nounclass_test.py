"""Test nounclass.py. Read Kotus XML file from stdin."""

import re
import sys
import nounclass

# a noun with (at least) one declension 0...49
RE_ONE_DECLENSION = re.compile(
    r"<s>([^<]+)</s>"
    r".*>([1-4]?[0-9])</tn>"
)

# a noun with two declensions 0...49
RE_TWO_DECLENSIONS = re.compile(
    r"<s>([^<]+)</s>"
    r".*>([1-4]?[0-9])</tn>"
    r".*>([1-4]?[0-9])</tn>"
)

def get_nouns():
    """Generate (word, {declension1, ...}) from stdin."""

    for line in sys.stdin:
        match1 = RE_ONE_DECLENSION.search(line)
        if match1 is not None:
            match2 = RE_TWO_DECLENSIONS.search(line)
            if match2 is not None:
                yield (match2.group(1), {int(g) for g in match2.group(2, 3)})
            else:
                yield (match1.group(1), {int(match1.group(2))})

def main():
    nounCount = errorCount = 0

    for (word, correctDeclensions) in get_nouns():
        detectedDeclensions = nounclass.get_declensions(word)
        correctDeclStr  = "/".join(str(c) for c in sorted(correctDeclensions))
        detectedDeclStr = "/".join(str(c) for c in sorted(detectedDeclensions))

        if not correctDeclensions.issubset(detectedDeclensions):
            print(
                f"Error: '{word}': expected declension {correctDeclStr}, got {detectedDeclStr}",
                file=sys.stderr
            )
            errorCount += 1
        elif len(correctDeclensions) < len(detectedDeclensions):
            print(f"Note: '{word}': expected {correctDeclStr:>2}, got {detectedDeclStr}")

        nounCount += 1

    print(f"Nouns checked: {nounCount}, errors: {errorCount}")
    print("Inspect the notes above to see if incorrect declensions were returned too.")

if __name__ == "__main__":
    main()
