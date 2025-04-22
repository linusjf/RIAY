#!/usr/bin/env bash
######################################################################
# Date Utility Functions
# Provides date-related functions for working with days of year
######################################################################

set -euo pipefail
shopt -s inherit_errexit

if ! declare -f mfromdoy > /dev/null; then
  ######################################################################
  # Get month name from day of year
  # Globals: None
  # Arguments:
  #   $1 - Day of year
  # Outputs: Month name to STDOUT
  # Returns: None (exits with status 1 on error)
  ######################################################################
  mfromdoy() {
    isnumeric "$1" || die "$1 is not numeric"
    require date
    local day
    # convert number to base ten
    day=$((${1}))
    [[ $day -ge 1 && $day -le 366 ]] || die "Day of year must be between 1 and 366"
    date --date="jan 1 + $((day - 1)) days" +%B
  }
fi

if ! declare -f datefromdoy > /dev/null; then
  ######################################################################
  # Get full date from day of year
  # Globals: None
  # Arguments:
  #   $1 - Day of year
  # Outputs: Formatted date to STDOUT
  # Returns: None (exits with status 1 on error)
  ######################################################################
  datefromdoy() {
    isnumeric "$1" || die "$1 is not numeric"
    require date
    local day
    # convert number to base ten
    day=$((${1}))
    [[ $day -ge 1 && $day -le 366 ]] || die "Day of year must be between 1 and 366"
    date --date="jan 1 + $((day - 1)) days" "+%B %d,%Y"
  }
fi

if ! declare -f monthfromnumber > /dev/null; then
  ######################################################################
  # Get month name from month number
  # Globals: None
  # Arguments:
  #   $1 - Month number (1-12)
  # Outputs: Month name to STDOUT
  # Returns: None (exits with status 1 on error)
  ######################################################################
  monthfromnumber() {
    require date
    case $1 in
      [1-9] | 1[0-2]) date -d "${1}/01" +%B ;;
      0[1-9]) date -d "${1}/01" +%B ;;
      *) die "Invalid month number: $1" ;;
    esac
  }
fi

if ! declare -f isnumeric > /dev/null; then
  ######################################################################
  # Check if input is numeric
  # Globals: None
  # Arguments:
  #   $1 - Value to check
  # Outputs: None
  # Returns: 0 if numeric, 1 otherwise
  ######################################################################
  isnumeric() {
    [[ "$1" =~ ^[0-9]+$ ]]
  }
fi

if ! declare -f die > /dev/null; then
  ######################################################################
  # Display error message and exit with failure status
  # Globals: None
  # Arguments:
  #   $1 - Error message
  # Outputs: Error message to STDERR
  # Returns: None (exits with status 1)
  ######################################################################
  die() {
    printf "%s\n" "$1" >&2
    exit 1
  }
fi

if ! declare -f require > /dev/null; then
  ######################################################################
  # Verify required commands are available
  # Globals: None
  # Arguments:
  #   $@ - Commands to check
  # Outputs: Error message to STDERR if command missing
  # Returns: None (exits with status 1 if command missing)
  ######################################################################
  require() {
    for cmd in "$@"; do
      if ! command -v "$cmd" > /dev/null 2>&1; then
        die "Required command '$cmd' not found"
      fi
    done
  }
fi
