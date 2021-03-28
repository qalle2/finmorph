# finmorph
Tools regarding the morphology of the Finnish language.

I have used [the Finnish wordlist by Kotus](https://kaino.kotus.fi/sanat/nykysuomi/) when creating the programs.
You need to download the XML file from there to use some of the programs.

## noundecl.py
Get the Kotus declension(s) (1&hellip;49) of a Finnish noun (including adjectives/pronouns/numerals). Argument: noun in nominative singular

Example:
```
$ python3 noundecl.py "kuusi"
declension 24 (like "un|i, -en, -ien/-ten, -ta, -ia, -een, -iin")
declension 27 (like "kä|si, -den, -sien/-tten, -ttä, -siä, -teen, -siin")
```

See also `test.py`.

To do: find more patterns to reduce number of exceptions; print consonant gradation info.

## verbconj.py
Get the Kotus conjugation(s) (52&hellip;78) of a Finnish verb. Argument: verb in infinitive

Example:
```
$ python3 verbconj.py "isota"
conjugation 72 (like "vanhe|ta, -nen, -ni, -nisi, -tkoon, -nnut, -ttiin")
conjugation 74 (like "katke|ta, -an, -si, -(a)isi, -tkoon, -nnut, -ttiin")
```

See also `test.py`.

To do: print consonant gradation info.

## test.py
Test whether `noundecl.py` and `verbconj.py` work correctly. Requires CSV input files which can be
created using `extract_words.sh`.

## extract_words.sh
Convert the Kotus XML file (see above) into CSV files that are used as input for `test.py`.
Warning: overwrites files.

## xml2csv.py
Read Kotus XML data from stdin, print words in CSV format. For an example, see `extract_words.sh`.

## merge_csv_lines.py
Read CSV data from stdin, merge lines with identical words. For an example, see `extract_words.sh`.

## filter_by_conjugation.py
Read CSV data from stdin, print lines that contain the specified declensions/conjugations.
Arguments: first and last declension/conjugation. For an example, see `extract_words.sh`.

## filter_monodisyll.py
Read CSV data from stdin, print lines that contain a mono- or disyllabic word. For an example, see
`extract_words.sh`.
