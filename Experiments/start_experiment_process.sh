#!/bin/sh

node="0"

if [ "$1" = "--node" ]; then
  node="$2"
  shift
  shift
fi

output_file=experiment_node${node}_output.log

numactl --physcpubind=$node --membind=$node \
  python -m Classical.perform_experiments $@ > $output_file &
