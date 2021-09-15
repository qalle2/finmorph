import sys
import verbconj

def get_consonant_gradation(verb, conj):
    """Does consonant gradation applies to the verb (str) in the specified conjugation (int)?
    return: bool"""

    # note: "keritä" is the only verb to which consonant graduation applies in some but not all
    # conjugations (not in 69, yes in 75)

    # TODO: finish this function
    return False

def main():
    if len(sys.argv) != 2:
        sys.exit(
            "Argument: a Finnish verb (not a compound) in the infinitive. Print the Kotus "
            "conjugation(s) (52-78) and whether consonant gradation applies."
        )
    verb = sys.argv[1]

    conjugationsAndConsGradations = set()  # {(conjugation, consonant_gradation_applies), ...}
    for conj in verbconj.get_conjugations(verb):
        conjugationsAndConsGradations.add((conj, get_consonant_gradation(verb, conj)))

    if not conjugationsAndConsGradations:
        sys.exit("Unrecognized verb.")

    for (conj, consGrad) in sorted(conjugationsAndConsGradations):
        print(
            f'Conjugation {conj} (like "{verbconj.CONJUGATION_DESCRIPTIONS[conj]}") '
            + ["without", "with"][consGrad]
            + " consonant gradation"
        )

if __name__ == "__main__":
    main()
