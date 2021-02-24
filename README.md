# finmorph
Tools regarding the morphology of the Finnish language.

I have used [the Finnish wordlist by Kotus](https://kaino.kotus.fi/sanat/nykysuomi/) when creating the programs.

## nounclass.py
Get the Kotus conjugation class(es) of a Finnish noun/adjective (class 1&hellip;49). Argument: noun/adjective in nominative singular

Note: This program is still at an early stage (it only gets ~62% of nouns right).

Example:
```
python3 nounclass.py "sana"
class 9 (like 'kala' (genitive 'kalan', partitive 'kalaa'))
```

TODO: print consonant gradation info

## verbclass.py
Get the Kotus conjugation class(es) of a Finnish verb (class 52&hellip;78). Argument: verb in infinitive

Example:
```
python3 verbclass.py "isota"
class 72 (like 'vanheta' (3SG past 'vanheni'))
class 74 (like 'katketa' (3SG past 'katkesi'))
```

TODO: print consonant gradation info
