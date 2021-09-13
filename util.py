import sys

def read_lines(file_):
    # generate lines from file without newlines
    try:
        with open(file_, "rt", encoding="utf8") as handle:
            handle.seek(0)
            yield from (l.rstrip("\n") for l in handle)
    except OSError:
        sys.exit("Error reading " + file_)
