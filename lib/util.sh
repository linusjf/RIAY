#!/usr/bin/env bash
######################################################################
# @file util.sh
# @brief General utility functions for bash scripting
# @description Contains common utility functions for output, debugging, and system operations.

#######################################
# Output functions
#######################################

if ! declare -f out > /dev/null; then
  #######################################
  # Print message to STDOUT
  # Globals: none
  # Arguments: message
  # Outputs: message to STDOUT
  # Returns: none
  #######################################
  out() { printf "%b\n" "$*"; }
  export -f out
fi

if ! declare -f err > /dev/null; then
  #######################################
  # Print message to STDERR
  # Globals: none
  # Arguments: message
  # Outputs: message to STDERR
  # Returns: none
  #######################################
  err() { >&2 printf "%b\n" "$*"; }
  export -f err
fi

if ! declare -f warn > /dev/null; then
  #######################################
  # Print message to STDERR
  # Globals: none
  # Arguments: message
  # Outputs: message to STDERR
  # Returns: none
  #######################################
  warn() { err "$*"; }
  export -f warn
fi

if ! declare -f die > /dev/null; then
  #######################################
  # Print fatal message to STDERR and exit
  # Globals: none
  # Arguments: message
  # Outputs: message to STDERR
  # Returns: exits with status passed in or default 1
  #######################################
  die() {
    msg="${1:-}"
    exitcode="${2:-1}"
    >&2 printf "%b\n" "$msg"
    exit "$exitcode"
  }
  export -f die
fi

if ! declare -f big > /dev/null; then
  #######################################
  # Print banner message to STDOUT
  # Globals: none
  # Arguments: message
  # Outputs: banner message to STDOUT
  # Returns: none
  #######################################
  big() { printf "\n###\n#\n#\ %b\n#\n###\n\n" "$*"; }
  export -f big
fi

if ! declare -f log > /dev/null; then
  #######################################
  # Print log message with timestamp and PID
  # Globals: none
  # Arguments: message
  # Outputs: log message to STDOUT
  # Returns: none
  #######################################
  log() { printf "%b %b %b\n" "$(now)" $$ "$*"; }
  export -f log
fi

#######################################
# Time functions
#######################################

if ! declare -f now > /dev/null; then
  #######################################
  # Get current UTC timestamp in ISO8601 format
  # Globals: none
  # Arguments: none
  # Outputs: timestamp to STDOUT
  # Returns: none
  #######################################
  now() { date -u "+%Y-%m-%dT%H:%M:%S.%NZ"; }
  export -f now
fi

if ! declare -f sec > /dev/null; then
  #######################################
  # Get current Unix epoch timestamp
  # Globals: none
  # Arguments: none
  # Outputs: timestamp to STDOUT
  # Returns: none
  #######################################
  sec() { date -u "+%s"; }
  export -f sec
fi

#######################################
# Random ID generation
#######################################

if ! declare -f zid > /dev/null; then
  #######################################
  # Generate random 128-bit hex ID
  # Globals: none
  # Arguments: none
  # Outputs: random ID to STDOUT
  # Returns: none
  #######################################
  zid() { hexdump -n 16 -v -e '16/1 "%02x" "\n"' /dev/random; }
  export -f zid
fi

#######################################
# Command checking
#######################################

if ! declare -f cmd > /dev/null; then
  #######################################
  # Check if command exists
  # Globals: none
  # Arguments: command name
  # Outputs: none
  # Returns: 0 if exists, 1 otherwise
  #######################################
  cmd() { command -v "$1" > /dev/null 2>&1; }
  export -f cmd
fi

#######################################
# Assertion functions
#######################################

if ! declare -f assert_empty > /dev/null; then
  #######################################
  # Assert variable is empty
  # Globals: none
  # Arguments: variable value
  # Outputs: error message if assertion fails
  # Returns: none
  #######################################
  assert_empty() { [ -z "$1" ] || err "${FUNCNAME[0]}" "$@"; }
  export -f assert_empty
fi

if ! declare -f assert_equal > /dev/null; then
  #######################################
  # Assert two values are equal
  # Globals: none
  # Arguments: value1 value2
  # Outputs: error message if assertion fails
  # Returns: none
  #######################################
  assert_equal() { [ "$1" = "$2" ] || err "${FUNCNAME[0]}" "$@"; }
  export -f assert_equal
fi

#######################################
# Temporary directory functions
#######################################

if ! declare -f temp_home > /dev/null; then
  #######################################
  # Create temporary directory
  # Globals: none
  # Arguments: optional prefix
  # Outputs: directory path to STDOUT
  # Returns: none
  #######################################
  temp_home() { out "$(mktemp -d -t "${1:-$(zid)}")"; }
  export -f temp_home
fi

if ! declare -f temp_dir > /dev/null; then
  #######################################
  # Create temporary directory with program name
  # Globals: none
  # Arguments: none
  # Outputs: directory path to STDOUT
  # Returns: none
  #######################################
  temp_dir() { out "$(temp_home "$(program)")"; }
  export -f temp_dir
fi

#######################################
# Program information
#######################################

if ! declare -f program > /dev/null; then
  #######################################
  # Get program name
  # Globals: none
  # Arguments: none
  # Outputs: program name to STDOUT
  # Returns: none
  #######################################
  program() { printf "%s\n" "$(basename "$0")"; }
  export -f program
fi
