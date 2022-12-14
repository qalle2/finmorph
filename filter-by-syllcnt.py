import sys
import countsyll, util

if len(sys.argv) != 3:
    sys.exit(
        "Arguments: CSV file, syllable count (1-4; 4=4 or more). Print lines "
        "containing a word with that many syllables."
    )

syllCnt = int(sys.argv[2], 10)
assert 1 <= syllCnt <= 4

for line in util.read_lines(sys.argv[1]):
    if countsyll.count_syllables(line.split(",")[0]) == syllCnt:
        print(line)
