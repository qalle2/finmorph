# Convert the Kotus XML file into CSV files that are used as input for 'test.py'.
# Warning: overwrites files.

python3 xml2csv.py < kotus-sanalista_v1.xml | python3 merge_csv_lines.py > words.csv

python3 filter_by_conjugation.py  1 49 < words.csv > nouns.csv
python3 filter_by_conjugation.py 52 78 < words.csv > verbs.csv

python3 filter_by_syllable_count.py 1 < nouns.csv > nouns-1syll.csv
python3 filter_by_syllable_count.py 2 < nouns.csv > nouns-2syll.csv
python3 filter_by_syllable_count.py 3 < nouns.csv > nouns-3syll.csv

ls -l *.csv
