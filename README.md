# finmorph
*This project has been moved to [Codeberg](https://codeberg.org/qalle/finmorph). This version will no longer be updated.*

Tools regarding the morphology of the Finnish language.

I have used [the Finnish wordlist by Kotus](https://kaino.kotus.fi/sanat/nykysuomi/) when creating the programs.

## Table of contents

* [File formats](#file-formats)
* [Programs interesting to the end user](#programs-interesting-to-the-end-user)
* [Programs less interesting to the end user](#programs-less-interesting-to-the-end-user)
* [Programs even less interesting to the end user](#programs-even-less-interesting-to-the-end-user)
* [Text files](#text-files)

## File formats

All files in this project use UTF-8 character encoding and Unix newlines.

CSV file format used in this project:
* field separator: comma (`,`)
* no fields are quoted
* no empty fields
* types of fields: words (strings), declensions/conjugations (integers)
* lines in `plurals.csv`: two words (e.g. `häät,hää`)
* lines in all other CSV files: one word and zero or more declensions/conjugations (e.g. `ahtaus,39,40`)

## Programs interesting to the end user

### conjugate_verb.py
```
Conjugate a Finnish verb. Arguments: VERB [MOOD TENSE VOICE [NUMBER [PERSON]]].
Moods: ind/con/pot/imp. Tenses: pre/pst/per. Voices: act/pss. Numbers: sg/pl.
Persons: 1/2/3. If 1 argument only, print all supported combinations.
```

Note: perfect tense and passive voice are not supported yet; only these
combinations of mood/tense/voice are supported:
* indicative present active
* indicative past active
* conditional present active
* potentional present active
* imperative present active

Example:
```
$ python3 conjugate_verb.py "keritä" ind pre act sg 1
ind-pre-act-sg-1: kerkiän, keritsen

$ python3 conjugate_verb.py "soutaa"
ind-pre-act-sg-1: soudan
ind-pre-act-sg-2: soudat
ind-pre-act-sg-3: soutaa
ind-pre-act-pl-1: soudamme
ind-pre-act-pl-2: soudatte
ind-pre-act-pl-3: soutavat
ind-pst-act-sg-1: soudin, sousin
ind-pst-act-sg-2: soudit, sousit
ind-pst-act-sg-3: sousi, souti
ind-pst-act-pl-1: soudimme, sousimme
ind-pst-act-pl-2: souditte, sousitte
ind-pst-act-pl-3: sousivat, soutivat
con-pre-act-sg-1: soutaisin
con-pre-act-sg-2: soutaisit
con-pre-act-sg-3: soutaisi
con-pre-act-pl-1: soutaisimme
con-pre-act-pl-2: soutaisitte
con-pre-act-pl-3: soutaisivat
pot-pre-act-sg-1: soutanen
pot-pre-act-sg-2: soutanet
pot-pre-act-sg-3: soutanee
pot-pre-act-pl-1: soutanemme
pot-pre-act-pl-2: soutanette
pot-pre-act-pl-3: soutanevat
imp-pre-act-sg-2: souda
imp-pre-act-sg-3: soutakoon
imp-pre-act-pl-1: soutakaamme
imp-pre-act-pl-2: soutakaa
imp-pre-act-pl-3: soutakoot
```

### decline_noun.py
```
Decline a Finnish noun. Arguments: NOUN [CASE NUMBER]. Cases: nom, gen, par,
ess, tra, ine, ela, ill, ade, abl, all, abe, ins. Numbers: sg, pl. If case &
number omitted, print all supported combinations.
```

Note: instructive singular and comitative are not supported.

Examples:
```
$ python3 decline_noun.py "kuusi" gen sg
GenSg: kuuden, kuusen

$ python3 decline_noun.py "kuusi"
NomSg: kuusi
NomPl: kuudet, kuuset
GenSg: kuuden, kuusen
GenPl: kuusien, kuusten, kuutten
ParSg: kuusta, kuutta
ParPl: kuusia
EssSg: kuusena, kuutena
EssPl: kuusina
TraSg: kuudeksi, kuuseksi
TraPl: kuusiksi
IneSg: kuudessa, kuusessa
InePl: kuusissa
ElaSg: kuudesta, kuusesta
ElaPl: kuusista
IllSg: kuuseen, kuuteen
IllPl: kuusiin
AdeSg: kuudella, kuusella
AdePl: kuusilla
AblSg: kuudelta, kuuselta
AblPl: kuusilta
AllSg: kuudelle, kuuselle
AllPl: kuusille
AbeSg: kuudetta, kuusetta
AbePl: kuusitta
InsPl: kuusin
```

### find-partial-homonyms.py
Find partially homonymous inflected nouns and verbs. Slow.

`partial-homonyms.txt` was generated with this program.

### inflected_by_length.py
Print lemma and inflected forms of nouns and verbs with specified length.
Arguments: minimumLength maximumLength

Example:
```
$ python3 inflected_by_length.py 22 22
kansalaisuudettomuudet
suunnittelemattomuudet
...
```

### noun_consgrad.py
Argument: a Finnish noun (including adjectives/pronouns/numerals, excluding
compounds) in nominative singular. Print the Kotus declension(s) (1-49) and
whether consonant gradation applies.

Example:
```
$ python3 noun_consgrad.py "kuusi"
Declension 24 (like "un|i, -en, -ien/-ten, -ta, -ia, -een, -iin") without
consonant gradation
Declension 27 (like "kä|si, -den, -sien/-tten, -ttä, -siä, -teen, -siin")
without consonant gradation
```

Needs `noundecl.py` and `countsyll.py`. Can be tested with `test-nounverb.py`.

### noundecl.py
Argument: a Finnish noun (including adjectives/pronouns/numerals, excluding
compounds) in nominative singular. Print the Kotus declension(s) (1-49).

Example:
```
$ python3 noundecl.py "kuusi"
Declension 24 (like "un|i, -en, -ien/-ten, -ta, -ia, -een, -iin")
Declension 27 (like "kä|si, -den, -sien/-tten, -ttä, -siä, -teen, -siin")
```

Needs `countsyll.py`. Can be tested with `test-nounverb.py`.

### verb_consgrad.py
Argument: a Finnish verb (not a compound) in the infinitive. Print the Kotus
conjugation(s) (52-76) and whether consonant gradation applies.

Example:
```
$ python3 verb_consgrad.py "keritä"
Conjugation 69 (like "vali|ta, -tsen, -tsi, -tsisi, -tkoon, -nnut, -ttiin")
without consonant gradation
Conjugation 75 (like "selvi|tä, -än, -si, -äisi, -tköön, -nnyt, -ttiin") with
consonant gradation
```

Needs `verbconj.py`. Can be tested with `test-nounverb.py`.

### verbconj.py
Argument: a Finnish verb (not a compound) in the infinitive. Print the Kotus
conjugation(s) (52-76).

Example:
```
$ python3 verbconj.py "keritä"
Conjugation 69 (like "vali|ta, -tsen, -tsi, -tsisi, -tkoon, -nnut, -ttiin")
Conjugation 75 (like "selvi|tä, -än, -si, -äisi, -tköön, -nnyt, -ttiin")
```

Needs `countsyll.py`. Can be tested with `test-nounverb.py`.

### countsyll.py
Count the number of syllables in a Finnish word. Argument: word

Example:
```
$ python3 countsyll.py "liioitella"
Syllables: 4 or more, or the word is unknown
```

### splitcomp.py
Split a Finnish compound. Argument: compound to split.

Example:
```
$ python3 splitcomp.py "ylivoimamaali"
yli_voima_maali
```

Needs `generated-lists/nonfinals.txt` and `generated-lists/finals.csv` which
can be generated with `extract.sh`.

TODO: make the program more space efficient (those word lists are more than a
hundred kilobytes together).

## Programs less interesting to the end user

### extract.sh
Converts the Kotus XML file (link above) into CSV files that are needed by the
other programs. Warning: overwrites the files listed below.

Note: before running this script, extract the Kotus XML file to the same
directory as this project.

Creates the subdirectory `generated-lists/` and generates these files under it:
* `words-orig.csv`: the original words (no leading/trailing apostrophes/hyphens/spaces) (~94,000 words)
* `words.csv`: words without plurals or compounds but with singular forms of plurals and finals of compounds (~41,000 words)
  * `nouns.csv`: nouns (Kotus declensions 1&ndash;49) from `words.csv` (~26,000 words)
    * `nouns-1syll.csv`: monosyllabic nouns
    * `nouns-2syll.csv`: disyllabic nouns
    * `nouns-3syll.csv`: trisyllabic nouns
    * `nouns-4syll.csv`: quadrisyllabic and longer nouns
  * `verbs.csv`: verbs (Kotus conjugations 52&ndash;76) from `words.csv` (~9,400 words)
    * `verbs-1syll.csv`: monosyllabic verbs
    * `verbs-2syll.csv`: disyllabic verbs
    * `verbs-3syll.csv`: trisyllabic verbs
    * `verbs-4syll.csv`: quadrisyllabic and longer verbs
* `words-consgrad.csv`: like `words.csv` but only the words to which consonant gradation applies (~11,000 words)
* `finals.csv`: words that occur as final parts of compounds (and possibly non-finally or alone) (~8,400 words)
* `nonfinals.txt`: words that occur as non-final parts of compounds (not finally but possibly alone) (~5,300 words)
* `compositives.txt`: words that occur as non-final parts of compounds (not finally or alone) (~2,900 words)

Also generates `stats-nounverb.txt` under the current directory (see [text files](#text-files)).

### test-conjugate_verb.py
Test `conjugate_verb.py`. No arguments.

### test-decline_noun.py
Test `decline_noun.py`. No arguments.

### test-nounverb.py
```
Argument: which program to test ('n'=noundecl.py, 'v'=verbconj.py,
'ng'=noun_consgrad.py, 'vg'=verb_consgrad.py).
```

Needs files created by `extract.sh`.

### test-splitcomp.py
Test `splitcomp.py` against known single words and compounds.

Requires `generated-lists/words.csv` which can be generated with `extract.sh`.

## Programs even less interesting to the end user

These are only meant to be used by `extract.sh`.

### xml2csv.py
Read Kotus XML file, print distinct words and their declensions/conjugations
(0-2) in CSV format. Arguments: XML file, which words ('a' = all, 'g' = only
those that consonant gradation applies to).

### finals.py
Get words that occur as finals of compounds. Print them and their
declensions/conjugations in CSV format. Arguments: wordCsvFile compoundListFile

### csv-combine.py
Arguments: one or more CSV files. For each distinct word, print a CSV line with
all declensions/conjugations occurring with that word in the files.

### replace-plurals.py
Arguments: CSV file with words and declensions/conjugations, CSV file with
plurals and singulars. Print words and declensions/conjugations in CSV format,
with plurals replaced with singulars.

### strip-compounds.py
Arguments: CSV file with words and declensions/conjugations, list file with
compounds. Print CSV lines without those that contain a compound.

### filter-by-conjugation.py
Arguments: CSV file with words and declensions/conjugations, first
declension/conjugation, last declension/conjugation. Print lines that contain
declensions/conjugations within that range.

### filter-by-syllcnt.py
Arguments: CSV file, syllable count (1-4; 4=4 or more). Print lines containing
a word with that many syllables.

### nonfinals.py
Print words that only occur as non-final parts of compounds (not final).
Argument: compound list file

### compositives.py
Print words that only occur as non-final parts of compounds (not final or
alone). Arguments: compound list file, word CSV file

### stats-nounverb.py
Print a table of noun/verb counts by declension/conjugation, syllable count and
ending. Argument: CSV file with words (no compounds).

## Text files

### compounds.txt
A list of compounds on the Kotus word list. Creating this list involved a lot of manual work.

Notes:
* One compound per line.
* The individual words of each compound have been separated by underscores (`_`), e.g. `yli_oppilas_tutkinto_lauta_kunta`.
* No other character denotes a word boundary inside a compound; for example, these compounds are only two individual words each:
  * `jok'_ainoa`
  * `valo-_oppi`
  * `suomen _kieli`
  * `vaa'an_kieli`
  * `tax-free-_myynti`
  * `all stars -_joukkue`
* Includes "plural only" words (e.g. `hopea_häät`).
* Examples of words/prefixes/suffixes of Latin/Greek origin I didn't consider separate words:
  * prefixes: a-, di-, dis-, in-, inter-, iso-, multi-, poly-, post-, pre-, re-, sub-, syn-, tri-
  * suffixes: -grafi(nen/a), -grammi, -kroninen, -logi(nen/a), -metri(nen/a) ("metri" as a device, not as a unit), -paatti(nen)/-patia, -skooppi(nen)/-skopia
* Tip: to restore a compound to its original form, simply delete all underscores.
* Tip: to split a compound properly:
  * first split by underscores&hellip;
  * &hellip;then strip leading/trailing apostrophes/hyphens/spaces (`'- `) from each individual word
  * e.g. `all stars -_joukkue` becomes `all stars` and `joukkue`
* The GPLv3 license does not apply to this file (I think) because it is largely based on the Kotus wordlist.

### partial-homonyms.txt
A list of partially homonymous inflected nouns and verbs. Automatically
generated with `find-partial-homonyms.py`.

### plurals.csv
A list of "plural only" words on the Kotus list.

Notes:
* Two fields on each line: a word in plural and its singular form (e.g. `sakset,saksi`).
* No compounds (e.g. `seppeleensitojaiset`).
* Includes words that only occur as the final part of a compound, not alone (e.g. `sitojaiset`).

### stats-nounverb.txt
A table of noun/verb counts by declension/conjugation, syllable count and
ending. Automatically generated.
