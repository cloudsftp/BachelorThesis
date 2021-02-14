#!/bin/sh

status=0

python -m unittest
[ $? -eq 0 ] || status=1

find . -maxdepth 4 -name '*\.py' | grep -v __init__ | grep -v uqo | sed 's/\.py//g' | sed 's#\./##g' | sed 's#/#.#g' | xargs -I{} mypy -m {}
[ $? -eq 0 ] || status=1

exit $status