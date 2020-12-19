#!/bin/sh

output_file=experiment_output.log
numactl python -m Classical.perform_experiments $@ > $output_file &
