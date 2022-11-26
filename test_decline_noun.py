"""Test decline_noun.py by comparing the output to test files."""

import os, sys
import decline_noun

_TEST_DIR = "decline_noun-tests"  # read test files from here

# (case, number)
_ALL_TESTS = (
    ("nom", "sg"),
    ("nom", "pl"),
    ("gen", "sg"),
    ("tra", "sg"),
    ("ine", "sg"),
    ("ela", "sg"),
    ("ade", "sg"),
    ("abl", "sg"),
    ("all", "sg"),
    ("abe", "sg"),
    ("ess", "sg"),
    ("ill", "sg"),
    ("par", "sg"),
)

def _read_csv(case, number):
    # Read test cases from CSV file.
    # each line ([] = optional): NomSg,inflected[,inflected...];
    #     inflected forms must be in alphabetical (Unicode) order
    # return: {NomSg: (inflected, ...), ...}

    words = {}
    path = os.path.join(_TEST_DIR, f"{case}-{number}.csv")
    with open(path, "rt", encoding="utf8") as handle:
        handle.seek(0)
        for line in handle:
            line = line.rstrip("\n")
            if line and not line.startswith("#"):
                items = line.split(",")
                if len(items) < 2 or min(len(i) for i in items) < 2:
                    sys.exit("Invalid CSV line: " + line)
                words[items[0]] = tuple(items[1:])
    return words

def run_test(case, number):
    """Run a test for one case and number.
    case:   e.g. 'gen'
    number: e.g. 'sg'
    return: number of words tested"""

    if case == "nom" and number == "sg":
        # {NomSg: (NomSg,), ...}
        words = dict((w, (w,)) for w in _read_csv("gen", "sg"))
    else:
        # {NomSg: (inflected, ...), ...}
        words = _read_csv(case, number)

    for word in words:
        result = tuple(sorted(set(
            decline_noun.decline_noun(word, case, number)
        )))
        if result != words[word]:
            sys.exit("{}{} of {}: expected {}, got {}".format(
                case.title(),
                number.title(),
                word,
                "/".join(words[word]),
                "/".join(result),
            ))

    return len(words)

def run_all_tests(verbose=False):
    """Run tests for all cases and numbers."""

    for (case, number) in _ALL_TESTS:
        if verbose:
            print(f"Running test: {case.title()}{number.title()}")
        wordCnt = run_test(case, number)
        if verbose:
            print(f"Test passed ({wordCnt} words).")

def main():
    print("Testing decline_noun.py...")
    run_all_tests(True)
    print("All tests passed.")

if __name__ == "__main__":
    main()
