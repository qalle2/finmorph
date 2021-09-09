"""Split a Finnish compound."""

import sys

def split_compound(comp):
    """comp: a Finnish compound; e.g. 'all stars -joukkue'
    return: a tuple of parts without leading/trailing apostrophes/hyphens/spaces; e.g.
    ('all stars', 'joukkue')"""

    # TODO: lots of logic
    return tuple(comp.replace(" ", "-").replace("--", "-").split("-"))

def main():
    if len(sys.argv) != 2:
        sys.exit(
            "Argument: compound to split. Print the compound with individual words separated by "
            "underscores."
        )

    print("_".join(split_compound(sys.argv[1])))

if __name__ == "__main__":
    main()
