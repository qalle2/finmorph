# finmorph
Tools regarding the morphology of the Finnish language.

I have used [the Finnish wordlist by Kotus](https://kaino.kotus.fi/sanat/nykysuomi/) when creating the programs.

## verbclass.py
Get the Kotus conjugation class(es) of a Finnish verb. Argument: verb in infinitive

Example:
```
python3 verbclass.py "isota"
class 72 (like 'vanheta' (3SG past 'vanheni'))
class 74 (like 'katketa' (3SG past 'katkesi'))
```
