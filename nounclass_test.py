"""Test nounclass.py. Read Kotus XML file from stdin."""

import re
import sys
import nounclass

RE_TWO_CLASSES = re.compile(
    r"<s>([^<]+)</s>"
    r".*>([0-9]+)</tn>"
    r".*>([0-9]+)</tn>"
)

RE_ONE_CLASS = re.compile(
    r"<s>([^<]+)</s>"
    r".*>([0-9]+)</tn>"
)

def get_words():
    """Generate (word, (conjugation1, ...)) from stdin."""

    for line in sys.stdin:
        match = RE_TWO_CLASSES.search(line)
        if match is not None:
            conjugations = (int(g) for g in match.group(2, 3))
            yield (match.group(1), tuple(sorted(conjugations)))
        else:
            match = RE_ONE_CLASS.search(line)
            if match is not None:
                conjugation = int(match.group(2))
                yield (match.group(1), (conjugation,))

def main():
    nounCount = 0
    errorCount = 0

    for (word, conjus) in get_words():
        if 1 <= conjus[0] <= 49 and word == word.lower():
            conjus = tuple(c for c in conjus if 1 <= c <= 49)
            detectedConjus = nounclass.get_noun_class(word)
            conjusStr = "/".join(str(c) for c in conjus)
            detectedConjusStr = "/".join(str(c) for c in detectedConjus)

            if not all(c in detectedConjus for c in conjus):
                print(
                    f"Error: '{word}': expected declension {conjusStr}, got {detectedConjusStr}",
                    file=sys.stderr
                )
                errorCount += 1
            elif len(conjus) < len(detectedConjus):
                print(f"Note: '{word}': expected {conjusStr}, got {detectedConjusStr}")

            nounCount += 1

    print(f"Nouns checked: {nounCount}, errors: {errorCount}")
    print("Inspect the notes above to see if incorrect declensions were returned too.")

if __name__ == "__main__":
    main()
