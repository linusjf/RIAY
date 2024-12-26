#!/usr/bin/env bash

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : internet
# @created     : Tuesday Mar 26, 2024 11:57:10 IST
#
# @description :
######################################################################
checkinternet() {
  hash telnet || exit
  telnet 8.8.8.8 53 &> /dev/null
  if test $? -eq 0; then
    return 0
  else
    echo "Check your internet connection..."
    return 1
  fi
}
