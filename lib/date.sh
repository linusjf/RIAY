#!/usr/bin/env bash
######################################################################
# Date Utility Functions
# Provides date-related functions for working with days of year
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
source "${SCRIPT_DIR}/lib/util.sh"

#######################################
# Validate month number
# Globals: none
# Arguments:
#   $1 - Month number
# Outputs: Error to STDERR if invalid
# Returns: 0 if valid, 1 otherwise
#######################################
if ! declare -f date::validatemonth > /dev/null; then
  date::validatemonth() {
    [[ "$1" =~ ^[1-9]$|^1[0-2]$ ]] || {
      err "Error: Month number must be between 1 and 12"
      return 1
    }
  }
  export -f date::validatemonth
fi

if ! declare -f date::isnumeric > /dev/null; then
  ######################################################################
  # Check if input is numeric
  # Globals: None
  # Arguments:
  #   $1 - Value to check
  # Outputs: None
  # Returns: 0 if numeric, 1 otherwise
  ######################################################################
  date::isnumeric() {
    [[ "$1" =~ ^[0-9]+$ ]]
  }
  export -f date::isnumeric
fi

if ! declare -f date::mfromdoy > /dev/null; then
  ######################################################################
  # Get month name from day of year
  # Globals: None
  # Arguments:
  #   $1 - Day of year
  # Outputs: Month name to STDOUT
  # Returns: None (exits with status 1 on error)
  ######################################################################
  date::mfromdoy() {
    date::isnumeric "$1" || die "$1 is not numeric"
    require_commands date
    local day
    # convert number to base ten
    day=$((10#$1))
    [[ $day -ge 1 && $day -le 366 ]] || die "Day of year must be between 1 and 366"
    date --date="jan 1 + $((day - 1)) days" +%B
  }
  export -f date::mfromdoy
fi

if ! declare -f date::datefromdoy > /dev/null; then
  ######################################################################
  # Get full date from day of year
  # Globals: None
  # Arguments:
  #   $1 - Day of year
  # Outputs: Formatted date to STDOUT
  # Returns: None (exits with status 1 on error)
  ######################################################################
  date::datefromdoy() {
    date::isnumeric "$1" || die "$1 is not numeric"
    require_commands date
    local day
    # convert number to base ten
    day=$((${1}))
    [[ $day -ge 1 && $day -le 366 ]] || die "Day of year must be between 1 and 366"
    date --date="jan 1 + $((day - 1)) days" "+%B %d,%Y"
  }
  export -f date::datefromdoy
fi

if ! declare -f date::monthfromnumber > /dev/null; then
  ######################################################################
  # Get month name from month number
  # Globals: None
  # Arguments:
  #   $1 - Month number (1-12)
  # Outputs: Month name to STDOUT
  # Returns: None (exits with status 1 on error)
  ######################################################################
  date::monthfromnumber() {
    require_commands date
    case $1 in
      [1-9] | 1[0-2]) date -d "${1}/01" +%B ;;
      0[1-9]) date -d "${1}/01" +%B ;;
      *) die "Invalid month number: $1" ;;
    esac
  }
  export -f date::monthfromnumber
fi

if ! declare -f date::monthnumberfrommonth > /dev/null; then
  date::monthnumberfrommonth() {
    require_commands date
    month_name="$1"
    year="$2"
    month_number=$(date -d "1 $month_name $year" +"%m")
    echo "$month_number"
  }
  export -f date::monthnumberfrommonth
fi

if ! declare -f date::isleapyear > /dev/null; then
  date::isleapyear() {
    year="$1"

    ((year % 4 == 0 && year % 100 != 0)) \
      || ((year % 400 == 0))
  }
  export -f date::isleapyear
fi

if ! declare -f date::daycount > /dev/null; then
  date::daycount() {
    year="$1"
    # Check if year is a leap year
    if date::isleapyear "$year"; then
      echo 366
    else
      echo 365
    fi
  }
  export -f date::daycount
fi
