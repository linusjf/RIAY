#!/usr/bin/env bash
# Library for command and environment variable requirements checking

# Check if required commands are available
# Globals: none
# Arguments: command names
# Outputs: error message to STDERR if command not found
# Returns: exits with status 127 if command not found
require_commands() {
  for cmd in "$@"; do
    if ! command -v "$cmd" > /dev/null 2>&1; then
      echo "Error: Required command not found: $cmd" >&2
      exit 127
    fi
  done
}

# Check if required environment variables are set
# Globals: none
# Arguments: variable names
# Outputs: error message to STDERR if variable not set
# Returns: exits with status 1 if variable not set
require_vars() {
  for var in "$@"; do
    if [[ -z "${!var:-}" ]]; then
      echo "Error: Required environment variable not set: $var" >&2
      exit 1
    fi
  done
}
