#!/bin/sh

folders="Classical Data UCP"
for folder in $folders
do
  cd $folder
  python -m unittest
  mypy *.py
  cd ..
done
