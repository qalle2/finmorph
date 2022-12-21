import re, sys
import util

# a simple line in the XML file:
#   <st>
#     <s>yö</s>
#     <t><tn>19</tn></t>
#   </st>
#
# a more complex line in the XML file:
#   <st>
#     <s>havas</s>
#     <t> <tn>41</tn> <av>E</av> </t>
#     <t> <tn>39</tn>            </t>
#   </st>

# 2 declensions/conjugations, consonant gradation in both
REGEX_YY = re.compile("""
    <s>([^<]+)</s>
    .* >([0-9]+)</tn> .* </av>
    .* >([0-9]+)</tn> .* </av>
""", re.VERBOSE)
# 2 declensions/conjugations, consonant gradation in at least 1st one
REGEX_YN = re.compile("""
    <s>([^<]+)</s>
    .* >([0-9]+)</tn> .* </av>
    .* >([0-9]+)</tn>
""", re.VERBOSE)
# 2 declensions/conjugations, consonant gradation in at least 2nd one
REGEX_NY = re.compile("""
    <s>([^<]+)</s>
    .* >([0-9]+)</tn>
    .* >([0-9]+)</tn> .* </av>
""", re.VERBOSE)
# 2 declensions/conjugations, don't care about consonant gradation
REGEX_NN = re.compile("""
    <s>([^<]+)</s>
    .* >([0-9]+)</tn>
    .* >([0-9]+)</tn>
""", re.VERBOSE)
# (at least) 1 declension/conjugation, consonant gradation
REGEX_Y = re.compile("""
    <s>([^<]+)</s>
    .* >([0-9]+)</tn> .* </av>
""", re.VERBOSE)
# (at least) 1 declension/conjugation, don't care about consonant gradation
REGEX_N = re.compile("""
    <s>([^<]+)</s>
    .* >([0-9]+)</tn>
""", re.VERBOSE)
# any number of declensions/conjugations, don't care about consonant gradation
REGEX_NONE = re.compile("""
    <s>([^<]+)</s>
""", re.VERBOSE)

if len(sys.argv) != 3:
    sys.exit(
        "Read Kotus XML file, print distinct words and their declensions/"
        "conjugations (0-2) in CSV format. Arguments: XML file, which words "
        "('a' = all, 'g' = only those that consonant gradation applies to)."
    )

getAllWords = {"a": True, "g": False}[sys.argv[2]]

conjugationsByWord = {}  # word: set of declensions/conjugations

if getAllWords:
    for line in util.read_lines(sys.argv[1]):
        assert line.count("</tn>") <= 2

        # only detect number of conjugations, not consonant gradation
        for regex in (REGEX_NN, REGEX_N, REGEX_NONE):
            match = regex.search(line)
            if match is not None:
                break

        if match is not None:
            word = match.groups()[0].strip("'- ")
            # save all conjugations
            conjs = {int(c, 10) for c in match.groups()[1:]}
            conjugationsByWord.setdefault(word, set()).update(conjs)
else:
    for line in util.read_lines(sys.argv[1]):
        assert line.count("</tn>") <= 2

        # detect number of conjugations and consonant gradation
        for regex in (
            REGEX_YY, REGEX_YN, REGEX_NY, REGEX_NN,
            REGEX_Y, REGEX_N,
            REGEX_NONE
        ):
            match = regex.search(line)
            if match is not None:
                break

        if match is not None \
        and regex in (REGEX_YY, REGEX_YN, REGEX_NY, REGEX_Y):
            word = match.groups()[0].strip("'- ")
            # save conjugations with consonant gradation
            if regex == REGEX_YN:
                conjs = match.groups()[1:2]  # 1st only
            elif regex == REGEX_NY:
                conjs = match.groups()[2:3]  # 2nd only
            else:
                conjs = match.groups()[1:]
            conjs = {int(c, 10) for c in conjs}
            conjugationsByWord.setdefault(word, set()).update(conjs)

for word in conjugationsByWord:
    print(",".join(
        [word] + [str(c) for c in sorted(conjugationsByWord[word])]
    ))
