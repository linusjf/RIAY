#!/usr/bin/env bash

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : python
# @created     : Sunday Jun 15, 2025 14:09:32 IST
#
# @description :
######################################################################

set -o errexit
set -o nounset
set -o pipefail

if [[ -z "${SCRIPT_DIR:-}" ]]; then
  if command -v realpath > /dev/null 2>&1; then
    readonly SCRIPT_DIR="$(dirname "$(realpath "$0")")"
  else
    readonly SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" &> /dev/null && pwd -P)"
  fi
fi

source "${SCRIPT_DIR}/lib/require.sh"

require_commands python pip

if ! declare -f python::is_package_installed > /dev/null; then
  function python::is_package_installed() {
    local package="$1"
    pip show "$package" &> /dev/null && pip check &> /dev/null
  }
  export -f python::is_package_installed
fi
