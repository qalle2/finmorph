"""Test conjugate_verb.py by comparing the output to test files."""

import os, sys
from conjugate_verb import ALL_FORMS, ITEM_NAMES, conjugate_verb

TEST_DIR = "conjugate_verb-tests"  # read test files from here

def format_test_name(verbForm):
    # verbForm: a tuple from FORMS
    return "-".join(ITEM_NAMES[i] for i in verbForm)

def read_csv(verbForm):
    # Read test cases from CSV file.
    # each line ([] = optional): NomSg,inflected[,inflected...];
    #     inflected forms must be in alphabetical (Unicode) order
    # verbForm: a tuple from FORMS
    # return: {NomSg: (inflected, ...), ...}

    filename = format_test_name(verbForm) + ".csv"
    path = os.path.join(TEST_DIR, filename)
    if not os.path.isfile(path):
        print(f"Warning: {filename} not found, skipping", file=sys.stderr)
        return {}

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

def run_test(verbForm):
    # run a test
    # verbForm: a tuple from ALL_FORMS
    # return: (verb_count, error_count)

    verbs = read_csv(verbForm)  # {NomSg: (inflected, ...), ...}
    errorCnt = 0

    for verb in verbs:
        result = tuple(sorted(conjugate_verb(verb, *verbForm)))
        if result != verbs[verb]:
            print(
                f"Error: {format_test_name(verbForm)} of '{verb}': "
                "expected '" + "/".join(verbs[verb]) + "', got '"
                + "/".join(result) + "'",
                file=sys.stderr
            )
            errorCnt += 1

    return (len(verbs), errorCnt)

def main():
    print("Testing conjugate_verb.py...")
    totalVerbCnt = totalErrorCnt = 0

    for verbForm in ALL_FORMS:
        (verbCnt, errorCnt) = run_test(verbForm)
        totalVerbCnt += verbCnt
        totalErrorCnt += errorCnt

    print(
        f"Tested {len(ALL_FORMS)} verb form(s) (except if file not found) "
        f"and {totalVerbCnt} verb(s)."
    )
    print(f"Detected {totalErrorCnt} error(s).")

main()
