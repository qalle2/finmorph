import sys
from noundecl import get_declensions
from verbconj import get_conjugations
from noun_consgrad import get_consonant_gradation as get_noun_cons_grad
from verb_consgrad import get_consonant_gradation as get_verb_cons_grad
from decline_noun import decline_noun_specific, CASES, NUMBERS
from conjugate_verb import conjugate_verb_specific, ALL_FORMS, ITEM_NAMES

def get_lemmas(filename):
    # generate lemmas (uninflected forms)
    with open(filename, "rt", encoding="utf8") as handle:
        handle.seek(0)
        yield from (l.split(",")[0] for l in handle)

def get_nouns(lemmas):
    # generate inflected forms of noun lemmas

    forms = tuple(
        (c, n) for c in CASES for n in NUMBERS
        if not (c == "ins" and n == "sg")
    )

    for form in forms:
        # (case, number)
        for lemma in lemmas:
            for decl in get_declensions(lemma):
                consGrad = get_noun_cons_grad(lemma, decl)
                yield from decline_noun_specific(lemma, decl, consGrad, *form)

def get_verbs(lemmas):
    # generate inflected forms of verb lemmas

    yield from lemmas

    for form in ALL_FORMS:
        # (mood, tense, voice, number, person)
        for lemma in lemmas:
            for conj in get_conjugations(lemma):
                consGrad = get_verb_cons_grad(lemma, conj)
                yield \
                from conjugate_verb_specific(lemma, conj, consGrad, *form)

def main():
    if len(sys.argv) != 3:
        sys.exit(
            "Print lemma and inflected forms of nouns and verbs with "
            "specified length. Arguments: minimumLength maximumLength"
        )
    (minLen, maxLen) = (int(a) for a in sys.argv[1:])

    lemmas = set(get_lemmas("generated-lists/nouns.csv"))
    for word in get_nouns(lemmas):
        if minLen <= len(word) <= maxLen:
            print(word)

    lemmas = set(get_lemmas("generated-lists/verbs.csv"))
    for word in get_verbs(lemmas):
        if minLen <= len(word) <= maxLen:
            print(word)

main()
