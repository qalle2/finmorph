# finmorph
Tools regarding the morphology of the Finnish language.

I have used [the Finnish wordlist by Kotus](https://kaino.kotus.fi/sanat/nykysuomi/) when creating the programs.

## nounclass.py
Get the Kotus declension(s) (1&hellip;49) of a Finnish noun (including adjectives/pronouns/numerals). Argument: noun in nominative singular

Example:
```
$ python3 nounclass.py "kuusi"
declension 24 (like "un|i, -en, -ien/-ten, -ta, -ia, -een, -iin")
declension 27 (like "kä|si, -den, -sien/-tten, -ttä, -siä, -teen, -siin")
```

To do: print consonant gradation info.

## verbclass.py
Get the Kotus conjugation(s) (52&hellip;78) of a Finnish verb. Argument: verb in infinitive

Example:
```
$ python3 verbclass.py "isota"
conjugation 72 (like "vanheta" (3SG past "vanheni"))
conjugation 74 (like "katketa" (3SG past "katkesi"))
```

To do: print consonant gradation info.
