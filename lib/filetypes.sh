#!/usr/bin/env bash

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : filetypes
# @created     : Wednesday May 07, 2025 15:13:28 IST
#
# @description :
######################################################################

set -euo pipefail
shopt -s inherit_errexit

# Source utility functions
if [[ -z "${SCRIPT_DIR:-}" ]]; then
  readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd -P)"
fi
source "${SCRIPT_DIR}/lib/require.sh"

require_commands file grep tr

######################################################################
# Verify file is a valid JPEG
######################################################################
if ! declare -f filetypes::is_jpeg_file > /dev/null; then
  filetypes::is_jpeg_file() {
    file "$1" | grep -q 'JPEG'
  }
  export -f filetypes::is_jpeg_file
fi

######################################################################
######################################################################
if ! declare -f filetypes::is_jpeg_extension > /dev/null; then
  filetypes::is_jpeg_extension() {
    local ext="${1##*.}"
    local ext_lower
    ext_lower=$(echo "${ext}" | tr '[:upper:]' '[:lower:]')
    [[ "${ext_lower}" == "jpg" || "${ext_lower}" == "jpeg" ]]
  }
  export -f filetypes::is_jpeg_extension
fi
