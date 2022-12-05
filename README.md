# finmorph
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

### decline_noun.py
```
Decline a Finnish noun. Arguments: NOUN [CASE NUMBER]. Cases: nom, gen, par,
ess, tra, ine, ela, ill, ade, abl, all, abe, ins. Numbers: sg, pl. If case &
number omitted, print all supported combinations.
```

These cases have not yet been implemented in plural: translative, inessive, elative, adessive, ablative, allative, abessive, instructive.

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
IneSg: kuudessa, kuusessa
ElaSg: kuudesta, kuusesta
IllSg: kuuseen, kuuteen
IllPl: kuusiin
AdeSg: kuudella, kuusella
AblSg: kuudelta, kuuselta
AllSg: kuudelle, kuuselle
AbeSg: kuudetta, kuusetta
```

### find_partial_homonym_nouns.py
Find partially homonymous inflected nouns. Under construction (the results are incomplete). Slow.

`partial-homonym-nouns.txt` has been generated with this program.

### noun_consgrad.py
Argument: a Finnish noun (including adjectives/pronouns/numerals, excluding compounds) in nominative singular. Print the Kotus declension(s) (1-49) and whether consonant gradation applies.

Example:
```
$ python3 noun_consgrad.py "kuusi"
Declension 24 (like "un|i, -en, -ien/-ten, -ta, -ia, -een, -iin") without
consonant gradation
Declension 27 (like "käsi, käden, -en/kätten, kättä, -ä, käteen, -in") without
consonant gradation
```

Needs `noundecl.py` and `countsyll.py`. Can be tested with `test_nounverb.py`.

### noundecl.py
Argument: a Finnish noun (including adjectives/pronouns/numerals, excluding compounds) in nominative singular. Print the Kotus declension(s) (1-49).

Example:
```
$ python3 noundecl.py "kuusi"
Declension 24 (like "un|i, -en, -ien/-ten, -ta, -ia, -een, -iin")
Declension 27 (like "käsi, käden, -en/kätten, kättä, -ä, käteen, -in")
```

Needs `countsyll.py`. Can be tested with `test_nounverb.py`.

### verb_consgrad.py
Argument: a Finnish verb (not a compound) in the infinitive. Print the Kotus conjugation(s) (52-78) and whether consonant gradation applies.

Example:
```
$ python3 verb_consgrad.py "keritä"
Conjugation 69 (like "vali|ta, -tsen, -tsi, -tsisi, -tkoon, -nnut, -ttiin")
without consonant gradation
Conjugation 75 (like "selvi|tä, -än, -si, -äisi, -tköön, -nnyt, -ttiin") with
consonant gradation
```

Needs `verbconj.py`. Can be tested with `test_nounverb.py`.

### verbconj.py
Argument: a Finnish verb (not a compound) in the infinitive. Print the Kotus conjugation(s) (52-78).

Example:
```
$ python3 verbconj.py "keritä"
Conjugation 69 (like "vali|ta, -tsen, -tsi, -tsisi, -tkoon, -nnut, -ttiin")
Conjugation 75 (like "selvi|tä, -än, -si, -äisi, -tköön, -nnyt, -ttiin")
```

Needs `countsyll.py`. Can be tested with `test_nounverb.py`.

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

Needs `generated-lists/nonfinals.txt` and `generated-lists/finals.csv` which can be generated with `extract.sh`.

TODO: make the program more space efficient (those word lists are more than a hundred kilobytes together).

## Programs less interesting to the end user

### extract.sh
Converts the Kotus XML file (link above) into CSV files that are needed by the other programs.
Warning: overwrites the files listed below.

Note: before running this script, extract the Kotus XML file to the same directory as this project.

Creates the subdirectory `generated-lists/` and generates these files under it:
* `words-orig.csv`: the original words (no leading/trailing apostrophes/hyphens/spaces) (~94,000 words)
* `words.csv`: words without plurals or compounds but with singular forms of plurals and finals of compounds (~41,000 words)
  * `nouns.csv`: nouns (Kotus declensions 1&ndash;49) from `words.csv` (~26,000 words)
    * `nouns-1syll.csv`: monosyllabic nouns
    * `nouns-2syll.csv`: disyllabic nouns
    * `nouns-3syll.csv`: trisyllabic nouns
    * `nouns-4syll.csv`: quadrisyllabic and longer nouns
  * `verbs.csv`: verbs (Kotus conjugations 52&ndash;78) from `words.csv` (~9,400 words)
    * `verbs-1syll.csv`: monosyllabic verbs
    * `verbs-2syll.csv`: disyllabic verbs
    * `verbs-3syll.csv`: trisyllabic verbs
    * `verbs-4syll.csv`: quadrisyllabic and longer verbs
* `words-consgrad.csv`: like `words.csv` but only the words to which consonant gradation applies (~11,000 words)
* `finals.csv`: words that occur as final parts of compounds (and possibly non-finally or alone) (~8,400 words)
* `nonfinals.txt`: words that occur as non-final parts of compounds (not finally but possibly alone) (~5,300 words)
* `compositives.txt`: words that occur as non-final parts of compounds (not finally or alone) (~2,900 words)

Also generates `stats-compound.txt` and `stats-nounverb.txt` under the current directory (see [text files](#text-files)).

### test_decline_noun.py
Test `decline_noun.py`. No arguments.

### test_nounverb.py
Argument: which program to test ('n'=noundecl.py, 'v'=verbconj.py, 'nc'=noun_consgrad.py,
'vc'=verb_consgrad.py).

Needs files created by `extract.sh`.

### test_splitcomp.py
Test `splitcomp.py` against known single words and compounds.

Requires `generated-lists/words.csv` which can be generated with `extract.sh`.

### validate_compounds.py
Validate `compounds.txt` and `generated-lists/words.csv`.

## Programs even less interesting to the end user

These are only meant to be used by `extract.sh`.

### xml2csv.py
Read Kotus XML file, print distinct words and their declensions/conjugations (0-2) in CSV format. Arguments: XML file, which words ('a' = all, 'g' = only those that consonant gradation applies to).

### finals.py
Get words that occur as finals of compounds. Print them and their declensions/conjugations in CSV format. Arguments: wordCsvFile compoundListFile

### csv_combine.py
Arguments: one or more CSV files. For each distinct word, print a CSV line with all declensions/conjugations occurring with that word in the files.

### replace_plurals.py
Arguments: CSV file with words and declensions/conjugations, CSV file with plurals and singulars. Print words and declensions/conjugations in CSV format, with plurals replaced with singulars.

### strip_compounds.py
Arguments: CSV file with words and declensions/conjugations, list file with compounds. Print CSV lines without those that contain a compound.

### filter_by_conjugation.py
Arguments: CSV file with words and declensions/conjugations, first declension/conjugation, last declension/conjugation. Print lines that contain declensions/conjugations within that range.

### filter_by_syllcnt.py
Arguments: CSV file, syllable count (1-4; 4=4 or more). Print lines containing a word with that many syllables.

### nonfinals.py
Print words that only occur as non-final parts of compounds (not final). Argument: compound list file

### compositives.py
Print words that only occur as non-final parts of compounds (not final or alone). Arguments: compound list file, word CSV file

### stats_compound.py
Print a table of compound counts by number of parts and number of letters. Argument: compound list file.

### stats_nounverb.py
Print a table of noun/verb counts by declension/conjugation, syllable count and ending. Argument: CSV file with words (no compounds).

### util.py
Simple helper functions.

## Text files

### compounds.txt
A list of compounds on the Kotus word list.

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

### nonfinals.txt
Uninflected words that only occur as non-final parts of compounds, not finally or alone.
E.g. `hassel` (as in `hasselpähkinä`) but not `hevos`, `pään` or `pää`.
Under construction (vowel-final words still missing).

### partial-homonym-nouns.txt
A list of partially homonymous inflected nouns. Incomplete. Automatically generated with `find_partial_homonym_nouns.py`.

### plurals.csv
A list of "plural only" words on the Kotus list.

Notes:
* Two fields on each line: a word in plural and its singular form (e.g. `sakset,saksi`).
* No compounds (e.g. `seppeleensitojaiset`).
* Includes words that only occur as the final part of a compound, not alone (e.g. `sitojaiset`).

### stats-compound.txt
A table of compound counts by number of parts and number of letters.
Automatically generated.

### stats-nounverb.txt
A table of noun/verb counts by declension/conjugation, syllable count and ending.
Automatically generated.
