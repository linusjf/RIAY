#!/usr/bin/env bash

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : validators
# @created     : Wednesday May 07, 2025 15:02:57 IST
#
# @description :
######################################################################

set -euo pipefail
shopt -s inherit_errexit

# Source utility functions
if [[ -z "${SCRIPT_DIR:-}" ]]; then
  readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd -P)"
fi
source "${SCRIPT_DIR}/lib/util.sh"

if ! declare -f validators::isnumeric > /dev/null; then
  ######################################################################
  # Check if input is numeric
  # Globals: None
  # Arguments:
  #   $1 - Value to check
  # Outputs: None
  # Returns: 0 if numeric, 1 otherwise
  ######################################################################
  validators::isnumeric() {
    [[ "$1" =~ ^[0-9]+$ ]]
  }
  export -f validators::isnumeric
fi

if ! declare -f validators::validate_input > /dev/null; then
  ######################################################################
  # Validate input length
  # Globals: None
  # Arguments:
  #   $1 - Input value
  #   $2 - Maximum length
  #   $3 - Error message prefix
  # Outputs: Error message to STDERR if validation fails
  # Returns: None (exits with status 1 on error)
  ######################################################################
  validators::validate_input() {
    local value="$1" max_length="$2" error_message="$3"
    [[ -z "$value" ]] && die "Error: $error_message cannot be empty"
    [[ ${#value} -gt "$max_length" ]] && die "Error: $error_message too long. Maximum $max_length characters"
    return 0
  }
  export -f validators::validate_input
fi

if ! declare -f validators::validate_file > /dev/null; then
  ######################################################################
  # Validate file exists and is readable
  # Globals: none
  # Arguments:
  #   $1 - path to file
  # Outputs: error message to STDERR on failure
  # Returns: exits with status 2 on invalid input
  ######################################################################
  validators::validate_file() {
    local file="$1"

    if [[ $# -ne 1 ]]; then
      err "Error: Exactly one argument required"
      return 1
    fi

    if [[ ! -f "${file}" ]]; then
      err "Error: '${file}' is not a valid file"
      return 2
    fi

    if [[ ! -r "${file}" ]]; then
      err "Error: Cannot read '${file}'"
      return 2
    fi
    return 0
  }
  export -f validators::validate_file
fi
