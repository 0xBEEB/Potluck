#!/usr/bin/env bash

. ../$1.PKGBUILD
echo ${depends[*]}
