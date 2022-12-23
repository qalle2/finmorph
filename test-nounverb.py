# test noundecl.py, verbconj.py, noun_consgrad.py or verb_consgrad.py

import sys
from noundecl import get_declensions
from verbconj import get_conjugations
from noun_consgrad import get_consonant_gradation as get_cons_grad_noun
from verb_consgrad import get_consonant_gradation as get_cons_grad_verb

CONS_GRAD_FILE = "generated-lists/words-consgrad.csv"

def read_csv(file_):
    # generate lines from a CSV file as tuples of fields
    with open(file_, "rt", encoding="utf8") as handle:
        handle.seek(0)
        for line in handle:
            line = line.rstrip("\n")
            fields = line.split(",")
            if len(fields) < 2:
                sys.exit("Invalid CSV line:" + line)
            yield tuple(fields)

def run_test_n():
    # test noundecl.py

    wordCount = errorCount = 0

    for fields in read_csv("generated-lists/nouns.csv"):
        # get word and correct declensions
        word = fields[0]
        # fix errors in source data
        if word == "finaali":
            decls = {6}
        elif word == "ilmeinen":
            decls = {38}
        else:
            decls = {int(c, 10) for c in fields[1:]}
            if word == "tuomas":
                decls.add(39)
        decls = tuple(sorted(decls))

        detectedDecls = get_declensions(word)
        if detectedDecls != decls:
            print(
                f"'{word}': expected declension(s) "
                + "/".join(str(c) for c in sorted(decls))
                + ", got "
                + "/".join(str(c) for c in sorted(detectedDecls))
            )
            errorCount += 1
        wordCount += 1

    return (wordCount, errorCount)

def run_test_v():
    # test verbconj.py

    wordCount = errorCount = 0

    for fields in read_csv("generated-lists/verbs.csv"):
        # get word and correct conjugations
        word = fields[0]
        if word.endswith("ee"):
            continue
        # fix errors in source data
        if word == "hilsehtiä":
            conjs = {61}
        elif word == "pörhistyä":
            conjs = {52}
        else:
            conjs = {int(c, 10) for c in fields[1:]}
        if not conjs:
            continue
        conjs = tuple(sorted(conjs))

        detectedConjs = get_conjugations(word)
        if detectedConjs != conjs:
            print(
                f"'{word}': expected conjugation(s) "
                + "/".join(str(c) for c in sorted(conjs))
                + ", got "
                + "/".join(str(c) for c in sorted(detectedConjs))
            )
            errorCount += 1
        wordCount += 1

    return (wordCount, errorCount)

def get_cons_grad_data(test):
    # get declensions/conjugations to which consonant gradation applies
    conjsByWord = {}
    for fields in read_csv(CONS_GRAD_FILE):
        conjsByWord[fields[0]] = {int(c, 10) for c in fields[1:]}

    # fix errors in the source data
    if test == "ng":
        conjsByWord["alje"] = {48}
        conjsByWord["auer"] = {49}
        conjsByWord["harre"] = {48}
        conjsByWord["hynte"] = {48}
        conjsByWord["näin"] = {33}
        conjsByWord["pue"] = {48}
        conjsByWord["ryntys"] = {41}
    else:
        conjsByWord["hilsehtiä"] = {61}

    return conjsByWord

def run_test_ng():
    # test noun_consgrad.py

    declsByWord = get_cons_grad_data("ng")
    wordCount = errorCount = 0

    for fields in read_csv("generated-lists/nouns.csv"):
        # get word and correct declensions
        word = fields[0]
        decls = set(int(c, 10) for c in fields[1:])
        if word == "tuomas":
            decls.add(39)  # error in source data; fix here for now
        decls = tuple(sorted(decls))

        for decl in get_declensions(word):
            detectedGrad = get_cons_grad_noun(word, decl)
            if detectedGrad \
            and decl not in declsByWord.setdefault(word, set()):
                word2 = f"'{word}'"
                print(
                    f"{word2:20} in declension {decl:2}: "
                    "expected no consonant gradation but got it"
                )
                errorCount += 1
            elif not detectedGrad \
            and decl in declsByWord.setdefault(word, set()):
                word2 = f"'{word}'"
                print(
                    f"{word2:20} in declension {decl:2}: "
                    "expected consonant gradation but got none"
                )
                errorCount += 1
        wordCount += 1

    return (wordCount, errorCount)

def run_test_vg():
    # test verb_consgrad.py

    conjsByWord = get_cons_grad_data("nv")
    wordCount = errorCount = 0

    for fields in read_csv("generated-lists/verbs.csv"):
        # get word and correct conjugations
        word = fields[0]
        if word.endswith("ee"):
            continue
        conjs = set(int(c, 10) for c in fields[1:])
        if not conjs:
            continue
        conjs = tuple(sorted(conjs))

        for conj in get_conjugations(word):
            detectedGrad = get_cons_grad_verb(word, conj)
            if detectedGrad \
            and conj not in conjsByWord.setdefault(word, set()):
                word2 = f"'{word}'"
                print(
                    f"{word2:20} in conjugation {conj:2}: "
                    "expected no consonant gradation but got it"
                )
                errorCount += 1
            elif not detectedGrad \
            and conj in conjsByWord.setdefault(word, set()):
                word2 = f"'{word}'"
                print(
                    f"{word2:20} in conjugation {conj:2}: "
                    "expected consonant gradation but got none"
                )
                errorCount += 1
        wordCount += 1

    return (wordCount, errorCount)

def main():
    if len(sys.argv) != 2:
        sys.exit(
            "Argument: which program to test ('n'=noundecl.py, "
            "'v'=verbconj.py, 'ng'=noun_consgrad.py, 'vg'=verb_consgrad.py)."
        )
    test = sys.argv[1]

    if test == "n":
        (wordCount, errorCount) = run_test_n()
    elif test == "v":
        (wordCount, errorCount) = run_test_v()
    elif test == "ng":
        (wordCount, errorCount) = run_test_ng()
    elif test == "vg":
        (wordCount, errorCount) = run_test_vg()
    else:
        sys.exit("Invalid argument.")

    print(f"Words: {wordCount}, errors: {errorCount}")

main()
