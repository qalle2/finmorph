import collections, re, sys
import countsyll, util

INTRO = """\
A table of noun/verb counts by declension/conjugation, syllable count and ending.
This file was generated automatically.

Columns:
    Conj  = Kotus declension/conjugation
    Word  = a representative noun/verb in the declension/conjugation
    1syll = number of monosyllabic words
    2syll = number of disyllabic words
    3syll = number of trisyllabic words
    4syll = number of quadrisyllabic and longer words
    -VV   = number of words that end with two vowels
    -CV   = number of words that end with a consonant and a vowel
    -C    = number of words that end with a consonant
    Total = total number of words (= 1syll + 2syll + 3syll + 4syll = -VV + -CV + -C)

The last row (TOTAL) has the number of words for all declensions/conjugations combined.

Conj Word      1syll 2syll 3syll 4syll   -VV   -CV    -C Total
---- --------- ----- ----- ----- ----- ----- ----- ----- -----"""

# regexes for word endings
RE_TWO_VOWEL = re.compile(
    "[aeiouyäöéû]{2} - ?$", re.IGNORECASE | re.VERBOSE
)
RE_CONS_VOWEL = re.compile(
    "[^aeiouyäöéû][aeiouyäöéû] -? $", re.IGNORECASE | re.VERBOSE
)

# noun declensions / verb conjugations and sample words
CONJUGATIONS = {
    0: "(other)",
    # nouns
    1: "valo", 2: "palvelu", 3: "valtio", 4: "laatikko",
    5: "risti", 6: "paperi", 7: "ovi", 8: "nalle",
    9: "kala", 10: "koira", 11: "omena", 12: "kulkija",
    13: "katiska", 14: "solakka", 15: "korkea", 16: "vanhempi",
    17: "vapaa", 18: "maa", 19: "suo", 20: "filee",
    21: "rosé", 22: "parfait", 23: "tiili", 24: "uni",
    25: "toimi", 26: "pieni", 27: "käsi", 28: "kynsi",
    29: "lapsi", 30: "veitsi", 31: "kaksi", 32: "sisar",
    33: "kytkin", 34: "onneton", 35: "lämmin", 36: "sisin",
    37: "vasen", 38: "nainen", 39: "vastaus", 40: "kalleus",
    41: "vieras", 42: "mies", 43: "ohut", 44: "kevät",
    45: "kahdeksas", 46: "tuhat", 47: "kuollut", 48: "hame",
    49: "askel(e)",
    # verbs
    52: "sanoa", 53: "muistaa", 54: "huutaa", 55: "soutaa",
    56: "kaivaa", 57: "saartaa", 58: "laskea", 59: "tuntea",
    60: "lähteä", 61: "sallia", 62: "voida", 63: "saada",
    64: "juoda", 65: "käydä", 66: "rohkaista", 67: "tulla",
    68: "tupakoida", 69: "valita", 70: "juosta", 71: "nähdä",
    72: "vanheta", 73: "salata", 74: "katketa", 75: "selvitä",
    76: "taitaa", 77: "kumajaa", 78: "kaikaa",
}

if len(sys.argv) != 2:
    sys.exit(
        "Print a table of noun/verb counts by declension/conjugation, syllable count and ending. "
        "Argument: CSV file with words (no compounds)."
    )

# word counts by declension/conjugation and ending
totalCnts = collections.Counter()
monoSyllCnts = collections.Counter()
diSyllCnts = collections.Counter()
triSyllCnts = collections.Counter()
quadSyllCnts = collections.Counter()
twoVwlEndCnts = collections.Counter()
cnsVwlEndCnts = collections.Counter()
cnsEndCnts = collections.Counter()

for line in util.read_lines(sys.argv[1]):
    fields = line.split(",")
    word = fields[0]
    conjugations = {int(c, 10) for c in fields[1:]} & set(CONJUGATIONS)
    conjugations = conjugations if conjugations else {0}  # other/unknown

    totalCnts.update(conjugations)

    syllCnt = countsyll.count_syllables(word)
    if syllCnt == 1:
        monoSyllCnts.update(conjugations)
    elif syllCnt == 2:
        diSyllCnts.update(conjugations)
    elif syllCnt == 3:
        triSyllCnts.update(conjugations)
    else:
        quadSyllCnts.update(conjugations)

    if RE_TWO_VOWEL.search(word) is not None:
        twoVwlEndCnts.update(conjugations)
    elif RE_CONS_VOWEL.search(word) is not None:
        cnsVwlEndCnts.update(conjugations)
    else:
        cnsEndCnts.update(conjugations)

counters = (
    monoSyllCnts,
    diSyllCnts,
    triSyllCnts,
    quadSyllCnts,
    twoVwlEndCnts,
    cnsVwlEndCnts,
    cnsEndCnts,
    totalCnts,
)

print(INTRO)
for conj in CONJUGATIONS:
    print(f"{conj:4} {CONJUGATIONS[conj]:9}", " ".join(f"{c[conj]:5}" for c in counters))
print("     TOTAL    ", " ".join(f"{sum(c.values()):5}" for c in counters))
