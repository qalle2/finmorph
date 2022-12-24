"""Test conjugate_verb.py by comparing the output to test files."""

import os, sys
from conjugate_verb import *

TEST_DIR = "conjugate_verb-tests"  # read test files from here

# verb forms to test
FORMS = (
    # mood, tense, voice, number/None, person/None
    (M_IND, T_PRE, V_ACT, N_SG, P_1),
    (M_IND, T_PRE, V_ACT, N_SG, P_3),
    (M_IND, T_PRE, V_ACT, N_PL, P_3),
    (M_IND, T_PST, V_ACT, N_SG, P_1),
    (M_IND, T_PST, V_ACT, N_SG, P_3),

    (M_CON, T_PRE, V_ACT, N_SG, P_3),

    (M_IMP, T_PRE, V_ACT, N_SG, P_2),
    (M_IMP, T_PRE, V_ACT, N_SG, P_3),
    (M_IMP, T_PRE, V_ACT, N_PL, P_1),
    (M_IMP, T_PRE, V_ACT, N_PL, P_2),
    (M_IMP, T_PRE, V_ACT, N_PL, P_3),
)

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
    # Run a test. Return number of verbs tested.
    # verbForm: a tuple from FORMS

    verbs = read_csv(verbForm)  # {NomSg: (inflected, ...), ...}

    for verb in verbs:
        result = tuple(sorted(conjugate_verb(verb, *verbForm)))
        if result != verbs[verb]:
            sys.exit(
                format_test_name(verbForm) + " of "
                + verb + ": expected " + "/".join(verbs[verb]) + ", got "
                + "/".join(result)
            )

    return len(verbs)

def main():
    print("Testing conjugate_verb.py...")

    for verbForm in FORMS:
        verbCnt = run_test(verbForm)
        print(
            format_test_name(verbForm) + f" test passed ({verbCnt:3} verbs)."
        )

    print("All tests passed.")

main()
