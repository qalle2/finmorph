"""Split a Finnish compound."""

# TODO: handle spaces/apostrophes/hyphens better
# TODO: try to reduce the length of word lists required

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
    "harakiri",
    "haravointi",
    "hienosto",
    "hyötyisä",
    "irtonainen",
    "isobaari",
    "isometrinen",
    "isotermi",
    "jäähyväinen",
    "kaavamaistaa",
    "kaikkinainen",
    "kaksinainen",
    "kamalasti",
    "kanavointi",
    "karriääri",
    "katkonainen",
    "kaupunkimaistaa",
    "kaupunkimaistua",
    "kavalasti",
    "kemikaali",
    "kiintonainen",
    "kikkara",
    "kikkeli",
    "kitaristi",
    "kohtalainen",
    "koisata",
    "kokonainen",
    "kolminainen",
    "koloristi",
    "kukintoinen",
    "kuulakka",
    "kuuloinen",
    "kuuluminen",
    "kuuluvilla",
    "kuurata",
    "kyykkysillään",
    "kyykkysiltään",
    "kyyryssä",
    "lihavointi",
    "liikanainen",
    "loiskunta",
    "luuloinen",
    "luurata",
    "maailma",
    "maakari",
    "maalailla",
    "maatiainen",
    "maatuska",
    "mainostaja",
    "menopaussi",
    "moninainen",
    "mutageeni",
    "mutageeninen",
    "myrskyisä",
    "palaveri",
    "papurikko",
    "pensastoinen",
    "piilevä",  # can be a compound or not
    "piinata",
    "piipari",
    "piipata",
    "piirakka",
    "piisata",
    "plussata",
    "poikkinainen",
    "poppari",
    "poppeli",
    "puheilta",
    "pulloveri",
    "punkero",
    "punkkari",
    "punkteerata",
    "puolinainen",
    "puoskari",
    "puutiainen",
    "pyylevä",
    "pääsyinen",
    "raijata",
    "raikaste",
    "railakka",
    "railoinen",
    "rainata",
    "rapauttaa",
    "rappari",
    "rapsakka",
    "rikkonainen",
    "romanialainen",
    "ruiskaista",
    "saamaristi",
    "sensuuri",
    "seurannainen",
    "seutuvilla",
    "suhtauttaa",
    "suojata",
    "suolakko",
    "suolisto",
    "suoranainen",
    "suorasti",
    "suosija",
    "suulaasti",
    "suunnata",
    "suuntaus",
    "suurima",
    "sävyisä",
    "säätöinen",
    "tanhuvilla",
    "teemallinen",
    "teemasto",
    "tehdasmaistua",
    "tienata",
    "tieteillä",
    "tietoinen",
    "toisinto",
    "töppösillään",
    "töppösiltään",
    "ulkonainen",
    "ulkoneva",
    "umpinainen",
    "uusinto",
    "vaiheilta",
    "vajanainen",
    "vakinainen",
    "valannainen",
    "valinnainen",
    "valmisteille",
    "varistori",
    "varsinainen",
    "vartaloinen",
    "voilokki",
    "voimallinen",
    "vuolaasti",
    "vuorata",
    "yhtäänne",
}

EXCEPTIONS = {
    # 2 parts
    "alamaisesti": ("ala", "maisesti"),
    "eioo": ("ei", "oo"),
    "epätasa": ("epä", "tasa"),  # in "epätasa-arvo"
    "erämainen": ("erä", "mainen"),
    "etelämainen": ("etelä", "mainen"),
    "itämainen": ("itä", "mainen"),
    "kapsäkki": ("kap", "säkki"),
    "kenties": ("ken", "ties"),
    "kotimainen": ("koti", "mainen"),
    "kotimaisuus": ("koti", "maisuus"),
    "länsimainen": ("länsi", "mainen"),
    "länsimaisesti": ("länsi", "maisesti"),
    "länsimaisuus": ("länsi", "maisuus"),
    "maailmanensi": ("maailman", "ensi"),  # in "maailmanensi-ilta"
    "maaliero": ("maali", "ero"),
    "mannermaisuus": ("manner", "maisuus"),
    "paraikaa": ("par", "aikaa"),
    "pohjoismainen": ("pohjois", "mainen"),
    "serbokroatian": ("serbo", "kroatian"),  # in "serbokroatian kieli"
    "sotilaskuri": ("sotilas", "kuri"),
    "teemailta": ("teema", "ilta"),
    "ulkomainen": ("ulko", "mainen"),
    "ulkomaisuus": ("ulko", "maisuus"),
    "vaivihkaa": ("vai", "vihkaa"),
    "valkovenäjän": ("valko", "venäjän"),  # in "valkovenäjän kieli"
    # 3+ parts
    "kotimaisuusaste": ("koti", "maisuus", "aste"),
    "peruselintarvike": ("perus", "elin", "tarvike"),
    "yhteispohjoismainen": ("yhteis", "pohjois", "mainen"),
    "ylioppilastutkintolautakunta": ("yli", "oppilas", "tutkinto", "lauta", "kunta"),
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
    if comp in EXCEPTIONS:
        return EXCEPTIONS[comp]

    # try to split in two
    for pos in range(2, len(comp) - 2 + 1):
    #for pos in range(len(comp) - 2, 2 - 1, -1):
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
