# test decline_noun.py by comparing the output to test files

import os, sys
from decline_noun \
import ALL_FORMS, C_NOM, C_GEN, ITEM_NAMES, N_SG, decline_noun

TEST_DIR = "decline_noun-tests"  # read test files from here

def format_test_name(case, number):
    return "-".join(ITEM_NAMES[i] for i in (case, number))

def read_csv(case, number):
    # read test cases from CSV file
    # each line ([] = optional): NomSg,inflected[,inflected...]
    # inflected forms must be in alphabetical order
    # return: {NomSg: (inflected, ...), ...}

    words = {}
    path = os.path.join(TEST_DIR, format_test_name(case, number) + ".csv")

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
    # run a test for one case and number
    # case: e.g. C_GEN
    # number: e.g. N_SG
    # return: (word_count, error_count)

    if case == C_NOM and number == N_SG:
        # {NomSg: (NomSg,), ...}
        words = dict((w, (w,)) for w in read_csv(C_GEN, N_SG))
    else:
        # {NomSg: (inflected, ...), ...}
        words = read_csv(case, number)

    errorCnt = 0
    for word in words:
        result = tuple(sorted(decline_noun(word, case, number)))
        if result != words[word]:
            print(
                f"Error: {ITEM_NAMES[case]}-{ITEM_NAMES[number]} of '{word}': "
                "expected '" + "/".join(words[word]) + "', got '"
                + "/".join(result) + "'",
                file=sys.stderr
            )
            errorCnt += 1

    return (len(words), errorCnt)

def main():
    print("Testing decline_noun.py...")
    totalWordCnt = totalErrorCnt = 0

    for (case, number) in ALL_FORMS:
        (wordCnt, errorCnt) = run_test(case, number)
        totalWordCnt += wordCnt
        totalErrorCnt += errorCnt

    print(
        f"Tested {len(ALL_FORMS)} case/number combination(s) and "
        f"{totalWordCnt} noun(s)."
    )
    print(f"Detected {totalErrorCnt} error(s).")

main()
