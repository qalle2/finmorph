"""Conjugate a Finnish verb. Under construction."""

import re, sys
from verb_consgrad import get_consonant_gradation
from verbconj import get_conjugations

# - C = any consonant, V = any vowel, A = a/ä, O = o/ö, U = u/y
# - conjugations (52-76) are from Kotus

# -----------------------------------------------------------------------------

# verbs with optional consonant gradation
_OPTIONAL_CONS_GRAD = frozenset((
    "halvata", "kevetä", "kimmota", "lohkoa", "pokata", "pykiä", "raakata",
    "sulkia", "tavata"
))

# consonant gradation is weak to strong in these conjugations
_CONJS_STRENGTHEN = frozenset((
    # rohkaista, tulla, vanheta, salata, katketa, selvitä
    66, 67, 72, 73, 74, 75
))

# -----------------------------------------------------------------------------

# rules for consonant gradation
# - format: (regex_from, regex_to)
# - "$" will be appended to regex_from
# - only the 1st match with regex_from will be applied
# - the ending will be changed afterwards
#
# strong to weak (happens before -VA)
_CONS_GRAD_WEAKEN = tuple((re.compile(f + "$"), t) for (f, t) in (
    # k
    ("kk([aeiouyäö][aä])",               r"k\1"),    # -kkVA
    ("nk([aeiouyäö][aä])",               r"ng\1"),   # -nkVA
    ("([lr])k(e[aä])",                   r"\1j\2"),  # -lkeA/-rkeA
    ("([aeiouyäöhlr])k([aeiouyäö][aä])", r"\1\2"),   # V/h/l/r + kVA
    # p
    ("pp([aeiouyäö][aä])",              r"p\1"),    # -ppVA
    ("mp([aeiouyäö][aä])",              r"mm\1"),   # -mpVA
    ("([aeiouyäölr])p([aeiouyäö][aä])", r"\1v\2"),  # -VpVA/-lpVA/-rpVA
    # t
    ("tt([aeiouyäö][aä])",             r"t\1"),     # -ttVA
    ("([lnr])t([aeiouyäö][aä])",       r"\1\1\2"),  # -ltVA/-ntVA/-rtVA
    ("([aeiouyäöh])t([aeiouyäö][aä])", r"\1d\2"),   # -VtVA/-htVA
))
#
# weak to strong (happens before -VA/-VtA/-ellA)
_CONS_GRAD_STRENGTHEN = tuple((re.compile(f + "$"), t) for (f, t) in (
    # k/p/t -> kk/pp/tt
    ("([aeiouyäölmnr])([kpt])([aeiouyäö]t?[aä]|ell[aä])", r"\1\2\2\3"),
    # g/j/- -> k
    ("ng([aeiouyäö]t?[aä]|ell[aä])",                 r"nk\1"),   # ng
    ("([hlr])j([aeiouyäö]t?[aä]|ell[aä])",           r"\1k\2"),  # hj/lj/rj
    ("([aeiouyäö][hlr]?)([aeiouyäö]t?[aä]|ell[aä])", r"\1k\2"),  # V/Vh/Vl/Vr
    # m/v -> p
    ("mm([aeiouyäö]t?[aä]|ell[aä])",              r"mp\1"),   # mm
    ("([aeiouyäölr])v([aeiouyäö]t?[aä]|ell[aä])", r"\1p\2"),  # Vv/lv/rv
    # d/l/n/r -> t
    (r"([lnr])\1([aeiouyäö]t?[aä]|ell[aä])",     r"\1t\2"),  # ll/nn/rr
    ("([aeiouyäöh])d([aeiouyäö]t?[aä]|ell[aä])", r"\1t\2"),  # Vd/hd
))

_CONS_GRAD_STRENGTHEN_EXCEPTIONS = {
    # the only conjugation 66 verbs with consonant gradation
    "häväistä":  "häpäistä",
    "rangaista": "rankaista",
    "vavista":   "vapista",
}

def _consonant_gradation(verb, strengthen=False):
    # apply consonant gradation to the verb
    # strengthen: False = strong to weak, True = weak to strong

    if strengthen and verb in _CONS_GRAD_STRENGTHEN_EXCEPTIONS:
        return _CONS_GRAD_STRENGTHEN_EXCEPTIONS[verb]

    regexes = _CONS_GRAD_STRENGTHEN if strengthen else _CONS_GRAD_WEAKEN
    for (reFrom, reTo) in regexes:
        if re.search(reFrom, verb) is not None:
            return re.sub(reFrom, reTo, verb)
    sys.exit(f"Failed to apply consonant gradation: {verb=}, {strengthen=}")

def _consonant_gradation_main(verb, conj, mood, tense, voice, person):
    # generate the verb with/without consonant gradation
    # (before changing ending)

    if mood == "ind" and tense in ("pre", "pst") and voice == "act" \
    and (person != "3" or conj in _CONJS_STRENGTHEN):
        yield _consonant_gradation(verb, conj in _CONJS_STRENGTHEN)
        if verb in _OPTIONAL_CONS_GRAD:
            yield verb
    else:
        yield verb

# -----------------------------------------------------------------------------

# rules for changing endings of verbs
# - format: conjugation: ((regex_from, regex_to), ...)
# - "$" will be appended to regex_from
# - only the 1st match with regex_from will be applied
# - consonant gradation has already been applied
# - number/person endings will be added afterwards
# - for clarity, avoid making changes here that need to be undone later

_CHANGES_IND_PRE_ACT = {
    52: (("[aä]",      ""),),     # sanoa
    53: (("[aä]",      ""),),     # muistaa
    54: (("[aä]",      ""),),     # huutaa
    55: (("[aä]",      ""),),     # soutaa
    56: (("[aä]",      ""),),     # kaivaa
    57: (("[aä]",      ""),),     # saartaa
    58: (("[aä]",      ""),),     # laskea
    59: (("[aä]",      ""),),     # tuntea
    60: (("[aä]",      ""),),     # lähteä
    61: (("[aä]",      ""),),     # sallia
    62: (("d[aä]",     ""),),     # voida
    63: (("d[aä]",     ""),),     # saada
    64: (("d[aä]",     ""),),     # juoda
    65: (("d[aä]",     ""),),     # käydä
    66: (("t[aä]",     "e"),),    # rohkaista
    67: (("[lnr][aä]", "e"),),    # tulla
    68: (("d[aä]",     ""),),     # tupakoida + variant tupakoitse
    69: (("t[aä]",     "tse"),),  # valita
    70: (("st[aä]",    "kse"),),  # juosta
    71: (("hd[aä]",    "e"),),    # nähdä
    72: (("t[aä]",     "ne"),),   # vanheta
    73: (("ta", "a"), ("tä", "ä")),  # salata
    74: (("ta", "a"), ("tä", "ä")),  # katketa
    75: (("ta", "a"), ("tä", "ä")),  # selvitä
    76: (("[aä]",      ""),),     # taitaa
}

_CHANGES_IND_PST_ACT = {
    52: (("[aä]",       "i"),),    # sanoa
    53: (("(aa|ää)",    "i"),),    # muistaa
    54: (("t(aa|ää)",   "si"),),   # huutaa
    55: (("(aa|ää)",    "i"),),    # soutaa
    56: (("aa",         "oi"),),   # kaivaa
    57: (("aa",         "oi"),),   # saartaa
    58: (("e[aä]",      "i"),),    # laskea
    59: (("tea",        "si"),),   # tuntea
    60: (("eä",         "i"),),    # lähteä
    61: (("i[aä]",      "i"),),    # sallia
    62: (("d[aä]",      ""),),     # voida
    63: (("[aäy]d[aä]", "i"),),    # saada
    64: (("iedä", "ei"), ("uoda", "oi"), ("yödä", "öi")),  # juoda
    65: (("ydä",        "vi"),),   # käydä
    66: (("t[aä]",      "i"),),    # rohkaista
    67: (("[lnr][aä]",  "i"),),    # tulla
    68: (("d[aä]", ""), ("e", "i")),  # tupakoida + variant tupakoitse
    69: (("t[aä]",      "tsi"),),  # valita
    70: (("st[aä]",     "ksi"),),  # juosta
    71: (("hd[aä]",     "i"),),    # nähdä
    72: (("t[aä]",      "ni"),),   # vanheta
    73: (("t[aä]",      "si"),),   # salata
    74: (("t[aä]",      "si"),),   # katketa
    75: (("t[aä]",      "si"),),   # selvitä
    76: (("t(aa|ää)",   "si"),),   # taitaa
}

def _change_ending(verb, conj, mood, tense, voice):
    # change the ending of the verb (before applying consonant gradation or
    # adding number/person endings)

    # get regexes to apply
    if mood == "ind" and tense == "pre" and voice == "act":
        changes = _CHANGES_IND_PRE_ACT.get(conj, ())
    elif mood == "ind" and tense == "pst" and voice == "act":
        changes = _CHANGES_IND_PST_ACT.get(conj, ())
    else:
        sys.exit("not implemented")

    # apply the first regex that matches
    for (regexFrom, regexTo) in changes:
        regexFrom += "$"
        if re.search(regexFrom, verb) is not None:
            return re.sub(regexFrom, regexTo, verb)
    return verb

# -----------------------------------------------------------------------------

# supported grammatical moods, tenses, voices, numbers and persons
# indicative, imperative, conditional, potential
MOODS   = ("ind", "con", "pot", "imp")
TENSES  = ("pre", "pst", "per")   # present, past, perfect
VOICES  = ("act", "pss")          # active, passive
NUMBERS = ("sg",  "pl")           # singular, plural
PERSONS = ("1", "2", "3")         # first, second, third

_NUMBER_PERSON_ENDINGS = {
    ("sg", "1"): "n",
    ("sg", "2"): "t",
    ("pl", "1"): "mme",
    ("pl", "2"): "tte",
}

def _get_active_forms(inflected, tense, number, person):
    # generate verbs with case/number endings

    # use "a" or "ä" in -A endings?
    aOrAuml = "a" if re.search(r"^[^aou]+$", inflected[0]) is None else "ä"

    if person == "3":
        if number == "sg":
            if tense == "pre":
                for i in inflected:
                    if re.search("[aeiouyäö]i$", i) is not None:
                        yield i
                    else:
                        yield i + i[-1]
            else:
                yield from inflected
        else:
            yield from (i + "v" + aOrAuml + "t" for i in inflected)
    else:
        yield from (
            i + _NUMBER_PERSON_ENDINGS[(number, person)] for i in inflected
        )

def conjugate_verb_specific(
    verb, conj, consGrad, mood, tense, voice, number, person
):
    """Get inflected forms of a Finnish verb.
    verb:     a verb in 1st infinitive (str)
    conj:     Kotus conjugation (52-76)
    consGrad: does consonant gradation apply in certain cases/numbers? (bool)
    mood:     one of MOODS
    tense:    one of TENSES
    voice:    one of VOICES
    number:   one of NUMBERS or None
    person:   one of PERSONS or None
    generate: inflected forms of verb"""

    assert isinstance(verb, str)
    assert 52 <= conj <= 76
    assert isinstance(consGrad, bool)
    assert mood   in MOODS
    assert tense  in TENSES
    assert voice  in VOICES
    assert number in NUMBERS or number is None
    assert person in PERSONS or person is None
    assert mood == "ind" or tense == "pre"
    assert mood != "imp" or voice == "act"
    assert (voice == "pss") == (number is None)
    assert (tense == "per") == (person is None)
    assert mood != "imp" or number != "sg" or person != "1"

    # add variant (tupakoida -> tupakoitse)
    variants = [verb]
    if conj == 68:
        variants.append(re.sub("d[aä]$", "tse", verb))
    #print("variants:", variants)

    # apply consonant gradation
    if consGrad:
        inflected = []
        for variant in variants:
            inflected.extend(_consonant_gradation_main(
                variant, conj, mood, tense, voice, person
            ))
    else:
        inflected = variants.copy()
    del variants
    #print("after cons. grad.:", inflected)

    # change ending (without adding case/number endings)
    inflected = list(
        _change_ending(i, conj, mood, tense, voice) for i in inflected
    )

    inflected = tuple(inflected)
    #print(f"{inflected=} {conj=} {consGrad=}")

    # append case/number endings and generate verbs
    yield from _get_active_forms(inflected, tense, number, person)

def conjugate_verb(verb, mood, tense, voice, number=None, person=None):
    """Get inflected forms of a Finnish verb. Autodetects conjugation(s) and
    whether consonant gradation applies.
    verb:   a verb in 1st infinitive
    mood:   one of MOODS
    tense:  one of TENSES
    voice:  one of VOICES
    number: one of NUMBERS or None
    person: one of PERSONS or None
    return: set of inflected forms (may be empty if the verb was not
            recognized)"""

    assert isinstance(verb, str)
    assert mood   in MOODS
    assert tense  in TENSES
    assert voice  in VOICES
    assert number in NUMBERS or number is None
    assert person in PERSONS or person is None
    assert mood == "ind" or tense == "pre"
    assert mood != "imp" or voice == "act"
    assert (voice == "pss") == (number is None)
    assert (tense == "per") == (person is None)
    assert mood != "imp" or number != "sg" or person != "1"

    results = set()

    for conj in get_conjugations(verb):
        consGrad = get_consonant_gradation(verb, conj)
        results.update(
            conjugate_verb_specific(
                verb, conj, consGrad, mood, tense, voice, number, person
            )
        )

    return results

# all supported combinations of mood, tense, voice, number and person
_ALL_FORMS = (
    ("ind", "pre", "act", "sg", "1"),
    ("ind", "pre", "act", "sg", "2"),
    ("ind", "pre", "act", "sg", "3"),
    ("ind", "pre", "act", "pl", "1"),
    ("ind", "pre", "act", "pl", "2"),
    ("ind", "pre", "act", "pl", "3"),
    ("ind", "pst", "act", "sg", "1"),
    ("ind", "pst", "act", "sg", "2"),
    ("ind", "pst", "act", "sg", "3"),
    ("ind", "pst", "act", "pl", "1"),
    ("ind", "pst", "act", "pl", "2"),
    ("ind", "pst", "act", "pl", "3"),
)

def main():
    if len(sys.argv) not in (2, 5, 6, 7):
        sys.exit(
            "Conjugate a Finnish verb. Arguments: VERB [MOOD TENSE VOICE "
            "[NUMBER [PERSON]]]. Moods: " + "/".join(MOODS) + ". Tenses: "
            + "/".join(TENSES) + ". Voices: " + "/".join(VOICES) + ". "
            "Numbers: " + "/".join(NUMBERS) + ". Persons: "
            + "/".join(PERSONS) + ". If 1 argument only, print all supported "
            "combinations."
        )

    verb = sys.argv[1]
    if len(sys.argv) >= 5:
        (mood, tense, voice) = sys.argv[2:5]
        allForms = False
    else:
        allForms = True
    number = sys.argv[5] if len(sys.argv) >= 6 else None
    person = sys.argv[6] if len(sys.argv) >= 7 else None

    if not allForms:
        if mood not in MOODS:
            sys.exit("Invalid mood.")
        if tense not in TENSES:
            sys.exit("Invalid tense.")
        if voice not in VOICES:
            sys.exit("Invalid voice.")
        if number is not None and number not in NUMBERS:
            sys.exit("Invalid number.")
        if person is not None and person not in PERSONS:
            sys.exit("Invalid person.")

        if mood != "ind" and tense != "pre":
            sys.exit(
                "Can't have past/perfect tense with conditional/potential/"
                "imperative mood."
            )
        if mood == "imp" and voice == "pss":
            sys.exit("Can't have passive voice with imperative mood.")
        if (voice == "pss") != (number is None):
            sys.exit(
                "Number required in active voice, forbidden in passive voice."
            )
        if (tense == "per") != (person is None):
            sys.exit(
                "Person required in present/past tense, forbidden in perfect "
                "tense."
            )
        if mood == "imp" and number == "sg" and person == "1":
            sys.exit("1st person singular forbidden with imperative mood.")

    forms = _ALL_FORMS if allForms else ((mood, tense, voice, number, person),)

    for form in forms:
        conjugatedVerbs = set(conjugate_verb(verb, *form))
        if not conjugatedVerbs:
            sys.exit("Unrecognized verb.")
        print("-".join(form) + ": " + ", ".join(sorted(conjugatedVerbs)))

if __name__ == "__main__":
    main()
