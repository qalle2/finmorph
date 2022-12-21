"""Split a Finnish compound."""

# TODO: reduce the number of exceptions needed (handle spaces/hyphens better)
# TODO: reduce the length of word lists needed

import itertools, sys

SINGLE_WORDS = {
    # spaces/hyphens
    "à la",
    "à la carte",
    "a priori",
    "agar-agar",
    "alter ego",
    "angina pectoris",
    "art director",
    "beauty box",
    "bed and breakfast",
    "best man",
    "big band",
    "body stocking",
    "bossa nova",
    "CD-ROM",
    "cha-cha-cha",
    "charlotte russe",
    "come-back",
    "crème fraîche",
    "cum laude",
    "cum laude approbatur",
    "dalai-lama",
    "desktop publishing",
    "director cantus",
    "director musices",
    "disc jockey",
    "drag racing",
    "drag show",
    "drive-in",
    "eau de Cologne",
    "ex tempore",
    "eximia cum laude approbatur",
    "fan club",
    "fast food",
    "fifty-fifty",
    "floor show",
    "force majeure",
    "ginger ale",
    "go-go",
    "happy hour",
    "hi-hat",
    "hi-tec",
    "hi-tech",
    "high tech",
    "honoris causa",
    "hot dog",
    "jam session",
    "jet lag",
    "jet set",
    "junk food",
    "knock-out",
    "know-how",
    "kung-fu",
    "long drink",
    "lubenter approbatur",
    "magna cum laude approbatur",
    "make-up",
    "milk shake",
    "non-food",
    "non-iron",
    "non-woven",
    "open house",
    "osso buco",
    "par avion",
    "pick-up",
    "port salut",
    "poste restante",
    "prima ballerina",
    "prima vista",
    "primus motor",
    "pro gradu",
    "rock and roll",
    "roll-on",
    "science fiction",
    "self-made man",
    "small talk",
    "soft ice",
    "still drink",
    "talk show",
    "tax-free",
    "tie-break",
    "tonic water",
    "vol-au-vent",
    # no spaces/hyphens
    "aasialainen",
    "aasialaisuus",
    "aatelisto",
    "aktivointi",
    "aleneva",
    "antibioottinen",
    "antigeeni",
    "arabialainen",
    "asteriski",
    "aukinainen",
    "avonainen",
    "avosetti",
    "bikarbonaatti",
    "bilanssi",
    "biogeeninen",
    "biometrinen",
    "desimaali",
    "erogeeninen",
    "fileerata",
    "geometrinen",
    "haikara",
    "hailakka",
    "haipakka",
    "hajanainen",
    "halkinainen",
    "halogeeni",
    "harakiri",
    "haravointi",
    "heterogeeninen",
    "hienosto",
    "homogeeninen",
    "hyötyisä",
    "irtonainen",
    "isobaari",
    "isometrinen",
    "isotermi",
    "jäähyväinen",
    "kaavamaistaa",
    "kaikkialla",
    "kaikkialle",
    "kaikkialta",
    "kaikkinainen",
    "kaksinainen",
    "kalorimetri",
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
    "kiliastinen",
    "kiropraktiikka",
    "kitaristi",
    "kohtalainen",
    "koisata",
    "kokonainen",
    "kolminainen",
    "koloristi",
    "kronometri",
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
    "loiskina",
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
    "metastaattinen",
    "mezzopiano",
    "moninainen",
    "monitori",
    "mutageeni",
    "mutageeninen",
    "myrskyisä",
    "mysteeri",
    "palaveri",
    "panostaja",
    "papurikko",
    "parametri",
    "parataksi",
    "parataktinen",
    "patogeeninen",
    "peesata",
    "peeveli",
    "pensastoinen",
    "perätyksin",
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
    "portfolio",
    "psykogeeninen",
    "psykometrinen",
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
    "superoksidi",
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
    # spaces/hyphens - 2 parts
    "à la carte -annos": ("à la carte", "annos"),
    "all stars -joukkue": ("all stars", "joukkue"),
    "au pair -tyttö": ("au pair", "tyttö"),
    "CD-ROM-asema": ("CD-ROM", "asema"),
    "CD-ROM-levy": ("CD-ROM", "levy"),
    "cum laude -tentti": ("cum laude", "tentti"),
    "go-go-tyttö": ("go-go", "tyttö"),
    "joint venture -yritys": ("joint venture", "yritys"),
    "open house -kutsut": ("open house", "kutsut"),
    "pin-up-tyttö": ("pin-up", "tyttö"),
    "poste restante -lähetys": ("poste restante", "lähetys"),
    "ro-ro-alus": ("ro-ro", "alus"),
    "stand up -komedia": ("stand up", "komedia"),
    "stand up -koomikko": ("stand up", "koomikko"),
    "tax-free-myymälä": ("tax-free", "myymälä"),
    "tax-free-myynti": ("tax-free", "myynti"),
    # spaces/hyphens - 3+ parts
    "cum laude -arvosana": ("cum laude", "arvo", "sana"),
    "drive-in-elokuvateatteri": ("drive-in", "elo", "kuva", "teatteri"),
    # no spaces/hyphens - 2 parts
    "alamaisesti": ("ala", "maisesti"),
    "eioo": ("ei", "oo"),
    "epätasa": ("epä", "tasa"),  # in "epätasa-arvo"
    "erämainen": ("erä", "mainen"),
    "etelämainen": ("etelä", "mainen"),
    "itämainen": ("itä", "mainen"),
    "jok'ainoa": ("jok", "ainoa"),
    "jok'ikinen": ("jok", "ikinen"),
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
    # no spaces/hyphens - 3+ parts
    "kotimaisuusaste": ("koti", "maisuus", "aste"),
    "peruselintarvike": ("perus", "elin", "tarvike"),
    "yhteispohjoismainen": ("yhteis", "pohjois", "mainen"),
    "ylioppilastutkintolautakunta": (
        "yli", "oppilas", "tutkinto", "lauta", "kunta"
    ),
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

def read_lines(filename):
    with open(filename, "rt", encoding="utf8") as handle:
        handle.seek(0)
        yield from (l.rstrip("\n") for l in handle)

NON_FINALS = {
    l.rstrip("\n") for l in read_lines("generated-lists/nonfinals.txt")
}
FINALS = {
    l.rstrip("\n").split(",")[0]
    for l in read_lines("generated-lists/finals.csv")
}
assert NON_FINALS.isdisjoint(FINALS)

NON_FINALS.difference_update(PART_BLOCKLIST)
FINALS.difference_update(PART_BLOCKLIST)

def split_compound(comp):
    """comp: a Finnish compound; e.g. 'all stars -joukkue'
    return: a tuple of parts without leading/trailing apostrophes/hyphens/
    spaces; e.g. ('all stars', 'joukkue')"""

    # handle exceptions
    if comp in SINGLE_WORDS:
        return (comp,)
    try:
        return EXCEPTIONS[comp]
    except KeyError:
        pass

    # if there are spaces or hyphens, recursively handle words between them
    if " " in comp or "-" in comp:
        comp = comp.replace(" ", "-").replace("--", "-").split("-")
        return tuple(
            itertools.chain.from_iterable(split_compound(p) for p in comp)
        )

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
                if (part2 in FINALS or part2 in NON_FINALS) \
                and part3 in FINALS \
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
                        if (part3 in FINALS or part3 in NON_FINALS) \
                        and part4 in FINALS \
                        and comp[pos3-1] + comp[pos3] not in DOUBLE_VOWELS:
                            return (part1, part2, part3, part4)

    return (comp,)

def main():
    if len(sys.argv) != 2:
        sys.exit(
            "Argument: compound to split. Print the compound with individual "
            "words separated by underscores."
        )

    print("_".join(split_compound(sys.argv[1])))

if __name__ == "__main__":
    main()
