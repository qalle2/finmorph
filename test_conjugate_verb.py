"""Test conjugate_verb.py by comparing the output to test files."""

import os, sys
from conjugate_verb import conjugate_verb

_TEST_DIR = "conjugate_verb-tests"  # read test files from here

# verb forms to test
FORMS = (
    # mood, tense, voice, number/None, person/None
    ("ind", "pre", "act", "sg", "1"),
)

def _read_csv(mood, tense, voice, number, person):
    # Read test cases from CSV file.
    # each line ([] = optional): NomSg,inflected[,inflected...];
    #     inflected forms must be in alphabetical (Unicode) order
    # return: {NomSg: (inflected, ...), ...}

    filename = "-".join((mood, tense, voice, number, person)) + ".csv"
    path = os.path.join(_TEST_DIR, filename)
    verbs = {}

    with open(path, "rt", encoding="utf8") as handle:
        handle.seek(0)
        for line in handle:
            line = line.rstrip("\n")
            if line and not line.startswith("#"):
                items = line.split(",")
                if len(items) < 2 or min(len(i) for i in items) < 2:
                    sys.exit("Invalid CSV line: " + line)
                verbs[items[0]] = tuple(items[1:])
    return verbs

def run_test(mood, tense, voice, number, person):
    # Run a test. Return number of verbs tested.

    #if case == "nom" and number == "sg":
    #    # {NomSg: (NomSg,), ...}
    #    verbs = dict((w, (w,)) for w in _read_csv("gen", "sg"))

    # {NomSg: (inflected, ...), ...}
    verbs = _read_csv(mood, tense, voice, number, person)

    for verb in verbs:
        result = tuple(sorted(
            conjugate_verb(verb, mood, tense, voice, number, person)
        ))
        if result != verbs[verb]:
            sys.exit(
                "-".join((mood, tense, voice, number, person)) + " of "
                + verb + ": expected " + "/".join(verbs[verb]) + ", got "
                + "/".join(result)
            )

    return len(verbs)

def main():
    print("Testing conjugate_verb.py...")

    for form in FORMS:
        verbCnt = run_test(*form)
        print(
            "-".join(form) + f" test passed ({verbCnt:3} verbs)."
        )

    print("All tests passed.")

main()
