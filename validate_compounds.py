# validate "compounds.txt" and "generated-lists/words.csv"
# note: remember that "extract.sh" updates the latter based on the former

import collections, itertools, sys
import util

# parts of fancy Latin/Greek compounds; used for finding possible new compounds
FANCY_PARTS = {
    "a", "aero", "agraari", "amfi", "aneroidi", "antropo", "arkeo", "astro",
    #
    "baro", "bi", "bio", "bioottinen",
    #
    "definiitti", "di", "digi", "digitaali", "dis", "dividuaali",
    #
    "eko", "enkefalo", "etno",
    #
    "feno", "fleksiivi", "fysio",
    #
    "galvano", "geeninen", "geno", "geo", "grafi", "grafia", "grafinen", "grafisesti", "grammi",
    #
    "halo", "heht", "hemi", "horo", "hydr", "hydro", "hygro", "hypo",
    #
    "ideo", "immuno", "indo", "infra", "inter",
    #
    "kardio", "kinesia", "kosmeto", "kristus", "kroninen", "krono", "kronoida", "kronointi",
    "kryo",
    #
    "latiivi", "logi", "logia", "loginen", "logisesti", "logisoida", "logisointi",
    #
    "metria", "metrisesti", "metrisuus", "metrisyys", "mon", "morfo", "morfologisesti", "multi",
    "musiko",
    #
    "neuro", "nominaali",
    #
    "opto",
    #
    "paattinen", "paattisuus", "pan", "patia", "petro", "poly", "port", "possessiivi", "post",
    "pre", "psyko",
    #
    "reaali", "reaalinen", "reaalisuus", "resiprookki", "rogatiivi",
    #
    "seksuaali", "semiitti", "semiittinen", "semiittisesti", "semitismi", "sensus", "skooppi",
    "skooppinen", "skooppisesti", "skopia", "sosio", "spektro", "strukturaali", "sub", "sykliini",
    "sym", "syn",
    #
    "teetti", "teettinen", "teistisesti", "termo", "tesia", "tetr", "tomo", "tragi", "trans",
    "transitiivi", "tri",
    #
    "vaso",
}

# these parts are unlikely to appear in a compound
EXCLUDE_PARTS = {
    # "alainen" and "alaisuus" here avoid politically incorrect compounds
    "ah", "ai", "alainen", "alaisuus",
    "ha", "haa", "hau", "he", "hei", "hi", "hui", "hä",
    "in", "ir", "ismi", "istua", "isyys", "itse",
    "ja", "jo", "juu",
    "kai", "kas", "kii", "kop", "kuu",
    "lainen", "lata", "lei", "luo",
    "ma", "maa", "mainen", "maisesti", "maisuus", "maton", "me", "mi", "moi", "moinen", "mä",
    "nainen", "nais", "naisuus", "ne", "no",
    "oh", "oi", "oo",
    "pai", "par", "pas",
    "rai", "rata", "re",
    "sa", "sata", "se", "sei", "sen", "silla", "so", "soida", "sointi", "suo", "syys", "sä",
    "taa", "tai", "te", "teinen", "toi", "toinen", "tse", "tuma", "tää",
    "uus",
    "vai", "vainen", "vek", "voi",
}

assert EXCLUDE_PARTS.isdisjoint(FANCY_PARTS)

# read compounds
compounds = set(util.read_lines("compounds.txt"))

# check for duplicate lines (e.g. "maa_liero" and "maali_ero")
plainCompoundCounts = collections.Counter(c.replace("_", "") for c in compounds)
for plainComp in sorted(c for c in plainCompoundCounts if plainCompoundCounts[c] >= 2):
    print("Duplicate line:", plainComp)
del plainCompoundCounts

# convert into tuples, e.g. {("all stars", "joukkue"), ...}
compoundTuples = set()
for comp in compounds:
    compTuple = tuple(p.strip("'- ") for p in comp.split("_"))
    if len(compTuple) < 2:
        print(f'One-part compound: "{comp}"')
    if min(len(p) for p in compTuple) == 0:
        print(f'Zero-length part in compound: "{comp}"')
    compoundTuples.add(compTuple)

# count parts
partCounts = collections.Counter(itertools.chain.from_iterable(compoundTuples))
print(
    f"{sum(partCounts.values())} parts "
    f"({len(partCounts)} distinct) "
    f"in {len(compoundTuples)} compounds"
)
print()

print(
    "Compounds that contain a part that only occurs once in all compounds and is a prefix/suffix "
    "of another part:"
)
# e.g. {"yhde", "lyhde", "yhden", ...}
similarParts = set(itertools.chain.from_iterable(
    (p[:-1], p) for p in partCounts if p[:-1] in partCounts
))
similarParts.update(itertools.chain.from_iterable(
    (p[1:], p) for p in partCounts if p[1:] in partCounts
))
similarParts = {p for p in similarParts if partCounts[p] == 1}
print(",".join("_".join(c) for c in sorted(compoundTuples) if set(c) & similarParts))
print()

parts = set(partCounts)
del partCounts

# add single words (non-compounds) and fancy Latin/Greek words to parts
parts.update(l.split(",")[0].strip("'- ") for l in util.read_lines("generated-lists/words.csv"))
print(f"{len(parts)} distinct parts including single words")
parts.update(FANCY_PARTS)
print(f"{len(parts)} distinct parts including fancy Latin/Greek ones")

# is any part also among compounds?
for comp in sorted(compounds):
    comp = comp.replace("_", "")  # restore original
    if comp in parts:
        print(f'A compound is being used as a part: "{comp}"')
print()

print("Possible compounds (parts that consist of two or three other parts):")
results = set()
for comp in parts:
    for pos1 in range(2, len(comp) - 2 + 1):
        (part1, part2) = (comp[:pos1], comp[pos1:])
        #
        if part1 in parts and part1 not in EXCLUDE_PARTS:
            if part2 in parts and part2 not in EXCLUDE_PARTS \
            and not (part1[-1] == part2[0] and part1[-1] in "aeiouyäö"):
                results.add((part1, part2))
            #
            for pos2 in range(pos1 + 2, len(comp) - 2 + 1):
                (part2, part3) = (comp[pos1:pos2], comp[pos2:])
                if part2 in parts and part3 in parts \
                and part2 not in EXCLUDE_PARTS and part3 not in EXCLUDE_PARTS \
                and not (part1[-1] == part2[0] and part1[-1] in "aeiouyäö") \
                and not (part2[-1] == part3[0] and part2[-1] in "aeiouyäö"):
                    results.add((part1, part2, part3))

print(",".join(sorted("".join(r) for r in results)))
print()

print("Possible non-compounds (compounds that contain a fancy Latin/Greek part):")
print(",".join(
    "_".join(c) for c in sorted(compoundTuples) if set(c) & FANCY_PARTS
))
print()

print(
    "Compounds with possibly misplaced word boundaries (e.g. 'maaliero' being split as both "
    "'maa_liero' and 'maali_ero'):"
)
partPairsByNoBoundary = {}  # e.g. {"maaliero": {"maa_liero", "maali_ero"}, ...}
for comp in compoundTuples:
    for partPair in zip(comp[:-1], comp[1:]):
        partPairsByNoBoundary.setdefault("".join(partPair), set()).add("_".join(partPair))
for partPair in partPairsByNoBoundary:
    if len(partPairsByNoBoundary[partPair]) > 1:
        print("/".join(partPairsByNoBoundary[partPair]))
print()
