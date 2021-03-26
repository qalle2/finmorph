# Warning: overwrites files

python3 xml2csv.py < kotus-sanalista_v1.xml > words.txt

python3 filter_by_conjugation.py  1 49 < words.txt > nouns.txt
python3 filter_by_conjugation.py 52 78 < words.txt > verbs.txt

python3 filter_by_syllable_count.py 1 < nouns.txt > nouns-1syll.txt
python3 filter_by_syllable_count.py 2 < nouns.txt > nouns-2syll.txt
python3 filter_by_syllable_count.py 3 < nouns.txt > nouns-3syll.txt

ls -l *.txt
