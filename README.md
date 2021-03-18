# finmorph
Tools regarding the morphology of the Finnish language.

I have used [the Finnish wordlist by Kotus](https://kaino.kotus.fi/sanat/nykysuomi/) when creating the programs. You need to download the XML file from there to use some of the programs.

## nounclass.py
Get the Kotus declension(s) (1&hellip;49) of a Finnish noun (including adjectives/pronouns/numerals). Argument: noun in nominative singular

Example:
```
$ python3 nounclass.py "kuusi"
declension 24 (like "un|i, -en, -ien/-ten, -ta, -ia, -een, -iin")
declension 27 (like "kä|si, -den, -sien/-tten, -ttä, -siä, -teen, -siin")
```

See also `test.py`.

To do: find more patterns to reduce number of exceptions; print consonant gradation info.

## verbclass.py
Get the Kotus conjugation(s) (52&hellip;78) of a Finnish verb. Argument: verb in infinitive

Example:
```
$ python3 verbclass.py "isota"
conjugation 72 (like "vanheta" (3SG past "vanheni"))
conjugation 74 (like "katketa" (3SG past "katkesi"))
```

See also `test.py`.

To do: print more verb forms; print consonant gradation info.

## test.py
Test whether `nounclass.py` and `verbclass.py` work correctly. You need to create the input files
with `extract_words.py` first.

Sample output (nouns):
```
$ python3 test.py n
Warning: 'ahtaus': expected conjugation(s) 40, got 39/40
Warning: 'ahtaus': expected conjugation(s) 39, got 39/40
<snip>
Words: 28783, errors: 0, warnings: 33
```

Sample output (verbs):
```
$ python3 test.py v
Warning: 'isota': expected conjugation(s) 72, got 72/74
Warning: 'isota': expected conjugation(s) 74, got 72/74
<snip>
Words: 9499, errors: 0, warnings: 8
```

## extract_words.py
Read the Kotus XML file from stdin. Print words in declensions/conjugations specified by command
line arguments. For an example, see `extract_words.sh`. Its output files can be used as
quick-to-parse input files for `test.py`.
