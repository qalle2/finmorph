# Warning: overwrites files
python3 extract_words.py  1 49 < ~/lang/kotus/kotus-sanalista_v1.xml > nouns.txt
python3 extract_words.py 52 78 < ~/lang/kotus/kotus-sanalista_v1.xml > verbs.txt
ls -l *.txt
