#!/bin/bash

# This tool saves a couple of different pages from erudit and saves the results in a folder. It
# then becomes easy to diff the result. This is handy to confirm that a refactoring doesn't change
# anything on the front-facing side.

# Usage example:
# ./scandump.sh https://www.erudit.org prod
# ./scandump.sh https://test.erudit.org test
# diff -ur prod test | vim -

PREFIX=${1:-https://www.erudit.org}
DUMPDIR=${2:-htmldump}

PATHS=(
   "/fr"
   "/en"
   "/fr/revues/"
   "/fr/revues/alterstice/"
   "/fr/revues/alterstice/2017-v7-n1-alterstice03139/"
   "/fr/revues/alterstice/2017-v7-n1-alterstice03139/1040609ar/"
   "/fr/recherche/?basic_search_term=arendt"
   "/fr/recherche/?basic_search_term=arendt&filter_funds=Persée"
)

fetch() {
    curl -L $1 > "$DUMPDIR/$2.html"
}

mkdir -p $DUMPDIR

counter=0
for p in ${PATHS[@]}; do
    url=${PREFIX}${p}
    echo "Fetching ${url}"
    fetch $url $counter
    counter=$((counter+1))
done
