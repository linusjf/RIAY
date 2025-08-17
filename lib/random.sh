#!/usr/bin/env bash

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : random
# @created     : Sunday Aug 17, 2025 18:16:43 IST
#
# @description :
######################################################################

set -o errexit
set -o nounset
set -o pipefail

if [[ -z "${SCRIPT_DIR:-""}" ]]; then
  if command -v realpath > /dev/null 2>&1; then
    SCRIPT_DIR="$(dirname "$(realpath "$0")")"
  else
    SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" &> /dev/null && pwd -P)"
  fi
fi

source "${SCRIPT_DIR}/lib/require.sh"

require_commands tr head

# random utility functions

if ! declare -f random::random_string > /dev/null; then
  random::random_string() {
    local length=$1
    tr -dc 'A-Za-z0-9' < /dev/urandom | head -c "${length}"
    echo
  }
  export -f random::random_string
fi
