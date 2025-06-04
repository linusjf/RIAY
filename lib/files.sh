#!/usr/bin/env bash
######################################################################
# File Utility Functions
# Provides file and directory related functions for working with files and paths
######################################################################

set -euo pipefail
shopt -s inherit_errexit
if [[ -z "${SCRIPT_DIR:-""}" ]]; then
  if command -v realpath >/dev/null 2>&1; then
    SCRIPT_DIR="$(dirname "$(realpath "$0")")"
  else
    SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" &>/dev/null && pwd -P)"
  fi
fi

source "${SCRIPT_DIR}/lib/require.sh"

require_commands realpath pwd mkdir

if ! declare -f files::get_relative_path >/dev/null; then
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

if ! declare -f files::get_temp_dir >/dev/null; then
  files::get_temp_dir() {
    if [ -n "$TMPDIR" ] && [ -d "$TMPDIR" ]; then
      echo "$TMPDIR"
    elif [ -d /data/data/com.termux/files/usr/tmp ]; then # Termux tmp
      echo "/data/data/com.termux/files/usr/tmp"
    elif [ -d /data/local/tmp ]; then # Android tmp
      echo "/data/local/tmp"
    else
      echo "/tmp"
    fi
  }
  export -f files::get_temp_dir
fi

if ! declare -f files::create_temp_dir >/dev/null; then
  files::create_temp_dir() {
    local dir_name="$1"
    local temp_dir="$(files::get_temp_dir)/$dir_name"

    mkdir -p "$temp_dir"
    echo "$temp_dir"
  }
  export -f files::create_temp_dir
fi

if ! declare -f files::safe_remove_dir >/dev/null; then
  files::safe_remove_dir() {
    local dir="$1"
    local temp_dir="$(files::get_temp_dir)"

    # Only remove if directory exists, is under temporary directory, and isn't the temp directory itself
    if [[ -d "$dir" ]] && [[ "$dir" == "$temp_dir"* ]] && [[ "$dir" != "$temp_dir" ]]; then
      rm -rf "$dir"
    fi
  }
  export -f files::safe_remove_dir
fi
