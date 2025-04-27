#!/usr/bin/env bash
# Library for command and environment variable requirements checking
if [[ -z "${SCRIPT_DIR:-""}" ]]; then
  readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd -P)"
fi
# Source util.sh if available
if [[ -f "${SCRIPT_DIR}/util.sh" ]]; then
  source "${SCRIPT_DIR}/util.sh"
fi

if ! declare -f require_commands > /dev/null; then
  #######################################
  # Check if required commands are available
  # Globals: none
  # Arguments: command names
  # Outputs: error message to STDERR if command not found
  # Returns: exits with status 127 if command not found
  #######################################
  require_commands() {
    for cmd in "$@"; do
      if ! command -v "$cmd" > /dev/null 2>&1; then
        err "Required command not found: $cmd"
        exit 127
      fi
    done
  }
  export -f require_commands
fi

if ! declare -f require_vars > /dev/null; then
  #######################################
  # Check if required environment variables are set
  # Globals: none
  # Arguments: variable names
  # Outputs: error message to STDERR if variable not set
  # Returns: exits with status 1 if variable not set
  #######################################
  require_vars() {
    for var in "$@"; do
      if [[ -z "${!var:-}" ]]; then
        err "Required environment variable not set: $var"
        exit 1
      fi
    done
  }
  export -f require_vars
fi

if ! declare -f require_functions > /dev/null; then
  #######################################
  # Check if required functions are defined
  # Globals: none
  # Arguments: function names
  # Outputs: error message to STDERR if function not defined
  # Returns: exits with status 1 if function not defined
  #######################################
  require_functions() {
    for func in "$@"; do
      if ! declare -f "$func" > /dev/null 2>&1; then
        err "Required function not defined: $func"
        exit 1
      fi
    done
  }
  export -f require_functions
fi
