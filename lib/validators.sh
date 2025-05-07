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
  function validators::isnumeric() {
    [[ "$1" =~ ^[0-9]+$ ]]
  }
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
  function validators::validate_input() {
    local value="$1" max_length="$2" error_message="$3"
    [[ -z "$value" ]] && die "Error: $error_message cannot be empty"
    [[ ${#value} -gt "$max_length" ]] && die "Error: $error_message too long. Maximum $max_length characters"
    return 0
  }
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
  function validators::validate_file() {
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
fi

if ! declare -f validators::validate_arg_count > /dev/null; then
  ######################################################################
  # Validate argument count
  # Globals: none
  # Arguments:
  #   $1 - actual count
  #   $2 - expected count
  #   $3 - error message (optional)
  # Outputs: error message to STDERR on failure
  # Returns: exits with status 1 on invalid input
  ######################################################################
  function validators::validate_arg_count() {
    local actual="$1" expected="$2" message="${3:-Incorrect number of arguments}"
    if [[ "$actual" -ne "$expected" ]]; then
      err "Error: $message (expected $expected, got $actual)"
      return 1
    fi
    return 0
  }
fi

if ! declare -f validators::file_exists > /dev/null; then
  ######################################################################
  # Check if file exists
  # Globals: none
  # Arguments:
  #   $1 - path to file
  # Outputs: error message to STDERR on failure
  # Returns: exits with status 2 if file doesn't exist
  ######################################################################
  function validators::file_exists() {
    local file="$1"
    if [[ ! -e "${file}" ]]; then
      err "Error: '${file}' does not exist"
      return 2
    fi
    return 0
  }
fi

if ! declare -f validators::file_readable > /dev/null; then
  ######################################################################
  # Check if file is readable
  # Globals: none
  # Arguments:
  #   $1 - path to file
  # Outputs: error message to STDERR on failure
  # Returns: exits with status 2 if file isn't readable
  ######################################################################
  function validators::file_readable() {
    local file="$1"
    if [[ ! -r "${file}" ]]; then
      err "Error: '${file}' is not readable"
      return 2
    fi
    return 0
  }
fi

# Export all functions at the end
export -f validators::isnumeric
export -f validators::validate_input
export -f validators::validate_file
export -f validators::validate_arg_count
export -f validators::file_exists
export -f validators::file_readable
