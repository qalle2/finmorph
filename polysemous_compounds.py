# find compounds that can be split to many parts or in many ways

# 6 parts: "sanomalehdentoimittaja" = sa_no_ma_lehden_toi_mitta_ja
# 10 ways to split: "nuorisoseuralainen"

import util

def format_compound(compound, splitPositions):
    # e.g. "ylivoimamaali", (3, 8) -> "yli_voima_maali"
    parts = []
    prevPos = 0
    for pos in splitPositions:
        parts.append(compound[prevPos:pos])
        prevPos = pos
    parts.append(compound[prevPos:])
    return "_".join(parts)

def main():
    compounds = set()  # also non-compounds
    parts = set()  # also non-compounds

    for line in util.read_lines("generated-lists/words.csv"):
        word = line.split(",")[0]
        compounds.add(word)
        parts.add(word)

    for comp in util.read_lines("compounds.txt"):
        compounds.add(comp.replace("_", ""))
        parts.update(p.strip("'- ") for p in comp.split("_"))

    print(f"Compounds: {len(compounds)}, parts: {len(parts)}")

    splits = []  # ways to split a compound (tuples of positions)

    for comp in sorted(compounds):
        splits.clear()

        # try to split in 2-8 (a-g = split position)
        for a in range(2, len(comp) - 2 + 1):
            if comp[:a] in parts:
                if comp[a:] in parts:
                    splits.append((a,))
                #
                for b in range(a + 2, len(comp) - 2 + 1):
                    if comp[a:b] in parts:
                        if comp[b:] in parts:
                            splits.append((a, b))
                        #
                        for c in range(b + 2, len(comp) - 2 + 1):
                            if comp[b:c] in parts:
                                if comp[c:] in parts:
                                    splits.append((a, b, c))
                                #
                                for d in range(c + 2, len(comp) - 2 + 1):
                                    if comp[c:d] in parts:
                                        if comp[d:] in parts:
                                            splits.append((a, b, c, d))
                                        #
                                        for e in range(d + 2, len(comp) - 2 + 1):
                                            if comp[d:e] in parts:
                                                if comp[e:] in parts:
                                                    splits.append((a, b, c, d, e))
                                                #
                                                for f in range(e + 2, len(comp) - 2 + 1):
                                                    if comp[e:f] in parts:
                                                        if comp[f:] in parts:
                                                            splits.append((a, b, c, d, e, f))
                                                        #
                                                        for g in range(f + 2, len(comp) - 2 + 1):
                                                            if comp[f:g] in parts:
                                                                if comp[g:] in parts:
                                                                    splits.append((a, b, c, d, e, f, g))

        for split in splits:
            if len(split) >= 6:
                print(f"{comp} = {format_compound(comp, split)} ({len(split)} parts)")

        if len(splits) >= 10:
            print(f"{comp} ({len(splits)} ways to split):")
            for split in sorted(splits):
                print("    " + format_compound(comp, split))

main()
