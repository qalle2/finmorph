"""Read CSV data from stdin, merge lines with identical words. (If successive lines contain
an identical word, only output that word once, along with the union of all the
declensions/conjugations.)"""

import sys

def format_output_line(word, conjugations):
    return word + ";" + ",".join(str(c) for c in sorted(conjugations))

combinedConjugations = set()  # declensions/conjugations of one word from several lines
prevWord = None  # previous word

for line in sys.stdin:
    # parse line
    if line.count(";") != 1:
        sys.exit("Every line must contain exactly one semicolon.")
    (word, conjugations) = line.rstrip().split(";")
    conjugations = {int(c) for c in conjugations.split(",")}

    if prevWord is None:
        # first line; start new word
        prevWord = word
    elif word != prevWord:
        # run of identical words has ended; print previous word and start new one
        print(format_output_line(prevWord, combinedConjugations))
        combinedConjugations.clear()
        prevWord = word

    # collect declensions/conjugations from successive identical words
    combinedConjugations.update(conjugations)

if prevWord is not None:
    # print last word
    print(format_output_line(prevWord, combinedConjugations))
