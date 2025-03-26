#!/usr/bin/env bash

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : internet
# @created     : Tuesday Mar 26, 2024 11:57:10 IST
#
# @description : Functions for checking internet connectivity
######################################################################

# Check if internet connection is available
#
# Globals:
#   None
# Arguments:
#   None
# Outputs:
#   Error message to STDERR if no connection
# Returns:
#   0 if internet connection is available
#   1 if no connection
checkinternet() {
  if ! hash telnet 2> /dev/null; then
    echo "Error: telnet command not found" >&2
    return 1
  fi

  if ! telnet 8.8.8.8 53 &> /dev/null; then
    echo "Error: No internet connection detected" >&2
    return 1
  fi

  return 0
}
