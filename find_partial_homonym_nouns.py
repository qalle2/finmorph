# Find partially homonymous inflected nouns. Under construction (the results
# are incomplete). Slow.

import sys
from noundecl import get_declensions
from noun_consgrad import get_consonant_gradation
from decline_noun import decline_noun_specific, CASES_AND_NUMBERS

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
    # return: {inflected: {(declension, lemma), ...}, ...}

    lemmasByInflected = {}
    for (case, number) in CASES_AND_NUMBERS:
        status_msg(f"Generating forms: {case.title()}{number.title()}...")
        for lemma in lemmas:
            for decl in get_declensions(lemma):
                consGrad = get_consonant_gradation(lemma, decl)
                for inflected in (
                    decline_noun_specific(lemma, decl, consGrad, case, number)
                ):
                    lemmasByInflected.setdefault(inflected, set()).add(
                        (decl, lemma)
                    )
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
    print(
        "Columns: declensions of all lemmas, inflected form, lemmas and their "
        "declensions."
    )
    print()

    for inflected in sorted(lemmasByInflected):
        # e.g. lemmasByInflected["kuusta"] = {(18, "kuu"), (24, "kuusi")}

        # e.g. (18, 24)
        allDeclensions = tuple(sorted(set(
            i[0] for i in lemmasByInflected[inflected]
        )))
        allDeclensionsStr = "/".join(format(d, "02") for d in allDeclensions)

        # e.g. "kuu 18 / kuusi 24"
        lemmasStr = " / ".join(
            f"{l} {d}" for (d, l) in sorted(lemmasByInflected[inflected])
        )

        print(f"{allDeclensionsStr:11} {inflected:19} ({lemmasStr})")

main()
