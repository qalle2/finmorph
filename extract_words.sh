# Convert the Kotus XML file into CSV files that are used as input for 'test.py'.
# Warning: overwrites files.

python3 xml2csv.py < kotus-sanalista_v1.xml | python3 merge_csv_lines.py | python3 ../text-util/finsort.py > words.csv

python3 filter_by_conjugation.py  1 49 < words.csv > nouns.csv
python3 filter_by_conjugation.py 52 78 < words.csv > verbs.csv

python3 filter_monodisyll.py < nouns.csv > nouns-monodisyll.csv
python3 ../text-util/lineset.py d nouns.csv nouns-monodisyll.csv | python3 ../text-util/finsort.py > nouns-triplussyll.csv

ls -l *.csv
