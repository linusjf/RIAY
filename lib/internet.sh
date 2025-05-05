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
if ! declare -f internet::checkinternet > /dev/null; then
  internet::checkinternet() {
    if ! hash ping 2> /dev/null; then
      echo "Error: ping command not found" >&2
      return 1
    fi

    if ! ping -q -c 1 -W 2 8.8.8.8 &> /dev/null; then
      echo "No internet connection detected..." >&2
      return 1
    fi
    return 0
  }
  export -f internet::checkinternet
fi
