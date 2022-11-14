import re, sys
import util

# regexes for a line with 2/1/0 declensions/conjugations
REGEX_2CONJ = re.compile(
    r"<s>([^<]+)</s> .* >([0-9]+)</tn> .* >([0-9]+)</tn>", re.VERBOSE
)
REGEX_1CONJ = re.compile(
    r"<s>([^<]+)</s> .* >([0-9]+)</tn>", re.VERBOSE
)
REGEX_0CONJ = re.compile(
    r"<s>([^<]+)</s>", re.VERBOSE
)

if len(sys.argv) != 3:
    sys.exit(
        "Read Kotus XML file, print distinct words and their declensions/"
        "conjugations (0-2) in CSV format. Arguments: XML file, which words "
        "('a' = all, 'g' = only those that consonant gradation applies to)."
    )

getAllWords = {"a": True, "g": False}[sys.argv[2]]

conjugationsByWord = {}  # word: set of declensions/conjugations

for line in util.read_lines(sys.argv[1]):
    assert line.count("</tn>") <= 2

    if getAllWords or "</av>" in line:
        for regex in (REGEX_2CONJ, REGEX_1CONJ, REGEX_0CONJ):
            match = regex.search(line)
            if match is not None:
                break

        if match is not None:
            word = match.groups()[0].strip("'- ")
            conjugations = {int(c, 10) for c in match.groups()[1:]}
            conjugationsByWord.setdefault(word, set()).update(conjugations)

for word in conjugationsByWord:
    print(",".join(
        [word] + [str(c) for c in sorted(conjugationsByWord[word])]
    ))
