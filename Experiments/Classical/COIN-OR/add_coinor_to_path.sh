#!/bin/sh

programs="clp cbc ipopt bonmin couenne"

install_dir=/usr/local/share/coin-or/bin
bin_dir=/usr/local/sbin

for program in $programs
do
  sudo link $install_dir/$program $bin_dir/$program
done
