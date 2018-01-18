#!/bin/sh

# Because of a (temporary?) limitation in pip-tools, we need to document our git deps with "-e"
# However, we don't want to actually install our deps with "-e" so we need to `sed` our way out
# of this.
pip-compile -U requirements.in -o requirements.txt &&
sed -i 's/-e git/git/g' requirements.txt
