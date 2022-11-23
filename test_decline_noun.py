"""Test decline_noun.py by comparing the output to test files."""

import os, sys
import decline_noun

_TEST_DIR = "decline_noun-tests"  # read test files from here

# (case, number)
_ALL_TESTS = (
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

# Kotus declensions:
# 1=valo, 2=palvelu, 3=valtio, 4=laatikko, 5=risti, 6=paperi, 7=ovi, 8=nalle,
# 9=kala, 10=koira/kahdeksan, 11=omena, 12=kulkija, 13=katiska, 14=solakka,
# 15=korkea, 16=vanhempi, 17=vapaa, 18=maa, 19=suo, 20=filee, 21=rosé,
# 22=parfait, 23=tiili, 24=uni, 25=toimi, 26=pieni, 27=käsi, 28=kynsi,
# 29=lapsi, 30=veitsi, 31=kaksi, 32=sisar/kymmenen, 33=kytkin, 34=onneton,
# 35=lämmin, 36=sisin, 37=vasen, 38=nainen, 39=vastaus, 40=kalleus, 41=vieras,
# 42=mies, 43=ohut, 44=kevät, 45=kahdeksas, 46=tuhat, 47=kuollut, 48=hame,
# 49=askel/askele

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

    words = _read_csv(case, number)  # {NomSg: (inflected, ...), ...}

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
