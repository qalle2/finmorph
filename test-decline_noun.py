"""Test decline_noun.py by comparing the output to test files."""

import os, sys
from decline_noun import *

_TEST_DIR = "decline_noun-tests"  # read test files from here

def format_test_name(case, number):
    return "-".join(ITEM_NAMES[i] for i in (case, number))

def _read_csv(case, number):
    # Read test cases from CSV file.
    # each line ([] = optional): NomSg,inflected[,inflected...];
    #     inflected forms must be in alphabetical (Unicode) order
    # return: {NomSg: (inflected, ...), ...}

    words = {}
    path = os.path.join(_TEST_DIR, format_test_name(case, number) + ".csv")
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
    case:   e.g. C_GEN
    number: e.g. N_SG
    return: number of words tested"""

    if case == C_NOM and number == N_SG:
        # {NomSg: (NomSg,), ...}
        words = dict((w, (w,)) for w in _read_csv(C_GEN, N_SG))
    else:
        # {NomSg: (inflected, ...), ...}
        words = _read_csv(case, number)

    for word in words:
        result = tuple(sorted(decline_noun(word, case, number)))
        if result != words[word]:
            sys.exit("{}{} of {}: expected {}, got {}".format(
                ITEM_NAMES[case],
                ITEM_NAMES[number],
                word,
                "/".join(words[word]),
                "/".join(result),
            ))

    return len(words)

def run_all_tests(verbose=False):
    """Run tests for all cases and numbers."""

    for case in CASES:
        for number in ((N_PL,) if case == C_INS else NUMBERS):
            wordCnt = run_test(case, number)
            if verbose:
                print(
                    format_test_name(case, number)
                    + f": test passed ({wordCnt:3} words)."
                )

def main():
    print("Testing decline_noun.py...")
    run_all_tests(True)
    print("All tests passed.")

if __name__ == "__main__":
    main()
