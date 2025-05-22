#!/usr/bin/env bash
######################################################################
# File Utility Functions
# Provides file and directory related functions for working with files and paths
######################################################################

set -euo pipefail
shopt -s inherit_errexit
if [[ -z "${SCRIPT_DIR:-""}" ]]; then
  if command -v realpath > /dev/null 2>&1; then
    SCRIPT_DIR="$(dirname "$(realpath "$0")")"
  else
    SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" &> /dev/null && pwd -P)"
  fi
fi

source "${SCRIPT_DIR}/lib/require.sh"

require_commands realpath pwd

if ! declare -f files::get_relative_path > /dev/null; then
  files::get_relative_path() {
    local input_path="$1"

    # Make sure the file exists
    if [[ ! -e "$input_path" ]]; then
      echo "Error: '$input_path' does not exist." >&2
      return 1
    fi

    # Resolve to absolute path
    local abs_path
    abs_path=$(realpath "$input_path")

    # Get current directory
    local cwd="$(pwd)"

    # Compute relative path
    realpath --relative-to="$cwd" "$abs_path"
  }
  export -f files::get_relative_path
fi
