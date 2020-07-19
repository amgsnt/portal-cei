#!/bin/bash

python cei.py
rm -Rf out
mkdir out
mv CEIHIST* out/
cat out/CEIHIST* >> out/CEIHIST.cat
rm -Rf out/CEIHIST*.csv
