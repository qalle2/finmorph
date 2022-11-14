import sys
import util

if len(sys.argv) != 3:
    sys.exit(
        "Arguments: CSV file with words and declensions/conjugations, list "
        "file with compounds. Print CSV lines without those that contain a "
        "compound."
    )

# read compounds without underscores
compounds = set(l.replace("_", "") for l in util.read_lines(sys.argv[2]))

# filter CSV lines
for line in util.read_lines(sys.argv[1]):
    if line.split(",")[0] not in compounds:
        print(line)
