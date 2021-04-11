#!/bin/sh

coinhsl_arch="x86_64"
coinhsl_ver="2015.06.23"

tar xfz coinhsl-linux-$coinhsl_arch-$coinhsl_ver.tar.gz
ln -s libcoinhsl.so.0 coinhsl-linux-$coinhsl_arch-$coinhsl_ver/lib/libhsl.so
