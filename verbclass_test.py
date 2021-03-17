"""Test verbclass.py. Read Kotus XML file from stdin."""

import re
import sys
import verbclass

TWO_DECLENSIONS_REGEX = re.compile(
    r"<s>([^<]+)</s>"
    r".*>(5[2-9]|6[0-9]|7[0-8])</tn>"
    r".*>(5[2-9]|6[0-9]|7[0-8])</tn>"
)

ONE_DECLENSION_REGEX = re.compile(
    r"<s>([^<]+)</s>"
    r".*>(5[2-9]|6[0-9]|7[0-8])</tn>"
)

def get_words():
    """Generate (word, {conjugation1, ...}) from stdin."""

    for line in sys.stdin:
        match1 = ONE_DECLENSION_REGEX.search(line)
        if match1 is not None:
            match2 = TWO_DECLENSIONS_REGEX.search(line)
            if match2 is not None:
                yield (match2.group(1), set(int(g) for g in match2.group(2, 3)))
            else:
                yield (match1.group(1), {int(match1.group(2))})

def main():
    verbCount = errorCount = 0

    for (word, correctConjugations) in get_words():
        detectedConjugations = verbclass.get_conjugations(word)
        correctConjStr  = "/".join(str(c) for c in correctConjugations)
        detectedConjStr = "/".join(str(c) for c in detectedConjugations)

        if not detectedConjugations.issuperset(correctConjugations):
            print(
                f"ERROR: '{word}': expected conjugation {correctConjStr}, got {detectedConjStr}",
                file=sys.stderr
            )
            errorCount += 1
        elif detectedConjugations != correctConjugations:
            print(
                f"Note: '{word}': expected conjugation {correctConjStr}, got {detectedConjStr}",
                file=sys.stderr
            )

        verbCount += 1

    print(f"Verbs checked: {verbCount}, errors: {errorCount}")

if __name__ == "__main__":
    main()
