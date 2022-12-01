# Find partially homonymous inflected nouns. Under construction (the results
# are incomplete). Slow.

import collections, itertools, sys
from decline_noun import decline_noun
from noundecl import get_declensions

# (case, number)
CASES = (
    ("nom", "sg"),
    ("nom", "pl"),
    ("gen", "sg"),
    ("gen", "pl"),
    ("tra", "sg"),
    ("ine", "sg"),
    ("ela", "sg"),
    ("ade", "sg"),
    ("abl", "sg"),
    ("all", "sg"),
    ("abe", "sg"),
    ("ess", "sg"),
    ("ill", "sg"),
    ("par", "sg"),
)

def status_msg(msg):
    # print a status message to stderr (won't be redirected to output file)
    print(msg, file=sys.stderr)

def get_lemmas():
    # read noun lemmas (uninflected forms)
    with open("generated-lists/nouns.csv", "rt", encoding="utf8") as handle:
        handle.seek(0)
        lemmas = {l.split(",")[0] for l in handle}
    return lemmas

def group_lemmas_by_inflected(lemmas):
    # group lemmas by inflected forms
    # return: {inflected: {lemma, ...}, ...}

    lemmasByInflected = {}
    for (case, number) in CASES:
        status_msg(f"Generating forms: {case.title()}{number.title()}...")
        for lemma in lemmas:
            for inflected in decline_noun(lemma, case, number):
                lemmasByInflected.setdefault(inflected, set()).add(lemma)
    return lemmasByInflected

def delete_non_homonyms(lemmasByInflected):
    # delete inflected forms with just one lemma
    return dict(
        (l, lemmasByInflected[l]) for l in lemmasByInflected
        if len(lemmasByInflected[l]) > 1
    )

def main():
    lemmas = get_lemmas()
    status_msg(f"Lemmas: {len(lemmas)}")
    lemmasByInflected = group_lemmas_by_inflected(lemmas)
    status_msg(f"Inflected forms: {len(lemmasByInflected)}")
    lemmasByInflected = delete_non_homonyms(lemmasByInflected)
    status_msg(f"Homonymous inflected forms: {len(lemmasByInflected)}")

    print("Automatically generated with 'find_partial_homonym_nouns.py'.")
    print("Columns:")
    print("- declensions of all lemmas (may include incorrect ones)")
    print("- inflected form")
    print("- lemmas and their declensions (may include incorrect declensions)")
    print()

    for inflected in sorted(lemmasByInflected):
        # e.g. "kuusta" -> {"kuusi": (24, 27), "kuu": (18,)}
        declensionsByLemma = dict(
            (l, get_declensions(l)) for l in lemmasByInflected[inflected]
        )

        # e.g. "kuusta" -> (18, 24, 27)
        allDeclensions = tuple(sorted(set(itertools.chain.from_iterable(
            declensionsByLemma.values()
        ))))
        allDeclensionsStr = "/".join(str(d) for d in allDeclensions)

        # e.g. "kuusta" -> (("kuu", (18,)), ("kuusi", (24, 27)))
        lemmas = tuple(
            (l, declensionsByLemma[l])
            for l in sorted(lemmasByInflected[inflected])
        )
        lemmasStr = " / ".join(
            l[0] + " " + ",".join(str(d) for d in l[1]) for l in lemmas
        )

        print(f"{allDeclensionsStr:10} {inflected:19} ({lemmasStr})")

main()
