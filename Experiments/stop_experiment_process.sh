#!/bin/sh

kill_process_with_name() {
  name="$1"

  echo Searching for process with name \"$name\"
  proc_info=$(ps -aux | grep "${name}" | grep -v grep)
  proc_pid=$(echo $proc_info | cut -d' ' -f2)

  if [ "$proc_pid" != "" ]; then
    echo Found $proc_pid
    kill $proc_pid
  else
    echo No process Found
  fi

  echo
}


kill_process_with_name 'python -m Classical.perform_experiments'
kill_process_with_name 'couenne'
