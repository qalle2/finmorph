# Find partially homonymous inflected words. Slow.

import sys
from noundecl import get_declensions
from verbconj import get_conjugations
from noun_consgrad import get_consonant_gradation as get_noun_cons_grad
from verb_consgrad import get_consonant_gradation as get_verb_cons_grad
from decline_noun import decline_noun_specific, CASES, NUMBERS
from conjugate_verb import conjugate_verb_specific, ALL_FORMS, ITEM_NAMES

def status_msg(msg):
    # print a status message to stderr (won't be redirected to output file)
    print(msg, file=sys.stderr)

def get_lemmas(filename):
    # generate lemmas (uninflected forms)
    with open(filename, "rt", encoding="utf8") as handle:
        handle.seek(0)
        yield from (l.split(",")[0] for l in handle)

def group_noun_lemmas(lemmas, lemmasByInflected):
    # group noun lemmas by inflected forms
    # lemmasByInflected/return: {inflected: {(declension, lemma), ...}, ...}

    forms = tuple(
        (c, n) for c in CASES for n in NUMBERS
        if not (c == "ins" and n == "sg")
    )

    for form in forms:
        # (case, number)
        status_msg("Generating forms: " + "-".join(form) + "...")
        for lemma in lemmas:
            for decl in get_declensions(lemma):
                consGrad = get_noun_cons_grad(lemma, decl)
                for inflected in (
                    decline_noun_specific(lemma, decl, consGrad, *form)
                ):
                    lemmasByInflected.setdefault(inflected, set()).add(
                        (decl, lemma)
                    )

    return lemmasByInflected

def group_verb_lemmas(lemmas, lemmasByInflected):
    # group verb lemmas by inflected forms
    # lemmasByInflected/return: {inflected: {(conjugation, lemma), ...}, ...}

    for form in ALL_FORMS:
        # (mood, tense, voice, number, person)
        status_msg(
            "Generating forms: " + "-".join(ITEM_NAMES[i] for i in form)
            + "..."
        )
        for lemma in lemmas:
            for conj in get_conjugations(lemma):
                consGrad = get_verb_cons_grad(lemma, conj)
                for inflected in (
                    conjugate_verb_specific(lemma, conj, consGrad, *form)
                ):
                    lemmasByInflected.setdefault(inflected, set()).add(
                        (conj, lemma)
                    )

    return lemmasByInflected

def delete_non_homonyms(lemmasByInflected):
    # delete inflected forms with just one lemma
    return dict(
        (l, lemmasByInflected[l]) for l in lemmasByInflected
        if len(lemmasByInflected[l]) > 1
    )

def main():
    lemmasByInflected = {}

    lemmas = set(get_lemmas("generated-lists/nouns.csv"))
    status_msg(f"Noun lemmas: {len(lemmas)}")
    lemmasByInflected = group_noun_lemmas(lemmas, lemmasByInflected)
    status_msg(f"Inflected forms: {len(lemmasByInflected)}")

    lemmas = set(get_lemmas("generated-lists/verbs.csv"))
    status_msg(f"Verb lemmas: {len(lemmas)}")
    lemmasByInflected = group_verb_lemmas(lemmas, lemmasByInflected)
    status_msg(f"Inflected forms: {len(lemmasByInflected)}")

    lemmasByInflected = delete_non_homonyms(lemmasByInflected)
    status_msg(f"Homonymous inflected forms: {len(lemmasByInflected)}")

    print(f"Automatically generated with '{sys.argv[0]}'.")
    print(
        "Columns: declensions/conjugations of all lemmas, inflected form, "
        "lemmas and their declensions/conjugations."
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

        print(f"{allDeclensionsStr:14} {inflected:19} ({lemmasStr})")

main()
