"""Split a Finnish compound."""

import itertools, sys
import util

SINGLE_WORDS = {
    "aasialainen",
    "aasialaisuus",
    "aatelisto",
    "aktivointi",
    "aleneva",
    "arabialainen",
    "asteriski",
    "aukinainen",
    "avonainen",
    "avosetti",
    "desimaali",
    "fileerata",
    "haikara",
    "hailakka",
    "haipakka",
    "hajanainen",
    "halkinainen",
    "hienosto",
    "hyötyisä",
    "irtonainen",
    "isobaari",
    "isometrinen",
    "isotermi",
    "kaavamaistaa",
    "kamalasti",
    "kanavointi",
    "katkonainen",
    "kaupunkimaistaa",
    "kaupunkimaistua",
    "kiintonainen",
    "kitaristi",
    "koisata",
    "koloristi",
    "kuulakka",
    "kuuloinen",
    "kuuluminen",
    "kuurata",
    "kyyryssä",
    "lihavointi",
    "luuloinen",
    "luurata",
    "maailma",
    "maakari",
    "maatiainen",
    "maatuska",
    "menopaussi",
    "moninainen",
    "mutageeni",
    "myrskyisä",
    "palaveri",
    "piilevä",  # can be a compound or not
    "piipari",
    "piipata",
    "piisata",
    "poppari",
    "poppeli",
    "puheilta",
    "pulloveri",
    "puolinainen",
    "puutiainen",
    "pyylevä",
    "pääsyinen",
    "raikaste",
    "railakka",
    "railoinen",
    "rapauttaa",
    "rappari",
    "rapsakka",
    "romanialainen",
    "ruiskaista",
    "saamaristi",
    "suolakko",
    "suolisto",
    "suorasti",
    "suosija",
    "suoranainen",
    "suulaasti",
    "suuntaus",
    "suurima",
    "sävyisä",
    "säätöinen",
    "tanhuvilla",
    "teemallinen",
    "teemasto",
    "tehdasmaistua",
    "ulkonainen",
    "ulkoneva",
    "umpinainen",
    "vaiheilta",
    "vajanainen",
    "valannainen",
    "valinnainen",
    "varistori",
    "varsinainen",
    "voilokki",
    "voimallinen",
    "vuolaasti",
    "vuorata",
}

PART_BLOCKLIST = {
    "au", "av",
    "hei", "hui",
    "jaa",
    "kap", "ken",
    "mainen", "maisesti", "maisuus", "me",
    "oo", "op",
    "par",
    "vai",
}

DOUBLE_VOWELS = {"aa", "ee", "ii", "oo", "uu", "yy", "ää", "öö"}

NON_FINALS = {l.rstrip("\n") for l in util.read_lines("generated-lists/nonfinals.txt")}
FINALS = {l.rstrip("\n").split(",")[0] for l in util.read_lines("generated-lists/finals.csv")}
assert NON_FINALS.isdisjoint(FINALS)

NON_FINALS.difference_update(PART_BLOCKLIST)
FINALS.difference_update(PART_BLOCKLIST)

def split_compound(comp):
    """comp: a Finnish compound; e.g. 'all stars -joukkue'
    return: a tuple of parts without leading/trailing apostrophes/hyphens/spaces; e.g.
    ('all stars', 'joukkue')"""

    if "'" in comp or "-" in comp or " " in comp:
        # recursion
        comp = comp.replace("'", "-").replace(" ", "-").replace("--", "-").split("-")
        return tuple(itertools.chain.from_iterable(split_compound(p) for p in comp))

    if comp in SINGLE_WORDS:
        return (comp,)

    # try to split in two
    for pos in range(2, len(comp) - 2 + 1):
        (part1, part2) = (comp[:pos], comp[pos:])
        #
        if (part1 in FINALS or part1 in NON_FINALS) and part2 in FINALS \
        and comp[pos-1] + comp[pos] not in DOUBLE_VOWELS:
            return (part1, part2)

    # try to split in three
    for pos1 in range(2, len(comp) - 2 + 1):
        part1 = comp[:pos1]
        #
        if (part1 in FINALS or part1 in NON_FINALS) \
        and comp[pos1-1] + comp[pos1] not in DOUBLE_VOWELS:
            for pos2 in range(pos1 + 2, len(comp) - 2 + 1):
                (part2, part3) = (comp[pos1:pos2], comp[pos2:])
                #
                if (part2 in FINALS or part2 in NON_FINALS) and part3 in FINALS \
                and comp[pos2-1] + comp[pos2] not in DOUBLE_VOWELS:
                    return (part1, part2, part3)

    # try to split in four
    for pos1 in range(2, len(comp) - 2 + 1):
        part1 = comp[:pos1]
        #
        if (part1 in FINALS or part1 in NON_FINALS) \
        and comp[pos1-1] + comp[pos1] not in DOUBLE_VOWELS:
            for pos2 in range(pos1 + 2, len(comp) - 2 + 1):
                part2 = comp[pos1:pos2]
                #
                if (part2 in FINALS or part2 in NON_FINALS) \
                and comp[pos2-1] + comp[pos2] not in DOUBLE_VOWELS:
                    for pos3 in range(pos2 + 2, len(comp) - 2 + 1):
                        (part3, part4) = (comp[pos2:pos3], comp[pos3:])
                        #
                        if (part3 in FINALS or part3 in NON_FINALS) and part4 in FINALS \
                        and comp[pos3-1] + comp[pos3] not in DOUBLE_VOWELS:
                            return (part1, part2, part3, part4)

    return (comp,)

def main():
    if len(sys.argv) != 2:
        sys.exit(
            "Argument: compound to split. Print the compound with individual words separated by "
            "underscores."
        )

    print("_".join(split_compound(sys.argv[1])))

if __name__ == "__main__":
    main()
