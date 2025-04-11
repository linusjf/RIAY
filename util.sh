#!/usr/bin/env bash
######################################################################
# @file util.sh
# @brief General utility functions for bash scripting
# @description Contains common utility functions for output, debugging, and system operations.

#######################################
# Output functions
#######################################

#######################################
# Print message to STDOUT
# Globals: none
# Arguments: message
# Outputs: message to STDOUT
# Returns: none
#######################################
out() { printf "%b\n" "$*"; }
export -f out

#######################################
# Print message to STDERR
# Globals: none
# Arguments: message
# Outputs: message to STDERR
# Returns: none
#######################################
err() { >&2 printf "%b\n" "$*"; }
export -f err

#######################################
# Print fatal message to STDERR and exit
# Globals: none
# Arguments: message
# Outputs: message to STDERR
# Returns: exits with status 1
#######################################
die() {
  >&2 printf "%b\n" "$*"
  exit 1
}
export -f die

#######################################
# Print banner message to STDOUT
# Globals: none
# Arguments: message
# Outputs: banner message to STDOUT
# Returns: none
#######################################
big() { printf "\n###\n#\n#\ %b\n#\n###\n\n" "$*"; }
export -f big

#######################################
# Print log message with timestamp and PID
# Globals: none
# Arguments: message
# Outputs: log message to STDOUT
# Returns: none
#######################################
log() { printf "%b %b %b\n" "$(now)" $$ "$*"; }
export -f log

#######################################
# Time functions
#######################################

#######################################
# Get current UTC timestamp in ISO8601 format
# Globals: none
# Arguments: none
# Outputs: timestamp to STDOUT
# Returns: none
#######################################
now() { date -u "+%Y-%m-%dT%H:%M:%S.%NZ"; }
export -f now

#######################################
# Get current Unix epoch timestamp
# Globals: none
# Arguments: none
# Outputs: timestamp to STDOUT
# Returns: none
#######################################
sec() { date -u "+%s"; }
export -f sec

#######################################
# Random ID generation
#######################################

#######################################
# Generate random 128-bit hex ID
# Globals: none
# Arguments: none
# Outputs: random ID to STDOUT
# Returns: none
#######################################
zid() { hexdump -n 16 -v -e '16/1 "%02x" "\n"' /dev/random; }
export -f zid

#######################################
# Command checking
#######################################

#######################################
# Check if command exists
# Globals: none
# Arguments: command name
# Outputs: none
# Returns: 0 if exists, 1 otherwise
#######################################
cmd() { command -v "$1" > /dev/null 2>&1; }
export -f cmd

#######################################
# Assertion functions
#######################################

#######################################
# Assert variable is empty
# Globals: none
# Arguments: variable value
# Outputs: error message if assertion fails
# Returns: none
#######################################
assert_empty() { [ -z "$1" ] || err "${FUNCNAME[0]}" "$@"; }
export -f assert_empty

#######################################
# Assert two values are equal
# Globals: none
# Arguments: value1 value2
# Outputs: error message if assertion fails
# Returns: none
#######################################
assert_equal() { [ "$1" = "$2" ] || err "${FUNCNAME[0]}" "$@"; }
export -f assert_equal

#######################################
# Temporary directory functions
#######################################

#######################################
# Create temporary directory
# Globals: none
# Arguments: optional prefix
# Outputs: directory path to STDOUT
# Returns: none
#######################################
temp_home() { out "$(mktemp -d -t "${1:-$(zid)}")"; }
export -f temp_home

#######################################
# Create temporary directory with program name
# Globals: none
# Arguments: none
# Outputs: directory path to STDOUT
# Returns: none
#######################################
temp_dir() { out "$(temp_home "$(program)")"; }
export -f temp_dir

#######################################
# Program information
#######################################

#######################################
# Get program name
# Globals: none
# Arguments: none
# Outputs: program name to STDOUT
# Returns: none
#######################################
program() { printf "%s\n" "$(basename "$0")"; }
export -f program
