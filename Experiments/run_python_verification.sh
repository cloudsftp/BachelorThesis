#!/bin/sh

status=0

folders="Classical Data UCP"
for folder in $folders
do
  cd $folder
  python -m unittest
  [ $? -eq 0 ] || status=1
  mypy *.py
  [ $? -eq 0 ] || status=1
  cd ..
done

exit $status