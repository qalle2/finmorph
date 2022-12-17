"""Conjugate a Finnish verb. Under construction."""

import re, sys
from verb_consgrad import get_consonant_gradation
from verbconj import get_conjugations

# - C = any consonant, V = any vowel, A = a/ä, O = o/ö, U = u/y
# - conjugations (52-76) are from Kotus

# enumerate internal names for grammatical moods, tenses, voices, numbers and
# persons
(
    M_IND, M_CON, M_POT, M_IMP,
    T_PRE, T_PST, T_PER,
    V_ACT, V_PSS,
    N_SG, N_PL,
    P_1, P_2, P_3,
) = range(14)

# group moods etc.
# indicative, conditional, potential, imperative
MOODS   = (M_IND, M_CON, M_POT, M_IMP)
TENSES  = (T_PRE, T_PST, T_PER)  # present, past, perfect
VOICES  = (V_ACT, V_PSS)         # active, passive
NUMBERS = (N_SG,  N_PL)          # singular, plural
PERSONS = (P_1, P_2, P_3)        # first, second, third

# names of moods etc. for input/output
ITEM_NAMES = {
    M_IND: "ind",
    M_CON: "con",
    M_POT: "pot",
    M_IMP: "imp",
    T_PRE: "pre",
    T_PST: "pst",
    T_PER: "per",
    V_ACT: "act",
    V_PSS: "pss",
    N_SG:  "sg",
    N_PL:  "pl",
    P_1:   "1",
    P_2:   "2",
    P_3:   "3",
}

# -----------------------------------------------------------------------------

# consonant gradation is weak to strong in these conjugations
_CONJS_STRENGTHEN = frozenset((
    # rohkaista, tulla, vanheta, salata, katketa, selvitä
    66, 67, 72, 73, 74, 75
))

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

_CONS_GRAD_EXCEPTIONS = {
    # the only conjugation 66 verbs with consonant gradation
    "häväistä":  "häpäistä",
    "rangaista": "rankaista",
    "vavista":   "vapista",
    #
    "digata": "diggata",
    "hylkiä": "hyljiä",
    "lobata": "lobbata",
}

def _consonant_gradation(verb, strengthen=False):
    # apply consonant gradation to the verb
    # strengthen: False = strong to weak, True = weak to strong

    if verb in _CONS_GRAD_EXCEPTIONS:
        return _CONS_GRAD_EXCEPTIONS[verb]

    regexes = _CONS_GRAD_STRENGTHEN if strengthen else _CONS_GRAD_WEAKEN
    for (reFrom, reTo) in regexes:
        if re.search(reFrom, verb) is not None:
            return re.sub(reFrom, reTo, verb)
    sys.exit(f"Failed to apply consonant gradation: {verb=}, {strengthen=}")

def _consonant_gradation_main(verb, conj, mood, tense, voice, person):
    # apply consonant gradation (before doing anything else)

    strengthen = conj in _CONJS_STRENGTHEN
    if (
        mood == M_IND and tense in (T_PRE, T_PST) and voice == V_ACT
        and (person != P_3 or strengthen)
        or
        mood == M_CON and voice == V_ACT and strengthen
    ):
        return _consonant_gradation(verb, strengthen)
    return verb

# -----------------------------------------------------------------------------

def _get_variants(verb, infl, conj, mood, tense):
    # return variants of verb in a tuple
    # infl: verb with consonant gradation, e.g. soutaa or soudaa

    if mood == M_IND and tense == T_PST:
        if conj == 55:
            # soutaa
            return (infl, re.sub("t(aa|ää)$", r"s\1", verb))
        if conj == 57:
            # saartaa
            return (re.sub("aa$", r"o", infl), re.sub("taa$", "s", verb))
        if conj == 60:
            # lähteä
            return (infl, "läks")

    if mood == M_CON:
        if conj == 74:
            # katketa
            return (infl, re.sub("t([aä])$", r"\1", infl))

    return (infl,)  # no change

# -----------------------------------------------------------------------------

# rules for changing endings of verbs
# - format: conjugation: (regex_from, regex_to)
# - "$" will be appended to regex_from
# - consonant gradation has already been applied
# - variant forms have already been added
# - conditional/number/person endings will be added afterwards
# - for clarity, avoid making changes here that need to be undone later

_CHANGES_IND_PRE_ACT = {
    52: ("[aä]",      ""),     # sanoa
    53: ("[aä]",      ""),     # muistaa
    54: ("[aä]",      ""),     # huutaa
    55: ("[aä]",      ""),     # soutaa
    56: ("a",         ""),     # kaivaa
    57: ("a",         ""),     # saartaa
    58: ("[aä]",      ""),     # laskea
    59: ("a",         ""),     # tuntea
    60: ("ä",         ""),     # lähteä
    61: ("[aä]",      ""),     # sallia
    62: ("d[aä]",     ""),     # voida
    63: ("d[aä]",     ""),     # saada
    64: ("d[aä]",     ""),     # juoda
    65: ("d[aä]",     ""),     # käydä
    66: ("t[aä]",     "e"),    # rohkaista
    67: ("[lnr][aä]", "e"),    # tulla
    68: ("d[aä]",     ""),     # tupakoida
    69: ("t[aä]",     "tse"),  # valita
    70: ("st[aä]",    "kse"),  # juosta
    # 71 nähdä
    72: ("t[aä]",     "ne"),   # vanheta
    73: ("t([aä])",   r"\1"),  # salata
    74: ("t([aä])",   r"\1"),  # katketa
    75: ("t([aä])",   r"\1"),  # selvitä
    76: ("[aä]",      ""),     # taitaa
}

_CHANGES_PAST_COND = {
    # common to ind-pst-act and con-pre-act; a temporary dict
    52: ("[aä]",       ""),    # sanoa
    58: ("e[aä]",      ""),    # laskea
    60: ("eä",         ""),    # lähteä
    61: ("i[aä]",      ""),    # sallia
    62: ("id[aä]",     ""),    # voida
    63: ("[aäy]d[aä]", ""),    # saada
    64: ("[iuy]([eoö])d[aä]", r"\1"),  # juoda
    65: ("ydä",        "v"),   # käydä
    66: ("t[aä]",      ""),    # rohkaista
    67: ("[lnr][aä]",  ""),    # tulla
    68: ("id[aä]",     ""),    # tupakoida
    69: ("t[aä]",      "ts"),  # valita
    70: ("st[aä]",     "ks"),  # juosta
    # 71 nähdä
    72: ("t[aä]",      "n"),   # vanheta
}
_CHANGES_IND_PST_ACT = _CHANGES_PAST_COND | {
    53: ("(aa|ää)",     ""),   # muistaa
    54: ("[st](aa|ää)", "s"),  # huutaa
    55: ("(aa|ää)",     ""),   # soutaa
    56: ("aa",          "o"),  # kaivaa
    # 57 saartaa
    59: ("tea",         "s"),  # tuntea
    73: ("t[aä]",       "s"),  # salata
    74: ("t[aä]",       "s"),  # katketa
    75: ("t[aä]",       "s"),  # selvitä
    76: ("t(aa|ää)",    "s"),  # taitaa
}
_CHANGES_CON_PRE_ACT = _CHANGES_PAST_COND | {
    53: ("[aä]",    ""),     # muistaa
    54: ("[aä]",    ""),     # huutaa
    55: ("[aä]",    ""),     # soutaa
    56: ("a",       ""),     # kaivaa
    57: ("a",       ""),     # saartaa
    59: ("ea",      ""),     # tuntea
    73: ("t[aä]",   ""),     # salata
    74: ("t[aä]",   ""),     # katketa
    75: ("t([aä])", r"\1"),  # selvitä
    76: ("[aä]",    ""),     # taitaa
}
del _CHANGES_PAST_COND

def _change_ending(verb, conj, mood, tense, voice):
    # change the ending of the verb (before applying consonant gradation or
    # adding number/person endings)

    # get regexes to apply
    if mood == M_IND and voice == V_ACT:
        if tense == T_PRE:
            changes = _CHANGES_IND_PRE_ACT.get(conj, None)
        elif tense == T_PST:
            changes = _CHANGES_IND_PST_ACT.get(conj, None)
        else:
            sys.exit("not implemented")
    elif mood == M_CON and voice == V_ACT:
        changes = _CHANGES_CON_PRE_ACT.get(conj, ())
    else:
        sys.exit("not implemented")

    if changes is None:
        return verb

    # apply the regex
    (regexFrom, regexTo) = changes
    regexFrom += "$"
    if re.search(regexFrom, verb) is not None:
        return re.sub(regexFrom, regexTo, verb)
    return verb

# -----------------------------------------------------------------------------

_NUMBER_PERSON_ENDINGS = {
    (N_SG, P_1): "n",
    (N_SG, P_2): "t",
    (N_PL, P_1): "mme",
    (N_PL, P_2): "tte",
}

_IS_FINAL_VOWEL_LONG = re.compile(
    "(aa|ee|ii|oo|uu|yy|ää|öö|[aeouyäö]i|ie|uo|yö)$"
)

def _get_active_forms(inflected, mood, tense, number, person):
    # generate verbs with case/number endings

    # use "a" or "ä" in -A endings?
    aOrAuml = "a" if re.search(r"^[^aou]+$", inflected[0]) is None else "ä"

    if mood == M_IND and tense == T_PRE and number == N_SG and person == P_3:
        # lengthen final vowel if possible
        yield from (
            i + i[-1] if _IS_FINAL_VOWEL_LONG.search(i) is None else i
            for i in inflected
        )
    else:
        if person == P_3:
            ending = "" if number == N_SG else "v" + aOrAuml + "t"
        else:
            ending = _NUMBER_PERSON_ENDINGS[(number, person)]
        yield from (i + ending for i in inflected)

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
    assert mood == M_IND or tense == T_PRE
    assert mood != M_IMP or voice == V_ACT
    assert (voice == V_PSS) == (number is None)
    assert (tense == T_PER) == (person is None)
    assert mood != M_IMP or number != N_SG or person != P_1

    if conj == 68:
        # tupakoida: recursively get the variant "tupakoitsea", a conjugation
        # 58 (lukea) verb; also proceed with current verb
        yield from conjugate_verb_specific(
            re.sub("d([aä])$", r"tse\1", verb),
            58, consGrad, mood, tense, voice, number, person
        )
    elif conj == 71:
        # nähdä: conjugate like "näkeä", a conjugation 58 (lukea) verb
        verb = re.sub("hdä$", "keä", verb)
        conj = 58
        consGrad = True

    # apply consonant gradation
    if consGrad:
        inflected = _consonant_gradation_main(
            verb, conj, mood, tense, voice, person
        )
    else:
        inflected = verb

    # get variants in a tuple, e.g. (lähdeä, läksi)
    inflected = _get_variants(verb, inflected, conj, mood, tense)

    # change ending (without adding case/number endings)
    inflected = tuple(
        _change_ending(i, conj, mood, tense, voice) for i in inflected
    )

    # add the ending that's common to all conjugations
    if mood == M_IND and tense == T_PST and voice == V_ACT:
        inflected = tuple(i + "i" for i in inflected)
    elif mood == M_CON and tense == T_PRE and voice == V_ACT:
        inflected = tuple(i + "isi" for i in inflected)

    #print(f"{inflected=} {conj=} {consGrad=}")

    # append case/number endings and generate verbs
    yield from _get_active_forms(inflected, mood, tense, number, person)

# verbs with optional consonant gradation
_OPTIONAL_CONS_GRAD = frozenset((
    "halvata", "kevetä", "kimmota", "lohkoa", "pokata", "pykiä", "raakata",
    "sulkia", "tavata"
))

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
    assert mood == M_IND or tense == T_PRE
    assert mood != M_IMP or voice == V_ACT
    assert (voice == V_PSS) == (number is None)
    assert (tense == T_PER) == (person is None)
    assert mood != M_IMP or number != N_SG or person != P_1

    results = set()

    for conj in get_conjugations(verb):
        if verb in _OPTIONAL_CONS_GRAD:
            consGrads = (False, True)
        elif verb in ("digata", "lobata"):
            consGrads = (True,)
        else:
            consGrads = (get_consonant_gradation(verb, conj),)

        for consGrad in consGrads:
            results.update(
                conjugate_verb_specific(
                    verb, conj, consGrad, mood, tense, voice, number, person
                )
            )

    return results

# all supported combinations of mood, tense, voice, number and person
ALL_FORMS = (
    (M_IND, T_PRE, V_ACT, N_SG, P_1),
    (M_IND, T_PRE, V_ACT, N_SG, P_2),
    (M_IND, T_PRE, V_ACT, N_SG, P_3),
    (M_IND, T_PRE, V_ACT, N_PL, P_1),
    (M_IND, T_PRE, V_ACT, N_PL, P_2),
    (M_IND, T_PRE, V_ACT, N_PL, P_3),
    (M_IND, T_PST, V_ACT, N_SG, P_1),
    (M_IND, T_PST, V_ACT, N_SG, P_2),
    (M_IND, T_PST, V_ACT, N_SG, P_3),
    (M_IND, T_PST, V_ACT, N_PL, P_1),
    (M_IND, T_PST, V_ACT, N_PL, P_2),
    (M_IND, T_PST, V_ACT, N_PL, P_3),
    (M_CON, T_PRE, V_ACT, N_SG, P_1),
    (M_CON, T_PRE, V_ACT, N_SG, P_2),
    (M_CON, T_PRE, V_ACT, N_SG, P_3),
    (M_CON, T_PRE, V_ACT, N_PL, P_1),
    (M_CON, T_PRE, V_ACT, N_PL, P_2),
    (M_CON, T_PRE, V_ACT, N_PL, P_3),
)

def _items_to_str(items):
    # format a list of e.g. moods
    return "/".join(ITEM_NAMES[i] for i in items)

def main():
    if len(sys.argv) not in (2, 5, 6, 7):
        sys.exit(
            "Conjugate a Finnish verb. "
            "Arguments: VERB [MOOD TENSE VOICE [NUMBER [PERSON]]]. "
            f"Moods: {_items_to_str(MOODS)}. "
            f"Tenses: {_items_to_str(TENSES)}. "
            f"Voices: {_items_to_str(VOICES)}. "
            f"Numbers: {_items_to_str(NUMBERS)}. "
            f"Persons: {_items_to_str(PERSONS)}. "
            "If 1 argument only, print all supported combinations."
        )

    verb = sys.argv[1]
    (mood, tense, voice, number, person) \
    = sys.argv[2:] + (7 - len(sys.argv)) * [None]

    # "ind" -> M_IND etc.
    argToItem = dict((v, k) for (k, v) in ITEM_NAMES.items())
    try:
        (mood, tense, voice, number, person) = (
            None if a is None else argToItem[a]
            for a in (mood, tense, voice, number, person)
        )
    except KeyError:
        sys.exit("Unrecognized argument (mood/tense/etc.).")
    del argToItem

    if mood is None:
        formsToPrint = ALL_FORMS
    else:
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

        if mood != M_IND and tense != T_PRE:
            sys.exit(
                "Can't have past/perfect tense with conditional/potential/"
                "imperative mood."
            )
        if mood == M_IMP and voice == V_PSS:
            sys.exit("Can't have passive voice with imperative mood.")
        if (voice == V_PSS) != (number is None):
            sys.exit(
                "Number required in active voice, forbidden in passive voice."
            )
        if (tense == T_PER) != (person is None):
            sys.exit(
                "Person required in present/past tense, forbidden in perfect "
                "tense."
            )
        if mood == M_IMP and number == N_SG and person == P_1:
            sys.exit("1st person singular forbidden with imperative mood.")

        formsToPrint = ((mood, tense, voice, number, person),)

    for form in formsToPrint:
        # sort variants by length
        conjugatedVerbs = sorted(conjugate_verb(verb, *form))
        conjugatedVerbs.sort(key=lambda v: len(v))
        if not conjugatedVerbs:
            sys.exit("Unrecognized verb.")
        print(
            "-".join(ITEM_NAMES[i] for i in form) + ": "
            + ", ".join(conjugatedVerbs)
        )

if __name__ == "__main__":
    main()
