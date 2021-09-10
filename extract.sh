# Converts the Kotus XML file into CSV files that are needed by the other programs.
# Warning: overwrites files.

mkdir -p generated-lists

echo "Converting the Kotus XML file into a CSV file..."
python3 xml2csv.py kotus-sanalista_v1.xml > generated-lists/words-orig.csv

echo "Adding words that only occur as finals of compounds..."
python3 finals.py generated-lists/words-orig.csv compounds.txt | sort > generated-lists/finals.csv
python3 csv_combine.py generated-lists/words-orig.csv generated-lists/finals.csv > generated-lists/words.csv

echo "Replacing (non-compound) plurals with singulars and deleting compounds..."
python3 replace_plurals.py generated-lists/words.csv plurals.csv > generated-lists/temp.csv
python3 strip_compounds.py generated-lists/temp.csv compounds.txt > generated-lists/words.csv
rm generated-lists/temp.csv

echo "Separating nouns and verbs..."
python3 filter_by_conjugation.py generated-lists/words.csv 1 49 > generated-lists/nouns.csv
python3 filter_by_conjugation.py generated-lists/words.csv 52 78 > generated-lists/verbs.csv

echo "Grouping by number of syllables..."
for ((i = 1; i <= 4; i++)); do
    python3 filter_by_syllcnt.py generated-lists/nouns.csv $i > generated-lists/nouns-${i}syll.csv
    python3 filter_by_syllcnt.py generated-lists/verbs.csv $i > generated-lists/verbs-${i}syll.csv
done

echo "Writing nonfinals.txt..."
python3 nonfinals.py compounds.txt | sort > generated-lists/nonfinals.txt

echo "generated-lists/:"
ls -l generated-lists/

echo "Writing stats-compound.txt and stats-nounverb.txt..."
python3 stats_compound.py compounds.txt > stats-compound.txt
python3 stats_nounverb.py generated-lists/words.csv > stats-nounverb.txt
